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
Cada item vem do RF/critério do PRD e do contrato/caso de erro do Tech
Spec — não invente critério novo aqui, consolide o que já existe a
montante. Todo item tem que ser verificável por comando executável, não
por leitura de código.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|

## Instruções específicas para a IA implementadora
Instruções objetivas — arquivos/módulos esperados, padrões de código a
seguir, testes obrigatórios, o que NÃO alterar.

## Verificação de escopo (nada a mais, nada a menos)
Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima tem código correspondente (nada
      do PRD/TS ficou de fora).
- [ ] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada" ou "Instruções específicas" — se a
      implementação tocou um arquivo não listado aqui, ou é escopo que
      faltou registrar na SDD (atualize-a) ou é scope creep a remover
      antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado ("já que estava ali").

## Evidência de verificação (preencher antes de status `implemented`)
Para cada critério da tabela acima, comando rodado de fato nesta sessão e
saída real — não "deve passar" nem resultado de memória. Sem isto, status
não pode avançar para `implemented`.

| # | Comando rodado | Saída (resumo) | Passou? |
|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | {lista de ids} |
| ai_targets | {lista de ferramentas} |
