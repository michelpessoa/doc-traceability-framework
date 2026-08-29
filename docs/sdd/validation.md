# Verificação — SDD-DTF-0008

- **Veredito:** FAIL
- **Diff verificado:** `f082252~1..f082252` (doc-traceability-framework) / `70b8092~1..70b8092` (doc-traceability-central, mesmo diff — mirror do PR #22, PR #21 no central)
- **Verificador independente:** sim (sessão separada da que implementou; não leu o histórico da sessão de implementação, só a SDD atual — já corrigida — e o diff)

**Nota sobre o veredito:** todos os 8 comandos de aceite + os dois sensores
rodaram e deram exatamente o resultado esperado nesta sessão (tabela
abaixo). O `FAIL` não é sobre o código funcionar — é sobre a conformidade
"nas duas direções" da seção 1 do procedimento: a SDD contém uma afirmação
factualmente incorreta sobre a fixture do critério 6, e um arquivo do diff
não está listado em "Especificação técnica consolidada". Ver "Descompassos
encontrados".

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `render_prompts.py && diff -rq _framework/scripts _framework/skills/.../scripts --exclude=__pycache__ && diff _framework/rules/workflow-rules.yaml _framework/skills/.../workflow-rules.yaml` | `render_prompts.py` exit 0, todas as linhas `✅ ... sincronizado.`; os dois `diff` sem saída, exit 0 | — | sim |
| 2 | RF08 sensor: editar à mão `skills/.../scripts/framework_lib.py` (linha extra), rodar `render_prompts.py --check`, regenerar com `render_prompts.py` (sem `--check`), rodar `--check` de novo | Editado: `❌ .../framework_lib.py: divergente de .../framework_lib.py.` exit 1. Após regenerar (via script, não `git checkout`): `--check` exit 0, `git status` limpo | Falhou com a condição introduzida, voltou a passar depois — discrimina de verdade | sim |
| 3 | `grep -c '"\.\./AGENTS.md"' _framework/scripts/check_renderings.py` e `grep -c "def check_capability_procedures" _framework/scripts/check_renderings.py` | `1` e `1` | — | sim |
| 4 | RF09 sensor: alterar `capabilities.write_handover.procedure` para `procedures/handover-NONEXISTENT.md` (via `Edit`), rodar `check_renderings.py`, reverter (via `Edit`), rodar de novo | Alterado: `❌ 1 problema(s) encontrado(s): - write_handover: procedure aponta para procedures/handover-NONEXISTENT.md (não existe).` exit 1. Revertido: exit 0, `5 renderização(ões) concordam...` | Falhou com a condição introduzida, nomeando `write_handover`, voltou a passar depois — discrimina de verdade | sim |
| 5 | `grep -c "ai_targets" _framework/templates/sdd.template.md _framework/rules/workflow-rules.yaml` | `0` nos dois arquivos | — | sim |
| 6 | RF10 — documento já emitido com `ai_targets` continua válido. **A fixture que a SDD nomeia (`docs/sdd/SDD-DTF-0001.md`, "que já tem o campo") não tem o campo** — confirmado por `grep -n "ai_targets" docs/sdd/SDD-DTF-0001.md` (só ocorre em prosa, "remoção de `ai_targets`", nunca em front-matter) e por `git log -p` do arquivo inteiro (o front-matter nunca teve essa chave). Adaptei o sensor: adicionei `ai_targets: []` ao front-matter via `Edit`, rodei `framework_check.py --auto`, revertidas via `Edit` (não `git checkout`) | Com o campo inserido: `framework_check.py --auto` — exit 0, `✅ Todas as verificações do framework passaram.`, nenhum erro relacionado a `ai_targets`. Revertido: `git status` limpo | Testei o comportamento real (campo extra não quebra validação) porque a fixture nomeada na SDD não existia como descrito | sim, mas com descompasso na SDD — ver abaixo |
| 7 | `diff -r --exclude=__pycache__ doc-traceability-framework/_framework doc-traceability-central/_framework` | sem saída, exit 0 | — | sim |
| 8 | `framework_check.py --auto` e `render_prompts.py --check`, nos dois repositórios | Framework: exit 0 nos dois (avisos pré-existentes: versão de framework por projeto, tipos legados PRD/TS no `.mdc` — nada relacionado a este diff). Central: exit 0 nos dois | — | sim |
| — | `validate_state.py docs/sdd` (checagem mecânica complementar) | `✅ 8 documento(s) verificados: nenhuma SDD implemented sem evidência.` exit 0 | — | sim |

## Descompassos encontrados

1. **Critério 6 nomeia uma fixture que não existe como descrita.** A SDD
   (seção "Casos de borda", linha ~76-78, e "Instruções específicas para a
   IA implementadora", linha ~182-185) afirma que `docs/sdd/SDD-DTF-0001.md`
   "já tem o campo" `ai_targets` no front-matter. Isso é falso: `grep` e
   `git log -p` confirmam que esse arquivo nunca teve `ai_targets` como
   chave de front-matter — a única ocorrência da string é prosa listando
   `ai_targets` como fora de escopo daquela SDD. Nenhum documento em
   `docs/` deste repositório tem `ai_targets:` em front-matter de verdade
   (`SDD-DTF-0007.md` também só cita a string em prosa). O critério RF10
   em si (campo extra de front-matter não quebra `validate_doc.py`) foi
   verificado de verdade nesta sessão inserindo o campo manualmente e
   revertendo — mas a SDD precisa de correção: ou aponta para uma fixture
   real, ou reconhece explicitamente que a fixture terá de ser criada
   (documento sintético) porque nenhuma SDD emitida carrega o campo.

2. **Arquivo do diff fora da lista em "Especificação técnica consolidada":**
   `_framework/skills/doc-traceability-framework/templates/sdd.template.md`
   foi alterado no commit `f082252` (2 linhas removidas, mesmas duas de
   `_framework/templates/sdd.template.md`) mas a seção "Especificação
   técnica consolidada" da SDD só lista `_framework/templates/sdd.template.md`
   (linha 135) — a cópia dentro da skill não aparece ali. A mensagem do
   commit reconhece o ajuste ("Efeito colateral corrigido... fora do
   escopo de `sync_copies`... sincronizado à mão, mesma fonte"), então a
   correção em si é coerente com RF08/RF10 e com `ADR-DTF-0001` (a cópia
   da skill nunca deveria divergir do original) — mas a SDD não registra
   esse arquivo como alvo. Escopo não registrado, não scope creep: o
   conteúdo do ajuste é correto, falta só a linha na spec.

Fora esses dois pontos, as duas direções de conformidade fecham:

- RF08, RF09, RF10 têm código correspondente identificável (`sync_copies`
  + chamada em `main()`; `RENDERINGS` com `../AGENTS.md` +
  `check_capability_procedures`; remoção de `ai_targets` do YAML e do
  template, propagada às duas strings-prefixo transcritas).
- Nenhuma abstração, config, feature flag ou refactor sem requisito
  correspondente — os diffs de `registry_tools.py`/`validate_state.py`
  dentro da cópia da skill são só o efeito mecânico de `sync_copies`
  trazendo essas cópias, que já estavam desatualizadas desde a v2.0.0,
  para o que já existe no original (confirmado lendo o diff: nenhuma
  função nova nesses dois arquivos, só conteúdo já existente no fonte).
- RF11 (paridade) confirmado por `diff -r` vazio entre os dois `_framework/`.
- `ai_targets` **não** foi removido de `docs/sdd/SDD-DTF-0001.md` — como
  já dito no achado 1, esse arquivo nunca teve o campo, então não há como
  violar a não-retroatividade ali; mas a intenção da regra (não tocar
  documento já emitido) foi respeitada em todo o restante: nenhuma SDD
  emitida foi alterada por este diff além da própria SDD-DTF-0008.

## Lições

- **Fixture citada em critério de aceite precisa ser conferida antes de
  aprovar a SDD, não só no momento da verificação.** A SDD afirmou como
  fato ("que já tem o campo") algo que um `grep` de 5 segundos teria
  desmentido. Vale um passo explícito no procedimento de escrita de SDD:
  toda fixture citada em "Critérios de aceite" se confirma por comando
  antes do `approved`, não se assume por lembrança da sessão anterior.
- **"Efeito colateral corrigido" mencionado só na mensagem de commit não
  é registro na SDD.** A mensagem de commit é boa prática de
  transparência, mas não substitui atualizar "Especificação técnica
  consolidada" — é exatamente o tipo de arquivo que a verificação
  independente existe para pegar, porque quem implementou tem o commit
  message como "já documentei isso" e não volta à SDD.
- O sensor dos critérios 2 e 4 usou `Edit`/regeneração de script para
  desfazer a condição, nunca `git checkout <arquivo>` — evita o risco de
  desfazer o HEAD errado e exercita o próprio mecanismo de correção que o
  critério describe (regenerar / corrigir o YAML), reforçando o padrão já
  registrado na lição equivalente de SDD-DTF-0007.
