from django.db import models
from auditlog.registry import auditlog
from clients.enums import EntityType, MaritalStatus
from config.models import BusinessSector, IdDocumentType
from core.enums import Gender
from core.models import BaseModel


class ClientDetails(BaseModel):
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    primary_id_number = models.CharField(max_length=200)
    primary_id_document_type = models.ForeignKey(
        IdDocumentType,
        on_delete=models.RESTRICT,
        related_name="id_document_type",
    )
    external_id = models.CharField(max_length=200, null=True, blank=True)
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    marital_status = models.CharField(
        max_length=20, choices=MaritalStatus.choices, null=True, blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    address_street = models.CharField(max_length=200, null=True, blank=True)
    address_suburb = models.CharField(max_length=200, null=True, blank=True)
    address_town = models.CharField(max_length=200, null=True, blank=True)
    address_province = models.CharField(max_length=200, null=True, blank=True)
    upload_ref = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Client Details"
        verbose_name_plural = "Client Details"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClientEmploymentDetails(BaseModel):
    client = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="client_employment_details",
    )
    employer_name = models.CharField(max_length=200)
    employer_address_street = models.CharField(max_length=200, null=True, blank=True)
    employer_address_suburb = models.CharField(max_length=200, null=True, blank=True)
    employer_address_town = models.CharField(max_length=200, null=True, blank=True)
    employer_address_province = models.CharField(max_length=200, null=True, blank=True)
    employer_phone_number = models.CharField(max_length=200, null=True, blank=True)
    employer_email = models.EmailField(null=True, blank=True)
    employer_website = models.CharField(max_length=200, null=True, blank=True)
    gross_pay = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    basic_pay = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    job_title = models.CharField(max_length=200, null=True, blank=True)
    sector = models.ForeignKey(
        BusinessSector,
        on_delete=models.CASCADE,
        related_name="client_employment_business_sector", null=True, blank=True
    )

    class Meta:
        verbose_name = "Client Details"
        verbose_name_plural = "Client Details"

    def __str__(self):
        return f"{self.client} - {self.employer_name}"


# Register models for Audit
auditlog.register(ClientDetails)
auditlog.register(ClientEmploymentDetails)
