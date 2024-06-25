import traceback
from datetime import datetime, date

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

first_day_of_previous_month: date = first_day_of_previous_month()
last_day_of_previous_month: date = last_day_of_previous_month()
today_start_date: date = datetime.today()
today_end_date: date = datetime.today()


def daily_job_postings(start_date=today_start_date, end_date=today_end_date):
    print("Running daily job postings")
    nifty_configs = fetch_configs(identifier='Nifty Cover')
    indlu_configs = fetch_configs(identifier='Indlu')
    start_date_time, end_date_time = __get_start_and_end_dates_with_time(start_date, end_date)
    credit_life_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.CREDIT_LIFE)
    funeral_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.FUNERAL_COVER)
    fetched_claims = __fetch_claims(start_date_time, end_date_time)
    try:
        credit_life_daily(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life cover: {e}")

    try:
        life_funeral_daily(funeral_policies, nifty_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life funeral: {e}")

    try:
        claims_daily(fetched_claims, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending claims: {e}")

    status = 200
    data = {
        "message": "Successfully sent daily job postings",
    }
    return status, data


def monthly_job_postings(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    """

    @param start_date:
    @type end_date: date
    """
    print("Running monthly job postings")
    nifty_configs = fetch_configs(identifier='Nifty Cover')
    indlu_configs = fetch_configs(identifier='Indlu')
    start_date_time, end_date_time = __get_start_and_end_dates_with_time(start_date, end_date)
    credit_life_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.CREDIT_LIFE)
    funeral_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.FUNERAL_COVER)
    fetched_claims = __fetch_claims(start_date_time, end_date_time)
    try:
        credit_life_monthly(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life cover: {e}")

    try:
        life_funeral_monthly(funeral_policies, nifty_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life funeral: {e}")

    try:
        claims_monthly(fetched_claims, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending monthly claims: {e}")

    status = 200
    data = {
        "message": "Successfully sent monthly job postings",
    }
    return status, data


def __get_start_and_end_dates_with_time(start_date, end_date):
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    return start_datetime, end_datetime


def credit_life_daily(credit_life_policies, nifty_configs, indlu_configs, start_date=today_start_date,
                      end_date=today_end_date):
    __credit_life(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)


def credit_life_monthly(credit_life_policies, nifty_configs, indlu_configs,
                        start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    __credit_life(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date, False)


def __credit_life(
        credit_life_policies, nifty_configs, indlu_configs, start_date, end_date, is_daily_submission=True,
):
    try:
        if credit_life_policies.exists():
            # fetch the data
            nifty_data = list(filter(lambda policy: policy.entity == 'Nifty Cover', credit_life_policies))
            indlu_data = list(filter(lambda policy: policy.entity == 'Indlu', credit_life_policies))

            nifty_policies = PolicyDetailSerializer(nifty_data, many=True).data
            indlu_policies = PolicyDetailSerializer(indlu_data, many=True).data
            print(f'now processing for nifty , {len(nifty_policies)} policies')
            process_credit_life(nifty_policies, nifty_configs, start_date, end_date, is_daily_submission)
            print(f'now processing for indlu , {len(indlu_policies)} policies')
            process_credit_life(indlu_policies, indlu_configs, start_date, end_date, is_daily_submission)
            return
        print('No Life policies to process...')
    except Exception as e:
        print(e)
        raise Exception(e)


def process_credit_life(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('CREDIT_LIFE_DAILY' if is_daily_submission else 'CREDIT_LIFE_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        data, response_status = guard_risk.life_credit_daily(data, start_date, end_date, client_identifier) \
            if is_daily_submission else guard_risk.life_credit_monthly(data, start_date, end_date, client_identifier)
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
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def life_funeral_daily(funeral_policies, nifty_configs, start_date=today_start_date, end_date=today_end_date):
    __life_funeral(funeral_policies, nifty_configs, start_date, end_date)


def life_funeral_monthly(funeral_policies, nifty_configs, start_date, end_date):
    __life_funeral(funeral_policies, nifty_configs, start_date, end_date, False)


def __life_funeral(
        funeral_policies, nifty_configs, start_date, end_date, is_daily_submission=True
):
    try:
        if funeral_policies.exists():
            nifty_data = list(filter(lambda p: p.entity == 'Nifty Cover', funeral_policies))
            nifty_policies = PolicyDetailSerializer(nifty_data, many=True).data
            process_life_funeral(nifty_policies, nifty_configs, start_date, end_date, is_daily_submission)
        else:
            print('No funeral policies to process...')
    except Exception as e:
        print(e)
        raise Exception(e)


def process_life_funeral(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('LIFE_FUNERAL_DAILY' if is_daily_submission else 'LIFE_FUNERAL_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        data, response_status = guard_risk.life_funeral_daily(data, start_date, end_date, client_identifier) \
            if is_daily_submission else guard_risk.life_funeral_monthly(data, start_date, end_date, client_identifier)
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


def claims_daily(claims_fetched, nifty_configs, indlu_configs, start_date=today_start_date, end_date=today_end_date):
    return __claims(claims_fetched, nifty_configs, indlu_configs, start_date, end_date)


def claims_monthly(claims_fetched, nifty_configs, indlu_configs, start_date=first_day_of_previous_month,
                   end_date=last_day_of_previous_month):
    return __claims(claims_fetched, nifty_configs, indlu_configs, start_date, end_date, False)


def __claims(
        fetched_claims, nifty_configs, indlu_configs, start_date, end_date, is_daily_submission=True
):
    try:
        if fetched_claims.exists():
            nifty_data = list(filter(lambda claim: claim.policy.entity == 'Nifty Cover', fetched_claims))
            indlu_data = list(filter(lambda claim: claim.policy.entity == 'Indlu', fetched_claims))

            nifty_claims = ClaimSerializer(nifty_data, many=True).data
            indlu_claims = ClaimSerializer(indlu_data, many=True).data

            process_claims(nifty_claims, nifty_configs, start_date, end_date, is_daily_submission)
            process_claims(indlu_claims, indlu_configs, start_date, end_date, is_daily_submission)
        else:
            print('No claims to process...')
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception(e)


def process_claims(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('CLAIM_DAILY' if is_daily_submission else 'CLAIM_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        data, response_status = guard_risk.life_claims_daily(data, start_date, end_date, client_identifier)\
            if is_daily_submission else guard_risk.life_claims_monthly(data, start_date, end_date, client_identifier)
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
        created__gte=start_date,
        created__lte=end_date,
        policy_type__policy_type=policy_type.name,
        policy_type__isnull=False
    )


def __fetch_claims(start_date: datetime, end_date: datetime):
    return Claim.objects.filter(
        created__gte=start_date,
        created__lte=end_date,
    )
