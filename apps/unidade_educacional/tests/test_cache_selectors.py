"""Valida o uso do cache de leitura nos selectors do domínio UE."""

from unittest.mock import patch

import pytest

from apps.unidade_educacional import selectors
from apps.unidade_educacional.selectors import (
    listar_equipamentos,
    listar_ues_basicas,
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
