---
id: SDD-DTF-0051
type: SDD
title: "Resumos do mapa: map_summaries com precedência sobre o banner e testes das ramificações de _cut_words"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0049]
source_docs:
  - id: "SPEC-DTF-0027"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0027.md"
  - id: "SPEC-DTF-0026"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0026.md"
  - id: "SPEC-DTF-0022"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0022.md"
consumption_instructions: "Compilada da SPEC-DTF-0026 (approved), corrigida pela SPEC-DTF-0027 (approved): os textos dos §5, §14 e §15 são os da 0027, porque os da 0026 estouravam o teto de 180 bytes por linha do mapa. A 0026 complementa as SPECs 0022 e 0024: só o RF02 (cadeia de fontes) e a regra de corte do RF03 da 0022 são tocados, e o código de _cut_words não muda, só ganha testes. Ordem: escrever os testes de RF03 e RF04 primeiro e vê-los falhar (RF04) ou passar-e-sobreviver-à-mutação (RF03, X3); depois inverter a tupla de fontes em _section_summary; depois as três entradas em kit-index.yaml; depois regenerar. Gerados (mapa, INDEX, prompts, cópia da skill) nunca à mão: render_prompts.py e render_indexes.py. Não usar isolation: worktree do agente; criar o worktree à mão. O central espelha por PR próprio (task 6, prefixo central:). Implementar em sessão separada; verificação por sdd-verifier em outra sessão."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, indice, mapa, resumo]
---

# Resumos do mapa: map_summaries com precedência sobre o banner e testes das ramificações de _cut_words

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório do projeto (kit) porque é o documento lido pela
> IA ao implementar.

## Resumo executivo

Três resumos do mapa `workflow-rules.map.md` (§5, §14 e §15) terminam em `…`
sem dizer qual seção abrir, porque `map_summaries` de `kit-index.yaml` é a 4ª
fonte da cadeia e o banner do YAML vence. Esta SDD inverte a ordem
(`map_summaries` vira a 1ª fonte), define os três textos e cobre com teste
duas coisas que hoje sobrevivem à mutação: a ramificação de `_cut_words` que
descarta palavra final terminada em `(`, `:`, `,` ou `;` (mutação X3,
`49 passed` mesmo sem ela) e a própria precedência.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR: nenhum critério de `decision_gates.rfc_to_adr` se aplica
(SPEC-DTF-0026, `parent_adr: null`). Vale a SPEC-DTF-0026; a SPEC-DTF-0022
permanece para tudo que a 0026 não altera.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Em `_section_summary`, `map_summaries` passa a ser a 1ª fonte; sem entrada, a cadeia body, parágrafo, escalar, tail segue como está | Quando `kit-index.yaml` tiver `map_summaries` para um id cujo YAML também tem banner, o sistema deve usar o override como Resumo |
| RF02 | `kit-index.yaml` ganha `map_summaries` para §5, §14 e §15 com os textos exatos da tabela abaixo, cada um cabendo na sobra da linha do mapa (84, 51 e 64 bytes), e a linha do mapa não termina em `…` e tem até 180 bytes | Quando o mapa for regenerado, o sistema deve mostrar nos §5, §14 e §15 exatamente esses textos, sem `…` |
| RF03 | Testes de `_cut_words` para palavra final terminada em `:`, `,`, `;` e `(` (com parêntese balanceado antes) | Quando `_cut_words` receber os textos da tabela de RF03, o sistema deve devolver a saída indicada; a mutação X3 deve reprovar pelo menos um teste |
| RF04 | Teste de precedência com fixture: banner com override usa o override; banner sem override usa o banner | Quando a ordem antiga da cadeia for restaurada, o sistema deve reprovar pelo menos um teste |

Textos de RF02 (fixos; da SPEC-DTF-0027, que substitui os da 0026 por caberem na linha de 180 bytes):

| § | Resumo |
|---|---|
| 5 | `Incidente e postmortem têm ciclo próprio (open a closed), fora do padrão` |
| 14 | `Gate: sem commit de implementação direto em main` |
| 15 | `Gate de conteúdo: SPEC e SDD sem placeholder antes de in_review` |

Casos de RF03 (`_cut_words(texto, limite)`):

| Texto | Limite | Saída esperada |
|---|---|---|
| `alfa beta gama: delta epsilon` | 20 | `alfa beta…` |
| `alfa beta gama, delta epsilon` | 20 | `alfa beta…` |
| `alfa beta gama; delta epsilon` | 20 | `alfa beta…` |
| `alfa) beta gama( delta epsilon` | 22 | `alfa) beta…` |

Fora de escopo: reescrever §3, §13, §16, §18 e §19; mudar `SUMMARY_MAX`,
`SUMMARY_MIN`, `TITLE_MAX`, `DANGLING` ou os tetos; mudar o código de
`_cut_words`; editar SPECs `approved`.

## Especificação técnica consolidada

- **`_section_summary`** em `_framework/scripts/render_indexes.py`: a tupla
  `(body, " ".join(para), _scalar_source(first_key_value), override, tail)`
  passa a `(override, body, " ".join(para), _scalar_source(first_key_value), tail)`.
  Nenhuma outra linha da função muda. A cópia em
  `_framework/skills/doc-traceability-framework/scripts/render_indexes.py` é
  gerada por `render_prompts.py`; nunca à mão.
- **`kit-index.yaml`**: acrescentar as chaves `"5"`, `"14"` e `"15"` em
  `map_summaries`, com os textos de RF02, e trocar o comentário do topo
  ("quando o YAML não tem fonte") por "e vale mesmo que o YAML tenha fonte".
  Entradas existentes (§2, §6, §7, §9, §12) não mudam.
- **Testes** em `_framework/tests/test_render_indexes.py`: o teste `test_map_summaries_so_sem_fonte_automatica` codifica a ordem antiga da cadeia e é substituído pelo de precedência (RF04); um teste com as
  quatro linhas de RF03 (nome contendo `cut_words`) e um teste
  `test_precedencia_override_sobre_banner` (nome contendo
  `precedencia_override`), ambos sem mock.
- **Gerados**: `_framework/rules/workflow-rules.map.md`,
  `_framework/INDEX.md`, `docs/sdd/INDEX.md` e a cópia da skill, por
  `render_prompts.py` e `render_indexes.py`.
- **Espelho**: central recebe os mesmos arquivos do `_framework/`.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Rodar A01, A03 e A05 no `main` e guardar as saídas reais (ANTES) | RF02, RF03 | (decisão pura) | |
| 2 | Testes de RF03 e RF04 (o de RF04 substitui `test_map_summaries_so_sem_fonte_automatica`, que afirma a ordem antiga); ver o de RF04 falhar antes da troca | RF03, RF04 | `_framework/tests/test_render_indexes.py` | 1 |
| 3 | Inverter a ordem da tupla de fontes | RF01 | `_framework/scripts/render_indexes.py` | 2 |
| 4 | Entradas e comentário em `kit-index.yaml` | RF02 | `_framework/rules/kit-index.yaml` | 3 |
| 5 | Regenerar com `render_prompts.py` e `render_indexes.py`; rodar A01 a A10 registrando comando e saída reais | RF01 a RF04 | `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md`, `docs/sdd/INDEX.md`, cópia da skill de `render_indexes.py` | 4 |
| 6 | Espelhar no central em worktree, branch e PR próprios | RF01 a RF04 | `central:_framework/scripts/render_indexes.py`, cópia da skill, `central:_framework/rules/kit-index.yaml`, `central:_framework/rules/workflow-rules.map.md`, `central:_framework/tests/test_render_indexes.py`, `central:_framework/INDEX.md` | 5 |

Ordem: 1, 2, 3, 4, 5, 6 (cadeia linear; sem paralelismo).

## Critérios de aceite / definição de pronto

Executar na raiz do kit. "Antes" = `main`, antes de qualquer edição.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF02: resumos do §5, §14 e §15 | `grep -e '^\| §5 ' -e '^\| §14 ' -e '^\| §15 ' _framework/rules/workflow-rules.map.md` | ANTES: 3 linhas terminando em `…`; DEPOIS: 3 linhas com os textos de RF02, nenhuma com `…` e cada uma com até 180 bytes (`printf '%s' "$linha" \| wc -c`) | automatizado |
| A02 | RF03, RF04: testes novos | `python3 -m pytest _framework/tests/test_render_indexes.py -k "cut_words or precedencia_override" -v` | ANTES: `precedencia_override` falha e o de RF03 passa; DEPOIS: 0 failed | automatizado |
| A03 | RF03: mutação X3 derrubada | Em cópia descartável: `sed -i 's/ or words\[-1\]\[-1\] in "(:,;"//' _framework/scripts/render_indexes.py`; `python3 -m pytest _framework/tests/test_render_indexes.py -q`; restaurar | ANTES (sem os testes novos): `49 passed`; DEPOIS: com a mutação, pelo menos 1 failed | automatizado |
| A04 | RF04: precedência derrubável | Em cópia descartável, devolver `override` à 4ª posição da tupla; `pytest -k precedencia_override` | Com a ordem antiga: pelo menos 1 failed; com a nova: 0 failed | automatizado |
| A05 | RF01: entradas antigas de `map_summaries` inalteradas | `git diff -U0 _framework/rules/workflow-rules.map.md \| grep -e '^[-+]\| §2 ' -e '^[-+]\| §6 ' -e '^[-+]\| §7 ' -e '^[-+]\| §9 ' -e '^[-+]\| §12 '; echo "exit=$?"` | Sem linhas e `exit=1` | automatizado |
| A06 | RF02: mapa dentro dos tetos e índices em dia | `python3 _framework/scripts/render_indexes.py --check; echo "exit=$?"` | `exit=0` | automatizado |
| A07 | RF01 a RF04: suíte, formatação, gerados e cópia da skill | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff format --check _framework/scripts; python3 _framework/scripts/render_prompts.py --check; cmp _framework/scripts/render_indexes.py _framework/skills/doc-traceability-framework/scripts/render_indexes.py; echo "exit=$?"` | 0 failed, `cmp` sem saída e `exit=0` | automatizado |
| A08 | Só os arquivos previstos mudaram | `git diff --name-only main` | Só os arquivos das tasks 2 a 5, esta SDD e os gerados de `docs/sdd/`; nenhum `workflow-rules.yaml`, nenhum `prompts/` | automatizado |
| A09 | Escopo do código: só a tupla mudou | `git diff -U0 main -- _framework/scripts/render_indexes.py` | Um hunk em `_section_summary` que só reordena os elementos da tupla; `_cut_words` intocada | automatizado |
| A10 | Espelho no central | Em `/home/michel/doc-traceability-central`: `for f in scripts/render_indexes.py skills/doc-traceability-framework/scripts/render_indexes.py rules/kit-index.yaml rules/workflow-rules.map.md tests/test_render_indexes.py INDEX.md; do cmp /home/michel/doc-traceability-framework/_framework/$f _framework/$f && echo "igual $f"; done; python3 _framework/scripts/render_indexes.py --check; echo "exit=$?"` | 6 linhas `igual ...` e `exit=0` | automatizado |
| A11 | SPEC-DTF-0027 RF02: constantes e tetos intactos | `python3 -c "import sys; sys.path.insert(0,'_framework/scripts'); import render_indexes as ri; print(ri.SUMMARY_MIN, ri.SUMMARY_MAX)"; git diff -U0 main -- _framework/scripts/render_indexes.py \| grep -e '^[-+].*SUMMARY_M' -e '^[-+].*TITLE_M'; echo "exit=$?"` | `28 100`, nenhuma linha de diff e `exit=1` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** branch `sdd/SDD-DTF-0051-resumos-mapa`, em worktree
  do kit criado à mão a partir de `origin/main`. Commits com
  `Refs: SDD-DTF-0051`. Nunca em `main`, nunca force-push. O espelho é
  feito em worktree próprio do central, com branch e PR próprios.
- **Só a tupla.** Não mexer no código de `_cut_words`, em `SUMMARY_MAX`,
  `SUMMARY_MIN`, `DANGLING` nem em outros resumos.
- **Testes primeiro.** Escrever os testes e guardar a saída antes da troca.
- **Gerados só por script**, nunca à mão; nem `docs/sdd/INDEX.md` nem
  `registry.md` (`render_indexes.py` e `generate_registry_md.py docs/sdd`).
- **Tabelas markdown:** não escrever regex com `](` nem alternância com
  barra vertical dentro de célula; usar `grep -e` repetido.
- **Se uma linha do mapa passar de 180 bytes**, ou se o resumo sair com
  `…`, parar: o texto se corrige por nova SPEC; não baixar teto nem piso.
- **Evidência de verificação** só pelo `sdd-verifier`, em sessão separada.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF04) tem código
      correspondente.
- [x] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", na "Decomposição em tasks" ou em "Instruções
      específicas".
- [x] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado.
- [x] `workflow-rules.yaml` intocado e `framework.version` igual ao de
      `origin/main`.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 2 (subagente `sdd-verifier` com contexto próprio, worktrees de `origin/main`: kit `6f42e45`, central `9cd0f0d`). Na rodada 1 (kit `6e265f1`) a mutação "override em 2º, depois do corpo do banner" sobrevivia; o PR #140 acrescentou o caso e o PR #160 o espelhou. "ANTES" de A01 a A11 é o SHA fixo `551b928` (main do kit antes do PR #139), e não `main`, que avançou. Fidelidade à origem: `check_source_docs.py` confere `source_docs` com o registry central.

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0051.md`.
Veredito: **PASS**, com ressalva aceita: A01 e o texto dos §5, §14 e §15 no `kit-index.yaml` não têm asserção automatizada além do `render_indexes.py --check`.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 2 | Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0051.md <central>/docs/DTF` | `source_docs ... conferem com o registry central`, `exit=0`; RF01 a RF04 da 0026 e RF01/RF02 da 0027 presentes na SDD; textos do RF02 são os da 0027; nenhum critério relaxado | n/a | Sim | n/a | automatizado |
| 2 | A01 | `grep -e '^\| §5 ' -e '^\| §14 ' -e '^\| §15 ' _framework/rules/workflow-rules.map.md` e `wc -c` | DEPOIS: 171, 179 e 180 bytes, nenhuma com `…`; ANTES (551b928): 3 com `…` | Sem asserção automatizada (ressalva); `--check` derruba divergência sem regeneração | Sim | n/a | automatizado |
| 2 | A02 | `pytest test_render_indexes.py -k "cut_words or precedencia_override" -v` | 2 passed; testes novos sobre o código antigo: 1 failed, 1 passed | Precedência falha com o código antigo | Sim | _framework/tests/test_render_indexes.py:607, _framework/tests/test_render_indexes.py:798 | automatizado |
| 2 | A03 | Cópia: `sed` remove ` or words[-1][-1] in "(:,;"`; pytest do arquivo | ANTES: 49 passed com a mutação; DEPOIS: 1 failed, 49 passed | X3 derrubada; cada caractere sozinho também | Sim | _framework/tests/test_render_indexes.py:798 | automatizado |
| 2 | A04 | Cópia com `override` em 4º; `pytest -k precedencia_override` | Ordem antiga 1 failed; nova 1 passed | Derrubada; override em 2º, 3º e 5º também | Sim | _framework/tests/test_render_indexes.py:607 | automatizado |
| 2 | A05 | `git diff -U0 551b928 HEAD -- workflow-rules.map.md` filtrado por §2, §6, §7, §9, §12 | Sem linhas, `exit=1` | n/a (medição) | Sim | n/a | automatizado |
| 2 | A06 | `render_indexes.py --check; echo exit=$?` | Em dia, `exit=0` | `--check` sai 1 com mapa divergente | Sim | n/a | automatizado |
| 2 | A07 | pytest das duas suítes; `ruff format --check`; `render_prompts.py --check`; `cmp` | 296 passed; 33 files already formatted; `cmp` sem saída; `exit=0` | Sensores de A03 e A04 | Sim | n/a | automatizado |
| 2 | A08 | `git diff --name-only 551b928 HEAD` | 5 arquivos previstos | n/a (medição) | Sim | n/a | automatizado |
| 2 | A09 | `git diff -U0 551b928 HEAD -- _framework/scripts/render_indexes.py` | 1 hunk, só a tupla | n/a (medição) | Sim | n/a | automatizado |
| 2 | A10 | `cmp` dos 6 arquivos kit x central; `--check` no central | 6 `igual ...`; `exit=0` | n/a (medição) | Sim | n/a | automatizado |
| 2 | A11 | Constantes e diff por `SUMMARY_M` e `TITLE_M` | `28 100`, sem diff, `exit=1` | n/a (medição) | Sim | n/a | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0027, SPEC-DTF-0026, SPEC-DTF-0022 |
| relates_to | SDD-DTF-0049 (mapa e INDEX da rodada 2) |
| Gate RFC → ADR | Nenhum critério de `decision_gates.rfc_to_adr` se aplica |
