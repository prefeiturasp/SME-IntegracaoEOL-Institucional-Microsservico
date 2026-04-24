from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from apps.core.views import BaseAPIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from apps.core.mock_data import (
    listar_administradores,
    listar_equipamentos,
    listar_escolas,
    listar_tipos_escolas,
    listar_tipos_unidade_educacao,
    listar_unidades_parceiras,
    obter_dados_escola,
    obter_escola_por_codigo,
    obter_sincronizacao_escola,
    obter_subprefeitura_escola,
    obter_unidade_eol,
)

_TAG_UE = ["Escola"]

class UnidadeEducacionalAdminSgpView(BaseAPIView):
    """Retorna administradores SGP de uma unidade (E01)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="codigoUE",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Código da UE.",
            ),
            OpenApiParameter(
                name="anoLetivo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ano letivo para filtro.",
            ),
        ],
        responses={200: OpenApiTypes.ANY},
        description="Logins dos administradores SGP da UE (E01).",
        tags=_TAG_UE,
        operation_id="E01_administrador_sgp",
    )
    def get(
        self, _request: Request, codigoUE: str
    ) -> Response:
        """Resposta 200, 204 ou 400 se o código estiver vazio."""
        if not codigoUE.strip():
            raise ValidationError("Código da UE é obrigatório.")
        admins = listar_administradores(codigoUE)
        if admins is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(admins)


class UnidadeEducacionalDetalheView(BaseAPIView):
    """Retorna unidade pelo código EOL (E02)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="codigoEscolaEol",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Código EOL da unidade.",
            ),
        ],
        responses={200: OpenApiTypes.ANY},
        description="Dados básicos de uma UE (E02).",
        tags=_TAG_UE,
        operation_id="E02_dados_basicos_ue",
    )
    def get(
        self, _request: Request, codigoEscolaEol: str
    ) -> Response:
        """Resposta 200, 400 se vazio, ou 404 se o código for '000000'."""
        if not codigoEscolaEol.strip():
            raise ValidationError(
                "Código da unidade EOL é obrigatório."
            )
        resultado = obter_escola_por_codigo(codigoEscolaEol)
        if resultado is None:
            raise NotFound("Unidade não encontrada.")
        return Response([resultado])


class UnidadeEolView(BaseAPIView):
    """Retorna unidade EOL resumida (E03)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="codigoEol",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Código EOL da unidade.",
            ),
        ],
        responses={200: OpenApiTypes.ANY},
        description="UE por código EOL (E03).",
        tags=_TAG_UE,
        operation_id="E03_ue_codigo_eol",
    )
    def get(
        self, _request: Request, codigoEol: str
    ) -> Response:
        """Resposta 200 ou 404 se o código for '000000'."""
        unidade = obter_unidade_eol(codigoEol)
        if unidade is None:
            raise NotFound("Unidade EOL não encontrada.")
        return Response(unidade)


class DadosUnidadeEducacionalView(BaseAPIView):
    """Retorna dados detalhados da unidade (E04)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="codigoEscolaEol",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Código EOL da unidade.",
            ),
        ],
        responses={200: OpenApiTypes.ANY},
        description="Dados completos de uma UE (E04).",
        tags=_TAG_UE,
        operation_id="E04_dados_completos_ue",
    )
    def get(
        self, _request: Request, codigoEscolaEol: str
    ) -> Response:
        """Resposta 200 or 404 if code is '000000'."""
        dados = obter_dados_escola(codigoEscolaEol)
        if dados is None:
            raise NotFound("Dados da unidade não encontrados.")
        return Response(dados)


class UnidadeEducacionalListPostView(BaseAPIView):
    """Retorna unidades por lista de códigos via POST (E06)."""

    @extend_schema(
        request={"application/json": {"type": "array", "items": {"type": "string"}}},
        responses={200: OpenApiTypes.ANY},
        description="Busca UEs por lista de códigos (E06).",
        tags=_TAG_UE,
        operation_id="E06_buscar_ues_lista_codigos",
        examples=[
            OpenApiExample(
                "Exemplo de Requisição (E06)",
                value=["019251", "019252"],
                request_only=True,
            )
        ],
    )
    def post(self, request: Request) -> Response:
        """Resposta 200 ou 400 se a lista estiver vazia."""
        codigos = request.data
        if not isinstance(codigos, list) or not codigos:
            raise ValidationError(
                "Lista de códigos é obrigatória e não pode ser vazia."
            )
        escolas = listar_escolas(codigos)
        return Response(escolas)


class TiposUnidadeEducacaoView(BaseAPIView):
    """Retorna tipos de unidade de educação (E10)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Lista tipos de unidades de educação (E10).",
        tags=_TAG_UE,
        operation_id="E10_tipos_unidade_educacional",
    )
    def get(self, _request: Request) -> Response:
        """Resposta 200 with tipos de UE."""
        return Response(listar_tipos_unidade_educacao())


class TiposEscolasView(BaseAPIView):
    """Retorna tipos de escola com código e sigla (E11)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Código e sigla de tipos de escola (E11).",
        tags=_TAG_UE,
        operation_id="E11_codigo_sigla_tipos_escola",
    )
    def get(self, _request: Request) -> Response:
        """Resposta 200 with list of types."""
        return Response(listar_tipos_escolas())


class SubprefeituraUnidadeEducacionalView(BaseAPIView):
    """Retorna subprefeituras da unidade (E17)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="codigoEscolaEol",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Código EOL da unidade.",
            ),
        ],
        responses={200: OpenApiTypes.ANY},
        description="Subprefeituras da unidade (E17).",
        tags=_TAG_UE,
        operation_id="E17_subprefeituras_ue",
    )
    def get(
        self, _request: Request, codigoEscolaEol: str
    ) -> Response:
        """Resposta 200 or 404 if code is '000000'."""
        subprefeituras = obter_subprefeitura_escola(
            codigoEscolaEol
        )
        if subprefeituras is None:
            raise NotFound("Unidade não encontrada.")
        return Response(subprefeituras)


class SincronizacaoUnidadeEducacionalView(BaseAPIView):
    """Retorna dados de sincronização da unidade (E23)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ueCodigo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Código da UE.",
            ),
        ],
        responses={200: OpenApiTypes.ANY},
        description="Detalhes para sincronização institucional da UE (E23).",
        tags=_TAG_UE,
        operation_id="E23_detalhes_sincronizacao_institucional_ue",
    )
    def get(
        self, _request: Request, ueCodigo: str
    ) -> Response:
        """Resposta 200 or 404 if code is '000000'."""
        dados = obter_sincronizacao_escola(ueCodigo)
        if dados is None:
            raise NotFound("Unidade não encontrada.")
        return Response(dados)


class EquipamentosView(BaseAPIView):
    """Retorna equipamentos com filtros via query (E25)."""

    @extend_schema(
        parameters=[
            OpenApiParameter("codigosSubprefeitura", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, many=True),
            OpenApiParameter("codigosDre", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, many=True),
            OpenApiParameter("tiposUnidade", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, many=True),
            OpenApiParameter("tiposEscola", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, many=True),
            OpenApiParameter("nomeEscola", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter("codigoEol", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiTypes.ANY},
        description="Equipamentos SME com filtro (E25).",
        tags=_TAG_UE,
        operation_id="E25_equipamentos_sme_filtro",
    )
    def get(self, _request: Request) -> Response:
        """Resposta 200 com a lista de equipamentos."""
        equipamentos = listar_equipamentos()
        return Response(equipamentos)


class UnidadesParceirasView(BaseAPIView):
    """Retorna unidades parceiras por lista de códigos (E26)."""

    @extend_schema(
        request={"application/json": {"type": "array", "items": {"type": "string"}}},
        responses={200: OpenApiTypes.ANY},
        description="Unidades parceiras por lista de códigos (E26).",
        examples=[
            OpenApiExample(
                "Exemplo de Requisição (E26)",
                value=["019251", "019252"],
                request_only=True,
            )
        ],
        tags=_TAG_UE,
        operation_id="E26_unidades_parceiras_lista_codigos",
    )
    def post(self, request: Request) -> Response:
        """Resposta 200 ou 400 se a lista estiver vazia."""
        codigos = request.data
        if not isinstance(codigos, list) or not codigos:
            raise ValidationError(
                "Lista de códigos é obrigatória e não pode ser vazia."
            )
        unidades = listar_unidades_parceiras(codigos)
        return Response(unidades)


class TodasUnidadesView(BaseAPIView):
    """Retorna todas as unidades/escolas (E27)."""

    @extend_schema(
        responses={200: OpenApiTypes.ANY},
        description="Lista todas as UEs (E27).",
        tags=_TAG_UE,
        operation_id="E27_lista_todas_ues",
    )
    def get(self, _request: Request) -> Response:
        """Resposta 200 with todas as unidades."""
        return Response(listar_escolas())
