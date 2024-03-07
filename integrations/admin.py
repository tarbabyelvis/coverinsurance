from django.contrib import admin
from integrations.models import IntegrationConfigs

@admin.register(IntegrationConfigs)
class IntegrationConfigsAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_enabled']
    search_fields = ('name', )