<!--
  Copie este arquivo para .github/copilot-instructions.md na raiz do
  repositório DO PROJETO (não do repositório central do framework).
  Implementa as mesmas regras de _framework/rules/workflow-rules.yaml e
  _framework/prompts/universal.md.
-->
# Framework de Documentação & Rastreabilidade para IA (v1.7.0)

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
- Antes de mover a SDD de `draft` para `in_review`, rode a autorrevisão
  do rodapé do template: todo critério de aceite verificável por comando
  executável, todo item técnico apontando arquivo/módulo concreto,
  nenhum placeholder ("TBD", "tratar erros apropriadamente", "seguir o
  padrão do projeto" sem nomear o arquivo), e ambiguidade real marcada
  como `NEEDS CLARIFICATION` em vez de suposta — a SDD não vai a
  `approved` com essa marcação pendente. Ver `gate_content_quality`,
  `_framework/rules/workflow-rules.yaml` seção 15.

## Antes de gerar código (gate obrigatório, não opcional)
Verifique se existe uma SDD `approved`/`implemented` em `docs/sdd/` para
a feature em questão. **Se não existir, NÃO implemente** — mesmo que
você consiga ver um ADR ou PRD/Tech Spec referenciado em outro lugar,
ou até o próprio pedido pareça claro o suficiente para começar. Avise o
usuário que falta a SDD (e, se for o caso, o PRD/Tech Spec de origem no
repositório central) e peça para ela ser criada/compilada primeiro — um
ADR com "Consequências" detalhada não é especificação suficiente (ver
`_framework/rules/workflow-rules.yaml`, seção 13,
`gate_implementation_before_code`). Só prossiga sem SDD se o usuário
confirmar explicitamente que quer pular o gate, sabendo que está
violando a regra.

Se a SDD referenciar um ADR/PRD/Tech Spec e você precisar de mais
contexto, siga a `url` em `source_docs` até o repositório central — não
tente adivinhar o conteúdo.

## Antes de commitar código (gate obrigatório, não opcional)
Nunca commite implementação direto na branch main/master deste
repositório. Antes do primeiro commit:
1. Se a branch atual for main/master, crie uma branch nova a partir dela
   (nome rastreável ao id do documento, ex.:
   `feat/ADR-EVM-0011-controle-estoque`, `sdd/SDD-EVM-0009`).
2. Commite nessa branch, nunca em main.
3. Leve o resultado a main por PR, referenciando os ids relacionados
   (RFC/ADR/PRD/TS/SDD) no corpo — não faça merge do PR sozinho sem
   sinal do humano responsável, salvo instrução explícita em contrário.

Ver `_framework/rules/workflow-rules.yaml`, seção 14,
`gate_branch_before_commit`. Só commite direto em main se o usuário
confirmar explicitamente que quer pular o gate, sabendo que está
violando a regra (reduz revisão e quebra o uso de CI/CD).

## Antes de marcar a SDD como `implemented` (gate obrigatório)
Não marque `implemented` de memória. Confirme: todo requisito consolidado
da SDD tem código correspondente; todo arquivo tocado pela implementação
está listado na SDD (arquivo fora da lista é escopo não registrado —
atualize a SDD — ou scope creep — remova antes do commit, nunca em
silêncio); nenhuma abstração/dependência extra sem requisito na SDD; a
tabela "Evidência de verificação" preenchida com comando+saída reais
desta sessão para cada critério de aceite. Ver `gate_scope_verification`,
`_framework/rules/workflow-rules.yaml` seção 16 (repositório central).

## Handover ao trocar de sessão/agente
Ao terminar o planejamento antes de outra sessão implementar, ou perto de
~45% de uso de contexto com trabalho pela frente: gere `HANDOFF.md` na
raiz deste repositório (seções fixas: Goal, Status, Ids relacionados,
Files touched, Key decisions, Open threads/blockers, Next step, Don't
do), referenciando ids (SDD-X, TS-X, PRD-X) em vez de reescrever
conteúdo — a próxima sessão lê os documentos originais quando precisar de
detalhe. Ver `handover_protocol`, `_framework/rules/workflow-rules.yaml`
seção 17.

## O que NÃO fazer aqui
Não crie Strategy Doc, RFC, ADR, PRD ou Tech Spec neste repositório —
esses tipos pertencem ao repositório central, onde passam pelo gate de
decisão RFC→ADR (5 critérios objetivos — ver
`_framework/rules/workflow-rules.yaml`). Se o pedido for para um projeto
que nunca usou o framework antes, o processo é outro (onboarding, ver
`_framework/prompts/onboarding-bootstrap.md` no repositório central) —
não invente um atalho aqui.

## Auditoria de aderência (commits/PRs x registry)
A adesão de todo o time a referenciar documentos em commits/PRs nunca
pode ser garantida — este repositório vai acumular commits sem nenhum id
do framework, e isso é esperado, não uma falha a corrigir com CI. Se
pedirem para auditar aderência ou "ver se os commits têm documento por
trás", use `_framework/prompts/framework-audit.md` (repositório central)
— é diagnóstico sob demanda, nunca um gate de merge. Script de apoio:
`_framework/scripts/registry_tools.py audit <git_log_file> <docs_dir...>`.

Regras completas: `_framework/rules/workflow-rules.yaml` (repositório
central).
