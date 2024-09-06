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

from .file_handler import DailyRotatingFileHandler

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
    "http://za-uat.localhost",
    "http://localhost",
    "https://dev-cover-workflow.fin-connect.net",
    "https://*.dev-cover-workflow.fin-connect.net",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True

# Application definition

SHARED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_tenants",
    "corsheaders",
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
    "authentication",
    "rest_framework.authtoken"
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
    "superbase_util"
]

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

TENANT_MODEL = "tenants.Tenant"  # app.Model

TENANT_DOMAIN_MODEL = "tenants.Domain"  # app.Model

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "tenants.middleware.CustomTenantMiddleware.CustomTenantMiddleware",
    "django.middleware.common.CommonMiddleware",
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
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': False,
#     'BLACKLIST_AFTER_ROTATION': True,
#     'UPDATE_LAST_LOGIN': False,
#
#     'ALGORITHM': 'HS256',
#     'SIGNING_KEY': settings.SECRET_KEY,
#     'VERIFYING_KEY': None,
#     'AUDIENCE': None,
#     'ISSUER': None,
#
#     'AUTH_HEADER_TYPES': ('Bearer',),
#     'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
#     'USER_ID_FIELD': 'id',
#     'USER_ID_CLAIM': 'user_id',
#     'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
#
#     'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
#     'TOKEN_TYPE_CLAIM': 'token_type',
#
#     'JTI_CLAIM': 'jti',
#
#     'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
#     'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),   #update here for acess token
#     'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1), # update here for refresh token
# }


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# LOCAL
# DATABASES = {
#     "default": {
#         "ENGINE": "django_tenants.postgresql_backend",
#         "NAME": os.getenv("DATABASE_NAME", "fin_cover"),
#         "USER": os.getenv("DATABASE_USER", "postgres"),
#         "PASSWORD": os.getenv("DATABASE_PASSWORD", "postgres"),
#         "HOST": os.getenv("DATABASE_HOST", "0.0.0.0"),
#         "PORT": os.getenv("DATABASE_PORT", 5432),
#     },
# }
# DEV
# DATABASES = {
#     "default": {
#         "ENGINE": "django_tenants.postgresql_backend",
#         "NAME": os.getenv("DATABASE_NAME", "fin_cover"),
#         "USER": os.getenv("DATABASE_USER", "xWniG2oMKu85"),
#         "PASSWORD": os.getenv("DATABASE_PASSWORD", "BzjUftSC7JDSf%]["),
#         "HOST": os.getenv("DATABASE_HOST", "dev-core-pg.cluster-clzcsbthrzqz.eu-central-1.rds.amazonaws.com"),
#         "PORT": os.getenv("DATABASE_PORT", 5432),
#     },
# }
# PROD
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("DATABASE_NAME", "fin_cover"),
        "USER": os.getenv("DATABASE_USER", "St6ye3_3e4T6"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "TXRKjQNRJOq2WmUA"),
        "HOST": os.getenv("DATABASE_HOST", "prod-core-pg.cluster-clzcsbthrzqz.eu-central-1.rds.amazonaws.com"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
    },
}

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Ensure the logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': DailyRotatingFileHandler,
        #     'directory': os.path.join(BASE_DIR, 'logs'),
        #     'prefix': 'cover-admin',
        #     'formatter': 'verbose',
        # },
    },
    "loggers": {
        'django': {
            'handlers': ['console', ],
            'level': 'INFO',
            'propagate': True,
        },
        '__main__': {
            'handlers': ['console', ],
            'level': 'INFO',
            'propagate': True,
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
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
}

CELERY_BROKER_URL = "redis://localhost:6379/0"  # Redis URL
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"  # Redis URL for results

# settings.py

CELERY_BEAT_SCHEDULE = {
    "task1": {
        "task": "jobs.tasks.process_task1",
        # Replace with your cron schedule
        "schedule": crontab(minute=0, hour=0),
    },
    "task2": {
        "task": "jobs.tasks.process_task2",
        # Replace with your cron schedule
        "schedule": crontab(minute=0, hour=0),
    },
    "task3": {
        "task": "jobs.tasks.process_task3",
        # Replace with your cron schedule
        "schedule": crontab(minute=0, hour=0),
    },
}
# DEV
SUPABASE_TOKEN = os.getenv(
    "SUPABASE_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1ZHlsc3hla211Ymh6bnFuYWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NTkzNTIyMTEsImV4cCI6MTk3NDkyODIxMX0.LDLbwoiUEs9x0pRF1bdFtxzlzTzv9qWu_j8rzro-mtk",
)
SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://judylsxekmubhznqnakm.functions.supabase.co"
)
SUPABASE_POSTGREST_URL = os.getenv(
    "SUPABASE_URL", "https://judylsxekmubhznqnakm.supabase.co"
)
SUPABASE_PROJECTID = os.getenv("SUPABASE_PROJECTID", "judylsxekmubhznqnakm")
SUPABASE_REST_URL = os.getenv(
    "SUPABASE_REST_URL", "https://judylsxekmubhznqnakm.supabase.co"
)

# PROD
# SUPABASE_TOKEN = os.getenv(
#     "SUPABASE_TOKEN",
#     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhtc3BsaWJjZW11ZmhkeWV5dWdtIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NjIxMTA1MTYsImV4cCI6MTk3NzY4NjUxNn0.zWTZ9FUUmXglACrYicbkRfhJXgvkvvPTZSQdC4MEWdo",
# )
# SUPABASE_URL = os.getenv(
#     "SUPABASE_URL", "https://xmsplibcemufhdyeyugm.functions.supabase.co"
# )
# SUPABASE_POSTGREST_URL = os.getenv(
#     "SUPABASE_URL", "https://xmsplibcemufhdyeyugm.supabase.co"
# )
# SUPABASE_PROJECTID = os.getenv("SUPABASE_PROJECTID", "xmsplibcemufhdyeyugm")
# SUPABASE_REST_URL = os.getenv(
#     "SUPABASE_REST_URL", "https://xmsplibcemufhdyeyugm.supabase.co"
# )
