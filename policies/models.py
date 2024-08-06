from django.db import models
from clients.models import ClientDetails
from config.models import Agent, InsuranceCompany, PolicyName, Relationships
from core.enums import Gender, PolicyStatus, PremiumFrequency
from core.models import BaseModel
from auditlog.registry import auditlog


class Policy(BaseModel):
    client = models.ForeignKey(
        ClientDetails,
        on_delete=models.RESTRICT,
        related_name="policy_client_details",
    )
    policy_type = models.ForeignKey(
        PolicyName,
        on_delete=models.RESTRICT,
        related_name="policy_name_policy",
        null=True,
        blank=True,
    )
    commencement_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    closed_date = models.DateField(null=True, blank=True)
    sum_insured = models.DecimalField(max_digits=20, decimal_places=2)
    premium = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=2
    )
    total_premium = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=2
    )
    policy_term = models.IntegerField(null=True, blank=True)  # in months
    policy_number = models.CharField(max_length=200, null=True, blank=True, unique=True)
    business_unit = models.CharField(max_length=200, null=True, blank=True)
    sub_scheme = models.CharField(max_length=200, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    external_reference = models.CharField(
        max_length=60, null=True, blank=True, unique=True
    )
    insurer = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.RESTRICT,
        related_name="policy_insurance_company",
        default=1
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.RESTRICT,
        related_name="policy_agent",
        null=True,
        blank=True,
    )
    policy_details = models.JSONField(null=True, blank=True, default=dict)
    policy_status = models.CharField(max_length=20, choices=PolicyStatus.choices)
    premium_frequency = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=PremiumFrequency.choices,
        default="Monthly",
    )
    commission_percentage = models.FloatField(null=True, blank=True)
    commission_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    commission_frequency = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=PremiumFrequency.choices,
        default="Monthly",
    )
    admin_fee = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    submitted_to_insurer = models.BooleanField(default=False)
    entity = models.CharField(max_length=50, null=False, blank=False, default='Indlu')
    policy_provider_type = models.CharField(max_length=25, null=True, blank=True, default='Internal Credit Life')
    is_legacy = models.BooleanField(default=False)

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
    term = models.IntegerField()
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
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="policy_premium_payment",
    )
    payment_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=200, null=True, blank=True)
    payment_reference = models.CharField(max_length=200, null=True, blank=True)
    payment_details = models.JSONField(null=True, blank=True)
    payment_receipt = models.FileField(null=True, blank=True)
    is_reversed = models.BooleanField(default=False)
    branch_name = models.CharField(max_length=200, null=True, blank=True)
    policy_payment_method = models.CharField(max_length=200, null=True, blank=True)
    transaction_type = models.CharField(max_length=200, null=True, blank=True)
    client_transaction_id = models.CharField(max_length=200, null=True, blank=True)
    teller_transaction_number = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Premium Payment"
        verbose_name_plural = "Premium Payments"

    def __str__(self):
        return f"{self.id} - {self.policy}"


class PremiumPaymentScheduleLink(models.Model):
    premium_payment = models.ForeignKey(
        "PremiumPayment", on_delete=models.CASCADE, related_name="premium_payment_links"
    )
    policy_payment_schedule = models.ForeignKey(
        "PolicyPaymentSchedule",
        on_delete=models.CASCADE,
        related_name="premium_payment_links",
    )


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


class CliCharge(BaseModel):
    ifk_client_number = models.CharField(max_length=200, null=True, blank=True)
    transaction_date = models.DateField(null=True, blank=True)
    ifk_transaction_type = models.CharField(max_length=200, null=True, blank=True)
    transaction_type = models.CharField(max_length=200, null=True, blank=True)
    minfo = models.CharField(max_length=200, null=True, blank=True)
    debit = models.DecimalField(max_digits=20, decimal_places=2)
    credit = models.DecimalField(max_digits=20, decimal_places=2)
    net_amount = models.DecimalField(max_digits=20, decimal_places=2)
    cfk_branch = models.CharField(max_length=200, null=True, blank=True)


auditlog.register(Policy)
auditlog.register(PolicyPaymentSchedule)
auditlog.register(PremiumPayment)
auditlog.register(Dependant)
auditlog.register(Beneficiary)
auditlog.register(CliCharge)
