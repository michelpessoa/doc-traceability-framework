---
id: SDD-DTF-0065
type: SDD
title: "Achados não bloqueantes das SDD-DTF-0062 a 0064: checks da policy no núcleo, testes que discriminam a chamada da checagem 4 e os tipos legados, e negativo que discrimina"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0062, SDD-DTF-0063, SDD-DTF-0064]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: três achados não bloqueantes das verificações independentes (validation-SDD-DTF-0062.md achado 1; validation-SDD-DTF-0063.md achados 2 e 3; validation-SDD-DTF-0064.md achado 2); ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0056). Leia esta SDD inteira; ela nomeia a linha nova do núcleo, os testes e as mutações. Teste primeiro, visto falhar; depois o código. As cópias dos scripts na skill, AGENTS.md, os prompts gerados, docs/especificacao.md e os índices saem de render_prompts.py, nunca à mão. O central espelha em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [render_prompts, core_facts, check_renderings, testes, mutacoes, tooling]
---

# Achados não bloqueantes das SDD-DTF-0062 a 0064: checks da policy no núcleo, testes que discriminam a chamada da checagem 4 e os tipos legados, e negativo que discrimina

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

As verificações independentes das SDD-DTF-0062, 0063 e 0064 deram PASS,
mas registraram achados que não bloqueavam e ficaram para depois:

1. **Checks da policy fora do núcleo** (`validation-SDD-DTF-0062.md`,
   achado 1). A tabela `### Aprovação` que `core_facts`
   (`_framework/scripts/render_prompts.py`) gera mostra `SDD | todos |
   policy`, mas não a lista `checks` da regra. Quem lê `AGENTS.md` ou um
   prompt gerado não fica sabendo o que a `policy` exige antes de aprovar
   uma SDD.
2. **A chamada da checagem 4 sem teste** (`validation-SDD-DTF-0063.md`,
   achado 2). Trocar por `pass` a linha que chama `check_unknown_names` em
   `main` (`_framework/scripts/check_renderings.py`) deixa a suíte
   inteira verde. Só os sensores A02 e A03 da SDD-DTF-0063, feitos à mão,
   provam essa ligação.
3. **Tipos legados sem teste** (`validation-SDD-DTF-0063.md`, achado 3). A
   união com `legacy_document_types` que `main` monta em `known_types` não
   é discriminada. Sem ela, os testes continuam passando, e um
   `PRD-EVM-0001` numa renderização passaria a reprovar.
4. **Negativo que não discrimina** (`validation-SDD-DTF-0064.md`, achado
   2). Em `test_sdd0064_negativo_sequencia_que_nao_e_id_nao_acusa`, o caso
   `ADR-EVM-Xy` não discrimina. Sem o lookahead, ele casa `ADR`, que é tipo
   conhecido, e não gera falha. `XYZ-EVM-Xy` discriminaria.

Esta SDD fecha os quatro: uma linha nova no núcleo, testes que rodam o
`main` do script numa cópia do kit, a troca de um caso de teste e as
mutações que os seguram no selftest.

## Emendas

- **2026-11-25, especificação do RF02 e do RF03.** A implementação parou
  antes da task 1: o `main` de `check_renderings.py` também confere os
  artefatos de `MECHANIZED_ARTIFACTS` em `../.claude/`
  (`settings.json`, `agents/sdd-verifier.md`,
  `commands/framework-check.md`). Uma cópia só de `_framework/` e
  `AGENTS.md` sai com 1 sem nenhuma alteração, o que impede o RF03
  (espera 0) e tira do RF02 o valor do código de saída. Além disso, no
  `SKILL.md` a cadeia de status fica inteira dentro de uma única crase
  (`` `draft → in_review → …` ``), então não existe `` `in_review` `` entre
  crases para trocar. O owner escolheu, na conversa de 2026-11-25, emendar
  esta SDD: o helper copia também `.claude/`, e a troca do RF02 passa a ser
  a da primeira ocorrência de `→ in_review →` por `→ obsolete →`, como no
  sensor A02 da SDD-DTF-0063. A emenda não muda os RF01 a RF06 nem os
  critérios. O status segue `approved`, porque `status_lifecycle` não tem
  `approved → in_review`; a aprovação da emenda é uma review "Aprovado" do
  owner no commit dela, na PR #161.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: uma linha a mais num texto gerado a partir de chave que já existe
(`approval_policy.rules[].checks`), testes e mutações.
`workflow-rules.yaml`, `kit-index.yaml` e `framework.version` não mudam
(`lessons_policy`: é falha de execução, não desenho). As SDD-DTF-0062, 0063
e 0064 estão `implemented` e não são editadas.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Em `core_facts`, depois da tabela de `### Aprovação`, uma linha em branco e, para cada regra de `approval_policy.rules` com `checks` não vazio, na ordem do YAML, o item `- Checks de {tipos} ({approver}): {checks}.`, com `{tipos}` separados por `, ` e cada check entre crases, separados por `, `. A tabela, a linha `Sem regra que case` e a frase de `approved_by` não mudam. Regra sem `checks` não ganha item | Quando `core_facts` rodar com o YAML real, a saída deve conter ``- Checks de SDD (policy): `validate_doc.py`, `registry_tools.py validate`, `check_source_docs.py (com source_docs)`, `verify-sdd passo 0 (com source_docs)`.`` |
| RF02 | Testes em `_framework/scripts/tests/test_check_renderings_unknown.py` rodam o `main` de `check_renderings.py` como subprocesso numa cópia de `_framework/` e de `AGENTS.md` em `tmp_path`, com um status inexistente acrescentado à cadeia de status do `SKILL.md` da cópia | Quando o teste rodar, o script da cópia deve sair com 1 e imprimir `cita o status inexistente`; e, com a chamada de `check_unknown_names` em `main` trocada por `pass`, o teste deve falhar |
| RF03 | Um teste no mesmo arquivo, na mesma cópia, acrescenta `PRD-EVM-0001` e `TS-EVM-0001` ao `SKILL.md` da cópia | Quando o teste rodar, o script da cópia deve sair com 0; e, com `known_types` reduzido a `set(types)` em `main`, o teste deve falhar |
| RF04 | Em `test_sdd0064_negativo_sequencia_que_nao_e_id_nao_acusa`, o caso `ADR-EVM-Xy` vira `XYZ-EVM-Xy`; o resto do teste não muda | Quando o pytest do arquivo rodar com o `(?!\w)` final de `ID_PREFIX` removido, esse teste deve falhar |
| RF05 | Testes em `_framework/scripts/tests/test_render_prompts_core.py` cobrem o RF01: o item da regra SDD com o YAML real, e uma regra sem `checks` sem item. Os testes que já existem não mudam | Quando o pytest do arquivo rodar, todos devem passar, e com o laço do RF01 removido pelo menos um deve falhar |
| RF06 | `_framework/scripts/tests/mutations.yaml` ganha três mutações: a chamada de `check_unknown_names` em `main` vira `pass` e `known_types` vira `set(types)`, as duas mortas por `test_check_renderings_unknown.py`; e o laço do RF01 desligado, morto por `test_render_prompts_core.py` | Quando `python3 _framework/scripts/selftest.py` rodar, as três mutações novas devem morrer, e a contagem de mutações deve subir em três unidades |

Fora de escopo: mudar a tabela de `### Aprovação` ou a lista `checks` no
YAML; outras checagens de `check_renderings.py`; a redação dos critérios
das SDDs anteriores (por exemplo, "gerados de `docs/sdd/`" no A06, que
inclui o `registry.yaml`, que não é gerado); `STATUS_CHAIN`,
`STATUS_DECLARED` e `ID_PREFIX`.

## Especificação técnica consolidada

- **RF01, onde.** `_framework/scripts/render_prompts.py`, função
  `core_facts`, bloco de `approval_policy`, logo depois do laço que monta
  as linhas da tabela e antes de `Sem regra que case`. Um laço sobre
  `policy.get("rules")` que só emite item para regra com `r.get("checks")`
  verdadeiro, depois de uma única linha em branco, e só se houver ao
  menos uma regra com `checks`.
- **RF02 e RF03, a cópia.** Um helper do teste copia
  `_framework/` (sem `__pycache__`), `.claude/` e `AGENTS.md` da raiz do
  kit para `tmp_path` com `shutil.copytree` (e `shutil.copy2` para o
  `AGENTS.md`), mantendo a mesma estrutura (emenda de 2026-11-25). O
  `.claude/` entra porque o `main` confere os artefatos de
  `MECHANIZED_ARTIFACTS` nele. A estrutura igual serve para que
  `find_rules_file` ache o `workflow-rules.yaml` da cópia e `RENDERINGS`
  (`../AGENTS.md`) resolva. O teste edita só
  `tmp_path/_framework/skills/doc-traceability-framework/SKILL.md` e roda
  `tmp_path/_framework/scripts/check_renderings.py` com `sys.executable`,
  `cwd=tmp_path`.
- **RF02, a cadeia.** Trocar, na cópia do `SKILL.md`, a primeira
  ocorrência de `→ in_review →` por `→ obsolete →`, como no sensor A02 da
  SDD-DTF-0063 (emenda de 2026-11-25); se a renderização não tiver essa
  ocorrência, acrescentar ao fim a linha
  `` `draft` → `obsolete` → `approved` ``.
- **RF04.** Só o texto do caso muda: `ADR-EVM-Xy` → `XYZ-EVM-Xy`.
- **RF06, mutações.** No formato das entradas existentes, cada `find`
  aparecendo uma única vez no validador:
  - `check_renderings.py`, `find` igual à linha
    `problems += check_unknown_names(rel, raw, known_statuses, known_types)`,
    `replace` `pass`, com a mesma indentação;
  - `check_renderings.py`, `find` igual a
    `known_types = set(types) | set((rules.get("legacy_document_types") or {}).keys())`,
    `replace` `known_types = set(types)`;
  - `render_prompts.py`, `find` um trecho do laço do RF01 que só exista
    nele, `replace` que o desligue sem quebrar a sintaxe.
- **Gerados.** `AGENTS.md`, `docs/especificacao.md`,
  `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`,
  `_framework/prompts/copilot/copilot-instructions.md`, as cópias dos dois
  scripts na skill e `_framework/INDEX.md` saem de `render_prompts.py`.
- **Espelho no central.** Os dois scripts, as cópias deles na skill, os
  dois arquivos de teste, `mutations.yaml` e os gerados do central, em
  branch e PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos e o caso trocado, vistos falhar | RF02 a RF05 | `_framework/scripts/tests/test_check_renderings_unknown.py`, `_framework/scripts/tests/test_render_prompts_core.py` | |
| 2 | Item de checks no núcleo | RF01 | `_framework/scripts/render_prompts.py` | 1 |
| 3 | Mutações do selftest | RF06 | `_framework/scripts/tests/mutations.yaml` | 2 |
| 4 | Regenerar gerados | RF01 | `AGENTS.md`, `docs/especificacao.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/prompts/copilot/copilot-instructions.md`, `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `_framework/skills/doc-traceability-framework/scripts/check_renderings.py`, `_framework/INDEX.md` | 2 |
| 5 | Espelhar no central e regenerar lá, em branch e PR próprios | RF01 a RF06 | `central:_framework/scripts/render_prompts.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `central:_framework/scripts/tests/test_check_renderings_unknown.py`, `central:_framework/scripts/tests/test_render_prompts_core.py`, `central:_framework/scripts/tests/mutations.yaml` e os gerados do central | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A08.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF02 a RF05: testes | `python3 -m pytest _framework/scripts/tests/test_check_renderings_unknown.py _framework/scripts/tests/test_render_prompts_core.py -q` | ANTES da task 2: pelo menos 1 failed (o do RF01); DEPOIS: todos passam | automatizado |
| A02 | RF02, RF03: sensores no `main` | Em cópia descartável, aplicar uma de cada vez as duas mutações de `check_renderings.py` do RF06; rodar o pytest de `test_check_renderings_unknown.py`; restaurar | Com cada mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF04: o negativo discrimina | Em cópia descartável, remover o `(?!\w)` final de `ID_PREFIX`; rodar o pytest de `test_check_renderings_unknown.py`; restaurar | Com a mutação: `test_sdd0064_negativo_sequencia_que_nao_e_id_nao_acusa` falha; restaurado: 0 failed | automatizado |
| A04 | RF01 nos gerados | `for f in AGENTS.md _framework/prompts/universal.md _framework/prompts/cursor/doc-framework.mdc _framework/prompts/copilot/copilot-instructions.md docs/especificacao.md; do grep -qF -e '- Checks de SDD (policy): `validate_doc.py`' $f \|\| echo "falta em $f"; done` | Nenhum `falta` | automatizado |
| A05 | RF01: o item bate com o YAML | Leitura lado a lado do diff de `AGENTS.md` e de `approval_policy.rules[].checks` em `workflow-rules.yaml` | Um item por regra com `checks`, com os checks na ordem do YAML, e nenhum item para regra sem `checks` | manual |
| A06 | RF06: selftest | `python3 _framework/scripts/selftest.py; echo "exit=$?"` | `N mutação(ões): todos os mutantes morreram.`, com N três unidades acima do da base da branch, e `exit=0` | automatizado |
| A07 | Gerados, suíte, lint e escopo | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 _framework/scripts/check_renderings.py; echo "exit=$?"; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0` três vezes; 0 failed; ruff e mypy sem erro; só os arquivos das tasks 1 a 4, esta SDD, o seu `validation-SDD-DTF-0065.md`, `docs/sdd/registry.yaml` e os gerados de `docs/sdd/` | automatizado |
| A08 | Central: espelho e gerados | No central: `cmp` dos arquivos da task 5 contra o kit; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `grep -c "Checks de SDD (policy)" AGENTS.md`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída; `exit=0`; `1`; `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0065-achados-0062-0063-0064`, aberta
  a partir de `main`. Comece por `git fetch origin main && git merge
  origin/main` e regenere os gerados de `docs/sdd/` se houver conflito.
  Commits com `Refs: SDD-DTF-0065`. Nunca em `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída. Os
  testes do RF02 e do RF03 já passam antes da task 2, porque o código que
  eles seguram já existe; a falha deles se prova pelos sensores do A02.
- **Não mudar** a tabela nem as outras linhas de `### Aprovação`, os
  testes existentes além do caso do RF04, `ID_PREFIX`, `STATUS_CHAIN`,
  `STATUS_DECLARED`, `check_unknown_names`, `workflow-rules.yaml`,
  `kit-index.yaml` nem as SDD-DTF-0062 a 0064.
- **Gerados só por script:** `render_prompts.py` para as cópias da skill,
  as renderizações e os índices; `generate_registry_md.py` para
  `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF06) tem código ou teste
      correspondente.
- [ ] Todo arquivo tocado aparece nas tasks ou nas instruções.
- [ ] Nenhuma abstração, config ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** {sim | não — mesma sessão que implementou}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
