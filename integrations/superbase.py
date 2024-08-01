import json
import time
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
        "reportName": "Loan Closure - Creation Details",
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
    max_retries = 3
    attempt = 0
    status = 0
    while attempt < max_retries:
        response = make_request(tenant_id, payload, uri)
        status, data = process_response(response)
        if status == 200:
            return status, data
        else:
            attempt += 1
    return status, None


def make_request(tenant_id, payload, uri):
    return requests.post(
        SUPABASE_URL + uri,
        json=payload,
        headers={
            "tenant-id": tenant_id,
            "Authorization": "Bearer {}".format(SUPABASE_TOKEN),
        },
    )


def process_response(response):
    try:
        response_json = response.json()  # Use response.json() instead of json.loads(response.text)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response")
        response_json = {}

    # Check if response_json is a dictionary
    if isinstance(response_json, dict):
        message = response_json.get("message")
        if isinstance(message, dict) and message.get("result") == 200:
            return 200, message.get("data")
        else:
            result = message.get("result") if isinstance(message, dict) else None
            return result, None
    else:
        print("Response JSON is not a dictionary")
        return 0, None

