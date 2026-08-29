---
id: RFC-{PROJECT_CODE}-{SEQ}
type: RFC
title: "{Título da proposta}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
parent_strategy: null   # id do STRAT de origem, se houver
parent_postmortem: null # id do PM de origem, se esta RFC nasceu de um action item de postmortem
requires_adr: null       # null até o gate ser avaliado (ver seção "Gate de decisão")
decision_gate_criteria_met: []
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> Use antes de decisões relevantes: mudança transversal, impacto em
> múltiplos times, custo alto, risco técnico, nova tecnologia ou
> alteração de contrato entre serviços.

## Contexto
## Problema
## Objetivos
## Não objetivos
## Alternativas consideradas
## Proposta
## Impactos
## Riscos
## Plano
## Métricas de sucesso

---

## Gate de decisão: esta RFC exige um ADR?
> Preencher **somente após a RFC ser aprovada**. Marque cada critério que
> se aplica. Se **qualquer** critério for verdadeiro, `requires_adr: true`
> e um ADR deve ser criado antes da SPEC. Se nenhum se aplica,
> `requires_adr: false` e o fluxo segue direto para a SPEC.

- [ ] Introduz ou altera um padrão arquitetural
- [ ] Decisão de alto custo ou difícil reversão
- [ ] Trade-off técnico relevante entre alternativas viáveis
- [ ] Impacto cross-team (mais de um time/domínio afetado)
- [ ] Troca ou introdução de tecnologia/vendor/dependência externa relevante

**Decisão do gate:** `requires_adr = {true|false}`
**Justificativa:**

## Documentos originados
| ID | Tipo | Título | Status |
|---|---|---|---|
| | | | |
