from django.db import models


class Integrations(models.TextChoices):
    GUARDRISK = "GUARDRISK", "Guardrisk"
