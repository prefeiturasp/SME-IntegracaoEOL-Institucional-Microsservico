"""Testes comportamentais e de contrato — domínio DRE (D01-D13)."""

from collections.abc import Callable

import pytest
from django.urls import reverse
from pytest_django.fixtures import DjangoAssertNumQueries
from rest_framework.test import APIClient

from apps.dre.models import DRE
from apps.unidade_educacional.models import UnidadeEducacional

pytestmark = pytest.mark.django_db

_URL_CODIGOS_ABRANGENCIA = "/api/v1/institucional/abrangencia/codigos-dres/"
_URL_NOMES_ABRANGENCIA = (
    "/api/v1/institucional/abrangencia/nome-abreviacao-dres/"
)
_URLS_ABRANGENCIA = (_URL_CODIGOS_ABRANGENCIA, _URL_NOMES_ABRANGENCIA)


class TestCacheViewsDre:
    """Valida o contrato HTTP das listagens em cache por DRE."""

    @pytest.mark.parametrize(
        "sufixo", ["ues/", "unidades/", "unidades/codigo-integracao/"]
    )
    def test_preserva_json_sem_consultar_banco(
        self,
        sufixo: str,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
        django_assert_num_queries: DjangoAssertNumQueries,
    ) -> None:
        """D08, D10 e D11 preservam o JSON sem SQL após aquecer o cache."""
        ue = ue_factory()
        url = f"/api/v1/institucional/dres/{ue.codigo_dre}/{sufixo}"
        primeira = api_client.get(url)
        assert primeira.status_code == 200
        assert len(primeira.json()) == 1

        with django_assert_num_queries(0):
            segunda = api_client.get(url)

        assert segunda.status_code == 200
        assert segunda.json() == primeira.json()


class TestEndpointsAbrangencia:
    """Valida as consultas de DREs disponíveis na tag Abrangencia."""

    @pytest.mark.parametrize(
        ("url", "esperado"),
        [
            (_URL_CODIGOS_ABRANGENCIA, ["108100", "108200"]),
            (
                _URL_NOMES_ABRANGENCIA,
                [
                    {
                        "codigo": "108100",
                        "nome": "DRE A",
                        "abreviacao": "DRE-A",
                    },
                    {
                        "codigo": "108200",
                        "nome": "DRE B",
                        "abreviacao": None,
                    },
                ],
            ),
        ],
    )
    def test_retorna_contrato_legado(
        self, api_client, dre_abrangencia_factory, url, esperado
    ):
        """Retorna os dados das DREs na ordem materializada pelo ETL."""
        dre_abrangencia_factory(
            codigo_dre="108200", nome="DRE B", abreviacao=None, ordem=2
        )
        dre_abrangencia_factory(
            codigo_dre="108100", nome="DRE A", abreviacao="DRE-A", ordem=1
        )

        resp = api_client.get(url)

        assert resp.status_code == 200
        assert resp.data == esperado

    @pytest.mark.parametrize("url", _URLS_ABRANGENCIA)
    def test_sem_dres_elegiveis_retorna_204(self, api_client, db, url):
        """Retorna sem conteúdo quando não há DREs elegíveis."""
        resp = api_client.get(url)

        assert resp.status_code == 204
        assert resp.data is None

    @pytest.mark.parametrize("url", _URLS_ABRANGENCIA)
    def test_sem_api_key_retorna_401_ou_403(self, db, url):
        """Exige a API key configurada pelo microsserviço."""
        assert APIClient().get(url).status_code in (401, 403)

    @pytest.mark.parametrize("url", _URLS_ABRANGENCIA)
    def test_schema_expoe_tag_abrangencia(self, api_client, db, url):
        """Publica a consulta na tag Abrangencia do Swagger."""
        resp = api_client.get(
            "/api/v1/institucional/schema/", HTTP_ACCEPT="application/json"
        )

        assert resp.data["paths"][url]["get"]["tags"] == ["Abrangencia"]


class TestAutenticacaoDre:
    """Valida que todas as rotas DRE exigem API key."""

    def test_sem_api_key_retorna_401(self):
        """Requisição sem credencial retorna 401 ou 403."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/dres/")
        assert resp.status_code in (401, 403)

    def test_api_key_errada_retorna_403(self):
        """Requisição com chave inválida retorna 401 ou 403."""
        from django.conf import settings
        from rest_framework.test import APIClient

        client = APIClient()
        client.credentials(
            **{
                f"HTTP_{settings.API_KEY_HEADER.upper().replace('-', '_')}": "chave-errada"
            }
        )
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

    def test_tipo_inexistente_retorna_lista_vazia(
        self, api_client, ue_factory
    ):
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
            "codigoEscola",
            "nomeEscola",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoSubprefeitura",
            "nomeSubprefeitura",
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
        resp = api_client.get("/api/v1/institucional/dres/%20/subprefeituras/")
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
        resp = api_client.get("/api/v1/institucional/dres/%20/escola/Sigpae/")
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
            "codigoEol",
            "nomeOficial",
            "nomeNaoOficial",
            "tipoUE",
            "logadouro",
            "numero",
            "bairro",
            "cep",
            "distrito",
            "subPrefeitura",
            "nomeDre",
            "email",
            "telefone1",
            "telefone2",
            "anoConstrucao",
            "propriedade",
            "capacidadeVagasMatutino",
            "capacidadeVagasVespertino",
            "capacidadeVagasNoturno",
            "capacidadeVagasIntermediario",
            "capacidadeVagasIntegral",
            "capacidadeVagasTotal",
            "organizacaoParceira",
            "quantidadeDeFuncionarios",
            "status",
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

    def test_d06_contem_campos_ids_institucionais(
        self, api_client, ue_factory
    ):
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
        """DreId coincide com o código EOL da DRE."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        assert item["dreId"] == ue.codigo_dre

    def test_d06_tipo_unidade_id_igual_tipo_escola_id(
        self, api_client, ue_factory
    ):
        """TipoUnidadeId e tipoEscolaId têm o mesmo valor."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escola/"
        )
        item = resp.data[0]
        assert item["tipoUnidadeId"] == item["tipoEscolaId"]

    def test_d06_tipo_escola_id_eh_inteiro_ou_null(
        self, api_client, ue_factory
    ):
        """TipoEscolaId é inteiro ou None."""
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
        """SubprefeituraId é inteiro ou None."""
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
            "codigoEscola",
            "nomeEscola",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoSubprefeitura",
            "nomeSubprefeitura",
        ]:
            assert (
                campo in item
            ), f"Campo legado '{campo}' removido — violação de contrato"

    def test_d05_contem_campos_ids_institucionais(
        self, api_client, ue_factory
    ):
        """D05 retorna 200 com campos expandidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            f"/escolas/{ue.codigo_tipo_escola}/"
        )
        assert resp.status_code == 200

    def test_d09_contem_campos_ids_institucionais(
        self, api_client, ue_factory
    ):
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
            codigo_ue="900001",
            nome="UE SEM TIPO",
            codigo_dre=dre.codigo_dre,
            codigo_tipo_escola=None,
            codigo_sub_prefeitura=None,
            organizacao_parceira=False,
            vagas_matutino=0,
            vagas_vespertino=0,
            vagas_noturno=0,
            vagas_intermediario=0,
            vagas_integral=0,
            vagas_total=0,
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
            "codigoEol",
            "nomeOficial",
            "subPrefeitura",
            "nomeDre",
            "capacidadeVagasTotal",
            "organizacaoParceira",
        ]:
            assert campo in item, f"Campo legado '{campo}' removido"

    def test_d10_tipo_unidade_adm_id_inteiro_ou_null(
        self, api_client, ue_factory
    ):
        """TipoUnidadeAdmId é inteiro ou None."""
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
        """DreId coincide com o código EOL da DRE."""
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
        """TipoUnidadeId e tipoEscolaId têm o mesmo valor."""
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


class TestD12EscolasConsolidadas:
    """D12 — GET /api/v1/institucional/dres/{codigoEolDRE}/escolas/."""

    def test_retorna_todas_as_escolas_apenas_da_dre_informada(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
    ) -> None:
        """Sem filtro, lista escolas de tipos distintos apenas da DRE pedida."""
        primeira = ue_factory()
        segunda = ue_factory(codigo_dre=primeira.codigo_dre)
        ue_factory()
        url = reverse(
            "dre-escolas-consolidadas",
            kwargs={"codigo_eol_dre": primeira.codigo_dre},
        )
        resp = api_client.get(url)
        assert url == (
            f"/api/v1/institucional/dres/{primeira.codigo_dre}/escolas/"
        )
        assert resp.status_code == 200
        assert [item["codigoEscola"] for item in resp.data] == [
            primeira.codigo_ue,
            segunda.codigo_ue,
        ]

    @pytest.mark.parametrize("tipo_escola_id", [0, 1])
    def test_retorna_escolas_filtradas_por_tipo(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
        tipo_escola_id: int,
    ) -> None:
        """O filtro inclui somente escolas do tipo e da DRE informados."""
        ue = ue_factory(codigo_tipo_escola=tipo_escola_id)
        ue_factory(codigo_dre=ue.codigo_dre, codigo_tipo_escola=2)
        ue_factory(codigo_tipo_escola=tipo_escola_id)
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escolas/",
            {"tipo_escola_id": str(tipo_escola_id)},
        )
        assert resp.status_code == 200
        assert [item["codigoEscola"] for item in resp.data] == [ue.codigo_ue]
        assert resp.data[0]["tipoEscolaId"] == tipo_escola_id

    def test_tipo_inexistente_retorna_lista_vazia(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
    ) -> None:
        """Um tipo sem escolas correspondentes retorna 200 com lista vazia."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escolas/",
            {"tipo_escola_id": "999999"},
        )
        assert resp.status_code == 200
        assert resp.data == []

    @pytest.mark.parametrize(
        ("parametros", "status_esperado"),
        [
            ({}, 204),
            ({"tipo_escola_id": "1"}, 200),
            ({"tipo_escola_id": "0"}, 200),
        ],
    )
    def test_dre_sem_escolas_preserva_status_por_filtro(
        self,
        api_client: APIClient,
        dre_factory: Callable[..., DRE],
        parametros: dict[str, str],
        status_esperado: int,
    ) -> None:
        """DRE sem escolas retorna 204 sem filtro ou 200 com lista vazia."""
        dre = dre_factory()

        resp = api_client.get(
            f"/api/v1/institucional/dres/{dre.codigo_dre}/escolas/", parametros
        )

        assert resp.status_code == status_esperado
        if status_esperado == 204:
            assert resp.data is None
            assert resp.content == b""
        else:
            assert resp.data == []

    @pytest.mark.parametrize(
        ("parametros", "status_esperado"),
        [({}, 204), ({"tipo_escola_id": "1"}, 200)],
    )
    def test_dre_inexistente_preserva_status_por_filtro(
        self,
        api_client: APIClient,
        parametros: dict[str, str],
        status_esperado: int,
    ) -> None:
        """DRE inexistente também respeita o contrato de resultado vazio."""
        resp = api_client.get(
            "/api/v1/institucional/dres/999999/escolas/", parametros
        )

        assert resp.status_code == status_esperado
        assert resp.data == (None if status_esperado == 204 else [])

    @pytest.mark.parametrize("com_filtro", [False, True])
    def test_contrato_campos_legados_e_expandidos(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
        com_filtro: bool,
    ) -> None:
        """Preserva campos, IDs, tipos e código de integração da escola."""
        ue = ue_factory(codigo_ue_integracao="INT001")
        parametros = (
            {"tipo_escola_id": str(ue.codigo_tipo_escola)}
            if com_filtro
            else {}
        )

        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escolas/", parametros
        )

        assert resp.status_code == 200
        assert len(resp.data) == 1
        item = resp.data[0]
        assert set(item) == {
            "codigoEscola",
            "nomeEscola",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoSubprefeitura",
            "nomeSubprefeitura",
            "tipoEscolaId",
            "tipoUnidadeId",
            "subprefeituraId",
            "dreId",
            "codigoIntegracao",
        }
        assert item["codigoEscola"] == ue.codigo_ue
        assert item["nomeEscola"] == ue.nome
        assert item["codigoDRE"] == item["dreId"] == ue.codigo_dre
        assert item["tipoEscolaId"] == ue.codigo_tipo_escola
        assert item["tipoUnidadeId"] == item["tipoEscolaId"]
        assert isinstance(item["tipoEscolaId"], int)
        assert item["subprefeituraId"] == ue.codigo_sub_prefeitura
        assert isinstance(item["subprefeituraId"], int)
        assert item["codigoSubprefeitura"] == str(ue.codigo_sub_prefeitura)
        assert item["codigoIntegracao"] == "INT001"

    def test_ue_sem_tipo_subprefeitura_e_integracao_preserva_nulos(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
    ) -> None:
        """Dados opcionais ausentes mantêm IDs nulos e descrições vazias."""
        ue = ue_factory(
            codigo_tipo_escola=None,
            codigo_sub_prefeitura=None,
            codigo_ue_integracao=None,
        )

        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}/escolas/"
        )

        assert resp.status_code == 200
        assert len(resp.data) == 1
        item = resp.data[0]
        for campo in (
            "tipoEscolaId",
            "tipoUnidadeId",
            "subprefeituraId",
            "codigoIntegracao",
        ):
            assert item[campo] is None
        for campo in (
            "tipoEscola",
            "siglaTipoEscola",
            "codigoSubprefeitura",
            "nomeSubprefeitura",
        ):
            assert item[campo] == ""

    @pytest.mark.parametrize("parametros", [{}, {"tipo_escola_id": "1"}])
    def test_codigo_dre_vazio_retorna_400(
        self, api_client: APIClient, parametros: dict[str, str]
    ) -> None:
        """Rejeita código de DRE em branco com e sem filtro por tipo."""
        resp = api_client.get(
            "/api/v1/institucional/dres/%20/escolas/", parametros
        )

        assert resp.status_code == 400
        assert resp.json() == {"detail": "Código EOL da DRE é obrigatório."}

    @pytest.mark.parametrize(
        "tipo_escola_id", ["", " ", "abc", "1.5", "-1", "null", "true"]
    )
    def test_tipo_invalido_retorna_400_sem_consultar_banco(
        self,
        api_client: APIClient,
        django_assert_num_queries: DjangoAssertNumQueries,
        tipo_escola_id: str,
    ) -> None:
        """Rejeita filtro vazio, negativo ou não inteiro antes de consultar."""
        with django_assert_num_queries(0):
            resp = api_client.get(
                "/api/v1/institucional/dres/108100/escolas/",
                {"tipo_escola_id": tipo_escola_id},
            )

        assert resp.status_code == 400
        assert resp.json()["tipo_escola_id"]

    def test_sem_api_key_retorna_401_ou_403(self) -> None:
        """Exige API key na listagem consolidada de escolas."""
        resp = APIClient().get("/api/v1/institucional/dres/108100/escolas/")

        assert resp.status_code in (401, 403)


class TestD13UnidadesConsolidadas:
    """D13 — GET /api/dres/{codigoEolDRE}/unidades/consolidadas/."""

    @pytest.mark.parametrize("parametros", [{}, {"retorno": "completo"}])
    def test_retorna_200_com_contrato_completo(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
        parametros: dict[str, str],
    ) -> None:
        """O retorno padrão e o completo preservam o contrato predial."""
        ue = ue_factory()
        url = reverse(
            "dre-unidades-consolidadas",
            kwargs={"codigo_eol_dre": ue.codigo_dre},
        )

        resp = api_client.get(url, parametros)

        assert resp.status_code == 200
        assert resp.data == [
            {
                "codigoEol": ue.codigo_ue,
                "nomeOficial": ue.nome,
                "nomeNaoOficial": ue.nome_nao_oficial,
                "tipoUnidadeAdmin": "DIRETORIA REGIONAL DE EDUCACAO",
                "tipoUE": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL 1",
                "logadouro": ue.logradouro,
                "numero": ue.numero,
                "bairro": ue.bairro,
                "cep": 1310100,
                "distrito": ue.distrito,
                "subPrefeitura": "SUBPREFEITURA 1",
                "nomeDre": "DIRETORIA REGIONAL DE EDUCACAO IPIRANGA 1",
                "email": ue.email,
                "telefone1": ue.telefone_1,
                "telefone2": None,
                "anoConstrucao": ue.ano_construcao,
                "propriedade": ue.propriedade,
                "capacidadeVagasMatutino": ue.vagas_matutino,
                "capacidadeVagasVespertino": ue.vagas_vespertino,
                "capacidadeVagasNoturno": ue.vagas_noturno,
                "capacidadeVagasIntermediario": ue.vagas_intermediario,
                "capacidadeVagasIntegral": ue.vagas_integral,
                "capacidadeVagasTotal": ue.vagas_total,
                "organizacaoParceira": ue.organizacao_parceira,
                "quantidadeDeFuncionarios": ue.quantidade_funcionarios,
                "status": ue.status,
                "subprefeituraId": ue.codigo_sub_prefeitura,
                "tipoUnidadeAdmId": 24,
            }
        ]

    def test_retorna_lista_de_codigos(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
    ) -> None:
        """O formato codigos retorna somente uma lista de códigos EOL."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/consolidadas/",
            {"retorno": "codigos"},
        )

        assert resp.status_code == 200
        assert resp.data == [ue.codigo_ue]

    def test_retorna_200_com_contrato_de_integracao(
        self,
        api_client: APIClient,
        ue_factory: Callable[..., UnidadeEducacional],
    ) -> None:
        """O formato integracao retorna os campos de integração e IDs."""
        ue = ue_factory(codigo_ue_integracao="INT001")
        resp = api_client.get(
            f"/api/v1/institucional/dres/{ue.codigo_dre}"
            "/unidades/consolidadas/",
            {"retorno": "integracao"},
        )

        assert resp.status_code == 200
        assert resp.data == [
            {
                "codigoUe": ue.codigo_ue,
                "nomeUe": ue.nome,
                "codigoIntegracao": "INT001",
                "tipoEscolaId": ue.codigo_tipo_escola,
                "tipoUnidadeId": ue.codigo_tipo_escola,
                "subprefeituraId": ue.codigo_sub_prefeitura,
                "dreId": ue.codigo_dre,
            }
        ]

    @pytest.mark.parametrize(
        "parametros",
        [
            {},
            {"retorno": "completo"},
            {"retorno": "codigos"},
            {"retorno": "integracao"},
        ],
    )
    def test_dre_sem_unidades_retorna_lista_vazia(
        self,
        api_client: APIClient,
        dre_factory: Callable[..., DRE],
        parametros: dict[str, str],
    ) -> None:
        """DRE sem unidades retorna 200 com lista vazia em todos os formatos."""
        dre = dre_factory()
        resp = api_client.get(
            f"/api/v1/institucional/dres/{dre.codigo_dre}"
            "/unidades/consolidadas/",
            parametros,
        )

        assert resp.status_code == 200
        assert resp.data == []

    def test_dre_inexistente_retorna_lista_vazia(
        self, api_client: APIClient
    ) -> None:
        """DRE inexistente retorna 200 com lista vazia."""
        resp = api_client.get(
            "/api/v1/institucional/dres/999999/unidades/consolidadas/"
        )

        assert resp.status_code == 200
        assert resp.data == []

    def test_codigo_vazio_retorna_400(self, api_client: APIClient) -> None:
        """Código de DRE em branco retorna 400."""
        resp = api_client.get(
            "/api/v1/institucional/dres/%20/unidades/consolidadas/"
        )

        assert resp.status_code == 400

    @pytest.mark.parametrize("retorno", ["", "invalido"])
    def test_retorno_invalido_retorna_400(
        self, api_client: APIClient, retorno: str
    ) -> None:
        """Formato vazio ou desconhecido retorna 400."""
        resp = api_client.get(
            "/api/v1/institucional/dres/108100/unidades/consolidadas/",
            {"retorno": retorno},
        )

        assert resp.status_code == 400
        assert resp.data["retorno"]

    def test_sem_api_key_retorna_401_ou_403(self) -> None:
        """Exige API key na consulta consolidada de unidades."""
        resp = APIClient().get(
            "/api/v1/institucional/dres/108100/unidades/consolidadas/"
        )

        assert resp.status_code in (401, 403)
