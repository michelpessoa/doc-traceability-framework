---
id: SDD-DTF-0061
type: SDD
title: "render_prompts.py sincroniza e confere as cópias dos prompts dentro da skill"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0060]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção de tooling achada na verificação da SDD-DTF-0060 (rodada 1, descompasso bloqueante, e rodada 2, item 4); ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0056). Leia esta SDD inteira; ela nomeia a constante, as mensagens e os testes. Teste primeiro, visto falhar; depois o código. A cópia do script na skill e o _framework/INDEX.md são gerados por render_prompts.py, nunca à mão. A SDD-DTF-0062 também muda render_prompts.py, em outra função: se ela entrar antes, faça merge de main e regenere. O central espelha em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [render_prompts, skill, prompts, tooling, sync]
---

# render_prompts.py sincroniza e confere as cópias dos prompts dentro da skill

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`_framework/rules/kit-index.yaml` declara
`skills/doc-traceability-framework/prompts/*` como "Cópia gerada de
prompts/{name} dentro da skill" e manda regenerar com `render_prompts.py`.
Só que `sync_copies` (`_framework/scripts/render_prompts.py`) copia scripts,
o YAML e os templates, e não copia os prompts. Por isso
`render_prompts.py --check` não vê quando
`skills/doc-traceability-framework/prompts/onboarding-bootstrap.md` ou
`framework-audit.md` ficam para trás do canônico. Isso aconteceu na
SDD-DTF-0060, rodada 1: a skill instalada lia os prompts antigos, porque
`references/onboarding.md` e `references/audit.md` mandam ler a cópia da
skill. A SDD-DTF-0060 resolveu à mão (RF10, `cp`). Esta SDD faz o gerador
cobrir as cópias, para que a divergência volte a reprovar o `--check`.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: uma função de um script e o seu teste, no mesmo padrão já usado
para templates. `workflow-rules.yaml`, `kit-index.yaml` e
`framework.version` não mudam (`lessons_policy`: é falha de execução, não
desenho).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | `render_prompts.py` ganha a constante `BUNDLED_PROMPTS = ("framework-audit.md", "onboarding-bootstrap.md")`, os prompts que a skill embute, e `sync_copies` sincroniza cada `prompts/{nome}` para `skills/doc-traceability-framework/prompts/{nome}` por `_sync_file` | Quando o canônico `prompts/onboarding-bootstrap.md` for diferente da cópia da skill e `render_prompts.py` rodar sem `--check`, a cópia deve ficar idêntica ao canônico |
| RF02 | Com `--check`, a cópia divergente ou ausente reprova com a mensagem que `_sync_file` já usa (`❌ {dest}: divergente de {src}.`) e o script sai com código 1 | Quando a cópia da skill divergir do canônico e `render_prompts.py --check` rodar, a saída deve conter `divergente de` e o código de saída deve ser 1 |
| RF03 | Arquivo `*.md` em `skills/doc-traceability-framework/prompts/` cujo nome não está em `BUNDLED_PROMPTS` reprova nos dois modos, com `❌ {arquivo}: órfão (fora de BUNDLED_PROMPTS) — remova à mão.`, e nunca é apagado pelo script | Quando existir `skills/doc-traceability-framework/prompts/extra.md`, `render_prompts.py` com e sem `--check` deve imprimir `órfão` e sair com 1, e o arquivo deve continuar existindo |
| RF04 | A docstring de `sync_copies` passa a citar os prompts embutidos ao lado de scripts, YAML e templates | Quando a docstring for lida, ela deve conter `BUNDLED_PROMPTS` |
| RF05 | Testes em `_framework/scripts/tests/test_render_prompts_sync.py` cobrem RF01 a RF03 em repositório temporário e conferem que o kit real está em dia | Quando o pytest do arquivo rodar, os testes novos devem passar, e com a sincronização dos prompts removida de `sync_copies` pelo menos um deve falhar |
| RF06 | `_framework/scripts/tests/mutations.yaml` ganha uma mutação que remove a sincronização dos prompts, morta por `test_render_prompts_sync.py`, para `selftest.py` cobrir o RF01 | Quando `python3 _framework/scripts/selftest.py` rodar, a mutação nova deve morrer, e a contagem de mutações deve subir em uma unidade |

Fora de escopo: copiar para a skill outros prompts (`universal.md`, Cursor,
Copilot); mudar `kit-index.yaml`, `references/onboarding.md` ou
`references/audit.md`; o núcleo canônico das renderizações (SDD-DTF-0062);
`check_renderings.py` (SDD-DTF-0063).

## Especificação técnica consolidada

- **Onde.** `_framework/scripts/render_prompts.py`, função `sync_copies`,
  e a constante nova `BUNDLED_PROMPTS` no topo do módulo.
- **Sincronização.** Depois do laço dos templates, para cada nome de
  `BUNDLED_PROMPTS`: `ok &= _sync_file(root / "prompts" / nome, skill /
  "prompts" / nome, check)`.
- **Órfãos.** Para cada `*.md` direto em `skill / "prompts"` (não
  recursivo) cujo `name` não está em `BUNDLED_PROMPTS`: imprimir a
  mensagem do RF03 e `ok = False`. Não apagar.
- **Testes.** Em `test_render_prompts_sync.py`, no padrão dos testes de
  template existentes (`tmp_path` com a árvore mínima): gera a cópia
  (RF01); `--check` com cópia divergente e com cópia ausente (RF02); órfão
  nos dois modos, com o arquivo preservado (RF03); o kit real com
  `sync_copies(root, check=True)` verdadeiro.
- **Gerados.** A cópia `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`
  e `_framework/INDEX.md` saem de `render_prompts.py`.
- **Espelho no central.** O script, a cópia da skill, o teste,
  `mutations.yaml` e `_framework/INDEX.md`, em branch e PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar | RF01 a RF03, RF05 | `_framework/scripts/tests/test_render_prompts_sync.py` | |
| 2 | Constante, sincronização, órfãos e docstring | RF01 a RF04 | `_framework/scripts/render_prompts.py` | 1 |
| 3 | Mutação do selftest | RF06 | `_framework/scripts/tests/mutations.yaml` | 2 |
| 4 | Regenerar a cópia da skill e o índice | RF01 a RF04 | `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `_framework/INDEX.md` | 2 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF06 | `central:_framework/scripts/render_prompts.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `central:_framework/scripts/tests/test_render_prompts_sync.py`, `central:_framework/scripts/tests/mutations.yaml`, `central:_framework/INDEX.md` | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A07.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01 a RF03, RF05: testes novos | `python3 -m pytest _framework/scripts/tests/test_render_prompts_sync.py -q` | ANTES da task 2: pelo menos 3 failed; DEPOIS: todos passam | automatizado |
| A02 | RF01: sensor da sincronização | Em cópia descartável, remover de `sync_copies` o laço de `BUNDLED_PROMPTS`; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF02: o kit real reprova divergência | Em cópia descartável do kit, acrescentar uma linha a `_framework/skills/doc-traceability-framework/prompts/framework-audit.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `divergente de` na saída e `exit=1` | automatizado |
| A04 | RF04: docstring | `grep -c "BUNDLED_PROMPTS" _framework/scripts/render_prompts.py` | ≥ 3 (constante, uso e docstring) | automatizado |
| A05 | RF06: selftest | `python3 _framework/scripts/selftest.py; echo "exit=$?"` | `N mutação(ões): todos os mutantes morreram.`, com N uma unidade acima do de `origin/main` antes da branch, e `exit=0` | automatizado |
| A06 | Gerados, suíte, lint e escopo | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/render_prompts.py _framework/skills/doc-traceability-framework/scripts/render_prompts.py; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0`; `cmp` sem saída; 0 failed; ruff e mypy sem erro; `exit=0`; só os arquivos das tasks 1 a 4, esta SDD, o seu `validation-SDD-DTF-0061.md` e os gerados de `docs/sdd/` | automatizado |
| A07 | Central: espelho idêntico | No central: `cmp` dos arquivos da task 5 contra o kit; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` nos dois | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0061-sync-prompts-da-skill`, já aberta
  com esta SDD. Comece por `git fetch origin main && git merge origin/main`
  e regenere os gerados se houver conflito em `docs/sdd/`. Commits com
  `Refs: SDD-DTF-0061`. Nunca em `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Não mudar** `workflow-rules.yaml`, `kit-index.yaml`, os prompts, os
  `references/` da skill, `check_renderings.py` nem `core_facts`.
- **Gerados só por script:** `render_prompts.py` para a cópia da skill e os
  índices; `generate_registry_md.py` para `registry.md`.
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
