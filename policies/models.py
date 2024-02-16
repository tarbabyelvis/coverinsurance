from django.db import models
from clients.enums import EntityType
from clients.models import ClientDetails
from config.models import InsuranceCompany, Relationships
from core.enums import Gender, PolicyStatus
from core.models import BaseModel


class Agent(BaseModel):
    agent_name = models.CharField(max_length=200, null=True, blank=True)
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


class Policy(BaseModel):
    client = models.ForeignKey(
        ClientDetails,
        on_delete=models.RESTRICT,
        related_name="policy_client_details",
    )
    commencement_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    premium = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=2
    )
    policy_terms = models.IntegerField(null=True, blank=True)  # in months
    policy_number = models.CharField(max_length=200, null=True, blank=True)
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


class Dependant(BaseModel):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="policy_dependants",
    )

    relationship = models.ForeignKey(
        Relationships,
        on_delete=models.RESTRICT,
        related_name="policy_insurance_company",
    )
    dependant_name = models.CharField(max_length=200, null=True, blank=True)
    dependant_dob = models.DateField(null=True, blank=True)
    dependant_gender = models.CharField(max_length=20, choices=Gender.choices)
    dependant_address_street = models.CharField(max_length=200, null=True, blank=True)
    dependant_address_suburb = models.CharField(max_length=200, null=True, blank=True)
    dependant_address_town = models.CharField(max_length=200, null=True, blank=True)
    dependant_address_province = models.CharField(max_length=200, null=True, blank=True)


class Beneficiary(BaseModel):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="policy_dependants",
    )

    relationship = models.ForeignKey(
        Relationships,
        on_delete=models.RESTRICT,
        related_name="policy_insurance_company",
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
