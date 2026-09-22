Performance
===========

Estratégia
----------

O microserviço é otimizado para leitura de alto volume via Transition Gateway.

Queries
-------

- ``listar_dres()``: query simples com ``.only()`` em 3 campos
- ``listar_escolas_por_dre()``: carrega DRE + TipoEscola + SubPrefeitura em lookups
  de memória (3 queries totais, independente do número de UEs)
- ``listar_unidades_por_dre()``: ``.values()`` + lookup de SubPrefeitura (2 queries)
- ``listar_equipamentos()``: ``.values()`` + lookups paralelos (4 queries máximo)

Sem N+1
-------

Todos os endpoints de lista carregam relacionamentos em dicionários antes do loop:

.. code-block:: python

    dres = {d.codigo_dre: d for d in DRE.objects.filter(...)}
    tipos = {t.codigo_tipo_escola: t for t in TipoEscola.objects.filter(...)}
    subs = {s.codigo_sub_prefeitura: s for s in SubPrefeitura.objects.filter(...)}

Índices Esperados no Banco
--------------------------

O ETL cria automaticamente:

- ``idx_ue_dre`` em ``unidade_educacional(codigo_dre)``
- ``idx_ue_tipo_escola`` em ``unidade_educacional(codigo_tipo_escola)``
- ``idx_ue_subprefeitura`` em ``unidade_educacional(codigo_sub_prefeitura)``

Endpoints Críticos
------------------

.. code-block:: text

    GET /api/dres/                     → ~1 query
    GET /api/dres/{cod}/escola/        → ~4 queries
    GET /api/dres/{cod}/ues/           → ~1 query
    GET /api/dres/{cod}/unidades/      → ~2 queries
    GET /api/escolas/{cod}/            → ~3 queries
    POST /api/escolas/                 → ~3 queries
    GET /api/escolas/todas-unidades/   → ~3 queries
    GET /api/escolas/equipamentos/     → ~4 queries

Medir via Django Debug Toolbar ou:

.. code-block:: bash

    docker compose -f docker-compose-dev.yml exec institucional \
      python manage.py shell -c "
    from django.test.utils import override_settings
    from django.db import connection, reset_queries
    from django.conf import settings
    settings.DEBUG = True
    reset_queries()
    from apps.dre.selectors import listar_dres
    listar_dres()
    print(len(connection.queries), 'queries')
    "
