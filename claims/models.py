from django.db import models
from config.models import ClaimType
from core.models import BaseModel


class Claim(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    claim_type = models.ForeignKey(
        ClaimType,
        on_delete=models.RESTRICT,
        related_name="claim_type",
    )
    claim_details = models.JSONField(null=True, blank=True)
    claim_status = models.CharField(max_length=200, null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    claim_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
