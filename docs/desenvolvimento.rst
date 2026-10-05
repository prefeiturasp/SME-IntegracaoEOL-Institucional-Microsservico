Desenvolvimento
===============

Variáveis de Ambiente
---------------------

Copie ``.env.example`` para ``.env`` e ajuste:

.. code-block:: bash

    cp .env.example .env

.. code-block:: ini

    DJANGO_SECRET_KEY=troque-por-uma-chave-secreta-forte
    DJANGO_DEBUG=1
    DJANGO_ALLOWED_HOSTS=*
    API_KEY=dev-key-default
    API_KEY_HEADER=X-API-Key
    URL_BANCO_INSTITUCIONAL=postgres://user:password@host:5432/institucional
    APP_PREFIX=
    CACHE_TTL_DRE_SECONDS=300
    CACHE_TTL_TIPO_ESCOLA_SECONDS=900

Executar com Docker (produção)
------------------------------

.. code-block:: bash

    docker compose up --build

Executar com Docker (desenvolvimento + debugpy)
-----------------------------------------------

.. code-block:: bash

    docker compose -f docker-compose-dev.yml up --build

A porta ``5679`` expõe o debugpy para attach do VS Code.

Testes
------

.. code-block:: bash

    # Dentro do container
    docker compose -f docker-compose-dev.yml exec institucional \
      python -m pytest apps/ tests/ --cov=apps --cov-report=term-missing --cov-fail-under=90

Lint
----

.. code-block:: bash

    docker compose -f docker-compose-dev.yml exec institucional bash -c "
      ruff check . &&
      black --check . &&
      isort --check-only . &&
      mypy apps config
    "

Swagger / OpenAPI
-----------------

Com o container rodando, acesse:

- ``http://localhost:8002/api/docs/`` — Swagger UI
- ``http://localhost:8002/api/schema/`` — schema YAML

Gerar schema estático:

.. code-block:: bash

    docker compose -f docker-compose-dev.yml exec institucional \
      python manage.py spectacular --file schema.yml

Gerar documentação Sphinx
--------------------------

Gere a documentação HTML:

.. code-block:: bash

    docker compose -f docker-compose-dev.yml exec institucional bash -c "
      sphinx-build -b html docs/ docs/_build/html
    "

A documentação gerada ficará em ``docs/_build/html/index.html``.

O Sphinx está configurado com:

- ``autodoc``: extrai docstrings dos módulos Python automaticamente.
- ``napoleon``: interpreta docstrings no padrão Google (``Args``, ``Returns``, ``Raises``).
- ``viewcode``: adiciona links para o código-fonte em cada símbolo documentado.
- ``intersphinx``: links cruzados para a documentação do Python e do Django.
