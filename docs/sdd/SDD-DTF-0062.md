---
id: SDD-DTF-0062
type: SDD
title: "Núcleo canônico das renderizações traz a aprovação como dado e o executor, e o ciclo de status deixa de sugerir rejected → implemented"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0060]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: o texto gerado passa a carregar regras que já estão em workflow-rules.yaml (approval_policy e executor_contract, 2.4.0 a 2.6.0), sem regra nova; ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0056). Como muda o que AGENTS.md e os prompts dizem às IAs, o owner pode subir o sizing na review. Leia esta SDD inteira; ela nomeia os títulos, as colunas e os testes. Teste primeiro, visto falhar. Todo o texto novo sai dos dados do YAML, nunca de prosa fixa que repita a regra. Gerados só por render_prompts.py. A SDD-DTF-0061 também muda render_prompts.py, em outra função: se ela entrar antes, faça merge de main e regenere. O central espelha o script e regenera os próprios gerados, em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [render_prompts, core_facts, agents-md, prompts, aprovacao, executor, status]
---

# Núcleo canônico das renderizações traz a aprovação como dado e o executor, e o ciclo de status deixa de sugerir rejected → implemented

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`core_facts` (`_framework/scripts/render_prompts.py`) gera o "Núcleo
canônico". Esse bloco entra em `AGENTS.md`, `docs/especificacao.md`,
`prompts/universal.md`, `prompts/cursor/doc-framework.mdc` e
`prompts/copilot/copilot-instructions.md`, que são o que Codex, Cursor,
Copilot, Gemini e qualquer chat leem. Ele traz as leis, os tipos, o sizing,
o ciclo de status e o gate RFC → ADR. Não traz a aprovação como dado
(`approval_policy`, 2.5.0 e 2.6.0) nem o contrato do executor
(`executor_contract`, 2.4.0): nas cinco renderizações, `approval_policy`,
`approved_by` e `executor_contract` têm zero menções. Uma IA fora do
Claude Code não fica sabendo que a SPEC `medium` aprovada precisa de
`approved_by` humano preso ao hash. Além disso, a linha do ciclo de status
monta uma cadeia com os cinco primeiros estados (`draft` → `in_review` →
`approved` → `rejected` → `implemented`), o que sugere a transição
`rejected → implemented`, que `allowed_transitions` não tem.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: uma função geradora e os seus testes; o texto novo vem de chaves
que já existem. `workflow-rules.yaml` e `framework.version` não mudam.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | `core_facts` ganha a subseção `### Aprovação`, depois de "Ciclo de vida de status", com uma tabela `\| Tipos \| Sizing \| Quem aprova \|`, uma linha por item de `approval_policy.rules` (sizing ausente vira `todos`), a linha `Sem regra que case: {default_approver}.` e a frase com `approved_by`, `content_sha256` calculado por `approval_hash.py`, a lista de `approval_policy.hash_excluded_sections` e `review_approval.py` | Quando `core_facts` rodar com o YAML real, a saída deve ter `### Aprovação` e uma linha de tabela para cada regra de `approval_policy.rules`, com os tipos na ordem do YAML |
| RF02 | `core_facts` ganha a subseção `### Executor`, depois de `### Aprovação`, com `contract_version` e um item por entrada de `executor_contract.writes`, no texto do YAML | Quando `core_facts` rodar com o YAML real, a saída deve ter `### Executor`, `contract_version` e cada frase de `executor_contract.writes` |
| RF03 | O ciclo de status deixa de ser a cadeia dos cinco primeiros estados: passa a `Estados: ` seguido de todos os `status_lifecycle.states` entre crases, separados por vírgula; a linha "Transições válidas" e a do INC não mudam | Quando `core_facts` rodar, a saída não deve conter `` `rejected` → `implemented` `` e deve conter cada um dos sete estados |
| RF04 | O texto de RF01 a RF03 vem dos dados do YAML: com um YAML de teste em que `approval_policy.rules` tem uma regra a mais, a tabela ganha a linha | Quando o teste passar a `core_facts` um dicionário com uma regra extra, a saída deve ter uma linha a mais na tabela |
| RF05 | Testes num arquivo novo, `_framework/scripts/tests/test_render_prompts_core.py`, cobrem RF01 a RF04 | Quando o pytest do arquivo rodar, todos devem passar, e com a subseção de aprovação removida de `core_facts` pelo menos um deve falhar |
| RF06 | Os cinco gerados que usam `core_facts` são regenerados e `check_renderings.py` continua passando | Quando `render_prompts.py --check` e `check_renderings.py` rodarem, os dois devem sair com 0 |

Fora de escopo: a prosa fixa dos prompts (`prefix` de `build_universal`,
`build_cursor_mdc` e `build_copilot_instructions`); exigir os fatos novos em
`check_renderings.py` (SDD-DTF-0063 cuida de status e tipo inexistentes);
`QUICKSTART.md`, que não usa `core_facts`; as cópias de prompts da skill
(SDD-DTF-0061).

## Especificação técnica consolidada

- **Onde.** `_framework/scripts/render_prompts.py`, função `core_facts`.
- **Aprovação.** Depois do bloco do ciclo de status:
  `["", "### Aprovação", "", "| Tipos | Sizing | Quem aprova |", "|---|---|---|"]`,
  depois uma linha por regra:
  `f"| {', '.join(r['types'])} | {', '.join(r.get('sizing') or ['todos'])} | {r['approver']} |"`,
  depois `f"Sem regra que case: {policy['default_approver']}."` e uma frase
  que cita `approved_by`, `content_sha256`, `approval_hash.py`, as
  `hash_excluded_sections` entre crases e `review_approval.py`. Sem
  `approval_policy` no YAML, a subseção não é gerada.
- **Executor.** `["", "### Executor", "", f"`contract_version` {cv}. O que um executor pode escrever:", ""]`
  e um `- {frase}` por item de `executor_contract.writes`. Sem
  `executor_contract`, a subseção não é gerada.
- **Ciclo.** Trocar a linha
  `"`" + "` → `".join(lifecycle["states"][:5]) + "`"` por
  `"Estados: " + ", ".join(f"`{s}`" for s in lifecycle["states"]) + "."`.
- **Testes.** `test_render_prompts_core.py` importa `core_facts` e
  `load_rules` como os testes existentes do diretório.
- **Gerados.** `AGENTS.md`, `docs/especificacao.md`,
  `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`,
  `_framework/prompts/copilot/copilot-instructions.md`, a cópia do script na
  skill e os índices (`_framework/INDEX.md`, `_framework/rules/workflow-rules.map.md`
  se mudar) saem de `render_prompts.py`.
- **Espelho no central.** O script, a cópia da skill e o teste; depois
  `python3 _framework/scripts/render_prompts.py` no central regenera os
  gerados de lá.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar | RF01 a RF05 | `_framework/scripts/tests/test_render_prompts_core.py` | |
| 2 | Subseções de aprovação e executor e o ciclo de status | RF01 a RF04 | `_framework/scripts/render_prompts.py` | 1 |
| 3 | Regenerar gerados | RF06 | `AGENTS.md`, `docs/especificacao.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/prompts/copilot/copilot-instructions.md`, `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `_framework/INDEX.md`, `_framework/rules/workflow-rules.map.md` | 2 |
| 4 | Espelhar no central e regenerar lá, em branch e PR próprios | RF01 a RF06 | `central:_framework/scripts/render_prompts.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `central:_framework/scripts/tests/test_render_prompts_core.py` e os gerados do central | 3 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A07.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01 a RF05: testes novos | `python3 -m pytest _framework/scripts/tests/test_render_prompts_core.py -q` | ANTES da task 2: pelo menos 3 failed; DEPOIS: todos passam | automatizado |
| A02 | RF01: sensor | Em cópia descartável, remover de `core_facts` a subseção de aprovação; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF01 e RF02 nos gerados | `for f in AGENTS.md _framework/prompts/universal.md _framework/prompts/cursor/doc-framework.mdc _framework/prompts/copilot/copilot-instructions.md docs/especificacao.md; do for t in "### Aprovação" "### Executor" approval_hash.py review_approval.py contract_version; do grep -qF -e "$t" $f \|\| echo "falta $t em $f"; done; done` | Nenhum `falta` | automatizado |
| A04 | RF03 nos gerados | `grep -c '\`rejected\` → \`implemented\`' AGENTS.md _framework/prompts/universal.md docs/especificacao.md` | `0` nos três | automatizado |
| A05 | RF01 a RF03: cada linha nova bate com a chave do YAML (`approval_policy`, `executor_contract`, `status_lifecycle`) | Leitura lado a lado do diff de `AGENTS.md` e das chaves | Nenhuma linha sem chave correspondente ou que a contradiga | manual |
| A06 | RF06, suíte, lint e escopo | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 _framework/scripts/check_renderings.py; echo "exit=$?"; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0` três vezes; 0 failed; ruff e mypy sem erro; só os arquivos das tasks 1 a 3, esta SDD, o seu `validation-SDD-DTF-0062.md` e os gerados de `docs/sdd/` | automatizado |
| A07 | Central: espelho e gerados | No central: `cmp` do script, da cópia da skill e do teste contra o kit; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `grep -c "### Aprovação" AGENTS.md`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída; `exit=0`; `1`; `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0062-nucleo-aprovacao-executor`, já
  aberta com esta SDD. Comece por `git fetch origin main && git merge
  origin/main` e regenere os gerados se houver conflito. Commits com
  `Refs: SDD-DTF-0062`. Nunca em `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Sem prosa que repita a regra:** a tabela e os itens saem dos dados; a
  única frase fixa é a do RF01, que nomeia campos e scripts.
- **Não mudar** `workflow-rules.yaml`, os `prefix` dos prompts,
  `check_renderings.py`, `sync_copies` nem `QUICKSTART.md`.
- **Gerados só por script:** `render_prompts.py`; nunca editar `AGENTS.md`
  nem os prompts gerados à mão.
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
