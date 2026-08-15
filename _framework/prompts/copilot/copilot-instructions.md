<!--
  Copie este arquivo para .github/copilot-instructions.md na raiz do
  repositório DO PROJETO (não do repositório central do framework).
  Implementa as mesmas regras de _framework/rules/workflow-rules.yaml e
  _framework/prompts/universal.md.
-->
# Framework de Documentação & Rastreabilidade para IA (v1.1.0)

Este repositório de código é o **repositório de projeto** dentro de um
modelo de dois repositórios: um **repositório central** guarda Strategy
Doc, RFC, ADR, PRD e Tech Spec de todos os projetos (histórico
institucional de decisões); este repositório de projeto guarda apenas as
SDDs, em `docs/sdd/`, porque é o único documento pensado para orientar a
IA no momento de implementar.

## Ao trabalhar com `docs/sdd/`
- Use `templates/sdd.template.md` (do kit `_framework/` do repositório
  central) para criar uma SDD nova. IDs seguem `{TYPE}-{PROJECT_CODE}-{SEQ4}`
  (ex.: `SDD-CHECKOUT-0003`), sequenciais dentro deste repositório.
- Front-matter obrigatório: `id, type, title, status, project, owner,
  created, updated, relates_to, supersedes, superseded_by, tags`, mais
  `source_docs` (lista de `{id, url}` apontando para o PRD/TS/ADR de
  origem no repositório central — a url é obrigatória, pois esses
  documentos não estão neste repositório), `ai_targets` e
  `consumption_instructions`.
- Status: `draft → in_review → approved → implemented|rejected|superseded
  → archived`. Atualize `docs/sdd/registry.yaml` junto com qualquer
  criação ou mudança de status — front-matter e registry nunca podem
  divergir.

## Antes de gerar código
Verifique se existe uma SDD `approved` em `docs/sdd/` para a feature em
questão. Se não existir, avise o usuário em vez de implementar sem
spec. Se a SDD referenciar um ADR/PRD/Tech Spec e você precisar de mais
contexto, siga a `url` em `source_docs` até o repositório central — não
tente adivinhar o conteúdo.

## O que NÃO fazer aqui
Não crie Strategy Doc, RFC, ADR, PRD ou Tech Spec neste repositório —
esses tipos pertencem ao repositório central, onde passam pelo gate de
decisão RFC→ADR (5 critérios objetivos — ver
`_framework/rules/workflow-rules.yaml`). Se o pedido for para um projeto
que nunca usou o framework antes, o processo é outro (onboarding, ver
`_framework/prompts/onboarding-bootstrap.md` no repositório central) —
não invente um atalho aqui.

Regras completas: `_framework/rules/workflow-rules.yaml` (repositório
central).
