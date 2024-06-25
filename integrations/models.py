from django.db import models
from integrations.enums import Integrations
from auditlog.registry import auditlog


class IntegrationConfigs(models.Model):
    name = models.CharField(max_length=20, choices=Integrations.choices)
    access_key = models.CharField(max_length=100, null=True, blank=True)
    base_url = models.URLField()
    is_enabled = models.BooleanField(default=False)
    entity = models.CharField(max_length=20, null=True, blank=True)
    client_identifier = models.CharField(max_length=100, null=False, blank=False, default='143')

    class Meta:
        verbose_name = "Integration Config"
        verbose_name_plural = "Integration Configs"

    def __str__(self):
        return self.name


class IntegrationLogs(models.Model):
    request_data = models.JSONField()
    response_data = models.JSONField(null=True)
    response_status = models.IntegerField(null=True)
    status = models.CharField(max_length=20, null=True)  # New field for request status
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.CharField(max_length=20, choices=Integrations.choices)

    def __str__(self):
        return f"Integration Logs - ID: {self.pk}"

    class Meta:
        verbose_name = "Integration Request"
        verbose_name_plural = "Integration Requests"


auditlog.register(IntegrationConfigs)
auditlog.register(IntegrationLogs)
