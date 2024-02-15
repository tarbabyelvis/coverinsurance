from django.db import models
from clients.models import ClientDetails
from config.models import InsuranceCompany
from core.models import BaseModel


class BasePolicyModel(BaseModel):
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
    insurance_company = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.RESTRICT,
        related_name="policy_insurance_company",
    )

    class Meta:
        abstract = True


class FuneralCoverPolicy(BasePolicyModel):
    pass


class CreditLifePolicy(BasePolicyModel):
    pass
