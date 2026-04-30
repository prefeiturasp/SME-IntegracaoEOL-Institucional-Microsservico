"""Testes dos endpoints cross-domain de Turmas (T01-T02)."""

import pytest

pytestmark = pytest.mark.django_db


class TestT01SincronizacoesTurma:
    """T01 — GET /api/ues/{ueCodigo}/turmas/{turmaCodigo}/sincronizacoes-institucionais/"""

    def test_retorna_501(self, api_client, db):
        resp = api_client.get(
            "/api/ues/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 501

    def test_shape_cross_domain(self, api_client, db):
        resp = api_client.get(
            "/api/ues/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.data["dominio"] == "pedagogico"
        assert resp.data["transitionGateway"] is True
        assert "detail" in resp.data

    def test_detail_sem_ponto_final(self, api_client, db):
        resp = api_client.get(
            "/api/ues/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert not resp.data["detail"].endswith(".")

    def test_requer_autenticacao(self, db):
        from rest_framework.test import APIClient
        resp = APIClient().get(
            "/api/ues/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.status_code in (401, 403)

    def test_rota_legacy_retorna_501(self, api_client, db):
        """[LEGACY COMPATIBILITY ROUTE] /api/turmas/{ueCodigo}/turmas/... retorna 501."""
        resp = api_client.get(
            "/api/turmas/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"

    def test_header_autenticacao_correto(self, db):
        """Valida que x-api-eol-key é o header aceito."""
        from django.conf import settings
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(HTTP_X_API_EOL_KEY=settings.API_KEY)
        resp = client.get(
            "/api/ues/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 501


class TestT02AnosLetivosSincronizacao:
    """T02 — GET /api/turmas/ue/{ueCodigo}/sincronizacoes-institucionais/anos-letivos/"""

    def test_retorna_501(self, api_client, db):
        resp = api_client.get(
            "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.status_code == 501

    def test_shape_cross_domain(self, api_client, db):
        resp = api_client.get(
            "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.data["dominio"] == "pedagogico"
        assert resp.data["transitionGateway"] is True
        assert "detail" in resp.data

    def test_detail_sem_ponto_final(self, api_client, db):
        resp = api_client.get(
            "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert not resp.data["detail"].endswith(".")

    def test_requer_autenticacao(self, db):
        from rest_framework.test import APIClient
        resp = APIClient().get(
            "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.status_code in (401, 403)

    def test_rota_legacy_retorna_501(self, api_client, db):
        """[LEGACY COMPATIBILITY ROUTE] /api/ues/ue/{ueCodigo}/... retorna 501."""
        resp = api_client.get(
            "/api/ues/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"

    def test_header_autenticacao_correto(self, db):
        """Valida que x-api-eol-key é o header aceito."""
        from django.conf import settings
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(HTTP_X_API_EOL_KEY=settings.API_KEY)
        resp = client.get(
            "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.status_code == 501


class TestRotasCanonicase:
    """Valida rotas canônicas e aliases legados de T01/T02."""

    def test_t01_canonico_retorna_501(self, api_client, db):
        resp = api_client.get(
            "/api/ues/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 501

    def test_t02_canonico_retorna_501(self, api_client, db):
        resp = api_client.get(
            "/api/turmas/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.status_code == 501

    def test_t01_legacy_retorna_501(self, api_client, db):
        """[LEGACY COMPATIBILITY ROUTE] alias de T01."""
        resp = api_client.get(
            "/api/turmas/019251/turmas/ABC123/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"

    def test_t02_legacy_retorna_501(self, api_client, db):
        """[LEGACY COMPATIBILITY ROUTE] alias de T02."""
        resp = api_client.get(
            "/api/ues/ue/019251/sincronizacoes-institucionais/anos-letivos/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"
