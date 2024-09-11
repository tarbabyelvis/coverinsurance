from django.utils import timezone

from django.db import models
from clients.enums import EntityType
from config.enums import DocumentCategories, PolicyType
from core.models import BaseModel
from auditlog.registry import auditlog


class OrganisationConfig(BaseModel):
    name = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        # Allow only a single instance of Company
        if OrganisationConfig.objects.exists() and not self.pk:
            raise ValueError("Only one instance of Organisation is allowed.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion of the Company instance
        raise ValueError("Cannot delete the Organisation details.")

    class Meta:
        verbose_name = "Organisation Config"
        verbose_name_plural = "Organisation Configs"

    def __str__(self):
        return self.name


class PolicyName(BaseModel):
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=20, choices=PolicyType.choices)
    default_commission = models.FloatField(blank=True, null=True)
    has_beneficiaries = models.BooleanField(default=False)
    has_dependencies = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Policy Name"
        verbose_name_plural = "Policy Names"

    def __str__(self):
        return self.name


class PolicyTypeFields(models.Model):
    short_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    input_type = models.CharField(max_length=200)
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    policy_type = models.ForeignKey(
        PolicyName,
        on_delete=models.RESTRICT,
        related_name="policy_type_fields",
    )

    class Meta:
        verbose_name = "Policy Type Field"
        verbose_name_plural = "Policy Type Fields"

    def __str__(self):
        return self.name


class InsuranceCompany(BaseModel):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Insurance Company"
        verbose_name_plural = "Insurance Companies"

    def __str__(self):
        return self.name


class ClaimType(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    policy = models.ForeignKey(
        PolicyName,
        on_delete=models.RESTRICT,
        related_name="claim_type_policy",
    )

    class Meta:
        verbose_name = "Claim Type"
        verbose_name_plural = "Claim Types"

    def __str__(self):
        return self.name


class ClaimFields(models.Model):
    short_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    input_type = models.CharField(max_length=200)
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    claim_type = models.ForeignKey(
        ClaimType,
        on_delete=models.RESTRICT,
        related_name="claims_fields",
    )

    class Meta:
        verbose_name = "Claim Field"
        verbose_name_plural = "Claim Fields"

    def __str__(self):
        return self.name


class DocumentType(models.Model):
    document_type = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=DocumentCategories.choices)

    class Meta:
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"

    def __str__(self):
        return self.document_type


class Relationships(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Relationship"
        verbose_name_plural = "Relationships"

    def __str__(self):
        return self.name


class IdDocumentType(models.Model):
    type_name = models.CharField(max_length=200)
    objects = models.Manager()

    class Meta:
        verbose_name = "ID Document Type"
        verbose_name_plural = "ID Document Types"

    def __str__(self):
        return self.type_name


class BusinessSector(BaseModel):
    sector = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Business Sector"
        verbose_name_plural = "Business Sectors"

    def __str__(self):
        return self.sector


class Agent(BaseModel):
    agent_name = models.CharField(max_length=200, null=True, blank=True)
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"

    def __str__(self):
        return self.agent_name


class ClaimantDetails(models.Model):
    name = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    id_number = models.CharField(max_length=60)
    id_type = models.CharField(max_length=60)
    email = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=60)
    bank = models.CharField(max_length=60)
    branch = models.CharField(max_length=60)
    branch_code = models.CharField(max_length=60)
    account_name = models.CharField(max_length=60)
    account_number = models.CharField(max_length=60)
    account_type = models.CharField(max_length=60)
    created = models.DateField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.bank

    class Meta:
        verbose_name = "Claimant Details"
        verbose_name_plural = "Claimant Details"


class LoanProduct(models.Model):
    product_name = models.CharField(max_length=60, blank=False, null=False)
    product_id = models.IntegerField()
    policy_type_id = models.IntegerField(default=1)
    business_unit = models.CharField(max_length=40, default='THF')
    sub_scheme = models.CharField(max_length=40, default='Credit Life')
    entity = models.CharField(max_length=60, default='Indlu')
    is_legacy = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.product_name + " - " + self.business_unit + " - " + self.entity

    class Meta:
        verbose_name = "Loan Product Config"
        verbose_name_plural = "Loan Product Configs"


class PaymentAccount(models.Model):
    name = models.CharField(max_length=60)
    payment_type_id = models.IntegerField()


class Sms(models.Model):
    template = models.CharField(max_length=60, unique=True, null=False, blank=False)
    template_id = models.IntegerField()
    service_name = models.TextField(null=True, default=None, blank=True)
    sms_from = models.CharField(max_length=500, null=True, blank=True)
    linked_organization = models.CharField(max_length=20)


# register the class for Audit
auditlog.register(PolicyName)
auditlog.register(InsuranceCompany)
auditlog.register(ClaimFields)
auditlog.register(DocumentType)
auditlog.register(Relationships)
auditlog.register(IdDocumentType)
auditlog.register(BusinessSector)
auditlog.register(Agent)
auditlog.register(OrganisationConfig)
auditlog.register(PolicyTypeFields)
auditlog.register(ClaimantDetails)
auditlog.register(LoanProduct)
auditlog.register(PaymentAccount)
auditlog.register(Sms)
