from django.contrib import admin
from .models import AuditTrail


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'model_name', 'model_id', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__email', 'model_name', 'details')
