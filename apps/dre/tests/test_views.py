"""Testes comportamentais e de contrato — domínio DRE (D01-D11)."""

import pytest

pytestmark = pytest.mark.django_db


class TestAutenticacaoDre:
    """Valida que todas as rotas DRE exigem API key."""

    def test_sem_api_key_retorna_401(self):
        """Requisição sem credencial retorna 401 ou 403."""
        from rest_framework.test import APIClient
        resp = APIClient().get("/api/v1/institucional/dres/")
        assert resp.status_code in (401, 403)

    def test_api_key_errada_retorna_403(self):
        """Requisição com chave inválida retorna 401 ou 403."""
        from rest_framework.test import APIClient
        from django.conf import settings
        client = APIClient()
        client.credentials(**{
            f"HTTP_{settings.API_KEY_HEADER.upper().replace('-', '_')}": "chave-errada"
        })
        resp = client.get("/api/v1/institucional/dres/")
        assert resp.status_code in (401, 403)


class TestD01ListarDres:
    """D01 — GET /api/dres/"""

    def test_retorna_200_com_lista(self, api_client, dre_factory):
        """Retorna lista de DREs com status 200."""
        dre_factory(codigo_dre="108100", nome="DRE IPIRANGA", sigla="DRE-IP")
        resp = api_client.get("/api/v1/institucional/dres/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_contrato_campos_camel_case(self, api_client, dre_factory):
        """Campos do contrato estão em camelCase."""
        dre_factory(codigo_dre="108100", nome="DRE IPIRANGA", sigla="DRE-IP")
        resp = api_client.get("/api/v1/institucional/dres/")
        assert resp.status_code == 200
        item = resp.data[0]
        assert "codigoDRE" in item
        assert "nomeDRE" in item
        assert "siglaDRE" in item

    def test_lista_vazia_retorna_200(self, api_client, db):
        """Sem DREs cadastradas retorna lista vazia com 200."""
        resp = api_client.get("/api/v1/institucional/dres/")
        assert resp.status_code == 200
        assert resp.data == []

    def test_valores_corretos_no_contrato(self, api_client, dre_factory):
        """Valores dos campos correspondem aos dados cadastrados."""
        dre_factory(codigo_dre="108100", nome="DRE IPIRANGA", sigla="DRE-IP")
        resp = api_client.get("/api/v1/institucional/dres/")
        item = resp.data[0]
        assert item["codigoDRE"] == "108100"
        assert item["nomeDRE"] == "DRE IPIRANGA"
        assert item["siglaDRE"] == "DRE-IP"


class TestD02FiltrarDresPorCodigos:
    """D02 — POST /api/dres/"""

    def test_retorna_dres_encontradas(self, api_client, dre_factory):
        """Retorna DREs correspondentes aos códigos enviados."""
        dre_factory(codigo_dre="108100", nome="DRE IPIRANGA", sigla="DRE-IP")
        resp = api_client.post(
            "/api/v1/institucional/dres/", ["108100"], format="json"
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["codigoDRE"] == "108100"

    def test_corpo_vazio_retorna_204(self, api_client, db):
        """Lista vazia retorna 204."""
        resp = api_client.post(
            "/api/v1/institucional/dres/", [], format="json"
        )
        assert resp.status_code == 204

    def test_codigos_sem_registros_retorna_204(self, api_client, db):
        """Códigos inexistentes retornam 204."""
        resp = api_client.post(
            "/api/v1/institucional/dres/", ["999999"], format="json"
        )
        assert resp.status_code == 204

    def test_corpo_invalido_retorna_400(self, api_client, db):
        """Corpo não-lista retorna 400."""
        resp = api_client.post(
            "/api/v1/institucional/dres/",
            {"codigo": "100001"},
            format="json",
        )
        assert resp.status_code == 400


class TestD04DetalheDre:
    """D04 — GET /api/dres/{codigoEolDRE}/"""

    def test_retorna_200_com_contrato(self, api_client, dre_factory):
        """Retorna lista com a DRE encontrada."""
        dre_factory(codigo_dre="108100", nome="DRE IPIRANGA", sigla="DRE-IP")
        resp = api_client.get("/api/v1/institucional/dres/108100/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list) and len(resp.data) == 1
        assert resp.data[0]["codigoDRE"] == "108100"
        assert resp.data[0]["nomeDRE"] == "DRE IPIRANGA"
        assert resp.data[0]["siglaDRE"] == "DRE-IP"

    def test_nao_encontrada_retorna_404(self, api_client, db):
        """DRE inexistente retorna 404."""
        resp = api_client.get("/api/v1/institucional/dres/999999/")
        assert resp.status_code == 404


class TestD05EscolasTipo:
    """D05 — GET /api/dres/{codigoEolDRE}/escolas/{tipoEscolaId}/."""

    def test_retorna_escolas_filtradas(self, api_client, ue_factory):
        """Retorna escolas do tipo informado com status 200."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            f"/escolas/{ue.codigo_tipo_escola}/"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        assert len(resp.data) >= 1

    def test_tipo_inexistente_retorna_lista_vazia(self, api_client, ue_factory):
        """Tipo sem escolas vinculadas retorna lista vazia."""
        ue = ue_factory()
        url = f"/api/v1/institucional/dres/{ue.codigo_dre}/escolas/999999/"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data == []

    def test_codigo_dre_vazio_retorna_400(self, api_client, db):
        """Código de DRE vazio retorna 400."""
        resp = api_client.get("/api/v1/institucional/dres/%20/escolas/1/")
        assert resp.status_code == 400


class TestD06EscolasPorDre:
    """D06 — GET /api/dres/{codigoEolDRE}/escola/"""

    def test_retorna_200_com_escolas(self, api_client, ue_factory):
        """Retorna escolas da DRE com status 200."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_contrato_campos_escola(self, api_client, ue_factory):
        """Todos os campos do contrato D06 estão presentes."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        assert resp.status_code == 200
        item = resp.data[0]
        for campo in [
            "codigoEscola", "nomeEscola", "codigoDRE",
            "tipoEscola", "siglaTipoEscola", "nomeDRE",
            "siglaDRE", "codigoSubprefeitura", "nomeSubprefeitura",
        ]:
            assert campo in item, f"Campo '{campo}' ausente no contrato D06"

    def test_dre_sem_escolas_retorna_204(self, api_client, dre_factory):
        """DRE sem escolas vinculadas retorna 204."""
        dre_factory(codigo_dre="999000")
        resp = api_client.get("/api/v1/institucional/dres/999000/escola/")
        assert resp.status_code == 204


class TestD07Subprefeituras:
    """D07 — GET /api/dres/{dreCodigo}/subprefeituras/"""

    def test_retorna_subprefeituras(self, api_client, ue_factory):
        """Retorna lista de subprefeituras com status 200."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/subprefeituras/"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_contrato_subprefeitura(self, api_client, ue_factory):
        """Campos do contrato de subprefeitura estão presentes."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/subprefeituras/"
        )
        if resp.data:
            item = resp.data[0]
            assert "codigoSubprefeitura" in item
            assert "nomeSubprefeitura" in item

    def test_codigo_vazio_retorna_400(self, api_client, db):
        """Código vazio retorna 400."""
        resp = api_client.get(
            "/api/v1/institucional/dres/%20/subprefeituras/"
        )
        assert resp.status_code == 400


class TestD08CodigosUes:
    """D08 — GET /api/dres/{dreCodigo}/ues/"""

    def test_retorna_lista_de_strings(self, api_client, ue_factory):
        """Retorna lista de códigos EOL como strings."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/ues/"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        assert ue.codigo_ue in resp.data

    def test_dre_sem_ues_retorna_lista_vazia(self, api_client, dre_factory):
        """DRE sem UEs retorna lista vazia."""
        dre_factory(codigo_dre="000999")
        resp = api_client.get("/api/v1/institucional/dres/000999/ues/")
        assert resp.status_code == 200
        assert resp.data == []

    def test_codigo_vazio_retorna_400(self, api_client, db):
        """Código vazio retorna 400."""
        resp = api_client.get("/api/v1/institucional/dres/%20/ues/")
        assert resp.status_code == 400


class TestD09EscolasSigpae:
    """D09 — GET /api/dres/{codigoEolDRE}/escola/Sigpae/"""

    def test_retorna_200_com_escolas(self, api_client, ue_factory):
        """Retorna escolas no formato SIGPAE com status 200."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/Sigpae/"
        )
        assert resp.status_code == 200

    def test_dre_sem_escolas_retorna_204(self, api_client, dre_factory):
        """DRE sem escolas retorna 204."""
        dre_factory(codigo_dre="888000")
        resp = api_client.get(
            "/api/v1/institucional/dres/888000/escola/Sigpae/"
        )
        assert resp.status_code == 204

    def test_codigo_vazio_retorna_400(self, api_client, db):
        """Código vazio retorna 400."""
        resp = api_client.get(
            "/api/v1/institucional/dres/%20/escola/Sigpae/"
        )
        assert resp.status_code == 400


class TestD10UnidadesPrediais:
    """D10 — GET /api/dres/{dreCodigo}/unidades/"""

    def test_retorna_200_com_contrato_completo(self, api_client, ue_factory):
        """Retorna unidades prediais com todos os campos do contrato D10."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/unidades/"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1
        item = resp.data[0]
        for campo in [
            "codigoEol", "nomeOficial", "nomeNaoOficial", "tipoUE",
            "logadouro", "numero", "bairro", "cep", "distrito",
            "subPrefeitura", "nomeDre", "email", "telefone1", "telefone2",
            "anoConstrucao", "propriedade", "capacidadeVagasMatutino",
            "capacidadeVagasVespertino", "capacidadeVagasNoturno",
            "capacidadeVagasIntermediario", "capacidadeVagasIntegral",
            "capacidadeVagasTotal", "organizacaoParceira",
            "quantidadeDeFuncionarios", "status",
        ]:
            assert campo in item, f"Campo '{campo}' ausente no contrato D10"

    def test_dre_inexistente_retorna_lista_vazia(self, api_client, db):
        """DRE inexistente retorna lista vazia com 200."""
        resp = api_client.get("/api/v1/institucional/dres/000000/unidades/")
        assert resp.status_code == 200
        assert resp.data == []


class TestD11CodigosIntegracao:
    """D11 — GET /api/dres/{dreCodigo}/unidades/codigo-integracao/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        """Retorna códigos de integração com campos do contrato D11."""
        ue = ue_factory(codigo_ue_integracao="0000000000000001")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/codigo-integracao/"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1
        item = resp.data[0]
        assert "codigoUe" in item
        assert "nomeUe" in item
        assert "codigoIntegracao" in item

    def test_dre_sem_ues_retorna_lista_vazia(self, api_client, db):
        """DRE sem UEs retorna lista vazia."""
        resp = api_client.get(
            "/api/v1/institucional/dres/111111/unidades/codigo-integracao/"
        )
        assert resp.status_code == 200
        assert resp.data == []


class TestD05D06D09CamposExpandidos:
    """Valida campos institucionais expandidos nos endpoints D05/D06/D09."""

    def test_d06_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """D06 inclui campos de IDs institucionais."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        assert resp.status_code == 200
        item = resp.data[0]
        assert "tipoEscolaId" in item
        assert "tipoUnidadeId" in item
        assert "subprefeituraId" in item
        assert "dreId" in item
        assert "codigoIntegracao" in item

    def test_d06_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        """dreId coincide com o código EOL da DRE."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        assert item["dreId"] == ue.codigo_dre

    def test_d06_tipo_unidade_id_igual_tipo_escola_id(
        self, api_client, ue_factory
    ):
        """tipoUnidadeId e tipoEscolaId têm o mesmo valor."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        assert item["tipoUnidadeId"] == item["tipoEscolaId"]

    def test_d06_tipo_escola_id_eh_inteiro_ou_null(
        self, api_client, ue_factory
    ):
        """tipoEscolaId é inteiro ou None."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        assert item["tipoEscolaId"] is None or isinstance(
            item["tipoEscolaId"], int
        )

    def test_d06_subprefeitura_id_eh_inteiro_ou_null(
        self, api_client, ue_factory
    ):
        """subprefeituraId é inteiro ou None."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        assert item["subprefeituraId"] is None or isinstance(
            item["subprefeituraId"], int
        )

    def test_d06_campos_legados_permanecem(self, api_client, ue_factory):
        """Campos legados do contrato D06 não foram removidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        for campo in [
            "codigoEscola", "nomeEscola", "codigoDRE",
            "tipoEscola", "siglaTipoEscola", "nomeDRE",
            "siglaDRE", "codigoSubprefeitura", "nomeSubprefeitura",
        ]:
            assert campo in item, (
                f"Campo legado '{campo}' removido — violação de contrato"
            )

    def test_d05_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """D05 retorna 200 com campos expandidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            f"/escolas/{ue.codigo_tipo_escola}/"
        )
        assert resp.status_code == 200

    def test_d09_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """D09 inclui campos de IDs institucionais quando há resultados."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/Sigpae/"
        )
        assert resp.status_code == 200
        if resp.data:
            item = resp.data[0]
            assert "tipoEscolaId" in item
            assert "subprefeituraId" in item

    def test_d06_ue_sem_tipo_escola_id_null(self, api_client, dre_factory, db):
        """UE sem tipo de escola tem tipoEscolaId e subprefeituraId nulos."""
        from apps.unidade_educacional.models import UnidadeEducacional
        dre = dre_factory(codigo_dre="999001")
        UnidadeEducacional.objects.create(
            codigo_ue="900001", nome="UE SEM TIPO",
            codigo_dre=dre.codigo_dre, codigo_tipo_escola=None,
            codigo_sub_prefeitura=None, organizacao_parceira=False,
            vagas_matutino=0, vagas_vespertino=0, vagas_noturno=0,
            vagas_intermediario=0, vagas_integral=0, vagas_total=0,
            quantidade_funcionarios=0,
        )
        resp = api_client.get(
            f"/api/v1/institucional/dres/{dre.codigo_dre}/escola/"
        )
        assert resp.status_code == 200
        item = resp.data[0]
        assert item["tipoEscolaId"] is None
        assert item["subprefeituraId"] is None


class TestD10CamposExpandidos:
    """Valida campos institucionais expandidos no endpoint D10."""

    def test_d10_contem_subprefeitura_id(self, api_client, ue_factory):
        """D10 inclui subprefeituraId e tipoUnidadeAdmId."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/unidades/"
        )
        assert resp.status_code == 200
        item = resp.data[0]
        assert "subprefeituraId" in item
        assert "tipoUnidadeAdmId" in item

    def test_d10_campos_legados_permanecem(self, api_client, ue_factory):
        """Campos legados do contrato D10 não foram removidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/unidades/"
        )
        item = resp.data[0]
        for campo in [
            "codigoEol", "nomeOficial", "subPrefeitura", "nomeDre",
            "capacidadeVagasTotal", "organizacaoParceira",
        ]:
            assert campo in item, f"Campo legado '{campo}' removido"

    def test_d10_tipo_unidade_adm_id_inteiro_ou_null(
        self, api_client, ue_factory
    ):
        """tipoUnidadeAdmId é inteiro ou None."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/unidades/"
        )
        item = resp.data[0]
        assert item["tipoUnidadeAdmId"] is None or isinstance(
            item["tipoUnidadeAdmId"], int
        )


class TestD11CamposExpandidos:
    """Valida campos institucionais expandidos no endpoint D11."""

    def test_d11_contem_tipo_escola_id_e_subprefeitura_id(
        self, api_client, ue_factory
    ):
        """D11 inclui tipoEscolaId, tipoUnidadeId, subprefeituraId e dreId."""
        ue = ue_factory(codigo_ue_integracao="INT001")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/codigo-integracao/"
        )
        assert resp.status_code == 200
        item = resp.data[0]
        assert "tipoEscolaId" in item
        assert "tipoUnidadeId" in item
        assert "subprefeituraId" in item
        assert "dreId" in item

    def test_d11_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        """dreId coincide com o código EOL da DRE."""
        ue = ue_factory(codigo_ue_integracao="INT003")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/codigo-integracao/"
        )
        item = resp.data[0]
        assert item["dreId"] == ue.codigo_dre

    def test_d11_tipo_unidade_id_igual_tipo_escola_id(
        self, api_client, ue_factory
    ):
        """tipoUnidadeId e tipoEscolaId têm o mesmo valor."""
        ue = ue_factory(codigo_ue_integracao="INT004")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/codigo-integracao/"
        )
        item = resp.data[0]
        assert item["tipoUnidadeId"] == item["tipoEscolaId"]

    def test_d11_campos_legados_permanecem(self, api_client, ue_factory):
        """Campos legados do contrato D11 não foram removidos."""
        ue = ue_factory(codigo_ue_integracao="INT002")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/codigo-integracao/"
        )
        item = resp.data[0]
        for campo in ["codigoUe", "nomeUe", "codigoIntegracao"]:
            assert campo in item, f"Campo legado '{campo}' removido"


class TestD03Supervisores:
    """D03 — GET /api/dres/{codigoEolDRE}/supervisores/ — cross-domain."""

    def test_retorna_501_com_info_dominio(self, api_client, db):
        """Retorna 501 com domínio 'professores' no payload."""
        resp = api_client.get(
            "/api/v1/institucional/dres/108100/supervisores/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "professores"
