"""Selectors do domínio UE — queries otimizadas, sem N+1."""

from apps.core.types import SubPrefeiturarContract
from apps.dre.models import DRE, SubPrefeitura, TipoEscola
from apps.unidade_educacional.contracts import (
    EquipamentoContract,
    SincronizacaoUeContract,
    TipoEscolaContract,
    UeBasicaContract,
    UeCompletaContract,
    UeEolContract,
    UnidadeParceirasContract,
)
from apps.unidade_educacional.models import UnidadeEducacional


def _lookup_dres(ids: set[str]) -> dict[str, DRE]:
    return {
        d.codigo_dre: d
        for d in DRE.objects.filter(codigo_dre__in=ids).only(
            "codigo_dre", "nome", "sigla", "tipo_unidade_adm", "descricao_unidade_adm"
        )
    }


def _lookup_tipos(ids: set[int]) -> dict[int, TipoEscola]:
    return {
        t.codigo_tipo_escola: t
        for t in TipoEscola.objects.filter(
            codigo_tipo_escola__in=ids
        ).only("codigo_tipo_escola", "sigla", "descricao")
    }


def _lookup_subs(ids: set[int]) -> dict[int, SubPrefeitura]:
    return {
        s.codigo_sub_prefeitura: s
        for s in SubPrefeitura.objects.filter(
            codigo_sub_prefeitura__in=ids
        ).only("codigo_sub_prefeitura", "nome")
    }


def _cep_to_int(cep: str | None) -> int | None:
    if not cep:
        return None
    try:
        return int(str(cep).replace("-", "").replace(".", ""))
    except (ValueError, TypeError):
        return None


def _build_ue_basica(
    r: dict,
    dres: dict[str, DRE],
    tipos: dict[int, TipoEscola],
) -> UeBasicaContract:
    dre = dres.get(r["codigo_dre"])
    tipo = tipos.get(r["codigo_tipo_escola"]) if r["codigo_tipo_escola"] else None
    return UeBasicaContract(
        codigoEscola=r["codigo_ue"],
        nomeEscola=r["nome"],
        nomeDRE=dre.nome if dre else "",
        siglaDRE=dre.sigla or "" if dre else "",
        codigoDRE=r["codigo_dre"],
        tipoEscola=tipo.descricao if tipo else "",
        siglaTipoEscola=tipo.sigla or "" if tipo else "",
        codigoTipoEscola=r["codigo_tipo_escola"] or 0,
        tipoEscolaId=r["codigo_tipo_escola"],
        tipoUnidadeId=r["codigo_tipo_escola"],
        subprefeituraId=r.get("codigo_sub_prefeitura"),
        dreId=r["codigo_dre"],
        codigoIntegracao=r.get("codigo_ue_integracao"),
    )


def listar_ues_basicas(codigos: list[str] | None = None) -> list[UeBasicaContract]:
    """Lista UEs com dados básicos. Se `codigos` for None, retorna todas."""
    qs = UnidadeEducacional.objects.values(
        "codigo_ue", "nome", "codigo_dre", "codigo_tipo_escola",
        "codigo_sub_prefeitura", "codigo_ue_integracao",
    )
    if codigos is not None:
        qs = qs.filter(codigo_ue__in=codigos)
    rows = list(qs.order_by("nome"))
    if not rows:
        return []

    dre_ids = {r["codigo_dre"] for r in rows}
    tipo_ids = {r["codigo_tipo_escola"] for r in rows if r["codigo_tipo_escola"]}
    dres = _lookup_dres(dre_ids)
    tipos = _lookup_tipos(tipo_ids)
    return [_build_ue_basica(r, dres, tipos) for r in rows]


def obter_ue_basica_por_codigo(codigo: str) -> UeBasicaContract | None:
    """Retorna dados básicos de uma UE ou None."""
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo).values(
            "codigo_ue", "nome", "codigo_dre", "codigo_tipo_escola",
            "codigo_sub_prefeitura", "codigo_ue_integracao",
        )
    )
    if not rows:
        return None
    r = rows[0]
    dres = _lookup_dres({r["codigo_dre"]})
    tipos = _lookup_tipos({r["codigo_tipo_escola"]} if r["codigo_tipo_escola"] else set())
    return _build_ue_basica(r, dres, tipos)


def obter_ue_eol(codigo: str) -> UeEolContract | None:
    """Retorna UE resumida para o contrato E03 ou None."""
    try:
        ue = UnidadeEducacional.objects.only(
            "codigo_ue", "nome", "tipo_ue", "codigo_tipo_escola"
        ).get(codigo_ue=codigo)
    except UnidadeEducacional.DoesNotExist:
        return None
    return UeEolContract(
        codigo=ue.codigo_ue,
        sigla=ue.tipo_ue,
        nomeUnidade=ue.nome,
        tipo=ue.codigo_tipo_escola,
        codigoReferencia=ue.codigo_ue,
    )


def obter_ue_completa(codigo: str) -> UeCompletaContract | None:
    """Retorna dados completos de UE para contrato E04 ou None."""
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo).values(
            "codigo_ue", "nome", "nome_nao_oficial", "tipo_ue",
            "tipo_logradouro", "logradouro", "numero", "bairro", "cep",
            "municipio", "email", "telefone_1", "codigo_dre",
            "codigo_tipo_escola", "codigo_inep",
            "codigo_sub_prefeitura", "codigo_ue_integracao",
        )
    )
    if not rows:
        return None
    r = rows[0]
    dres = _lookup_dres({r["codigo_dre"]})
    tipos = _lookup_tipos(
        {r["codigo_tipo_escola"]} if r["codigo_tipo_escola"] else set()
    )
    dre = dres.get(r["codigo_dre"])
    tipo = tipos.get(r["codigo_tipo_escola"]) if r["codigo_tipo_escola"] else None
    return UeCompletaContract(
        nomeDRE=dre.nome if dre else "",
        siglaDRE=dre.sigla or "" if dre else "",
        codigoDRE=r["codigo_dre"],
        codigoINEP=str(r["codigo_inep"]) if r["codigo_inep"] else None,
        siglaTipoEscola=tipo.sigla if tipo else None,
        nome=r["nome"],
        nomeExibicao=r["nome_nao_oficial"],
        codigo=r["codigo_ue"],
        tipoUnidade=r["tipo_ue"],
        email=r["email"],
        telefone=r["telefone_1"],
        tipoLogradouro=r["tipo_logradouro"],
        logradouro=r["logradouro"],
        numero=r["numero"],
        bairro=r["bairro"],
        cep=_cep_to_int(r["cep"]),
        municipio=r["municipio"],
        uf="SP",
        tipoUnidadeAdm=dre.tipo_unidade_adm if dre else None,
        descTipoUnidadeAdm=dre.descricao_unidade_adm if dre else None,
        tipoEscolaId=r["codigo_tipo_escola"],
        tipoUnidadeId=r["codigo_tipo_escola"],
        subprefeituraId=r["codigo_sub_prefeitura"],
        dreId=r["codigo_dre"],
        codigoIntegracao=r["codigo_ue_integracao"],
    )


def listar_tipos_escolas() -> list[TipoEscolaContract]:
    """Tipos de escola para contrato E11."""
    return [
        TipoEscolaContract(
            codigo=t.codigo_tipo_escola,
            descricaoSigla=t.sigla,
            dtAtualizacao=None,
        )
        for t in TipoEscola.objects.only(
            "codigo_tipo_escola", "sigla"
        ).order_by("codigo_tipo_escola")
    ]


def obter_subprefeituras_ue(codigo: str) -> list[SubPrefeiturarContract] | None:
    """Subprefeituras associadas a uma UE (E17)."""
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo)
        .exclude(codigo_sub_prefeitura__isnull=True)
        .values("codigo_sub_prefeitura")
    )
    if not rows:
        # verifica se a UE existe
        if not UnidadeEducacional.objects.filter(codigo_ue=codigo).exists():
            return None
        return []
    sub_ids = {r["codigo_sub_prefeitura"] for r in rows}
    subs = _lookup_subs(sub_ids)
    return [
        SubPrefeiturarContract(
            codigoSubprefeitura=str(sid),
            nomeSubprefeitura=subs[sid].nome if sid in subs else "",
        )
        for sid in sub_ids
    ]


def obter_sincronizacao_ue(codigo: str) -> SincronizacaoUeContract | None:
    """Dados de sincronização institucional da UE (E23)."""
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo).values(
            "codigo_ue", "nome", "codigo_dre", "codigo_tipo_escola",
            "codigo_sub_prefeitura", "codigo_ue_integracao",
        )
    )
    if not rows:
        return None
    r = rows[0]
    return SincronizacaoUeContract(
        ueCodigo=r["codigo_ue"],
        dataAtualizacao=None,
        dreCodigo=r["codigo_dre"],
        ueNome=r["nome"],
        tipoEscolaCodigo=r["codigo_tipo_escola"],
        tipoEscolaId=r["codigo_tipo_escola"],
        tipoUnidadeId=r["codigo_tipo_escola"],
        subprefeituraId=r["codigo_sub_prefeitura"],
        dreId=r["codigo_dre"],
        codigoIntegracao=r["codigo_ue_integracao"],
    )


def listar_equipamentos(
    codigos_subprefeitura: list[int] | None = None,
    codigos_dre: list[str] | None = None,
    tipos_unidade: list[int] | None = None,
    tipos_escola: list[int] | None = None,
    nome_escola: str | None = None,
    codigo_eol: str | None = None,
) -> list[EquipamentoContract]:
    """Lista equipamentos/UEs com filtros (E25)."""
    qs = UnidadeEducacional.objects.values(
        "codigo_ue", "nome", "codigo_dre",
        "codigo_tipo_escola", "codigo_sub_prefeitura",
        "tipo_logradouro", "logradouro", "numero", "bairro",
        "codigo_ue_integracao",
    )
    if codigos_subprefeitura:
        qs = qs.filter(codigo_sub_prefeitura__in=codigos_subprefeitura)
    if codigos_dre:
        qs = qs.filter(codigo_dre__in=codigos_dre)
    if tipos_unidade:
        qs = qs.filter(codigo_tipo_escola__in=tipos_unidade)
    if tipos_escola:
        qs = qs.filter(codigo_tipo_escola__in=tipos_escola)
    if nome_escola:
        qs = qs.filter(nome__icontains=nome_escola)
    if codigo_eol:
        qs = qs.filter(codigo_ue=codigo_eol)

    rows = list(qs.order_by("nome"))
    if not rows:
        return []

    dre_ids = {r["codigo_dre"] for r in rows}
    tipo_ids = {r["codigo_tipo_escola"] for r in rows if r["codigo_tipo_escola"]}
    sub_ids = {r["codigo_sub_prefeitura"] for r in rows if r["codigo_sub_prefeitura"]}
    dres = _lookup_dres(dre_ids)
    tipos = _lookup_tipos(tipo_ids)
    subs = _lookup_subs(sub_ids)

    result: list[EquipamentoContract] = []
    for r in rows:
        dre = dres.get(r["codigo_dre"])
        tipo = tipos.get(r["codigo_tipo_escola"]) if r["codigo_tipo_escola"] else None
        sub = subs.get(r["codigo_sub_prefeitura"]) if r["codigo_sub_prefeitura"] else None
        result.append(
            EquipamentoContract(
                codigoEol=r["codigo_ue"],
                nomeEscola=r["nome"],
                nomeDRE=dre.nome if dre else "",
                siglaDRE=dre.sigla or "" if dre else "",
                codigoDRE=r["codigo_dre"],
                tipoEscola=tipo.descricao if tipo else None,
                siglaTipoEscola=tipo.sigla if tipo else None,
                codigoSubprefeitura=str(r["codigo_sub_prefeitura"]) if r["codigo_sub_prefeitura"] else None,
                nomeSubprefeitura=sub.nome if sub else None,
                tipoLogradouro=r["tipo_logradouro"],
                logradouro=r["logradouro"],
                numero=r["numero"],
                bairro=r["bairro"],
                tipoEscolaId=r["codigo_tipo_escola"],
                tipoUnidadeId=r["codigo_tipo_escola"],
                subprefeituraId=r["codigo_sub_prefeitura"],
                dreId=r["codigo_dre"],
                codigoIntegracao=r["codigo_ue_integracao"],
            )
        )
    return result


def listar_unidades_parceiras(codigos: list[str]) -> list[UnidadeParceirasContract]:
    """UEs com organizacao_parceira=True filtradas por códigos (E26)."""
    rows = UnidadeEducacional.objects.filter(
        codigo_ue__in=codigos, organizacao_parceira=True
    ).values("codigo_ue", "nome", "email")
    return [
        UnidadeParceirasContract(
            codigo=r["codigo_ue"],
            nome=r["nome"],
            email=r["email"],
        )
        for r in rows
    ]
