# Verificação — SDD-DTF-0006

- **Veredito:** PASS
- **Diff verificado:** `dc9867e~1..dc9867e` (kit, `doc-traceability-framework`); mirror `fc97fd3~1..fc97fd3` (central, `doc-traceability-central`)
- **Verificador independente:** sim (subagente separado, sem leitura do histórico da sessão implementadora — apenas SDD, diff e árvore de arquivos)

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 — RF04, 3 procedimentos existem | `ls _framework/procedures/{handover,pickup,verify-sdd}.md` (kit e central) | 3 arquivos listados nos dois repos | estático, sem sensor necessário | Sim |
| 2 — RF04, sem front-matter | `head -1 _framework/procedures/handover.md \| grep -c '^---$'` (kit e central) | `0` nos dois | estático — SDD dispensa sensor | Sim |
| 3 — RF04, template preservado | `diff <(git show <base>:_framework/skills/handover/SKILL.md \| sed -n '/^```markdown$/,/^```$/p') <(sed -n '/^```markdown$/,/^```$/p' _framework/procedures/handover.md)` (usei `git show <base>:arquivo` no lugar do `.bak` citado na SDD, pois não foi deixado `.bak` fora do controle de versão — conteúdo equivalente: versão do `SKILL.md` antes do commit de implementação) — kit e central | sem saída (diff vazio) nos dois | comparação textual — sem sensor aplicável | Sim |
| 4 — RF05, schema de contrato (parse YAML) | `python3 -c "import yaml; ...assert all(k in caps['write_handover'] for k in (...))"` (kit) | exit 0 sem erro | **Sensor executado**: renomeei temporariamente `trigger:` → `trigger_SENSOR_TEST:` na entrada `write_handover` via `Edit` (não `git checkout`); reexecutei o comando → `AssertionError`, exit 1, confirmando falha real; desfiz a edição via `Edit` (revertendo ao texto original) e reexecutei → exit 0 novamente, `git diff --stat` limpo | Sim |
| 5 — RF05, sem nome de fornecedor | `grep -iE "claude\|cursor\|copilot\|codex\|gemini" _framework/rules/workflow-rules.yaml \| grep -A0 -B0 "trigger:\|produces:\|invariants:\|procedure:"` (kit e central) | sem saída (grep exit 1) nos dois | estático — SDD dispensa sensor | Sim |
| 6 — RF06, stub ≤ 25 linhas | `for f in _framework/skills/{handover,pickup,verify-sdd}/SKILL.md; do awk '/^---$/{c++} c==2{n++} END{print n-1}' "$f"; done` (kit e central) | `5`, `5`, `7` nos dois repos — todos ≤ 25 | estático — SDD dispensa sensor | Sim |
| 7 — RF06, sem seção normativa própria | `grep -c "^## Regras$\|^## Template$\|^## Procedimento$" _framework/skills/{handover,pickup,verify-sdd}/SKILL.md` (kit e central) | `0` nos 3 arquivos, nos dois repos | estático — SDD dispensa sensor | Sim |
| 8 — RF06, stub aponta para o procedimento | `grep -l "procedures/" _framework/skills/{handover,pickup,verify-sdd}/SKILL.md \| wc -l` (kit e central) | `3` nos dois | sem sensor previsto pela SDD | Sim |
| 9 — Regressão | `python3 _framework/scripts/framework_check.py --auto` (kit e central) | `✅ Todas as verificações do framework passaram.` exit 0 nos dois | sem sensor previsto pela SDD | Sim |
| 10 — Paridade (RF11) | `diff -r --exclude=__pycache__ _framework/ /home/michel/doc-traceability-central/_framework/` (nas duas direções) | sem saída, exit 0 | sem sensor previsto pela SDD | Sim |

Verificação adicional (não é critério da tabela, mas cobre a checagem
mecânica complementar do procedimento):
`python3 _framework/scripts/render_prompts.py` no kit → todos os artefatos
derivados (`especificacao.md` incluído) reportados "em dia", sem diff —
confirma que `docs/especificacao.md`, tocado no commit fora da lista
explícita da SDD, é puramente derivado de `workflow-rules.yaml` e não
scope creep manual.

## Descompassos encontrados

1. **Arquivo tocado não listado explicitamente na SDD**: `docs/especificacao.md`
   está no diff (`dc9867e`, `fc97fd3`) mas não aparece em "Especificação
   técnica consolidada" da SDD-DTF-0006. Não é scope creep — é saída
   mecânica de `render_prompts.py` a partir de `workflow-rules.yaml`
   (confirmado: rerodar o gerador não produz diff adicional), e o próprio
   commit já anota isso ("docs/especificacao.md regenerado"). Ainda
   assim, a SDD deveria ter registrado esse artefato derivado como parte
   do escopo esperado de qualquer mudança em `workflow-rules.yaml` seção
   12/17 — é descompasso de documentação, não de código.

Fora esse ponto: todo requisito consolidado (RF04, RF05, RF06) tem código
correspondente identificável nos dois repositórios; nenhum arquivo do
diff ficou sem explicação; não há abstração, feature flag ou refactor sem
requisito correspondente (a migração é conteúdo movido, não reescrito).

## Lições

- **Arquivo derivado/gerado deveria ser citado explicitamente na SDD,
  mesmo sendo mecânico.** Toda SDD que altera `workflow-rules.yaml` e
  esse repositório tem um gerador (`render_prompts.py`) que produz
  `docs/especificacao.md`, `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`
  a partir dele deveria listar esses artefatos derivados na
  "Especificação técnica consolidada" como "regenerados automaticamente,
  sem edição manual" — evita a checagem "todo arquivo do diff aparece na
  SDD?" precisar de julgamento extra do verificador para distinguir
  scope creep de efeito colateral esperado.
