from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import (
    Tenant,
    Domain,
)


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("name", "created_on")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    pass
