from django.contrib import admin
from integrations.models import IntegrationConfigs, IntegrationLogs


@admin.register(IntegrationConfigs)
class IntegrationConfigsAdmin(admin.ModelAdmin):
    list_display = ["name", "is_enabled"]
    search_fields = ("name",)


@admin.register(IntegrationLogs)
class IntegrationLogsAdmin(admin.ModelAdmin):
    list_display = ["id", "service", "status"]
    search_fields = ("service",)
