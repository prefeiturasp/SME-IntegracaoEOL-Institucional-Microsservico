"""Selectors do domínio DRE — queries otimizadas, sem N+1."""

from typing import Any

from apps.core.types import SubPrefeiturarContract
from apps.dre.contracts import (
    CodigoIntegracaoContract,
    DreResumoContract,
    EscolaPorDreContract,
    UnidadePredialContract,
)
from apps.dre.models import DRE, SubPrefeitura
from apps.unidade_educacional.models import UnidadeEducacional

# --- DRE ---


def listar_dres() -> list[DreResumoContract]:
    """Retorna todas as DREs com campos mínimos do contrato EOL."""
    qs = DRE.objects.only("codigo_dre", "nome", "sigla").order_by("nome")
    return [
        DreResumoContract(
            codigoDRE=d.codigo_dre,
            nomeDRE=d.nome,
            siglaDRE=d.sigla or "",
        )
        for d in qs
    ]


def filtrar_dres_por_codigos(
    codigos: list[str],
) -> list[DreResumoContract]:
    """Filtra DREs pela lista de códigos."""
    qs = DRE.objects.filter(codigo_dre__in=codigos).only(
        "codigo_dre", "nome", "sigla"
    )
    return [
        DreResumoContract(
            codigoDRE=d.codigo_dre,
            nomeDRE=d.nome,
            siglaDRE=d.sigla or "",
        )
        for d in qs
    ]


def obter_dre_por_codigo(codigo: str) -> DreResumoContract | None:
    """Retorna uma DRE pelo código ou None se não existir."""
    try:
        d = DRE.objects.only("codigo_dre", "nome", "sigla").get(
            codigo_dre=codigo
        )
    except DRE.DoesNotExist:
        return None
    return DreResumoContract(
        codigoDRE=d.codigo_dre,
        nomeDRE=d.nome,
        siglaDRE=d.sigla or "",
    )


# --- Subprefeituras ---


def listar_subprefeituras_por_dre(
    codigo_dre: str,
) -> list[SubPrefeiturarContract]:
    """Lista subprefeituras distintas das UEs de uma DRE."""
    ids = (
        UnidadeEducacional.objects.filter(codigo_dre=codigo_dre)
        .exclude(codigo_sub_prefeitura__isnull=True)
        .values_list("codigo_sub_prefeitura", flat=True)
        .distinct()
    )
    qs = SubPrefeitura.objects.filter(
        codigo_sub_prefeitura__in=ids
    ).only("codigo_sub_prefeitura", "nome")
    return [
        SubPrefeiturarContract(
            codigoSubprefeitura=str(s.codigo_sub_prefeitura),
            nomeSubprefeitura=s.nome,
        )
        for s in qs
    ]


# --- Escolas por DRE ---


def _ue_rows_por_dre(
    codigo_dre: str, tipo_escola_sigla: str | None = None
) -> Any:
    """QuerySet de UEs por DRE com todos os dados de join em memória."""
    qs = UnidadeEducacional.objects.filter(codigo_dre=codigo_dre).values(
        "codigo_ue",
        "nome",
        "codigo_dre",
        "codigo_tipo_escola",
        "codigo_sub_prefeitura",
        "codigo_ue_integracao",
    )
    if tipo_escola_sigla:
        # join via subquery de TipoEscola
        from apps.dre.models import TipoEscola

        ids = TipoEscola.objects.filter(
            sigla__iexact=tipo_escola_sigla
        ).values_list("codigo_tipo_escola", flat=True)
        qs = qs.filter(codigo_tipo_escola__in=ids)
    return qs


def listar_escolas_por_dre(
    codigo_dre: str, tipo_escola_sigla: str | None = None
) -> list[EscolaPorDreContract]:
    """Escolas de uma DRE com dados de TipoEscola, DRE e SubPrefeitura."""
    from apps.dre.models import TipoEscola

    # Carrega lookups em memória para evitar N+1
    try:
        dre_obj = DRE.objects.only("codigo_dre", "nome", "sigla").get(
            codigo_dre=codigo_dre
        )
    except DRE.DoesNotExist:
        return []

    rows = list(_ue_rows_por_dre(codigo_dre, tipo_escola_sigla))
    if not rows:
        return []

    tipo_ids = {r["codigo_tipo_escola"] for r in rows if r["codigo_tipo_escola"]}
    tipos = {
        t.codigo_tipo_escola: t
        for t in TipoEscola.objects.filter(
            codigo_tipo_escola__in=tipo_ids
        ).only("codigo_tipo_escola", "sigla", "descricao")
    }

    sub_ids = {r["codigo_sub_prefeitura"] for r in rows if r["codigo_sub_prefeitura"]}
    subs = {
        s.codigo_sub_prefeitura: s
        for s in SubPrefeitura.objects.filter(
            codigo_sub_prefeitura__in=sub_ids
        ).only("codigo_sub_prefeitura", "nome")
    }

    result: list[EscolaPorDreContract] = []
    for r in rows:
        tipo = tipos.get(r["codigo_tipo_escola"])
        sub = subs.get(r["codigo_sub_prefeitura"])
        result.append(
            EscolaPorDreContract(
                codigoEscola=r["codigo_ue"],
                nomeEscola=r["nome"],
                codigoDRE=dre_obj.codigo_dre,
                tipoEscola=tipo.descricao if tipo else "",
                siglaTipoEscola=tipo.sigla if tipo else "",
                nomeDRE=dre_obj.nome,
                siglaDRE=dre_obj.sigla or "",
                codigoSubprefeitura=str(r["codigo_sub_prefeitura"]) if r["codigo_sub_prefeitura"] else "",
                nomeSubprefeitura=sub.nome if sub else "",
                tipoEscolaId=r["codigo_tipo_escola"],
                tipoUnidadeId=r["codigo_tipo_escola"],
                subprefeituraId=r["codigo_sub_prefeitura"],
                dreId=dre_obj.codigo_dre,
                codigoIntegracao=r.get("codigo_ue_integracao"),
            )
        )
    return result


# --- Códigos de UEs ---


def listar_codigos_ues_por_dre(codigo_dre: str) -> list[str]:
    """Retorna lista de códigos EOL das UEs de uma DRE."""
    return list(
        UnidadeEducacional.objects.filter(codigo_dre=codigo_dre)
        .values_list("codigo_ue", flat=True)
        .order_by("codigo_ue")
    )


# --- Unidades prediais ---


def listar_unidades_por_dre(codigo_dre: str) -> list[UnidadePredialContract]:
    """Lista completa de unidades prediais de uma DRE (D10)."""
    try:
        dre_obj = DRE.objects.only(
            "codigo_dre", "nome", "tipo_unidade_adm"
        ).get(
            codigo_dre=codigo_dre
        )
    except DRE.DoesNotExist:
        return []

    rows = list(
        UnidadeEducacional.objects.filter(codigo_dre=codigo_dre).values(
            "codigo_ue",
            "nome",
            "nome_nao_oficial",
            "tipo_ue",
            "tipo_logradouro",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "distrito",
            "email",
            "telefone_1",
            "telefone_2",
            "ano_construcao",
            "propriedade",
            "organizacao_parceira",
            "vagas_matutino",
            "vagas_vespertino",
            "vagas_noturno",
            "vagas_intermediario",
            "vagas_integral",
            "vagas_total",
            "quantidade_funcionarios",
            "status",
            "codigo_sub_prefeitura",
            "codigo_tipo_escola",
        )
    )
    if not rows:
        return []

    sub_ids = {r["codigo_sub_prefeitura"] for r in rows if r["codigo_sub_prefeitura"]}
    subs = {
        s.codigo_sub_prefeitura: s
        for s in SubPrefeitura.objects.filter(
            codigo_sub_prefeitura__in=sub_ids
        ).only("codigo_sub_prefeitura", "nome")
    }

    result: list[UnidadePredialContract] = []
    for r in rows:
        sub = subs.get(r["codigo_sub_prefeitura"])
        cep_val: int | None = None
        if r["cep"]:
            try:
                cep_val = int(str(r["cep"]).replace("-", "").replace(".", ""))
            except (ValueError, TypeError):
                cep_val = None
        result.append(
            UnidadePredialContract(
                codigoEol=r["codigo_ue"],
                nomeOficial=r["nome"],
                nomeNaoOficial=r["nome_nao_oficial"],
                tipoUnidadeAdmin=None,
                tipoUE=r["tipo_ue"],
                logadouro=r["logradouro"],
                numero=r["numero"],
                bairro=r["bairro"],
                cep=cep_val,
                distrito=r["distrito"],
                subPrefeitura=sub.nome if sub else None,
                nomeDre=dre_obj.nome,
                email=r["email"],
                telefone1=r["telefone_1"],
                telefone2=r["telefone_2"],
                anoConstrucao=r["ano_construcao"],
                propriedade=r["propriedade"],
                capacidadeVagasMatutino=r["vagas_matutino"],
                capacidadeVagasVespertino=r["vagas_vespertino"],
                capacidadeVagasNoturno=r["vagas_noturno"],
                capacidadeVagasIntermediario=r["vagas_intermediario"],
                capacidadeVagasIntegral=r["vagas_integral"],
                capacidadeVagasTotal=r["vagas_total"],
                organizacaoParceira=r["organizacao_parceira"],
                quantidadeDeFuncionarios=r["quantidade_funcionarios"],
                status=r["status"],
                subprefeituraId=r["codigo_sub_prefeitura"],
                tipoUnidadeAdmId=dre_obj.tipo_unidade_adm,
            )
        )
    return result


# --- Códigos de integração ---


def listar_codigos_integracao_por_dre(
    codigo_dre: str,
) -> list[CodigoIntegracaoContract]:
    """UEs com código de integração de uma DRE (D11)."""
    rows = (
        UnidadeEducacional.objects.filter(codigo_dre=codigo_dre)
        .values(
            "codigo_ue",
            "nome",
            "codigo_ue_integracao",
            "codigo_tipo_escola",
            "codigo_sub_prefeitura",
        )
        .order_by("codigo_ue")
    )
    return [
        CodigoIntegracaoContract(
            codigoUe=r["codigo_ue"],
            nomeUe=r["nome"],
            codigoIntegracao=r["codigo_ue_integracao"],
            tipoEscolaId=r["codigo_tipo_escola"],
            tipoUnidadeId=r["codigo_tipo_escola"],
            subprefeituraId=r["codigo_sub_prefeitura"],
            dreId=codigo_dre,
        )
        for r in rows
    ]
