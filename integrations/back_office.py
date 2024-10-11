import json

import requests

from FinCover.settings import BACK_OFFICE_URL


def __make_backoffice_request(tenant_id, uri, payload):
    back_office_url = generate_back_office_url(tenant_id, uri)
    response = requests.post(
        url=back_office_url,
        json=payload,
        headers={
            "content-type": 'application/json',
        },
    )
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON from response")
        return 0, {}

    return 200, response_json


def generate_back_office_url(tenant: str, path: str = '') -> str:
    base_url = BACK_OFFICE_URL
    base_domain = base_url.replace('https://', '').replace('http://', '')
    tenant_subdomain = f'{tenant}.{base_domain}'
    full_url = f'https://{tenant_subdomain}{path}'
    return full_url
