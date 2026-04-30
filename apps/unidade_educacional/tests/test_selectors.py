"""Testes unitários dos selectors UE — cobertura de branches."""

import pytest

pytestmark = pytest.mark.django_db


class TestListarUesBasicas:
    def test_sem_ues_retorna_vazio(self, db):
        from apps.unidade_educacional.selectors import listar_ues_basicas
        assert listar_ues_basicas() == []

    def test_com_codigos_especificos(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_ues_basicas
        ue = ue_factory(codigo_ue="019251")
        resultado = listar_ues_basicas(["019251"])
        assert len(resultado) == 1
        assert resultado[0]["codigoEscola"] == "019251"

    def test_codigos_nao_encontrados_retorna_vazio(self, db):
        from apps.unidade_educacional.selectors import listar_ues_basicas
        assert listar_ues_basicas(["999999"]) == []

    def test_ue_sem_dre_retorna_strings_vazias(self, db):
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
        resultado = listar_ues_basicas()
        assert resultado[0]["nomeDRE"] == ""
        assert resultado[0]["siglaDRE"] == ""


class TestObterUeBasicaPorCodigo:
    def test_nao_encontrada_retorna_none(self, db):
        from apps.unidade_educacional.selectors import obter_ue_basica_por_codigo
        assert obter_ue_basica_por_codigo("000000") is None

    def test_retorna_contrato_correto(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_basica_por_codigo
        ue = ue_factory(codigo_ue="019251", nome="EMEF TESTE")
        resultado = obter_ue_basica_por_codigo("019251")
        assert resultado is not None
        assert resultado["nomeEscola"] == "EMEF TESTE"

    def test_ue_sem_tipo_escola(self, dre_factory, db):
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.unidade_educacional.selectors import obter_ue_basica_por_codigo
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
        from apps.unidade_educacional.selectors import obter_ue_basica_por_codigo
        ue = ue_factory(codigo_ue="019254")
        resultado = obter_ue_basica_por_codigo("019254")
        assert resultado is not None
        assert "tipoEscolaId" in resultado
        assert "subprefeituraId" in resultado
        assert "codigoIntegracao" in resultado

    def test_tipo_escola_id_coincide_com_codigo_tipo_escola(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_basica_por_codigo
        ue = ue_factory(codigo_ue="019255")
        resultado = obter_ue_basica_por_codigo("019255")
        assert resultado is not None
        assert resultado["tipoEscolaId"] == resultado["codigoTipoEscola"]


class TestObterUeEol:
    def test_nao_encontrada_retorna_none(self, db):
        from apps.unidade_educacional.selectors import obter_ue_eol
        assert obter_ue_eol("000000") is None

    def test_retorna_contrato_correto(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_eol
        ue = ue_factory(codigo_ue="019251")
        resultado = obter_ue_eol("019251")
        assert resultado is not None
        assert resultado["codigo"] == "019251"
        assert resultado["codigoReferencia"] == "019251"


class TestObterUeCompleta:
    def test_nao_encontrada_retorna_none(self, db):
        from apps.unidade_educacional.selectors import obter_ue_completa
        assert obter_ue_completa("000000") is None

    def test_uf_sempre_sp(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory()
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["uf"] == "SP"

    def test_sem_codigo_inep_retorna_none(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory(codigo_inep=None)
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["codigoINEP"] is None

    def test_cep_formatado_corretamente(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory(cep="01310-100")
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["cep"] == 1310100

    def test_cep_none_retorna_none(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_ue_completa
        ue = ue_factory(cep=None)
        resultado = obter_ue_completa(ue.codigo_ue)
        assert resultado is not None
        assert resultado["cep"] is None


class TestObterSubprefeituraUe:
    def test_ue_nao_encontrada_retorna_none(self, db):
        from apps.unidade_educacional.selectors import obter_subprefeituras_ue
        assert obter_subprefeituras_ue("000000") is None

    def test_ue_sem_subprefeitura_retorna_lista_vazia(self, dre_factory, db):
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
    def test_nao_encontrada_retorna_none(self, db):
        from apps.unidade_educacional.selectors import obter_sincronizacao_ue
        assert obter_sincronizacao_ue("000000") is None

    def test_retorna_contrato_correto(self, ue_factory):
        from apps.unidade_educacional.selectors import obter_sincronizacao_ue
        ue = ue_factory(codigo_ue="019251")
        resultado = obter_sincronizacao_ue("019251")
        assert resultado is not None
        assert resultado["ueCodigo"] == "019251"
        assert resultado["dreCodigo"] == ue.codigo_dre


class TestListarEquipamentos:
    def test_sem_ues_retorna_vazio(self, db):
        from apps.unidade_educacional.selectors import listar_equipamentos
        assert listar_equipamentos() == []

    def test_filtro_por_dre(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue = ue_factory()
        resultado = listar_equipamentos(codigos_dre=[ue.codigo_dre])
        assert len(resultado) >= 1

    def test_filtro_por_subprefeitura(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue = ue_factory()
        resultado = listar_equipamentos(codigos_subprefeitura=[ue.codigo_sub_prefeitura])
        assert len(resultado) >= 1

    def test_filtro_por_tipo_escola(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue = ue_factory()
        resultado = listar_equipamentos(tipos_escola=[ue.codigo_tipo_escola])
        assert len(resultado) >= 1

    def test_filtro_combinado_sem_resultado(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_equipamentos
        ue_factory()
        resultado = listar_equipamentos(codigos_dre=["DRE_NAOEXISTE"])
        assert resultado == []


class TestListarUnidadesParceiras:
    def test_sem_parceiras_retorna_vazio(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_unidades_parceiras
        ue = ue_factory(organizacao_parceira=False)
        assert listar_unidades_parceiras([ue.codigo_ue]) == []

    def test_retorna_apenas_parceiras(self, ue_factory):
        from apps.unidade_educacional.selectors import listar_unidades_parceiras
        ue = ue_factory(codigo_ue="019251", organizacao_parceira=True)
        resultado = listar_unidades_parceiras(["019251"])
        assert len(resultado) == 1
        assert resultado[0]["codigo"] == "019251"
