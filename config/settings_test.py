"""
Settings para execução dos testes automatizados.

Herda todas as configurações de config.settings e substitui apenas o banco
por SQLite in-memory — elimina dependência de PostgreSQL na pipeline de CI
e garante isolamento total entre execuções (banco descartado ao fim de cada run).

As tabelas managed=False são criadas manualmente no conftest.py via
`django_db_setup`, porque o SQLite não executa migrations reais.

Ativado automaticamente pelo pytest via pytest.ini (DJANGO_SETTINGS_MODULE).
"""

from config.settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
