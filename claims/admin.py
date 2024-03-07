from django.contrib import admin

from claims.models import Claim

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['name', 'claim_type', "claim_status", "claimant_name", "claimant_surname", "claimant_id_number"]
    search_fields = ['name', 'claim_type', "claimant_name", "claimant_surname", "claimant_id_number", "claimant_email"]