---
id: SDD-DTF-0050
type: SDD
title: "Prompt do Cursor sem PRD+TS: fluxo e ids de exemplo em SPEC no texto de render_prompts.py, com teste de regressão"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0042, SDD-DTF-0048]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0047). A SPEC-DTF-0021 deixou este resíduo fora de escopo de propósito (decisão 5): o texto do prompt do Cursor vem de uma string em render_prompts.py, não do YAML. Leia esta SDD inteira; ela nomeia a string, as duas trocas e o teste. Escrever o teste primeiro e vê-lo falhar, depois implementar. Gerados (prompts, cópia da skill de render_prompts.py) nunca à mão: rodar render_prompts.py. O central espelha por PR próprio (task 5, prefixo central:). Implementar em sessão separada, worktree próprio no kit, branch sdd/SDD-DTF-0050-*; verificação por sdd-verifier em outra sessão."
supersedes: null
superseded_by: null
tags: [tooling, prd-ts, cursor, check_renderings, frente-tooling]
---

# Prompt do Cursor sem PRD+TS: fluxo e ids de exemplo em SPEC no texto de render_prompts.py, com teste de regressão

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

O prompt do Cursor (`_framework/prompts/cursor/doc-framework.mdc`) ainda
descreve o fluxo como `ADR → PRD+TS → SDD` e cita `TS-X` como id de exemplo.
O texto vem de uma string literal em `_framework/scripts/render_prompts.py`
(a função que monta o prefixo do Cursor) e não do YAML, por isso a SDD-DTF-0048
não o alcançou. O sintoma são os dois avisos persistentes de
`_framework/scripts/check_renderings.py` ("cita o tipo legado 'PRD'/'TS'
sem marcar que é legado"). Esta SDD troca as duas ocorrências por SPEC (o
tipo que substituiu o par PRD+TS) e acrescenta um teste de regressão sobre o
texto gerado.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — RFC dispensou decisão arquitetural via gate (RFC-DTF-0008,
`decision_gates.rfc_to_adr = false`). SPEC substitui o par PRD + Tech Spec
desde o framework 2.0; o fluxo novo, inclusive no YAML, é
`ADR → SPEC → SDD`.

Medido no `main` do kit (após a SDD-DTF-0049): `check_renderings.py` emite 2
avisos, ambos do `doc-framework.mdc`. O cabeçalho do `universal.md` já mostra
a versão real (`v2.3.2`): o `"v1.7.0"` do literal é substituído por
`prefix.replace("v1.7.0", f"v{version}", 1)`, então não há defeito ali.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | No prefixo do Cursor, o fluxo de decisão passa de `(sim: ADR → PRD+TS → SDD)` e `(não: PRD+TS → SDD)` para `(sim: ADR → SPEC → SDD)` e `(não: SPEC → SDD)` | Quando `render_prompts.py` regenerar o Cursor, o sistema deve produzir um `doc-framework.mdc` sem a expressão `PRD+TS` |
| RF02 | No prefixo do Cursor, os ids de exemplo do handover passam de `(SDD-X, TS-X)` para `(SDD-X, SPEC-X, ADR-X)`, como já está no Copilot e no universal | Quando `render_prompts.py` regenerar o Cursor, o sistema deve produzir um `doc-framework.mdc` sem `TS-X` |
| RF03 | O texto gerado dos três prompts (`universal.md`, `cursor/doc-framework.mdc`, `copilot/copilot-instructions.md`) não cita PRD nem TS como passo do fluxo | Se um dos três arquivos gerados contiver `PRD+TS`, `PRD + TS` ou `TS-X`, então o teste novo deve falhar, exceto em linha que traga a marca "legado" (âncora de legado vinda do YAML, como `par PRD+TS, em projeto legado` no `universal.md`); e, se a lista de arquivos que o teste verifica deixar de conter algum dos três prompts, então o teste deve falhar |
| RF04 | Os gerados são regenerados pelo script, nunca à mão, e a cópia de `render_prompts.py` na skill segue idêntica | Quando `render_prompts.py --check` rodar após a regeneração, o sistema deve sair com código 0 |
| RF05 | O central espelha a mudança por PR próprio | Quando `cmp` comparar os arquivos tocados no kit com o mesmo caminho no central, o sistema deve reportar arquivos idênticos |

Fora de escopo: qualquer texto do YAML (já tratado na SDD-DTF-0048), o
`onboarding.applies_when` (âncora de legado), novos tipos de aviso do
`check_renderings.py` e o texto de `AGENTS.md`/`QUICKSTART.md`.

## Especificação técnica consolidada

- **Onde está o texto.** Função que monta o prefixo do Cursor em
  `_framework/scripts/render_prompts.py` (a linha com
  `description: Framework de Documentação & Rastreabilidade para IA — SDD local`).
  Duas trocas dentro do literal: `ADR → PRD+TS → SDD` e `PRD+TS → SDD` viram
  `ADR → SPEC → SDD` e `SPEC → SDD`; `(SDD-X, TS-X)` vira
  `(SDD-X, SPEC-X, ADR-X)`. Nenhuma outra linha do literal muda.
- **Teste novo.** `_framework/tests/test_prompts_sem_prd_ts.py` lê os três
  gerados e reprova a presença de `PRD+TS`, `PRD + TS` e `TS-X`, com a linha e
  o arquivo na mensagem. Uma função de detecção sobre texto em memória
  (`ocorrencias(texto) -> list[tuple[int, str]]`) e um teste que a aplica aos
  três arquivos reais; um segundo teste de mutação alimenta a função com um
  texto que contém `PRD+TS` e exige detecção. `ocorrencias()` isenta a linha que contém "legado": o `universal.md` traz `par PRD+TS, em projeto legado`, âncora de legado que vem do YAML (fora de escopo), e sem a isenção o teste reprovaria esse arquivo mesmo depois da correção. O teste de mutação cobre a linha com a marca e a linha sem ela. Um terceiro teste, `test_gerados_cobrem_os_tres_prompts`, afirma que a tupla `GERADOS` é exatamente `universal.md`, `doc-framework.mdc` e `copilot-instructions.md`, todos existentes; sem ele, a verificação de RF03 pode encolher sem falha (a verificação independente mostrou que remover o Copilot ou o `universal.md` da tupla sobrevivia à suíte).
- **Manifesto e índice.** `render_indexes.py` exige entrada em `_framework/rules/kit-index.yaml` para todo arquivo do kit: o teste novo ganha a entrada (o manifesto não é gerado) e `_framework/INDEX.md` é regenerado por `render_prompts.py`. O central precisa da mesma entrada no espelho.
- **Cópia da skill.** `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`
  é gerada por `render_prompts.py`; não editar à mão.
- **Espelho.** Central: `_framework/scripts/render_prompts.py`, a cópia da
  skill, `_framework/prompts/cursor/doc-framework.mdc` e o teste novo.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Rodar A01 e A02 no `main` e guardar as saídas reais (ANTES) | RF01, RF02 | (decisão pura) | |
| 2 | Teste novo, visto falhar com o texto atual | RF03 | `_framework/tests/test_prompts_sem_prd_ts.py` | 1 |
| 3 | Trocar as duas expressões no literal do prefixo do Cursor | RF01, RF02 | `_framework/scripts/render_prompts.py` | 2 |
| 4 | Regenerar com `render_prompts.py`, rodar `--check` e A01 a A06 registrando comando e saída reais | RF04 | `_framework/prompts/cursor/doc-framework.mdc`, `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `_framework/rules/kit-index.yaml`, `_framework/INDEX.md` | 3 |
| 5 | Espelhar no central em worktree, branch e PR próprios do central | RF05 | `central:_framework/scripts/render_prompts.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `central:_framework/prompts/cursor/doc-framework.mdc`, `central:_framework/tests/test_prompts_sem_prd_ts.py`, `central:_framework/rules/kit-index.yaml`, `central:_framework/INDEX.md` | 4 |

Ordem: 1, 2, 3, 4, 5 (cadeia linear; sem paralelismo).

## Critérios de aceite / definição de pronto

Executar na raiz do kit. "Antes" = `main`, antes de qualquer edição;
"depois" = na branch de implementação, com os gerados regenerados.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01, RF02: os avisos do Cursor somem | `python3 _framework/scripts/check_renderings.py > "$TMPD/cr.txt" 2>&1; grep -c "tipo legado" "$TMPD/cr.txt"` | ANTES: `2`; DEPOIS: `0` | automatizado |
| A02 | RF01, RF02: sem `PRD+TS` nem `TS-X` no Cursor | `grep -c "PRD+TS" _framework/prompts/cursor/doc-framework.mdc; grep -c "TS-X" _framework/prompts/cursor/doc-framework.mdc` | ANTES: `2` e `1`; DEPOIS: `0` e `0` | automatizado |
| A03 | RF03: teste de regressão | `python3 -m pytest _framework/tests/test_prompts_sem_prd_ts.py -v` | ANTES: arquivo inexistente, e o teste visto falhar antes da troca; DEPOIS: todos passam | automatizado |
| A04 | RF03: sensor de mutação | Em cópia descartável, inserir `PRD+TS` numa linha do `doc-framework.mdc` gerado; rodar o pytest do A03; restaurar | Com a mutação: pelo menos 1 failed, com arquivo e linha na mensagem; restaurado: 0 failed | automatizado |
| A05 | RF04: gerados em dia, idempotência e cópia da skill | `python3 _framework/scripts/render_prompts.py && python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/render_prompts.py _framework/skills/doc-traceability-framework/scripts/render_prompts.py` | Última linha do primeiro comando `exit=0`; nenhuma linha "divergente"; `cmp` sem saída | automatizado |
| A06 | Suíte completa e formatação sem regressão | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff format --check _framework/scripts; echo "exit=$?"` | 0 failed e `exit=0` | automatizado |
| A07 | Só os arquivos previstos mudaram | `git diff --name-only main` no kit | Só os arquivos das tasks 2 a 4 (incluídos `kit-index.yaml` e `INDEX.md`), a SDD desta mudança e os gerados de `docs/sdd/`; nenhum `workflow-rules.yaml`, nenhum outro `prompts/` | automatizado |
| A08 | RF05: espelho no central | Em `/home/michel/doc-traceability-central`: `for f in scripts/render_prompts.py skills/doc-traceability-framework/scripts/render_prompts.py prompts/cursor/doc-framework.mdc tests/test_prompts_sem_prd_ts.py rules/kit-index.yaml INDEX.md; do cmp /home/michel/doc-traceability-framework/_framework/$f _framework/$f && echo "igual $f"; done; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | 6 linhas `igual ...` e `exit=0` | automatizado |
| A09 | RF03: a lista de arquivos verificados não encolhe | `python3 -m pytest _framework/tests/test_prompts_sem_prd_ts.py -k gerados_cobrem -v`; em cópia descartável, remover o `copilot-instructions.md` da tupla `GERADOS` e depois o `universal.md`, rodando o pytest inteiro do arquivo a cada vez; restaurar | Sem mutação: 1 passed; com cada mutação: pelo menos 1 failed | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** branch `sdd/SDD-DTF-0050-prompt-cursor-sem-prd-ts`,
  em worktree próprio do kit criado à mão a partir de `origin/main`
  (`git worktree add ../dtf-wt-0050 -b sdd/SDD-DTF-0050-prompt-cursor-sem-prd-ts origin/main`).
  Commits com `Refs: SDD-DTF-0050`. Nunca em `main`, nunca force-push. O
  espelho é feito em worktree próprio do central, com branch e PR próprios.
- **Só o literal do Cursor.** Duas trocas de texto na string do prefixo do
  Cursor e nada mais em `render_prompts.py`. Não mexer no YAML, em
  `check_renderings.py`, nos prefixos de `universal.md` e Copilot nem em
  `AGENTS.md`.
- **Teste primeiro.** Escrever `test_prompts_sem_prd_ts.py`, ver falhar com o
  texto atual (guardar a saída), só então trocar o literal.
- **Gerados só por script.** `render_prompts.py` regenera `doc-framework.mdc`
  e a cópia da skill; nunca editar à mão, nem `docs/sdd/INDEX.md` nem
  `registry.md` (`render_indexes.py` e `generate_registry_md.py docs/sdd`).
- **Tabelas markdown:** não escrever regex com `](` nem alternância com
  barra vertical dentro de célula; para alternar, usar `grep -e` repetido.
- **Evidência de verificação** só pelo `sdd-verifier`, em sessão separada.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF05) tem código
      correspondente.
- [x] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", na "Decomposição em tasks" ou em "Instruções
      específicas" — se tocou um arquivo não listado, ou é escopo que
      faltou registrar na SDD (atualize-a) ou é scope creep a remover.
- [x] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado.
- [x] `workflow-rules.yaml` intocado e `framework.version` igual ao de
      `origin/main`.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 2 (segunda verificação independente, depois dos PRs #134 e #135 do kit
e #155 e #156 do central): todas as linhas abaixo foram rodadas nesta sessão,
em worktrees de `origin/main` (kit em `9c8dc23`, central em `a6d00a5`); o
"antes" de A01 e A02 é o SHA fixo `524fa59` (main anterior ao PR #134). Na
rodada 1 duas mutações sobreviviam (remover o Copilot e remover o
`universal.md` da tupla `GERADOS`); o RF03 ampliado, o terceiro teste e o
critério A09 vieram da correção, e ambas são derrubadas agora. Fidelidade à
origem: n/a, sizing `small` sem `source_docs` (precedente SDD-DTF-0047).

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0050.md`.
Veredito: **PASS**.

**Verificador independente:** sim

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Teste que passa com a implementação quebrada é
ruído verde. Critério sem teste automatizado: escreva "sem teste", nunca
marque como verificado por leitura de código. Coluna "Assertion
(file:line)": caminho e linha exatos da asserção que resolve o critério;
critério `manual` ou `n/a` usa `n/a`. Coluna "Perfil usado": repete o
"Perfil esperado" do critério ou declara divergência com justificativa entre
parênteses.

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 2 | A01 | `python3 _framework/scripts/check_renderings.py > "$TMPD/cr.txt" 2>&1; grep -c "tipo legado" "$TMPD/cr.txt"`, ANTES em worktree de `524fa59` (main anterior ao PR #134), DEPOIS em worktree de `origin/main` (`9c8dc23`) | ANTES (524fa59): `2` (avisos `cita o tipo legado 'PRD'` e `'TS'` em `prompts/cursor/doc-framework.mdc`); DEPOIS (9c8dc23): `0` | n/a (comando de medição; coberto por A03) | Sim | n/a | automatizado |
| 2 | A02 | `grep -c "PRD+TS" _framework/prompts/cursor/doc-framework.mdc; grep -c "TS-X" _framework/prompts/cursor/doc-framework.mdc`, ANTES em `524fa59`, DEPOIS em `9c8dc23` | ANTES (524fa59): `2` e `1`; DEPOIS (9c8dc23): `0` e `0` | n/a (comando de medição; coberto por A03) | Sim | n/a | automatizado |
| 2 | A03 | `python3 -m pytest _framework/tests/test_prompts_sem_prd_ts.py -v` em `9c8dc23`; ANTES: o mesmo arquivo de teste copiado sobre os gerados de `524fa59` (cópia descartável) | DEPOIS: 3 passed (`test_gerados_sem_prd_ts`, `test_detector_pega_mutacao_em_memoria`, `test_gerados_cobrem_os_tres_prompts`). ANTES (arquivo inexistente em 524fa59): com o teste sobre os gerados antigos, `test_gerados_sem_prd_ts` FAILED citando `doc-framework.mdc:43`, `:44` e `:84` | Ver A04, A09 e as mutações do detector abaixo | Sim | _framework/tests/test_prompts_sem_prd_ts.py:36, _framework/tests/test_prompts_sem_prd_ts.py:41, _framework/tests/test_prompts_sem_prd_ts.py:42, _framework/tests/test_prompts_sem_prd_ts.py:43 | automatizado |
| 2 | A04 | Cópia descartável de `9c8dc23`: acrescentado ` PRD+TS` ao fim da linha 5 do `doc-framework.mdc`; `python3 -m pytest _framework/tests/test_prompts_sem_prd_ts.py -q`; restaurado do backup | Com a mutação: 1 failed, 2 passed, mensagem `_framework/prompts/cursor/doc-framework.mdc:5: --- PRD+TS` (arquivo e linha). Restaurado: 3 passed | Mutação no gerado derrubou `test_gerados_sem_prd_ts`. Mutações do detector (cada uma em cópia, pytest inteiro do arquivo): remover a isenção de legado: 2 failed; remover `TS-X` do padrão: 1 failed; padrão sem a variante `PRD + TS`: 1 failed; isenção total (`if False`): 1 failed; âncora vazia (tudo isento): 1 failed; remover `PRD+TS` do padrão: 1 failed. Nenhuma sobreviveu; restaurado: 3 passed | Sim | _framework/tests/test_prompts_sem_prd_ts.py:36, _framework/tests/test_prompts_sem_prd_ts.py:41 | automatizado |
| 2 | A05 | `python3 _framework/scripts/render_prompts.py && python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/render_prompts.py _framework/skills/doc-traceability-framework/scripts/render_prompts.py` em `9c8dc23` | `✅ docs/sdd/INDEX.md: em dia.` e `✅ _framework/INDEX.md: em dia.` (mais o aviso pré-existente de 30 SDDs sem seção de arquivos), última linha `exit=0`; nenhuma linha `divergente`; `cmp` sem saída; `git status --short` limpo depois da regeneração | n/a (comando de medição; gerados em dia cobertos por `--check`) | Sim | n/a | automatizado |
| 2 | A06 | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff format --check _framework/scripts; echo "exit=$?"` em `9c8dc23` | `295 passed in 29.73s`; `33 files already formatted`; `exit=0` | sem sensor próprio (suíte inteira; sensores em A04 e A09) | Sim | n/a | automatizado |
| 2 | A07 | `git diff --name-status 524fa59 9c8dc23` (base fixa: main antes do PR #134; soma dos PRs #134 e #135); `git diff -U0` de `render_prompts.py` com `--word-diff`; `git diff --name-only` filtrado por `workflow-rules` | 8 arquivos: `_framework/INDEX.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/rules/kit-index.yaml`, `_framework/scripts/render_prompts.py`, a cópia da skill, `_framework/tests/test_prompts_sem_prd_ts.py` (A), `docs/sdd/INDEX.md`, `docs/sdd/SDD-DTF-0050.md`. `render_prompts.py`: uma linha (120) e só as três trocas (`PRD+TS`→`SPEC` duas vezes, `TS-X)`→`SPEC-X, ADR-X)`). `workflow-rules.yaml`: diff de 0 linhas; único `prompts/` é o do Cursor | n/a (comando de medição) | Sim | n/a | automatizado |
| 2 | A08 | Loop de `cmp` dos 6 arquivos entre o kit (`9c8dc23`) e worktree do central em `origin/main` (`a6d00a5`, PR #155 e PR #156; o checkout do central estava atrás de origin/main), mais `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` no central; e `pytest` do teste e da suíte no central | 6 linhas `igual ...` (scripts/render_prompts.py, cópia da skill, prompts/cursor/doc-framework.mdc, tests/test_prompts_sem_prd_ts.py, rules/kit-index.yaml, INDEX.md); `exit=0`; no central, teste novo: 3 passed e suíte: 295 passed | n/a (comando de medição; teste espelhado coberto por A03) | Sim | n/a | automatizado |
| 2 | A09 | `python3 -m pytest _framework/tests/test_prompts_sem_prd_ts.py -k gerados_cobrem -v` em `9c8dc23`; em cópia descartável, removido `copilot-instructions.md` da tupla `GERADOS`, pytest do arquivo inteiro; restaurado; removido `universal.md`, idem; restaurado; extra: removido `doc-framework.mdc` | Sem mutação: `1 passed, 2 deselected`. Sem Copilot: 1 failed, 2 passed (asserção do conjunto de nomes, `:48` no original, `:47` na cópia com uma linha a menos). Sem universal: 1 failed, 2 passed. Extra, sem Cursor: 1 failed, 2 passed. Restaurado: 3 passed | As duas mutações que sobreviviam na rodada 1 (remover o Copilot, remover o `universal.md`) agora são derrubadas por `test_gerados_cobrem_os_tres_prompts` | Sim | _framework/tests/test_prompts_sem_prd_ts.py:48, _framework/tests/test_prompts_sem_prd_ts.py:49 | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | nenhum (sizing small, precedente SDD-DTF-0047) |
| relates_to | SDD-DTF-0042 (frente de otimização do kit), SDD-DTF-0048 (deixou este resíduo fora de escopo) |
| Gate RFC → ADR | Nenhum critério de `decision_gates.rfc_to_adr` se aplica |
