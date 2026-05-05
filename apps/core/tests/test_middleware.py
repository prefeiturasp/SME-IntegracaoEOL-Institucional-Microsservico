"""Testes do middleware de observabilidade e de prefixo."""

import pytest

pytestmark = pytest.mark.django_db


class TestObservabilidadeMiddleware:
    """Verifica injeção de correlation-id e tempo de resposta nos headers."""

    def test_injeta_correlation_id_nos_headers(self, api_client, db):
        resp = api_client.get("/institucional/api/health/live/")
        assert "X-Correlation-Id" in resp
        assert len(resp["X-Correlation-Id"]) == 36  # UUID4 format

    def test_propaga_correlation_id_do_request(self, db):
        from rest_framework.test import APIClient

        client = APIClient()
        resp = client.get(
            "/institucional/api/health/live/", HTTP_X_CORRELATION_ID="meu-id-customizado"
        )
        assert resp["X-Correlation-Id"] == "meu-id-customizado"

    def test_injeta_response_time_ms(self, api_client, db):
        resp = api_client.get("/institucional/api/health/live/")
        assert "X-Response-Time-Ms" in resp
        assert float(resp["X-Response-Time-Ms"]) >= 0


class TestPrefixMiddleware:
    """Verifica que rotas funcionam com e sem prefixo."""

    def test_rota_sem_prefixo_funciona(self, api_client, db):
        resp = api_client.get("/institucional/api/health/live/")
        assert resp.status_code == 200


class TestCrossDomainShape:
    """Verifica a forma padronizada de todas as respostas cross-domain."""

    _CHAVES_OBRIGATORIAS = {"detail", "dominio", "transitionGateway"}

    def _assert_shape(self, resp) -> None:
        assert resp.status_code == 501
        for chave in self._CHAVES_OBRIGATORIAS:
            assert chave in resp.data, f"Chave '{chave}' ausente na resposta 501"
        assert resp.data["transitionGateway"] is True

    def test_d03_supervisores(self, api_client, db):
        self._assert_shape(api_client.get("/api/dres/108100/supervisores/"))

    def test_e01_admin_sgp(self, api_client, db):
        self._assert_shape(api_client.get("/api/escolas/019251/administrador-sgp/"))

    def test_e05_quantidade_alunos(self, api_client, db):
        self._assert_shape(api_client.get("/api/escolas/019251/alunos/quantidade/"))

    def test_e07_professores_ano(self, api_client, db):
        self._assert_shape(api_client.get("/api/escolas/019251/professores/2024/"))

    def test_e08_professores(self, api_client, db):
        self._assert_shape(api_client.get("/api/escolas/019251/professores/"))

    def test_e09_modalidades(self, api_client, db):
        self._assert_shape(api_client.get("/api/escolas/modalidades_ensino/"))

    def test_e12_salas(self, api_client, db):
        self._assert_shape(
            api_client.get("/api/escolas/019251/salas/SALA/anos_letivos/2024/")
        )

    def test_e13_funcionarios(self, api_client, db):
        self._assert_shape(api_client.get("/api/escolas/019251/funcionarios/"))

    def test_e18_turmas(self, api_client, db):
        self._assert_shape(
            api_client.get("/api/escolas/019251/turmas/anos_letivos/2024/")
        )

    def test_e24_matriculas(self, api_client, db):
        self._assert_shape(
            api_client.get("/api/escolas/019251/aluno/123/matriculas/")
        )

    def test_t01_sincronizacao_turma(self, api_client, db):
        self._assert_shape(
            api_client.get(
                "/api/ues/019251/turmas/ABC/sincronizacoes-institucionais/"
            )
        )

    def test_t02_anos_letivos(self, api_client, db):
        self._assert_shape(
            api_client.get(
                "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
            )
        )
