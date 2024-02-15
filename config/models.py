from django.db import models

from config.enum import PolicyType
from core.models import BaseModel


class PolicyName(BaseModel):
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=20, choices=PolicyType.choices)

    class Meta:
        verbose_name = "Policy Name"
        verbose_name_plural = "Policy Names"

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


class ClaimFields(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    input_type = models.CharField(max_length=200, null=True, blank=True)
    is_required = models.BooleanField(default=False)
    claim_type = models.ForeignKey(
        ClaimType,
        on_delete=models.RESTRICT,
        related_name="claims_fields",
    )
