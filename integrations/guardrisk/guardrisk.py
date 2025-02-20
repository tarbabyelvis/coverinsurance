from integrations.enums import Integrations
from integrations.guardrisk.data.life_claims_global import prepare_life_claims_payload
from integrations.guardrisk.data.life_credit import prepare_life_credit_payload
from integrations.guardrisk.data.life_funeral import (
    prepare_life_funeral_payload,
)
from integrations.guardrisk.data.premiums import prepare_premium_payload
from integrations.utils import post_request_and_save


def create_url(base: str, path: str):
    return base + path


class GuardRisk:
    def __init__(self, access_key, base_url):
        self.access_key = access_key
        self.base_url = base_url

    # critical
    def life_claims_monthly(self, claim_data, start_date, end_date, client_identifier):
        path = "/DeltaV2/api/LifeClaimsGlobal"
        return self.__life_claims(claim_data, start_date, end_date, path, client_identifier)

    def life_claims_daily(self, claim_data, start_date, end_date, client_identifier):
        path = "/DeltaV2/api/LifeClaimsGlobalDaily"
        return self.__life_claims(claim_data, start_date, end_date, path, client_identifier)

    def __life_claims(self, claim_data, start_date, end_date, path, client_identifier):
        request_data = prepare_life_claims_payload(claim_data, start_date, end_date, client_identifier)
        url = create_url(self.base_url, path)
        data_size = len(request_data)
        print(f'submitting {data_size} claims')

        headers = {"CallerId": self.access_key,
                   "RowCount": str(data_size)}
        print(f'claims json being sent {request_data}')
        # Call the function to post the request and save it along with the response
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK.name
        )
        return response_data, response_status

    # critical

    def life_funeral_monthly(self, data, start_date, end_date, client_identifier):
        path = "/DeltaV2/api/LifeFuneral"
        return self.__life_funeral(data, start_date, end_date, path, client_identifier)

    def life_funeral_daily(self, data, start_date, end_date, client_identifier):
        path = "/DeltaV2/api/LifeFuneralDaily"
        return self.__life_funeral(data, start_date, end_date, path, client_identifier)

    def __life_funeral(self, data, start_date, end_date, path, client_identifier):
        request_data = prepare_life_funeral_payload(data, start_date, end_date, client_identifier)
        url = create_url(self.base_url, path)
        data_size = len(request_data)
        print(f'submitting {data_size} funeral policies')

        headers = {"CallerId": self.access_key,
                   "RowCount": str(data_size)}
        # Call the function to post the request and save it along with the response
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK.name
        )

        return response_data, response_status

    # critical
    def life_credit_monthly(self, data, start_date, end_date, client_identifier):
        path = "/DeltaV2/api/LifeCredit"
        print('calling life credit api...')
        return self.__life_credit(data, start_date, end_date, path, client_identifier)

    def life_credit_daily(self, data, start_date, end_date, client_identifier):
        path = "/DeltaV2/api/LifeCreditDaily"
        return self.__life_credit(data, start_date, end_date, path, client_identifier)

    def __life_credit(self, data, start_date, end_date, path, client_identifier):
        request_data = prepare_life_credit_payload(
            data, start_date, end_date, client_identifier
        )
        data_size = len(request_data)
        print(f'submitting {data_size} credit life policies')

        url = create_url(self.base_url, path)
        headers = {"CallerId": self.access_key,
                   "RowCount": str(data_size)}
        # Call the function to post the request and save it along with the response
        print(f'credit life json being sent {request_data}')
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK.name
        )
        print(f'response data being sent {response_data}')

        return response_data, response_status

    def life_premiums_monthly(self, data, start_date, end_date):
        path = "/DeltaV2/api/STPremiums"
        print('calling premium api...')
        return self.__premiums(data, start_date, end_date, path)

    def life_premiums_daily(self, data, start_date, end_date):
        path = "/DeltaV2/api/STPremiumsDaily"
        return self.__premiums(data, start_date, end_date, path)

    def __premiums(self, data, start_date, end_date, path):
        request_data = prepare_premium_payload(
            data, start_date, end_date
        )
        data_size = len(request_data)
        print(f'submitting {data_size} premiums')

        url = create_url(self.base_url, path)
        headers = {"CallerId": self.access_key,
                   "RowCount": str(data_size)}
        # Call the function to post the request and save it along with the response
        response_data, response_status, _ = post_request_and_save(
            request_data, url, headers, Integrations.GUARDRISK.name
        )
        return response_data, response_status
