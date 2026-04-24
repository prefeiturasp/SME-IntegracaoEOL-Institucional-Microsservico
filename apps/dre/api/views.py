"""Views do domínio DRE (D01-D11)."""
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from apps.core.views import BaseAPIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes

from apps.core.mock_data import (
    listar_codigos_integracao_por_dre,
    listar_codigos_ues_por_dre,
    listar_dres,
    filtrar_dres_por_codigos,
    listar_subprefeituras_por_dre,
    listar_unidades_por_dre,
    obter_dre_por_codigo,
    listar_escolas_por_dre,
)

_TAG_DRE = ["DiretoriaRegionalEducacao"]

class DreListView(BaseAPIView):
    """Lista DREs (GET) e filtra por código via POST (D01/D02)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Lista todas as DREs (D01).",
        tags=_TAG_DRE,
        operation_id="D01_listar_dres",
    )
    def get(self, _request: Request) -> Response:
        """Resposta com lista de todas as DREs (D01)."""
        return Response(listar_dres())

    @extend_schema(
        request={"application/json": {"type": "array", "items": {"type": "string"}}},
        responses={200: OpenApiTypes.ANY, 204: None},
        description="Busca DREs por lista de códigos (D02).",
        tags=_TAG_DRE,
        operation_id="D02_filtrar_dres_por_codigos",
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value=["100001", "100002"],
                request_only=True,
            )
        ],
    )
    def post(self, request: Request) -> Response:
        """Resposta com DREs encontradas ou 204 se vazio (D02)."""
        codigos = request.data
        if not isinstance(codigos, list):
            raise ValidationError("O corpo da requisição deve ser uma lista de códigos.")
        if not codigos:
            return Response(status=status.HTTP_204_NO_CONTENT)
        dres = filtrar_dres_por_codigos(codigos)
        if not dres:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(dres)


class DreDetalheView(BaseAPIView):
    """Retorna uma DRE pelo código EOL (D04)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Retorna uma DRE pelo código EOL (D04).",
        tags=_TAG_DRE,
        operation_id="D04_detalhe_dre",
    )
    def get(
        self, _request: Request, codigoEolDRE: str
    ) -> Response:
        """Resposta 200 ou 404 se não for encontrada."""
        dre = obter_dre_por_codigo(codigoEolDRE)
        if dre is None:
            raise NotFound("DRE não encontrada.")
        return Response(dre)


class DreEscolasTipoView(BaseAPIView):
    """Retorna escolas de uma DRE filtradas por tipo (D05)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Escolas filtradas por tipo (D05).",
        tags=_TAG_DRE,
        operation_id="D05_escolas_filtradas_por_tipo",
    )
    def get(
        self,
        _request: Request,
        codigoEolDRE: str,
        tipoEscola: str,
    ) -> Response:
        """Resposta 200 ou 400 se o código for inválido."""
        if not codigoEolDRE.strip():
            raise ValidationError("Código EOL da DRE é obrigatório.")
        escolas = listar_escolas_por_dre(codigoEolDRE, tipoEscola)
        return Response(escolas)


class DreEscolasView(BaseAPIView):
    """Retorna todas as escolas de uma DRE (D06)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Escolas vinculadas a uma DRE (D06).",
        tags=_TAG_DRE,
        operation_id="D06_escolas_vinculadas_dre",
    )
    def get(
        self, _request: Request, codigoEolDRE: str
    ) -> Response:
        """Resposta 200 ou 204 se a DRE não possuir escolas."""
        escolas = listar_escolas_por_dre(codigoEolDRE)
        if not escolas:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(escolas)


class DreSubprefeiturasView(BaseAPIView):
    """Retorna subprefeituras de uma DRE (D07)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Subprefeituras de uma DRE (D07).",
        tags=_TAG_DRE,
        operation_id="D07_subprefeituras_dre",
    )
    def get(
        self, _request: Request, dreCodigo: str
    ) -> Response:
        """Resposta 200 ou 400 se o código for inválido."""
        if not dreCodigo.strip():
            raise ValidationError("Código da DRE é obrigatório.")
        subprefeituras = listar_subprefeituras_por_dre(dreCodigo)
        return Response(subprefeituras)


class DreUesView(BaseAPIView):
    """Retorna códigos das UEs de uma DRE (D08)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Códigos de UEs de uma DRE (D08).",
        tags=_TAG_DRE,
        operation_id="D08_codigos_ues_dre",
    )
    def get(
        self, _request: Request, dreCodigo: str
    ) -> Response:
        """Resposta 200 ou 400 se for inválido."""
        if not dreCodigo.strip():
            raise ValidationError("Código da DRE é obrigatório.")
        codigos = listar_codigos_ues_por_dre(dreCodigo)
        return Response(codigos)


class DreEscolasSigpaeView(BaseAPIView):
    """Retorna escolas SIGPAE de uma DRE (D09)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Escolas para o SIGPAE (D09).",
        tags=_TAG_DRE,
        operation_id="D09_escolas_sigpae",
    )
    def get(
        self, _request: Request, codigoEolDRE: str
    ) -> Response:
        """Resposta 200, 204 se não houver escolas, ou 400 se for inválido."""
        if not codigoEolDRE.strip():
            raise ValidationError("Código EOL da DRE é obrigatório.")
        escolas = listar_escolas_por_dre(codigoEolDRE)
        if not escolas:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(escolas)


class DreUnidadesView(BaseAPIView):
    """Retorna unidades completas de uma DRE (D10)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Unidades de gestão predial (D10).",
        tags=_TAG_DRE,
        operation_id="D10_unidades_gestao_predial",
    )
    def get(
        self, _request: Request, dreCodigo: str
    ) -> Response:
        """Resposta 200 com dados completos das unidades."""
        unidades = listar_unidades_por_dre(dreCodigo)
        return Response(unidades)


class DreCodigosIntegracaoView(BaseAPIView):
    """Retorna códigos de integração das UEs da DRE (D11)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="UEs com código de integração (D11).",
        tags=_TAG_DRE,
        operation_id="D11_ues_codigo_integracao",
    )
    def get(
        self, _request: Request, dreCodigo: str
    ) -> Response:
        """Resposta 200 com códigos de integração."""
        codigos = listar_codigos_integracao_por_dre(dreCodigo)
        return Response(codigos)
