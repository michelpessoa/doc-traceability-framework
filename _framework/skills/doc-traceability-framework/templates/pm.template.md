---
id: PM-{PROJECT_CODE}-{SEQ}
type: PM
title: "Postmortem — {título do incidente}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável pela análise}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
source_incident: "{id do INC de origem}"
severity_inherited: "{SEV1|SEV2|SEV3|SEV4}"
action_items: []
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> Postmortem é blameless: o objetivo é entender causa e sistema, não
> apontar culpados. Segue o ciclo de vida padrão do framework
> (draft → in_review → approved → ...).

## Resumo
O que aconteceu, em 2-3 frases, para quem não viveu o incidente.

## Linha do tempo detalhada
(Pode expandir a linha do tempo do INC de origem.)

## Causa raiz
Análise completa — não só "o que quebrou", mas "por que o sistema
permitiu que isso quebrasse".

## Fatores contribuintes
O que tornou o incidente possível ou pior do que precisava ser (ex.:
falta de alerta, dependência única, processo manual).

## O que funcionou bem
Vale registrar também — não é só sobre o que deu errado.

## Action items
| # | Descrição | Triagem | Documento gerado |
|---|---|---|---|
| 1 | | `small_direct_fix` \| `structural_change` | |

> `small_direct_fix` → entra pelo sizing como `small` ou `medium`, sem RFC.
> `structural_change` → vira uma nova RFC (referenciando este PM em
> `relates_to`), e segue o gate normal a partir daí.

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_incident | {id do INC} |
| severity_inherited | {severidade} |
