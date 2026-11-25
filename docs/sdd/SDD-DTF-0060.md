---
id: SDD-DTF-0060
type: SDD
title: "Skill do framework e prompts de onboarding e auditoria cobrem a aprovação como dado, o executor, a SDD enxuta e o greenfield"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0040, SDD-DTF-0053, SDD-DTF-0054, SDD-DTF-0055, SDD-DTF-0057, SDD-DTF-0058]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção de documentação pedida pelo owner em 2026-11-25, sem mudança de regra, script ou template; ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0040). Três arquivos de produto, todos escritos à mão. A fonte de cada afirmação nova é a chave de workflow-rules.yaml citada no RF, nunca memória. A skill é roteador: aponta a chave do YAML, não copia a regra. check_renderings.py lê o SKILL.md e tem de continuar passando. O _framework/INDEX.md é gerado por render_prompts.py. A SDD-DTF-0059 cobre os guias, em branch própria. O central espelha os três arquivos em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [skill, prompts, onboarding, audit, documentacao, drift, aprovacao, executor, greenfield]
---

# Skill do framework e prompts de onboarding e auditoria cobrem a aprovação como dado, o executor, a SDD enxuta e o greenfield

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`_framework/skills/doc-traceability-framework/SKILL.md` é o roteador que os
agentes seguem, e não muda desde setembro: não cita `approval_policy`,
`approved_by`, `approval_hash.py`, `review_approval.py`, `approvers`,
`executor_contract` nem a SDD enxuta (2.4.0 a 2.8.0). Um agente que segue a
skill não sabe que a SPEC `medium` aprovada precisa de `approved_by` humano
com evidência da review, nem que a SDD compilada pode ser aprovada por
política. `_framework/prompts/onboarding-bootstrap.md` e
`_framework/prompts/framework-audit.md` ainda se apresentam como v1.3.0,
não tratam `repository_status` e mandam "registrar o que for aprovado" sem
dizer como a aprovação é registrada desde a 2.5.0. Esta SDD fecha essas
lacunas sem mudar regra nenhuma.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: três arquivos de texto, reversão trivial, sem alternativa técnica a
registrar. `workflow-rules.yaml`, scripts, templates e `framework.version`
não mudam (`lessons_policy`).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | SKILL.md: seção nova "Aprovação", depois de "Ciclo de vida de status", que aponta `approval_policy` (seção 21: quem aprova cada tipo e sizing, humano ou política), `approved_by` (`frontmatter_schema`), `approval_hash.py`, `review_approval.py` e `approvers`, e diz que mudar o corpo depois da aprovação invalida o `content_sha256` | Quando o SKILL.md for lido, deve existir o título `## Aprovação` e ele deve citar `approval_policy`, `approved_by`, `approval_hash.py`, `review_approval.py` e `approvers` |
| RF02 | SKILL.md: o item "Monta a SDD" e o parágrafo de fluxo dizem que a SDD com `source_docs` em projeto sob 2.7.0 é enxuta (requisitos por referência à SPEC, `sizing` obrigatório, `check_source_docs.py` nas duas direções) e que a coluna `Projeto` (2.8.0) limita os RFs ao `project` da SDD | Quando o SKILL.md for lido, ele deve conter `enxuta` e `Projeto` |
| RF03 | SKILL.md: item novo em "O que fazer em cada pedido comum" para executor (ferramenta que roda o fluxo), apontando `executor_contract` (seção 20) e a regra de escrever só por PR; item novo para "Registra a aprovação", apontando RF01 | Quando o SKILL.md for lido, ele deve conter `executor_contract` |
| RF04 | SKILL.md: a tabela "Leia sob demanda" ganha a linha "aprovação, review, hash, executor" apontando `references/workflow-rules.yaml` nas chaves `approval_policy` e `executor_contract` | Quando o SKILL.md for lido, a tabela "Leia sob demanda" deve ter uma linha com `executor_contract` |
| RF05 | onboarding-bootstrap.md: o Passo 1.1 grava `repository_status: active` junto com `repository` (`registry.central_registry.repository_field`); se o código ainda não existe, o prompt não se aplica e o projeto segue em greenfield (`repository_status: none_yet`) | Quando o prompt for lido, ele deve conter `repository_status` e `none_yet` |
| RF06 | onboarding-bootstrap.md: o Passo 5 e o checklist de saída dizem que, em projeto sob 2.5.0 ou maior, o BASE e cada ADR confirmados entram em `approved` com `approved_by` `kind: human` e `evidence` (URL da review), e que pela PR isso sai de `review_approval.py` | Quando o prompt for lido, ele deve conter `approved_by` e `review_approval.py` |
| RF07 | framework-audit.md: o Passo 0 trata `repository_status: none_yet` — sem repositório de código não há commit a auditar, e o prompt para e reporta isso | Quando o prompt for lido, ele deve conter `none_yet` |
| RF08 | framework-audit.md: o Passo 5 diz como a aprovação de ADR reconstruído é registrada desde a 2.5.0, igual ao RF06 | Quando o prompt for lido, ele deve conter `approved_by` |
| RF09 | Os títulos dos dois prompts deixam de se apresentar como v1.3.0: passam a `(v1.3.0, revisado na 2.8.0)` | Quando os prompts forem lidos, a primeira linha de cada um deve conter `revisado na 2.8.0` |

Fora de escopo: `workflow-rules.yaml`, scripts, templates, as cópias
geradas dentro da skill (`references/`, `scripts/`, `templates/`), as
skills `handover`, `pickup` e `verify-sdd`, `prompts/universal.md` (gerado)
e os guias (SDD-DTF-0059). Os prompts de Cursor e Copilot também ficam de
fora: são gerados por `render_prompts.py` a partir de prefixos fixos no
próprio script, que ainda se apresentam como v1.7.0; atualizá-los é
mudança de script, para uma SDD própria.

## Especificação técnica consolidada

- **Onde.** `_framework/skills/doc-traceability-framework/SKILL.md`
  (RF01 a RF04), `_framework/prompts/onboarding-bootstrap.md` (RF05,
  RF06, RF09) e `_framework/prompts/framework-audit.md` (RF07 a RF09).
- **SKILL.md continua roteador.** As adições apontam a chave do YAML
  (`workflow-rules.yaml:approval_policy`, no formato das linhas
  existentes) e não copiam a regra. O front-matter (`name`,
  `description`) não muda.
- **`check_renderings.py`** confere o SKILL.md contra o YAML (tipos, Iron
  Laws, sizing, nenhum tipo ou status inexistente) e tem de continuar
  passando.
- **Gerado.** `_framework/INDEX.md` é refeito por `render_prompts.py`,
  nunca à mão.
- **Espelho no central.** Os três arquivos e `_framework/INDEX.md`,
  copiados sem divergência para `doc-traceability-central`, em branch e
  PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Seções e itens novos da skill | RF01 a RF04 | `_framework/skills/doc-traceability-framework/SKILL.md` | |
| 2 | Prompt de onboarding | RF05, RF06, RF09 | `_framework/prompts/onboarding-bootstrap.md` | |
| 3 | Prompt de auditoria | RF07 a RF09 | `_framework/prompts/framework-audit.md` | |
| 4 | Regenerar o índice | RF01 a RF09 | `_framework/INDEX.md` | 1, 2, 3 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF09 | `central:_framework/skills/doc-traceability-framework/SKILL.md`, `central:_framework/prompts/onboarding-bootstrap.md`, `central:_framework/prompts/framework-audit.md`, `central:_framework/INDEX.md` | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A08.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01: seção Aprovação na skill | `f=_framework/skills/doc-traceability-framework/SKILL.md; grep -n "^## Aprovação" $f; for t in approval_policy approved_by approval_hash.py review_approval.py approvers; do grep -q "$t" $f \|\| echo "falta $t"; done` | Uma linha de título e nenhum `falta` | automatizado |
| A02 | RF02 a RF04: enxuta, Projeto e executor na skill | `f=_framework/skills/doc-traceability-framework/SKILL.md; for t in enxuta Projeto executor_contract; do grep -q "$t" $f \|\| echo "falta $t"; done` | Nenhum `falta` | automatizado |
| A03 | RF05 e RF06: prompt de onboarding | `f=_framework/prompts/onboarding-bootstrap.md; for t in repository_status none_yet approved_by review_approval.py; do grep -q "$t" $f \|\| echo "falta $t"; done` | Nenhum `falta` | automatizado |
| A04 | RF07 e RF08: prompt de auditoria | `f=_framework/prompts/framework-audit.md; for t in none_yet approved_by; do grep -q "$t" $f \|\| echo "falta $t"; done` | Nenhum `falta` | automatizado |
| A05 | RF09: títulos dos prompts | `head -1 _framework/prompts/onboarding-bootstrap.md _framework/prompts/framework-audit.md \| grep -c "revisado na 2.8.0"` | `2` | automatizado |
| A06 | RF01 a RF09: cada afirmação nova bate com a chave do YAML que ela cita (`approval_policy`, `frontmatter_schema.approved_by`, `executor_contract`, `registry.central_registry`) | Leitura lado a lado do diff dos três arquivos e das chaves citadas de `_framework/rules/workflow-rules.yaml` | Nenhuma afirmação sem chave correspondente ou que a contradiga | manual |
| A07 | Renderizações, gerados, suíte, validação e escopo | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0` três vezes; 0 failed; só os três arquivos, `_framework/INDEX.md`, esta SDD e os gerados de `docs/sdd/` (`registry.yaml`, `registry.md`, `INDEX.md`) | automatizado |
| A08 | Central: espelho idêntico | No central: `cmp` dos três arquivos e de `_framework/INDEX.md` contra o kit; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0060-skill-e-prompts`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0060`. Nunca em `main`.
- **Fonte:** cada afirmação nova vem da chave do YAML citada no RF, aberta
  na hora de escrever.
- **Não mudar** `workflow-rules.yaml`, scripts, templates, as cópias
  geradas dentro da skill, as outras skills, os prompts gerados nem os
  guias.
- **Gerados só por script:** `render_prompts.py` para `_framework/INDEX.md`;
  `generate_registry_md.py` para `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF09) tem trecho
      correspondente nos três arquivos.
- [ ] Todo arquivo tocado aparece nas tasks ou nas instruções.
- [ ] Nenhuma mudança em regra, script, template, gerado, outra skill ou
      guia.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** {sim | não — mesma sessão que implementou}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
