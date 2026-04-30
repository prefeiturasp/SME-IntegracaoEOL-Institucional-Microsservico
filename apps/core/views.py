"""View base compartilhada por todos os domínios."""

from drf_spectacular.utils import inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

_DOMINIOS = ("professores", "alunos", "pedagogico", "institucional")

# Schema reutilizável para respostas 501 cross-domain
_CROSS_DOMAIN_SCHEMA = inline_serializer(
    name="CrossDomainResponse",
    fields={
        "detail": serializers.CharField(default="Endpoint de responsabilidade de outro domínio"),
        "dominio": serializers.CharField(),
        "transitionGateway": serializers.BooleanField(default=True),
    },
)

# Schema reutilizável para respostas de erro (400/404)
_PROBLEM_DETAILS_SCHEMA = inline_serializer(
    name="ProblemDetails",
    fields={"detail": serializers.CharField()},
)


class BaseAPIView(APIView):
    """View base com autenticação e permissão padrão do projeto."""

    @staticmethod
    def cross_domain(dominio: str) -> Response:
        """Resposta padrão 501 para endpoints de outro domínio."""
        return Response(
            {
                "detail": "Endpoint de responsabilidade de outro domínio",
                "dominio": dominio,
                "transitionGateway": True,
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
