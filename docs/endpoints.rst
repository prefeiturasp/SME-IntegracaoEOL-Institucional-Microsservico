Endpoints
=========

Ver documentação interativa em ``/api/v1/institucional/docs/`` e schema
OpenAPI em ``/api/v1/institucional/schema/``.

As consultas consolidadas D12, D13 e E28 usam o prefixo
``/api/v1/institucional/``. Exigem autenticação por API key no header
configurado (por padrão, ``X-API-Key``) e não recebem corpo no GET.

Abrangência — base ``/api/v1/institucional/abrangencia/``
----------------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Método
     - Endpoint
     - Status
   * - GET
     - ``/api/v1/institucional/abrangencia/codigos-dres/``
     - ✅ Implementado
   * - GET
     - ``/api/v1/institucional/abrangencia/nome-abreviacao-dres/``
     - ✅ Implementado

DRE
---

Base: ``/api/v1/institucional/dres/``.

.. list-table::
   :header-rows: 1

   * - ID
     - Método
     - Endpoint
     - Status
   * - D01
     - GET
     - ``/api/v1/institucional/dres/``
     - ✅ Implementado
   * - D02
     - POST
     - ``/api/v1/institucional/dres/``
     - ✅ Implementado
   * - D03
     - GET
     - ``/api/v1/institucional/dres/{codigoEolDRE}/supervisores/``
     - ⚠️ Cross-domain Professores (501)
   * - D04
     - GET
     - ``/api/v1/institucional/dres/{codigoEolDRE}/``
     - ✅ Implementado
   * - D05
     - GET
     - ``/api/v1/institucional/dres/{codigoEolDRE}/escolas/{tipoEscola}/``
     - Depreciado; usar :ref:`endpoint-d12`
   * - D06
     - GET
     - ``/api/v1/institucional/dres/{codigoEolDRE}/escola/``
     - Depreciado; usar :ref:`endpoint-d12`
   * - D07
     - GET
     - ``/api/v1/institucional/dres/{dreCodigo}/subprefeituras/``
     - ✅ Implementado
   * - D08
     - GET
     - ``/api/v1/institucional/dres/{dreCodigo}/ues/``
     - Depreciado; usar :ref:`endpoint-d13`
   * - D09
     - GET
     - ``/api/v1/institucional/dres/{codigoEolDRE}/escola/Sigpae/``
     - Depreciado; usar :ref:`endpoint-d12`
   * - D10
     - GET
     - ``/api/v1/institucional/dres/{dreCodigo}/unidades/``
     - Depreciado; usar :ref:`endpoint-d13`
   * - D11
     - GET
     - ``/api/v1/institucional/dres/{dreCodigo}/unidades/codigo-integracao/``
     - Depreciado; usar :ref:`endpoint-d13`
   * - D12
     - GET
     - ``/api/v1/institucional/dres/{codigo_eol_dre}/escolas/``
     - Implementado; ver :ref:`endpoint-d12`
   * - D13
     - GET
     - ``/api/v1/institucional/dres/{codigo_eol_dre}/unidades/consolidadas/``
     - Implementado; ver :ref:`endpoint-d13`

Escola/UE
---------

Base: ``/api/v1/institucional/escolas/``.

Ver ``cross_domain.rst`` para endpoints com status 501.

Todos os endpoints E01-E28 estão registrados nas URLs.
Os endpoints institucionais retornam 200/204/400/404.
Os cross-domain retornam 501 com ``{"dominio": "<responsável>"}``.

.. list-table::
   :header-rows: 1

   * - ID
     - Método
     - Endpoint
     - Status
   * - E06
     - POST
     - ``/api/v1/institucional/escolas/``
     - Depreciado; usar :ref:`endpoint-e28`
   * - E26
     - POST
     - ``/api/v1/institucional/escolas/unidades-parceiras/``
     - Depreciado; usar :ref:`endpoint-e28`
   * - E28
     - GET
     - ``/api/v1/institucional/escolas/unidades/``
     - Implementado; ver :ref:`endpoint-e28`

Consultas consolidadas
------------------------

Os exemplos abaixo são ilustrativos. Os endpoints retornam arrays sem paginação.

.. _endpoint-d12:

D12 — Escolas por DRE
~~~~~~~~~~~~~~~~~~~~~~~~

``GET /api/v1/institucional/dres/{codigo_eol_dre}/escolas/``

Lista as escolas vinculadas à DRE, com filtro opcional por tipo de escola.

.. list-table:: Parâmetros
   :header-rows: 1

   * - Nome
     - Local
     - Regra
   * - ``codigo_eol_dre``
     - Rota
     - String obrigatória, não pode conter apenas espaços.
   * - ``tipo_escola_id``
     - Query
     - Inteiro opcional, maior ou igual a zero. Ausente: todos os tipos.

O filtro inclui os subtipos CEU associados: 1 inclui 16; 2 inclui 17;
10 inclui 18; 28 inclui 31. As escolas são ordenadas pelo código EOL.

.. code-block:: http

   GET /api/v1/institucional/dres/108100/escolas/?tipo_escola_id=1 HTTP/1.1

A resposta usa :class:`~apps.dre.contracts.EscolaPorDreContract`:

.. code-block:: json

   [
     {
       "codigoEscola": "019251",
       "nomeEscola": "ESCOLA EXEMPLO",
       "codigoDRE": "108100",
       "tipoEscola": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
       "siglaTipoEscola": "EMEF",
       "nomeDRE": "DRE EXEMPLO",
       "siglaDRE": "DRE-EX",
       "codigoSubprefeitura": "13",
       "nomeSubprefeitura": "SUBPREFEITURA EXEMPLO",
       "tipoEscolaId": 1,
       "tipoUnidadeId": 1,
       "subprefeituraId": 13,
       "dreId": "108100",
       "codigoIntegracao": "INT001"
     }
   ]

- ``200``: lista de escolas; com filtro, pode ser ``[]``.
- ``204``: consulta sem filtro e sem escolas, inclusive para DRE inexistente.
  Não há corpo na resposta.
- ``400``: código da DRE em branco ou tipo inválido.

.. _endpoint-d13:

D13 — Unidades por DRE
~~~~~~~~~~~~~~~~~~~~~~~~~

``GET /api/v1/institucional/dres/{codigo_eol_dre}/unidades/consolidadas/``

Consulta as unidades da DRE em um dos três formatos definidos por ``retorno``.
O código da DRE é uma string obrigatória na rota e não pode conter apenas espaços.
``retorno`` é opcional na query e tem padrão ``completo``.

.. list-table:: Formatos de resposta
   :header-rows: 1

   * - ``retorno``
     - Conteúdo
   * - ``completo``
     - Array de :class:`~apps.dre.contracts.UnidadePredialContract`,
       com dados prediais, endereço, vagas e contatos.
   * - ``codigos``
     - Array de códigos EOL como strings.
   * - ``integracao``
     - Array de :class:`~apps.dre.contracts.CodigoIntegracaoContract`.
       O código de integração pode ser nulo.

As unidades são ordenadas pelo código EOL em todos os formatos.

.. code-block:: http

   GET /api/v1/institucional/dres/108100/unidades/consolidadas/?retorno=completo HTTP/1.1

Exemplo do formato ``completo``; a grafia ``logadouro`` pertence ao contrato:

.. code-block:: json

   [
     {
       "codigoEol": "019251",
       "nomeOficial": "ESCOLA EXEMPLO",
       "nomeNaoOficial": null,
       "tipoUnidadeAdmin": "DIRETORIA REGIONAL DE EDUCACAO",
       "tipoUE": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
       "logadouro": "RUA EXEMPLO",
       "numero": "100",
       "bairro": "BAIRRO EXEMPLO",
       "cep": 1310100,
       "distrito": "DISTRITO EXEMPLO",
       "subPrefeitura": "SUBPREFEITURA EXEMPLO",
       "nomeDre": "DRE EXEMPLO",
       "email": null,
       "telefone1": null,
       "telefone2": null,
       "anoConstrucao": null,
       "propriedade": null,
       "capacidadeVagasMatutino": 100,
       "capacidadeVagasVespertino": 100,
       "capacidadeVagasNoturno": 0,
       "capacidadeVagasIntermediario": 0,
       "capacidadeVagasIntegral": 0,
       "capacidadeVagasTotal": 200,
       "organizacaoParceira": false,
       "quantidadeDeFuncionarios": 20,
       "status": "ATIVO",
       "subprefeituraId": 13,
       "tipoUnidadeAdmId": 24
     }
   ]

Com ``retorno=codigos``:

.. code-block:: json

   ["019251", "019252"]

Com ``retorno=integracao``:

.. code-block:: json

   [
     {
       "codigoUe": "019251",
       "nomeUe": "ESCOLA EXEMPLO",
       "codigoIntegracao": "INT001",
       "tipoEscolaId": 1,
       "tipoUnidadeId": 1,
       "subprefeituraId": 13,
       "dreId": "108100"
     }
   ]

- ``200``: lista no formato solicitado. Sem unidades correspondentes,
  retorna ``[]`` em qualquer formato.
- ``400``: código da DRE em branco ou ``retorno`` vazio/desconhecido.

.. _endpoint-e28:

E28 — Unidades por códigos EOL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``GET /api/v1/institucional/escolas/unidades/``

Consulta as unidades dos códigos informados, com filtro opcional de parceiras.

.. list-table:: Parâmetros de query
   :header-rows: 1

   * - Nome
     - Tipo
     - Regra
   * - ``codigos``
     - Lista de strings
     - Obrigatória. Repetir o parâmetro para cada código EOL.
       Códigos vazios ou compostos apenas por espaços são rejeitados.
   * - ``apenasParceiras``
     - Booleano
     - Opcional, padrão ``false``. Com ``true``, restringe às parceiras.

Com ``apenasParceiras=false`` ou ausente, inclui parceiras e não parceiras,
ordenadas por nome. Retorna :class:`~apps.unidade_educacional.contracts.UeBasicaContract`:

.. code-block:: http

   GET /api/v1/institucional/escolas/unidades/?codigos=019251&codigos=019252 HTTP/1.1

.. code-block:: json

   [
     {
       "codigoEscola": "019251",
       "nomeEscola": "ESCOLA EXEMPLO",
       "nomeDRE": "DRE EXEMPLO",
       "siglaDRE": "DRE-EX",
       "codigoDRE": "108100",
       "tipoEscola": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
       "siglaTipoEscola": "EMEF",
       "codigoTipoEscola": 1,
       "tipoEscolaId": 1,
       "tipoUnidadeId": 1,
       "subprefeituraId": 13,
       "dreId": "108100",
       "codigoIntegracao": "INT001"
     }
   ]

Com ``apenasParceiras=true``, retorna
:class:`~apps.unidade_educacional.contracts.UnidadeParceirasContract`.
O nome recebe a sigla do tipo quando ainda não começa com ela;
o e-mail pode ser nulo. Não há ordenação explícita nessa opção.

.. code-block:: http

   GET /api/v1/institucional/escolas/unidades/?codigos=019252&apenasParceiras=true HTTP/1.1

.. code-block:: json

   [
     {
       "codigo": "019252",
       "nome": "CEI UNIDADE PARCEIRA EXEMPLO",
       "email": null
     }
   ]

- ``200``: lista de unidades. Códigos inexistentes são omitidos.
  Sem correspondências, inclusive quando não há parceiras entre os códigos
  informados, retorna ``[]``.
- ``400``: códigos ausentes/vazios ou booleano inválido.

Migração das rotas depreciadas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As rotas antigas continuam disponíveis, marcadas como depreciadas no OpenAPI.
Use os novos GETs conforme a tabela. Todas as rotas abaixo são relativas a
``/api/v1/institucional/``.

.. list-table::
   :header-rows: 1

   * - Origem
     - Substituto
   * - D05: ``GET dres/{codigo_eol_dre}/escolas/{tipo_escola_id}/``
     - D12 com ``tipo_escola_id`` na query.
   * - D06: ``GET dres/{codigo_eol_dre}/escola/``
     - D12 sem filtro de tipo.
   * - D09: ``GET dres/{codigo_eol_dre}/escola/Sigpae/``
     - D12 sem filtro de tipo.
   * - D08: ``GET dres/{dre_codigo}/ues/``
     - D13 com ``retorno=codigos``, preservando o array de códigos EOL.
   * - D10: ``GET dres/{dre_codigo}/unidades/``
     - D13 com ``retorno=completo`` ou sem o parâmetro.
   * - D11: ``GET dres/{dre_codigo}/unidades/codigo-integracao/``
     - D13 com ``retorno=integracao``.
   * - E06: ``POST escolas/``
     - E28 com ``apenasParceiras=false`` ou ausente.
   * - E26: ``POST escolas/unidades-parceiras/``
     - E28 com ``apenasParceiras=true``.

Na migração dos POSTs para E28, enviar os códigos como parâmetros ``codigos``
repetidos na query, em vez do array JSON no corpo.
