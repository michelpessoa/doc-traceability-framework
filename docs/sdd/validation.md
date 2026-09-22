# Verificação — SDD-DTF-0040

- **Veredito:** PASS
- **Diff verificado:** `e620526d88af8be29f507c6cb1b208d14c970358..HEAD` (`git merge-base HEAD origin/main`)
- **Verificador independente:** sim (subagente dedicado, sem histórico da sessão implementadora)

## Passo 0 — Fidelidade à origem

`source_docs` está vazio (sizing `small`, achado de auditoria conforme
`consumption_instructions` — sem SPEC/RFC/ADR de origem). `check_source_docs.py`
não se aplica; não-retroativo, conforme o procedimento. Nenhum achado bloqueante.

## Critérios de aceite — evidência (rodada 1)

| # | Critério (RF-ID) | Comando rodado | Saída real | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF01 — não afirma mais "nenhum é imposto por CI" | `grep -n "nenhum é imposto por CI" docs/guias/guia-tecnico.md` | sem saída, exit 1 | Reverti a frase (seção 7) para a versão antiga; grep passou a casar (exit 0). Restaurado, grep voltou a exit 1. Discrimina. | Sim |
| 2 | RF01 — menciona `ci_gate_verify_sdd.py` | `grep -n "ci_gate_verify_sdd.py" docs/guias/guia-tecnico.md` | linhas 46, 170, 295 (3 ocorrências) | sem teste automatizado adicional (coberto pelo sensor do #1, mesma edição) | Sim |
| 3 | RF02 — 5 scripts citados | `grep -cE "check_source_docs\.py\|ci_gate_verify_sdd\.py\|lessons_check\.py\|selftest\.py\|parallel_plan\.py" docs/guias/guia-tecnico.md` | `10` (≥5) | sem teste automatizado | Sim |
| 4 | RF03 — path `guides/` corrigido | `grep -n "guides/" docs/guias/guia-tecnico.md` | sem saída, exit 1 | Reverti `docs/guias/` → `guides/` na árvore; grep passou a casar (exit 0). Restaurado, exit 1 de novo. Discrimina. | Sim |
| 5 | RF03 — `gate-ci-verify-sdd.md` na lista de guias | `grep -n "gate-ci-verify-sdd.md" docs/guias/guia-tecnico.md` | linha 51 | mesma edição do sensor #4 | Sim |
| 6 | RF04 — passo 0 mencionado | `grep -inE "fidelidade . origem\|passo 0" docs/guias/guia-tecnico.md` | 3 ocorrências (linhas 289, 336, 343) | sem teste automatizado | Sim |
| 7 | RF04 — autoridade de despacho | `grep -in "autoridade de despacho" docs/guias/guia-tecnico.md` | linha 357 | sem teste automatizado | Sim |
| 8 | RF04 — teto de 3 rodadas | `grep -in "3 rodadas" docs/guias/guia-tecnico.md` | linha 360 | sem teste automatizado | Sim |
| 9 | RF05 — `file:line` mencionado | `grep -in "file:line" docs/guias/guia-tecnico.md` | linha 349 | sem teste automatizado | Sim |
| 10 | RF06 — sweep no checklist | `grep -in "sweep" docs/guias/guia-tecnico.md` | linha 198 | Reverti "Sweep de requisitos transversais" → "Requisitos transversais"; grep passou a falhar (exit 1, sem saída). Restaurado (diff idêntico ao backup), grep voltou a casar. Discrimina. | Sim |
| 11 | RF07 — `lessons_check.py` / `Chave de recorrência` | `grep -cE "lessons_check\.py\|Chave de recorrência" docs/guias/guia-tecnico.md` | `5` (≥2) | sem teste automatizado | Sim |
| 12 | Markdown balanceado | `python3 -c "t=open('docs/guias/guia-tecnico.md').read(); assert t.count('\`\`\`')%2==0"` | sem `AssertionError`, exit 0 | n/a (checagem estrutural, não requisito de conteúdo) | Sim |
| 13 | Suíte completa | `python3 -m pytest _framework/ -q` | `180 passed in 26.88s` | n/a — suíte pré-existente do framework | Sim |
| 14 | `render_prompts.py --check` | `python3 _framework/scripts/render_prompts.py --check` | todos os arquivos "sincronizado", exit 0 | n/a | Sim |

Perfil usado em todos: `manual` (grep direto pela sessão verificadora,
sem suíte de teste automatizada dedicada ao guia — coerente com o
"Perfil esperado" implícito da SDD, que já usa grep como comando de
verificação, não pytest).

## Escopo (nada a mais, nada a menos)

- `git diff --name-only e620526d88af8be29f507c6cb1b208d14c970358..HEAD`:
  `docs/guias/guia-tecnico.md`, `docs/sdd/SDD-DTF-0040.md`,
  `docs/sdd/registry.yaml` — exatamente os 3 arquivos esperados. Nenhum
  script, `workflow-rules.yaml` ou outro guia tocado.
- Todo trecho do diff de `guia-tecnico.md` mapeia para RF01-RF07 (seções
  2, 7, 9, 9.1, 9.2) — sem adição fora do escopo declarado.
- `registry.yaml`: entrada nova para SDD-DTF-0040 com `status: approved`,
  campos batendo com o front-matter da SDD.
- Working tree limpa após os testes de sensor (confirmado com `diff` byte
  a byte contra a cópia de backup antes de cada reversão).

## Descompassos encontrados

Nenhum. Requisito↔conteúdo bate nas duas direções, nenhum arquivo fora
de escopo, nenhum critério de aceite falhou, sensor de discriminação
confirmado em 3 dos 7 critérios de grep (RF01, RF03, RF06) — acima do
mínimo de 2 pedido.

Observação não bloqueante: a réplica em
`doc-traceability-central/docs/guias/guia-tecnico.md` (mencionada em
`consumption_instructions` como obrigatória) está fora do escopo desta
SDD e desta verificação — cobre só o repositório do kit, como a própria
SDD declara.

## Lições

Nenhuma — verificação sem descompasso não gera lição nova.

---

# Verificação — SDD-DTF-0041

- **Veredito:** PASS
- **Diff verificado:** `af47a05b0048cdc84ff03035f50338b5a1ece351..HEAD` (`git merge-base HEAD origin/main`)
- **Verificador independente:** sim (subagente dedicado, sem histórico da sessão implementadora)

## Passo 0 — Fidelidade à origem

`source_docs` está vazio (sizing `small`, achado de auditoria conforme
`consumption_instructions` — sem SPEC/RFC/ADR de origem, mesma rodada de
auditoria que originou SDD-DTF-0040). `check_source_docs.py` não se
aplica; não-retroativo, conforme o procedimento. Nenhum achado
bloqueante.

## Critérios de aceite — evidência (rodada 1)

| # | Critério (RF-ID) | Comando rodado | Saída real | Sensor | Assertion (file:line) | Perfil usado | Passou? |
|---|---|---|---|---|---|---|---|
| 1 | RF01 — enum de `type` inclui SPEC | `grep -n "enum\[STRAT, RFC, ADR, SPEC, PRD, TS, SDD, BASE, INC, PM\]" _framework/rules/workflow-rules.yaml` | `663:    type: "enum[STRAT, RFC, ADR, SPEC, PRD, TS, SDD, BASE, INC, PM] — obrigatório"` | Reverti a linha 663 para o enum antigo (sem SPEC); grep passou a exit 1 (sem saída). Restaurado via cópia de backup (`cp` prévio), grep voltou a casar linha 663. Discrimina. | `_framework/rules/workflow-rules.yaml:663` | manual (grep) | Sim |
| 2 | RF02 — entrada `SPEC:` em `type_specific_fields` com os 3 campos | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); f=d['frontmatter_schema']['type_specific_fields']['SPEC']; assert set(f)=={'parent_rfc','parent_adr','sizing'}"` | sem erro, exit 0 | Removi o bloco `SPEC:` inteiro de `type_specific_fields`; script passou a levantar `KeyError: 'SPEC'` (exit 1). Restaurado via cópia de backup, script voltou a passar sem erro. Discrimina. | `_framework/rules/workflow-rules.yaml:691-694` | automatizado | Sim |
| 3 | RF03 — descrição de `source_docs` cita SPEC | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); assert 'SPEC' in d['frontmatter_schema']['type_specific_fields']['SDD']['source_docs']"` | sem erro, exit 0 | sem teste automatizado adicional (coberto pela mesma edição verificada no #1/#2; texto de `source_docs` já cita "SPEC(s) e ADR(s)" na linha 696-698) | `_framework/rules/workflow-rules.yaml:696` | automatizado | Sim |
| 4 | YAML continua parseável | `python3 -c "import yaml; yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))"` | sem erro, exit 0 | n/a — checagem estrutural, não requisito de conteúdo | n/a | automatizado | Sim |
| 5 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | `180 passed in 27.00s` | n/a — suíte pré-existente do framework, não escrita para esta SDD | n/a | automatizado | Sim |
| 6 | `render_prompts.py --check` | `python3 _framework/scripts/render_prompts.py --check` | todos os arquivos "em dia"/"sincronizado" (incl. `references/workflow-rules.yaml: sincronizado`), exit 0 | n/a | n/a | automatizado | Sim |
| 7 | `framework_check.py --auto` | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` (4 projetos: docs/sdd, EXEMPLO, LEGADO, project-repo-checkout), exit 0 | n/a | n/a | automatizado | Sim |

Sensor de discriminação aplicado a 2 critérios (RF01 e RF02, acima do
mínimo de 1 pedido pelo despacho): em ambos os casos, reverter a mudança
correspondente fez o critério falhar (exit 1 / `KeyError`), e restaurar
o arquivo (via `cp` de uma cópia de backup, nunca `git stash`) fez o
critério voltar a passar. Working tree confirmada limpa (`git status` /
`git diff --stat` vazios) após cada restauração.

## Escopo (nada a mais, nada a menos)

- `git diff --stat af47a05b0048cdc84ff03035f50338b5a1ece351..HEAD`:
  `_framework/rules/workflow-rules.yaml`,
  `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`,
  `docs/sdd/SDD-DTF-0041.md`, `docs/sdd/registry.yaml` — exatamente os 4
  arquivos esperados (fonte canônica + cópia bundlada regenerada por
  `render_prompts.py`, nunca editada à mão + SDD + registry). Nenhum
  script, `document_types`, `legacy_document_types`, `framework_lib.py`,
  `validate_doc.py` ou `framework.version` tocado.
- A cópia bundlada
  (`_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`)
  é byte-a-byte idêntica ao diff da fonte canônica (`git diff` mostra o
  mesmo hunk nos dois arquivos) — consistente com "regenerada por
  `render_prompts.py`, não editada à mão".
- Todo trecho do diff mapeia para RF01-RF03: enum de `type` (RF01), bloco
  `SPEC:` em `type_specific_fields` (RF02), descrição de
  `SDD.source_docs` (RF03) — sem adição fora do escopo declarado.
- `registry.yaml`: entrada nova para SDD-DTF-0041 com `status: approved`,
  campos batendo com o front-matter da SDD.
- Working tree limpa após os testes de sensor (confirmado com `git
  status`/`git diff --stat` vazios antes e depois de cada rodada).

## Descompassos encontrados

Nenhum. Requisito↔conteúdo bate nas duas direções (RF01-RF03 todos com
trecho correspondente e nenhum trecho fora de RF01-RF03), nenhum arquivo
fora de escopo, todos os 7 critérios de aceite passaram com saída real
desta sessão, sensor de discriminação confirmado em 2 dos critérios com
teste automatizado real (RF01, RF02).

## Lições

Nenhuma — verificação sem descompasso não gera lição nova.
