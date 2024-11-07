from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import *

admin.site.site_header = "FinCover Administration"


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "user_type",
    )
    list_filter = ("is_staff", "is_active", "user_type", "is_superuser", "groups")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "user_type",
                    "is_supervisor",
                    "is_teamleader",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Security", {"fields": ("login_attempts", "password_expiry_date")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email", "last_name", "first_name")
    ordering = (
        "email",
        "last_name",
        "first_name",
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.save()
        super(CustomUserAdmin, self).save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "access_code")
    list_editable = (
        "code",
        "access_code",
    )
    search_fields = ("user__email", "code", "access_code")


admin.site.register(Profile, ProfileAdmin)
