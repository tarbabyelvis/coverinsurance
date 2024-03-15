from django.db import models


class EntityType(models.TextChoices):
    INDIVIDUAL = "Individual", "Individual"
    ORGANIZATION = "Organization", "Organization"


class MaritalStatus(models.TextChoices):
    MARRIED = "Married", "Married"
    SINGLE = "Single", "Single"
    DIVORCED = "Divorced", "Divorced"
    WIDOWED = "Widowed", "Widowed"
    OTHER = "Other", "Other"
    UNKNOWN = "Unknown", "Unknown"
