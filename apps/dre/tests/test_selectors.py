"""Testes unitários dos selectors DRE — cobertura de branches."""

import pytest

pytestmark = pytest.mark.django_db


class TestListarDres:
    """Cobre listar_dres(): lista completa e tratamento de sigla nula."""

    def test_retorna_lista_vazia_sem_dres(self, db):
        """Sem DREs cadastradas retorna lista vazia."""
        from apps.dre.selectors import listar_dres
        assert listar_dres() == []

    def test_retorna_lista_com_dres(self, dre_factory):
        """DRE cadastrada aparece na lista com código correto."""
        from apps.dre.selectors import listar_dres
        dre_factory(codigo_dre="108100", nome="DRE A", sigla="A")
        resultado = listar_dres()
        assert len(resultado) == 1
        assert resultado[0]["codigoDRE"] == "108100"

    def test_sigla_none_vira_string_vazia(self, dre_factory):
        """Sigla None é normalizada para string vazia no contrato."""
        from apps.dre.selectors import listar_dres
        dre_factory(codigo_dre="108100", nome="DRE SEM SIGLA", sigla=None)
        resultado = listar_dres()
        assert resultado[0]["siglaDRE"] == ""


class TestFiltrarDresPorCodigos:
    """Cobre filtrar_dres_por_codigos(): filtragem por lista de códigos."""

    def test_codigos_nao_encontrados(self, db):
        """Códigos inexistentes retornam lista vazia."""
        from apps.dre.selectors import filtrar_dres_por_codigos
        assert filtrar_dres_por_codigos(["999999"]) == []

    def test_filtra_apenas_os_solicitados(self, dre_factory):
        """Retorna apenas as DREs cujos códigos foram solicitados."""
        from apps.dre.selectors import filtrar_dres_por_codigos
        dre_factory(codigo_dre="108100", nome="A", sigla="A")
        dre_factory(codigo_dre="108200", nome="B", sigla="B")
        resultado = filtrar_dres_por_codigos(["108100"])
        assert len(resultado) == 1
        assert resultado[0]["codigoDRE"] == "108100"


class TestObterDrePorCodigo:
    """Cobre obter_dre_por_codigo(): retorno de DRE existente e ausente."""

    def test_retorna_none_se_nao_existir(self, db):
        """Código inexistente retorna None."""
        from apps.dre.selectors import obter_dre_por_codigo
        assert obter_dre_por_codigo("000000") is None

    def test_retorna_dre_existente(self, dre_factory):
        """DRE existente retorna contrato com nome correto."""
        from apps.dre.selectors import obter_dre_por_codigo
        dre_factory(codigo_dre="108100", nome="DRE X", sigla="X")
        resultado = obter_dre_por_codigo("108100")
        assert resultado is not None
        assert resultado["nomeDRE"] == "DRE X"


class TestListarSubprefeiturasPorDre:
    """Cobre listar_subprefeituras_por_dre(): exclui UEs sem subprefeitura."""

    def test_dre_sem_ues_retorna_vazio(self, db):
        """DRE sem UEs vinculadas retorna lista vazia."""
        from apps.dre.selectors import listar_subprefeituras_por_dre
        assert listar_subprefeituras_por_dre("000000") == []

    def test_ue_sem_subprefeitura_excluida(self, dre_factory, db):
        """UE com subprefeitura None não aparece no resultado."""
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
    """Cobre listar_escolas_por_dre(): filtro por tipo, UE sem tipo/sub."""

    def test_dre_nao_existente_retorna_vazio(self, db):
        """DRE inexistente retorna lista vazia."""
        from apps.dre.selectors import listar_escolas_por_dre
        assert listar_escolas_por_dre("999999") == []

    def test_dre_sem_ues_retorna_vazio(self, dre_factory):
        """DRE sem UEs retorna lista vazia."""
        from apps.dre.selectors import listar_escolas_por_dre
        dre = dre_factory()
        assert listar_escolas_por_dre(dre.codigo_dre) == []

    def test_com_filtro_de_tipo(self, ue_factory):
        """Filtro por tipo retorna apenas UEs do tipo informado."""
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(
            ue.codigo_dre, ue.codigo_tipo_escola
        )
        assert isinstance(resultado, list)
        assert len(resultado) >= 1

    def test_tipo_sem_match_retorna_vazio(self, ue_factory):
        """Tipo sem UEs correspondentes retorna lista vazia."""
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre, 999999)
        assert resultado == []

    def test_ue_sem_tipo_escola(self, dre_factory, db):
        """UE sem tipo de escola tem tipoEscola e codigoSubprefeitura vazios."""
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
    """Cobre listar_unidades_por_dre(): CEP inválido e DRE inexistente."""

    def test_dre_nao_existente_retorna_vazio(self, db):
        """DRE inexistente retorna lista vazia."""
        from apps.dre.selectors import listar_unidades_por_dre
        assert listar_unidades_por_dre("000000") == []

    def test_cep_invalido_vira_none(self, dre_factory, db):
        """CEP não numérico é normalizado para None no contrato."""
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
    """Cobre campos institucionais expandidos em listar_escolas_por_dre()."""

    def test_contem_tipo_escola_id(self, ue_factory):
        """Resultado inclui tipoEscolaId, subprefeituraId e codigoIntegracao."""
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        assert len(resultado) == 1
        assert "tipoEscolaId" in resultado[0]
        assert "subprefeituraId" in resultado[0]
        assert "codigoIntegracao" in resultado[0]

    def test_tipo_escola_id_preenchido(self, ue_factory):
        """Retorna tipoEscolaId igual ao código de tipo da UE."""
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        item = resultado[0]
        assert item["tipoEscolaId"] == ue.codigo_tipo_escola

    def test_subprefeitura_id_preenchido(self, ue_factory):
        """Retorna subprefeituraId igual ao código de subprefeitura da UE."""
        from apps.dre.selectors import listar_escolas_por_dre
        ue = ue_factory()
        resultado = listar_escolas_por_dre(ue.codigo_dre)
        item = resultado[0]
        assert item["subprefeituraId"] == ue.codigo_sub_prefeitura

    def test_campos_legados_intactos(self, ue_factory):
        """Campos legados do contrato não foram removidos."""
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
    """Cobre campos institucionais expandidos em listar_unidades_por_dre()."""

    def test_contem_subprefeitura_id(self, ue_factory):
        """Resultado inclui subprefeituraId e tipoUnidadeAdmId."""
        from apps.dre.selectors import listar_unidades_por_dre
        ue = ue_factory()
        resultado = listar_unidades_por_dre(ue.codigo_dre)
        assert len(resultado) == 1
        assert "subprefeituraId" in resultado[0]
        assert "tipoUnidadeAdmId" in resultado[0]

    def test_subprefeitura_id_preenchido(self, ue_factory):
        """Retorna subprefeituraId igual ao código de subprefeitura da UE."""
        from apps.dre.selectors import listar_unidades_por_dre
        ue = ue_factory()
        resultado = listar_unidades_por_dre(ue.codigo_dre)
        assert resultado[0]["subprefeituraId"] == ue.codigo_sub_prefeitura

    def test_campos_legados_intactos(self, ue_factory):
        """Campos legados do contrato não foram removidos."""
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
    """Cobre listar_codigos_integracao_por_dre(): contrato e campos de IDs."""

    def test_dre_sem_ues_retorna_vazio(self, db):
        """DRE sem UEs retorna lista vazia."""
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        assert listar_codigos_integracao_por_dre("000000") == []

    def test_retorna_contrato_correto(self, ue_factory):
        """Retorna codigoIntegracao igual ao valor cadastrado na UE."""
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        ue = ue_factory(codigo_ue_integracao="INT001")
        resultado = listar_codigos_integracao_por_dre(ue.codigo_dre)
        assert resultado[0]["codigoIntegracao"] == "INT001"

    def test_contem_campos_ids_institucionais(self, ue_factory):
        """Resultado inclui tipoEscolaId e subprefeituraId."""
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        ue = ue_factory()
        resultado = listar_codigos_integracao_por_dre(ue.codigo_dre)
        assert len(resultado) == 1
        assert "tipoEscolaId" in resultado[0]
        assert "subprefeituraId" in resultado[0]

    def test_tipo_escola_id_preenchido(self, ue_factory):
        """Retorna tipoEscolaId igual ao código de tipo da UE."""
        from apps.dre.selectors import listar_codigos_integracao_por_dre
        ue = ue_factory()
        resultado = listar_codigos_integracao_por_dre(ue.codigo_dre)
        assert resultado[0]["tipoEscolaId"] == ue.codigo_tipo_escola
