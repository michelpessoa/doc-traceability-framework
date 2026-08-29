---
id: SPEC-{PROJECT_CODE}-{SEQ}
type: SPEC
title: "{Título do que será construído}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
parent_rfc: null   # id da RFC de origem, ou null se o sizing dispensou RFC
parent_adr: null   # id do ADR, ou null se o gate dispensou ADR
sizing: "{small | medium | large | complex}"   # ver sizing em workflow-rules.yaml
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> SPEC substitui o par PRD + Tech Spec, que eram dois documentos com o
> mesmo autor, o mesmo parent e frequentemente o mesmo título. A parte de
> **requisito** garante o O QUÊ; a parte de **desenho** garante o COMO e o
> ONDE. Ambas em um arquivo só, porque separá-las nunca produziu revisão
> separada.
>
> Proibido placeholder ("TBD", "definir depois", "ajustar conforme
> necessário", "seguir o padrão do projeto" sem nomear o arquivo padrão).
> Ambiguidade real vira `[NEEDS CLARIFICATION: pergunta objetiva]` em vez
> de suposição silenciosa. Documento não vai a `approved` com marcador
> pendente.

## Objetivo

## Usuários / personas afetadas

---

# Parte 1 — Requisito (o QUÊ)

## Requisitos funcionais
Cada requisito tem **RF-ID próprio** e critério de aceite verificável
objetivamente (número, condição, valor esperado) — não "deve funcionar
bem", e não um bucket solto de critérios no fim do documento.

| RF-ID | Requisito | Critério de aceite |
|---|---|---|
| RF01 | | |

## Casos de borda / condições de erro
Todo caminho de falha ou condição-limite relevante a algum RF acima,
explícito: entrada inválida, dado ausente, permissão negada, concorrência,
limite de tamanho/volume. Descrição genérica de tratamento de erro não
conta como caso de borda.

| Caso | RF relacionado | Comportamento esperado |
|---|---|---|
| | | |

## Requisitos não funcionais

## Fora de escopo
O que esta SPEC explicitamente NÃO cobre — é o que protege a implementação
de crescer "enquanto está ali".

---

# Parte 2 — Desenho (o COMO e o ONDE)

## Visão geral da solução

## Contratos técnicos (APIs, eventos, schemas)
Para cada contrato: nome exato de função/endpoint/evento, assinatura ou
schema completo (tipos de entrada e saída) e **onde vive** (arquivo ou
módulo, com caminho). Prosa livre do tipo "no serviço de X" não é
contrato.

**Consumes** (o que espera de código/dados já existentes — nomes e tipos
exatos):

**Produces** (o que entrega para quem consumir depois — nomes e tipos
exatos):

## Tratamento de erro por contrato
| Caso | RF relacionado | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| | | | |

## Estratégia de teste
Cada critério de aceite da Parte 1 precisa de um teste que o verifique, e
o teste deriva do critério — nunca espelha a implementação. É isto que a
SDD consolida; se faltar aqui, a SDD inventa na hora.

| RF-ID / contrato | Tipo de teste | Mock? | Arquivo de teste |
|---|---|---|---|
| | | | |

## Plano de implementação
Cada item cita o(s) arquivo(s) exato(s) a criar ou alterar.

## Riscos operacionais e mitigação

## Plano de rollout / rollback

## Observabilidade (métricas, logs, alertas)

## Times consumidores impactados

---

## Dependências
Referenciar `parent_rfc` e `parent_adr` quando aplicável, e qualquer
dependência operacional (acesso, ambiente, terceiro).

## Documentos originados
| ID | Tipo | Título | Status |
|---|---|---|---|
| | | | |

## Autorrevisão antes de status `in_review`
Rode como último passo antes de propor a mudança de status. Checagem
mecânica equivalente: `python3 _framework/scripts/validate_doc.py <este arquivo>`.

- [ ] Todo requisito tem RF-ID próprio e critério de aceite verificável.
- [ ] Todo contrato tem assinatura/schema exato e arquivo/módulo (onde).
- [ ] Todo RF tem tratamento de erro mapeado na Parte 2.
- [ ] Todo critério de aceite tem teste correspondente na estratégia de teste.
- [ ] Nenhum placeholder e nenhum marcador de ambiguidade pendente.
- [ ] Nomes de contrato consistentes entre as seções (`criarPedido` numa
      seção e `criarNovoPedido` noutra é bug de documento, não estilo).
- [ ] "Fora de escopo" preenchido, não deixado vazio por omissão.
