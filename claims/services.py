


def process_death_claim():
    payload = {
        "loanId": loanId,
        "paymentTypeId": paymentTypeId,
        "transactionAmount": transactionAmount,
        "transactionDate": transactionDate,
        "accountNumber": accountNumber,
        "checkNumber": checkNumber,
        "routingCode": routingCode,
        "receiptNumber": receiptNumber,
        "bankNumber": bankNumber,
        "note": note,
        "transactionType": "repayment",
    }

