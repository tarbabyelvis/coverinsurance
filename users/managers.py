from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Permission


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        """
        Create and save a SuperUser with the given email and password.
        """
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_superuser", True)

        if not kwargs.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not kwargs.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")
        user = self.create_user(email, password, **kwargs)

        try:
            permission = Permission.objects.get(codename="view_internal_loans")
            user.user_permissions.remove(permission)
        except Permission.DoesNotExist:
            pass

        return user
