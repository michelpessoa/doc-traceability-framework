---
id: SDD-DTF-0056
type: SDD
title: "registry.md com seção para todo tipo de documento: ordem derivada de document_types, sem descarte silencioso"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-17"
updated: "2026-11-17"
relates_to: [SDD-DTF-0043]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção pontual de tooling pedida pelo owner em 2026-11-17; ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0047 e SDD-DTF-0052). Leia esta SDD inteira; ela nomeia as funções, a ordem, os rótulos e os testes. Teste primeiro, visto falhar; depois o código. A cópia do script na skill é gerada por render_prompts.py, nunca à mão. O central espelha os mesmos arquivos e regenera docs/DTF/registry.md com o script, em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [registry, gerado, tooling, tipos-de-documento]
---

# registry.md com seção para todo tipo de documento: ordem derivada de document_types, sem descarte silencioso

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`_framework/scripts/generate_registry_md.py` fixa
`TYPE_ORDER = ["STRAT", "RFC", "ADR", "PRD", "TS", "SDD"]` e só renderiza
seção para esses tipos. Desde a 2.0.0, PRD e TS viraram SPEC, e BASE, INC e
PM existem em `document_types`; documentos desses tipos entram na contagem
"Total de documentos" mas não aparecem em nenhuma seção. No central,
`docs/DTF/registry.md` diz **51** documentos e mostra só 22 (STRAT, RFC e
ADR): as 29 SPECs somem. Esta SDD faz a ordem vir de `workflow-rules.yaml`
e garante que todo documento do registry caia em alguma seção.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: um script e seu teste, sem mudança de regra, schema ou contrato.
`workflow-rules.yaml` não muda (não ganha chave de rótulo), e
`framework.version` fica em `2.5.0`: é falha de execução, não desenho
(`lessons_policy`).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | A ordem das seções é a ordem das chaves de `document_types` seguida da de `legacy_document_types` em `workflow-rules.yaml` | Quando o YAML for acessível, `type_order(rules)` deve devolver `STRAT, RFC, ADR, SPEC, SDD, BASE, INC, PM, PRD, TS` |
| RF02 | Sem o YAML acessível, vale uma ordem embutida com os mesmos dez tipos | Quando `find_rules_file` devolver `None`, o registry com um documento de cada um dos dez tipos deve ter uma seção para cada um |
| RF03 | Nenhum documento do registry é descartado: tipo ausente da ordem (inclusive tipo vazio) ganha seção própria depois dos declarados, em ordem alfabética, com o rótulo `Tipo não declarado: {tipo}` | Quando o registry tiver um documento de tipo `XYZ`, seu id deve aparecer na saída sob `## Tipo não declarado: XYZ (1)` |
| RF04 | O rótulo de cada seção é o rótulo curto embutido do tipo; tipo declarado no YAML sem rótulo curto usa o `name` do YAML | Quando o registry tiver STRAT, os títulos atuais não mudam (`## Strategy Doc (n)`); SPEC sai como `## SPEC (n)` |
| RF05 | A soma das linhas das seções é igual ao "Total de documentos" | Quando o teste contar as linhas de tabela de um registry com um documento de cada tipo declarado mais um não declarado, a soma deve ser igual ao total |
| RF06 | A ordem embutida não fica para trás do YAML | Quando um tipo existir em `document_types` ou `legacy_document_types` e não estiver na ordem embutida ou nos rótulos curtos, um teste deve falhar |

Fora de escopo: o conteúdo das tabelas (colunas, formato da linha), o
cabeçalho e o `--check`, `workflow-rules.yaml`, outros scripts, e a
regeneração de `registry.md` em projetos que não sejam o DTF do central.

## Especificação técnica consolidada

- **Onde.** `_framework/scripts/generate_registry_md.py`.
- **Constantes.** `TYPE_ORDER` passa a ser a ordem embutida com os dez
  tipos (`STRAT, RFC, ADR, SPEC, SDD, BASE, INC, PM, PRD, TS`). `TYPE_LABEL`
  cobre os dez: `STRAT: "Strategy Doc"`, `RFC: "RFC"`, `ADR: "ADR"`,
  `SPEC: "SPEC"`, `SDD: "SDD"`, `BASE: "Baseline"`, `INC: "Incidente"`,
  `PM: "Postmortem"`, `PRD: "PRD"`, `TS: "Tech Spec"`. Nova constante
  `UNDECLARED_LABEL = "Tipo não declarado: {type}"`.
- **`type_order(rules: dict) -> list[str]`.** Chaves de
  `rules["document_types"]` e depois de `rules["legacy_document_types"]`,
  sem repetição; se as duas forem vazias ou ausentes, `list(TYPE_ORDER)`.
- **`type_label(doc_type: str, rules: dict) -> str`.** `TYPE_LABEL` se
  houver; senão o `name` do tipo em `document_types` ou
  `legacy_document_types`; senão `UNDECLARED_LABEL`.
- **`render_registry(data)`.** Carrega as regras uma vez
  (`load_rules()` só se `find_rules_file()` achar o YAML; senão `{}`).
  Agrupa por `str(d.get("type") or "")`. Percorre `type_order(rules)` e, em
  seguida, os tipos presentes que não estão na ordem, em ordem alfabética.
  O cabeçalho e a linha "Total de documentos" não mudam.
- **Testes.** Em `_framework/scripts/tests/test_generate_registry_md.py`:
  ordem com o YAML real (RF01); fallback com um documento de cada tipo
  (RF02); tipo não declarado (RF03); rótulos (RF04); soma das linhas igual
  ao total (RF05); ordem embutida e rótulos cobrem o YAML real (RF06).
- **Cópia da skill.** `_framework/skills/doc-traceability-framework/scripts/generate_registry_md.py`
  é regenerada por `render_prompts.py`.
- **Espelho no central.** O script, a cópia da skill e o teste; depois
  `python3 _framework/scripts/generate_registry_md.py docs/DTF` regenera
  `docs/DTF/registry.md`.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar com o código atual | RF01 a RF06 | `_framework/scripts/tests/test_generate_registry_md.py` | |
| 2 | Ordem derivada do YAML, rótulos e seção para tipo não declarado | RF01 a RF05 | `_framework/scripts/generate_registry_md.py` | 1 |
| 3 | Regenerar a cópia da skill e o índice do kit (a faixa de tamanho do teste muda) | RF01 a RF05 | `_framework/skills/doc-traceability-framework/scripts/generate_registry_md.py`, `_framework/INDEX.md` | 2 |
| 4 | Espelhar no central e regenerar `docs/DTF/registry.md`, em branch e PR próprios | RF01 a RF06 | `central:_framework/scripts/generate_registry_md.py`, `central:_framework/skills/doc-traceability-framework/scripts/generate_registry_md.py`, `central:_framework/scripts/tests/test_generate_registry_md.py`, `central:docs/DTF/registry.md`, `central:_framework/INDEX.md` (gerado, idêntico ao do kit) | 3 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01 a RF06: testes novos | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -q` | ANTES da task 2: pelo menos 5 failed; DEPOIS: todos passam | automatizado |
| A02 | RF03: sensor de mutação | Em cópia descartável, remover o laço dos tipos fora da ordem em `render_registry`; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF01: sensor da ordem | Em cópia descartável, fazer `type_order` devolver sempre `list(TYPE_ORDER)` sem `SPEC`; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A04 | Gerados em dia e cópia da skill idêntica | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/generate_registry_md.py _framework/skills/doc-traceability-framework/scripts/generate_registry_md.py` | `exit=0` e `cmp` sem saída | automatizado |
| A05 | Suíte completa, lint e tipos sem regressão | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts` | 0 failed e os três sem erro | automatizado |
| A06 | Só os arquivos previstos mudaram | `git diff --name-only origin/main` | Só os arquivos das tasks 1 a 3, esta SDD e os gerados de `docs/sdd/` (`registry.yaml`, `registry.md`, `INDEX.md`) | automatizado |
| A07 | Central: espelho idêntico e SPECs no registry.md | No central: `cmp` dos 3 arquivos contra o kit; `python3 _framework/scripts/generate_registry_md.py docs/DTF --check`; `grep -c '^\| \`SPEC-DTF-' docs/DTF/registry.md`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída; `em dia`; contagem igual ao número de SPECs em `docs/DTF/registry.yaml`; `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0056-registry-md-todos-os-tipos`, a
  partir de `origin/main`. Commits com `Refs: SDD-DTF-0056`. Nunca em
  `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Não mudar** `workflow-rules.yaml`, o formato das linhas de tabela, o
  cabeçalho nem o `--check`.
- **Gerados só por script:** `render_prompts.py` para a cópia da skill e os
  índices; `generate_registry_md.py` para todo `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  separada.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF06) tem código ou teste
      correspondente.
- [x] Todo arquivo tocado pela implementação aparece na "Decomposição em
      tasks". (Rodada 2. Kit, `012ff47..61ce3eb`: os 4 arquivos das tasks 1 a
      3, esta SDD, os gerados de `docs/sdd/` e o relatório da verificação.
      Central, `origin/main...679876b`: os 5 arquivos da task 4, que ganhou
      `central:_framework/INDEX.md` no ajuste pós-aprovação aceito pelo
      owner.)
- [x] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado.
- [x] `workflow-rules.yaml` intocado e `framework.version` igual ao de
      `origin/main`.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 1: todas as linhas abaixo foram rodadas nesta sessão, na branch
`sdd/SDD-DTF-0056-registry-md-todos-os-tipos` (head `a620b1c`), com base fixa
`012ff47` (`origin/main` no momento da verificação). O "antes" do A01 é um
worktree descartável de `012ff47` com o arquivo de teste novo copiado por
cima. Os sensores A02 e A03 e as mutações extras rodaram em worktree
descartável do head, nunca no checkout. O A07 rodou no central, na branch
`claude/laughing-galileo-d9nymc` (head `e41dc71`). Veredito da rodada 1:
FAIL, porque o A04 reprovou (`docs/sdd/INDEX.md` não foi regenerado depois da
edição da task 3).

Rodada 2: outro verificador independente, em sessão separada, rodou de novo
A01 a A07 na mesma branch, no head `61ce3eb`, com a mesma base fixa `012ff47`.
O "antes" do A01 é um worktree descartável de `012ff47` com o arquivo de
teste atual (13 testes) copiado por cima. Os sensores A02 e A03 e as quatro
mutações extras, incluindo as duas que sobreviviam na rodada 1, rodaram em
worktree descartável do head, nunca no checkout. O A07 rodou no central, na
branch `claude/laughing-galileo-d9nymc` (head `679876b`). As linhas da rodada
1 ficam abaixo como histórico.

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0056.md`.
Veredito: **PASS** (rodada 2). Antes do passo 5, o pipe cru do comando `grep`
na linha A07 dos "Critérios de aceite" precisa ser escapado; sem isso,
`validate_state.py` reprova a SDD em `implemented` (validation, item 4). Nas
duas linhas A07 abaixo o pipe já está escapado, só como formatação.

Fidelidade à origem: n/a, sizing `small` sem `source_docs` (precedente SDD-DTF-0047 e SDD-DTF-0052).

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | A01 | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -q`, ANTES em worktree de `012ff47` com o teste novo copiado; DEPOIS no head `a620b1c` | ANTES: `8 failed, 4 passed` (falham os 8 testes novos: `AttributeError` de `type_order`/`type_label`, `assert 6 == 10` de seções, `'## Tipo não declarado: XYZ (1)'` ausente, `assert 6 == 12` de linhas, conjunto de `TYPE_ORDER` sem SPEC/BASE/INC/PM; os 4 anteriores passam). DEPOIS: `12 passed` | Ver A02, A03 e as mutações extras no validation | Sim | _framework/scripts/tests/test_generate_registry_md.py:77, _framework/scripts/tests/test_generate_registry_md.py:82, _framework/scripts/tests/test_generate_registry_md.py:89, _framework/scripts/tests/test_generate_registry_md.py:97, _framework/scripts/tests/test_generate_registry_md.py:105, _framework/scripts/tests/test_generate_registry_md.py:112, _framework/scripts/tests/test_generate_registry_md.py:121, _framework/scripts/tests/test_generate_registry_md.py:129 | automatizado |
| 1 | A02 | Worktree descartável do head: linha `order += sorted(t for t in by_type if t not in order)` removida de `render_registry`; pytest do A01; restaurado do backup | Com a mutação: `2 failed, 10 passed` (`test_tipo_nao_declarado_ganha_secao_propria`, `test_soma_das_linhas_igual_ao_total`). Restaurado: `12 passed`; `git status` limpo | Mutação derrubada | Sim | _framework/scripts/tests/test_generate_registry_md.py:97, _framework/scripts/tests/test_generate_registry_md.py:121 | automatizado |
| 1 | A03 | Worktree descartável do head: corpo de `type_order` trocado por `return [t for t in TYPE_ORDER if t != "SPEC"]`; pytest do A01; restaurado | Com a mutação: `3 failed, 9 passed` (`test_type_order_vem_do_yaml_real`, `test_type_order_sem_yaml_usa_ordem_embutida`, `test_rotulos_curtos`). Restaurado: `12 passed`; `git status` limpo. Extras: sem `or list(TYPE_ORDER)` dá 1 failed; `type_label` sem `name` do YAML dá 1 failed; `type_order` fixa em `list(TYPE_ORDER)` e `rules = {}` sobrevivem (12 passed; mutantes equivalentes enquanto YAML e constante coincidem) | Mutação derrubada | Sim | _framework/scripts/tests/test_generate_registry_md.py:77, _framework/scripts/tests/test_generate_registry_md.py:82, _framework/scripts/tests/test_generate_registry_md.py:105 | automatizado |
| 1 | A04 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/generate_registry_md.py _framework/skills/doc-traceability-framework/scripts/generate_registry_md.py` | `✅ _framework/INDEX.md: em dia.`; `❌ docs/sdd/INDEX.md: divergente do gerado — rode render_indexes.py.`; `exit=1`; `cmp` sem saída. Regenerado em worktree descartável, a linha da SDD-DTF-0056 passa a começar por `_framework/INDEX.md` | n/a (comando de medição) | Não | docs/sdd/INDEX.md:61 | automatizado |
| 1 | A05 | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts` | `392 passed in 50.85s`; `All checks passed!`; `38 files already formatted`; `Success: no issues found in 38 source files` | sem sensor próprio (suíte inteira; sensores em A02 e A03) | Sim | _framework/scripts/tests/test_generate_registry_md.py:77 | automatizado |
| 1 | A06 | `git diff --name-status origin/main` (= `012ff47`); `git diff --quiet origin/main -- _framework/rules/workflow-rules.yaml` | 8 arquivos: `_framework/INDEX.md`, o script, o teste, a cópia da skill, `docs/sdd/INDEX.md`, `docs/sdd/SDD-DTF-0056.md` (A), `docs/sdd/registry.md`, `docs/sdd/registry.yaml`; `workflow-rules.yaml` intocado (exit 0), `framework.version` `2.5.0` | n/a (comando de medição) | Sim | n/a | automatizado |
| 1 | A07 | No central (`e41dc71`): `cmp` dos 3 arquivos contra o kit; `python3 _framework/scripts/generate_registry_md.py docs/DTF --check`; `grep -c '^\| \`SPEC-DTF-' docs/DTF/registry.md`; `grep -c 'type: SPEC' docs/DTF/registry.yaml`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | 3 linhas `igual ...`; `✅ docs/DTF/registry.md: em dia.`; `29` e `29`; `exit=0` (`Todas as verificações do framework passaram`). Seções: Strategy Doc 3, RFC 10, ADR 9, SPEC 29 = 51 = total. Diff do central: os 4 arquivos da task 4 e mais `_framework/INDEX.md` (idêntico ao do kit) | n/a (comando de medição; teste espelhado, 12 passed no central) | Sim | n/a | automatizado |
| 2 | A01 | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -q`, ANTES em worktree de `012ff47` com o teste atual copiado; DEPOIS no head `61ce3eb` | ANTES: `9 failed, 4 passed` (falham os 9 testes da SDD-DTF-0056, inclusive `test_ordem_segue_o_yaml_mesmo_diferente_da_embutida` com `AttributeError: ... no attribute 'type_order'`; os 4 anteriores passam). DEPOIS: `13 passed` | Ver A02, A03 e as quatro mutações extras | Sim | _framework/scripts/tests/test_generate_registry_md.py:77, _framework/scripts/tests/test_generate_registry_md.py:82, _framework/scripts/tests/test_generate_registry_md.py:89, _framework/scripts/tests/test_generate_registry_md.py:97, _framework/scripts/tests/test_generate_registry_md.py:105, _framework/scripts/tests/test_generate_registry_md.py:112, _framework/scripts/tests/test_generate_registry_md.py:121, _framework/scripts/tests/test_generate_registry_md.py:129, _framework/scripts/tests/test_generate_registry_md.py:136, _framework/scripts/tests/test_generate_registry_md.py:140 | automatizado |
| 2 | A02 | Worktree descartável do head: linha `order += sorted(t for t in by_type if t not in order)` removida de `render_registry`; pytest do A01; restaurado do backup | Com a mutação: `2 failed, 11 passed` (`test_tipo_nao_declarado_ganha_secao_propria`, `test_soma_das_linhas_igual_ao_total`). Restaurado: `13 passed`; `git status` limpo | Mutação derrubada | Sim | _framework/scripts/tests/test_generate_registry_md.py:97, _framework/scripts/tests/test_generate_registry_md.py:121 | automatizado |
| 2 | A03 | Worktree descartável do head: corpo de `type_order` trocado por `return [t for t in TYPE_ORDER if t != "SPEC"]`; pytest do A01; restaurado. Extras: `type_order` fixa em `return list(TYPE_ORDER)`; `rules = {}` fixo em `render_registry`; `type_order` sem `or list(TYPE_ORDER)`; `type_label` sem o `name` do YAML | Com a mutação: `4 failed, 9 passed` (`test_type_order_vem_do_yaml_real`, `test_type_order_sem_yaml_usa_ordem_embutida`, `test_rotulos_curtos`, `test_ordem_segue_o_yaml_mesmo_diferente_da_embutida`). Extras, cada uma `1 failed, 12 passed`: `type_order` fixa cai em `:136` e `rules = {}` cai em `:140` (as duas sobreviventes da rodada 1, agora derrubadas pelo teste novo); sem fallback cai em `test_type_order_sem_yaml_usa_ordem_embutida`; sem `name` cai em `test_rotulo_cai_no_name_do_yaml_sem_rotulo_curto`. Restaurado após cada uma: `13 passed`; `cmp` com o backup e `git status` limpos | Mutações derrubadas (6 de 6) | Sim | _framework/scripts/tests/test_generate_registry_md.py:77, _framework/scripts/tests/test_generate_registry_md.py:82, _framework/scripts/tests/test_generate_registry_md.py:105, _framework/scripts/tests/test_generate_registry_md.py:136, _framework/scripts/tests/test_generate_registry_md.py:140 | automatizado |
| 2 | A04 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/generate_registry_md.py _framework/skills/doc-traceability-framework/scripts/generate_registry_md.py` | `✅ _framework/INDEX.md: em dia.`; `✅ docs/sdd/INDEX.md: em dia.` (mais o aviso pré-existente de 30 SDDs sem seção de arquivos); `exit=0`; `cmp` sem saída | n/a (comando de medição) | Sim | docs/sdd/INDEX.md:61 | automatizado |
| 2 | A05 | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts` | `393 passed in 53.37s`; `All checks passed!`; `38 files already formatted`; `Success: no issues found in 38 source files` | sem sensor próprio (suíte inteira; sensores em A02 e A03) | Sim | _framework/scripts/tests/test_generate_registry_md.py:77 | automatizado |
| 2 | A06 | `git diff --name-status origin/main` (= `012ff47`); `git diff --quiet 012ff47 -- _framework/rules/workflow-rules.yaml` | 9 arquivos: `_framework/INDEX.md`, o script, o teste, a cópia da skill, `docs/sdd/INDEX.md`, `docs/sdd/SDD-DTF-0056.md` (A), `docs/sdd/registry.md`, `docs/sdd/registry.yaml` e `docs/sdd/validation-SDD-DTF-0056.md` (A, relatório desta verificação, exigido pelo gate de CI); `workflow-rules.yaml` intocado (exit 0), `framework.version` `2.5.0` | n/a (comando de medição) | Sim | n/a | automatizado |
| 2 | A07 | No central (`679876b`): `cmp` dos 3 arquivos e de `_framework/INDEX.md` contra o kit; `python3 _framework/scripts/generate_registry_md.py docs/DTF --check`; `grep -c '^\| \`SPEC-DTF-' docs/DTF/registry.md`; `grep -c 'type: SPEC' docs/DTF/registry.yaml`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"`; `git diff --name-status origin/main...HEAD` | 4 linhas `igual ...`; `✅ docs/DTF/registry.md: em dia.`; `29` e `29`; `exit=0` (`Todas as verificações do framework passaram`). Seções: Strategy Doc 3, RFC 10, ADR 9, SPEC 29 = 51 = total. Diff do central: os 5 arquivos da task 4. Teste espelhado: `13 passed`; `render_prompts.py --check` exit 0 | n/a (comando de medição; teste espelhado coberto por A02/A03) | Sim | n/a | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | nenhum (sizing small, precedente SDD-DTF-0047 e SDD-DTF-0052) |
| relates_to | SDD-DTF-0043 (RF08: cabeçalho sem hora e `--check` do registry.md) |
| Gate RFC → ADR | Nenhum critério de `decision_gates.rfc_to_adr` se aplica |
| Aprovação | Owner (Michel Pessoa), 2026-11-17, sobre o texto desta SDD em `in_review` |
| Ajuste pós-aprovação | Owner aceitou em 2026-11-17, depois da rodada 1 do verify-sdd: `_framework/INDEX.md` na task 3, `central:_framework/INDEX.md` na task 4 e um teste de RF01 com regras sintéticas em ordem diferente da embutida; depois da rodada 2, pipe escapado no comando do A07 (só formatação) |
