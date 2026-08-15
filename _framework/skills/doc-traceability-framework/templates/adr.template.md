---
id: ADR-{PROJECT_CODE}-{SEQ}
type: ADR
title: "{Título da decisão}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
parent_rfc: "{id da RFC de origem, ou id do BASE se este ADR for reconstruído no onboarding}"
strategic_impact: false   # true = deve realimentar um Strategy Doc
decision: "{resumo de 1 linha da decisão tomada}"
provenance: authored   # authored = decisão tomada agora | reconstructed = inferida pela IA a partir de código existente (onboarding)
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> Formato enxuto (Michael Nygard). Uma vez com status `approved`, este
> documento é **imutável** — mudanças de entendimento geram um novo ADR
> que marca este como `superseded`.
>
> Se `provenance: reconstructed` (ADR gerado no onboarding de um projeto
> já existente): o status **nunca** começa em `approved`. Ele nasce em
> `in_review` e só avança depois que uma pessoa confirma ou corrige o
> raciocínio da IA — a IA está inferindo a partir do código, não
> reportando uma decisão que presenciou.

## Status
`draft | in_review | approved | rejected | superseded`

## Contexto
Qual é o problema que estamos decidindo e por quê agora.

## Decisão
O que foi decidido, de forma direta.

## Alternativas consideradas
Quais outras opções existiam e por que foram rejeitadas.

## Consequências
O que fica mais fácil, o que fica mais difícil, trade-offs aceitos.

## Impacto estratégico
Esta decisão deve realimentar um Strategy Doc? (`strategic_impact`)
Se sim, referenciar o STRAT criado/atualizado em `relates_to`.
