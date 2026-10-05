"""Middlewares de observabilidade e roteamento."""

import logging
import time
import uuid

from django.conf import settings
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

_SLOW_QUERY_MS = 200


class ObservabilidadeMiddleware:
    """Injeta X-Correlation-ID e registra métricas de cada requisição."""

    def __init__(self, get_response: object) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Processa a requisição injetando correlation ID e métricas de tempo.

        Args:
            request: Requisição HTTP recebida pelo Django.

        Returns:
            Resposta HTTP com headers X-Correlation-Id e X-Response-Time-Ms.
        """
        correlation_id = (
            request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
        )
        request.correlation_id = correlation_id  # type: ignore[attr-defined]

        t0 = time.monotonic()
        response: HttpResponse = self.get_response(request)  # type: ignore[assignment]
        elapsed_ms = round((time.monotonic() - t0) * 1000, 2)

        response["X-Correlation-Id"] = correlation_id
        response["X-Response-Time-Ms"] = str(elapsed_ms)

        log_level = (
            logging.WARNING if elapsed_ms > _SLOW_QUERY_MS else logging.DEBUG
        )
        logger.log(
            log_level,
            "method=%s path=%s status=%s elapsed_ms=%s correlation_id=%s",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            correlation_id,
        )
        return response


class PrefixMiddleware:
    """Remove o prefixo de path configurado antes do roteamento Django."""

    def __init__(self, get_response: object) -> None:
        self.get_response = get_response
        prefix = getattr(settings, "SCRIPT_PREFIX", "")
        self.prefix = f"/{prefix.strip('/')}" if prefix else ""

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Reescreve o path da requisição removendo o prefixo configurado.

        Args:
            request: Requisição HTTP recebida pelo Django.

        Returns:
            Resposta HTTP após o roteamento com o path ajustado.
        """
        if self.prefix and request.path_info.startswith(self.prefix):
            request.path_info = (
                request.path_info[len(self.prefix):] or "/"
            )
            request.path = request.path_info
        return self.get_response(request)  # type: ignore[return-value]
