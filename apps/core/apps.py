from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configura o app de utilitários compartilhados."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"

    def ready(self) -> None:
        """Inicializa observabilidade e resiliência no boot do processo."""
        from sme_sidecar_sdk import runtime

        runtime.configure()
