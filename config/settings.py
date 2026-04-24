"""Configurações do microsserviço institucional."""
import os

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "dev-secret-key-not-for-production"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "t")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.dre",
    "apps.unidade_educacional",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

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

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.core.authentication.ApiKeyPermission",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

API_KEY_HEADER = os.environ.get("API_KEY_HEADER", "x-api-key")

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-IntegracaoEOL-MS-Institucional API",
    "DESCRIPTION": "Mock do microsserviço institucional EOL",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKey": {
                "type": "apiKey",
                "name": API_KEY_HEADER,
                "in": "header",
            }
        }
    },
    "SECURITY": [{"ApiKey": []}],
}

API_KEY = os.environ.get("API_KEY", "dev-key-default")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "static/"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_TZ = True
USE_I18N = True
