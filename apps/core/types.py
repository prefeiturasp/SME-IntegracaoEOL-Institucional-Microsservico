"""Tipos compartilhados entre domínios."""

from typing import TypedDict


class SubPrefeiturarContract(TypedDict):
    """Dados de subprefeitura."""

    codigoSubprefeitura: str
    nomeSubprefeitura: str


class CrossDomainResponse(TypedDict):
    """Resposta padrão para endpoints de responsabilidade de outro domínio."""

    detail: str
    dominio: str
    transitionGateway: bool


class ProblemDetails(TypedDict):
    """Detalhe de erro em respostas de falha."""

    detail: str
