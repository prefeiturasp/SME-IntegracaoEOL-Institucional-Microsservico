"""Teste estático de imports entre domínios — bloqueia dependências cruzadas."""

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "apps"

# Regras: módulo fonte -> módulos proibidos de importar
REGRAS_PROIBIDAS: list[tuple[str, list[str]]] = [
    (
        "apps.dre",
        [
            "apps.unidade_educacional.api",
            "apps.unidade_educacional.repositories",
            "apps.unidade_educacional.selectors",
            "apps.unidade_educacional.services",
        ],
    ),
    (
        "apps.unidade_educacional",
        [
            # UE pode importar apps.dre.models (tabelas compartilhadas no banco)
            # mas NÃO deve importar lógica interna de DRE
            "apps.dre.api",
            "apps.dre.repositories",
            "apps.dre.selectors",
            "apps.dre.services",
            "apps.dre.contracts",
        ],
    ),
    # Nenhum domínio institucional importa de outros microserviços
    ("apps.dre", ["apps.professores", "apps.alunos", "apps.pedagogico"]),
    (
        "apps.unidade_educacional",
        ["apps.professores", "apps.alunos", "apps.pedagogico"],
    ),
]


def _coletar_imports(py_file: pathlib.Path) -> list[str]:
    """Retorna lista de módulos importados em um arquivo .py."""
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


def _dominio_para_path(dominio: str) -> pathlib.Path | None:
    """Converte 'apps.dre' em Path relativo ao ROOT."""
    partes = dominio.split(".")[1:]  # remove 'apps'
    p = ROOT
    for parte in partes:
        p = p / parte
    return p if p.exists() else None


def test_sem_imports_cruzados_entre_dominios() -> None:
    """Nenhum domínio deve importar implementação interna de outro."""
    violacoes: list[str] = []

    for dominio_fonte, proibidos in REGRAS_PROIBIDAS:
        fonte_path = _dominio_para_path(dominio_fonte)
        if fonte_path is None:
            continue

        for py_file in fonte_path.rglob("*.py"):
            # ignora testes — eles podem importar qualquer coisa para fixture
            if "tests" in py_file.parts or "test_" in py_file.name:
                continue
            imports = _coletar_imports(py_file)
            for imp in imports:
                for proibido in proibidos:
                    if imp == proibido or imp.startswith(proibido + "."):
                        rel = py_file.relative_to(ROOT.parent)
                        violacoes.append(
                            f"{rel}: importa '{imp}' (proibido para '{dominio_fonte}')"
                        )

    assert not violacoes, (
        "Imports entre domínios detectados:\n" + "\n".join(violacoes)
    )
