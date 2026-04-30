"""Contratos de resposta EOL para o domínio DRE.

Mapeiam campos internos (snake_case) para o contrato legado (camelCase).
"""

from typing import TypedDict

from apps.core.types import SubPrefeiturarContract  # noqa: F401 — re-export


class DreResumoContract(TypedDict):
    """Contrato D01/D02/D04 — listagem e detalhe de DRE."""

    codigoDRE: str
    nomeDRE: str
    siglaDRE: str


class EscolaPorDreContract(TypedDict):
    """Contrato D05/D06/D09 — escola listada por DRE."""

    codigoEscola: str
    nomeEscola: str
    codigoDRE: str
    tipoEscola: str
    siglaTipoEscola: str
    nomeDRE: str
    siglaDRE: str
    codigoSubprefeitura: str
    nomeSubprefeitura: str
    # Campos institucionais expandidos
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
    codigoIntegracao: str | None


class UnidadePredialContract(TypedDict):
    """Contrato D10 — unidade de gestão predial."""

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
    # Campos institucionais expandidos
    subprefeituraId: int | None
    tipoUnidadeAdmId: int | None


class CodigoIntegracaoContract(TypedDict):
    """Contrato D11 — código de integração por UE."""

    codigoUe: str
    nomeUe: str
    codigoIntegracao: str | None
    # Campos institucionais expandidos
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
