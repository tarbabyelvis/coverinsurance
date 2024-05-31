import re

import requests
from integrations.models import IntegrationLogs


def post_request_and_save(request_data, url, headers, service):
    try:
        response = requests.post(url, json=request_data, headers=headers)

        response_data = response.json()
        print(f'response gotten:: {response_data}')

        response_status = response.status_code
        if response_status == 200:
            status = "Success"
        else:
            status = "Error"
    except requests.exceptions.RequestException as e:
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


def get_frequency_number(frequency):
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


def extract_field(json_str, field):
    pattern = fr'"{field}":\s*"(.*?)"'
    match = re.search(pattern, json_str)
    return match.group(1) if match else None


def extract_nested_field(json_str, parent_field, nested_field):
    parent_pattern = fr'"{parent_field}":\s*{{(.*?)}}'
    parent_match = re.search(parent_pattern, json_str, re.DOTALL)
    if parent_match:
        parent_str = parent_match.group(1)
        return extract_field(parent_str, nested_field)
    return None
