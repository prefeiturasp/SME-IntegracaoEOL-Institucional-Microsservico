# SME-IntegracaoEOL-Institucional-Microsservico

Microserviço do domínio **Institucional** (DREs e Unidades Educacionais) — SME-SP.

Consome dados do banco institucional populado pelo ETL `SME-SGP-MS-ETL/apps/institucional`.
Disponibiliza rotas compatíveis com a API EOL legada para uso pelo **Transition Gateway**.

> **Não persiste dados.** Todos os models usam `managed = False`.

---

## Estrutura

```
apps/
  core/                   ← autenticação, middleware, tipos compartilhados
    authentication.py     ← ApiKeyAuthentication
    middleware.py         ← PrefixMiddleware (APP_PREFIX para Ingress)
    types.py              ← TypedDicts compartilhados entre domínios
  dre/                    ← DRE, TipoEscola, SubPrefeitura
    models.py             ← managed=False, leitura do banco institucional
    contracts.py          ← TypedDicts do contrato EOL para DRE
    selectors.py          ← queries otimizadas (sem N+1)
    api/views.py          ← views D01-D11
    api/urls.py
    tests/
  unidade_educacional/    ← UnidadeEducacional
    models.py             ← managed=False
    contracts.py          ← TypedDicts do contrato EOL para UE
    selectors.py          ← queries otimizadas
    api/views.py          ← views E01-E27 (institucionais + placeholders cross-domain)
    api/urls.py
    tests/
tests/
  test_domain_imports.py  ← lint estático: impede imports cruzados entre domínios
docs/                     ← Sphinx + Markdown de referência
```

---

## Pré-requisitos

- Docker e Docker Compose

---

## Variáveis de Ambiente

```bash
cp .env.example .env
```

| Variável | Descrição | Padrão |
|---|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta Django | — |
| `DJANGO_DEBUG` | Debug mode | `1` |
| `API_KEY` | Chave de autenticação da API | `dev-key-default` |
| `API_KEY_HEADER` | Nome do header | `X-API-Key` |
| `URL_BANCO_INSTITUCIONAL` | URL PostgreSQL do banco institucional | SQLite in-memory |
| `APP_PREFIX` | Prefixo de path no Ingress (ex: `institucional`) | vazio |
| `CACHE_TTL_DRE_SECONDS` | TTL de cache para DREs | `300` |
| `CACHE_TTL_TIPO_ESCOLA_SECONDS` | TTL de cache para tipos de escola | `900` |

---

## Executar com Docker

### Produção

```bash
docker compose up --build
```

### Desenvolvimento (com debugpy na porta 5679)

```bash
docker compose -f docker-compose-dev.yml up --build
```

Acesse: `http://localhost:8002/api/docs/`

---

## Autenticação

Todos os endpoints exigem o header `X-API-Key`:

```bash
curl -H "X-API-Key: dev-key-default" http://localhost:8002/api/dres/
```

---

## Documentação da API

| URL | Descrição |
|---|---|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 |

### Gerar schema estático

```bash
docker compose -f docker-compose-dev.yml exec institucional \
  python manage.py spectacular --file schema.yml
```

---

## Testes

Os testes usam SQLite in-memory isolado via `config.settings_test` — nunca tocam o banco de QA.

```bash
# Executar todos os testes com cobertura (≥95%)
docker compose -f docker-compose-dev.yml exec \
  -e DJANGO_SETTINGS_MODULE=config.settings_test institucional \
  python -m pytest apps/ tests/ \
  --cov=apps --cov-report=term-missing --cov-fail-under=95

# Via Makefile (equivalente ao comando acima)
make test

# Apenas os testes de DRE
docker compose -f docker-compose-dev.yml exec \
  -e DJANGO_SETTINGS_MODULE=config.settings_test institucional \
  python -m pytest apps/dre/tests/ -v

# Lint de imports e governança arquitetural
docker compose -f docker-compose-dev.yml exec \
  -e DJANGO_SETTINGS_MODULE=config.settings_test institucional \
  python -m pytest tests/ -v
```

---

## Lint e Qualidade

```bash
docker compose -f docker-compose-dev.yml exec institucional bash -c "
  ruff check . &&
  black --check . &&
  isort --check-only . &&
  mypy apps config
"
```

---

## Documentação Sphinx

A documentação técnica é gerada com [Sphinx](https://www.sphinx-doc.org/) a partir das docstrings
do código (padrão Google) e das páginas `.rst` em `docs/`.

```bash
# Gerar HTML (requer container dev rodando)
make docs
```

O resultado fica em `docs/_build/html/index.html`.

Para gerar sem o Makefile:

```bash
docker compose -f docker-compose-dev.yml exec institucional \
  sphinx-build -b html docs/ docs/_build/html
```

Extensões ativas:

| Extensão | Função |
|---|---|
| `autodoc` | Extrai docstrings dos módulos Python automaticamente |
| `napoleon` | Interpreta docstrings no padrão Google (`Args`, `Returns`, `Raises`) |
| `viewcode` | Adiciona links para o código-fonte em cada símbolo documentado |
| `autosectionlabel` | Permite referenciar seções entre páginas via `:ref:` |
| `intersphinx` | Links cruzados para a documentação do Python e do Django |

---

## Endpoints

### Abrangência — `/api/v1/institucional/abrangencia/`

| Método | Path | Descrição |
|---|---|---|
| GET | `/api/v1/institucional/abrangencia/codigos-dres/` | Lista os códigos das DREs |
| GET | `/api/v1/institucional/abrangencia/nome-abreviacao-dres/` | Lista código, nome e abreviação das DREs |

### DREs — `/api/dres/`

| ID | Método | Path | Status |
|---|---|---|---|
| D01 | GET | `/api/dres/` | ✅ Banco real |
| D02 | POST | `/api/dres/` | ✅ Banco real |
| D03 | GET | `/api/dres/{codigoEolDRE}/supervisores/` | ⚠️ Cross-domain Professores (501) |
| D04 | GET | `/api/dres/{codigoEolDRE}/` | ✅ Banco real |
| D05 | GET | `/api/dres/{codigoEolDRE}/escolas/{tipoEscola}/` | ✅ Banco real |
| D06 | GET | `/api/dres/{codigoEolDRE}/escola/` | ✅ Banco real |
| D07 | GET | `/api/dres/{dreCodigo}/subprefeituras/` | ✅ Banco real |
| D08 | GET | `/api/dres/{dreCodigo}/ues/` | ✅ Banco real |
| D09 | GET | `/api/dres/{codigoEolDRE}/escola/Sigpae/` | ✅ Banco real |
| D10 | GET | `/api/dres/{dreCodigo}/unidades/` | ✅ Banco real |
| D11 | GET | `/api/dres/{dreCodigo}/unidades/codigo-integracao/` | ✅ Banco real |

### Escola/UE — `/api/escolas/`

| ID | Método | Path | Status |
|---|---|---|---|
| E01 | GET | `/api/escolas/{codigoUE}/administrador-sgp/` | ⚠️ Cross-domain Professores (501) |
| E02 | GET | `/api/escolas/{codigoEscolaEol}/` | ✅ Banco real |
| E03 | GET | `/api/escolas/unidade-eol/{codigoEol}/` | ✅ Banco real |
| E04 | GET | `/api/escolas/dados/{codigoEscolaEol}/` | ✅ Banco real |
| E05 | GET | `/api/escolas/{codigoEscola}/alunos/quantidade/` | ⚠️ Cross-domain Alunos (501) |
| E06 | POST | `/api/escolas/` | ✅ Banco real |
| E07-E08 | GET | `.../professores/...` | ⚠️ Cross-domain Professores (501) |
| E09 | GET | `/api/escolas/modalidades_ensino/` | ⚠️ Cross-domain Pedagógico (501) |
| E10 | GET | `/api/escolas/tipos_unidade_educacao/` | ✅ Banco real |
| E11 | GET | `/api/escolas/tiposEscolas/` | ✅ Banco real |
| E12 | GET | `.../salas/.../anos_letivos/...` | ⚠️ Cross-domain Pedagógico (501) |
| E13-E16, E20-E22 | GET | `.../funcionarios/...` | ⚠️ Cross-domain Professores (501) |
| E17 | GET | `/api/escolas/{codigoEscolaEol}/subprefeituras/` | ✅ Banco real |
| E18-E19 | GET | `.../turmas/...` | ⚠️ Cross-domain Pedagógico (501) |
| E23 | GET | `/api/escolas/{ueCodigo}/sincronizacoes-institucionais/` | ✅ Banco real |
| E24 | GET | `.../aluno/.../matriculas/` | ⚠️ Cross-domain Alunos (501) |
| E25 | GET | `/api/escolas/equipamentos/` | ✅ Banco real |
| E26 | POST | `/api/escolas/unidades-parceiras/` | ✅ Banco real |
| E27 | GET | `/api/escolas/todas-unidades/` | ✅ Banco real |

Ver `docs/cross_domain_endpoints.md` para detalhes dos endpoints cross-domain.

---

## Status HTTP

| Código | Significado |
|---|---|
| 200 | Sucesso com dados |
| 204 | Consulta válida, sem registros |
| 400 | Parâmetros inválidos |
| 401/403 | API key ausente ou inválida |
| 404 | Recurso não encontrado |
| 501 | Endpoint de outro domínio (cross-domain) |

---

## Referências

- ETL institucional: `SME-SGP-MS-ETL/apps/institucional`
- Mapeamento de endpoints: `MAPEAMENTO_ENDPOINTS_API_EOL_DOMINIO_INSTITUCIONAL.pdf`
- Microserviço Professores (padrão estrutural): `SME-IntegracaoEOL-Professores-Microsservico`
