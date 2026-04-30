"""Tipos e contratos compartilhados entre domínios."""

from typing import TypedDict


class SubPrefeiturarContract(TypedDict):
    """Contrato D07/E17 — subprefeitura (compartilhado entre DRE e UE)."""

    codigoSubprefeitura: str
    nomeSubprefeitura: str


class CrossDomainResponse(TypedDict):
    """Contrato padrão 501 para endpoints cross-domain (Transition Gateway)."""

    detail: str
    dominio: str
    transitionGateway: bool


class ProblemDetails(TypedDict):
    """RFC 7807 Problem Details — usado em respostas 400/404."""

    detail: str
