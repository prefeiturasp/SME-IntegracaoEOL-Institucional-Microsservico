"""Selectors do domínio DRE."""

from typing import Any

from apps.core.types import SubPrefeiturarContract
from apps.dre.contracts import (
    CodigoIntegracaoContract,
    DreResumoContract,
    EscolaPorDreContract,
    UnidadePredialContract,
)
from apps.dre.models import DRE, SubPrefeitura, TipoEscola
from apps.unidade_educacional.models import UnidadeEducacional


def listar_dres() -> list[DreResumoContract]:
    """Lista todas as Diretorias Regionais de Educação.

    Returns:
        DREs cadastradas ordenadas por nome.
    """
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
    """Filtra DREs pela lista de códigos.

    Args:
        codigos: Códigos EOL das DREs a serem buscadas.

    Returns:
        DREs encontradas para os códigos informados.
    """
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
    """Retorna uma DRE pelo código ou None se não existir.

    Args:
        codigo: Código EOL da DRE.

    Returns:
        Dados resumidos da DRE, ou None se não encontrada.
    """
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
    """Lista subprefeituras distintas das UEs de uma DRE.

    Args:
        codigo_dre: Código EOL da DRE.

    Returns:
        Subprefeituras distintas referenciadas pelas UEs da DRE.
    """
    ids = (
        UnidadeEducacional.objects.filter(codigo_dre=codigo_dre)
        .exclude(codigo_sub_prefeitura__isnull=True)
        .exclude(codigo_sub_prefeitura=0)
        .values_list("codigo_sub_prefeitura", flat=True)
        .distinct()
    )
    qs = (
        SubPrefeitura.objects.filter(codigo_sub_prefeitura__in=ids)
        .exclude(codigo_sub_prefeitura=99)
        .only("codigo_sub_prefeitura", "nome")
    )
    return [
        SubPrefeiturarContract(
            codigoSubprefeitura=str(s.codigo_sub_prefeitura),
            nomeSubprefeitura=s.nome,
        )
        for s in qs
    ]


# --- Escolas por DRE ---


# Variantes CEU agrupadas no EOL junto ao tipo base.
_CEU_SUBTIPOS: dict[int, list[int]] = {
    1: [16],   # EMEF + CEU EMEF
    2: [17],   # EMEI + CEU EMEI
    10: [18],  # CEI DIRET + CEU CEI
    28: [31],  # CEMEI + CEU CEMEI
}


def _ue_rows_por_dre(
    codigo_dre: str, tipo_escola_id: int | None = None
) -> Any:
    """Retorna QuerySet de UEs de uma DRE, opcionalmente filtrado por tipo.

    Args:
        codigo_dre: Código EOL da DRE.
        tipo_escola_id: Código do tipo de escola para filtro opcional.

    Returns:
        QuerySet com campos básicos das UEs, ordenado por código.
    """
    qs = UnidadeEducacional.objects.filter(codigo_dre=codigo_dre).values(
        "codigo_ue",
        "nome",
        "codigo_dre",
        "codigo_tipo_escola",
        "codigo_sub_prefeitura",
        "codigo_ue_integracao",
    )
    if tipo_escola_id is not None:
        tipos = [tipo_escola_id] + _CEU_SUBTIPOS.get(tipo_escola_id, [])
        qs = qs.filter(codigo_tipo_escola__in=tipos)
    return qs.order_by("codigo_ue")


def listar_escolas_por_dre(
    codigo_dre: str, tipo_escola_id: int | None = None
) -> list[EscolaPorDreContract]:
    """Lista escolas de uma DRE, opcionalmente filtradas por tipo.

    Args:
        codigo_dre: Código EOL da DRE.
        tipo_escola_id: Código do tipo de escola para filtro opcional.

    Returns:
        Escolas da DRE com dados de tipo e subprefeitura resolvidos.
    """
    # Carrega lookups em memória para evitar N+1
    try:
        dre_obj = DRE.objects.only("codigo_dre", "nome", "sigla").get(
            codigo_dre=codigo_dre
        )
    except DRE.DoesNotExist:
        return []

    rows = list(_ue_rows_por_dre(codigo_dre, tipo_escola_id))
    if not rows:
        return []

    tipo_ids = {
        r["codigo_tipo_escola"]
        for r in rows
        if r["codigo_tipo_escola"]
    }
    tipos = {
        t.codigo_tipo_escola: t
        for t in TipoEscola.objects.filter(
            codigo_tipo_escola__in=tipo_ids
        ).only("codigo_tipo_escola", "sigla", "descricao")
    }

    sub_ids = {
        r["codigo_sub_prefeitura"]
        for r in rows
        if r["codigo_sub_prefeitura"]
    }
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
                codigoSubprefeitura=(
                    str(r["codigo_sub_prefeitura"])
                    if r["codigo_sub_prefeitura"]
                    else ""
                ),
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
    """Retorna lista de códigos EOL das UEs de uma DRE.

    Args:
        codigo_dre: Código EOL da DRE.

    Returns:
        Códigos EOL das UEs vinculadas, ordenados.
    """
    return list(
        UnidadeEducacional.objects.filter(
            codigo_dre=codigo_dre,
            codigo_tipo_escola__isnull=False,
        )
        .exclude(tipo_ue="UNIDADE ADMINISTRATIVA")
        .values_list("codigo_ue", flat=True)
        .order_by("codigo_ue")
    )


# --- Unidades prediais ---


def listar_unidades_por_dre(codigo_dre: str) -> list[UnidadePredialContract]:
    """Lista unidades prediais de uma DRE.

    Args:
        codigo_dre: Código EOL da DRE.

    Returns:
        Unidades com endereço, vagas e dados de subprefeitura resolvidos.
    """
    try:
        dre_obj = DRE.objects.only(
            "codigo_dre", "nome", "tipo_unidade_adm", "descricao_unidade_adm"
        ).get(
            codigo_dre=codigo_dre
        )
    except DRE.DoesNotExist:
        return []

    rows = list(
        UnidadeEducacional.objects.filter(
            codigo_dre=codigo_dre,
        ).values(
            "codigo_ue",
            "nome",
            "nome_nao_oficial",
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
        ).order_by("codigo_ue")
    )
    if not rows:
        return []

    tipo_ids = {
        r["codigo_tipo_escola"]
        for r in rows
        if r["codigo_tipo_escola"]
    }
    tipos = {
        t.codigo_tipo_escola: t
        for t in TipoEscola.objects.filter(
            codigo_tipo_escola__in=tipo_ids
        ).only("codigo_tipo_escola", "descricao")
    }

    sub_ids = {
        r["codigo_sub_prefeitura"]
        for r in rows
        if r["codigo_sub_prefeitura"]
    }
    subs = {
        s.codigo_sub_prefeitura: s
        for s in SubPrefeitura.objects.filter(
            codigo_sub_prefeitura__in=sub_ids
        ).only("codigo_sub_prefeitura", "nome")
    }

    result: list[UnidadePredialContract] = []
    for r in rows:
        tipo = tipos.get(r["codigo_tipo_escola"])
        sub = subs.get(r["codigo_sub_prefeitura"])
        cep_val: int | None = None
        if r["cep"]:
            try:
                cep_val = int(
                    str(r["cep"]).replace("-", "").replace(".", "")
                )
            except (ValueError, TypeError):
                cep_val = None
        result.append(
            UnidadePredialContract(
                codigoEol=r["codigo_ue"],
                nomeOficial=r["nome"],
                nomeNaoOficial=r["nome_nao_oficial"],
                tipoUnidadeAdmin=dre_obj.descricao_unidade_adm or None,
                tipoUE=tipo.descricao if tipo else None,
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
            )
        )
    return result




def listar_codigos_integracao_por_dre(
    codigo_dre: str,
) -> list[CodigoIntegracaoContract]:
    """Lista UEs com código de integração de uma DRE.

    Args:
        codigo_dre: Código EOL da DRE.

    Returns:
        UEs da DRE com seus respectivos códigos de integração.
    """
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
