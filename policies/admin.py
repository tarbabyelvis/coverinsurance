from django.contrib import admin
from policies.models import (
    Beneficiary,
    Dependant,
    Policy,
    PolicyPaymentSchedule,
    PremiumPayment,
)


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = [
        "client",
        "commencement_date",
        "expiry_date",
        "policy_term",
        "policy_number",
        "insurer",
    ]
    search_fields = ("client", "policy_number", "insurer")


@admin.register(PolicyPaymentSchedule)
class PolicyPaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ["policy", "payment_date", "amount_due", "is_paid"]
    search_fields = ("policy",)


@admin.register(PremiumPayment)
class PremiumPaymentAdmin(admin.ModelAdmin):
    list_display = ["policy_schedule", "payment_date", "amount", "payment_receipt"]
    search_fields = ("policy_schedule",)


@admin.register(Dependant)
class DependantAdmin(admin.ModelAdmin):
    list_display = ["policy", "relationship", "dependant_name"]
    search_fields = ("policy", "dependant_name")


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ["policy", "relationship", "beneficiary_name", "beneficiary_phone"]
    search_fields = ("policy", "relationship", "beneficiary_name")
