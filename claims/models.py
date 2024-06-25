from django.db import models
from config.models import ClaimType, DocumentType, IdDocumentType
from core.models import BaseModel
from auditlog.registry import auditlog
from policies.models import Policy


class Claim(BaseModel):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.RESTRICT,
        related_name="claim_policy",
    )
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
    claimant_id_type = models.ForeignKey(
        IdDocumentType,
        on_delete=models.RESTRICT,
        related_name="claimant_id_document_type",
    )
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
    claim_rejected = models.BooleanField(default=False)
    rejected_date = models.DateField(null=True, blank=True)
    rejected_reason = models.CharField(max_length=255, null=True, blank=True)


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


# Register models for audit
auditlog.register(Claim)
auditlog.register(ClaimDocument)
