"""Views do domínio Turmas (T01-T02) — placeholders cross-domain Pedagógico."""

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import BaseAPIView, _CROSS_DOMAIN_SCHEMA

_TAG_CD = ["CrossDomain"]


class SincronizacoesTurmaView(BaseAPIView):
    """T01 — cross-domain Pedagógico."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Sincronizações institucionais de uma turma (T01). "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T01_sincronizacoes_turma",
    )
    def get(
        self, _request: Request, ueCodigo: str, turmaCodigo: str
    ) -> Response:
        """Retorna 501 — competência do domínio Pedagógico."""
        return self.cross_domain("pedagogico")


class SincronizacoesTurmaLegacyView(BaseAPIView):
    """T01 [LEGACY COMPATIBILITY ROUTE] — alias /api/turmas/{ueCodigo}/turmas/{turmaCodigo}/..."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Sincronizações institucionais de uma turma (T01). "
            "[LEGACY COMPATIBILITY ROUTE] Use /api/ues/{ueCodigo}/turmas/{turmaCodigo}/sincronizacoes-institucionais/. "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T01_sincronizacoes_turma_legacy",
    )
    def get(
        self, _request: Request, ueCodigo: str, turmaCodigo: str
    ) -> Response:
        """Retorna 501 — competência do domínio Pedagógico."""
        return self.cross_domain("pedagogico")


class AnosLetivosSincronizacaoTurmaView(BaseAPIView):
    """T02 — cross-domain Pedagógico."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Anos letivos com sincronizações de turmas de uma UE (T02). "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T02_anos_letivos_sincronizacao_turma",
    )
    def get(self, _request: Request, ueCodigo: str) -> Response:
        """Retorna 501 — competência do domínio Pedagógico."""
        return self.cross_domain("pedagogico")


class AnosLetivosSincronizacaoTurmaLegacyView(BaseAPIView):
    """T02 [LEGACY COMPATIBILITY ROUTE] — alias /api/ues/ue/{ueCodigo}/..."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Anos letivos com sincronizações de turmas de uma UE (T02). "
            "[LEGACY COMPATIBILITY ROUTE] Use /api/turmas/ue/{ueCodigo}/sincronizacoes-institucionais/anos-letivos/. "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T02_anos_letivos_sincronizacao_turma_legacy",
    )
    def get(self, _request: Request, ueCodigo: str) -> Response:
        """Retorna 501 — competência do domínio Pedagógico."""
        return self.cross_domain("pedagogico")
