"""Testes de governança arquitetural — estrutura, contratos e padrões."""

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPS = ROOT / "apps"

# Domínios de negócio (excluindo core)
_DOMINIOS = ["dre", "unidade_educacional", "turmas"]

# Arquivos obrigatórios em domínios de negócio com views
_ARQUIVOS_OBRIGATORIOS = {
    "dre": ["models.py", "contracts.py", "selectors.py", "api/views.py", "api/urls.py"],
    "unidade_educacional": ["models.py", "contracts.py", "selectors.py", "api/views.py", "api/urls.py"],
}

# Módulos que NUNCA devem aparecer em código de produção
_IMPORTS_PROIBIDOS_GLOBAL = [
    "apps.professores",
    "apps.alunos",
    "apps.pedagogico",
    "unittest.mock",
]


def _py_files_dominio(dominio: str, excluir_testes: bool = True) -> list[pathlib.Path]:
    path = APPS / dominio
    if not path.exists():
        return []
    files = list(path.rglob("*.py"))
    if excluir_testes:
        files = [f for f in files if "tests" not in f.parts and "test_" not in f.name]
    return files


def _coletar_imports(py_file: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    modulos: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modulos.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modulos.append(node.module)
    return modulos


# ─── Estrutura ────────────────────────────────────────────────────────────────

def test_arquivos_obrigatorios_existem() -> None:
    """Domínios de negócio devem ter models, contracts, selectors, views e urls."""
    faltando: list[str] = []
    for dominio, arquivos in _ARQUIVOS_OBRIGATORIOS.items():
        for arq in arquivos:
            caminho = APPS / dominio / arq
            if not caminho.exists():
                faltando.append(str(caminho.relative_to(ROOT)))
    assert not faltando, "Arquivos obrigatórios ausentes:\n" + "\n".join(faltando)


def test_models_sao_managed_false() -> None:
    """Todo model em domínio de negócio deve usar managed=False."""
    violacoes: list[str] = []
    for dominio in ["dre", "unidade_educacional"]:
        models_file = APPS / dominio / "models.py"
        if not models_file.exists():
            continue
        conteudo = models_file.read_text(encoding="utf-8")
        if "managed = True" in conteudo or (
            "class Meta" in conteudo and "managed" not in conteudo
        ):
            violacoes.append(str(models_file.relative_to(ROOT)))
    assert not violacoes, (
        "Models sem managed=False (dados são read-only):\n" + "\n".join(violacoes)
    )


def test_sem_migrations() -> None:
    """Nenhum domínio deve ter pasta migrations (managed=False = sem migrations)."""
    encontradas: list[str] = []
    for dominio in _DOMINIOS:
        mig = APPS / dominio / "migrations"
        if mig.exists():
            encontradas.append(str(mig.relative_to(ROOT)))
    assert not encontradas, "Pastas de migrations encontradas:\n" + "\n".join(encontradas)


# ─── Contratos ────────────────────────────────────────────────────────────────

def test_contracts_usam_apenas_typed_dict() -> None:
    """Contratos de domínio devem ser TypedDict (sem dataclasses ou Pydantic)."""
    violacoes: list[str] = []
    for dominio in ["dre", "unidade_educacional"]:
        contracts_file = APPS / dominio / "contracts.py"
        if not contracts_file.exists():
            continue
        conteudo = contracts_file.read_text(encoding="utf-8")
        if "@dataclass" in conteudo or "BaseModel" in conteudo:
            violacoes.append(str(contracts_file.relative_to(ROOT)))
    assert not violacoes, (
        "Contratos usando dataclass/Pydantic em vez de TypedDict:\n"
        + "\n".join(violacoes)
    )


def _campos_snake_case_em_arquivo(contracts_file: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(contracts_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    violacoes: list[str] = []
    rel = contracts_file.relative_to(ROOT)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not (isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)):
                continue
            campo = item.target.id
            if "_" in campo and not campo.startswith("_") and campo != campo.upper():
                violacoes.append(f"{rel}: campo '{campo}' não é camelCase")
    return violacoes


def test_campos_contratos_sao_camel_case() -> None:
    """Campos dos TypedDicts de contratos devem ser camelCase (contrato EOL legado)."""
    violacoes: list[str] = []
    for dominio in ["dre", "unidade_educacional"]:
        contracts_file = APPS / dominio / "contracts.py"
        if contracts_file.exists():
            violacoes.extend(_campos_snake_case_em_arquivo(contracts_file))
    assert not violacoes, (
        "Campos snake_case encontrados em contratos (devem ser camelCase):\n"
        + "\n".join(violacoes)
    )


# ─── Imports proibidos globalmente ────────────────────────────────────────────

def _imports_proibidos_em_arquivo(py_file: pathlib.Path) -> list[str]:
    rel = py_file.relative_to(ROOT)
    return [
        f"{rel}: importa '{imp}'"
        for imp in _coletar_imports(py_file)
        for proibido in _IMPORTS_PROIBIDOS_GLOBAL
        if imp == proibido or imp.startswith(proibido + ".")
    ]


def test_sem_imports_de_microsservicos_externos() -> None:
    """Nenhum arquivo de produção pode importar módulos de outro microserviço."""
    violacoes: list[str] = []
    for dominio in _DOMINIOS:
        for py_file in _py_files_dominio(dominio, excluir_testes=True):
            violacoes.extend(_imports_proibidos_em_arquivo(py_file))
    assert not violacoes, (
        "Imports proibidos encontrados:\n" + "\n".join(violacoes)
    )


# ─── Views ────────────────────────────────────────────────────────────────────

def _nome_base(b: ast.expr) -> str:
    if isinstance(b, ast.Name):
        return b.id
    if isinstance(b, ast.Attribute):
        return b.attr
    return ""


def _violacoes_heranca_em_views(views_file: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(views_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    rel = views_file.relative_to(ROOT)
    violacoes: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or not node.bases:
            continue
        bases = [_nome_base(b) for b in node.bases]
        if "BaseAPIView" not in bases and "APIView" not in bases:
            violacoes.append(f"{rel}: {node.name} não herda de BaseAPIView")
    return violacoes


def test_views_herdam_de_base_api_view() -> None:
    """Todas as views de domínio devem herdar de BaseAPIView."""
    violacoes: list[str] = []
    for dominio in _DOMINIOS:
        views_file = APPS / dominio / "api" / "views.py"
        if views_file.exists():
            violacoes.extend(_violacoes_heranca_em_views(views_file))
    assert not violacoes, (
        "Views sem herança de BaseAPIView:\n" + "\n".join(violacoes)
    )


def test_selectors_nao_importam_views() -> None:
    """Selectors não podem importar views (dependência invertida)."""
    violacoes: list[str] = []
    for dominio in ["dre", "unidade_educacional"]:
        selectors_file = APPS / dominio / "selectors.py"
        if not selectors_file.exists():
            continue
        for imp in _coletar_imports(selectors_file):
            if ".api." in imp or imp.endswith(".views") or imp.endswith(".urls"):
                rel = selectors_file.relative_to(ROOT)
                violacoes.append(f"{rel}: importa '{imp}' (camada proibida)")
    assert not violacoes, (
        "Selectors importando views/urls:\n" + "\n".join(violacoes)
    )


# ─── Health endpoints ─────────────────────────────────────────────────────────

def test_health_endpoints_existem() -> None:
    """Arquivo apps/core/health.py deve existir com as três views."""
    health_file = APPS / "core" / "health.py"
    assert health_file.exists(), "apps/core/health.py não encontrado"
    conteudo = health_file.read_text(encoding="utf-8")
    for view in ("LivenessView", "ReadinessView", "HealthView"):
        assert view in conteudo, f"{view} não encontrada em health.py"


def test_health_urls_registradas() -> None:
    """URLs de health devem estar em config/urls.py."""
    urls_file = ROOT / "config" / "urls.py"
    conteudo = urls_file.read_text(encoding="utf-8")
    assert "health/live/" in conteudo
    assert "health/ready/" in conteudo
    assert "health/" in conteudo
