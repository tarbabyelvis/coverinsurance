"""
Django settings for FinCover project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-*tys91*uq0aa-@=jw!x*t#cv3hlq3_&uoh=d40ijr#&$v90p+q"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://fin-za.localhost",
    "https://dev-cover-workflow.fin-connect.net",
    "https://*.dev-cover-workflow.fin-connect.net",
]


# Application definition

SHARED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_tenants",
    "rest_framework",
    "tenants",
    "auditlog",
    "drf_yasg",
    "policies",
    "claims",
    "clients",
    "jobs",
    "reports",
    "complaints",
    "config",
]

TENANT_APPS = [
    "policies",
    "claims",
    "clients",
    "jobs",
    "reports",
    "complaints",
    "config",
    "integrations",
]

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

TENANT_MODEL = "tenants.Tenant"  # app.Model

TENANT_DOMAIN_MODEL = "tenants.Domain"  # app.Model

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "tenants.middleware.CustomTenantMiddleware.CustomTenantMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.APILoggingMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "FinCover.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "FinCover.wsgi.application"


REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("DATABASE_NAME", "fin_cover"),
        "USER": os.getenv("DATABASE_USER", "postgres"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "dominicd"),
        "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
    },
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django_tenants.postgresql_backend",
#         "NAME": os.getenv("DATABASE_NAME", "fin_cover"),
#         "USER": os.getenv("DATABASE_USER", "xWniG2oMKu85"),
#         "PASSWORD": os.getenv("DATABASE_PASSWORD", "BzjUftSC7JDSf%]["),
#         "HOST": os.getenv("DATABASE_HOST", "0.0.0.0"),
#         "PORT": os.getenv("DATABASE_PORT", 5433),
#     },
# }


DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "filters": ["tenant_context"],  # tenant config
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
    # tenant configs
    "filters": {
        "tenant_context": {"()": "django_tenants.log.TenantContextFilter"},
    },
    "formatters": {
        "tenant_context": {
            "format": "[%(schema_name)s:%(domain_url)s] "
            "%(levelname)-7s %(asctime)s %(message)s",
        },
    },
}

CELERY_BROKER_URL = "redis://localhost:6379/0"  # Redis URL
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"  # Redis URL for results

# settings.py

CELERY_BEAT_SCHEDULE = {
    "task1": {
        "task": "yourapp.tasks.process_task1",
        "schedule": crontab(minute=0, hour=0),  # Replace with your cron schedule
    },
    "task2": {
        "task": "yourapp.tasks.process_task2",
        "schedule": crontab(minute=0, hour=0),  # Replace with your cron schedule
    },
    "task3": {
        "task": "yourapp.tasks.process_task3",
        "schedule": crontab(minute=0, hour=0),  # Replace with your cron schedule
    },
}
