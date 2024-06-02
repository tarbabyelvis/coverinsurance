import traceback
from datetime import datetime

from claims.models import Claim
from claims.serializers import ClaimSerializer
from config.enums import PolicyType
from core.utils import first_day_of_previous_month, last_day_of_previous_month, get_current_schema
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


def credit_life_daily(start_date=today_start_date, end_date=today_end_date):
    identifier = "CREDIT_LIFE_DAILY"
    __credit_life(identifier, start_date, end_date)


def credit_life(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    identifier = "CREDIT_LIFE"
    __credit_life(identifier, start_date, end_date)


def __credit_life(
        identifier, start_date, end_date
):
    task = fetch_tasks(identifier)
    integration = fetch_configs(identifier)
    log = create_task_logs(task)
    try:
        # fetch the data
        policy = __fetch_policies(start_date, end_date, PolicyType.CREDIT_LIFE)

        if not policy.exists():
            print("Empty")
            raise Exception("Policies are empty")

        serializer = PolicyDetailSerializer(policy, many=True).data
        guardrisk = GuardRisk(integration.access_key, integration.base_url)
        is_daily_submission = identifier == "CREDIT_LIFE_DAILY"
        daily_function_called = guardrisk.life_credit_daily(serializer, start_date, end_date,
                                                            'Getsure')  # TODO Add the clientAdmin company pproperly
        monthly_function_called = guardrisk.life_credit(serializer, start_date, end_date, 'Getsure')
        data, response_status = daily_function_called if is_daily_submission else monthly_function_called
        log.data = data
        print(response_status)
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


def funeral_cover_daily(start_date=today_start_date, end_date=today_end_date):
    identifier = "LIFE_FUNERAL_DAILY"
    __funeral_cover(identifier, start_date, end_date)


def funeral_cover(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    identifier = "LIFE_FUNERAL"
    __funeral_cover(identifier, start_date, end_date)


def __funeral_cover(identifier, start_date, end_date):
    task = fetch_tasks(identifier)
    integration = fetch_configs(identifier)
    log = create_task_logs(task)
    try:
        # fetch the data
        policy = __fetch_policies(
            start_date,
            end_date,
            PolicyType.FUNERAL_COVER,
        )
        if not policy.exists():
            print("Empty")
            raise Exception("Policies are empty")

        serializer = PolicyDetailSerializer(policy, many=True).data
        guardrisk = GuardRisk(integration.access_key, integration.base_url)
        is_daily = identifier == "FUNERAL_COVER_DAILY"
        daily_function_called = guardrisk.life_funeral_daily(serializer, start_date, end_date)
        monthly_function_called = guardrisk.life_funeral(serializer, start_date, end_date)
        data, response_status = daily_function_called if is_daily else monthly_function_called
        log.data = data
        print(response_status)
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        log.status = "failed"
        log.save()


def life_claims_daily(start_date=today_start_date, end_date=today_end_date):
    identifier = "LIFE_CLAIMS_DAILY"
    __life_claims(identifier, start_date, end_date)


def life_claims(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    identifier = "LIFE_CLAIMS"
    __life_claims(identifier, start_date, end_date)


def __life_claims(
        identifier, start_date, end_date
):
    task = fetch_tasks(identifier)
    integration = fetch_configs(identifier)
    log = create_task_logs(task)
    schema = get_current_schema()
    print(f'current_schema: {schema}')
    try:
        claims = __fetch_claims(start_date, end_date)
        if not claims.exists():
            print("Empty")
            raise Exception("Claims are empty")

        serializer = ClaimSerializer(claims, many=True).data
        guardrisk = GuardRisk(integration.access_key, integration.base_url)
        is_daily_submission = identifier == "LIFE_CLAIMS_DAILY"
        daily_function_called = guardrisk.life_claims_global_daily(serializer, start_date, end_date)
        monthly_function_called = guardrisk.life_claims_global(serializer, start_date, end_date)
        data, response_status = daily_function_called if is_daily_submission else monthly_function_called
        log.data = data
        print(response_status)
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
        policy_type__policy_type=policy_type.name,
    )


def __fetch_claims(start_date: datetime, end_date: datetime):
    return Claim.objects.filter(
        submitted_date__gte=start_date,
        submitted_date__lte=end_date,
    )
