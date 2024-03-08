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
    claim_type = models.ForeignKey(
        PolicyName,
        on_delete=models.RESTRICT,
        related_name="policy_type_fields",
    )

    class Meta:
        verbose_name = "Claim Field"
        verbose_name_plural = "Claim Fields"

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

    class Meta:
        verbose_name = "ID Document Type"
        verbose_name_plural = "ID Document Types"

    def __str__(self):
        return self.type_name
    
class BusinessSector(BaseModel):
    sector = models.CharField(max_length=200)

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

