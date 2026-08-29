---
id: TS-{PROJECT_CODE}-{SEQ}
type: TS
title: "{Título da especificação técnica}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
parent_rfc: "{id da RFC de origem}"
parent_adr: null   # id do ADR, ou null se o gate dispensou ADR
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> Tech Spec é o documento que transforma uma decisão em desenho
> executável. Deve detalhar implementação, explicitar contratos técnicos,
> alinhar times consumidores, reduzir ambiguidade de execução, antecipar
> riscos operacionais e conectar arquitetura, código e rollout. É a fonte
> final para a SDD.

> Tech Spec garante o **COMO** e o **ONDE**: todo contrato abaixo precisa
> de assinatura/schema exato (não prosa livre), e todo item do plano de
> implementação precisa de arquivo/módulo concreto. Proibido placeholder
> ("TBD", "ajustar conforme necessário", "seguir padrão do projeto" sem
> dizer qual arquivo é o padrão) — se não souber ainda, marque
> `[NEEDS CLARIFICATION: pergunta objetiva]`.

## Visão geral da solução

## Contratos técnicos (APIs, eventos, schemas)
Para cada contrato: nome exato de função/endpoint/evento, assinatura ou
schema completo (tipos de entrada/saída), e **onde vive** (arquivo/módulo).

**Consumes** (o que este contrato espera de código/dados já existentes —
nomes e tipos exatos, não descrição):
**Produces** (o que este contrato entrega para quem for consumi-lo depois
— nomes e tipos exatos):

## Casos de borda / tratamento de erro
Todo caminho de falha do contrato acima: entrada inválida, dependência
indisponível, condição de corrida, limite excedido. Cada linha referencia
o RF do PRD que originou a exigência, quando houver.

| Caso | RF relacionado (PRD) | Comportamento esperado | Onde é tratado |
|---|---|---|---|

## Estratégia de teste
Que tipo de teste cobre cada contrato (unitário/integração/e2e), com que
nível de mock (real vs. mockado, e por quê), e onde o arquivo de teste
vive. Isto é o que a SDD vai consolidar em "Critérios de aceite" — se
faltar aqui, a SDD tem que inventar na hora.

| Contrato/RF | Tipo de teste | Mock? | Arquivo de teste |
|---|---|---|---|

## Times consumidores impactados
## Plano de implementação
Cada item do plano cita arquivo(s) exato(s) a criar/alterar — nunca "no
módulo de X" sem apontar o caminho.
## Riscos operacionais e mitigação
## Plano de rollout / rollback
## Observabilidade (métricas, logs, alertas)

## Documentos originados
| ID | Tipo | Título | Status |
|---|---|---|---|
| | | | |

## Autorevisão antes de status `in_review`
- [ ] Todo contrato tem assinatura/schema exato e arquivo/módulo (onde).
- [ ] Todo RF do PRD relevante tem tratamento de erro mapeado aqui.
- [ ] Nenhum placeholder ou "seguir padrão" sem apontar o arquivo padrão.
- [ ] Nenhum `NEEDS CLARIFICATION` pendente sem resposta.
- [ ] Estratégia de teste cobre todo contrato listado acima.
