"""Testes unitários dos selectors DRE — cobertura de branches."""

import pytest

pytestmark = pytest.mark.django_db


class TestListarDres:
    def test_retorna_lista_vazia_sem_dres(self, db):
        from apps.dre.selectors import listar_dres
        assert listar_dres() == []

    def test_retorna_lista_com_dres(self, dre_factory):
        from apps.dre.selectors import listar_dres
        dre_factory(codigo_dre="108100", nome="DRE A", sigla="A")
        resultado = listar_dres()
        assert len(resultado) == 1
        assert resultado[0]["codigoDRE"] == "108100"

    def test_sigla_none_vira_string_vazia(self, dre_factory):
        from apps.dre.selectors import listar_dres
        dre_factory(codigo_dre="108100", nome="DRE SEM SIGLA", sigla=None)
        resultado = listar_dres()
        assert resultado[0]["siglaDRE"] == ""


class TestFiltrarDresPorCodigos:
    def test_codigos_nao_encontrados(self, db):
        from apps.dre.selectors import filtrar_dres_por_codigos
        assert filtrar_dres_por_codigos(["999999"]) == []

    def test_filtra_apenas_os_solicitados(self, dre_factory):
        from apps.dre.selectors import filtrar_dres_por_codigos
        dre_factory(codigo_dre="108100", nome="A", sigla="A")
        dre_factory(codigo_dre="108200", nome="B", sigla="B")
        resultado = filtrar_dres_por_codigos(["108100"])
        assert len(resultado) == 1
        assert resultado[0]["codigoDRE"] == "108100"


class TestObterDrePorCodigo:
    def test_retorna_none_se_nao_existir(self, db):
        from apps.dre.selectors import obter_dre_por_codigo
        assert obter_dre_por_codigo("000000") is None

    def test_retorna_dre_existente(self, dre_factory):
        from apps.dre.selectors import obter_dre_por_codigo
        dre_factory(codigo_dre="108100", nome="DRE X", sigla="X")
        resultado = obter_dre_por_codigo("108100")
        assert resultado is not None
        assert resultado["nomeDRE"] == "DRE X"


class TestListarSubprefeiturasPorDre:
    def test_dre_sem_ues_retorna_vazio(self, db):
        from apps.dre.selectors import listar_subprefeituras_por_dre
        assert listar_subprefeituras_por_dre("000000") == []

    def test_ue_sem_subprefeitura_excluida(self, dre_factory, db):
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.dre.selectors import listar_subprefeituras_por_dre
        dre = dre_factory()
        UnidadeEducacional.objects.create(
            codigo_ue="000001",
            nome="UE SEM SUB",
            codigo_dre=dre.codigo_dre,
            codigo_sub_prefeitura=None,
            organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        assert listar_subprefeituras_por_dre(dre.codigo_dre) == []


class TestListarEscolasPorDre:
    def test_dre_nao_existente_retorna_vazio(self, db):
        from apps.dre.selectors import listar_escolas_por_dre
        assert listar_escolas_por_dre("999999") == []

    def test_dre_sem_ues_retorna_vazio(self, dre_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        dre = dre_factory()
        assert listar_escolas_por_dre(dre.codigo_dre) == []

    def test_com_filtro_de_tipo(self, ue_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre, "EMEF")
        assert isinstance(resultado, list)

    def test_tipo_sem_match_retorna_vazio(self, ue_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre, "TIPONEXISTENTE")
        assert resultado == []

    def test_ue_sem_tipo_escola(self, dre_factory, db):
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.dre.selectors import listar_escolas_por_dre
        dre = dre_factory()
        UnidadeEducacional.objects.create(
            codigo_ue="000002",
            nome="UE SEM TIPO",
            codigo_dre=dre.codigo_dre,
            codigo_tipo_escola=None,
            codigo_sub_prefeitura=None,
            organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        resultado = listar_escolas_por_dre(dre.codigo_dre)
        assert len(resultado) == 1
        assert resultado[0]["tipoEscola"] == ""
        assert resultado[0]["codigoSubprefeitura"] == ""


class TestListarUnidadesPorDre:
    def test_dre_nao_existente_retorna_vazio(self, db):
        from apps.dre.selectors import listar_unidades_por_dre
        assert listar_unidades_por_dre("000000") == []

    def test_cep_invalido_vira_none(self, dre_factory, db):
        from apps.unidade_educacional.models import UnidadeEducacional
        from apps.dre.selectors import listar_unidades_por_dre
        dre = dre_factory()
        UnidadeEducacional.objects.create(
            codigo_ue="000003",
            nome="UE CEP INVALIDO",
            codigo_dre=dre.codigo_dre,
            cep="nao-e-numero",
            organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        resultado = listar_unidades_por_dre(dre.codigo_dre)
        assert resultado[0]["cep"] is None


class TestListarEscolasPorDreCamposExpandidos:
    def test_contem_tipo_escola_id(self, ue_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        assert len(resultado) == 1
        assert "tipoEscolaId" in resultado[0]
        assert "subprefeituraId" in resultado[0]
        assert "codigoIntegracao" in resultado[0]

    def test_tipo_escola_id_preenchido(self, ue_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        item = resultado[0]
        assert item["tipoEscolaId"] == ue.codigo_tipo_escola

    def test_subprefeitura_id_preenchido(self, ue_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        item = resultado[0]
        assert item["subprefeituraId"] == ue.codigo_sub_prefeitura

    def test_campos_legados_intactos(self, ue_factory):
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        item = resultado[0]
        for campo in [
            "codigoEscola", "nomeEscola", "codigoDRE",
            "tipoEscola", "siglaTipoEscola", "nomeDRE",
            "siglaDRE", "codigoSubprefeitura", "nomeSubprefeitura",
        ]:
            assert campo in item, f"Campo legado '{campo}' removido"


class TestListarUnidadesPorDreCamposExpandidos:
    def test_contem_subprefeitura_id(self, ue_factory):
        from apps.dre.selectors import listar_unidades_por_dre
        ue = ue_factory()
        resultado = listar_unidades_por_dre(ue.codigo_dre)
        assert len(resultado) == 1
        assert "subprefeituraId" in resultado[0]
        assert "tipoUnidadeAdmId" in resultado[0]

    def test_subprefeitura_id_preenchido(self, ue_factory):
        from apps.dre.selectors import listar_unidades_por_dre
        ue = ue_factory()
        resultado = listar_unidades_por_dre(ue.codigo_dre)
        assert resultado[0]["subprefeituraId"] == ue.codigo_sub_prefeitura

    def test_campos_legados_intactos(self, ue_factory):
        from apps.dre.selectors import listar_unidades_por_dre
        ue = ue_factory()
        resultado = listar_unidades_por_dre(ue.codigo_dre)
        item = resultado[0]
        for campo in [
            "codigoEol", "nomeOficial", "subPrefeitura",
            "nomeDre", "capacidadeVagasTotal",
        ]:
            assert campo in item, f"Campo legado '{campo}' removido"


class TestListarCodigosIntegracao:
    def test_dre_sem_ues_retorna_vazio(self, db):
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        assert listar_codigos_integracao_por_dre("000000") == []

    def test_retorna_contrato_correto(self, ue_factory):
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        ue = ue_factory(codigo_ue_integracao="INT001")
        resultado = listar_codigos_integracao_por_dre(ue.codigo_dre)
        assert resultado[0]["codigoIntegracao"] == "INT001"

    def test_contem_campos_ids_institucionais(self, ue_factory):
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        ue = ue_factory()
        resultado = listar_codigos_integracao_por_dre(ue.codigo_dre)
        assert len(resultado) == 1
        assert "tipoEscolaId" in resultado[0]
        assert "subprefeituraId" in resultado[0]

    def test_tipo_escola_id_preenchido(self, ue_factory):
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        ue = ue_factory()
        resultado = listar_codigos_integracao_por_dre(ue.codigo_dre)
        assert resultado[0]["tipoEscolaId"] == ue.codigo_tipo_escola
