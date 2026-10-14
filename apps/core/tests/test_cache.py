"""Valida o helper de cache do KeyDB (apps.core.cache)."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

from apps.core import cache


class _BreakerStub:
    """Circuit breaker de teste: executa a função ou levanta um erro fixo."""

    def __init__(
        self,
        erro: Exception | None = None,
        side_effect: Callable[..., Any] | None = None,
    ) -> None:
        """Inicializa o stub.

        Args:
            erro: Exceção que ``call`` deve levantar; ``None`` executa ``func``.
            side_effect: Substitui a execução de ``func`` quando informado.
        """
        self.erro = erro
        self.side_effect = side_effect

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Executa ``func`` ou levanta o erro configurado no teste.

        Args:
            func: Função a ser executada quando não há erro configurado.
            *args: Argumentos posicionais repassados a ``func``.
            **kwargs: Argumentos nomeados repassados a ``func``.

        Returns:
            O retorno de ``func(*args, **kwargs)``.

        Raises:
            Exception: O erro configurado em ``erro``, quando houver.
        """
        if self.erro is not None:
            raise self.erro
        if self.side_effect is not None:
            return self.side_effect(func, *args, **kwargs)
        return func(*args, **kwargs)


@patch("apps.core.cache.get_circuit_breaker")
@patch("apps.core.cache.cache")
def test_retorna_valor_em_cache_sem_chamar_calcular(
    mock_django_cache: MagicMock, mock_get_breaker: MagicMock
) -> None:
    """Um hit no cache não deve executar ``calcular`` nem regravar."""
    mock_django_cache.get.return_value = ["valor-cacheado"]
    mock_get_breaker.return_value = _BreakerStub()
    calcular = MagicMock(return_value=["novo-valor"])

    resultado = cache.obter_ou_calcular("minha-chave", calcular, 60)

    assert resultado == ["valor-cacheado"]
    calcular.assert_not_called()
    mock_django_cache.set.assert_not_called()


@patch("apps.core.cache.get_circuit_breaker")
@patch("apps.core.cache.cache")
def test_calcula_e_grava_no_cache_quando_ausente(
    mock_django_cache: MagicMock, mock_get_breaker: MagicMock
) -> None:
    """Um miss no cache executa ``calcular`` e grava o TTL em segundos."""
    mock_django_cache.get.return_value = None
    mock_get_breaker.return_value = _BreakerStub()
    calcular = MagicMock(return_value={"quantidade": 10})

    resultado = cache.obter_ou_calcular("minha-chave", calcular, 30)

    assert resultado == {"quantidade": 10}
    calcular.assert_called_once_with()
    mock_django_cache.set.assert_called_once_with(
        "minha-chave", {"quantidade": 10}, 30 * 60
    )


@patch("apps.core.cache.get_circuit_breaker")
@patch("apps.core.cache.cache")
def test_lista_vazia_em_cache_nao_recalcula(
    mock_django_cache: MagicMock, mock_get_breaker: MagicMock
) -> None:
    """Lista vazia é um valor válido em cache e não deve ser recalculada."""
    mock_django_cache.get.return_value = []
    mock_get_breaker.return_value = _BreakerStub()
    calcular = MagicMock(return_value=["novo-valor"])

    resultado = cache.obter_ou_calcular("minha-chave", calcular, 10)

    assert resultado == []
    calcular.assert_not_called()


@patch("apps.core.cache.get_circuit_breaker")
@patch("apps.core.cache.cache")
def test_degrada_para_origem_quando_leitura_falha(
    mock_django_cache: MagicMock, mock_get_breaker: MagicMock
) -> None:
    """Falha (ou circuito aberto) na leitura não deve propagar o erro."""
    mock_get_breaker.return_value = _BreakerStub(
        erro=RuntimeError("keydb indisponível")
    )
    calcular = MagicMock(return_value=["origem"])

    resultado = cache.obter_ou_calcular("minha-chave", calcular, 10)

    assert resultado == ["origem"]
    calcular.assert_called_once_with()


@patch("apps.core.cache.get_circuit_breaker")
@patch("apps.core.cache.cache")
def test_retorna_valor_mesmo_quando_gravacao_falha(
    mock_django_cache: MagicMock, mock_get_breaker: MagicMock
) -> None:
    """Falha ao gravar não deve propagar o erro nem alterar o retorno."""
    mock_django_cache.get.return_value = None

    def _call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if func is mock_django_cache.set:
            raise RuntimeError("keydb indisponível")
        return func(*args, **kwargs)

    mock_get_breaker.return_value = _BreakerStub(side_effect=_call)
    calcular = MagicMock(return_value="valor")

    resultado = cache.obter_ou_calcular("minha-chave", calcular, 10)

    assert resultado == "valor"
