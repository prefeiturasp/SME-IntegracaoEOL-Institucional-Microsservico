"""Views do domínio Turmas."""

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import BaseAPIView, _CROSS_DOMAIN_SCHEMA

_TAG_CD = ["CrossDomain"]


class SincronizacoesTurmaView(BaseAPIView):
    """Sincronizações institucionais de uma turma — domínio Pedagógico."""

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
        self, _request: Request, ue_codigo: str, turma_codigo: str
    ) -> Response:
        """Redireciona para o microserviço Pedagógico.

        Args:
            _request: Requisição HTTP (não utilizada).
            ue_codigo: Código EOL da unidade educacional.
            turma_codigo: Código da turma.

        Returns:
            Resposta 501 com indicação de domínio responsável.
        """
        return self.cross_domain("pedagogico")


class SincronizacoesTurmaLegacyView(BaseAPIView):
    """Sincronizações institucionais de turma — rota legada.

    Competência do domínio Pedagógico.
    """

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Sincronizações institucionais de uma turma (T01). "
            "Use /api/ues/{ue_codigo}/turmas/{turma_codigo}/sincronizacoes-institucionais/. "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T01_sincronizacoes_turma_legacy",
    )
    def get(
        self, _request: Request, ue_codigo: str, turma_codigo: str
    ) -> Response:
        """Redireciona para o microserviço Pedagógico (rota legada).

        Args:
            _request: Requisição HTTP (não utilizada).
            ue_codigo: Código EOL da unidade educacional.
            turma_codigo: Código da turma.

        Returns:
            Resposta 501 com indicação de domínio responsável.
        """
        return self.cross_domain("pedagogico")


class AnosLetivosSincronizacaoTurmaView(BaseAPIView):
    """Anos letivos com sincronizações de turmas de uma UE.

    Competência do domínio Pedagógico.
    """

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Anos letivos com sincronizações de turmas de uma UE (T02). "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T02_anos_letivos_sincronizacao_turma",
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        """Redireciona para o microserviço Pedagógico.

        Args:
            _request: Requisição HTTP (não utilizada).
            ue_codigo: Código EOL da unidade educacional.

        Returns:
            Resposta 501 com indicação de domínio responsável.
        """
        return self.cross_domain("pedagogico")


class AnosLetivosSincronizacaoTurmaLegacyView(BaseAPIView):
    """Anos letivos com sincronizações de turmas de uma UE — rota legada.

    Competência do domínio Pedagógico.
    """

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Anos letivos com sincronizações de turmas de uma UE (T02). "
            "Use /api/turmas/ue/{ue_codigo}/sincronizacoes-institucionais/anos-letivos/. "
            "[CROSS-DOMAIN] Competência do microserviço Pedagógico."
        ),
        tags=_TAG_CD,
        operation_id="T02_anos_letivos_sincronizacao_turma_legacy",
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        """Redireciona para o microserviço Pedagógico (rota legada).

        Args:
            _request: Requisição HTTP (não utilizada).
            ue_codigo: Código EOL da unidade educacional.

        Returns:
            Resposta 501 com indicação de domínio responsável.
        """
        return self.cross_domain("pedagogico")
