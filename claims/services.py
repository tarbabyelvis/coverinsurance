from datetime import datetime

from rest_framework.exceptions import NotFound

from claims.models import Claim, Payment
from config.models import PaymentAccount
from integrations.superbase import loan_transaction


def process_claim_payment(tenant_id, claim_id):
    claim = __find_claim_id(claim_id)
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


def __find_claim_id(claim_id):
    claim = Claim.objects.filter(id=claim_id).first()
    if claim is None:
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
