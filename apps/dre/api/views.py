"""Views do domínio DRE (D01-D11)."""

from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import (
    BaseAPIView,
    _CROSS_DOMAIN_SCHEMA,
    _PROBLEM_DETAILS_SCHEMA,
)
from apps.dre.selectors import (
    filtrar_dres_por_codigos,
    listar_codigos_integracao_por_dre,
    listar_codigos_ues_por_dre,
    listar_dres,
    listar_escolas_por_dre,
    listar_subprefeituras_por_dre,
    listar_unidades_por_dre,
    obter_dre_por_codigo,
)

_TAG_DRE = ["DiretoriaRegionalEducacao"]

_DRE_FIELDS = {
    "codigoDRE": serializers.CharField(),
    "nomeDRE": serializers.CharField(),
    "siglaDRE": serializers.CharField(),
}

_ESCOLA_FIELDS = {
    "codigoEscola": serializers.CharField(),
    "nomeEscola": serializers.CharField(),
    "codigoDRE": serializers.CharField(),
    "tipoEscola": serializers.CharField(),
    "siglaTipoEscola": serializers.CharField(),
    "nomeDRE": serializers.CharField(),
    "siglaDRE": serializers.CharField(),
    "codigoSubprefeitura": serializers.CharField(),
    "nomeSubprefeitura": serializers.CharField(),
    "tipoEscolaId": serializers.IntegerField(allow_null=True),
    "tipoUnidadeId": serializers.IntegerField(allow_null=True),
    "subprefeituraId": serializers.IntegerField(allow_null=True),
    "dreId": serializers.CharField(),
    "codigoIntegracao": serializers.CharField(allow_null=True),
}

_SUBPREFEITURA_FIELDS = {
    "codigoSubprefeitura": serializers.CharField(),
    "nomeSubprefeitura": serializers.CharField(),
}

_UNIDADE_PREDIAL_FIELDS = {
    "codigoEol": serializers.CharField(),
    "nomeOficial": serializers.CharField(),
    "nomeNaoOficial": serializers.CharField(allow_null=True),
    "tipoUnidadeAdmin": serializers.CharField(allow_null=True),
    "tipoUE": serializers.CharField(allow_null=True),
    "logadouro": serializers.CharField(allow_null=True),
    "numero": serializers.CharField(allow_null=True),
    "bairro": serializers.CharField(allow_null=True),
    "cep": serializers.IntegerField(allow_null=True),
    "distrito": serializers.CharField(allow_null=True),
    "subPrefeitura": serializers.CharField(allow_null=True),
    "nomeDre": serializers.CharField(),
    "email": serializers.CharField(allow_null=True),
    "telefone1": serializers.CharField(allow_null=True),
    "telefone2": serializers.CharField(allow_null=True),
    "anoConstrucao": serializers.IntegerField(allow_null=True),
    "propriedade": serializers.CharField(allow_null=True),
    "capacidadeVagasMatutino": serializers.IntegerField(),
    "capacidadeVagasVespertino": serializers.IntegerField(),
    "capacidadeVagasNoturno": serializers.IntegerField(),
    "capacidadeVagasIntermediario": serializers.IntegerField(),
    "capacidadeVagasIntegral": serializers.IntegerField(),
    "capacidadeVagasTotal": serializers.IntegerField(),
    "organizacaoParceira": serializers.BooleanField(),
    "quantidadeDeFuncionarios": serializers.IntegerField(),
    "status": serializers.CharField(allow_null=True),
    "subprefeituraId": serializers.IntegerField(allow_null=True),
    "tipoUnidadeAdmId": serializers.IntegerField(allow_null=True),
}

_CODIGO_INTEGRACAO_FIELDS = {
    "codigoUe": serializers.CharField(),
    "nomeUe": serializers.CharField(),
    "codigoIntegracao": serializers.CharField(allow_null=True),
    "tipoEscolaId": serializers.IntegerField(allow_null=True),
    "tipoUnidadeId": serializers.IntegerField(allow_null=True),
    "subprefeituraId": serializers.IntegerField(allow_null=True),
    "dreId": serializers.CharField(),
}


class DreListView(BaseAPIView):
    """Lista DREs (GET) e filtra por código via POST (D01/D02)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="DreResumoList",
                fields=_DRE_FIELDS,
                many=True,
            ),
        },
        description="Lista todas as DREs (D01).",
        tags=_TAG_DRE,
        operation_id="D01_listar_dres",
        examples=[
            OpenApiExample(
                "Resposta D01",
                value=[
                    {
                        "codigoDRE": "108100",
                        "nomeDRE": "DRE IPIRANGA",
                        "siglaDRE": "DRE-IP",
                    },
                ],
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request) -> Response:
        """Resposta com lista de todas as DREs (D01)."""
        return Response(listar_dres())

    @extend_schema(
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        responses={
            200: inline_serializer(
                name="DreResumoFiltrado",
                fields=_DRE_FIELDS,
                many=True,
            ),
            204: None,
            400: _PROBLEM_DETAILS_SCHEMA,
        },
        description="Busca DREs por lista de códigos (D02).",
        tags=_TAG_DRE,
        operation_id="D02_filtrar_dres_por_codigos",
        examples=[
            OpenApiExample(
                "Exemplo de Requisição",
                value=["108100", "108200"],
                request_only=True,
            )
        ],
    )
    def post(self, request: Request) -> Response:
        """Resposta com DREs encontradas ou 204 se vazio (D02)."""
        codigos = request.data
        if not isinstance(codigos, list):
            raise ValidationError(
                "O corpo da requisição deve ser uma lista de códigos."
            )
        if not codigos:
            return Response(status=status.HTTP_204_NO_CONTENT)
        dres = filtrar_dres_por_codigos(codigos)
        if not dres:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(dres)


class DreDetalheView(BaseAPIView):
    """Retorna uma DRE pelo código EOL (D04)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="DreResumoDetalhe",
                fields=_DRE_FIELDS,
            ),
            404: _PROBLEM_DETAILS_SCHEMA,
        },
        description="Retorna uma DRE pelo código EOL (D04).",
        tags=_TAG_DRE,
        operation_id="D04_detalhe_dre",
        examples=[
            OpenApiExample(
                "Resposta D04",
                value={
                    "codigoDRE": "108100",
                    "nomeDRE": "DRE IPIRANGA",
                    "siglaDRE": "DRE-IP",
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request, codigoEolDRE: str) -> Response:
        """Resposta 200 ou 404 se não encontrada."""
        dre = obter_dre_por_codigo(codigoEolDRE)
        if dre is None:
            raise NotFound("DRE não encontrada.")
        return Response(dre)


class DreEscolasTipoView(BaseAPIView):
    """Retorna escolas de uma DRE filtradas por tipo (D05)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="EscolaPorDreTipo",
                fields=_ESCOLA_FIELDS,
                many=True,
            ),
        },
        description="Escolas filtradas por tipo de escola (D05).",
        tags=_TAG_DRE,
        operation_id="D05_escolas_filtradas_por_tipo",
    )
    def get(
        self,
        _request: Request,
        codigoEolDRE: str,
        tipoEscola: str,
    ) -> Response:
        """Resposta 200 com escolas filtradas ou lista vazia."""
        if not codigoEolDRE.strip():
            raise ValidationError("Código EOL da DRE é obrigatório.")
        escolas = listar_escolas_por_dre(codigoEolDRE, tipoEscola)
        return Response(escolas)


class DreEscolasView(BaseAPIView):
    """Retorna todas as escolas de uma DRE (D06)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="EscolaPorDre",
                fields=_ESCOLA_FIELDS,
                many=True,
            ),
            204: None,
        },
        description="Escolas vinculadas a uma DRE (D06).",
        tags=_TAG_DRE,
        operation_id="D06_escolas_vinculadas_dre",
    )
    def get(self, _request: Request, codigoEolDRE: str) -> Response:
        """Resposta 200 ou 204 se a DRE não possuir escolas."""
        escolas = listar_escolas_por_dre(codigoEolDRE)
        if not escolas:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(escolas)


class DreSubprefeiturasView(BaseAPIView):
    """Retorna subprefeituras de uma DRE (D07)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="SubprefeituaDre",
                fields=_SUBPREFEITURA_FIELDS,
                many=True,
            ),
        },
        description="Subprefeituras de uma DRE (D07).",
        tags=_TAG_DRE,
        operation_id="D07_subprefeituras_dre",
    )
    def get(self, _request: Request, dreCodigo: str) -> Response:
        """Resposta 200 com subprefeituras."""
        if not dreCodigo.strip():
            raise ValidationError("Código da DRE é obrigatório.")
        return Response(listar_subprefeituras_por_dre(dreCodigo))


class DreUesView(BaseAPIView):
    """Retorna códigos das UEs de uma DRE (D08)."""

    @extend_schema(
        responses={200: inline_serializer(
            name="CodigosUesDre",
            fields={
                "codigos": serializers.ListField(
                    child=serializers.CharField()
                )
            },
        )},
        description="Códigos de UEs de uma DRE (D08).",
        tags=_TAG_DRE,
        operation_id="D08_codigos_ues_dre",
    )
    def get(self, _request: Request, dreCodigo: str) -> Response:
        """Resposta 200 com lista de códigos."""
        if not dreCodigo.strip():
            raise ValidationError("Código da DRE é obrigatório.")
        return Response(listar_codigos_ues_por_dre(dreCodigo))


class DreEscolasSigpaeView(BaseAPIView):
    """Retorna escolas SIGPAE de uma DRE (D09)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="EscolaSigpae",
                fields=_ESCOLA_FIELDS,
                many=True,
            ),
            204: None,
        },
        description="Escolas para o SIGPAE (D09).",
        tags=_TAG_DRE,
        operation_id="D09_escolas_sigpae",
    )
    def get(self, _request: Request, codigoEolDRE: str) -> Response:
        """Resposta 200 ou 204 se não houver escolas."""
        if not codigoEolDRE.strip():
            raise ValidationError("Código EOL da DRE é obrigatório.")
        escolas = listar_escolas_por_dre(codigoEolDRE)
        if not escolas:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(escolas)


class DreUnidadesView(BaseAPIView):
    """Retorna unidades completas de uma DRE (D10)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="UnidadePredial",
                fields=_UNIDADE_PREDIAL_FIELDS,
                many=True,
            ),
        },
        description="Unidades de gestão predial (D10).",
        tags=_TAG_DRE,
        operation_id="D10_unidades_gestao_predial",
    )
    def get(self, _request: Request, dreCodigo: str) -> Response:
        """Resposta 200 com dados completos das unidades."""
        return Response(listar_unidades_por_dre(dreCodigo))


class DreCodigosIntegracaoView(BaseAPIView):
    """Retorna códigos de integração das UEs da DRE (D11)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                name="CodigoIntegracao",
                fields=_CODIGO_INTEGRACAO_FIELDS,
                many=True,
            ),
        },
        description="UEs com código de integração (D11).",
        tags=_TAG_DRE,
        operation_id="D11_ues_codigo_integracao",
    )
    def get(self, _request: Request, dreCodigo: str) -> Response:
        """Resposta 200 com códigos de integração."""
        return Response(listar_codigos_integracao_por_dre(dreCodigo))


class DreSupervisoresView(BaseAPIView):
    """Cross-domain: supervisores de uma DRE (D03).

    Responsabilidade do domínio Professores via Transition Gateway.
    """

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Supervisores de uma DRE (D03). "
            "[CROSS-DOMAIN] Competência do microserviço Professores. "
            "O Transition Gateway deve redirecionar esta chamada."
        ),
        tags=_TAG_DRE,
        operation_id="D03_supervisores_dre",
    )
    def get(self, _request: Request, codigoEolDRE: str) -> Response:
        """Retorna 501 — rota de competência do domínio Professores."""
        return self.cross_domain("professores")
