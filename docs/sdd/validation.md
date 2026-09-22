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
