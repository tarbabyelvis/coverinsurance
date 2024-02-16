from django.db import models
from config.models import ClaimType, DocumentType
from core.models import BaseModel


class Claim(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    claim_type = models.ForeignKey(
        ClaimType,
        on_delete=models.RESTRICT,
        related_name="claim_type",
    )
    claim_status = models.CharField(max_length=200, null=True, blank=True)
    claimant_name = models.CharField(max_length=200, null=True, blank=True)
    claimant_surname = models.CharField(max_length=200, null=True, blank=True)
    claimant_id_number = models.CharField(max_length=200, null=True, blank=True)
    claimant_id_type = models.CharField(max_length=200, null=True, blank=True)
    claimant_email = models.EmailField(null=True, blank=True)
    claimant_phone = models.CharField(max_length=50, null=True, blank=True)
    claimant_bank_name = models.CharField(max_length=200, null=True, blank=True)
    claimant_bank_account_number = models.CharField(
        max_length=50, null=True, blank=True
    )
    claimant_branch = models.CharField(max_length=50, null=True, blank=True)
    claimant_branch_code = models.CharField(max_length=50, null=True, blank=True)
    claim_assessed_by = models.CharField(max_length=200, null=True, blank=True)
    claim_assessment_date = models.DateField(null=True, blank=True)
    claim_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    claim_details = models.JSONField(null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    claim_paid_date = models.DateField(null=True, blank=True)


class ClaimDocument(BaseModel):
    claim = models.ForeignKey(
        Claim, on_delete=models.RESTRICT, related_name="claim_document"
    )
    document_name = models.CharField(max_length=200, null=True, blank=True)
    document_file = models.FileField(upload_to="claims/")
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.RESTRICT,
        related_name="claim_document_type",
    )
