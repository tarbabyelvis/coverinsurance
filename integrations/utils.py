import re
from datetime import datetime, timedelta, date
from dateutil import parser

import requests
from integrations.models import IntegrationLogs


def post_request_and_save(request_data, url, headers, service):
    try:
        print(f'url {url} headers {headers}')
        response = requests.post(url, json=request_data, headers=headers)
        print(f'response :: {response}')
        response_data = response.json()

        response_status = response.status_code
        if response_status == 200:
            status = "Success"
        else:
            status = "Error"
    except requests.exceptions.RequestException as e:
        print(f'Error on posting request: {e}')
        response_data = {"error": str(e)}
        response_status = 400
        status = "Error"

    # Save request and response data to the database
    request_and_response = IntegrationLogs.objects.create(
        request_data=request_data,
        response_data=response_data,
        response_status=response_status,
        status=status,
        service=service,
    )

    return response_data, response_status, request_and_response


def get_frequency_number(frequency: str):
    if frequency == 'Monthly':
        return "12"
    elif frequency == 'Quarterly':
        return "4"
    elif frequency == 'Bi-Annually' or frequency == 'Semi Annual' or frequency == 'Bi Annual':
        return "2"
    elif frequency == 'Annually' or frequency == 'Annual':
        return "1"
    else:
        return "0"


def is_new_policy(commencement_date, reporting_period_start,
                  reporting_period_end) -> str:  # TODO add the transferred T and R Replacement adjustments
    if isinstance(commencement_date, str):
        commencement_date = parser.parse(commencement_date).date()
    if isinstance(reporting_period_start, str):
        reporting_period_start = parser.parse(reporting_period_start).date()
    if isinstance(reporting_period_end, str):
        reporting_period_end = parser.parse(reporting_period_end).date()
    if reporting_period_start <= commencement_date <= reporting_period_end:
        return 'Y'
    else:
        return 'N'


def generate_claim_reference(claimant_id: str, policy_number: str) -> str:
    current_date = datetime.now().strftime('%Y%m%d')
    return f"{claimant_id}:{policy_number}-{current_date}"


def generate_payment_reference(policy_number: str, payment_date) -> str:
    return f"{policy_number}-{payment_date}"


def calculate_commission_amount(premium_amount) -> float:
    return round(0.075 * premium_amount, 2)


def calculate_guard_risk_admin_amount(premium_amount) -> float:
    return round(0.05 * premium_amount, 2)


def calculate_binder_fees_amount(premium_amount) -> float:
    return round(0.09 * premium_amount, 2)


def calculate_nett_amount(premium_amount: float,
                          guardrisk_amount: float,
                          commission: float,
                          binder_fee: float) -> float:
    return round((premium_amount - guardrisk_amount - commission - binder_fee), 2)


def calculate_vat_amount(premium_amount: float) -> float:
    return round(0.15 * premium_amount, 2)


def calculate_amount_excluding_vat(premium_amount: float, vat_amount) -> float:
    return round((premium_amount - vat_amount), 2)


def populate_dependencies(other_dependants, details):
    for dependant in other_dependants:
        full_name = dependant["dependant_name"]
        print('full_name', full_name)
        full_name = full_name.split(" ")
        if len(full_name) == 1:
            details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
            details[f"Dependent{dependant['index']}Initials"] = ""
            details[f"Dependent{dependant['index']}Surname"] = ""
        elif len(full_name) == 2:
            details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
            details[f"Dependent{dependant['index']}Initials"] = ""
            details[f"Dependent{dependant['index']}Surname"] = full_name[1]
        elif len(full_name) == 3:
            details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
            details[f"Dependent{dependant['index']}Initials"] = full_name[1]
            details[f"Dependent{dependant['index']}Surname"] = full_name[2]
        else:
            details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
            details[f"Dependent{dependant['index']}Initials"] = " ".join(
                full_name[1:-1]
            )
            details[f"Dependent{dependant['index']}Surname"] = full_name[-1]

        details[f"Dependent{dependant['index']}ID"] = dependant[
            "primary_id_number"
        ]
        details[f"Dependent{dependant['index']}Gender"] = dependant[
            "dependant_gender"
        ]
        details[f"Dependent{dependant['index']}DateofBirth"] = dependant[
            "dependant_dob"
        ]
        details[f"Dependent{dependant['index']}Type"] = dependant["type"]
        details[f"Dependent{dependant['index']}CoverAmount"] = dependant["cover_amount"]
        details[f"Dependent{dependant['index']}CoverCommencementDate"] = dependant["cover_commencement_date"]
