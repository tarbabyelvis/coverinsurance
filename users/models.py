from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import Q

from .managers import UserManager


class User(AbstractUser):
    username = None  # Remove username field since we use email for login
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Adding unique related_name attributes for groups and permissions
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USER_TYPES = (
        ('admin', 'Admin'),
        ('ceo', 'CEO'),
        ('insurance_manager', 'Insurance Manager'),
        ('insurance', 'Insurance'),
        ('finance_officer', 'Finance Officer'),
        ('collections_manager', 'Collections Manager'),
        ('collections', 'Collections'),
        ('it_manager', 'IT Manager'),
        ('it_officer', 'IT Officer'),
        ('records_officer', 'Records Officer'),
        ('internal_auditor', 'Internal Auditor'),
    )

    objects = UserManager()

    user_type = models.CharField(
        max_length=25, choices=USER_TYPES, default=USER_TYPES[1][0]
    )
    is_supervisor = models.BooleanField(default=False)
    is_teamleader = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    code = models.CharField(max_length=20, null=True, blank=True)
    access_code = models.CharField(
        max_length=10, unique=True, blank=True, null=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'code'], name='unique__when__access_code__is__null',
                                    condition=Q(access_code__isnull=True)),

            models.UniqueConstraint(
                fields=['user', 'code', 'access_code'], name='unique__when__access___code__not_null')
        ]

    objects = models.Manager()

    def __str__(self):
        return self.code
