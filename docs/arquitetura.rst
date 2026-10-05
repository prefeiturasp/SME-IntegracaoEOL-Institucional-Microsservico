Arquitetura
===========

Visão Geral
-----------

O microserviço institucional é um **consumidor de leitura** — ele não persiste dados,
apenas consulta as tabelas populadas pelo ETL institucional (``SME-SGP-MS-ETL``).

Fluxo de Dados
--------------

.. code-block:: text

    EOL (banco legado)
          │
          ▼
    SME-SGP-MS-ETL/apps/institucional
          │  (ETL: extrai, transforma e carrega)
          ▼
    Banco PostgreSQL Institucional
    ┌─────────────────────────────┐
    │  tipo_escola                │
    │  dre                        │
    │  sub_prefeitura             │
    │  unidade_educacional        │
    └─────────────────────────────┘
          │
          ▼
    SME-IntegracaoEOL-Institucional-Microsservico
          │  (leitura via models managed=False)
          ▼
    Transition Gateway
          │
          ▼
    SGP / outros consumidores

Estrutura de Domínios
---------------------

.. code-block:: text

    apps/
      core/           ← autenticação, middleware, tipos compartilhados
      dre/            ← DRE, TipoEscola, SubPrefeitura (models + selectors + views)
      unidade_educacional/  ← UnidadeEducacional (models + selectors + views)

Regras de Domínio
-----------------

- ``apps.dre`` não importa lógica interna de ``apps.unidade_educacional``
- ``apps.unidade_educacional`` pode usar models de ``apps.dre`` (banco compartilhado)
  mas não importa API, selectors ou services de DRE
- Nenhum domínio importa de microserviços externos (Professores, Alunos, Pedagógico)
- Tipos compartilhados ficam em ``apps.core.types``
