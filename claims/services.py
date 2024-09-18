from datetime import datetime, date, timedelta

from rest_framework.exceptions import NotFound

from claims.models import Claim, Payment
from claims.serializers import ClaimSerializer
from config.models import PaymentAccount
from core.enums import ClaimStatus, PaymentStatus
from core.utils import serialize_dates
from integrations.superbase import loan_transaction, suspend_debicheck, query_loan, activate_debicheck
from policies.models import Policy

DEATH = 1
RETRENCHMENT = 34
DISABILITY = 35


def process_claim(tenant_id, claim_id):
    try:
        claim = __find_claim_by_id(claim_id)
        claim_serializer = ClaimSerializer(claim)
        claim_data = claim_serializer.data
        print(f'claim :: {claim_data}')
        claim_type = claim_data['claim_type']
        loan_id = get_loan_id_from_claim_id(claim_data)
        start_date = claim_data['submitted_date']
        number_of_months_to_claim = -1 if claim_type == DEATH else 6  # Claim for all the months that were left for death claim otherwise take the months passed
        print(f'fetching repayment schedule for loan id {loan_id} for claim {claim_id}')
        status, repayment_schedule = find_next_n_months_installments(tenant_id, loan_id, start_date,
                                                                     number_of_months_to_claim)
        print(f'schedule status: {status} :: {repayment_schedule}')
        if status == 200:
            print('successful schedule fetch')
            if claim_type == RETRENCHMENT:
                status, message, data = suspend_debicheck(tenant_id=tenant_id, loan_id=loan_id)
                print(f'suspension status {status}, message {message}, suspend data {data}')
                if status == 200 or message == 'Intecon Contract already suspended':
                    total_amount = calculate_total_installment_amount(repayment_schedule)
                    update_claim_repayment_schedule_details(claim, total_amount, repayment_schedule)
            elif claim_type == DEATH:
                total_amount = calculate_total_installment_amount(repayment_schedule)
                update_claim_suspension_details(claim, start_date, number_of_months_to_claim, total_amount, claim_type)
        else:
            print('no installments found')
    except Exception as e:
        print(e)


def update_claim_repayment_schedule_details(claim, total_amount, repayment_schedule):
    claim_details = claim.claim_details or {}
    claim_details['retrenchment_amount_claimed'] = total_amount
    claim_details['repayment_schedule_claimed'] = repayment_schedule
    claim.claim_details = claim_details
    try:
        claim.claim_status = ClaimStatus.ON_ASSESSMENT
        claim.save()
    except Exception as e:
        print(e)


def update_claim_suspension_details(claim, start_date, number_of_months, total_amount, claim_type):
    claim_details = claim.claim_details or {}
    claim_details['debicheck_suspended'] = True
    claim_details['debicheck_suspension_from'] = start_date
    if claim_type == 'Retrenchment':
        debicheck_expiry_date = calculate_debicheck_expiry_date(start_date, number_of_months)
        claim_details['debicheck_suspension_to'] = debicheck_expiry_date
    claim_details['retrenchment_amount_claimed'] = total_amount
    claim.claim_details = claim_details
    try:
        claim.claim_status = ClaimStatus.APPROVED
        claim.save()
    except Exception as e:
        print(e)


def find_next_n_months_installments(tenant_id, loan_id, start_date, number_of_months: int = 6):
    try:
        response_status, message, data = query_loan(tenant_id, loan_id)
        print(f'response status: {response_status}, message: {message}, data: {data}')
        if response_status == 200:
            periods = data['repaymentSchedule']['periods']
            start_date = parse_date(start_date)
            next_periods = sorted(
                (p for p in periods if parse_date(p["dueDate"]) > start_date),
                key=lambda p: parse_date(p["dueDate"])
            )
            if number_of_months != -1:
                next_periods = next_periods[:number_of_months]
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


def parse_date(date_passed):
    if isinstance(date_passed, list):
        return parse_date_array(date_passed)
    elif isinstance(date_passed, str):
        return datetime.strptime(date_passed, '%Y-%m-%d').date()
    return date_passed


def parse_date_array(date_array):
    year, month, day = date_array
    return date(year, month, day)


def get_loan_id_from_claim_id(claim):
    policy_id = claim['policy']
    policy = Policy.objects.get(id=policy_id)
    return policy.loan_id


def process_claim_payment(
        tenant_id,
        claim_id,
        claim_amount,
        payment_date,
        notes,
        receipt_number,
        receipted_by,
        payment_method
):
    claim = __find_claim_by_id(claim_id)
    claim_serializer = ClaimSerializer(claim)
    claim_data = claim_serializer.data
    loan_id = get_loan_id_from_claim_id(claim_data)
    payment_account = get_payment_account_details()
    claim_amount = claim_amount
    # notes = f"Refinance of loan {loan_id} FinCover claim {claim_id}"
    claim_payment = Payment(
        transaction_date=payment_date,
        amount=claim_amount,
        transaction_type='repayment',
        notes=notes,
        receipt_number=receipt_number,
        receipted_by=receipted_by,
        payment_method=payment_method,
    )
    try:
        status, message, data = receipt_claim_repayment(
            tenant_id=tenant_id,
            loan_id=loan_id,
            transaction_amount=claim_amount,
            note=notes,
            payment_account=payment_account,
            transaction_date=payment_date
        )
        print(f'receipting status {status}, message {message}, data {data}')
        if __is_successful(status):
            claim_payment.status = PaymentStatus.SUCCESSFUL
            claim_payment.save()
            return
        claim_payment.status = PaymentStatus.FAILED
        claim_payment.save()
        print(f'failed to make repayment!')
    except Exception as e:
        print(e)
        raise e


def __is_successful(response_code):
    return response_code in [200, 201]


def get_payment_account_details():
    payment_account = PaymentAccount.objects.filter(name='INSURANCE').first()
    if payment_account is None:
        raise PaymentAccount.DoesNotExist("Payment account not configured")
    return payment_account


def generate_receipt_number(claim_id, policy_number, transaction_date):
    return f'{claim_id}_{policy_number}_{transaction_date}'


def __find_claim_by_id(claim_id: int):
    claim = Claim.objects.filter(id=claim_id).first()
    if not claim:
        raise NotFound("Claim with id {} not found".format(claim_id))
    return claim


def receipt_claim_repayment(tenant_id, loan_id, transaction_amount, note,
                            payment_account, transaction_date):
    transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
    payment_type_id = payment_account.payment_type_id

    payload = {
        "loanId": loan_id,
        "transactionDate": transaction_date,
        "note": note,
        "transactionType": "repayment",
        "paymentTypeId": payment_type_id,
        "transactionAmount": transaction_amount,

    }
    return loan_transaction(tenant_id, payload)


def create_claim_payment(payment):
    payment.save()


def approve_claim(tenant_id, claim_id):
    claim = __find_claim_by_id(claim_id)
    claim.claim_status = ClaimStatus.APPROVED
    claim.save()


def repudiate_claim(tenant_id, claim_id, repudiation_reason, repudiated_by):
    claim = __find_claim_by_id(claim_id)
    claim.claim_status = ClaimStatus.REPUDIATED
    claim.repudiated_reason = repudiation_reason
    claim.repudiated_date = datetime.today().date()
    claim.repudiated_by = repudiated_by
    claim.save()


def reactivate_debicheck(tenant_id, claim_id):
    claim = __find_claim_by_id(claim_id)
    claim_serializer = ClaimSerializer(claim)
    claim_data = claim_serializer.data
    loan_id = get_loan_id_from_claim_id(claim_data)
    try:
        status, message, data = activate_debicheck(tenant_id, loan_id)
        if status == 200:
            claim_details = claim.claim_details or {}
            claim_details['debicheck_suspended'] = False
            claim_details['debicheck_suspension_from'] = None
            claim_details['debicheck_suspension_to'] = None
            claim.claim_details = claim_details
            claim.save()
            return 200
    except Exception as e:
        print(e)
    return 0
