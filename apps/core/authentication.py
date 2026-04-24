"""Permissão baseada em X-API-Key para todas as rotas."""
from typing import Any

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class NaoAutorizado(APIException):
    """Exceção que força resposta HTTP 401."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Chave de API ausente ou inválida."
    default_code = "nao_autorizado"


class ApiKeyPermission(BasePermission):
    """Valida o header X-API-Key em todas as requisições."""

    message = "Chave de API ausente ou inválida."

    def has_permission(self, request: Request, _view: Any) -> bool:
        """Lança 401 se X-API-Key ausente ou inválida."""
        chave = request.headers.get(settings.API_KEY_HEADER, "")
        if chave != settings.API_KEY:
            raise NaoAutorizado()
        return True
