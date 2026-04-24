"""Testes das rotas de Unidade Educacional (E01-E04, E06, E10-E11, E17, E23, E25-E27)."""
import pytest
from rest_framework.test import APIClient

API_KEY = "dev-key-default"

@pytest.fixture
def client() -> APIClient:
    """Retorna cliente de teste com API key configurada."""
    c = APIClient()
    c.credentials(HTTP_X_API_KEY=API_KEY)
    return c

@pytest.mark.django_db
class TestUnidadeEducacionalEndpoints:
    """Endpoints mantidos de Unidade Educacional."""

    def test_ue_mock_manual(self) -> None:
        """Cobre funções de mock mantidas."""
        from apps.core.mock_data import (
            listar_escolas,
            listar_unidades_parceiras, obter_unidade_eol, 
            obter_subprefeitura_escola
        )
        assert len(listar_escolas()) > 0
        assert len(listar_unidades_parceiras()) > 0
        assert obter_unidade_eol("000000") is None
        assert obter_subprefeitura_escola("000000") is None

    # Sucessos
    def test_e01_admin_sgp(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/200001/administrador-sgp/")
        assert resposta.status_code == 200

    def test_e02_ue_detalhe(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/200001/")
        assert resposta.status_code == 200

    def test_e03_unidade_eol(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/unidade-eol/200001/")
        assert resposta.status_code == 200

    def test_e04_dados_ue(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/dados/200001/")
        assert resposta.status_code == 200

    def test_e06_ue_list_post(self, client: APIClient) -> None:
        resposta = client.post("/api/escolas/", ["200001"], format="json")
        assert resposta.status_code == 200

    def test_e10_tipos_ue(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/tipos_unidade_educacao/")
        assert resposta.status_code == 200

    def test_e11_tipos_escolas(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/tiposEscolas/")
        assert resposta.status_code == 200

    def test_e17_subprefeituras(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/200001/subprefeituras/")
        assert resposta.status_code == 200

    def test_e23_sincronizacao(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/200001/sincronizacoes-institucionais/")
        assert resposta.status_code == 200

    def test_e25_equipamentos(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/equipamentos/")
        assert resposta.status_code == 200

    def test_e26_unidades_parceiras(self, client: APIClient) -> None:
        resposta = client.post("/api/escolas/unidades-parceiras/", ["1"], format="json")
        assert resposta.status_code == 200

    def test_e27_todas_unidades(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/todas-unidades/")
        assert resposta.status_code == 200

    # Erros e Borda
    def test_e01_admin_sgp_vazio(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/%20/administrador-sgp/")
        assert resposta.status_code == 400

    def test_e01_admin_sgp_no_content(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/999999/administrador-sgp/")
        assert resposta.status_code == 204

    def test_e02_ue_detalhe_vazio(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/%20/")
        assert resposta.status_code == 400

    def test_e02_ue_detalhe_nao_encontrada(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/000000/")
        assert resposta.status_code == 404

    def test_e03_unidade_eol_nao_encontrada(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/unidade-eol/000000/")
        assert resposta.status_code == 404

    def test_e04_dados_ue_nao_encontrada(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/dados/000000/")
        assert resposta.status_code == 404

    def test_e06_ue_list_post_vazio(self, client: APIClient) -> None:
        resposta = client.post("/api/escolas/", [], format="json")
        assert resposta.status_code == 400

    def test_e17_subprefeituras_nao_encontrada(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/000000/subprefeituras/")
        assert resposta.status_code == 404

    def test_e23_sincronizacao_nao_encontrada(self, client: APIClient) -> None:
        resposta = client.get("/api/escolas/000000/sincronizacoes-institucionais/")
        assert resposta.status_code == 404

    def test_e26_unidades_parceiras_vazio(self, client: APIClient) -> None:
        resposta = client.post("/api/escolas/unidades-parceiras/", [], format="json")
        assert resposta.status_code == 400
