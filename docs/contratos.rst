Contratos
=========

Os contratos de resposta são definidos como ``TypedDict`` em:

- ``apps/dre/contracts.py``
- ``apps/unidade_educacional/contracts.py``
- ``apps/core/types.py`` (tipos compartilhados)

Nomes de campos seguem o padrão camelCase do legado EOL.
A conversão de snake_case (interno) para camelCase (resposta HTTP)
é feita nos selectors/presenters antes de retornar o TypedDict.

Regra geral de status HTTP:

- ``200 OK``: sucesso, incluindo listas vazias conforme o endpoint
- ``204 No Content``: consulta válida sem registros, conforme o endpoint
- ``400 Bad Request``: parâmetros inválidos ou corpo malformado
- ``404 Not Found``: recurso específico não localizado
- ``501 Not Implemented``: endpoint de competência de outro microserviço

Nas consultas consolidadas, :ref:`endpoint-d12` retorna ``204`` sem corpo
quando não há escolas e o filtro de tipo está ausente; com filtro, retorna
``200`` com ``[]``. :ref:`endpoint-d13` e :ref:`endpoint-e28` sempre retornam
``200`` com ``[]`` nas consultas válidas sem resultados.

O formato da resposta de D13 depende de ``retorno``. Em E28, depende de
``apenasParceiras``. Consulte os parâmetros e exemplos na página de
:doc:`endpoints`.
