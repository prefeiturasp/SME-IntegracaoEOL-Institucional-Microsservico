"""Configuração do Sphinx para o microserviço institucional."""

project = "SME-IntegracaoEOL-Institucional-Microsservico"
author = "SME"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_theme = "alabaster"
