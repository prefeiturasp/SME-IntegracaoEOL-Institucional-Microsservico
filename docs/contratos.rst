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

- ``200 OK``: sucesso com dados
- ``204 No Content``: consulta válida, sem registros
- ``400 Bad Request``: parâmetros inválidos ou corpo malformado
- ``404 Not Found``: recurso específico não localizado
- ``501 Not Implemented``: endpoint de competência de outro microserviço
