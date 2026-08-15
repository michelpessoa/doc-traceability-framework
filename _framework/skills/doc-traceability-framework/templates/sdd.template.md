---
id: SDD-{PROJECT_CODE}-{SEQ}
type: SDD
title: "{Título — o que será implementado}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
# source_docs: PRD, Tech Spec e ADR (se houver) que originaram esta SDD.
# Este documento vive no repositório do PROJETO, mas PRD/TS/ADR vivem no
# repositório CENTRAL — por isso cada entrada precisa do id E da url
# completa (sem isso a rastreabilidade quebra ao atravessar repositórios).
source_docs:
  - id: "{ex: PRD-PROJETO-0001}"
    url: "{URL completa do arquivo no repositório central}"
  - id: "{ex: TS-PROJETO-0001}"
    url: "{URL completa do arquivo no repositório central}"
ai_targets: []            # ex: [claude-code, cursor, copilot]
consumption_instructions: "{como uma IA deve usar este documento antes de implementar}"
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar. Deve ser autocontido o
> suficiente para que uma IA implemente corretamente sem precisar ler
> todos os documentos de origem, mas sempre rastreável a eles via
> `source_docs` (id + url, já que os documentos de origem estão em outro
> repositório).

## Resumo executivo
O que será construído e por quê (1 parágrafo).

## Decisão(ões) de arquitetura aplicável(is)
(Resumo do(s) ADR em `source_docs`, se houver. Se não houver ADR, declarar
explicitamente "Sem ADR — RFC dispensou decisão arquitetural via gate".)

## Requisitos consolidados
(Consolidado do PRD.)

## Especificação técnica consolidada
(Consolidado do Tech Spec: contratos, plano de implementação, rollout.)

## Critérios de aceite / definição de pronto
## Instruções específicas para a IA implementadora
Instruções objetivas — arquivos/módulos esperados, padrões de código a
seguir, testes obrigatórios, o que NÃO alterar.

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | {lista de ids} |
| ai_targets | {lista de ferramentas} |
