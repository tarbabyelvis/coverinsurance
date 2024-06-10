import traceback
from datetime import datetime

from claims.models import Claim
from claims.serializers import ClaimSerializer
from config.enums import PolicyType
from core.utils import first_day_of_previous_month, last_day_of_previous_month
from integrations.enums import Integrations
from integrations.guardrisk.guardrisk import GuardRisk
from integrations.models import IntegrationConfigs
from jobs.models import TaskLog
from policies.models import Policy
from policies.serializers import PolicyDetailSerializer
from .models import Task

first_day_of_previous_month = first_day_of_previous_month()
last_day_of_previous_month = last_day_of_previous_month()
today_start_date = datetime.today()
today_end_date = datetime.today()


def daily_job_postings():
    

def credit_life_daily(start_date=today_start_date, end_date=today_end_date):
    __credit_life(start_date, end_date)


def credit_life(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    __credit_life(start_date, end_date, False)


def __credit_life(
        start_date, end_date, is_daily_submission=True
):
    nifty_integration_configs = fetch_configs(identifier='Nifty Cover')
    indlu_integration_configs = fetch_configs(identifier='Indlu')
    try:
        # fetch the data
        policies = __fetch_policies(start_date, end_date, PolicyType.CREDIT_LIFE)

        if not policies.exists():
            print("Empty")
            raise Exception("Policies are empty")

        policies_data = PolicyDetailSerializer(policies, many=True).data
        nifty_policies_filter = filter(lambda p: p.entity == 'Nifty Cover', policies_data)
        indlu_policies_filter = filter(lambda p: p.entity == 'Indlu', policies_data)
        nifty_policies = list(nifty_policies_filter)
        indlu_policies = list(indlu_policies_filter)

        process_credit_life(nifty_policies, nifty_integration_configs, is_daily_submission)
        process_credit_life(indlu_policies, indlu_integration_configs, is_daily_submission)
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception(e)


def process_credit_life(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('Credit Life Daily' if is_daily_submission else 'Credit Life Monthly')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        daily_function_called = guard_risk.life_credit_daily(data, start_date, end_date, client_identifier)
        monthly_function_called = guard_risk.life_credit(data, start_date, end_date, client_identifier)
        data, response_status = daily_function_called if is_daily_submission else monthly_function_called
        print(response_status)
        log.data = data
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        traceback.print_exc()
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def life_funeral_daily(start_date=today_start_date, end_date=today_end_date):
    __life_funeral(start_date, end_date)


def life_funeral(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    __life_funeral(start_date, end_date, False)


def __life_funeral(
        start_date, end_date, is_daily_submission=True
):
    nifty_integration_configs = fetch_configs(identifier='Nifty Cover')
    try:
        # fetch the data
        policies = __fetch_policies(start_date, end_date, PolicyType.FUNERAL_COVER)

        if not policies.exists():
            print("Empty")
            raise Exception("Policies are empty")

        policies_data = PolicyDetailSerializer(policies, many=True).data
        nifty_policies_filter = filter(lambda p: p.entity == 'Nifty Cover', policies_data)
        nifty_policies = list(nifty_policies_filter)

        process_life_funeral(nifty_policies, nifty_integration_configs, is_daily_submission)
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception(e)


def process_life_funeral(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('Life Funeral Daily' if is_daily_submission else 'Life Funeral Monthly')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        daily_function_called = guard_risk.life_funeral_daily(data, start_date, end_date, client_identifier)
        monthly_function_called = guard_risk.life_funeral(data, start_date, end_date, client_identifier)
        data, response_status = daily_function_called if is_daily_submission else monthly_function_called
        print(response_status)
        log.data = data
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        traceback.print_exc()
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def claims_daily(start_date=today_start_date, end_date=today_end_date):
    __claims(start_date, end_date)


def claims(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    __claims(start_date, end_date, False)


def __claims(
        start_date, end_date, is_daily_submission=True
):
    nifty_integration_configs = fetch_configs(identifier='Nifty Cover')
    indlu_integration_configs = fetch_configs(identifier='Indlu')
    try:
        # fetch the data
        fetched_claims = __fetch_claims(start_date, end_date)

        if not fetched_claims.exists():
            print("Empty")
            raise Exception("Claims are empty")

        claims_data = ClaimSerializer(fetched_claims, many=True).data
        nifty_claims_filter = filter(lambda p: p.entity == 'Nifty Cover', claims_data)
        indlu_claims_filter = filter(lambda p: p.entity == 'Indlu', claims_data)
        nifty_claims = list(nifty_claims_filter)
        indlu_claims = list(indlu_claims_filter)

        process_claims(nifty_claims, nifty_integration_configs, is_daily_submission)
        process_claims(indlu_claims, indlu_integration_configs, is_daily_submission)
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception(e)


def process_claims(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('Claims Daily' if is_daily_submission else 'Claims Monthly')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        daily_function_called = guard_risk.life_claims_global_daily(data, start_date, end_date, client_identifier)
        monthly_function_called = guard_risk.life_claims_global(data, start_date, end_date, client_identifier)
        data, response_status = daily_function_called if is_daily_submission else monthly_function_called
        print(response_status)
        log.data = data
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        traceback.print_exc()
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def fetch_tasks(identifier):
    return Task.objects.filter(task=identifier).first()


def fetch_configs(identifier):
    return IntegrationConfigs.objects.get(
        name=Integrations.GUARDRISK.name, is_enabled=True, entity=identifier
    )


def create_task_logs(task: Task):
    return TaskLog.objects.create(task=task, status="running", manual_run=True)


def __fetch_policies(start_date: datetime, end_date: datetime, policy_type: PolicyType):
    return Policy.objects.filter(
        commencement_date__gte=start_date,
        commencement_date__lte=end_date,
        policy_type__policy_type=policy_type.name
    )


def __fetch_claims(start_date: datetime, end_date: datetime):
    return Claim.objects.filter(
        submitted_date__gte=start_date,
        submitted_date__lte=end_date,
    )
