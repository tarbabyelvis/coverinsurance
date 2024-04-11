from datetime import datetime
import traceback
from config.enums import PolicyType
from integrations.enums import Integrations
from integrations.guardrisk.guardrisk import GuardRisk
from integrations.models import IntegrationConfigs
from jobs.enums import Processes
from jobs.models import TaskLog
from policies.models import Policy
from policies.serializers import PolicyDetailSerializer
from .models import Task


def credit_life(
    identifier, start_date=datetime.now().date(), end_date=datetime.now().date()
):
    print("Credit life")

    task = Task.objects.get(task=Processes.CREDIT_LIFE.name)
    integration = IntegrationConfigs.objects.get(
        name=Integrations.GUARDRISK.name, is_enabled=True, entity__icontains=identifier
    )
    log = TaskLog.objects.create(task=task, status="running", manual_run=True)
    try:
        # fetch the data
        policy = Policy.objects.filter(
            # commencement_date__gte=start_date,
            # commencement_date__lte=end_date,
            # policy_type__policy_type=PolicyType.CREDIT_LIFE.name,
        )

        if not policy.exists():
            print("Empty")
            raise Exception("Policies are empty")

        serializer = PolicyDetailSerializer(policy, many=True).data
        guardrisk = GuardRisk(integration.access_key, integration.base_url)
        data, response_status = guardrisk.lifeCredit(
            serializer, start_date, end_date, identifier
        )
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


def funeral_cover(request_type, start_date, end_date):

    task = Task.objects.get(task=Processes.LIFE_FUNERAL.name)
    integration = IntegrationConfigs.objects.get(
        name=Integrations.GUARDRISK.name, is_enabled=True
    )
    log = TaskLog.objects.create(task=task, status="running", manual_run=True)
    try:
        # fetch the data
        policy = Policy.objects.filter(
            commencement_date__gte=start_date,
            commencement_date__lte=end_date,
            policy_type__policy_type=PolicyType.FUNERAL_COVERAGE.name,
        )

        serializer = PolicyDetailSerializer(policy, many=True).data
        guardrisk = GuardRisk(integration.access_key, integration.base_url)
        data, response_status = guardrisk.lifeFuneral(serializer, start_date, end_date)
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
