"""
Configurações Django do microserviço Institucional.

Lê todas as variáveis sensíveis de variáveis de ambiente — nenhum valor fixo
em produção. Em desenvolvimento, valores padrão seguros são aplicados para
permitir `runserver` sem configuração adicional.

Variáveis obrigatórias em produção:
  - DJANGO_SECRET_KEY: chave secreta do Django (obrigatória quando DJANGO_DEBUG=0)
  - URL_BANCO_INSTITUCIONAL: URL postgres do banco populado pelo ETL institucional
    Formato: postgres://usuario:senha@host:5432/nome_banco
  - API_KEY: chave usada pelo header x-api-eol-key para autenticar todas as rotas
  - DJANGO_ALLOWED_HOSTS: hosts permitidos, separados por vírgula

Variáveis opcionais relevantes:
  - APP_PREFIX: prefixo de path removido pelo PrefixMiddleware (ex.: /institucional)
  - NIVEL_LOG: nível de logging (padrão INFO)
  - CACHE_TTL_DRE_SECONDS / CACHE_TTL_TIPO_ESCOLA_SECONDS: TTL de cache por domínio

O banco usa connection pooling via dj-db-conn-pool (pool de 5 conexões, sem overflow).
Sem URL_BANCO_INSTITUCIONAL, cai para SQLite in-memory — válido apenas em testes.
"""

import os
import urllib.parse
from pathlib import Path
from typing import Any

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
_POOL_OPTIONS = {
    "POOL_SIZE": DB_POOL_SIZE,
    "MAX_OVERFLOW": 0,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 1800,
    "PRE_PING": True,
}


def _parse_db_url(url: Any) -> dict:
    """Faz o parse de uma URL postgres para dict de configuração Django."""
    if not url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }

    if isinstance(url, bytes):
        url = url.decode("utf-8")

    parsed = urllib.parse.urlparse(str(url))
    return {
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "postgres",
        "PASSWORD": parsed.password or "postgres",
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or 5432),
        "POOL_OPTIONS": _POOL_OPTIONS,
    }


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("DJANGO_DEBUG", "1") == "0":
        raise ImproperlyConfigured(
            "A variável DJANGO_SECRET_KEY é obrigatória em produção."
        )
    SECRET_KEY = os.getenv("HOSTNAME", "dev-secret-key-fallback")

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

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
    "apps.core.middleware.PrefixMiddleware",
    "apps.core.middleware.ObservabilidadeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

URL_BANCO_INSTITUCIONAL = os.getenv("URL_BANCO_INSTITUCIONAL")

DATABASES = {
    "default": _parse_db_url(URL_BANCO_INSTITUCIONAL),
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, object]] = []

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

SCRIPT_PREFIX = os.getenv("APP_PREFIX", "")

FORCE_SCRIPT_NAME = SCRIPT_PREFIX or None
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

_static_prefix = SCRIPT_PREFIX.rstrip("/") if SCRIPT_PREFIX else ""
STATIC_URL = f"{_static_prefix}/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

NOME_APLICACAO = os.getenv(
    "NOME_APLICACAO", "SME-IntegracaoEOL-Institucional-Microsservico"
)
AMBIENTE_APLICACAO = os.getenv("AMBIENTE_APLICACAO", "local")
NIVEL_LOG = os.getenv("NIVEL_LOG", "INFO")

API_KEY = os.getenv("API_KEY", "dev-key-default")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "x-api-eol-key")

CACHE_TTL_DRE_SECONDS = int(os.getenv("CACHE_TTL_DRE_SECONDS", "300"))
CACHE_TTL_TIPO_ESCOLA_SECONDS = int(
    os.getenv("CACHE_TTL_TIPO_ESCOLA_SECONDS", "900")
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

_openapi_server_url = SCRIPT_PREFIX if SCRIPT_PREFIX else ""

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-IntegracaoEOL-Institucional-Microsservico API",
    "DESCRIPTION": (
        "Endpoints do domínio Institucional — SGP EOL.\n\n"
        "Consome dados do banco institucional populado pelo ETL "
        "SME-SGP-MS-ETL/apps/institucional."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVERS": [{"url": _openapi_server_url}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "padrao": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "padrao",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": NIVEL_LOG,
    },
}
