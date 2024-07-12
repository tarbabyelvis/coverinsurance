import json

import requests

from FinCover.settings import SUPABASE_URL, SUPABASE_TOKEN


def query_new_loans(tenant_id, start_date, end_date):
    json_payload = {
        "reportName": "Disbursal - v2 Detailed",
        "payload": {
            "R_startDate": __serialize_dates(start_date),
            "R_endDate": __serialize_dates(end_date),
        }
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def __serialize_dates(date) -> str:
    return date.strftime("%Y-%m-%d")


def query_repayments(tenant_id, start_date, end_date):
    json_payload = {
        "reportName": "Collections - v2 Detailed",
        "payload": {
            "R_startDate": __serialize_dates(start_date),
            "R_endDate": __serialize_dates(end_date),
        }
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def query_closed_loans(tenant_id, start_date, end_date):
    json_payload = {
        "reportName": "Loan Closure",
        "payload": {
            "R_startDate": __serialize_dates(start_date),
            "R_endDate": __serialize_dates(end_date),
        }
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def query_written_off_loans(tenant_id, start_date, end_date):
    json_payload = {
        "reportName": "Written-Off Loans Summed",
        "payload": {
            "R_currencyId": "-1",
            "R_loanProductId": "-1",
            "R_officeId": "1",
            "R_startDate": __serialize_dates(start_date),
            "R_endDate": __serialize_dates(end_date),
        }
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def __fetch_data(tenant_id, payload, uri):
    status = 0
    data = []
    response = requests.post(
        SUPABASE_URL + uri,
        json=payload,
        headers={
            "tenant-id": tenant_id,
            "Authorization": "Bearer {}".format(SUPABASE_TOKEN),
        },
    )
    print(f'response: {response}')
    response = json.loads(response.text)
    if response["message"]["result"] == 200:
        status = 200
        data = response["message"]["data"]

    return status, data
