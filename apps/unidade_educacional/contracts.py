"""Contratos de resposta do domínio UE."""

from typing import TypedDict


class UeBasicaContract(TypedDict):
    """Dados básicos de unidade educacional."""

    codigoEscola: str
    nomeEscola: str
    nomeDRE: str
    siglaDRE: str
    codigoDRE: str
    tipoEscola: str
    siglaTipoEscola: str
    codigoTipoEscola: int
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UeEolContract(TypedDict):
    """Dados resumidos de unidade educacional por código EOL."""

    codigo: str
    sigla: str | None
    nomeUnidade: str
    tipo: int | None
    codigoReferencia: str


class UeCompletaContract(TypedDict):
    """Dados completos de unidade educacional."""

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
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UeRecorteContract(TypedDict):
    """Dados de UE no recorte de tipo de escola (Fund/Médio).

    Campos usados na composição de turmas atribuídas ao professor
    (escola + DRE + tipo).
    """

    codigo: str
    nome: str
    nomeExibicao: str | None
    tipoUnidade: str | None
    codigoTipoUnidadeEducacao: int | None
    codigoTipoEscola: int | None
    siglaTipoEscola: str | None
    codigoDRE: str
    nomeDRE: str
    siglaDRE: str


class TipoEscolaContract(TypedDict):
    """Dados de tipo de escola."""

    codigo: int
    descricaoSigla: str | None
    dtAtualizacao: str | None


class SincronizacaoUeContract(TypedDict):
    """Dados de sincronização institucional da unidade educacional."""

    ueCodigo: str
    dataAtualizacao: str | None
    dreCodigo: int | None
    ueNome: str
    tipoEscolaCodigo: int | None
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UnidadeParceirasContract(TypedDict):
    """Dados de unidade educacional parceira."""

    codigo: str
    nome: str
    email: str | None


class EquipamentoContract(TypedDict):
    """Dados de equipamento escolar com nomenclatura prefixada."""

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
