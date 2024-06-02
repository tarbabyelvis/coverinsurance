from django.db import models


class PolicyType(models.TextChoices):
    FUNERAL_COVER = (
        "FUNERAL_COVER",
        "Funeral Cover",
    )
    CREDIT_LIFE = (
        "CREDIT_LIFE",
        "Credit Life",
    )


class DocumentCategories(models.TextChoices):
    CLIENT_DOCUMENT = ("CLIENT_DOCUMENT", "Client Document")
    POLICY_DOCUMENT = ("POLICY_DOCUMENT", "Policy Document")
    CLAIM_DOCUMENT = ("CLAIM_DOCUMENT", "Claim Document")
