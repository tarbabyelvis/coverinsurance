import requests
from integrations.models import IntegrationLogs


def post_request_and_save(request_data, url, headers, service):
    try:
        response = requests.post(url, json=request_data, headers=headers)

        response_data = response.json()

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
    elif frequency == 'Bi-Annually':
        return 2
    elif frequency == 'Annually':
        return 1
    else:
        return 0
