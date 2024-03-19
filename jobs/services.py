from asyncio import Task

from config.enums import PolicyType
from integrations.enums import Integrations
from integrations.guardrisk.guardrisk import GuardRisk
from integrations.models import IntegrationConfigs
from jobs.enums import Processes
from jobs.models import TaskLog
from policies.models import Policy
from policies.serializers import PolicyDetailSerializer


def credit_life(request_type, start_date, end_date):
    print(start_date)
    print(end_date)
    print(request_type)
    task = Task.objects.get(task=Processes.CREDIT_LIFE)
    integration = IntegrationConfigs.objects.get(name=Integrations.GUARDRISK)
    log = TaskLog.objects.create(task=task, status="running", manual_run=True)
    try:
        # fetch the data
        policy = Policy.objects.filter(
            commencement_date__gte=start_date,
            commencement_date__lte=end_date,
            policy_type__policy_type=PolicyType.CREDIT_LIFE,
        )

        serializer = PolicyDetailSerializer(policy, many=True)
        guardrisk = GuardRisk(integration.access_key, integration.base_url)
        data, response_status = guardrisk.lifeCredit(serializer)
        log.data = data
        print(response_status)
        if response_status.startWith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        log.status = "failed"
        log.save()
