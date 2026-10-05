"""Testes dos endpoints de health check."""

from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestHealth:
    """Valida o endpoint público de health check."""

    @patch("apps.core.health._db_ok", return_value=(True, 1.2))
    def test_retorna_dependencias(self, _db_ok, db):
        """Health retorna status e checks do serviço."""
        response = APIClient().get("/api/v1/institucional/health/")

        assert response.status_code == 200
        assert response.data["status"] == "ok"
        assert response.data["checks"]["database"]["ok"] is True

    @patch("apps.core.health._db_ok", return_value=(False, 1.2))
    def test_retorna_degraded_quando_banco_falha(self, _db_ok, db):
        """Health informa degradação quando o banco está indisponível."""
        response = APIClient().get("/api/v1/institucional/health/")

        assert response.status_code == 503
        assert response.data["status"] == "degraded"
