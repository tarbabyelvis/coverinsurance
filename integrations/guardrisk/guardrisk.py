from integrations.enums import Integrations
from integrations.guardrisk.data.life_claims_global import prepare_life_claims_payload
from integrations.guardrisk.data.life_credit import prepare_life_credit_payload
from integrations.guardrisk.data.life_funeral import (
    prepare_life_funeral_payload,
)
from integrations.utils import post_request_and_save


class GuardRisk:
    def __init__(self, access_key, base_url):
        self.access_key = access_key
        self.base_url = base_url

    # critical
    def life_claims_global(self, claim_data):
        path = "/DeltaV2/api/LifeClaimsGlobal"
        request_data = prepare_life_claims_payload(claim_data)

        url = self.base_url + path
        headers = {"CallerId": self.base_url, "RowCount": str(len(request_data))}

        # Call the function to post the request and save it along with the response
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK
        )

        return response_data, response_status

    # critical
    def lifeFuneral(self, data):
        path = "/DeltaV2/api/LifeFuneral"
        request_data = prepare_life_funeral_payload(data)

        url = self.base_url + path
        headers = {"CallerId": self.base_url, "RowCount": str(len(request_data))}

        # Call the function to post the request and save it along with the response
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK
        )

        return response_data, response_status

    # critical
    def lifeCredit(self, data, start_date, end_date):
        path = "/DeltaV2/api/LifeCredit"
        request_data = prepare_life_credit_payload(data, start_date, end_date)

        url = self.base_url + path
        headers = {"CallerId": self.access_key, "RowCount": str(len(request_data))}

        # Call the function to post the request and save it along with the response
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK
        )

        return response_data, response_status
