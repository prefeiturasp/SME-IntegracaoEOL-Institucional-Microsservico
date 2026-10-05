"""Autenticação por API Key."""

from typing import Any

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class _ApiUser:
    """Representa o usuário autenticado via API key."""

    is_authenticated = True

    def __str__(self) -> str:
        return "api-key-user"


class ApiKeyAuthentication(BaseAuthentication):
    """Autentica requisições via API key no header configurado."""

    def authenticate(self, request: Request) -> tuple[Any, None] | None:
        """Valida a API key da requisição.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Tupla (usuário, None) se a chave for válida, None se ausente.

        Raises:
            AuthenticationFailed: Se o header estiver presente mas a chave
                for inválida.
        """
        header = settings.API_KEY_HEADER
        chave = request.headers.get(header, "")
        if not chave:
            return None
        if chave != settings.API_KEY:
            raise AuthenticationFailed("Chave de API inválida.")
        return (_ApiUser(), None)

    def authenticate_header(self, request: Request) -> str:
        return settings.API_KEY_HEADER
