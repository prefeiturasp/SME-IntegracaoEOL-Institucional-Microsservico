"""Testes dos endpoints de health check."""

from unittest.mock import patch

import pytest
from django.db.utils import OperationalError

pytestmark = pytest.mark.django_db


class TestLiveness:
    """GET /institucional/api/health/live/"""

    def test_retorna_200_sem_autenticacao(self, db):
        """Liveness não exige autenticação e retorna status ok."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/health/live/")
        assert resp.status_code == 200
        assert resp.data["status"] == "ok"


class TestReadiness:
    """GET /institucional/api/health/ready/"""

    def test_retorna_200_com_banco_ok(self, db):
        """Readiness retorna 200 com check de banco bem-sucedido."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/health/ready/")
        assert resp.status_code == 200
        assert resp.data["status"] == "ok"
        assert "checks" in resp.data
        assert "database" in resp.data["checks"]
        assert resp.data["checks"]["database"]["ok"] is True
        assert "latency_ms" in resp.data["checks"]["database"]

    def test_sem_autenticacao(self, db):
        """Readiness é acessível sem autenticação."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/health/ready/")
        assert resp.status_code in (200, 503)

    @patch(
        "apps.core.health.connection.ensure_connection",
        side_effect=OperationalError,
    )
    def test_retorna_503_com_banco_indisponivel(self, _ensure_connection, db):
        """Readiness informa degradação quando o banco está indisponível."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/health/ready/")

        assert resp.status_code == 503
        assert resp.data["status"] == "degraded"
        assert resp.data["checks"]["database"]["ok"] is False


class TestHealth:
    """GET /institucional/api/health/"""

    def test_retorna_200_com_versao(self, db):
        """Health retorna versão e checks no payload."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/health/")
        assert resp.status_code in (200, 503)
        assert "version" in resp.data
        assert "checks" in resp.data

    def test_sem_autenticacao(self, db):
        """Health é acessível sem autenticação."""
        from rest_framework.test import APIClient

        resp = APIClient().get("/api/v1/institucional/health/")
        assert resp.status_code in (200, 503)
