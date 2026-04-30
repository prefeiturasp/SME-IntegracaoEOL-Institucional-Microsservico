"""Autenticação por API Key para todas as rotas."""

from typing import Any

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class _ApiUser:
    """Usuário sintético retornado pelo autenticador de API key."""

    is_authenticated = True

    def __str__(self) -> str:
        return "api-key-user"


class ApiKeyAuthentication(BaseAuthentication):
    """Valida o header API Key configurado em API_KEY_HEADER."""

    def authenticate(self, request: Request) -> tuple[Any, None] | None:
        """Retorna (_ApiUser, None) se a chave for válida, None se ausente."""
        header = settings.API_KEY_HEADER
        chave = request.headers.get(header, "")
        if not chave:
            return None
        if chave != settings.API_KEY:
            raise AuthenticationFailed("Chave de API inválida.")
        return (_ApiUser(), None)

    def authenticate_header(self, request: Request) -> str:
        return settings.API_KEY_HEADER
