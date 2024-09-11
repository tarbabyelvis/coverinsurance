import json

import requests
from supabase import create_client, Client

from FinCover.settings import SUPABASE_URL, SUPABASE_POSTGREST_URL, SUPABASE_TOKEN

supabase: Client = create_client(SUPABASE_POSTGREST_URL, SUPABASE_TOKEN)


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


def query_premium_adjustments(tenant_id):
    json_payload = {
        "reportName": "Premiums Correction"
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def query_loans_past_due(tenant_id):
    json_payload = {
        "reportName": "Days Past Due"
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def query_closed_loans(tenant_id, start_date, end_date):
    json_payload = {
        "reportName": "Loan Closure - Creation Details",
        "payload": {
            "R_startDate": __serialize_dates(start_date),
            "R_endDate": __serialize_dates(end_date),
        }
    }
    return __fetch_data(tenant_id, json_payload, "/query-report")


def query_loan(tenant_id, loan_id: str):
    json_payload = {
        "loan_id": loan_id
    }
    return __fetch_data(tenant_id, json_payload, "/query-loan")


def suspend_debicheck(tenant_id, loan_id: str):
    print('requesting to suspend debicheck...')
    json_payload = {
        "loanId": loan_id
    }
    return __fetch_data(tenant_id, json_payload, "/intecon-suspend-kickoff")


def activate_debicheck(tenant_id, loan_id: str):
    json_payload = {
        "loanId": loan_id
    }
    return __fetch_data(tenant_id, json_payload, "/intecon-activate-kickoff")


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


def send_sms_messages(messages):
    if len(messages) == 0:
        return None
    return __insert_data(data=messages, table_name='comms_logs')


def loan_transaction(tenant_id, payload):
    print(f'sending loan transaction details:: {payload}')
    return __fetch_data(tenant_id, payload, "/loan-transaction")


def __fetch_data(tenant_id, payload, uri, max_retries=2):
    attempt = 0
    status = 0
    message = "Failed"
    data = None
    while attempt < max_retries:
        response = __make_request(tenant_id, payload, uri)
        status, message, data = __process_response(response)
        if status == 200 or status == 201:
            return status, message, data
        else:
            attempt += 1
            print(f'attempt {attempt} for payload {json.dumps(payload)}')
    return status,message, data


def __make_request(tenant_id, payload, uri):
    return requests.post(
        SUPABASE_URL + uri,
        json=payload,
        headers={
            "tenant-id": tenant_id,
            "Authorization": "Bearer {}".format(SUPABASE_TOKEN),
        },
    )


def __process_response(response):
    try:
        print(f'response: {response}')
        response_json = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON from response")
        response_json = {}

    if isinstance(response_json, dict):
        message = response_json.get("message")
        if isinstance(message, dict) and is_successful_response(message):
            return message.get("result"), message.get("message"), message.get("data")
        result = message.get("result") if isinstance(message, dict) else None
        message = message.get("message")
        return result, message, None
    else:
        print("Response JSON is not a dictionary")
        return 0, "Failed", None


def __insert_data(data, table_name):
    response = supabase.table(table_name).insert(data).execute()
    print(f'response: {response}')
    status, message, data = __process_response(response)
    print(f'response status: {status} :: data: {data}')
    if status == 201:
        return status, message, data
    return status, "Failed", None


def is_successful_response(message):
    return message.get("result") in [200, 201, 100]
