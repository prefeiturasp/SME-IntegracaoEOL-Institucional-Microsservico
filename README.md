# SME-IntegracaoEOL-Institucional-Microsservico

Microsserviço **mock** do domínio Institucional (DREs e Unidades Educacionais) SME-SP.

Todos os endpoints retornam dados estáticos sem banco de dados, sem regras de negócio para uso em testes de integração.

---

## Estrutura dos Apps

| App | Responsabilidade | Endpoints | Prefixo API |
|-----|-----------------|-----------|-------------|
| `apps.dre` | Diretorias Regionais de Educação e Subprefeituras | D01-D11 (exceto D03) | `/api/dres/` |
| `apps.unidade_educacional` | Unidades Educacionais (UEs), Equipamentos e Sincronização | E01-E27 (selecionados) | `/api/escolas/` |
| `apps.core` | Autenticação por API key, dados mock compartilhados | — | — |

### Modelos ETL Cobertos:

- **dre**: `Dre`, `DreSubprefeitura`
- **unidade_educacional**: `Escola` (Unidade Educacional), `Equipamento`, `SincronizacaoInstitucional`

---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (para rodar via container)

---

## Rodar localmente (sem Docker)

```bash
# 1. Copiar o .env
cp .env.example .env

# 2. Instalar dependências
pip install -r requirements/local.txt

# 3. Aplicar migrations (SQLite, apenas tabelas internas do Django)
python manage.py migrate

# 4. Rodar o servidor
python manage.py runserver 0.0.0.0:8001
```

Acesse em: http://localhost:8001/api/docs/

---

## Rodar com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: http://localhost:8001/api/docs/

---

## Autenticação

Todos os endpoints exigem o header `X-API-Key` com o valor configurado em `API_KEY` (`.env`).

Valor padrão em desenvolvimento: `dev-key-default`

```bash
curl -H "X-API-Key: dev-key-default" http://localhost:8001/api/dres/
```

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 (JSON/YAML) |

---

## Endpoints Implementados

### DREs

| ID | Método | Path | Descrição |
|----|--------|------|-----------|
| D01 | GET | `/api/dres/` | Lista todas as DREs |
| D02 | POST | `/api/dres/` | Filtra DREs por lista de códigos |
| D04 | GET | `/api/dres/{codigoEolDRE}/` | Retorna uma DRE pelo código EOL |
| D05 | GET | `/api/dres/{codigoEolDRE}/escolas/{tipoEscola}/` | Escolas filtradas por tipo |
| D06 | GET | `/api/dres/{codigoEolDRE}/escola/` | Escolas vinculadas a uma DRE |
| D07 | GET | `/api/dres/{codigoEolDRE}/subprefeituras/` | Subprefeituras de uma DRE |
| D08 | GET | `/api/dres/{dreCodigo}/ues/` | Códigos de UEs de uma DRE |
| D09 | GET | `/api/dres/{codigoEolDRE}/escola/Sigpae/` | Escolas para o sistema SIGPAE |
| D10 | GET | `/api/dres/{dreCodigo}/unidades/` | Unidades de gestão predial |
| D11 | GET | `/api/dres/{dreCodigo}/unidades/codigo-integracao/` | UEs com código de integração |

### Unidades Educacionais

| ID | Método | Path | Descrição |
|----|--------|------|-----------|
| E01 | GET | `/api/escolas/{ueCodigo}/administrador-sgp/` | Administradores SGP da UE |
| E02 | GET | `/api/escolas/{codigoEscolaEol}/` | Dados básicos de uma UE |
| E03 | GET | `/api/escolas/unidade-eol/{codigoEol}/` | UE por código EOL |
| E04 | GET | `/api/escolas/dados/{codigoEscolaEol}/` | Dados completos de uma UE |
| E06 | POST | `/api/escolas/` | Busca UEs por lista de códigos |
| E10 | GET | `/api/escolas/tipos_unidade_educacao/` | Lista tipos de unidades |
| E11 | GET | `/api/escolas/tiposEscolas/` | Código e sigla de tipos de escola |
| E17 | GET | `/api/escolas/{codigoEscolaEol}/subprefeituras/` | Subprefeituras da unidade |
| E23 | GET | `/api/escolas/{ueCodigo}/sincronizacoes-institucionais/` | Detalhes para sincronização |
| E25 | GET | `/api/escolas/equipamentos/` | Equipamentos SME com filtro |
| E26 | POST | `/api/escolas/unidades-parceiras/` | Unidades parceiras por códigos |
| E27 | GET | `/api/escolas/todas-unidades/` | Lista todas as UEs |

---

## Referências

- Contrato completo: `../swagger_contrato_microsservico.md`
- Projeto ETL de referência: `../SME-SGP-MS-ETL/`