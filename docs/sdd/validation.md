# Verificação — SDD-DTF-0016

- **Veredito:** PASS (técnico) — com bloqueio de processo pendente (ver "Descompassos encontrados")
- **Diff verificado:** `main` (39b3af8) .. `sdd/SDD-DTF-0016-rule-since-por-data` (cbc4a7c)
- **Verificador independente:** sim — sessão separada, sem ter lido o histórico da sessão implementadora, apenas a SDD e o diff.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1. Changelog tem `date` em toda entrada | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); print(all('date' in e for e in d['framework']['changelog']))"` | `True` | trivial (checagem estrutural) | Sim |
| 2. EVM (registry 2.1.0, PRD/TS criadas 2026-08-25/antes de 1.7.0) deixa de reprovar | `python3 _framework/scripts/framework_check.py /home/michel/doc-traceability-central/docs/EVM` (branch fix) vs. mesmo comando com `_framework` do `main` num `git worktree` separado | Branch fix: `✅ Todas as verificações do framework passaram.` (44 docs). `main` (pré-fix): `❌ 1 verificação(ões) falharam` — 11 PRD-EVM-000x reprovados por RF-ID ausente, idêntico ao relato da SDD. Confirmado `created: "2026-08-25"` em PRD-EVM-0001 (antes de 2026-08-29, data de 1.7.0) | Sim — reproduzi eu mesma o `❌` do `main` e o `✅` da branch, no mesmo diretório central, nesta sessão | Sim |
| 3. Documento pós-1.7.0 sem RF-ID continua reprovando (sensor negativo) | Criei `PRD-SENSOR-0001.md` (`created: "2026-09-01"`) sem RF-ID formal, fora de qualquer `registry.yaml` de projeto (fallback puro por data), e rodei `python3 _framework/scripts/validate_doc.py <path>` | `❌ 3 problema(s)`, incluindo `'Requisitos funcionais' sem RF-ID próprio` | Sim — quebrei deliberadamente `rule_applies_since_date` (`return False` quando `since_date and doc_created`) e reexecutei: o erro de RF-ID desapareceu (`❌ 2 problema(s)`, sem a linha de RF-ID). Desfiz a alteração e confirmei retorno ao `❌ 3 problema(s)` original, `git diff --stat` limpo | Sim |
| 4. Skill sincronizada | `python3 _framework/scripts/render_prompts.py` | Todas as linhas `✅ .../sincronizado`/`em dia`, incluindo `framework_lib.py`, `validate_doc.py`, `references/workflow-rules.yaml` | trivial (idempotência do sync) — também confirmado por `diff` byte-a-byte entre `_framework/scripts/{framework_lib,validate_doc}.py` e as cópias em `_framework/skills/doc-traceability-framework/` | Sim |
| 5. Regressão geral | `python3 -m pytest -q` → `7 passed in 0.12s`. `python3 _framework/scripts/framework_check.py --auto` → `✅ 16 documento(s) ok` + `✅ Todas as verificações do framework passaram` (examples/central/EXEMPLO, LEGADO, project-repo-checkout). `python3 _framework/scripts/framework_check.py docs/sdd` (neste repo) → `✅` (16 docs). `framework_check.py docs/EVM` (central) → `✅` (44 docs). `framework_check.py docs/DTF` (central) → `✅` (12 docs). `framework_check.py docs/ABSTRACTCLINIC` (central) → `✅` (17 docs) | sem sensor dedicado — regressão geral, não lógica nova desta SDD | Sim, todas |

## Conformidade requisito → código (e inverso)

Todos os 4 requisitos consolidados da SDD têm código correspondente confirmado por leitura de diff:
- `date` em `framework.changelog` (workflow-rules.yaml) — presente em todas as 11 entradas.
- `version_date()` e `rule_applies_since_date()` em `framework_lib.py` — implementação bate literalmente com o pseudocódigo da "Especificação técnica consolidada" da SDD.
- `validate_doc.check_document` troca `rule_applies` por `rule_applies_since_date(rules, RULE_SINCE[rule], fm.get("created"), version)`, com `load_rules()` chamado uma vez — confirmado no diff.
- `render_prompts.py` sincronizou as cópias da skill (mecanismo existente, não código novo) — confirmado por diff byte-a-byte igual entre original e cópia.

Direção inversa (arquivo no diff sem requisito): os 10 arquivos do diff (`LESSONS.md`, `workflow-rules.yaml`, `framework_lib.py`, `validate_doc.py`, as 3 cópias correspondentes em `_framework/skills/...`, `SDD-DTF-0016.md`, `registry.md`, `registry.yaml`) mapeiam integralmente para: os 3 arquivos de framework declarados + suas cópias sincronizadas (mecanismo já existente) + bookkeeping do próprio SDD/registry + `LESSONS.md` documentando o desvio de processo. Nenhum scope creep encontrado. `render_prompts.py` em si não foi alterado (corretamente, a SDD não pede isso).

## Descompassos encontrados

**Gate 13 (`gate_implementation_before_code`) violado — confirmado.** O único commit da branch (`cbc4a7c`) contém, na mesma mensagem, a nota: *"código escrito antes da SDD (gate 13 violado), registrado em LESSONS.md. SDD-DTF-0016 fica em draft até verificação independente"*. Não há como reconstruir pela árvore de commits a ordem cronológica real dentro da sessão implementadora (é um único commit atômico cobrindo LESSONS.md, código de framework e a própria SDD), mas a admissão está registrada tanto no corpo do commit quanto em `LESSONS.md` (entrada de 2026-09-04, "Gate 13 violado ao corrigir o próprio gate_content_quality") quanto no corpo da SDD (`Evidência de verificação` → "não — mesma sessão que implementou (gate 13 violado...)"). `docs/sdd/registry.yaml`/`registry.md` também refletem `status: draft` para SDD-DTF-0016, não `approved` nem `implemented` — a sessão implementadora não tentou esconder ou pular o problema, e explicitamente reteve o próprio avanço de status até esta verificação. Nenhuma exceção do gate 13 se aplica (não é INC ativo).

Nenhum outro descompasso: sem requisito órfão, sem arquivo fora de escopo, sem abstração extra.

## Lições

Já capturada em `LESSONS.md` (entrada de 2026-09-04) com a red flag correta ("já entendi o que fazer, documentar é burocracia") e o padrão notado (segunda ocorrência na mesma sessão, projetos diferentes DTF/EVM, mas não atinge o critério de virar regra global por ser comportamento de agente numa sessão, não gap estrutural — corretamente avaliado contra `lessons_policy.when_a_lesson_becomes_a_rule`, que exige 2 PROJETOS + checagem mecânica possível).

## Recomendação de status

Verificação técnica: **PASS** — todos os requisitos têm código correspondente, nenhum scope creep, todos os 5 critérios de aceite rodados nesta sessão com saída real, sensor de discriminação do critério 3 confirmado positivo (falha injetada faz o teste cair; revertida, volta a passar), regressão completa verde em todos os 6 alvos pedidos.

Processo: gate 13 foi violado (código antes da SDD existir), fato admitido pela própria sessão implementadora em três lugares (commit, LESSONS.md, corpo da SDD) e não escondido. O procedimento normativo (`_framework/rules/workflow-rules.yaml`, seção 13) trata esse gate como erro a evitar pela própria IA, sem exceção fora de incidentes ativos, e o padrão `if_user_asks_to_skip` (a única passagem do framework que trata de skip do gate 13) exige, quando a ordem é pulada, **confirmação humana explícita** antes de prosseguir — não apenas registro em prosa pela própria IA. Aqui a IA já se autoimpôs `status: draft` e retenção do avanço até verificação independente, o que é a correção mecânica adequada, mas essa autocorreção não substitui a confirmação humana explícita que o framework exige para esse tipo de desvio.

Portanto: **não avançar automaticamente para `implemented` nem para `approved` só com base nesta verificação técnica** — exigia aprovação humana explícita primeiro.

**Atualização 2026-09-08:** aprovação obtida (Michel Pessoa, dono do
projeto), ciente do gate 13 violado. PR #47 já estava mergeada em
`main` do kit desde 2026-09-05 (só a SDD ficou presa em `draft`). Nesta
sessão: `draft` → `implemented` direto (gate é de ordem, não de tempo de
espera), `LESSONS.md` mantido sem mudança (já adequado). Próximo passo:
sincronizar `_framework/` do kit para o espelho em
`doc-traceability-central` (`[[project_framework_dois_repos_sync]]`),
que ainda está com a versão antiga e por isso `main` do central segue
vermelho (`framework-check` runs #67/#68).

## Ressalvas de verificação

- Não pude reconstruir a ordem cronológica exata dentro da sessão implementadora (código antes/depois da SDD) via timestamps de commit, pois tudo está em um único commit atômico — a confirmação do gate 13 violado se apoia na admissão textual (commit message + LESSONS.md + corpo da SDD), não em evidência de timestamp independente.
- `gh pr view 47` confirma PR aberta, `main` ← `sdd/SDD-DTF-0016-rule-since-por-data`, estado `OPEN`, corpo da PR já menciona a mesma ressalva de gate 13/draft.
