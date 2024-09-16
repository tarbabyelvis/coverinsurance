from django.conf import settings
from django.db import models


class AuditTrail(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('LOGIN', 'Login'),
        ('INITIATE', 'Initiate'),
        ('AUTHORIZE', 'Authorize'),
        # Add more action types as needed
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=255)
    model_id = models.PositiveIntegerField()
    details = models.TextField(blank=True, null=True)
    changes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.model_name} ({self.model_id})"
