Endpoints
=========

Ver documentação interativa em ``/api/docs/``.

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

DRE — base ``/api/dres/``
--------------------------

.. list-table::
   :header-rows: 1

   * - ID
     - Método
     - Endpoint
     - Status
   * - D01
     - GET
     - ``/api/dres/``
     - ✅ Implementado
   * - D02
     - POST
     - ``/api/dres/``
     - ✅ Implementado
   * - D03
     - GET
     - ``/api/dres/{codigoEolDRE}/supervisores/``
     - ⚠️ Cross-domain Professores (501)
   * - D04
     - GET
     - ``/api/dres/{codigoEolDRE}/``
     - ✅ Implementado
   * - D05
     - GET
     - ``/api/dres/{codigoEolDRE}/escolas/{tipoEscola}/``
     - ✅ Implementado
   * - D06
     - GET
     - ``/api/dres/{codigoEolDRE}/escola/``
     - ✅ Implementado
   * - D07
     - GET
     - ``/api/dres/{dreCodigo}/subprefeituras/``
     - ✅ Implementado
   * - D08
     - GET
     - ``/api/dres/{dreCodigo}/ues/``
     - ✅ Implementado
   * - D09
     - GET
     - ``/api/dres/{codigoEolDRE}/escola/Sigpae/``
     - ✅ Implementado
   * - D10
     - GET
     - ``/api/dres/{dreCodigo}/unidades/``
     - ✅ Implementado
   * - D11
     - GET
     - ``/api/dres/{dreCodigo}/unidades/codigo-integracao/``
     - ✅ Implementado

Escola/UE — base ``/api/escolas/``
------------------------------------

Ver ``cross_domain.rst`` para endpoints com status 501.

Todos os endpoints E01-E27 estão registrados nas URLs.
Os endpoints institucionais retornam 200/204/400/404.
Os cross-domain retornam 501 com ``{"dominio": "<responsável>"}``.
