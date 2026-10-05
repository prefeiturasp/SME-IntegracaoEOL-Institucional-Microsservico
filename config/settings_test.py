"""Configurações Django para execução dos testes automatizados."""

from config.settings import (  # noqa: F401
    API_KEY,
    API_KEY_HEADER,
    ALLOWED_HOSTS,
    AUTH_PASSWORD_VALIDATORS,
    CACHE_TTL_DRE_SECONDS,
    CACHE_TTL_TIPO_ESCOLA_SECONDS,
    DEBUG,
    DEFAULT_AUTO_FIELD,
    FORCE_SCRIPT_NAME,
    INSTALLED_APPS,
    LANGUAGE_CODE,
    LOGGING,
    MIDDLEWARE,
    NOME_APLICACAO,
    AMBIENTE_APLICACAO,
    NIVEL_LOG,
    REST_FRAMEWORK,
    ROOT_URLCONF,
    SCRIPT_PREFIX,
    SECRET_KEY,
    SECURE_PROXY_SSL_HEADER,
    SPECTACULAR_SETTINGS,
    STATIC_ROOT,
    STATIC_URL,
    TEMPLATES,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
    USE_X_FORWARDED_HOST,
    WSGI_APPLICATION,
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
