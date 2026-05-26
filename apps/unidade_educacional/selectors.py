"""Selectors do domínio UE."""

import re as _re
from zoneinfo import ZoneInfo

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
    """Carrega DREs pelos códigos em um dict indexado por código.

    Args:
        ids: Conjunto de códigos EOL das DREs a carregar.

    Returns:
        Dict mapeando código EOL para instância de DRE.
    """
    return {
        d.codigo_dre: d
        for d in DRE.objects.filter(codigo_dre__in=ids).only(
            "codigo_dre",
            "nome",
            "sigla",
            "tipo_unidade_adm",
            "descricao_unidade_adm",
        )
    }


def _lookup_tipos(ids: set[int]) -> dict[int, TipoEscola]:
    """Carrega tipos de escola pelos códigos em um dict indexado por código.

    Args:
        ids: Conjunto de códigos de tipo de escola a carregar.

    Returns:
        Dict mapeando código de tipo para instância de TipoEscola.
    """
    return {
        t.codigo_tipo_escola: t
        for t in TipoEscola.objects.filter(
            codigo_tipo_escola__in=ids
        ).only("codigo_tipo_escola", "sigla", "descricao")
    }


def _lookup_subs(ids: set[int]) -> dict[int, SubPrefeitura]:
    """Carrega subprefeituras pelos códigos em um dict indexado por código.

    Args:
        ids: Conjunto de códigos de subprefeitura a carregar.

    Returns:
        Dict mapeando código para instância de SubPrefeitura.
    """
    return {
        s.codigo_sub_prefeitura: s
        for s in SubPrefeitura.objects.filter(
            codigo_sub_prefeitura__in=ids
        ).only("codigo_sub_prefeitura", "nome")
    }


def _cep_to_int(cep: str | None) -> int | None:
    """Converte string de CEP para inteiro, removendo pontuação.

    Args:
        cep: String de CEP (ex: "04218-050" ou "04218050").

    Returns:
        CEP como inteiro, ou None se ausente ou inválido.
    """
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
    """Monta contrato básico de UE a partir de uma linha e lookups pré-carregados.

    Args:
        r: Linha de dados brutos da UE (campos do .values()).
        dres: Lookup de DREs indexado por código EOL.
        tipos: Lookup de tipos de escola indexado por código.

    Returns:
        Contrato básico da UE com dados de DRE e tipo resolvidos.
    """
    dre = dres.get(r["codigo_dre"])
    tipo = (
        tipos.get(r["codigo_tipo_escola"])
        if r["codigo_tipo_escola"]
        else None
    )
    return UeBasicaContract(
        codigoEscola=r["codigo_ue"],
        nomeEscola=r["nome"],
        nomeDRE=dre.nome if dre else "",
        siglaDRE=dre.sigla or "" if dre else "",
        codigoDRE=r["codigo_dre"],
        tipoEscola=tipo.descricao if tipo else "",
        siglaTipoEscola=tipo.sigla.strip() if tipo and tipo.sigla else "",
        codigoTipoEscola=r["codigo_tipo_escola"] or 0,
        tipoEscolaId=r["codigo_tipo_escola"],
        tipoUnidadeId=r["codigo_tipo_escola"],
        subprefeituraId=r.get("codigo_sub_prefeitura"),
        dreId=r["codigo_dre"],
        codigoIntegracao=r.get("codigo_ue_integracao"),
    )


def listar_ues_basicas(
    codigos: list[str] | None = None,
    limite: int | None = None,
    offset: int = 0,
) -> tuple[list[UeBasicaContract], int]:
    """Lista UEs com dados básicos.

    Args:
        codigos: Lista de códigos EOL para filtro. Se None, retorna todas.
        limite: Número máximo de itens por página.
        offset: Posição inicial da página.

    Returns:
        Tupla (itens, total), onde total é o total sem paginação.
    """
    qs = UnidadeEducacional.objects.values(
        "codigo_ue",
        "nome",
        "codigo_dre",
        "codigo_tipo_escola",
        "codigo_sub_prefeitura",
        "codigo_ue_integracao",
    ).order_by("nome")
    if codigos is not None:
        qs = qs.filter(codigo_ue__in=codigos)
        rows = list(qs)
        total = len(rows)
    else:
        total = qs.count()
        if limite is not None:
            qs = qs[offset: offset + limite]
        rows = list(qs)

    if not rows:
        return [], total

    dre_ids = {r["codigo_dre"] for r in rows}
    tipo_ids = {
        r["codigo_tipo_escola"] for r in rows if r["codigo_tipo_escola"]
    }
    dres = _lookup_dres(dre_ids)
    tipos = _lookup_tipos(tipo_ids)
    return [_build_ue_basica(r, dres, tipos) for r in rows], total


def obter_ue_basica_por_codigo(codigo: str) -> UeBasicaContract | None:
    """Retorna dados básicos de uma UE pelo código EOL.

    Args:
        codigo: Código EOL da UE.

    Returns:
        Contrato básico da UE, ou None se não encontrada.
    """
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo).values(
            "codigo_ue",
            "nome",
            "codigo_dre",
            "codigo_tipo_escola",
            "codigo_sub_prefeitura",
            "codigo_ue_integracao",
        )
    )
    if not rows:
        return None
    r = rows[0]
    dres = _lookup_dres({r["codigo_dre"]})
    tipos = _lookup_tipos(
        {r["codigo_tipo_escola"]} if r["codigo_tipo_escola"] else set()
    )
    return _build_ue_basica(r, dres, tipos)


def obter_ue_eol(codigo: str) -> UeEolContract | None:
    """Retorna dados resumidos de uma UE pelo código EOL.

    Args:
        codigo: Código EOL da UE.

    Returns:
        Dados resumidos da UE, ou None se não encontrada.
    """
    try:
        ue = UnidadeEducacional.objects.only(
            "codigo_ue",
            "nome",
            "nome_nao_oficial",
            "codigo_tipo_unidade_educacao",
            "codigo_dre",
        ).get(codigo_ue=codigo)
    except UnidadeEducacional.DoesNotExist:
        return None
    return UeEolContract(
        codigo=ue.codigo_ue,
        sigla=ue.nome_nao_oficial,
        nomeUnidade=ue.nome,
        tipo=ue.codigo_tipo_unidade_educacao,
        codigoReferencia=ue.codigo_dre,
    )


def obter_ue_completa(codigo: str) -> UeCompletaContract | None:
    """Retorna dados completos de uma UE pelo código EOL.

    Args:
        codigo: Código EOL da UE.

    Returns:
        Dados completos com endereço, tipo e DRE resolvidos,
        ou None se não encontrada.
    """
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo).values(
            "codigo_ue",
            "nome",
            "nome_nao_oficial",
            "tipo_ue",
            "tipo_logradouro",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "municipio",
            "email",
            "telefone_1",
            "codigo_dre",
            "codigo_tipo_escola",
            "codigo_inep",
            "codigo_sub_prefeitura",
            "codigo_ue_integracao",
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
    tipo = (
        tipos.get(r["codigo_tipo_escola"]) if r["codigo_tipo_escola"] else None
    )
    sigla_tipo = tipo.sigla.strip() if tipo and tipo.sigla else None
    telefone_raw = r["telefone_1"]
    if telefone_raw:
        telefone_raw = _re.sub(r"^\(\d+\)\s*", "", telefone_raw).strip()
    return UeCompletaContract(
        nomeDRE=dre.nome if dre else "",
        siglaDRE=dre.sigla or "" if dre else "",
        codigoDRE=r["codigo_dre"],
        codigoINEP=str(r["codigo_inep"]) if r["codigo_inep"] else None,
        siglaTipoEscola=sigla_tipo,
        nome=r["nome"],
        nomeExibicao=r["nome_nao_oficial"],
        codigo=r["codigo_ue"],
        tipoUnidade=r["tipo_ue"],
        email=r["email"],
        telefone=telefone_raw,
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
    """Lista todos os tipos de escola com código, sigla e data de atualização.

    Returns:
        Tipos de escola ordenados por código, com data formatada em ISO 8601.
    """
    campos = ["codigo_tipo_escola", "sigla"]
    tem_dt = _coluna_existe("tipo_escola", "data_atualizacao")
    if tem_dt:
        campos.append("data_atualizacao")

    result = []
    for t in TipoEscola.objects.only(*campos).order_by("codigo_tipo_escola"):
        dt = getattr(t, "data_atualizacao", None) if tem_dt else None
        if dt is not None:
            dt = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
            ms_val = dt.microsecond // 1000
            if ms_val == 0:
                dt_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                ms = f"{ms_val:03d}".rstrip("0")
                dt_iso = dt.strftime("%Y-%m-%dT%H:%M:%S.") + ms
        else:
            dt_iso = None
        result.append(TipoEscolaContract(
            codigo=t.codigo_tipo_escola,
            descricaoSigla=t.sigla.strip() if t.sigla else None,
            dtAtualizacao=dt_iso,
        ))
    return result


def obter_subprefeituras_ue(
    codigo: str,
) -> list[SubPrefeiturarContract] | None:
    """Retorna subprefeituras de uma UE ou None se a UE não existir.

    Args:
        codigo: Código EOL da UE.

    Returns:
        Lista de subprefeituras vinculadas, lista vazia se não houver
        nenhuma, ou None se a UE não existir.
    """
    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo)
        .exclude(codigo_sub_prefeitura__isnull=True)
        .values("codigo_sub_prefeitura")
    )
    if not rows:
        if not UnidadeEducacional.objects.filter(
            codigo_ue=codigo
        ).exists():
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


def _coluna_existe(tabela: str, coluna: str) -> bool:
    """Verifica em tempo de execução se uma coluna existe no banco.

    Args:
        tabela: Nome da tabela no banco de dados.
        coluna: Nome da coluna a verificar.

    Returns:
        True se a coluna existir, False caso contrário ou em caso de erro.
    """
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name=%s AND column_name=%s LIMIT 1",
                [tabela, coluna],
            )
            return cursor.fetchone() is not None
    except Exception:
        return False


def obter_sincronizacao_ue(
    codigo: str,
) -> SincronizacaoUeContract | None:
    """Retorna dados de sincronização institucional de uma UE.

    Args:
        codigo: Código EOL da UE.

    Returns:
        Dados de sincronização com data de atualização formatada,
        ou None se a UE não for encontrada.
    """
    campos = [
        "codigo_ue",
        "nome",
        "codigo_dre",
        "codigo_tipo_escola",
        "codigo_sub_prefeitura",
        "codigo_ue_integracao",
    ]
    if _coluna_existe("unidade_educacional", "data_atualizacao"):
        campos.append("data_atualizacao")

    rows = list(
        UnidadeEducacional.objects.filter(codigo_ue=codigo).values(*campos)
    )
    if not rows:
        return None
    r = rows[0]
    dt = r.get("data_atualizacao")
    if dt is not None:
        dt = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
        data_iso = (
            dt.strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{dt.microsecond // 1000:03d}"
        )
    else:
        data_iso = None
    try:
        dre_int: int | None = (
            int(r["codigo_dre"]) if r["codigo_dre"] else None
        )
    except (ValueError, TypeError):
        dre_int = None
    return SincronizacaoUeContract(
        ueCodigo=r["codigo_ue"],
        dataAtualizacao=data_iso,
        dreCodigo=dre_int,
        ueNome=r["nome"],
        tipoEscolaCodigo=r["codigo_tipo_escola"],
        tipoEscolaId=r["codigo_tipo_escola"],
        tipoUnidadeId=r["codigo_tipo_escola"],
        subprefeituraId=r["codigo_sub_prefeitura"],
        dreId=r["codigo_dre"],
        codigoIntegracao=r["codigo_ue_integracao"],
    )


def _aplicar_filtros_equipamentos(
    qs,
    codigos_subprefeitura,
    codigos_dre,
    tipos_unidade,
    tipos_escola,
    nome_escola,
    codigo_eol,
):
    """Aplica filtros opcionais ao QuerySet de equipamentos.

    Args:
        qs: QuerySet base de UnidadeEducacional.
        codigos_subprefeitura: Códigos de subprefeitura para filtro.
        codigos_dre: Códigos EOL de DRE para filtro.
        tipos_unidade: Códigos de tipo de unidade para filtro.
        tipos_escola: Códigos de tipo de escola para filtro.
        nome_escola: Substring do nome da escola para filtro.
        codigo_eol: Código EOL exato da escola para filtro.

    Returns:
        QuerySet com os filtros aplicados.
    """
    if codigos_subprefeitura:
        qs = qs.filter(
            codigo_sub_prefeitura__in=codigos_subprefeitura
        )
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
    return qs


def _montar_logradouro(r: dict) -> str | None:
    """Concatena tipo, logradouro e número no formato EOL.

    Args:
        r: Linha de dados brutos da UE com campos de endereço.

    Returns:
        Logradouro formatado (ex: "RUA APUCARANA Nº 215"), ou None se vazio.
    """
    partes = []
    if r.get("tipo_logradouro"):
        partes.append(r["tipo_logradouro"].strip().upper())
    if r.get("logradouro"):
        partes.append(r["logradouro"].strip().upper())
    if r.get("numero"):
        partes.append(f"Nº {r['numero'].strip()}")
    return " ".join(partes) if partes else None


def _build_equipamento(
    r: dict,
    dres: dict,
    tipos: dict,
    subs: dict,
) -> EquipamentoContract:
    """Monta contrato de equipamento a partir dos dados brutos da UE.

    Args:
        r: Linha de dados brutos da UE (campos do .values()).
        dres: Lookup de DREs indexado por código EOL.
        tipos: Lookup de tipos de escola indexado por código.
        subs: Lookup de subprefeituras indexado por código.

    Returns:
        Contrato de equipamento com campos prefixados (cd_, nm_, dc_, sg_).
    """
    dre = dres.get(r["codigo_dre"])
    cd_tp_eq = r.get("codigo_tipo_unidade_educacao")
    dc_tp_eq = r.get("tipo_ue")
    tipo_escola = (
        tipos.get(r["codigo_tipo_escola"]) if r["codigo_tipo_escola"] else None
    )
    sub = (
        subs.get(r["codigo_sub_prefeitura"])
        if r["codigo_sub_prefeitura"]
        else None
    )
    dre_nome = dre.nome if dre else ""
    dre_sigla = (dre.sigla or "").strip() if dre else ""
    tipo_sigla = (
        tipo_escola.sigla.strip() if tipo_escola and tipo_escola.sigla else ""
    )
    tipo_desc = tipo_escola.descricao if tipo_escola else ""
    cd_tp_escola = (
        r["codigo_tipo_escola"]
        if r["codigo_tipo_escola"] is not None
        else 0
    )
    return EquipamentoContract(
        cd_equipamento=r["codigo_ue"],
        nm_exibicao_equipamento=r["nome_nao_oficial"] or r["nome"],
        nm_equipamento=r["nome"],
        cd_tp_equipamento=cd_tp_eq,
        dc_tp_equipamento=dc_tp_eq,
        cd_tp_escola=cd_tp_escola,
        dc_tipo_escola=tipo_desc,
        sg_tp_escola=tipo_sigla,
        cd_diretoria_referencia=r["codigo_dre"],
        nm_diretoria_referencia=dre_nome,
        cd_diretoria_portal=r["codigo_dre"],
        nm_diretoria_portal=dre_nome,
        nm_exibicao_diretoria_portal=dre_sigla or None,
        nm_exibicao_diretoria_referencia=dre_sigla or None,
        cd_logradouro=r.get("codigo_logradouro"),
        logradouro=_montar_logradouro(r),
        bairro=r["bairro"],
        codigoSubprefeitura=(
            str(r["codigo_sub_prefeitura"])
            if r["codigo_sub_prefeitura"]
            else None
        ),
        nomeSubprefeitura=sub.nome if sub else None,
        ehCeu=bool(r.get("eh_ceu", False)),
    )


def listar_equipamentos(
    codigos_subprefeitura: list[int] | None = None,
    codigos_dre: list[str] | None = None,
    tipos_unidade: list[int] | None = None,
    tipos_escola: list[int] | None = None,
    nome_escola: str | None = None,
    codigo_eol: str | None = None,
) -> list[EquipamentoContract]:
    """Lista equipamentos SME com filtros opcionais.

    Args:
        codigos_subprefeitura: Códigos de subprefeitura para filtro.
        codigos_dre: Códigos EOL de DRE para filtro.
        tipos_unidade: Códigos de tipo de unidade para filtro.
        tipos_escola: Códigos de tipo de escola para filtro.
        nome_escola: Substring do nome da escola para filtro.
        codigo_eol: Código EOL exato da escola para filtro.

    Returns:
        Equipamentos que atendem aos filtros, ordenados por nome.
    """
    campos_eq = [
        "codigo_ue",
        "nome",
        "nome_nao_oficial",
        "tipo_ue",
        "codigo_dre",
        "codigo_tipo_escola",
        "codigo_tipo_unidade_educacao",
        "codigo_sub_prefeitura",
        "tipo_logradouro",
        "codigo_logradouro",
        "logradouro",
        "numero",
        "bairro",
    ]
    if _coluna_existe("unidade_educacional", "eh_ceu"):
        campos_eq.append("eh_ceu")
    qs = UnidadeEducacional.objects.values(*campos_eq)
    qs = _aplicar_filtros_equipamentos(
        qs,
        codigos_subprefeitura,
        codigos_dre,
        tipos_unidade,
        tipos_escola,
        nome_escola,
        codigo_eol,
    )
    rows = list(qs.order_by("codigo_ue"))
    if not rows:
        return []

    dres = _lookup_dres({r["codigo_dre"] for r in rows})
    tipos = _lookup_tipos(
        {r["codigo_tipo_escola"] for r in rows if r["codigo_tipo_escola"]}
    )
    subs = _lookup_subs(
        {
            r["codigo_sub_prefeitura"]
            for r in rows
            if r["codigo_sub_prefeitura"]
        }
    )
    return [_build_equipamento(r, dres, tipos, subs) for r in rows]


def _nome_com_tipo(nome: str, tipo: "TipoEscola | None") -> str:
    """Prefixa o nome da UE com a sigla do tipo de escola.

    Args:
        nome: Nome da UE.
        tipo: Tipo de escola da UE, ou None.

    Returns:
        Nome prefixado com sigla (ex: "EMEF CASARAO"), ou nome original
        se já contiver o prefixo ou tipo for None.
    """
    if not tipo or not tipo.sigla:
        return nome
    sigla = tipo.sigla.strip()
    if not sigla or nome.upper().startswith(sigla.upper()):
        return nome
    return f"{sigla} {nome}"


def listar_unidades_parceiras(
    codigos: list[str],
) -> list[UnidadeParceirasContract]:
    """Lista unidades parceiras pelos códigos informados.

    Args:
        codigos: Códigos EOL das unidades a buscar.

    Returns:
        Unidades com organização_parceira=True encontradas nos códigos.
    """
    rows = list(
        UnidadeEducacional.objects.filter(
            codigo_ue__in=codigos, organizacao_parceira=True
        ).values("codigo_ue", "nome", "email", "codigo_tipo_escola")
    )
    if not rows:
        return []

    tipo_ids = {
        r["codigo_tipo_escola"] for r in rows if r["codigo_tipo_escola"]
    }
    tipos = _lookup_tipos(tipo_ids)

    return [
        UnidadeParceirasContract(
            codigo=r["codigo_ue"],
            nome=_nome_com_tipo(r["nome"], tipos.get(r["codigo_tipo_escola"])),
            email=r["email"],
        )
        for r in rows
    ]
