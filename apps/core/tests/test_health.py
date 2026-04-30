"""Testes dos endpoints de health check."""

import pytest

pytestmark = pytest.mark.django_db


class TestLiveness:
    """GET /api/health/live/"""

    def test_retorna_200_sem_autenticacao(self, db):
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/health/live/")
        assert resp.status_code == 200
        assert resp.data["status"] == "ok"


class TestReadiness:
    """GET /api/health/ready/"""

    def test_retorna_200_com_banco_ok(self, db):
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/health/ready/")
        assert resp.status_code == 200
        assert resp.data["status"] == "ok"
        assert "checks" in resp.data
        assert "database" in resp.data["checks"]
        assert resp.data["checks"]["database"]["ok"] is True
        assert "latency_ms" in resp.data["checks"]["database"]

    def test_sem_autenticacao(self, db):
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/health/ready/")
        assert resp.status_code in (200, 503)


class TestHealth:
    """GET /api/health/"""

    def test_retorna_200_com_versao(self, db):
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/health/")
        assert resp.status_code in (200, 503)
        assert "version" in resp.data
        assert "checks" in resp.data

    def test_sem_autenticacao(self, db):
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/health/")
        assert resp.status_code in (200, 503)
