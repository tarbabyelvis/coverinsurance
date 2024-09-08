from datetime import datetime, date, timedelta
from pyexpat.errors import messages

from rest_framework.exceptions import NotFound

from claims.models import Claim, Payment
from claims.serializers import ClaimSerializer
from config.models import PaymentAccount
from core.utils import serialize_dates
from integrations.superbase import loan_transaction, suspend_debicheck, query_loan


def process_retrenchment_claim(tenant_id, claim_id, number_of_months):
    try:
        claim = __find_claim_by_id(claim_id)
        claim_serializer = ClaimSerializer(claim)
        claim_data = claim_serializer.data
        policy = get_policy_from_claim_id(claim_data)
        loan_id: str = f"{policy['loan_id']}"
        start_date = claim_data['submitted_date']
        status, repayment_schedule = find_next_n_months_installments(tenant_id, loan_id, start_date, number_of_months)
        if status == 200:
            status, message, data = suspend_debicheck(tenant_id=tenant_id, loan_id=loan_id)
            print(f'suspension status {status}, message {message}, suspend data {data}')
            if status == 200 or message == 'Intecon Contract already suspended':
                total_amount = calculate_total_installment_amount(repayment_schedule)
                update_claim_suspension_details(claim, start_date, number_of_months, total_amount)
        else:
            print('no installments found')
    except Exception as e:
        print(e)


def update_claim_suspension_details(claim, start_date, number_of_months, total_amount):
    claim_details = claim.claim_details or {}
    claim_details['debicheck_suspended'] = True
    claim_details['debicheck_suspension_from'] = start_date
    debicheck_expiry_date = calculate_debicheck_expiry_date(start_date, number_of_months)
    claim_details['debicheck_suspension_to'] = debicheck_expiry_date
    claim_details['retrenchment_amount_claimed'] = total_amount
    claim.claim_details = claim_details
    try:
        claim.save()
    except Exception as e:
        print(e)


def find_next_n_months_installments(tenant_id, loan_id, start_date, number_of_months: int = 6):
    try:
        response_status, message, data = query_loan(tenant_id, loan_id)
        if response_status == 200:
            periods = data['repaymentSchedule']['periods']
            start_date = parse_date(start_date)
            next_periods = sorted(
                (p for p in periods if parse_date(p["dueDate"]) > start_date),
                key=lambda p: parse_date(p["dueDate"])
            )[:number_of_months]
            return 200, next_periods
    except Exception as e:
        print("Something went wrong fetching repayment schedule")
        print(e)
        return 0, []


def calculate_total_installment_amount(repayment_schedule):
    return sum(
        map(lambda schedule: schedule['totalOutstandingForPeriod'], repayment_schedule))


def calculate_debicheck_expiry_date(start_date, number_of_months):
    start_date = parse_date(start_date)
    expiry_date = start_date + timedelta(days=number_of_months)
    return serialize_dates(expiry_date)


def calculate_total_installments_to_claim(repayment_schedule: list):
    repayment_schedule = repayment_schedule or []


def parse_date(date_passed):
    if isinstance(date_passed, list):
        return parse_date_array(date_passed)
    elif isinstance(date_passed, str):
        return datetime.strptime(date_passed, '%Y-%m-%d').date()
    return date_passed


def parse_date_array(date_array):
    year, month, day = date_array
    return date(year, month, day)


def get_policy_from_claim_id(claim):
    return claim['policy']


def process_claim_payment(tenant_id, claim_id):
    claim = __find_claim_by_id(claim_id)
    policy = claim.policy
    loan_id = policy.loan_id
    claim_amount = claim.claim_amount
    transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    claim_payment = Payment(
        transaction_date=transaction_date,
        amount=claim_amount,
        receipt_number='',
        bank_account='',
        check_number='',
        payment_type_id='',
        transaction_type='',
        notes=''
    )
    receipt_claim_repayment(tenant_id, loan_id, claim_amount, transaction_date)


def __find_claim_by_id(claim_id: int):
    claim = Claim.objects.filter(id=claim_id).first()
    print(f'claim:: {claim}')
    if not claim:
        raise NotFound("Claim with id {} not found".format(claim_id))
    return claim


def receipt_claim_repayment(tenant_id, loan_id, transaction_amount, check_number, receipt_number, note):
    transaction_date = datetime.now().strftime('%Y-%m-%d')
    payment_account = PaymentAccount.objects.filter(name='INSURANCE').first()
    if payment_account is None:
        raise PaymentAccount.DoesNotExist
    payment_type_id = payment_account.payment_type_id
    account_number = payment_account.account_number
    bank_number = payment_account.bank_number
    routing_code = payment_account.routing_code

    if (
            transaction_amount is None
            or (
            (
                    type(transaction_amount) != float
                    and type(transaction_amount) != int
            )
    )
    ):
        print("Missing parameters")
        raise Exception("Missing parameters")

    payload = {
        "loanId": loan_id,
        "paymentTypeId": payment_type_id,
        "transactionAmount": transaction_amount,
        "transactionDate": transaction_date,
        "accountNumber": account_number,
        "checkNumber": check_number,
        "routingCode": routing_code,
        "receiptNumber": receipt_number,
        "bankNumber": bank_number,
        "note": note,
        "transactionType": "repayment",
    }
    try:
        status, data = loan_transaction(
            tenant_id, payload
        )
        if status == 200:
            print(f"Claim Recept response data: {data}")
            return data
        return None
    except Exception as e:
        print("Something went wrong receipting claim repayment")
        print(e)


def create_claim_payment(payment):
    payment.save()
