"""Testes das rotas de DRE (D01-D11) - Cobertura Total."""
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
class TestAutenticacao:
    """Verifica rejeição de requisições sem chave válida."""

    def test_sem_api_key_retorna_401(self) -> None:
        c = APIClient()
        resposta = c.get("/api/dres/")
        assert resposta.status_code == 401

@pytest.mark.django_db
class TestD01D11Dre:
    """D01-D11 — Endpoints de DRE."""

    def test_dre_mock_vazio_manual(self) -> None:
        """Cobre a linha dummy no mock de DRE."""
        from apps.core.mock_data import listar_dres
        assert listar_dres(dummy="vazio") == []

    # Sucessos
    def test_d01_listar_dres(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/")
        assert resposta.status_code == 200

    def test_d02_post_filtrar_dres_sucesso(self, client: APIClient) -> None:
        resposta = client.post("/api/dres/", ["100001"], format="json")
        assert resposta.status_code == 200


    def test_d04_detalhe_dre_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/")
        assert resposta.status_code == 200

    def test_d05_escolas_tipo_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/escolas/EMEF/")
        assert resposta.status_code == 200

    def test_d06_escolas_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/escola/")
        assert resposta.status_code == 200

    def test_d07_subprefeituras_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/subprefeituras/")
        assert resposta.status_code == 200

    def test_d08_ues_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/ues/")
        assert resposta.status_code == 200

    def test_d09_escolas_sigpae_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/escola/Sigpae/")
        assert resposta.status_code == 200

    def test_d10_unidades_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/unidades/")
        assert resposta.status_code == 200

    def test_d11_codigos_integracao_sucesso(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/100001/unidades/codigo-integracao/")
        assert resposta.status_code == 200

    def test_d02_post_non_list(self, client: APIClient) -> None:
        resposta = client.post("/api/dres/", {"codigo": "100001"}, format="json")
        assert resposta.status_code == 400

    def test_d02_post_vazio(self, client: APIClient) -> None:
        resposta = client.post("/api/dres/", [], format="json")
        assert resposta.status_code == 204

    def test_d02_post_nao_encontrado(self, client: APIClient) -> None:
        resposta = client.post("/api/dres/", ["999999"], format="json")
        assert resposta.status_code == 204


    def test_d04_detalhe_dre_nao_encontrada(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/000000/")
        assert resposta.status_code == 404

    def test_d05_escolas_tipo_vazio(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/%20/escolas/EMEF/")
        assert resposta.status_code == 400

    def test_d06_escolas_sem_resultados(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/999999/escola/")
        assert resposta.status_code == 204

    def test_d07_subprefeituras_vazio(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/%20/subprefeituras/")
        assert resposta.status_code == 400

    def test_d08_ues_vazio(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/%20/ues/")
        assert resposta.status_code == 400

    def test_d09_escolas_sigpae_vazio(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/%20/escola/Sigpae/")
        assert resposta.status_code == 400

    def test_d09_escolas_sigpae_sem_resultados(self, client: APIClient) -> None:
        resposta = client.get("/api/dres/999999/escola/Sigpae/")
        assert resposta.status_code == 204
