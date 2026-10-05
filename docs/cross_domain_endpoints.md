# Endpoints Cross-Domain — Microserviço Institucional

Este documento lista todos os endpoints que pertencem a outro domínio mas são expostos
temporariamente pelo microserviço institucional como **placeholders** com status `501`.

O **Transition Gateway** é responsável por redirecionar estas chamadas para o microserviço correto.

---

## Matriz de Responsabilidades

| ID | Endpoint | Domínio Responsável | Dados Institucionais para o Gateway | Status |
|---|---|---|---|---|
| D03 | GET `/api/dres/{codigoEolDRE}/supervisores/` | **Professores** | `codigoEolDRE` (DRE existe no banco institucional) | 501 placeholder |
| E01 | GET `/api/escolas/{codigoUE}/administrador-sgp/` | **Professores/SSO** | `codigoUE` (UE existe no banco institucional) | 501 placeholder |
| E05 | GET `/api/escolas/{codigoEscola}/alunos/quantidade/` | **Alunos** | `codigoEscola` | 501 placeholder |
| E07 | GET `/api/escolas/{codigoEolEscola}/professores/{anoLetivo}/` | **Professores** | `codigoEolEscola`, `anoLetivo` | 501 placeholder |
| E08 | GET `/api/escolas/{codigoEolEscola}/professores/` | **Professores** | `codigoEolEscola` | 501 placeholder |
| E09 | GET `/api/escolas/modalidades_ensino/` | **Pedagógico** | — | 501 placeholder |
| E12 | GET `/api/escolas/{codigoUE}/salas/{tipoSala}/anos_letivos/{anoLetivo}/` | **Pedagógico** | `codigoUE` | 501 placeholder |
| E13 | GET `/api/escolas/{codigoUE}/funcionarios/` | **Professores** | `codigoUE` | 501 placeholder |
| E14 | GET `/api/escolas/{codigoUE}/funcionarios/cargos/{codigoCargo}/` | **Professores** | `codigoUE` | 501 placeholder |
| E15 | GET `/api/escolas/{codigoUE}/funcionarios/funcoes-externas/{codigoFuncaoExterna}/` | **Professores** | `codigoUE` | 501 placeholder |
| E16 | GET `/api/escolas/{codigoUE}/funcionarios/funcoes-atividades/{codigoFuncaoAtividade}/` | **Professores** | `codigoUE` | 501 placeholder |
| E18 | GET `/api/escolas/{codigoUE}/turmas/anos_letivos/{anoLetivo}/` | **Pedagógico** | `codigoUE` | 501 placeholder |
| E19 | GET `/api/escolas/{codigoUE}/turmasSondagem/anos_letivos/{anoLetivo}/` | **Pedagógico** | `codigoUE` | 501 placeholder |
| E20 | GET `/api/escolas/{ueCodigo}/funcionarios/cargos/` | **Professores** | `ueCodigo` | 501 placeholder |
| E21 | GET `/api/escolas/{ueCodigo}/funcionarios/funcoes-atividades/` | **Professores** | `ueCodigo` | 501 placeholder |
| E22 | GET `/api/escolas/{ueCodigo}/funcionarios/funcoes-externas/` | **Professores** | `ueCodigo` | 501 placeholder |
| E24 | GET `/api/escolas/{codigoEscola}/aluno/{codigoAluno}/matriculas/` | **Alunos** | `codigoEscola`, `codigoAluno` | 501 placeholder |

---

## Endpoints Institucionais (banco real)

| ID | Endpoint | Status |
|---|---|---|
| D01 | GET `/api/dres/` | ✅ Implementado |
| D02 | POST `/api/dres/` | ✅ Implementado |
| D04 | GET `/api/dres/{codigoEolDRE}/` | ✅ Implementado |
| D05 | GET `/api/dres/{codigoEolDRE}/escolas/{tipoEscola}/` | ✅ Implementado |
| D06 | GET `/api/dres/{codigoEolDRE}/escola/` | ✅ Implementado |
| D07 | GET `/api/dres/{dreCodigo}/subprefeituras/` | ✅ Implementado |
| D08 | GET `/api/dres/{dreCodigo}/ues/` | ✅ Implementado |
| D09 | GET `/api/dres/{codigoEolDRE}/escola/Sigpae/` | ✅ Implementado |
| D10 | GET `/api/dres/{dreCodigo}/unidades/` | ✅ Implementado |
| D11 | GET `/api/dres/{dreCodigo}/unidades/codigo-integracao/` | ✅ Implementado |
| E02 | GET `/api/escolas/{codigoEscolaEol}/` | ✅ Implementado |
| E03 | GET `/api/escolas/unidade-eol/{codigoEol}/` | ✅ Implementado |
| E04 | GET `/api/escolas/dados/{codigoEscolaEol}/` | ✅ Implementado |
| E06 | POST `/api/escolas/` | ✅ Implementado |
| E10 | GET `/api/escolas/tipos_unidade_educacao/` | ✅ Implementado |
| E11 | GET `/api/escolas/tiposEscolas/` | ✅ Implementado |
| E17 | GET `/api/escolas/{codigoEscolaEol}/subprefeituras/` | ✅ Implementado |
| E23 | GET `/api/escolas/{ueCodigo}/sincronizacoes-institucionais/` | ✅ Implementado |
| E25 | GET `/api/escolas/equipamentos/` | ✅ Implementado |
| E26 | POST `/api/escolas/unidades-parceiras/` | ✅ Implementado |
| E27 | GET `/api/escolas/todas-unidades/` | ✅ Implementado |

---

## Lacunas de Dados

Campos que não existem no ETL institucional e não podem ser retornados:

- `dtAtualizacao` em `TipoEscola` (E11): ETL não armazena data de atualização por tipo
- `dataAtualizacao` em `SincronizacaoUeContract` (E23): ETL não registra timestamp de sincronização por UE
- `tipoUnidadeAdmin` em `UnidadePredialContract` (D10): campo não mapeado no ETL atual

---

## Estratégia de Implementação no Gateway

Para os endpoints cross-domain, o Transition Gateway deve:

1. Chamar o microserviço institucional para obter o `codigoUE` ou `codigoDRE`
2. Passar o identificador para o microserviço correto (Professores, Alunos, Pedagógico)
3. Montar a resposta composta se necessário

Os placeholders `501` garantem que o Gateway detecte que a rota existe mas não é
implementada aqui, evitando silêncio (200 com dados incorretos).
