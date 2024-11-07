from django.db import models


class Gender(models.TextChoices):
    MALE = "Male", "Male"
    FEMALE = (
        "Female",
        "Female",
    )
    UNKNOWN = "Unknown", "Unknown"


class PremiumFrequency(models.TextChoices):
    MONTHLY = "Monthly", "Monthly"
    QUARTERLY = "Quarterly", "Quarterly"
    ANNUAL = "Annual", "Annual"
    SEMI_ANNUAL = "Semi Annual", "Semi Annual"
    BI_ANNUAL = "Bi Annual", "Bi Annual"
    ONCE_OFF = "Once Off", "Once Off"


class PolicyStatus(models.TextChoices):
    ACTIVE = "A", "Active"
    LAPSED = "L", "Lapsed"
    CANCELLED = "X", "Cancelled"
    EXPIRY = "E", "Expiry"
    CLAIMED = "C", "Claimed"
    REINSTATED = "R", "Reinstated"
    NOT_TAKEN_UP = "N", "Not Taken Up (Non payment of premium)"
    PAID_UP = "P", "Paid Up"
    FULLY_PAID = "F", "Paid Up"
    SURRENDERED = "S", "Surrendered"
    SURRENDERED_REPLACE = "SR", "Surrendered due to replacement"
    TRANSFERRED_OUT = "T", "Transferred out",
    HISTORIC_LAPSED = "HL", "Historic Lapsed"


class ClaimStatus(models.TextChoices):
    CREATED = "CREATED", "Created"
    ON_ASSESSMENT = "ON_ASSESSMENT", "On Assessment"
    SUBMITTED = "SUBMITTED", "Submitted"
    REVIEW = "REVIEW", "Review"
    APPROVED = "APPROVED", "Approved"
    PAID = "PAID", "Paid"
    REPUDIATED = "REPUDIATED", "Repudiated"


class CreationStage(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"
    ON_ASSESSMENT = "ON_ASSESSMENT", "On Assessment"
    REVIEW = "REVIEW", "Review"
    DECLINED = "DECLINED", "Declined"
    CREATED = "CREATED", "Created"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    FAILED = "FAILED", "Failed"
    SUCCESSFUL = "SUCCESSFUL", "Successful"
    CANCELLED = "CANCELLED", "Cancelled"
