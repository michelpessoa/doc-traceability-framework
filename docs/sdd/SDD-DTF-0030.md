---
id: SDD-DTF-0030
type: SDD
title: "Paralelismo derivado: campo arquivos por RF, tabela de tasks na SDD, script parallel_plan.py"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0010"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0010.md"
  - id: "ADR-DTF-0003"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0003.md"
consumption_instructions: "Implementar as 7 RFs consolidadas abaixo. As duas cópias do kit (_framework/templates e _framework/skills/doc-traceability-framework/templates, mesmo repositório) precisam ficar byte a byte iguais para o par template/script correspondente — verifique com diff antes de marcar cada task como concluída. Não sincronizar a cópia do viverMelhor nesta SDD além do que a última task pedir; isso é responsabilidade de uma sessão aberta naquele repositório."
supersedes: null
superseded_by: null
tags: [paralelismo, sdd, spec, execucao, tooling]
---

# Paralelismo derivado: campo arquivos por RF, tabela de tasks na SDD, script parallel_plan.py

## Resumo executivo

Adiciona um sinal estrutural — não uma heurística de linguagem natural
nem um grafo desenhado à mão — que permite derivar automaticamente
quais RFs/tasks/SDDs de um projeto sob este framework são seguros de
implementar em paralelo: uma coluna `Arquivos` por RF na SPEC, uma
seção "Decomposição em tasks" na SDD, e um script (`parallel_plan.py`)
que cruza essas listas por interseção de conjunto e imprime grupos
paralelizáveis e pares bloqueados. É só sinal informativo: não é gate,
não bloqueia commit, não dispara execução sozinho.

## Decisão(ões) de arquitetura aplicável(is)

ADR-DTF-0003: paralelismo derivado de campo estrutural de arquivos, não
de grafo manual nem de heurística de IA sobre prosa livre. Trade-off
aceito: verbosidade adicional em SPEC/SDD (campo/tabela extra) em troca
de sinal determinístico e persistido no próprio documento.

## Requisitos consolidados

(Consolidado de SPEC-DTF-0010, Parte 1.)

| RF-ID | Requisito |
|---|---|
| RF01 | Template de SPEC ganha coluna `Arquivos` na tabela de "Requisitos funcionais" (Parte 1). |
| RF02 | Template de SDD ganha seção "Decomposição em tasks" entre "Especificação técnica consolidada" e "Critérios de aceite". |
| RF03 | Script deriva, de uma ou mais SDDs, grupos de tasks/SDDs sem interseção de arquivo (paralelizáveis) e pares com interseção (bloqueados). |
| RF04 | Interseção de arquivo força bloqueio mesmo sem `depends_on` declarado — ausência de dependência não é paralelismo automático quando há overlap. |
| RF05 | Linha com coluna de arquivos vazia (sem `(decisão pura)`) gera aviso e é excluída do cálculo, sem interromper a execução do script. |
| RF06 | Gate de qualidade de conteúdo (`validate_doc.py`) falha se alguma linha de RF (SPEC) ou task (SDD) tiver coluna de arquivos vazia e diferente de `(decisão pura)`. |
| RF07 | Seção "Decomposição em tasks" é opcional quando a SDD herdar sizing `small` da SPEC de origem ou tiver um único RF consolidado — gate não falha pela ausência nesse caso. |

Casos de borda consolidados (ver SPEC-DTF-0010 para detalhe completo):
path inexistente no disco não é erro (script não faz `stat`); duas
tasks com mesmo RF mas arquivos diferentes são paralelizáveis; SDD sem
a seção (caso RF07) usa `arquivos:` da SPEC via `source_docs` ou
reporta "sem tasks declaradas"; script nunca compara paths entre
repositórios de projetos diferentes; glob (`src/**/*.ts`) casa por
`fnmatch`/prefixo, não igualdade exata de string.

## Especificação técnica consolidada

(Consolidado de SPEC-DTF-0010, Parte 2 — contratos, plano de
implementação e rollout completos estão na SPEC; aqui só o necessário
para implementar sem reabrir o documento de origem.)

**Contratos:**
- `_framework/templates/spec.template.md` — tabela de RFs ganha coluna
  `Arquivos` (path relativo ao repo do projeto, separado por vírgula
  se houver mais de um, ou `(decisão pura)`).
- `_framework/templates/sdd.template.md` — nova seção "Decomposição em
  tasks": `# | Task | RF(s) de origem | Arquivos tocados | Depende de (#)`.
- `_framework/scripts/parallel_plan.py` — `derive_groups(entries:
  list[TaskEntry]) -> ParallelPlan`, `TaskEntry = {source: str, label:
  str, files: list[str], depends_on: list[str]}`, `ParallelPlan =
  {parallel_groups: list[list[str]], blocked_pairs: list[tuple[str,
  str, list[str]]]}`. CLI: `python3 _framework/scripts/parallel_plan.py
  <sdd1.md> [sdd2.md ...]` (texto) e `--json` (estruturado).
- `_framework/scripts/validate_doc.py` — novo item de checklist:
  coluna de arquivos vazia (RF06) e seção "Decomposição em tasks"
  ausente sem dispensa por sizing/RF único (RF07).

**Rollout:** não retroativo — SDD/SPEC já `approved`/`implemented` não
ganham a seção nova. Nenhuma migração de dado.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — coluna `Arquivos` na tabela de RF do template de SPEC | `grep -A2 "Requisitos funcionais" _framework/templates/spec.template.md \| grep "Arquivos"` | Coluna `Arquivos` presente no cabeçalho da tabela, nas duas cópias |
| 2 | RF02 — seção "Decomposição em tasks" no template de SDD, na posição certa | `grep -n "Decomposição em tasks\|Especificação técnica consolidada\|Critérios de aceite" _framework/templates/sdd.template.md` | "Decomposição em tasks" aparece entre as outras duas seções, nas duas cópias |
| 3 | RF03/RF04 — grupos e pares bloqueados corretos | `python3 -m pytest _framework/tests/test_parallel_plan.py -v` | Todos os testes de `derive_groups` passam, incluindo bloqueio por interseção sem `depends_on` |
| 4 | RF05 — linha vazia gera aviso, não interrompe | `python3 -m pytest _framework/tests/test_parallel_plan.py::test_linha_vazia_gera_aviso -v` | Teste passa: aviso emitido, execução continua, linha excluída do cálculo |
| 5 | RF06 — gate falha com coluna de arquivos vazia | `python3 -m pytest _framework/tests/test_validate_doc.py::test_gate_arquivos_vazio_falha -v` | Teste passa: `validate_doc.py` reporta falha citando RF-ID/task |
| 6 | RF07 — seção dispensada por sizing small/RF único | `python3 -m pytest _framework/tests/test_validate_doc.py::test_gate_dispensa_tasks_sizing_small -v` | Teste passa: gate não falha pela ausência da seção nesse caso |
| 7 | CLI ponta a ponta | `python3 _framework/scripts/parallel_plan.py _framework/tests/fixtures/sdd_fixture_a.md _framework/tests/fixtures/sdd_fixture_b.md` | Saída lista grupo(s) paralelizável(is) e par(es) bloqueado(s) sem traceback |
| 8 | Paridade entre as duas cópias do kit | `diff _framework/templates/spec.template.md _framework/skills/doc-traceability-framework/templates/spec.template.md && diff _framework/templates/sdd.template.md _framework/skills/doc-traceability-framework/templates/sdd.template.md && diff _framework/scripts/parallel_plan.py _framework/skills/doc-traceability-framework/scripts/parallel_plan.py && diff _framework/scripts/validate_doc.py _framework/skills/doc-traceability-framework/scripts/validate_doc.py` | Nenhuma diferença (exit code 0 nos 4 diffs) |
| 9 | Nota de cross-reference no guia de trilhas | `grep -n "RFC-DTF-0003\|ADR-DTF-0003" docs/guias/paralelizacao-trilhas.md` | Nota presente, sem reescrita do restante do guia |

Nota do implementador sobre o critério 1: o template de SPEC já tinha, antes
desta SDD, texto explicativo (as "cinco formas" de EARS) entre o heading
"Requisitos funcionais" e a tabela — por isso `grep -A2` não alcança a
linha `Arquivos` (fica ~13 linhas depois do heading, não 2). A coluna
existe e está correta nas duas cópias (conferido com
`grep -c "| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |"`
nos dois arquivos, ambos `1`); o comando literal do critério 1 não reflete
a estrutura real do template. Verificador: confirme a coluna por outro
meio, não pelo `grep -A2` literal.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Coluna `Arquivos` no template de SPEC | RF01 | `_framework/templates/spec.template.md`, `_framework/skills/doc-traceability-framework/templates/spec.template.md` | |
| 2 | Seção "Decomposição em tasks" no template de SDD | RF02 | `_framework/templates/sdd.template.md`, `_framework/skills/doc-traceability-framework/templates/sdd.template.md` | |
| 3 | Implementar `parallel_plan.py` (parser + `derive_groups` + CLI) | RF03, RF04, RF05 | `_framework/scripts/parallel_plan.py`, `_framework/skills/doc-traceability-framework/scripts/parallel_plan.py` | |
| 4 | Estender `validate_doc.py` (RF06, RF07) | RF06, RF07 | `_framework/scripts/validate_doc.py`, `_framework/skills/doc-traceability-framework/scripts/validate_doc.py` | |
| 5 | Testes de `parallel_plan.py` (inclui registrar `_framework/tests` em `testpaths` — os testes vivem fora de `_framework/scripts/tests`, sem isso `pytest` bare nunca os roda) | RF03, RF04, RF05 | `_framework/tests/test_parallel_plan.py`, `_framework/tests/fixtures/sdd_fixture_a.md`, `_framework/tests/fixtures/sdd_fixture_b.md`, `pyproject.toml` | 3 |
| 6 | Testes de `validate_doc.py` (casos novos) | RF06, RF07 | `_framework/tests/test_validate_doc.py` | 4 |
| 7 | Nota de cross-reference no guia de trilhas | (decisão pura) | `docs/guias/paralelizacao-trilhas.md` | |
| 8 | Verificar paridade das duas cópias do kit | RF01-RF07 | (nenhum arquivo novo — checagem de diff) | 1, 2, 3, 4 |

Tasks 1, 2, 3, 4 e 7 não compartilham arquivo entre si — paralelizáveis
(ex.: 5 agentes/sessões simultâneas). Task 5 depende de 3, task 6
depende de 4 (podem rodar em paralelo entre si, mas cada uma só após
sua dependência). Task 8 fecha o grafo, depende de 1-4.

## Instruções específicas para a IA implementadora

- Editar os templates e scripts nas **duas cópias** listadas por task —
  esquecer uma delas falha o critério de aceite 8 (paridade).
- `parallel_plan.py` é função pura (`derive_groups`) + parser de tabela
  Markdown + CLI fina — não introduzir estado global nem dependência
  de rede. Interseção de arquivo usa `fnmatch` para suportar glob
  (RF03, caso de borda "glob colide com path exato" da SPEC).
- `validate_doc.py`: os dois itens novos (RF06, RF07) entram no mesmo
  loop de checklist já existente (seção 15 do framework) — não criar
  função de validação paralela e desconectada das demais.
- Não tocar `docs/sdd/SDD-DTF-0020.md` nem `docs/sdd/validation.md` —
  modificados por outra sessão neste momento, fora de escopo desta SDD.
- Não sincronizar a cópia do kit no repositório `viverMelhor` a partir
  desta sessão — isso é tarefa de uma sessão aberta naquele
  repositório, depois desta SDD `implemented` (ver `consumption_instructions`).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima (RF01-RF07) tem código correspondente.
- [x] Todo arquivo tocado pela implementação aparece na tabela "Decomposição em tasks" acima — arquivo tocado fora da lista é escopo não registrado (atualizar a SDD) ou scope creep (remover). `pyproject.toml` adicionado à task 5 (registro de `testpaths`, necessário para `pytest` bare descobrir os testes novos).
- [x] Nenhuma abstração, config, feature flag ou refactor extra sem requisito consolidado (ex.: não introduzir orquestração automática de agentes — está em "Fora de escopo" da SPEC).

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

**Verificador independente:** sim — sessão separada da que implementou, sem ler o histórico dela; entrada foi só esta SDD e os arquivos do diff `f145ac9..415bda5` (commit `415bda5`, mergeado via PR #90). Verificação em 2026-09-15.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `grep -A2 "Requisitos funcionais" _framework/templates/spec.template.md \| grep "Arquivos"` (literal) + `grep -c "\| RF-ID \| Requisito \| Critério de aceite (EARS) \| Arquivos \|" _framework/templates/spec.template.md _framework/skills/doc-traceability-framework/templates/spec.template.md` (checagem alternativa) | Literal: exit 1, nenhuma saída (texto EARS entre o heading e a tabela empurra a linha `Arquivos` para ~13 linhas depois, não 2). Alternativo: `1` nas duas cópias — coluna presente no cabeçalho da tabela | sem teste automatizado | Sim (via checagem alternativa; comando literal do critério não bate com a estrutura real do template, confirmado nesta sessão — ver nota do implementador e descompasso 1 em `validation.md`) |
| 2 | `grep -n "Decomposição em tasks\|Especificação técnica consolidada\|Critérios de aceite" _framework/templates/sdd.template.md` (e cópia) | `49:## Especificação técnica consolidada`, `52:## Decomposição em tasks`, `63:## Critérios de aceite / definição de pronto` — idêntico nas duas cópias | sem teste automatizado | Sim |
| 3 | `python3 -m pytest _framework/tests/test_parallel_plan.py -v` | `11 passed in 0.26s` | mutação `if overlap or dependency:` → `if False:` em `derive_groups`: 4 testes falham (`test_interseccao_bloqueia_mesmo_sem_depends_on`, `test_depends_on_bloqueia_sem_interseccao_de_arquivo`, `test_glob_casa_com_path_exato`, `test_cli_ponta_a_ponta_sem_traceback`); restaurado com `git checkout --`, `11 passed` de novo | Sim |
| 4 | `python3 -m pytest _framework/tests/test_parallel_plan.py::test_linha_vazia_gera_aviso -v` | `1 passed` | mutação: removido o branch `if not files_cell: warnings.append(...); continue` em `parse_tasks`: `1 failed` (`assert False`); restaurado, `1 passed` | Sim |
| 5 | `python3 -m pytest _framework/tests/test_validate_doc.py::test_gate_arquivos_vazio_falha -v` | `1 passed` | mutação `if not files:` → `if False and not files:` em `check_files_column`: `1 failed`; restaurado, `1 passed` | Sim |
| 6 | `python3 -m pytest _framework/tests/test_validate_doc.py::test_gate_dispensa_tasks_sizing_small -v` | `1 passed` | mutação `if fm.get("sizing") == "small":` → `if False:` em `check_tasks_section`: `1 failed` (RF07 disparado indevidamente); restaurado, `1 passed` | Sim |
| 7 | `python3 _framework/scripts/parallel_plan.py _framework/tests/fixtures/sdd_fixture_a.md _framework/tests/fixtures/sdd_fixture_b.md` | 2 grupos paralelizáveis, 2 pares bloqueados (`... Criar handler <-> ... Testes do handler (depends_on)`, `... Criar handler <-> ... Utilitário compartilhado (src/shared/utils.py)`), aviso de linha vazia em stderr, sem traceback | sem teste automatizado dedicado (coberto indiretamente por `test_cli_ponta_a_ponta_sem_traceback`, ver critério 3) | Sim |
| 8 | `diff` dos 4 pares de arquivo (spec.template.md, sdd.template.md, parallel_plan.py, validate_doc.py, cada um entre `_framework/` e `_framework/skills/doc-traceability-framework/`) | Nenhuma diferença nos 4 diffs, exit 0 | sem teste automatizado | Sim |
| 9 | `grep -n "RFC-DTF-0003\|ADR-DTF-0003" docs/guias/paralelizacao-trilhas.md` | `8:> pensado à mão pelo time. \`RFC-DTF-0003\`/\`ADR-DTF-0003\` (paralelismo` — nota presente, restante do guia intocado | sem teste automatizado | Sim |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0010, ADR-DTF-0003 |
