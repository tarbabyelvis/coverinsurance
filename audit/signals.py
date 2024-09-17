from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from claims.models import Claim
from .models import AuditTrail

User = get_user_model()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditTrail.objects.create(
        user=user,
        action_type='LOGIN',
        model_name='User',
        model_id=user.id,
        details='User logged in',
    )


@receiver(post_save, sender=Claim)
def audit_create_or_update(sender, instance, created, **kwargs):
    if sender in [Claim]:  # List models to audit
        action = 'Created' if created else 'Updated'
        AuditTrail.objects.create(
            user=getattr(instance, 'user', None),
            action_type=action,
            model_name=sender.__name__,
            model_id=instance.pk,
            changes=str(instance.__dict__)
        )


@receiver(post_save, sender=get_user_model())
def audit_create_profile(sender, instance, created, **kwargs):
    if created:
        AuditTrail.objects.create(
            user=getattr(instance, 'user', None),
            action_type='CREATE',
            model_name=sender.__name__,
            model_id=instance.pk,
            details=f'User created by {sender.__name__} ',
            changes=str(instance.__dict__)
        )
