COMPOSE      = docker compose -f docker-compose-dev.yml
EXEC         = $(COMPOSE) exec institucional
RUN_TEST     = $(COMPOSE) run --rm -e DJANGO_SETTINGS_MODULE=config.settings_test institucional
PYTEST_ARGS ?= --cov=apps --cov-report=term-missing --cov-fail-under=95

.PHONY: run build stop test lint coverage docs schema help

help:
	@echo "Targets disponíveis:"
	@echo "  make run       — sobe o serviço em modo dev (porta 8002, debugpy 5679)"
	@echo "  make build     — rebuild da imagem dev"
	@echo "  make stop      — para e remove containers"
	@echo "  make test      — roda todos os testes com cobertura ≥95%"
	@echo "  make lint      — ruff + black + isort + mypy"
	@echo "  make coverage  — relatório de cobertura HTML (abre em docs/_cov/)"
	@echo "  make docs      — gera documentação Sphinx em docs/_build/html/"
	@echo "  make schema    — gera schema OpenAPI em schema.yml"

run:
	$(COMPOSE) up

build:
	$(COMPOSE) up --build

stop:
	$(COMPOSE) down

test:
	$(RUN_TEST) python -m pytest $(PYTEST_ARGS) -v

lint:
	$(EXEC) bash -c "\
		ruff check . && \
		black --check . && \
		isort --check-only . && \
		mypy apps config"

coverage:
	$(RUN_TEST) python -m pytest $(PYTEST_ARGS) \
		--cov-report=html:docs/_cov
	@echo "Relatório gerado em docs/_cov/index.html"

docs:
	$(EXEC) bash -c "sphinx-build -b html docs/ docs/_build/html"
	@echo "Documentação gerada em docs/_build/html/index.html"

schema:
	$(EXEC) python manage.py spectacular --file schema.yml
	@echo "Schema gerado em schema.yml"
