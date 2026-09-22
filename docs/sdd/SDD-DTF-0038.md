---
id: SDD-DTF-0038
type: SDD
title: "Selftest dos validadores por mutação (selftest.py) + mecanização da contagem de recorrência de lições (lessons_check.py)"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0015"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0015.md"
consumption_instructions: "Leia SPEC-DTF-0015 inteira antes de tocar em qualquer arquivo. Esta SDD consolida Parte 1/Parte 2, mas divergiu da SPEC num ponto: RF01 pede reaproveitar exatamente os pares find/replace já documentados nas tabelas de Evidência de SDD-DTF-0036 e SDD-DTF-0037 para os 4 validadores (validate_state.py, check_commit.py, check_hooks.py, check_source_docs.py) — só que essas duas SDDs documentam mutação só para validate_state.py (2 pares) e check_source_docs.py (1 par). Decisão registrada nesta SDD (confirmada com o humano antes de escrever este documento): reusar a mutação de check_hooks.py já documentada em SDD-DTF-0029 (fora do escopo literal de RF01, mesma técnica), e criar uma mutação nova para check_commit.py (sem fonte anterior), verificada manualmente nesta sessão antes de entrar em mutations.yaml (ver 'Especificação técnica consolidada'). Todos os 7 pares de mutations.yaml foram aplicados e revertidos de fato nesta sessão de planejamento, cada um confirmado matando o mutante — não são hipotéticos."
supersedes: null
superseded_by: null
tags: [selftest, lessons_policy, tlc-spec-lean, mecanizacao]
---

# Selftest dos validadores por mutação (selftest.py) + mecanização da contagem de recorrência de lições (lessons_check.py)

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`).

## Resumo executivo

Item 9 da STRAT-DTF-0003 (repo central) tem duas lacunas médias (E6, E7,
`tlc-spec-lean`): os validadores do kit têm mutação aplicada manualmente,
caso a caso, dentro de cada SDD que os tocou, sem comando único que
reaplique essas mutações e confirme que continuam matando a suíte; e o
critério "2 projetos" da `lessons_policy` é contado à mão, lendo
`LESSONS.md` de cada repositório. Esta SDD acrescenta dois scripts CLI
independentes ao kit: `selftest.py` (roda mutações declaradas em
`mutations.yaml` contra os validadores, reporta mutante sobrevivente
como falha) e `lessons_check.py` (extrai `Chave de recorrência` de
`LESSONS.md`, reporta slug recorrente em 2+ arquivos como candidata a
promoção).

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — SPEC-DTF-0015 avaliou o gate `rfc_to_adr` inline (nenhum
critério se aplica: nenhum padrão arquitetural novo, nenhuma alternativa
técnica concorrente relevante, não cross-team, não troca
tecnologia/vendor, reversão trivial) e pulou RFC/ADR, indo direto para
SPEC.

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | `_framework/scripts/tests/mutations.yaml` (novo) declara cada mutação como `{validator, test_file, description, find, replace}`, sem lógica de mutação hardcoded em script, com ao menos uma entrada por validador que já tem suíte de teste hoje (`validate_state.py`, `check_commit.py`, `check_hooks.py`, `check_source_docs.py`). |
| RF02 | `_framework/scripts/selftest.py` (novo), para cada mutação: aplica `find`→`replace` no `validator`, roda `test_file` via `pytest`, registra mutante morto (suíte falhou) ou sobrevivente (suíte passou), reverte o arquivo ao conteúdo original — sempre, mesmo se a suíte falhar por erro externo. |
| RF03 | Se `find` não existir no `validator` no momento de aplicar, `selftest.py` reporta erro explícito para essa entrada — nunca trata "não consegui aplicar" como mutante morto nem sucesso silencioso. |
| RF04 | `selftest.py` termina com exit code != 0 se qualquer mutante sobreviver (RF02) ou não puder ser aplicado (RF03); exit 0 só quando todas as mutações morrerem e todas forem aplicáveis. |
| RF05 | `_framework/scripts/lessons_check.py` (novo) extrai de um `LESSONS.md` cada entrada (`## <data> — <título>`) que contenha, em algum ponto do corpo, `**Chave de recorrência:** <slug>` — campo novo, opcional, retrocompatível (entrada sem o campo é ignorada, não erro). |
| RF06 | Dado 2+ paths de `LESSONS.md` (CLI, sem discovery automático), `lessons_check.py` agrupa entradas extraídas (RF05) por `slug` e reporta como "candidata a promoção" todo slug que aparecer em entradas de 2+ arquivos `LESSONS.md` distintos, listando data+arquivo de cada ocorrência. |
| RF07 | Entrada com `**Status da lição:** confirmada` não é reportada por RF06, mesmo que o slug recorra em 2+ arquivos. |

**Casos de borda (consolidados da SPEC):**
- `mutations.yaml` referencia `validator`/`test_file` inexistente → `selftest.py` reporta erro explícito para essa entrada, não interrompe a checagem das demais (RF02).
- Mesmo slug duas vezes no mesmo arquivo `LESSONS.md` não conta como recorrência entre projetos — RF06 exige arquivos distintos (RF06).
- `LESSONS.md` sem nenhuma entrada com "Chave de recorrência" → `lessons_check.py` roda normal, relata zero candidatas, não é erro (RF05).
- `test_file` já falha sem mutação alguma → fora de escopo detectar; mutante "morto" por suíte já quebrada é falso-positivo aceito (RF02).

## Especificação técnica consolidada

Arquivos tocados (produto):

- `_framework/scripts/tests/mutations.yaml` (novo, RF01) — 7 entradas,
  uma por par find/replace verificado nesta sessão de planejamento (ver
  tabela "Mutações de `mutations.yaml`" abaixo). Cobre os 4 validadores
  exigidos por RF01.
- `_framework/scripts/selftest.py` (novo, RF02-RF04):
  - `apply_mutation(target: Path, find: str, replace: str) -> str` —
    lê `target`, levanta erro explícito se `find` não estiver no
    conteúdo (RF03), escreve `replace` aplicado, retorna o conteúdo
    original (para revert).
  - `run_mutation(mutation: dict, scripts_dir: Path) -> dict` — chama
    `apply_mutation`, roda `pytest test_file` via `subprocess`, captura
    exit code, em bloco `finally` reescreve o conteúdo original
    (re-levanta `SystemExit` se a escrita de revert falhar — nunca
    deixa o validador mutado no disco silenciosamente); retorna
    `{"survived": bool, "error": str | None}`.
  - CLI: `python3 selftest.py [mutations.yaml]` (default
    `_framework/scripts/tests/mutations.yaml`), exit != 0 se qualquer
    mutação sobreviver ou não puder ser aplicada (RF04).
- `_framework/scripts/lessons_check.py` (novo, RF05-RF07):
  - `extract_entries(path: Path) -> list[dict]` — parseia entradas
    `## <data> — <título>`, extrai `{date, title, slug, confirmed,
    file}` de cada uma que tiver `**Chave de recorrência:** <slug>`;
    `path` inexistente → `SystemExit` com mensagem clara.
  - `find_candidates(entries_by_file: dict[Path, list[dict]]) -> dict[str, list[dict]]` —
    agrupa por slug, filtra `confirmed` (RF07), retorna só slugs com
    ocorrência em 2+ arquivos distintos (RF06).
  - CLI: `python3 lessons_check.py <LESSONS.md...>` (2+ paths).
- `_framework/rules/workflow-rules.yaml` (`lessons_policy`, seção 18):
  documentar `**Chave de recorrência:** <slug>` e
  `**Status da lição:** confirmada` como convenção opcional, não como
  schema obrigatório (Plano de implementação item 3 da SPEC).
- Replicar `selftest.py`, `lessons_check.py` e `mutations.yaml` na cópia
  bundlada da skill (`_framework/skills/doc-traceability-framework/`)
  via `render_prompts.py`.

**Mutações de `mutations.yaml` — todas aplicadas e revertidas de fato
nesta sessão de planejamento antes de entrar no arquivo de dados (não
hipotéticas):**

| # | validator | find | replace | test_file | Fonte |
|---|---|---|---|---|---|
| 1 | `validate_state.py` | `if esperado == "automatizado" and (len(row) <= assertion_idx or not row[assertion_idx].strip()):` | `if (len(row) <= assertion_idx or not row[assertion_idx].strip()):` | `test_validate_state.py -k "perfil or colunas_novas"` | SDD-DTF-0036 RF03, Evidência #3 |
| 2 | `validate_state.py` | `usado.split("(")[0].strip().lower() != esperado and "(" not in usado:` | `usado.split("(")[0].strip().lower() == esperado and "(" not in usado:` | `test_validate_state.py -k "perfil or colunas_novas"` | SDD-DTF-0036 RF04, Evidência #4 |
| 3 | `validate_state.py` | `if not source_docs or not evidence:` | `if not evidence:` | `test_validate_state.py -k "fidelidade or rf04 or rf05 or rf06"` | SDD-DTF-0037 RF05, validation-SDD-DTF-0037.md #4 |
| 4 | `validate_state.py` | `return str(created) > since_date` | `return str(created) >= since_date` | `test_validate_state.py -k "fidelidade or rf04 or rf05 or rf06"` | SDD-DTF-0037 RF06, validation-SDD-DTF-0037.md #5 |
| 5 | `check_source_docs.py` | `if status not in OK_STATUSES:` | `if False:` | `test_check_source_docs.py` | SDD-DTF-0037 RF02/RF03, validation-SDD-DTF-0037.md #2 |
| 6 | `check_hooks.py` | `token.startswith(p)` | `"CLAUDE_PROJECT_DIR" in token` | `test_check_hooks.py` | SDD-DTF-0029, validation Evidência #2 (fora do escopo literal de RF01 — SDD-DTF-0036/0037 não cobrem check_hooks.py; decisão desta SDD, confirmada com o humano) |
| 7 | `check_commit.py` | `if not m:` | `if False:` | `test_check_commit.py` | Sem fonte anterior — mutação nova desta SDD. Neutraliza a checagem de Conventional Commits (`CONVENTIONAL.match`); verificada nesta sessão: mata `test_range_reprova_commit_comum_fora_do_formato` e `test_arquivo_sem_merge_head_reprova_fora_do_formato` (suíte cai via `AttributeError` não tratado — conta como "morto" por RF02: suíte falhou, causa não distinguida, mesma limitação aceita nos casos de borda da SPEC) |

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | `mutations.yaml` com os 7 pares acima | RF01 | `_framework/scripts/tests/mutations.yaml` | |
| 2 | `selftest.py` (`apply_mutation`, `run_mutation`, CLI) | RF02, RF03, RF04 | `_framework/scripts/selftest.py` | 1 |
| 3 | Testes de regressão de `selftest.py` (fixture sintética + sensor de discriminação real) | RF02, RF03, RF04 | `_framework/scripts/tests/test_selftest.py` | 2 |
| 4 | `lessons_check.py` (`extract_entries`, `find_candidates`, CLI) | RF05, RF06, RF07 | `_framework/scripts/lessons_check.py` | |
| 5 | Testes de regressão de `lessons_check.py` | RF05, RF06, RF07 | `_framework/scripts/tests/test_lessons_check.py` | 4 |
| 6 | Documentar `Chave de recorrência`/`Status da lição` em `lessons_policy` | RF05-RF07 (convenção) | `_framework/rules/workflow-rules.yaml` | |
| 7 | Sincronizar bundle da skill principal | RF01-RF07 | `_framework/skills/doc-traceability-framework/` (scripts) | 1, 2, 4, 6 |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — `mutations.yaml` cobre os 4 validadores, 5 campos por entrada | `python3 -m pytest _framework/scripts/tests/test_selftest.py -k mutations_yaml -v` | Passa, confirma 4 validadores presentes | automatizado |
| 2 | RF02/RF04 — mutante sobrevivente reportado, exit != 0 | `python3 -m pytest _framework/scripts/tests/test_selftest.py -v` | Todos passam (inclui fixture com mutante sobrevivente proposital) | automatizado |
| 3 | RF03 — `find` ausente reportado como erro, não como sucesso | (mesmo comando do #2, inclui teste de `find` inexistente) | Passa | automatizado |
| 4 | Sensor de discriminação real — `selftest.py` roda contra as mutações reais de `mutations.yaml` | `python3 _framework/scripts/selftest.py` | Todos os 7 mutantes reportados como mortos, exit 0 | automatizado |
| 5 | RF05/RF07 — extração de `Chave de recorrência`, ignora `Status da lição: confirmada` | `python3 -m pytest _framework/scripts/tests/test_lessons_check.py -v` | Todos passam | automatizado |
| 6 | RF06 — slug recorrente em 2+ arquivos reportado, arquivo único não reportado | (mesmo comando do #5, inclui teste RF06) | Passa | automatizado |
| 7 | Sem regressão nos validadores contra os documentos reais do projeto | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | Ambos ✅, 0 problemas | automatizado |
| 8 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam | automatizado |
| 9 | Bundle da skill principal sincronizado | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência | automatizado |

## Instruções específicas para a IA implementadora

- Não hardcode nenhuma mutação em `selftest.py` — toda mutação vem de
  `mutations.yaml`, RF01 é explícito sobre isso.
- `run_mutation` reverte sempre, mesmo com falha do `pytest` por motivo
  externo (import quebrado etc.) — bloco `finally`. Se a própria escrita
  de revert falhar, re-levantar exceção (`SystemExit`) em vez de deixar
  o validador mutado no disco — nunca silenciar.
- `apply_mutation` levanta erro explícito (não `SystemExit` direto — ver
  contrato RF02/RF03 na SPEC) quando `find` não está no conteúdo atual;
  `run_mutation` traduz isso em `{"error": ...}`, não em `{"survived":
  False}`.
- Testes de `selftest.py` usam validador/teste **sintéticos** em
  `tmp_path` para RF02-RF04 (não rodar os validadores reais no teste
  unitário, para não acoplar a suíte inteira do kit) — só o critério de
  aceite #4 ("sensor de discriminação real") roda `selftest.py` de fato
  contra `mutations.yaml`.
- `lessons_check.py` não faz discovery automático de `LESSONS.md` — só
  os paths passados por CLI (RF06 é explícito: "sem discovery
  automático").
- Não implementar selftest de `validate_doc.py` — fora de escopo (SPEC,
  "Fora de escopo"), não existe `test_validate_doc.py` hoje.
- Não promover lição automaticamente a regra global — `lessons_check.py`
  só lista candidatas, decisão continua humana.
- Editar sempre as duas cópias do kit (`_framework/scripts/` e
  `_framework/skills/doc-traceability-framework/scripts/`) no mesmo
  commit, ou deixar `render_prompts.py` sincronizar — nunca editar a
  cópia bundlada à mão.
- Sensor de discriminação obrigatório para RF02-RF07 nos testes novos:
  mutar a implementação (temporariamente, nunca commitado), confirmar
  que o teste cai, reverter.

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF07 todos com trecho correspondente no código.
- [x] Nenhum arquivo tocado fora da lista de "Arquivos tocados" acima.
- [x] Nenhuma abstração/config/feature flag extra além do que RF01-RF07 pedem.

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0038.md`. Veredito: **PASS**.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0038.md /home/michel/doc-traceability-central/docs/DTF` (+ leitura de SPEC-DTF-0015 completa) | `✅ source_docs de SDD-DTF-0038.md conferem com o registry central.` — RF01-RF07 todos presentes na SDD, edge cases e contratos técnicos (Parte 2) idênticos à SPEC. RF01 tem divergência **deliberada e registrada**: SPEC pede reaproveitar exatamente os pares de SDD-DTF-0036/0037 para os 4 validadores; essas duas SDDs só cobrem `validate_state.py` (2 pares) e `check_source_docs.py` (1 par) — a SDD documenta em `consumption_instructions` e na tabela "Mutações de mutations.yaml" que a mutação de `check_hooks.py` vem de SDD-DTF-0029 e a de `check_commit.py` é nova sem fonte anterior, confirmada com o humano. Conferi origem de cada um dos 7 pares contra os documentos citados (SDD-DTF-0036 linhas 194-195, SDD-DTF-0037 linhas 178/180-181, SDD-DTF-0029 linha 141, validation-SDD-DTF-0037.md linha 34): todas as citações batem com find/replace/test_file reais. Registro é fiel, não é omissão. | n/a (checagem documental, não código) | Sim | n/a | n/a |
| 1 | 1 | `python3 -m pytest _framework/scripts/tests/test_selftest.py -k mutations_yaml -v` | `1 passed` — confirma cobertura dos 4 validadores | Mutação real: removida a entrada `check_commit.py` de `mutations.yaml` → `test_mutations_yaml_cobre_os_4_validadores_com_5_campos` FALHOU (`AssertionError: 'check_commit.py'` faltando); restaurado via cópia guardada (`cp`), diff vazio confirmado → voltou a passar | Sim | `_framework/scripts/tests/test_selftest.py:60` | automatizado |
| 1 | 2 | `python3 -m pytest _framework/scripts/tests/test_selftest.py -v` | `9 passed in 19.88s` | Mutação real em `selftest.py`: `apply_mutation` deixou de levantar `ValueError` quando `find` ausente (`if find not in original` → `if False`) → `test_apply_mutation_find_ausente_levanta_erro` e `test_run_mutation_find_ausente_reporta_erro_nao_sobrevivente` FALHARAM (2 de 9); restaurado via cópia guardada → 9 passed de novo | Sim | `_framework/scripts/tests/test_selftest.py:75` | automatizado |
| 1 | 3 | (mesmo comando do #2, inclui `test_run_mutation_find_ausente_reporta_erro_nao_sobrevivente`) | `PASSED` (dentro do run de 9 passed) | Mesma mutação do #2 (guarda de `find` ausente removida) → `test_run_mutation_find_ausente_reporta_erro_nao_sobrevivente` FALHOU (`assert True is False`, outcome["survived"] deixou de ser `False`); restaurado → voltou a passar | Sim | `_framework/scripts/tests/test_selftest.py:119` | automatizado |
| 1 | 4 | `python3 _framework/scripts/selftest.py` | `✅ 7 mutação(ões): todos os mutantes morreram.` exit 0 | Mutação real: corrompi o `find` da entrada `check_commit.py` em `mutations.yaml` (`if not m:` → `if not m_does_not_exist:`, simulando código-fonte divergido) → `selftest.py` reportou `❌ 1 problema(s)`, mutação não aplicável, exit 1; restaurado via cópia guardada, diff vazio confirmado → voltou a exit 0 com 7/7 mortos | Sim | `_framework/scripts/selftest.py:33` (guard de `find not in original`) | automatizado |
| 1 | 5 | `python3 -m pytest _framework/scripts/tests/test_lessons_check.py -v` | `11 passed in 0.10s` | Mutação real em `lessons_check.py`: `find_candidates` deixou de filtrar `entry["confirmed"]` (`if entry["confirmed"]:` → `if False:`) → `test_find_candidates_exclui_confirmada` FALHOU (slug confirmado voltou a aparecer como candidata); restaurado via cópia guardada → 11 passed de novo | Sim | `_framework/scripts/tests/test_lessons_check.py:118` | automatizado |
| 1 | 6 | (mesmo comando do #5, inclui `test_find_candidates_slug_em_dois_arquivos_e_candidata`, `test_find_candidates_slug_em_um_arquivo_so_nao_e_candidata`, `test_find_candidates_duas_ocorrencias_mesmo_arquivo_nao_conta`) | `PASSED` (dentro do run de 11 passed) | Mutação real: exigência de "2+ arquivos distintos" relaxada para "1+" (`len(...) >= 2` → `>= 1`) → `test_find_candidates_slug_em_um_arquivo_so_nao_e_candidata`, `test_find_candidates_duas_ocorrencias_mesmo_arquivo_nao_conta` e `test_find_candidates_exclui_confirmada` FALHARAM (3 de 11 — slug de arquivo único passou a ser reportado como candidata); restaurado via cópia guardada, diff vazio confirmado → 11 passed de novo | Sim | `_framework/scripts/tests/test_lessons_check.py:105` | automatizado |
| 1 | 7 | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | `✅ 37 documento(s) passaram no gate de qualidade de conteúdo.` / `✅ 37 documento(s) verificados: nenhuma SDD implemented sem evidência.` ambos exit 0 | sem teste automatizado novo (validadores pré-existentes, já sensor-testados em SDD-DTF-0036/0037; esta SDD não os modifica) | Sim | n/a | automatizado |
| 1 | 8 | `python3 -m pytest _framework/ -q` | `174 passed in 25.89s` (rodado após todas as mutações desta tabela restauradas) | coberto pelos sensores individuais #1-6 acima | Sim | n/a | automatizado |
| 1 | 9 | `python3 _framework/scripts/render_prompts.py --check` | `EXIT=0`, todos os arquivos `sincronizado`/`em dia` | Mutação real: acrescentei uma linha a `_framework/skills/doc-traceability-framework/scripts/lessons_check.py` (cópia bundlada) sem tocar no original → `render_prompts.py --check` reportou `❌ .../lessons_check.py: divergente`; restaurado via cópia guardada, diff vazio confirmado → voltou a `sincronizado`, exit 0 | Sim | `_framework/scripts/render_prompts.py` (checagem de sincronização, sem linha única de assertion — comparação de conteúdo) | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0015 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0015.md) |
