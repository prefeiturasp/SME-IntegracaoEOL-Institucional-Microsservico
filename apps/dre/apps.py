"""Configuração da aplicação DRE."""

from django.apps import AppConfig


class DreConfig(AppConfig):
    """Configura a aplicação DRE."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dre'
