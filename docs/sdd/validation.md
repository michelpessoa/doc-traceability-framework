# Verificação — SDD-DTF-0008

- **Veredito:** FAIL
- **Diff verificado:** `f082252~1..f082252` (doc-traceability-framework) / `70b8092~1..70b8092` (doc-traceability-central, mirror do PR #22, PR #21 no central)
- **Verificador independente:** sim (sessão separada da que implementou e da que corrigiu a tentativa anterior; não leu o histórico de nenhuma das duas, só a SDD atual em disco — já com as correções de `ba74c0a`/`dcd53b8` — e os diffs)

**Nota sobre o veredito:** os 8 comandos de aceite + os dois sensores
rodaram de novo nesta sessão e deram exatamente o resultado esperado
(tabela abaixo) — o código de `f082252`/`70b8092` nunca mudou entre as
duas tentativas e continua correto. O segundo descompasso da tentativa
anterior (arquivo fora da lista) está de fato corrigido. Mas o **primeiro
descompasso só foi corrigido pela metade**: a correção `ba74c0a` ajustou a
seção "Casos de borda" e a linha do critério 6, porém a mesma afirmação
factualmente falsa que motivou o FAIL original continua, palavra por
palavra, na seção "Instruções específicas para a IA implementadora" (linha
193-194) — que o `validation.md` da tentativa anterior já havia apontado
como um dos dois lugares onde a afirmação aparecia. Por isso este segundo
FAIL é sobre documentação, não sobre código: a SDD ainda se contradiz
internamente.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `render_prompts.py && diff -rq _framework/scripts _framework/skills/.../scripts --exclude=__pycache__ && diff _framework/rules/workflow-rules.yaml _framework/skills/.../workflow-rules.yaml` | `render_prompts.py` exit 0, todas as linhas `✅ ... sincronizado.`; os dois `diff` sem saída, exit 0 | — | sim |
| 2 | RF08 sensor: editar à mão `skills/.../scripts/framework_lib.py` (linha extra via `Edit`), rodar `render_prompts.py --check`, regenerar com `render_prompts.py` (sem `--check`), rodar `--check` de novo | Editado: `❌ .../framework_lib.py: divergente de .../framework_lib.py.`, exit 1 (`REAL_EXIT:1` medido via `$?` fora do `tail`). Regenerado (script, não `git checkout`): `--check` exit 0, `git status` limpo | Falhou com a condição introduzida, voltou a passar depois — discrimina de verdade | sim |
| 3 | `grep -c '"\.\./AGENTS.md"' _framework/scripts/check_renderings.py` e `grep -c "def check_capability_procedures" _framework/scripts/check_renderings.py` | `1` e `1` | — | sim |
| 4 | RF09 sensor: alterar `capabilities.write_handover.procedure` para `procedures/handover-DOES-NOT-EXIST.md` (via `Edit`), rodar `check_renderings.py`, reverter (via `Edit`), rodar de novo | Alterado: `SENSOR_EXIT:1`, `❌ 1 problema(s) encontrado(s): - write_handover: procedure aponta para procedures/handover-DOES-NOT-EXIST.md (não existe).` Revertido: exit 0, `✅ 5 renderização(ões) concordam...`, `git status` limpo | Falhou nomeando `write_handover`, voltou a passar depois — discrimina de verdade | sim |
| 5 | `grep -c "ai_targets" _framework/templates/sdd.template.md _framework/rules/workflow-rules.yaml` | `0` nos dois arquivos | — | sim |
| 6 | RF10 — documento com `ai_targets` continua válido. Inseri `ai_targets: [claude-code]` no front-matter de `docs/sdd/SDD-DTF-0001.md` via `Edit` (fixture sintética, como a versão corrigida da SDD agora pede), rodei `framework_check.py --auto`, removi a linha via `Edit` | Com o campo inserido: exit 0, `✅ Todas as verificações do framework passaram.`, nenhum erro relacionado a `ai_targets`. Revertido: `git status` limpo | Testado o comportamento real (campo extra não quebra validação) — critério RF10 em si passa | sim (RF10 comportamental confere; ver descompasso residual abaixo sobre a prosa da SDD) |
| 7 | `diff -r --exclude=__pycache__ doc-traceability-framework/_framework doc-traceability-central/_framework` | sem saída, exit 0 | — | sim |
| 8 | `framework_check.py --auto` e `render_prompts.py --check`, nos dois repositórios | Framework (kit): exit 0 nos dois. Central: exit 0 nos dois (avisos pré-existentes de versão de framework por projeto e tipos legados PRD/TS no `.mdc`, nada relacionado a este diff) | — | sim |
| — | `validate_state.py docs/sdd` (checagem mecânica complementar) | `✅ 8 documento(s) verificados: nenhuma SDD implemented sem evidência.` exit 0 | — | sim |

## Descompassos encontrados

1. **Descompasso 2 da tentativa anterior (arquivo fora da spec) — RESOLVIDO.**
   `_framework/skills/doc-traceability-framework/templates/sdd.template.md`
   agora está listado em "Especificação técnica consolidada" (bloco
   adicionado por `ba74c0a`, linhas 144-150 da SDD atual), com a explicação
   correta de por que ele não é coberto por `sync_copies` (RF08 só
   sincroniza `scripts/*.py` e o YAML, não `templates/`). Confirmado: todo
   arquivo do diff `f082252` (14 arquivos, contando a própria SDD) tem
   correspondência na "Especificação técnica consolidada" ou é efeito
   mecânico documentado (builders regenerados, cópias via `sync_copies`).

2. **Descompasso 1 da tentativa anterior (fixture inexistente) — CORRIGIDO
   SÓ PARCIALMENTE, ainda FAIL.** A tentativa anterior apontou que a
   afirmação falsa "`SDD-DTF-0001.md`, que já tem o campo `ai_targets`"
   aparecia em **dois** lugares da SDD: "Casos de borda" (~linha 76-78) e
   "Instruções específicas para a IA implementadora" (~linha 182-185) —
   ver `git show ba74c0a` mensagem de commit e o `validation.md` anterior,
   achado 1. A correção `ba74c0a` editou apenas o primeiro: a seção "Casos
   de borda" (linha 74-81 na versão atual) e a linha do critério 6 agora
   dizem corretamente que "Nenhuma SDD deste repositório tem hoje
   `ai_targets` de fato no front-matter". Mas a seção "Instruções
   específicas para a IA implementadora", linha 193-194, continua
   inalterada e ainda afirma:

   > **NÃO** remover `ai_targets` de SDDs já emitidas
   > (`SDD-DTF-0001.md`, que tem o campo) — não-retroatividade, ...

   Confirmado por `grep -n "tem o campo\|já tem" docs/sdd/SDD-DTF-0008.md`
   — só essa ocorrência sobrou, e é a mesma frase falsa da tentativa
   anterior. `git show ba74c0a -- docs/sdd/SDD-DTF-0008.md` confirma que o
   diff da correção não tocou essas linhas. A SDD agora se contradiz
   internamente: "Casos de borda" diz que nenhuma SDD tem o campo,
   "Instruções específicas" diz que `SDD-DTF-0001.md` tem. Não afeta o
   comportamento do código (o critério 6 já é verificado com fixture
   sintética, item 6 da tabela acima passa), mas é o mesmo tipo de erro
   documental que motivou o FAIL original, só que não varrido por
   completo.

## Lições

- **Corrigir um descompasso apontado em duas ocorrências exige checar as
  duas — `grep` da frase inteira, não só da seção mais óbvia.** A correção
  `ba74c0a` tratou a "Casos de borda" (onde o RF10 é definido formalmente)
  e esqueceu "Instruções específicas para a IA implementadora" (onde a
  mesma frase aparecia como orientação operacional). O `validation.md` da
  tentativa anterior já linkava as duas ocorrências por número de linha —
  a correção deveria ter usado essa lista como checklist literal, não
  reescrito de memória a partir do resumo do achado.
- **Verificação independente de uma correção precisa re-`grep`ar a
  afirmação exata que motivou o FAIL, não só reconferir os comandos da
  tabela de critérios.** Os 8 comandos + 2 sensores passaram de primeira
  nesta sessão — se a verificação parasse aí, o FAIL residual passaria
  despercebido. O procedimento (seção 1, "as duas direções") cobre
  arquivo↔SDD e requisito↔código, mas não nomeia "reconferir descompassos
  da rodada anterior tokens por token"; vale acrescentar isso
  explicitamente quando a verificação é de uma correção pós-FAIL, não de
  uma implementação nova.
- O sensor dos critérios 2 e 4 usou `Edit`/regeneração de script para
  desfazer a condição, nunca `git checkout <arquivo>` — mede o exit code
  real fora de qualquer pipe (`comando > log 2>&1; echo $?`), porque medir
  `$?` depois de um `tail` no mesmo pipeline mede o `tail`, não o comando
  verificado (armadilha notada nesta sessão ao medir o critério 2 pela
  primeira vez).
