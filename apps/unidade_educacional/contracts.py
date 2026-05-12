"""Contratos de resposta do domínio UE.

Mapeiam campos internos (snake_case) para a representação de saída (camelCase).
"""

from typing import TypedDict


class UeBasicaContract(TypedDict):
    """Contrato E02/E06/E27 — dados básicos de UE."""

    codigoEscola: str
    nomeEscola: str
    nomeDRE: str
    siglaDRE: str
    codigoDRE: str
    tipoEscola: str
    siglaTipoEscola: str
    codigoTipoEscola: int
    # Campos institucionais expandidos
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UeEolContract(TypedDict):
    """Contrato E03 — UE por código EOL genérico."""

    codigo: str
    sigla: str | None
    nomeUnidade: str
    tipo: int | None
    codigoReferencia: str


class UeCompletaContract(TypedDict):
    """Contrato E04 — dados completos de UE."""

    nomeDRE: str
    siglaDRE: str
    codigoDRE: str
    codigoINEP: str | None
    siglaTipoEscola: str | None
    nome: str
    nomeExibicao: str | None
    codigo: str
    tipoUnidade: str | None
    email: str | None
    telefone: str | None
    tipoLogradouro: str | None
    logradouro: str | None
    numero: str | None
    bairro: str | None
    cep: int | None
    municipio: str | None
    uf: str
    tipoUnidadeAdm: int | None
    descTipoUnidadeAdm: str | None
    # Campos institucionais expandidos
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class TipoEscolaContract(TypedDict):
    """Contrato E11 — tipo de escola."""

    codigo: int
    descricaoSigla: str | None
    dtAtualizacao: str | None


class SincronizacaoUeContract(TypedDict):
    """Contrato E23 — sincronização institucional da UE.

    dreCodigo é int; dataAtualizacao é datetime ISO 8601 ou null.
    """

    ueCodigo: str
    dataAtualizacao: str | None
    dreCodigo: int | None
    ueNome: str
    tipoEscolaCodigo: int | None
    # Campos institucionais expandidos
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UnidadeParceirasContract(TypedDict):
    """Contrato E26 — unidade parceira."""

    codigo: str
    nome: str
    email: str | None


class EquipamentoContract(TypedDict):
    """Contrato E25 — equipamento/UE com filtros.

    Campos com nomenclatura prefixada (cd_*, nm_*, dc_*, sg_*) conforme
    definição do contrato E25.
    """

    cd_equipamento: str
    nm_exibicao_equipamento: str
    nm_equipamento: str
    cd_tp_equipamento: int | None
    dc_tp_equipamento: str | None
    cd_tp_escola: int | None
    dc_tipo_escola: str | None
    sg_tp_escola: str | None
    cd_diretoria_referencia: str
    nm_diretoria_referencia: str
    cd_diretoria_portal: str
    nm_diretoria_portal: str
    nm_exibicao_diretoria_portal: str | None
    nm_exibicao_diretoria_referencia: str | None
    cd_logradouro: int | None
    logradouro: str | None
    bairro: str | None
    codigoSubprefeitura: str | None
    nomeSubprefeitura: str | None
    ehCeu: bool
