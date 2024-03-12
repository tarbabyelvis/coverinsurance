from django.db import models
from clients.models import ClientDetails
from config.models import Agent, InsuranceCompany, Relationships
from core.enums import Gender, PolicyStatus
from core.models import BaseModel
from auditlog.registry import auditlog


class Policy(BaseModel):
    client = models.ForeignKey(
        ClientDetails,
        on_delete=models.RESTRICT,
        related_name="policy_client_details",
    )
    commencement_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    sum_insured = models.DecimalField(max_digits=20, decimal_places=2)
    total_premium = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=2
    )
    policy_term = models.IntegerField(null=True, blank=True)  # in months
    policy_number = models.CharField(max_length=200, null=True, blank=True)
    external_reference = models.CharField(max_length=60, null=True, blank=True)
    insurer = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.RESTRICT,
        related_name="policy_insurance_company",
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.RESTRICT,
        related_name="policy_agent",
        null=True,
        blank=True,
    )
    policy_details = models.JSONField(null=True, blank=True)
    policy_status = models.CharField(max_length=20, choices=PolicyStatus.choices)
    commission_percentage = models.FloatField(null=True, blank=True)
    commission_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    admin_fee = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    def get_status_symbol(self):
        """
        Method to get the associated symbol for the status.
        """
        for status in self.PolicyStatus:
            if self.status == status.value[0]:
                return status.value[0]
        return None

    class Meta:
        verbose_name = "Policy"
        verbose_name_plural = "Policies"

    def __str__(self):
        return f"{self.id} - {self.client}"


class PolicyPaymentSchedule(BaseModel):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="policy_payment_schedule",
    )
    payment_date = models.DateField(null=True, blank=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    amount_due = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    payment_due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    payment_schedule_details = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Policy Payment Schedule"
        verbose_name_plural = "Policy Payment Schedules"

    def __str__(self):
        return f"{self.id} - {self.policy}"


class PremiumPayment(BaseModel):
    policy_schedule = models.ForeignKey(
        PolicyPaymentSchedule,
        on_delete=models.RESTRICT,
        related_name="policy_schedule_premium_payments",
    )
    payment_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=200, null=True, blank=True)
    payment_reference = models.CharField(max_length=200, null=True, blank=True)
    payment_details = models.JSONField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PolicyStatus.choices)
    payment_receipt = models.FileField(null=True, blank=True)
    payment_receipt_date = models.DateField(null=True, blank=True)
    is_reversed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Premium Payment"
        verbose_name_plural = "Premium Payments"

    def __str__(self):
        return f"{self.id} - {self.policy_schedule}"


class Dependant(BaseModel):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="policy_dependants",
    )

    relationship = models.ForeignKey(
        Relationships,
        on_delete=models.RESTRICT,
        related_name="relationship_dependant",
    )
    dependant_name = models.CharField(max_length=200, null=True, blank=True)
    dependant_dob = models.DateField(null=True, blank=True)
    dependant_gender = models.CharField(max_length=20, choices=Gender.choices)
    dependant_address_street = models.CharField(max_length=200, null=True, blank=True)
    dependant_address_suburb = models.CharField(max_length=200, null=True, blank=True)
    dependant_address_town = models.CharField(max_length=200, null=True, blank=True)
    dependant_address_province = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Dependant"
        verbose_name_plural = "Dependants"

    def __str__(self):
        return f"{self.id} - {self.policy}"


class Beneficiary(BaseModel):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="policy_beneficiary",
    )

    relationship = models.ForeignKey(
        Relationships,
        on_delete=models.RESTRICT,
        related_name="relationship_beneficiary",
    )
    beneficiary_name = models.CharField(max_length=200, null=True, blank=True)
    beneficiary_dob = models.DateField(null=True, blank=True)
    beneficiary_gender = models.CharField(max_length=20, choices=Gender.choices)
    beneficiary_phone = models.CharField(max_length=20, null=True, blank=True)
    beneficiary_address_street = models.CharField(max_length=200, null=True, blank=True)
    beneficiary_address_suburb = models.CharField(max_length=200, null=True, blank=True)
    beneficiary_address_town = models.CharField(max_length=200, null=True, blank=True)
    beneficiary_address_province = models.CharField(
        max_length=200, null=True, blank=True
    )

    class Meta:
        verbose_name = "Beneficiary"
        verbose_name_plural = "Beneficiaries"

    def __str__(self):
        return f"{self.id} - {self.policy}"


auditlog.register(Policy)
auditlog.register(PolicyPaymentSchedule)
auditlog.register(PremiumPayment)
auditlog.register(Dependant)
auditlog.register(Beneficiary)
