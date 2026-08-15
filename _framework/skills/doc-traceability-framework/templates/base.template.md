---
id: BASE-{PROJECT_CODE}-{SEQ}
type: BASE
title: "Baseline — estado atual do projeto {PROJECT_CODE}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
scan_date: "{YYYY-MM-DD}"
known_gaps: []
tags: [onboarding]
---

# Baseline — {PROJECT_CODE}

> Este documento é usado SOMENTE no onboarding de um projeto que já tinha
> código em produção antes de adotar este framework. Não é uma decisão —
> é uma fotografia do que já existe hoje, levantada por uma IA lendo o
> repositório de código. Normalmente existe apenas UM por projeto.

## Como este levantamento foi feito
Repositório(s) analisado(s), data do scan, ferramenta/IA usada.

## Stack e arquitetura atual
Linguagens, frameworks, bancos de dados, infraestrutura, principais
serviços/módulos e como se conectam.

## Integrações e dependências externas
APIs, filas, provedores, contratos com outros times/sistemas.

## Dívidas técnicas conhecidas
O que já se sabe que precisa de atenção (não é para resolver aqui, só
registrar).

## O que não foi possível inferir com confiança (`known_gaps`)
Liste aqui qualquer coisa que o levantamento automático não conseguiu
determinar com segurança — fica para alguém do time completar.

## ADRs reconstruídos a partir deste baseline
| ID | Decisão | Status |
|---|---|---|
| | | |

## Próximo passo
Depois que os ADRs acima forem revisados e aprovados, este projeto passa
a operar no fluxo normal do framework (Strategy → RFC → gate → ...),
começando a numeração de RFC/PRD/TS/SDD do zero.
