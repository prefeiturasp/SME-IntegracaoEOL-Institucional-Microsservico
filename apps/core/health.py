"""Endpoints de health check — liveness, readiness e status."""

import time

from django.db import connection
from django.db.utils import OperationalError
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

_VERSION = "1.0.0"


def _db_ok() -> tuple[bool, float]:
    t0 = time.monotonic()
    try:
        connection.ensure_connection()
        return True, round((time.monotonic() - t0) * 1000, 2)
    except OperationalError:
        return False, round((time.monotonic() - t0) * 1000, 2)


class LivenessView(APIView):
    """GET /api/health/live/ — sinal de vida do processo."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, _request: Request) -> Response:
        return Response({"status": "ok"})


class ReadinessView(APIView):
    """GET /api/health/ready/ — pronto para receber tráfego."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, _request: Request) -> Response:
        db_ok, db_ms = _db_ok()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "version": _VERSION,
            "checks": {
                "database": {"ok": db_ok, "latency_ms": db_ms},
            },
        }
        status_code = 200 if db_ok else 503
        return Response(payload, status=status_code)


class HealthView(APIView):
    """GET /api/health/ — status detalhado."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, _request: Request) -> Response:
        db_ok, db_ms = _db_ok()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "version": _VERSION,
            "checks": {
                "database": {"ok": db_ok, "latency_ms": db_ms},
            },
        }
        return Response(payload, status=200 if db_ok else 503)
