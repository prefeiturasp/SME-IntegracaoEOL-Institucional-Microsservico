"""Valida o uso do cache de leitura nos selectors do domínio DRE."""

from collections.abc import Callable, Sequence
from unittest.mock import patch

import pytest
from pytest_django.fixtures import DjangoAssertNumQueries

from apps.dre.models import DRE
from apps.dre.selectors import (
    listar_codigos_dres_abrangencia,
    listar_codigos_integracao_por_dre,
    listar_codigos_ues_por_dre,
    listar_escolas_por_dre,
    listar_unidades_por_dre,
)
from apps.unidade_educacional.models import UnidadeEducacional

pytestmark = pytest.mark.django_db

_SELECTORS_POR_DRE = [
    pytest.param(listar_codigos_ues_por_dre, 1, id="D08"),
    pytest.param(listar_unidades_por_dre, 4, id="D10"),
    pytest.param(listar_codigos_integracao_por_dre, 1, id="D11"),
]


@pytest.mark.parametrize(("selector", "consultas"), _SELECTORS_POR_DRE)
class TestCachePorDre:
    """Valida cache, isolamento e expiração das consultas por DRE."""

    def test_segunda_chamada_sem_consulta(
        self,
        selector: Callable[[str], Sequence[object]],
        consultas: int,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """A resposta quente é idêntica e dispensa consultas ao banco."""
        ue = ue_factory()
        with django_assert_num_queries(consultas):
            primeira = selector(ue.codigo_dre)
        assert len(primeira) == 1

        with django_assert_num_queries(0):
            assert selector(ue.codigo_dre) == primeira

    def test_chaves_isoladas_por_dre(
        self,
        selector: Callable[[str], Sequence[object]],
        consultas: int,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """DREs distintas mantêm seus próprios resultados em cache."""
        primeira_ue = ue_factory()
        segunda_ue = ue_factory()
        primeira = selector(primeira_ue.codigo_dre)
        segunda = selector(segunda_ue.codigo_dre)
        assert primeira != segunda

        with django_assert_num_queries(0):
            assert selector(primeira_ue.codigo_dre) == primeira
            assert selector(segunda_ue.codigo_dre) == segunda

    def test_resultado_vazio_tambem_e_cacheado(
        self,
        selector: Callable[[str], Sequence[object]],
        consultas: int,
        dre_factory: Callable[..., DRE],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """Uma DRE sem UEs não é consultada novamente a cada chamada."""
        dre = dre_factory()
        assert selector(dre.codigo_dre) == []

        with django_assert_num_queries(0):
            assert selector(dre.codigo_dre) == []

    def test_resultado_expira_apos_doze_horas(
        self,
        selector: Callable[[str], Sequence[object]],
        consultas: int,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """Mudanças na origem ficam visíveis quando vence o TTL de 12h."""
        ue = ue_factory()
        with patch("time.time", return_value=1_800_000_000) as relogio:
            primeira = selector(ue.codigo_dre)
            ue.delete()
            relogio.return_value += 12 * 60 * 60 - 1

            with django_assert_num_queries(0):
                assert selector(ue.codigo_dre) == primeira

            relogio.return_value += 1
            assert selector(ue.codigo_dre) == []

    @pytest.mark.parametrize("operacao", ["get", "set"])
    def test_falha_no_cache_preserva_resposta(
        self,
        selector: Callable[[str], Sequence[object]],
        consultas: int,
        operacao: str,
        ue_factory: Callable[..., UnidadeEducacional],
    ) -> None:
        """Falhas de leitura ou gravação não impedem consultar a origem."""
        ue = ue_factory()
        with patch(
            f"apps.core.cache.cache.{operacao}",
            side_effect=ConnectionError("Cache indisponível"),
        ):
            resultado = selector(ue.codigo_dre)

        assert len(resultado) == 1
        assert selector(ue.codigo_dre) == resultado


class TestCacheSelectorsDre:
    """A segunda consulta idêntica deve ser atendida pelo cache."""

    def test_codigos_dres_segunda_chamada_sem_consulta(
        self, dre_abrangencia_factory, django_assert_num_queries
    ):
        """ABR01 reutiliza o resultado sem acessar o banco."""
        dre_abrangencia_factory(codigo_dre="108100", nome="DRE A", ordem=1)
        assert listar_codigos_dres_abrangencia() == ["108100"]

        with django_assert_num_queries(0):
            assert listar_codigos_dres_abrangencia() == ["108100"]

    def test_escolas_por_dre_segunda_chamada_sem_consulta(
        self, ue_factory, django_assert_num_queries
    ):
        """D05/D06/D09 reutilizam o resultado sem acessar o banco."""
        ue = ue_factory()
        primeira = listar_escolas_por_dre(ue.codigo_dre)
        assert len(primeira) == 1

        with django_assert_num_queries(0):
            assert listar_escolas_por_dre(ue.codigo_dre) == primeira

    def test_escolas_por_dre_chave_considera_o_tipo(self, ue_factory):
        """Tipos diferentes não compartilham a mesma entrada de cache."""
        ue = ue_factory()
        todas = listar_escolas_por_dre(ue.codigo_dre)
        outro_tipo = listar_escolas_por_dre(ue.codigo_dre, 999999)

        assert len(todas) == 1
        assert outro_tipo == []

    def test_valor_em_cache_persiste_ate_expirar(
        self, dre_abrangencia_factory
    ):
        """Mudanças na origem só aparecem após o TTL (sem invalidação)."""
        dre_abrangencia_factory(codigo_dre="108100", nome="DRE A", ordem=1)
        assert listar_codigos_dres_abrangencia() == ["108100"]

        dre_abrangencia_factory(codigo_dre="108200", nome="DRE B", ordem=2)

        assert listar_codigos_dres_abrangencia() == ["108100"]
