"""
Settings para execução dos testes automatizados.

Herda todas as configurações de config.settings e substitui apenas o banco
por SQLite in-memory — elimina dependência de PostgreSQL na pipeline de CI
e garante isolamento total entre execuções (banco descartado ao fim de cada run).

As tabelas managed=False são criadas manualmente no conftest.py via
`django_db_setup`, porque o SQLite não executa migrations reais.

Ativado automaticamente pelo pytest via pytest.ini (DJANGO_SETTINGS_MODULE).
"""

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
