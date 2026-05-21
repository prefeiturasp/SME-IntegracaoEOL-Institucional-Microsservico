"""Configuração do Sphinx para a documentação do microserviço Institucional."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import django

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

project = "SME-IntegracaoEOL-Institucional-Microsservico"
author = "SME"
release = "1.0.0"
language = "pt_BR"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

autosectionlabel_prefix_document = True

source_suffix = {".rst": "restructuredtext"}

root_doc = "index"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_title = "SME-IntegracaoEOL Institucional"
html_short_title = "Institucional Docs"
html_static_path = ["_static"]

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_use_param = False
napoleon_use_rtype = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

latex_engine = "xelatex"
latex_documents = [
    (
        "index",
        "sme-integracaoeol-institucional.tex",
        "SME-IntegracaoEOL Institucional",
        "SME",
        "manual",
    ),
]

latex_elements = {
    "babel": "",
    "preamble": r"""
\usepackage{polyglossia}
\setmainlanguage{portuguese}

\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{setspace}
\usepackage{float}

\pagestyle{fancy}

\fancyhead[L]{SME-IntegracaoEOL Institucional}
\fancyhead[R]{\leftmark}
\fancyfoot[C]{\thepage}

\setlength{\headheight}{15pt}

\onehalfspacing

\usepackage{listings}
\lstset{
    breaklines=true,
    basicstyle=\ttfamily\small
}
""",
    "fontpkg": r"""
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
""",
    "maketitle": r"""
\begin{titlepage}
    \centering
    \vspace*{3cm}

    {\Huge\bfseries SME-IntegracaoEOL Institucional \par}
    \vspace{1cm}

    {\Large Documentação Técnica \par}
    \vspace{2cm}

    {\large SME \par}
    \vspace{0.5cm}

    {\large \today \par}

    \vfill
\end{titlepage}
""",
    "figure_align": "H",
    "tableofcontents": r"""
\tableofcontents
\clearpage
""",
}
