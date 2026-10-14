"""Cache de leitura no KeyDB, protegido por circuit breaker."""

from __future__ import annotations

import logging
from collections.abc import Callable

from django.core.cache import cache
from sme_sidecar_sdk.resilience import get_circuit_breaker

logger = logging.getLogger(__name__)

# Nome do breaker dedicado ao KeyDB, isolado dos breakers de HTTP.
_BREAKER_NAME = "institucional-keydb-cache"

# TTL praticado hoje pelo legado
TTL_LEGADO_PADRAO_MINUTOS = 1440

# TTL padrão definido para os novos não cacheados pelo legado
TTL_RECOMENDADO_MINUTOS = 720


def obter_ou_calcular[
    T
](chave: str, calcular: Callable[[], T], minutos_para_expirar: int,) -> T:
    """Busca chave no KeyDB ou executa calcular e grava o resultado.

    Args:
        chave: Chave de cache já normalizada com os parâmetros da consulta.
        calcular: Função síncrona que busca o dado na origem quando o
            cache não possui o valor.
        minutos_para_expirar: Tempo de vida do valor em cache, em minutos.

    Returns:
        Dado obtido do cache ou recém-calculado por calcular.
    """
    breaker = get_circuit_breaker(_BREAKER_NAME)

    valor_em_cache: T | None = None
    try:
        valor_em_cache = breaker.call(cache.get, chave)
    except Exception:
        logger.warning(
            "Falha ao consultar cache KeyDB (chave=%s)", chave, exc_info=True
        )

    if valor_em_cache is not None:
        return valor_em_cache

    valor = calcular()

    try:
        breaker.call(cache.set, chave, valor, minutos_para_expirar * 60)
    except Exception:
        logger.warning(
            "Falha ao gravar cache KeyDB (chave=%s)", chave, exc_info=True
        )

    return valor
