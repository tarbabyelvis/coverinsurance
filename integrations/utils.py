import re
from datetime import datetime, timedelta

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
        response_status = None
        status = "Error"

    # Save request and response data to the database
    life_payments_request = IntegrationLogs.objects.create(
        request_data=request_data,
        response_data=response_data,
        response_status=response_status,
        status=status,
        service=service,
    )

    return response_data, response_status, life_payments_request


def get_frequency_number(frequency: str):
    if frequency == 'Monthly':
        return 12
    elif frequency == 'Quarterly':
        return 4
    elif frequency == 'Bi-Annually' or frequency == 'Semi Annual' or frequency == 'Bi Annual':
        return 2
    elif frequency == 'Annually' or frequency == 'Annual':
        return 1
    else:
        return 0


def is_new_policy(created_date_time: str) -> str:  # TODO add the transferred T and R Replacement adjustments
    created_date = datetime.strptime(created_date_time, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    yesterday = datetime.now() - timedelta(days=1)
    created_yesterday = created_date == yesterday.date()
    return 'P' if created_yesterday else 'N'


def generate_claim_reference(claimant_id: str, policy_number: str) -> str:
    current_date = datetime.now().strftime('%Y%m%d')
    return f"{claimant_id}:{policy_number}-{current_date}"


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
