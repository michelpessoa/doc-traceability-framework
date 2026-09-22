# Verificação — SDD-DTF-0034

- **Veredito:** PASS
- **Diff verificado:** 419ff7bee9748c3992a0b0663ce91ac0de2c9645..d66430f (merge-base origin/main..HEAD, branch sdd/SDD-DTF-0034)
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 (RF01) | `grep -n "Os [0-9]\+ tipos" _framework/skills/doc-traceability-framework/SKILL.md` | sem saída (exit 1) | sem teste automatizado | Sim |
| 2 (RF02) | `python3 -m pytest _framework/tests/test_skill_md_consistency.py::test_status_lifecycle_matches_yaml -v` | `1 passed in 0.12s` | Quebrei a frase "Transições válidas" (removi `draft` de `in_review → approved, rejected, draft`); teste falhou com `AssertionError: SKILL.md diz que 'in_review' vai para {'approved', 'rejected'}, mas workflow-rules.yaml diz {'approved', 'rejected', 'draft'}`; restaurei via `git checkout --` e confirmei `1 passed` de novo | Sim |
| 3 (RF03) | `grep -inE "você mesma\|voce mesma" _framework/skills/doc-traceability-framework/SKILL.md` | sem saída (exit 1) | sem teste automatizado | Sim |
| 4 (RF04) | `grep -n "_framework/\(scripts\|references\|templates\|prompts\)/" _framework/skills/doc-traceability-framework/SKILL.md` | sem saída (exit 1) | sem teste automatizado | Sim |
| 5 (RF05) | `grep -n "framework_check.py --auto" _framework/skills/doc-traceability-framework/SKILL.md` | linha 239: `roda a auditoria de ponta a ponta sem exigir o log preparado à mão` | sem teste automatizado | Sim |
| 6 (RF06) | `grep -n "parallel_plan.py" _framework/skills/doc-traceability-framework/SKILL.md` | linha 105: `scripts/parallel_plan.py` | sem teste automatizado | Sim |
| 7 (RF07) | `grep -inE "guard_bash.sh\|pre-commit" _framework/skills/doc-traceability-framework/SKILL.md` | linha 181: `guard_bash.sh` | sem teste automatizado | Sim |
| 8 (RF08) | `grep -n "sdd-verifier" _framework/skills/doc-traceability-framework/SKILL.md` | linha 340: `sdd-verifier` | sem teste automatizado | Sim |
| 9 (RF09) | `grep -inE "repository_status\|greenfield" _framework/skills/doc-traceability-framework/SKILL.md` | linhas 48 e 53 | sem teste automatizado | Sim |
| 10 (RF10) | `wc -l < _framework/skills/doc-traceability-framework/SKILL.md` | `391` (< 392) | sem teste automatizado | Sim |
| 11 (paridade) | `find . -maxdepth 5 -iname "SKILL.md" -path "*doc-traceability-framework*" -not -path "*/worktrees/*" -not -path "*/node_modules/*"` | encontrei uma segunda entrada em `.claude/skills/doc-traceability-framework/SKILL.md`, mas é symlink para o mesmo arquivo (`readlink -f` resolve para `_framework/skills/doc-traceability-framework/SKILL.md`), confirmado com `diff` (sem saída, exit 0) — não é cópia divergente | sem teste automatizado | Sim, com nota (não há segunda cópia real local; paridade com `doc-traceability-central` fica fora do escopo desta SDD) |
| 12 (suíte) | `python3 -m pytest _framework/ -q` | `121 passed in 4.65s` | — | Sim |
| 13 (render_prompts) | `python3 _framework/scripts/render_prompts.py --check` | todos os itens `✅ ... em dia/sincronizado`, nenhuma divergência; confirmado por `git diff --name-only <merge-base>..HEAD` que `AGENTS.md`/`QUICKSTART.md`/`workflow-rules.yaml` não foram tocados | — | Sim |

Conformidade nas duas direções: todo requisito RF01-RF10 tem trecho
correspondente identificável no `SKILL.md` editado (linhas citadas
acima). O diff completo (`_framework/skills/doc-traceability-framework/SKILL.md`,
`_framework/tests/test_skill_md_consistency.py`, `docs/sdd/SDD-DTF-0034.md`,
`docs/sdd/registry.md`, `docs/sdd/registry.yaml`) não contém nenhum
arquivo fora do que a SDD declara como escopo (produto: SKILL.md + teste
novo; os demais são SDD/registry, esperados). `_framework/tests/test_skill_md_consistency.py`
lê a tabela esperada do próprio `workflow-rules.yaml` via
`framework_lib.allowed_transitions()`, sem hardcode — não modifica
`framework_lib.py` (arquivo não tocado no diff).

## Descompassos encontrados

Nenhum. Nota lateral sem impacto: existe um symlink
`.claude/skills/doc-traceability-framework/SKILL.md` apontando para o
arquivo editado — não é uma segunda cópia divergente, apenas uma rota de
acesso adicional ao mesmo arquivo. A nota de escopo da própria SDD
(critério 11) já previa essa possibilidade e cobre o caso.

## Lições

Nenhuma — implementação bateu com a SDD em todos os 13 critérios na
primeira rodada de verificação independente.
