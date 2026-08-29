# Verificação — SDD-DTF-0008

- **Veredito:** PASS
- **Diff verificado:** `f082252` (kit, PR #22) / `70b8092` (central, PR #21) — Refs: SDD-DTF-0008
- **Verificador independente:** sim (sessão separada da que implementou; não li o histórico da sessão de implementação, só a SDD e o diff)

Esta é a terceira tentativa. As duas anteriores falharam por afirmações
factualmente incorretas na própria SDD (fixture errado no critério 6;
arquivo de template faltando na lista de "Especificação técnica
consolidada"; frase remanescente afirmando que `SDD-DTF-0001.md` já
tinha `ai_targets` no front-matter). Ambas foram corrigidas (`ba74c0a`,
`b71dda3`). Nesta sessão, `grep -rn "que tem o campo\|SDD-DTF-0001.md"
docs/sdd/SDD-DTF-0008.md` mostra só a linha do critério 6, que cita
`SDD-DTF-0001.md` como *exemplo de arquivo a usar no teste*, não como
afirmação sobre seu estado atual — não sobrou claim falso.

| # | Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF08 — cópias sincronizadas | `render_prompts.py && diff -rq _framework/scripts _framework/skills/.../scripts --exclude=__pycache__ && diff _framework/rules/workflow-rules.yaml _framework/skills/.../workflow-rules.yaml` — kit e central | exit 0, sem saída de diff, nos dois repositórios | — | Sim |
| 2 | RF08 (sensor) — cópia editada à mão reprova | Acrescentei linha em `_framework/skills/.../scripts/framework_lib.py` via `Edit`, rodei `render_prompts.py --check` | `❌ .../framework_lib.py: divergente de .../framework_lib.py.`, exit 1 | Regenerado (`render_prompts.py`), `diff` contra backup = vazio, `--check` voltou a exit 0, `git status` limpo | Sim |
| 3 | RF09 — `RENDERINGS` ganha AGENTS.md e `check_capability_procedures` existe | `grep -c '"\.\./AGENTS.md"' _framework/scripts/check_renderings.py` e `grep -c "def check_capability_procedures" ...` — kit e central | `1` e `1` nos dois repositórios | — | Sim |
| 4 | RF09 (sensor) — `procedure` inexistente reprova | Editei `write_handover.procedure` em `_framework/rules/workflow-rules.yaml` para `procedures/handover-NONEXISTENT.md` via `Edit`, rodei `check_renderings.py` | `❌ 1 problema(s) encontrado(s): - write_handover: procedure aponta para procedures/handover-NONEXISTENT.md (não existe).`, exit 1 | Restaurado do backup, `diff` = vazio, `check_renderings.py` voltou a `✅ ... concordam ...`, exit 0, `git status` limpo | Sim |
| 5 | RF10 — `ai_targets` fora do template e do YAML | `grep -c "ai_targets" _framework/templates/sdd.template.md _framework/rules/workflow-rules.yaml` — kit e central | `0` nos dois arquivos, nos dois repositórios | — | Sim |
| 6 | RF10 — documento com `ai_targets` continua válido | Inseri `ai_targets: [claude-code]` no front-matter de `docs/sdd/SDD-DTF-0001.md` (kit — único repo onde o arquivo existe; central não tem SDDs de DTF), rodei `framework_check.py --auto`, depois removi a linha | Com o campo: exit 0, nenhum erro relacionado a `ai_targets` (8 documentos ok). Sem o campo (estado restaurado): exit 0 também | — | Sim |
| 7 | RF11 — paridade | `diff -r --exclude=__pycache__` entre `_framework/` do kit e do central | exit 0, sem saída | — | Sim |
| 8 | Regressão | `framework_check.py --auto` e `render_prompts.py --check` — kit e central | exit 0 nos dois repositórios, todos os documentos/renderizações ok | — | Sim |

Checagem mecânica complementar: `python3 _framework/scripts/validate_state.py docs/sdd` → `✅ 8 documento(s) verificados: nenhuma SDD implemented sem evidência.` (exit 0).

## Conformidade com a spec (as duas direções)

- RF08 → `sync_copies` em `render_prompts.py` (critérios 1 e 2). RF09 →
  `RENDERINGS` + `check_capability_procedures` em `check_renderings.py`
  (critérios 3 e 4), confirmado que `procedures/handover.md`,
  `procedures/pickup.md` e `procedures/verify-sdd.md` existem de fato.
  RF10 → remoção de `ai_targets` do template e do YAML, com
  retrocompatibilidade confirmada (critérios 5 e 6). Nenhum requisito
  ficou sem código.
- Todos os 14 arquivos do diff `f082252`/`70b8092` aparecem na
  "Especificação técnica consolidada": os arquivos-fonte
  (`render_prompts.py`, `check_renderings.py`, `workflow-rules.yaml`,
  `sdd.template.md` nas duas cópias, `universal.md`,
  `copilot-instructions.md`) são citados individualmente; as cópias
  dentro de `skills/doc-traceability-framework/{scripts,references}/`
  (`framework_lib.py`, `registry_tools.py`, `validate_state.py`,
  `check_renderings.py`, `render_prompts.py`, `workflow-rules.yaml`) são
  cobertas pela descrição geral de `sync_copies` — efeito mecânico de
  resincronizar cópias que já estavam divergentes desde v2.0.0, não
  edição manual arquivo por arquivo, então não precisam de menção
  nominal. `docs/sdd/SDD-DTF-0008.md` no diff é a própria SDD,
  atualizada durante a implementação (registrado no corpo do commit).
- Nenhuma abstração, dependência, feature flag ou refactor sem
  requisito correspondente encontrado.

## Outras afirmações verificáveis conferidas nesta sessão

Dado o histórico de FAILs por claim factual incorreto, reli a SDD
inteira e conferi, além de `ai_targets`, cada afirmação testável:

- "`RENDERINGS` ganha só `../AGENTS.md`" — confirmado, lista tem
  exatamente 5 entradas, uma nova.
- "`build_quickstart` não chama `core_facts`" — confirmado por leitura
  da função.
- "Nenhuma SDD deste repositório tem hoje `ai_targets` de fato no
  front-matter" — confirmado por varredura de front-matter (não só
  grep de texto solto) em `docs/sdd/*.md` do kit e em todo `docs/` do
  central: zero ocorrências reais de campo, só menções em prosa.
- "`docs/especificacao.md` não menciona `ai_targets`" — confirmado,
  `grep -c` = 0, inclusive após regerar o arquivo nesta sessão.
- "stub de 5-7 linhas" (SKILL.md de handover/pickup/verify-sdd) —
  confirmado: corpo após o front-matter tem 5, 5 e 7 linhas
  respectivamente.
- Nenhuma outra afirmação sobre estado do repositório se mostrou
  incorreta.

## Descompassos encontrados

Nenhum.

## Lições

- Red flag reaproveitável (já viu duas vezes nesta mesma SDD): SDD que
  faz afirmação factual sobre o estado de *outro* documento do
  repositório (“X já tem/não tem campo Y”) precisa ser conferida
  arquivo por arquivo na verificação, não só por leitura da SDD — a
  segunda tentativa já tinha corrigido uma ocorrência da frase e deixado
  a outra sobreviver porque a correção não foi replicada em todos os
  lugares onde a mesma claim aparecia. Nesta terceira tentativa, `grep`
  dirigido às duas frases confirmou que não sobrou nenhuma.
- Quando uma SDD descreve um efeito mecânico de sincronização (aqui,
  `sync_copies`) que toca vários arquivos-cópia sem edição manual
  individual, é aceitável a spec cobri-los com uma descrição geral em
  vez de listar cada arquivo — desde que o comando de verificação (aqui,
  `diff -rq` no critério 1) prove que a cópia bate com a origem depois
  da execução.
