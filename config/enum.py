from django.db import models


class PolicyType(models.TextChoices):
    FUNERAL_COVERAGE = (
        "FUNERAL_COVER",
        "Funeral Cover",
    )
    CREDIT_LIFE = (
        "CREDIT_LIFE",
        "Credit Life",
    )
