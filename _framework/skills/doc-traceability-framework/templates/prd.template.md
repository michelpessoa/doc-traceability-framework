---
id: PRD-{PROJECT_CODE}-{SEQ}
type: PRD
title: "{Título do requisito de produto}"
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

> ⚠️ **Template legado.** PRD foi fundido em `SPEC` na v2.0.0 —
> use `spec.template.md` para trabalho novo. Este arquivo existe para
> projetos mapeados sob 1.x, que não migram
> (`lessons_policy.non_retroactive`).

# {Título}

> PRD garante o **O QUÊ**: cada requisito abaixo precisa do seu próprio
> critério de aceite verificável (não um bucket solto de "critérios" no
> fim). Proibido preencher com placeholder — "TBD", "definir depois",
> "critério óbvio" não são aceitos; se não sabe ainda, marque
> `[NEEDS CLARIFICATION: pergunta objetiva]` em vez de inventar. Um PRD
> `approved` com marcador `NEEDS CLARIFICATION` pendente é contraditório —
> resolva antes de aprovar.

## Objetivo
## Usuários / personas afetadas

## Requisitos funcionais
Cada requisito é uma linha com **RF-ID**, comportamento e critério de
aceite próprio — verificável objetivamente (número, condição, valor
esperado), não "deve funcionar bem".

| RF-ID | Requisito | Critério de aceite |
|---|---|---|
| RF01 | | |

## Casos de borda / condições de erro
Todo caminho de falha ou condição-limite relevante a algum RF acima,
explícito (não "tratar erros apropriadamente"): entrada inválida, dado
ausente, permissão negada, concorrência, limite de tamanho/volume.

| Caso | RF relacionado | Comportamento esperado |
|---|---|---|
| | | |

## Requisitos não funcionais
## Fora de escopo
(O que este PRD explicitamente NÃO cobre — protege contra a implementação
adicionar algo "enquanto está ali".)

## Critérios de aceite gerais
(Só o que não pertence a nenhum RF específico — ex.: critério de release
como um todo. A maioria dos critérios deve estar na tabela de Requisitos
funcionais, não aqui.)

## Dependências
(Referenciar `parent_rfc` e `parent_adr` quando aplicável.)

## Documentos originados
| ID | Tipo | Título | Status |
|---|---|---|---|
| | | | |

## Autorevisão antes de status `in_review`
- [ ] Todo RF tem RF-ID e critério de aceite próprio, verificável.
- [ ] Nenhum placeholder (`TBD`, "tratar apropriado", "critério óbvio").
- [ ] Nenhum `NEEDS CLARIFICATION` pendente sem resposta.
- [ ] "Fora de escopo" preenchido — não deixado vazio por omissão.
