"""Valida o uso do cache de leitura nos selectors do domínio DRE."""

import pytest

from apps.dre.selectors import (
    listar_codigos_dres_abrangencia,
    listar_escolas_por_dre,
)

pytestmark = pytest.mark.django_db


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
