from datetime import datetime

from rest_framework.response import Response

from integrations.superbase import loan_transaction


def receipt_claim_repayment(tenant_id, loan_id, payment_type_id, transaction_amount, account_number, check_number,
                            routing_code, receipt_cumber, bank_number, note):
    transaction_date = datetime.now().strftime('%Y-%m-%d')

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
        "receiptNumber": receipt_cumber,
        "bankNumber": bank_number,
        "note": note,
        "transactionType": "repayment",
    }
    try:
        request_status, request_data = loan_transaction(
            tenant_id, payload
        )
        print("Request status: ", request_status)
        if request_status == 200:
            print("Request data: ", request_data)
            # return Response(request_data, status=status.HTTP_201_CREATED)

        else:
            print("Error submitting a repayment")
            # return Response(request_data, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error submitting a repayment')
