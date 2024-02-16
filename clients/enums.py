from django.db import models


class EntityType(models.TextChoices):
    PERSON = "PERSON", "Person"
    ORGANIZATION = "ORGANIZATION", "Organization"


class MaritalStatus(models.TextChoices):
    MARRIED = "MARRIED", "Married"
    SINGLE = "SINGLE", "Single"
    DIVORCED = "DIVORCED", "Divorced"
    WIDOWED = "WIDOWED", "Widowed"
    OTHER = "OTHER", "Other"
    UNKNOWN = "UNKNOWN", "Unknown"
