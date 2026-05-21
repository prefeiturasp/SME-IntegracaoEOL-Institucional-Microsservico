"""Testes unitários dos selectors UE — cobertura de branches."""

import pytest

pytestmark = pytest.mark.django_db


class TestListarUesBasicas:
    """Cobre listar_ues_basicas(): lista total, filtro e UE sem DRE."""

    def test_sem_ues_retorna_vazio(self, db):
        """Sem UEs cadastradas retorna lista vazia e total zero."""
        from apps.unidade_educacional.selectors import listar_ues_basicas
        items, total = listar_ues_basicas()
        assert items == []
        assert total == 0

    def test_com_codigos_especificos(self, ue_factory):
        """Filtro por código retorna apenas a UE solicitada."""
        from apps.unidade_educacional.selectors import listar_ues_basicas
        ue_factory(codigo_ue="019251")
        items, total = listar_ues_basicas(["019251"])
        assert len(items) == 1
        assert items[0]["codigoEscola"] == "019251"
        assert total == 1

    def test_codigos_nao_encontrados_retorna_vazio(self, db):
        """Códigos inexistentes retornam lista vazia e total zero."""
        from apps.unidade_educacional.selectors import listar_ues_basicas
        items, total = listar_ues_basicas(["999999"])
        assert items == []
        assert total == 0

    def test_ue_sem_dre_retorna_strings_vazias(self, db):
        """UE com DRE inexistente retorna nomeDRE e siglaDRE vazios."""
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.unidade_educacional.selectors import listar_ues_basicas
        UnidadeEducacional.objects.create(
            codigo_ue="000010",
            nome="UE SEM DRE",
            codigo_dre="INEXISTENTE",
            organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        items, total = listar_ues_basicas()
        assert items[0]["nomeDRE"] == ""
        assert items[0]["siglaDRE"] == ""
        assert total == 1


class TestObterUeBasicaPorCodigo:
    """Cobre obter_ue_basica_por_codigo(): contrato E02 e campos de ID."""

    def test_nao_encontrada_retorna_none(self, db):
        """Código inexistente retorna None."""
        from apps.unidade_educacional.selectors import (
            obter_ue_basica_por_codigo,
        )
        assert obter_ue_basica_por_codigo("000000") is None

    def test_retorna_contrato_correto(self, ue_factory):
        """UE encontrada retorna contrato com nome correto."""
        from apps.unidade_educacional.selectors import (
            obter_ue_basica_por_codigo,
        )
        ue_factory(codigo_ue="019251", nome="EMEF TESTE")
        resultado = obter_ue_basica_por_codigo("019251")
        assert resultado is not None
        assert resultado["nomeEscola"] == "EMEF TESTE"

    def test_ue_sem_tipo_escola(self, dre_factory, db):
        """UE sem tipo de escola retorna tipoEscola vazio e codigoTipoEscola zero."""
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.unidade_educacional.selectors import (
            obter_ue_basica_por_codigo,
        )
        dre = dre_factory()
        UnidadeEducacional.objects.create(
            codigo_ue="000011",
            nome="UE SEM TIPO",
            codigo_dre=dre.codigo_dre,
            codigo_tipo_escola=None,
            organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        resultado = obter_ue_basica_por_codigo("000011")
        assert resultado is not None
        assert resultado["tipoEscola"] == ""
        assert resultado["codigoTipoEscola"] == 0

    def test_contem_campos_ids_institucionais(self, ue_factory):
        """Resultado inclui tipoEscolaId, subprefeituraId e codigoIntegracao."""
        from apps.unidade_educacional.selectors import (
            obter_ue_basica_por_codigo,
        )
        ue_factory(codigo_ue="019254")
        resultado = obter_ue_basica_por_codigo("019254")
        assert resultado is not None
        assert "tipoEscolaId" in resultado
        assert "subprefeituraId" in resultado
        assert "codigoIntegracao" in resultado

    def test_tipo_escola_id_coincide_com_codigo_tipo_escola(self, ue_factory):
        """Retorna tipoEscolaId igual ao codigoTipoEscola."""
        from apps.unidade_educacional.selectors import (
            obter_ue_basica_por_codigo,
        )
        ue_factory(codigo_ue="019255")
        resultado = obter_ue_basica_por_codigo("019255")
        assert resultado is not None
        assert resultado["tipoEscolaId"] == resultado["codigoTipoEscola"]


class TestObterUeEol:
    """Cobre obter_ue_eol(): contrato E03 e UE não encontrada."""

    def test_nao_encontrada_retorna_none(self, db):
        """Código inexistente retorna None."""
        from apps.unidade_educacional.selectors import obter_ue_eol
        assert obter_ue_eol("000000") is None

    def test_retorna_contrato_correto(self, ue_factory):
        """UE encontrada retorna contrato com código e codigoReferencia."""
        from apps.unidade_educacional.selectors import obter_ue_eol
        ue = ue_factory(codigo_ue="019251")
        resultado = obter_ue_eol("019251")
        assert resultado is not None
        assert resultado["codigo"] == "019251"
        assert resultado["codigoReferencia"] == ue.codigo_dre


class TestObterUeCompleta:
    """Cobre obter_ue_completa(): UF, INEP, formatação de CEP."""

    def test_nao_encontrada_retorna_none(self, db):
        """Código inexistente retorna None."""
        from apps.unidade_educacional.selectors import obter_ue_completa
        assert obter_ue_completa("000000") is None

    def test_uf_sempre_sp(self, ue_factory):
        """Campo uf sempre retorna SP."""
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory()
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["uf"] == "SP"

    def test_sem_codigo_inep_retorna_none(self, ue_factory):
        """UE sem código INEP retorna codigoINEP None."""
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory(codigo_inep=None)
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["codigoINEP"] is None

    def test_cep_formatado_corretamente(self, ue_factory):
        """CEP com hífen é convertido para inteiro sem formatação."""
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory(cep="01310-100")
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["cep"] == 1310100

    def test_cep_none_retorna_none(self, ue_factory):
        """UE sem CEP retorna cep None."""
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory(cep=None)
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["cep"] is None


class TestObterSubprefeituraUe:
    """Cobre obter_subprefeituras_ue(): UE ausente e UE sem subprefeitura."""

    def test_ue_nao_encontrada_retorna_none(self, db):
        """Código inexistente retorna None."""
        from apps.unidade_educacional.selectors import obter_subprefeituras_ue
        assert obter_subprefeituras_ue("000000") is None

    def test_ue_sem_subprefeitura_retorna_lista_vazia(self, dre_factory, db):
        """UE com subprefeitura None retorna lista vazia."""
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.unidade_educacional.selectors import obter_subprefeituras_ue
        dre = dre_factory()
        UnidadeEducacional.objects.create(
            codigo_ue="000020",
            nome="UE SEM SUB",
            codigo_dre=dre.codigo_dre,
            codigo_sub_prefeitura=None,
            organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        resultado = obter_subprefeituras_ue("000020")
        assert resultado == []


class TestObterSincronizacaoUe:
    """Cobre obter_sincronizacao_ue(): contrato E23 e UE não encontrada."""

    def test_nao_encontrada_retorna_none(self, db):
        """Código inexistente retorna None."""
        from apps.unidade_educacional.selectors import obter_sincronizacao_ue
        assert obter_sincronizacao_ue("000000") is None

    def test_retorna_contrato_correto(self, ue_factory):
        """UE encontrada retorna contrato com ueCodigo e dreCodigo."""
        from apps.unidade_educacional.selectors import obter_sincronizacao_ue
        ue = ue_factory(codigo_ue="019251")
        resultado = obter_sincronizacao_ue("019251")
        assert resultado is not None
        assert resultado["ueCodigo"] == "019251"
        assert resultado["dreCodigo"] == int(ue.codigo_dre)


class TestListarEquipamentos:
    """Cobre listar_equipamentos(): sem filtro e filtros por DRE/sub/tipo."""

    def test_sem_ues_retorna_vazio(self, db):
        """Sem UEs cadastradas retorna lista vazia."""
        from apps.unidade_educacional.selectors import listar_equipamentos
        assert listar_equipamentos() == []

    def test_filtro_por_dre(self, ue_factory):
        """Filtro por DRE retorna UEs da DRE informada."""
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue = ue_factory()
        resultado = listar_equipamentos(codigos_dre=[ue.codigo_dre])
        assert len(resultado) >= 1

    def test_filtro_por_subprefeitura(self, ue_factory):
        """Filtro por subprefeitura retorna UEs da subprefeitura informada."""
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue = ue_factory()
        resultado = listar_equipamentos(
            codigos_subprefeitura=[ue.codigo_sub_prefeitura]
        )
        assert len(resultado) >= 1

    def test_filtro_por_tipo_escola(self, ue_factory):
        """Filtro por tipo de escola retorna UEs do tipo informado."""
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue = ue_factory()
        resultado = listar_equipamentos(tipos_escola=[ue.codigo_tipo_escola])
        assert len(resultado) >= 1

    def test_filtro_combinado_sem_resultado(self, ue_factory):
        """DRE inexistente no filtro retorna lista vazia."""
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue_factory()
        resultado = listar_equipamentos(codigos_dre=["DRE_NAOEXISTE"])
        assert resultado == []


class TestListarUnidadesParceiras:
    """Cobre listar_unidades_parceiras(): filtra apenas parceiras."""

    def test_sem_parceiras_retorna_vazio(self, ue_factory):
        """UE não parceira não aparece no resultado."""
        from apps.unidade_educacional.selectors import (
            listar_unidades_parceiras,
        )
        ue = ue_factory(organizacao_parceira=False)
        assert listar_unidades_parceiras([ue.codigo_ue]) == []

    def test_retorna_apenas_parceiras(self, ue_factory):
        """UE parceira aparece no resultado com código correto."""
        from apps.unidade_educacional.selectors import (
            listar_unidades_parceiras,
        )
        ue_factory(codigo_ue="019251", organizacao_parceira=True)
        resultado = listar_unidades_parceiras(["019251"])
        assert len(resultado) == 1
        assert resultado[0]["codigo"] == "019251"
