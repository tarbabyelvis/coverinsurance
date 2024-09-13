from django.db import models
from config.models import ClaimType, DocumentType, IdDocumentType
from core.enums import ClaimStatus, PaymentStatus
from core.models import BaseModel
from auditlog.registry import auditlog
from django.utils import timezone


class Claim(BaseModel):
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.RESTRICT,
        related_name="claim_policy",
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    claim_type = models.ForeignKey(
        ClaimType,
        on_delete=models.RESTRICT,
        related_name="claim_type",
    )
    claim_status = models.CharField(max_length=30, choices=ClaimStatus.choices, default=ClaimStatus.CREATED)
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
    comments = models.TextField(null=True, blank=True)
    claim_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    claim_details = models.JSONField(null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    claim_paid_date = models.DateField(null=True, blank=True)
    claim_repudiated = models.BooleanField(default=False)
    repudiated_date = models.DateField(null=True, blank=True)
    repudiated_reason = models.CharField(max_length=255, null=True, blank=True)
    repudiated_by = models.CharField(max_length=255, null=True, blank=True)
    submitted_to_insurer = models.BooleanField(default=False)


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
    password = models.CharField(max_length=50, null=True, blank=True)
    document = models.FileField(upload_to="", null=True, blank=True)
    actual_name = models.TextField(null=True, blank=True)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    external_verification = models.BooleanField(default=False, null=True, blank=True)
    internally_verified = models.BooleanField(default=False, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    collection_date = models.DateTimeField(null=True, blank=True)
    trust_level = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    is_rejected = models.BooleanField(default=False, null=True, blank=True)
    old_doc_id = models.IntegerField(null=True, blank=True)



class ClientClaimDocuments(models.Model):
    client_documents = models.ForeignKey(ClaimDocument, on_delete=models.RESTRICT,
                                         related_name="client_claim_documents")
    claim = models.ForeignKey(Claim, on_delete=models.RESTRICT, related_name="claim_client_documents")

    class Meta:
        verbose_name = "Client Claim Document"
        verbose_name_plural = "Client Claim Documents"

class Payment(BaseModel):
    transaction_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_type = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    receipted_by = models.CharField(max_length=50, null=True, blank=True)


class ClaimTracker(models.Model):
    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, related_name="claim"
    )
    notes = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=5)
    # picked_by = models.ForeignKey(
    #     User,
    #     on_delete=models.RESTRICT,
    #     null=True,
    #     blank=True,
    #     related_name="fin_cover_user",
    # )
    picked_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    submission_date = models.DateTimeField(null=True, blank=True)
    assessment_date = models.DateTimeField(null=True, blank=True)
    changes_made = models.TextField(null=True, blank=True)
    objects = models.Manager()

    class Meta:
        verbose_name = "Claim Tracker"
        verbose_name_plural = "Claim Tracker"

    def __str__(self):
        return "{}".format(self.claim.id)


# Register models for audit
auditlog.register(Claim)
auditlog.register(Payment)
auditlog.register(ClaimDocument)
auditlog.register(ClaimTracker)
