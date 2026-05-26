"""Contratos de resposta do domínio DRE."""

from typing import TypedDict

from apps.core.types import SubPrefeiturarContract  # noqa: F401 — re-export


class DreResumoContract(TypedDict):
    """Dados resumidos de Diretoria Regional de Educação."""

    codigoDRE: str
    nomeDRE: str
    siglaDRE: str


class EscolaPorDreContract(TypedDict):
    """Dados de escola vinculada a uma DRE."""

    codigoEscola: str
    nomeEscola: str
    codigoDRE: str
    tipoEscola: str
    siglaTipoEscola: str
    nomeDRE: str
    siglaDRE: str
    codigoSubprefeitura: str
    nomeSubprefeitura: str
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UnidadePredialContract(TypedDict):
    """Dados completos de unidade predial."""

    codigoEol: str
    nomeOficial: str
    nomeNaoOficial: str | None
    tipoUnidadeAdmin: str | None
    tipoUE: str | None
    logadouro: str | None
    numero: str | None
    bairro: str | None
    cep: int | None
    distrito: str | None
    subPrefeitura: str | None
    nomeDre: str
    email: str | None
    telefone1: str | None
    telefone2: str | None
    anoConstrucao: int | None
    propriedade: str | None
    capacidadeVagasMatutino: int
    capacidadeVagasVespertino: int
    capacidadeVagasNoturno: int
    capacidadeVagasIntermediario: int
    capacidadeVagasIntegral: int
    capacidadeVagasTotal: int
    organizacaoParceira: bool
    quantidadeDeFuncionarios: int
    status: str | None


class CodigoIntegracaoContract(TypedDict):
    """Dados de código de integração de uma UE."""

    codigoUe: str
    nomeUe: str
    codigoIntegracao: str | None
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
