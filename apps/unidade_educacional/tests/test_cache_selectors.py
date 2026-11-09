"""Valida o uso do cache de leitura nos selectors do domínio UE."""

from collections.abc import Callable
from unittest.mock import patch

import pytest
from pytest_django.fixtures import DjangoAssertNumQueries

from apps.unidade_educacional import selectors
from apps.unidade_educacional.models import UnidadeEducacional
from apps.unidade_educacional.selectors import (
    listar_equipamentos,
    listar_ues_basicas,
    obter_ue_eol,
)

pytestmark = pytest.mark.django_db


class TestCacheSelectorsUe:
    """A segunda consulta idêntica deve ser atendida pelo cache."""

    def test_equipamentos_segunda_chamada_sem_consulta(
        self, ue_factory, django_assert_num_queries
    ):
        """E25 reutiliza o resultado sem acessar o banco."""
        ue = ue_factory()
        primeira = listar_equipamentos(codigos_dre=[ue.codigo_dre])
        assert len(primeira) == 1

        with django_assert_num_queries(0):
            assert listar_equipamentos(codigos_dre=[ue.codigo_dre]) == primeira

    def test_equipamentos_chave_ignora_ordem_dos_filtros(
        self, ue_factory, django_assert_num_queries
    ):
        """Mesmos filtros em ordem distinta compartilham a entrada."""
        ue = ue_factory()
        filtros = [ue.codigo_dre, "OUTRA_DRE"]
        primeira = listar_equipamentos(codigos_dre=filtros)

        with django_assert_num_queries(0):
            assert listar_equipamentos(codigos_dre=filtros[::-1]) == primeira

    def test_equipamentos_chave_considera_o_nome(self, ue_factory):
        """Filtros distintos não compartilham a mesma entrada de cache."""
        ue_factory()

        assert listar_equipamentos(nome_escola="NAO EXISTE") == []
        assert len(listar_equipamentos()) == 1

    def test_ues_basicas_pagina_segunda_chamada_sem_consulta(
        self, ue_factory, django_assert_num_queries
    ):
        """E27 reutiliza a página sem acessar o banco."""
        ue_factory()
        primeira = listar_ues_basicas(limite=10, offset=0)
        assert primeira[1] == 1

        with django_assert_num_queries(0):
            assert listar_ues_basicas(limite=10, offset=0) == primeira

    def test_ues_basicas_com_codigos_nao_usa_cache(self, ue_factory):
        """Consulta com lista de códigos reflete o banco a cada chamada."""
        ue = ue_factory()
        assert listar_ues_basicas([ue.codigo_ue])[1] == 1

        ue.delete()

        assert listar_ues_basicas([ue.codigo_ue]) == ([], 0)


class TestCacheUeEol:
    """Valida o cache dos dados resumidos por código EOL."""

    def test_segunda_chamada_sem_consulta(
        self,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """E03 reutiliza o contrato completo sem consultar o banco."""
        ue = ue_factory(codigo_tipo_unidade_educacao=7)
        with django_assert_num_queries(1):
            primeira = obter_ue_eol(ue.codigo_ue)
        assert primeira == {
            "codigo": ue.codigo_ue,
            "sigla": ue.nome_nao_oficial,
            "nomeUnidade": ue.nome,
            "tipo": 7,
            "codigoReferencia": ue.codigo_dre,
        }

        with django_assert_num_queries(0):
            assert obter_ue_eol(ue.codigo_ue) == primeira

    def test_chaves_isoladas_por_codigo(
        self,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """UEs distintas mantêm seus próprios contratos em cache."""
        primeira_ue = ue_factory()
        segunda_ue = ue_factory()
        primeira = obter_ue_eol(primeira_ue.codigo_ue)
        segunda = obter_ue_eol(segunda_ue.codigo_ue)
        assert primeira != segunda

        with django_assert_num_queries(0):
            assert obter_ue_eol(primeira_ue.codigo_ue) == primeira
            assert obter_ue_eol(segunda_ue.codigo_ue) == segunda

    def test_resultado_expira_apos_vinte_quatro_horas(
        self,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """O TTL de 24h preserva os dados até a próxima consulta à origem."""
        ue = ue_factory()
        codigo = ue.codigo_ue
        with patch("time.time", return_value=1_800_000_000) as relogio:
            primeira = obter_ue_eol(codigo)
            ue.delete()
            relogio.return_value += 24 * 60 * 60 - 1

            with django_assert_num_queries(0):
                assert obter_ue_eol(codigo) == primeira

            relogio.return_value += 1
            with django_assert_num_queries(1):
                assert obter_ue_eol(codigo) is None

    def test_ue_nao_encontrada_e_consultada_novamente(
        self, ue_factory: Callable[..., UnidadeEducacional]
    ) -> None:
        """Uma ausência anterior não esconde uma UE criada pelo ETL."""
        assert obter_ue_eol("019251") is None
        ue = ue_factory(codigo_ue="019251", nome_nao_oficial=None)

        resultado = obter_ue_eol(ue.codigo_ue)
        assert resultado is not None
        assert resultado["codigo"] == ue.codigo_ue
        assert resultado["sigla"] is None

    @pytest.mark.parametrize("operacao", ["get", "set"])
    def test_falha_no_cache_preserva_resposta(
        self, operacao: str, ue_factory: Callable[..., UnidadeEducacional]
    ) -> None:
        """E03 consulta a origem mesmo com falha no KeyDB."""
        ue = ue_factory()
        with patch(
            f"apps.core.cache.cache.{operacao}",
            side_effect=ConnectionError("Cache indisponível"),
        ):
            resultado = obter_ue_eol(ue.codigo_ue)

        assert resultado is not None
        assert resultado["codigo"] == ue.codigo_ue
        assert obter_ue_eol(ue.codigo_ue) == resultado


class TestColunaExiste:
    """Valida a memorização em processo da introspecção de schema."""

    def setup_method(self) -> None:
        """Limpa a memorização antes de cada teste."""
        selectors._consultar_coluna_existe.cache_clear()

    def teardown_method(self) -> None:
        """Limpa a memorização após cada teste."""
        selectors._consultar_coluna_existe.cache_clear()

    def test_resposta_valida_e_memorizada(self):
        """A segunda chamada não consulta o banco novamente."""
        with patch("django.db.connection.cursor") as cursor:
            cursor.return_value.__enter__.return_value.fetchone.return_value = (
                1,
            )

            assert selectors._coluna_existe("tabela", "coluna") is True
            assert selectors._coluna_existe("tabela", "coluna") is True

        assert cursor.call_count == 1

    def test_falha_nao_e_memorizada(self):
        """Erro de banco retorna False sem gravar o resultado."""
        with patch("django.db.connection.cursor", side_effect=RuntimeError):
            assert selectors._coluna_existe("tabela", "coluna") is False

        assert selectors._consultar_coluna_existe.cache_info().currsize == 0
