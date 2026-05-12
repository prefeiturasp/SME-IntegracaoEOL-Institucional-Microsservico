"""Views do domínio UE (E01-E27)."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import BaseAPIView, _CROSS_DOMAIN_SCHEMA, _PROBLEM_DETAILS_SCHEMA
from apps.unidade_educacional.contracts import (
    EquipamentoContract,
    SincronizacaoUeContract,
    TipoEscolaContract,
    UeBasicaContract,
    UeCompletaContract,
    UeEolContract,
    UnidadeParceirasContract,
)
from apps.unidade_educacional.selectors import (
    listar_equipamentos,
    listar_tipos_escolas,
    listar_ues_basicas,
    listar_unidades_parceiras,
    obter_subprefeituras_ue,
    obter_sincronizacao_ue,
    obter_ue_basica_por_codigo,
    obter_ue_completa,
    obter_ue_eol,
)

_TAG_UE = ["Escola"]
_TAG_CD = ["CrossDomain"]

_MSG_UNIDADE_NAO_ENCONTRADA = "Unidade não encontrada."

# Dicts de fields para reutilização nos inline_serializer com many=True
_UE_BASICA_FIELDS = {
    "codigoEscola": serializers.CharField(),
    "nomeEscola": serializers.CharField(),
    "nomeDRE": serializers.CharField(),
    "siglaDRE": serializers.CharField(),
    "codigoDRE": serializers.CharField(),
    "tipoEscola": serializers.CharField(),
    "siglaTipoEscola": serializers.CharField(),
    "codigoTipoEscola": serializers.IntegerField(),
    "tipoEscolaId": serializers.IntegerField(allow_null=True),
    "tipoUnidadeId": serializers.IntegerField(allow_null=True),
    "subprefeituraId": serializers.IntegerField(allow_null=True),
    "dreId": serializers.CharField(),
    "codigoIntegracao": serializers.CharField(allow_null=True),
}

_UE_EOL_FIELDS = {
    "codigo": serializers.CharField(),
    "sigla": serializers.CharField(allow_null=True),
    "nomeUnidade": serializers.CharField(),
    "tipo": serializers.IntegerField(allow_null=True),
    "codigoReferencia": serializers.CharField(),
}

_UE_COMPLETA_FIELDS = {
    "nomeDRE": serializers.CharField(),
    "siglaDRE": serializers.CharField(),
    "codigoDRE": serializers.CharField(),
    "codigoINEP": serializers.CharField(allow_null=True),
    "siglaTipoEscola": serializers.CharField(allow_null=True),
    "nome": serializers.CharField(),
    "nomeExibicao": serializers.CharField(allow_null=True),
    "codigo": serializers.CharField(),
    "tipoUnidade": serializers.CharField(allow_null=True),
    "email": serializers.CharField(allow_null=True),
    "telefone": serializers.CharField(allow_null=True),
    "tipoLogradouro": serializers.CharField(allow_null=True),
    "logradouro": serializers.CharField(allow_null=True),
    "numero": serializers.CharField(allow_null=True),
    "bairro": serializers.CharField(allow_null=True),
    "cep": serializers.IntegerField(allow_null=True),
    "municipio": serializers.CharField(allow_null=True),
    "uf": serializers.CharField(),
    "tipoUnidadeAdm": serializers.IntegerField(allow_null=True),
    "descTipoUnidadeAdm": serializers.CharField(allow_null=True),
    "tipoEscolaId": serializers.IntegerField(allow_null=True),
    "tipoUnidadeId": serializers.IntegerField(allow_null=True),
    "subprefeituraId": serializers.IntegerField(allow_null=True),
    "dreId": serializers.CharField(),
    "codigoIntegracao": serializers.CharField(allow_null=True),
}

_TIPO_ESCOLA_FIELDS = {
    "codigo": serializers.IntegerField(),
    "descricaoSigla": serializers.CharField(allow_null=True),
    "dtAtualizacao": serializers.CharField(allow_null=True),
}

_SUBPREFEITURA_FIELDS = {
    "codigoSubprefeitura": serializers.CharField(),
    "nomeSubprefeitura": serializers.CharField(),
}

_SINCRONIZACAO_UE_FIELDS = {
    "ueCodigo": serializers.CharField(),
    "dataAtualizacao": serializers.CharField(allow_null=True),
    "dreCodigo": serializers.IntegerField(allow_null=True),
    "ueNome": serializers.CharField(),
    "tipoEscolaCodigo": serializers.IntegerField(allow_null=True),
    "tipoEscolaId": serializers.IntegerField(allow_null=True),
    "tipoUnidadeId": serializers.IntegerField(allow_null=True),
    "subprefeituraId": serializers.IntegerField(allow_null=True),
    "dreId": serializers.CharField(),
    "codigoIntegracao": serializers.CharField(allow_null=True),
}

_EQUIPAMENTO_FIELDS = {
    "cd_equipamento": serializers.CharField(),
    "nm_exibicao_equipamento": serializers.CharField(),
    "nm_equipamento": serializers.CharField(),
    "cd_tp_equipamento": serializers.IntegerField(allow_null=True),
    "dc_tp_equipamento": serializers.CharField(allow_null=True),
    "cd_tp_escola": serializers.IntegerField(allow_null=True),
    "dc_tipo_escola": serializers.CharField(allow_null=True),
    "sg_tp_escola": serializers.CharField(allow_null=True),
    "cd_diretoria_referencia": serializers.CharField(),
    "nm_diretoria_referencia": serializers.CharField(),
    "cd_diretoria_portal": serializers.CharField(),
    "nm_diretoria_portal": serializers.CharField(),
    "nm_exibicao_diretoria_portal": serializers.CharField(allow_null=True),
    "nm_exibicao_diretoria_referencia": serializers.CharField(allow_null=True),
    "cd_logradouro": serializers.CharField(allow_null=True),
    "logradouro": serializers.CharField(allow_null=True),
    "bairro": serializers.CharField(allow_null=True),
    "codigoSubprefeitura": serializers.CharField(allow_null=True),
    "nomeSubprefeitura": serializers.CharField(allow_null=True),
    "ehCeu": serializers.BooleanField(),
}

_UNIDADE_PARCEIRA_FIELDS = {
    "codigo": serializers.CharField(),
    "nome": serializers.CharField(),
    "email": serializers.CharField(allow_null=True),
}

_TIPO_UNIDADE_EDUCACAO_FIELDS = {
    "sigla": serializers.CharField(),
    "descricao": serializers.CharField(),
}


def _paginar_ues_basicas(request: Request) -> Response:
    """Valida limite/offset e retorna página de UEs básicas."""
    try:
        limite = int(request.query_params.get("limite", 100))
        offset = int(request.query_params.get("offset", 0))
    except (ValueError, TypeError) as exc:
        raise ValidationError(
            "Os parâmetros 'limite' e 'offset' devem ser inteiros."
        ) from exc
    if limite < 1 or limite > 1000:
        raise ValidationError(
            "O parâmetro 'limite' deve estar entre 1 e 1000."
        )
    if offset < 0:
        raise ValidationError("O parâmetro 'offset' não pode ser negativo.")
    items, total = listar_ues_basicas(limite=limite, offset=offset)
    return Response({"count": total, "results": items})


class UnidadeEducacionalAdminSgpView(BaseAPIView):
    """Administradores SGP de uma UE (E01) — placeholder cross-domain."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Logins/RFs de administradores SGP da UE (E01). "
            "[CROSS-DOMAIN] Dados não disponíveis no ETL institucional. "
            "Competência do microserviço Professores/SSO via Transition Gateway."
        ),
        tags=_TAG_CD,
        operation_id="E01_administrador_sgp",
    )
    def get(self, _request: Request, codigo_ue: str) -> Response:
        """Retorna 501 — competência de outro domínio."""
        return self.cross_domain("professores")


class UnidadeEducacionalDetalheView(BaseAPIView):
    """Dados básicos de uma UE por código EOL (E02).

    Retorna objeto único identificado pelo código da UE.
    """

    @extend_schema(
        responses={
            200: inline_serializer(
                "UeBasicaDetalhe", fields=_UE_BASICA_FIELDS
            ),
            400: _PROBLEM_DETAILS_SCHEMA,
            404: _PROBLEM_DETAILS_SCHEMA,
        },
        description="Dados básicos de uma UE (E02).",
        tags=_TAG_UE,
        operation_id="E02_dados_basicos_ue",
        examples=[
            OpenApiExample(
                "Resposta E02",
                value={
                    "codigoEscola": "019251",
                    "nomeEscola": "EMEF EXEMPLO",
                    "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
                    "siglaDRE": "DRE-IP",
                    "codigoDRE": "108100",
                    "tipoEscola": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
                    "siglaTipoEscola": "EMEF",
                    "codigoTipoEscola": 1,
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request, codigo_escola_eol: str) -> Response:
        """Resposta 200 (objeto único) ou 404."""
        if not codigo_escola_eol.strip():
            raise ValidationError("Código da unidade EOL é obrigatório.")
        ue = obter_ue_basica_por_codigo(codigo_escola_eol)
        if ue is None:
            raise NotFound(_MSG_UNIDADE_NAO_ENCONTRADA)
        return Response(ue)


class UnidadeEolView(BaseAPIView):
    """UE resumida por código EOL genérico (E03)."""

    @extend_schema(
        responses={
            200: inline_serializer("UeEol", fields=_UE_EOL_FIELDS),
            404: _PROBLEM_DETAILS_SCHEMA,
        },
        description="UE por código EOL (E03).",
        tags=_TAG_UE,
        operation_id="E03_ue_codigo_eol",
        examples=[
            OpenApiExample(
                "Resposta E03",
                value={
                    "codigo": "019251",
                    "sigla": "EMEF",
                    "nomeUnidade": "EMEF EXEMPLO",
                    "tipo": 1,
                    "codigoReferencia": "019251",
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request, codigo_eol: str) -> Response:
        """Resposta 200 ou 404."""
        ue = obter_ue_eol(codigo_eol)
        if ue is None:
            raise NotFound("Unidade EOL não encontrada.")
        return Response(ue)


class DadosUnidadeEducacionalView(BaseAPIView):
    """Dados completos de uma UE (E04)."""

    @extend_schema(
        responses={
            200: inline_serializer("UeCompleta", fields=_UE_COMPLETA_FIELDS),
            404: _PROBLEM_DETAILS_SCHEMA,
        },
        description="Dados completos de uma UE (E04).",
        tags=_TAG_UE,
        operation_id="E04_dados_completos_ue",
        examples=[
            OpenApiExample(
                "Resposta E04",
                value={
                    "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
                    "siglaDRE": "DRE-IP",
                    "codigoDRE": "108100",
                    "codigoINEP": "35123456",
                    "siglaTipoEscola": "EMEF",
                    "nome": "EMEF EXEMPLO",
                    "nomeExibicao": "Escola do Bairro",
                    "codigo": "019251",
                    "tipoUnidade": "EMEF",
                    "email": "emef@sme.prefeitura.sp.gov.br",
                    "telefone": "1133330000",
                    "tipoLogradouro": "RUA",
                    "logradouro": "RUA DE EXEMPLO",
                    "numero": "100",
                    "bairro": "IPIRANGA",
                    "cep": 4218050,
                    "municipio": "SAO PAULO",
                    "uf": "SP",
                    "tipoUnidadeAdm": 24,
                    "descTipoUnidadeAdm": "DIRETORIA REGIONAL DE EDUCACAO",
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request, codigo_escola_eol: str) -> Response:
        """Resposta 200 ou 404."""
        dados = obter_ue_completa(codigo_escola_eol)
        if dados is None:
            raise NotFound("Dados da unidade não encontrados.")
        return Response(dados)


class QuantidadeAlunosView(BaseAPIView):
    """Quantidade de alunos de uma UE (E05) — cross-domain Alunos."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description=(
            "Quantidade de alunos de uma UE (E05). "
            "[CROSS-DOMAIN] Competência do microserviço Alunos."
        ),
        tags=_TAG_CD,
        operation_id="E05_quantidade_alunos_ue",
    )
    def get(self, _request: Request, codigo_escola: str) -> Response:
        """Retorna 501 — competência do domínio Alunos."""
        return self.cross_domain("alunos")


class UnidadeEducacionalListPostView(BaseAPIView):
    """Busca UEs: GET lista todas paginado (E27b), POST filtra por lista (E06)."""

    @extend_schema(
        parameters=[
            OpenApiParameter("limite", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Itens por página (padrão 100)."),
            OpenApiParameter("offset", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Posição inicial (padrão 0)."),
        ],
        responses={200: inline_serializer(
            "UeBasicaRaizPaginado",
            fields={
                "count": serializers.IntegerField(),
                "results": inline_serializer("UeBasicaRaiz", fields=_UE_BASICA_FIELDS, many=True),
            },
        )},
        description="Lista todas as UEs paginadas (GET raiz). Use `limite` e `offset` para navegar.",
        tags=_TAG_UE,
        operation_id="E27b_lista_todas_ues_raiz",
    )
    def get(self, request: Request) -> Response:
        """Resposta 200 com página de unidades e total."""
        return _paginar_ues_basicas(request)

    @extend_schema(
        request={"application/json": {"type": "array", "items": {"type": "string"}}},
        responses={
            200: inline_serializer(
                "UeBasicaFiltrada", fields=_UE_BASICA_FIELDS, many=True
            ),
            400: _PROBLEM_DETAILS_SCHEMA,
        },
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
        """Resposta 200 ou 400."""
        codigos = request.data
        if not isinstance(codigos, list) or not codigos:
            raise ValidationError(
                "Lista de códigos é obrigatória e não pode ser vazia."
            )
        items, _ = listar_ues_basicas(codigos)
        return Response(items)


class ProfessoresEscolaAnoView(BaseAPIView):
    """Professores de uma escola por ano letivo (E07) — cross-domain."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E07).",
        tags=_TAG_CD,
        operation_id="E07_professores_escola_ano",
    )
    def get(self, _request: Request, codigo_eol_escola: str, ano_letivo: str) -> Response:
        return self.cross_domain("professores")


class ProfessoresEscolaView(BaseAPIView):
    """Professores de uma escola (E08) — cross-domain."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E08).",
        tags=_TAG_CD,
        operation_id="E08_professores_escola",
    )
    def get(self, _request: Request, codigo_eol_escola: str) -> Response:
        return self.cross_domain("professores")


class ModalidadesEnsinoView(BaseAPIView):
    """Modalidades de ensino (E09) — cross-domain Pedagógico."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Pedagógico (E09).",
        tags=_TAG_CD,
        operation_id="E09_modalidades_ensino",
    )
    def get(self, _request: Request) -> Response:
        return self.cross_domain("pedagogico")


class TiposUnidadeEducacaoView(BaseAPIView):
    """Tipos de unidade de educação (E10).

    Retorna array de strings com os nomes completos dos tipos de escola
    (somente descrição).

    """

    @extend_schema(
        responses={200: inline_serializer(
            "TipoUnidadeEducacao",
            fields={"$value": serializers.CharField()},
            many=True,
        )},
        description="Tipos de unidade de educação (E10). Retorna array de strings com nomes dos tipos de escola.",
        tags=_TAG_UE,
        operation_id="E10_tipos_unidade_educacional",
    )
    def get(self, _request: Request) -> Response:
        """Retorna lista de nomes de tipos de escola."""
        from apps.dre.models import TipoEscola

        descricoes = (
            TipoEscola.objects.exclude(descricao__isnull=True)
            .values_list("descricao", flat=True)
            .order_by("codigo_tipo_escola")
        )
        return Response(list(descricoes))


class TiposEscolasView(BaseAPIView):
    """Tipos de escola com código e sigla (E11)."""

    @extend_schema(
        responses={200: inline_serializer(
            "TipoEscolaList", fields=_TIPO_ESCOLA_FIELDS, many=True
        )},
        description="Código e sigla de tipos de escola (E11).",
        tags=_TAG_UE,
        operation_id="E11_codigo_sigla_tipos_escola",
    )
    def get(self, _request: Request) -> Response:
        """Resposta 200 com lista de tipos."""
        return Response(listar_tipos_escolas())


class SalasAnoLetivoView(BaseAPIView):
    """Salas de uma UE por tipo e ano letivo (E12) — cross-domain Pedagógico."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Pedagógico (E12).",
        tags=_TAG_CD,
        operation_id="E12_salas_ue_ano_letivo",
    )
    def get(
        self,
        _request: Request,
        codigo_ue: str,
        tipo_sala: str,
        ano_letivo: str,
    ) -> Response:
        return self.cross_domain("pedagogico")


class FuncionariosUeView(BaseAPIView):
    """Funcionários de uma UE (E13) — cross-domain Professores."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E13).",
        tags=_TAG_CD,
        operation_id="E13_funcionarios_ue",
    )
    def get(self, _request: Request, codigo_ue: str) -> Response:
        return self.cross_domain("professores")


class FuncionariosCargoView(BaseAPIView):
    """Funcionários por cargo (E14) — cross-domain Professores."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E14).",
        tags=_TAG_CD,
        operation_id="E14_funcionarios_cargo",
    )
    def get(
        self, _request: Request, codigo_ue: str, codigo_cargo: str
    ) -> Response:
        return self.cross_domain("professores")


class FuncionariosFuncaoExternaView(BaseAPIView):
    """Funcionários por função externa (E15) — cross-domain Professores."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E15).",
        tags=_TAG_CD,
        operation_id="E15_funcionarios_funcao_externa",
    )
    def get(
        self, _request: Request, codigo_ue: str, codigo_funcao_externa: str
    ) -> Response:
        return self.cross_domain("professores")


class FuncionariosFuncaoAtividadeView(BaseAPIView):
    """Funcionários por função atividade (E16) — cross-domain Professores."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E16).",
        tags=_TAG_CD,
        operation_id="E16_funcionarios_funcao_atividade",
    )
    def get(
        self, _request: Request, codigo_ue: str, codigo_funcao_atividade: str
    ) -> Response:
        return self.cross_domain("professores")


class SubprefeituraUnidadeEducacionalView(BaseAPIView):
    """Subprefeituras da unidade (E17)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                "SubprefeituraUe", fields=_SUBPREFEITURA_FIELDS, many=True
            ),
            404: _PROBLEM_DETAILS_SCHEMA,
        },
        description="Subprefeituras da unidade (E17).",
        tags=_TAG_UE,
        operation_id="E17_subprefeituras_ue",
    )
    def get(self, _request: Request, codigo_escola_eol: str) -> Response:
        """Resposta 200 ou 404."""
        subs = obter_subprefeituras_ue(codigo_escola_eol)
        if subs is None:
            raise NotFound(_MSG_UNIDADE_NAO_ENCONTRADA)
        return Response(subs)


class TurmasAnoLetivoView(BaseAPIView):
    """Turmas de uma UE por ano letivo (E18) — cross-domain Pedagógico."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Pedagógico (E18).",
        tags=_TAG_CD,
        operation_id="E18_turmas_ue_ano_letivo",
    )
    def get(self, _request: Request, codigo_ue: str, ano_letivo: str) -> Response:
        return self.cross_domain("pedagogico")


class TurmasSondagemAnoLetivoView(BaseAPIView):
    """Turmas sondagem de uma UE por ano letivo (E19) — cross-domain Pedagógico."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Pedagógico (E19).",
        tags=_TAG_CD,
        operation_id="E19_turmas_sondagem_ue_ano_letivo",
    )
    def get(self, _request: Request, codigo_ue: str, ano_letivo: str) -> Response:
        return self.cross_domain("pedagogico")


class FuncionariosCargosListView(BaseAPIView):
    """Lista de cargos dos funcionários de uma UE (E20) — cross-domain Professores."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "anoLetivo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ano letivo para filtro de cargos.",
            ),
        ],
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E20).",
        tags=_TAG_CD,
        operation_id="E20_funcionarios_cargos_lista",
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        return self.cross_domain("professores")


class FuncionariosFuncoesAtividadesListView(BaseAPIView):
    """Lista funções-atividades de funcionários de UE (E21) — cross-domain Professores."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "anoLetivo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ano letivo para filtro de funções-atividades.",
            ),
        ],
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E21).",
        tags=_TAG_CD,
        operation_id="E21_funcionarios_funcoes_atividades_lista",
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        return self.cross_domain("professores")


class FuncionariosFuncoesExternasListView(BaseAPIView):
    """Lista funções-externas de funcionários de UE (E22) — cross-domain Professores."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "anoLetivo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ano letivo para filtro de funções-externas.",
            ),
        ],
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Professores (E22).",
        tags=_TAG_CD,
        operation_id="E22_funcionarios_funcoes_externas_lista",
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        return self.cross_domain("professores")


class SincronizacaoUnidadeEducacionalView(BaseAPIView):
    """Sincronização institucional da UE (E23)."""

    @extend_schema(
        responses={
            200: inline_serializer(
                "SincronizacaoUe", fields=_SINCRONIZACAO_UE_FIELDS
            ),
            404: _PROBLEM_DETAILS_SCHEMA,
        },
        description="Detalhes de sincronização institucional da UE (E23).",
        tags=_TAG_UE,
        operation_id="E23_detalhes_sincronizacao_institucional_ue",
        examples=[
            OpenApiExample(
                "Resposta E23",
                value={
                    "ueCodigo": "019251",
                    "dataAtualizacao": None,
                    "dreCodigo": "108100",
                    "ueNome": "EMEF EXEMPLO",
                    "tipoEscolaCodigo": 1,
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        """Resposta 200 ou 404."""
        dados = obter_sincronizacao_ue(ue_codigo)
        if dados is None:
            raise NotFound(_MSG_UNIDADE_NAO_ENCONTRADA)
        return Response(dados)


class MatriculasAlunoView(BaseAPIView):
    """Matrículas de aluno em escola (E24) — cross-domain Alunos."""

    @extend_schema(
        responses={501: _CROSS_DOMAIN_SCHEMA},
        description="[CROSS-DOMAIN] Competência do microserviço Alunos (E24).",
        tags=_TAG_CD,
        operation_id="E24_matriculas_aluno_escola",
    )
    def get(
        self, _request: Request, codigo_escola: str, codigo_aluno: str
    ) -> Response:
        return self.cross_domain("alunos")


class EquipamentosView(BaseAPIView):
    """Equipamentos/UEs com filtros (E25)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "codigosSubprefeitura",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                many=True,
            ),
            OpenApiParameter(
                "codigosDre",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                many=True,
            ),
            OpenApiParameter(
                "tiposUnidade",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                many=True,
            ),
            OpenApiParameter(
                "tiposEscola",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                many=True,
            ),
            OpenApiParameter(
                "nomeEscola", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "codigoEol", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: inline_serializer(
            "EquipamentoList", fields=_EQUIPAMENTO_FIELDS, many=True
        )},
        description="Equipamentos SME com filtros (E25).",
        tags=_TAG_UE,
        operation_id="E25_equipamentos_sme_filtro",
    )
    def get(self, request: Request) -> Response:
        """Resposta 200 com equipamentos filtrados."""
        def _parse_ints(key: str) -> list[int] | None:
            vals = request.query_params.getlist(key)
            if not vals:
                return None
            try:
                return [int(v) for v in vals]
            except ValueError:
                raise ValidationError(f"Parâmetro '{key}' deve conter inteiros.")

        def _parse_strs(key: str) -> list[str] | None:
            vals = request.query_params.getlist(key)
            return vals if vals else None

        return Response(
            listar_equipamentos(
                codigos_subprefeitura=_parse_ints("codigosSubprefeitura"),
                codigos_dre=_parse_strs("codigosDre"),
                tipos_unidade=_parse_ints("tiposUnidade"),
                tipos_escola=_parse_ints("tiposEscola"),
                nome_escola=request.query_params.get("nomeEscola"),
                codigo_eol=request.query_params.get("codigoEol"),
            )
        )


class UnidadesParceirasView(BaseAPIView):
    """Unidades parceiras por lista de códigos (E26) — POST."""

    @extend_schema(
        request={"application/json": {"type": "array", "items": {"type": "string"}}},
        responses={
            200: inline_serializer(
                "UnidadeParceiraList",
                fields=_UNIDADE_PARCEIRA_FIELDS,
                many=True,
            ),
            400: _PROBLEM_DETAILS_SCHEMA,
        },
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
        """Resposta 200 ou 400."""
        codigos = request.data
        if not isinstance(codigos, list) or not codigos:
            raise ValidationError(
                "Lista de códigos é obrigatória e não pode ser vazia."
            )
        return Response(listar_unidades_parceiras(codigos))


class TodasUnidadesView(BaseAPIView):
    """Todas as UEs (E27) — paginado por limite/offset."""

    @extend_schema(
        parameters=[
            OpenApiParameter("limite", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Itens por página (padrão 100)."),
            OpenApiParameter("offset", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Posição inicial (padrão 0)."),
        ],
        responses={
            200: inline_serializer(
                "UeBasicaTodasPaginado",
                fields={
                    "count": serializers.IntegerField(),
                    "results": inline_serializer("UeBasicaTodasList", fields=_UE_BASICA_FIELDS, many=True),
                },
            )
        },
        description="Lista todas as UEs paginadas (E27). Use `limite` e `offset` para navegar.",
        tags=_TAG_UE,
        operation_id="E27_lista_todas_ues",
    )
    def get(self, request: Request) -> Response:
        """Resposta 200 com página de unidades e total."""
        return _paginar_ues_basicas(request)
