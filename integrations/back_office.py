import requests

from FinCover.settings import BACK_OFFICE_URL


def __make_backoffice_request(tenant_id, uri, payload):
    back_office_url = generate_back_office_url(tenant_id, uri)
    return requests.post(
        url=back_office_url,
        json=payload,
        headers={
            "content-type": 'application/json',
        },
    )


def generate_back_office_url(tenant: str, path: str = '') -> str:
    base_url = BACK_OFFICE_URL
    base_domain = base_url.replace('https://', '').replace('http://', '')
    tenant_subdomain = f'{tenant}.{base_domain}'
    full_url = f'https://{tenant_subdomain}{path}'
    return full_url
