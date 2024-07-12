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


# class PolicyStatus(models.TextChoices):
#     PENDING = "PENDING", "Pending"
#     APPROVED = "APPROVED", "Approved"
#     REJECTED = "REJECTED", "Rejected"
#     CANCELLED = "CANCELLED", "Cancelled"
#     EXPIRED = "EXPIRED", "Expired"
#     QUOTATION = "QUOTATION", "Quotation"


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
    TRANSFERRED_OUT = "T", "Transferred out"


