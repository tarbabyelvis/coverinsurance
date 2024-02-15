from django.contrib import admin

from claims.models import ClaimFields
from config.models import ClaimType


class ClaimFieldsInline(admin.TabularInline):
    model = ClaimFields
    extra = 1


class ClaimAdmin(admin.ModelAdmin):
    inlines = (ClaimFieldsInline,)


admin.site.register(ClaimType, ClaimAdmin)
