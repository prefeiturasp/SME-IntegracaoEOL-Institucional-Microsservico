"""Contratos de resposta do domínio DRE."""

from typing import TypedDict

from apps.core.types import SubPrefeiturarContract  # noqa: F401 — re-export


class DreResumoContract(TypedDict):
    """Dados resumidos de Diretoria Regional de Educação.

    Attributes:
        codigoDRE: Código EOL da DRE.
        nomeDRE: Nome completo da DRE.
        siglaDRE: Sigla da DRE.
    """

    codigoDRE: str
    nomeDRE: str
    siglaDRE: str


class DreNomeAbreviacaoContract(TypedDict):
    """Dados de identificação de uma Diretoria Regional de Educação.

    Attributes:
        codigo: Código EOL da DRE.
        nome: Nome completo da DRE.
        abreviacao: Nome abreviado da DRE, quando disponível.
    """

    codigo: str
    nome: str
    abreviacao: str | None


class EscolaPorDreContract(TypedDict):
    """Dados de escola vinculada a uma DRE.

    Attributes:
        codigoEscola: Código EOL da escola.
        nomeEscola: Nome da escola.
        codigoDRE: Código EOL da DRE.
        tipoEscola: Descrição do tipo de escola.
        siglaTipoEscola: Sigla do tipo de escola.
        nomeDRE: Nome da DRE.
        siglaDRE: Sigla da DRE.
        codigoSubprefeitura: Código da subprefeitura como string.
        nomeSubprefeitura: Nome da subprefeitura.
        tipoEscolaId: Código numérico do tipo de escola.
        tipoUnidadeId: Código numérico do tipo de unidade (igual a tipoEscolaId).
        subprefeituraId: Código numérico da subprefeitura.
        dreId: Código EOL da DRE (igual a codigoDRE).
        codigoIntegracao: Código de integração externo, ou None.
    """

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
    """Dados completos de unidade predial.

    Attributes:
        codigoEol: Código EOL da unidade.
        nomeOficial: Nome oficial da unidade.
        nomeNaoOficial: Nome não oficial (sigla/apelido), ou None.
        tipoUnidadeAdmin: Descrição do tipo de unidade administrativa da DRE, ou None.
        tipoUE: Descrição do tipo de escola, ou None.
        logadouro: Logradouro do endereço, ou None.
        numero: Número do endereço, ou None.
        bairro: Bairro, ou None.
        cep: CEP como inteiro sem formatação, ou None.
        distrito: Distrito, ou None.
        subPrefeitura: Nome da subprefeitura, ou None.
        nomeDre: Nome da DRE.
        email: E-mail de contato, ou None.
        telefone1: Telefone principal, ou None.
        telefone2: Telefone secundário, ou None.
        anoConstrucao: Ano de construção, ou None.
        propriedade: Tipo de propriedade do imóvel, ou None.
        capacidadeVagasMatutino: Vagas no período matutino.
        capacidadeVagasVespertino: Vagas no período vespertino.
        capacidadeVagasNoturno: Vagas no período noturno.
        capacidadeVagasIntermediario: Vagas no período intermediário.
        capacidadeVagasIntegral: Vagas no período integral.
        capacidadeVagasTotal: Total de vagas.
        organizacaoParceira: Indica se é organização parceira.
        quantidadeDeFuncionarios: Quantidade de funcionários.
        status: Status da unidade, ou None.
        subprefeituraId: Código numérico da subprefeitura, ou None.
        tipoUnidadeAdmId: Código numérico do tipo de unidade administrativa da DRE, ou None.
    """

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
    subprefeituraId: int | None
    tipoUnidadeAdmId: int | None


class CodigoIntegracaoContract(TypedDict):
    """Dados de código de integração de uma UE.

    Attributes:
        codigoUe: Código EOL da unidade.
        nomeUe: Nome da unidade.
        codigoIntegracao: Código de integração externo, ou None.
        tipoEscolaId: Código numérico do tipo de escola.
        tipoUnidadeId: Código numérico do tipo de unidade (igual a tipoEscolaId).
        subprefeituraId: Código numérico da subprefeitura.
        dreId: Código EOL da DRE.
    """

    codigoUe: str
    nomeUe: str
    codigoIntegracao: str | None
    tipoEscolaId: int | None
    tipoUnidadeId: int | None
    subprefeituraId: int | None
    dreId: str
