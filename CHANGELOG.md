# Changelog

Este projeto segue versionamento semântico. Ver `framework.version` em
`_framework/rules/workflow-rules.yaml` como fonte da verdade da versão
atual.

## [1.7.0] - 2026-08-29
- Gate de qualidade de conteúdo (seção 15 de `workflow-rules.yaml`): os
  gates anteriores garantiam ORDEM (documento antes de código, branch
  antes de commit), nenhum garantia que o CONTEÚDO de PRD/Tech Spec/SDD
  fosse específico o bastante para implementação sem ambiguidade.
  Templates de PRD e Tech Spec ganham granularidade (requisito↔critério
  1:1 com RF-ID, contratos com Consumes/Produces e arquivo/módulo exato,
  casos de borda explícitos), marcador `NEEDS CLARIFICATION` para não
  supor em silêncio, e autorrevisão obrigatória antes de `in_review`.
- Gate de verificação de escopo (seção 16): antes de uma SDD virar
  `implemented`, é obrigatório conferir que todo requisito consolidado
  tem código, que todo arquivo tocado está listado na SDD (nada a mais,
  nada a menos), e preencher a tabela de evidência com comando + saída
  reais da sessão — checklist marcado de memória não conta.
- Protocolo de handover/pickup (seção 17) e duas skills novas
  (`_framework/skills/handover/`, `_framework/skills/pickup/`): passagem
  de contexto padronizada entre a sessão que planeja (PRD/TS/SDD) e a
  que implementa, via `HANDOFF.md` de seções fixas que referencia ids do
  framework em vez de reescrever conteúdo. Pensado para manter o agente
  implementador abaixo de ~45% de uso de contexto da sessão.
- Inspirações externas creditadas: autorrevisão contra placeholder e
  "evidência antes de afirmar conclusão" de github.com/obra/superpowers;
  formato de passagem de sessão de github.com/vmihalis/claude-handover —
  ambos adaptados ao modelo de dois repositórios deste framework, não
  copiados.
- Especificação narrada consolidada em um único
  `Framework_Documentacao_Rastreabilidade.md`, sem versão no nome, sempre
  na versão atual do framework: as cópias `_v1.1.md` e `_v1.2.md` foram
  removidas (paravam na v1.2.0 e nunca cobriram 1.3.0–1.7.0, então
  descreviam um framework que já não existia). O histórico de versões
  passa a viver só neste CHANGELOG, e o detalhe canônico de cada regra só
  em `workflow-rules.yaml`.

## [1.6.0] - 2026-08-25
- Gate obrigatório de branch antes de commit (seção 14 de
  `workflow-rules.yaml`): mesmo com PRD/TS/SDD no lugar, a implementação
  de um incidente real foi commitada direto em main, sem branch dedicada
  nem PR. Toda implementação coberta pelo framework passa a nascer em
  branch própria, com nome rastreável ao id de origem, e chega a main por
  PR referenciando os ids relacionados. Nova capability
  `enforce_branch_before_commit`.

## [1.5.0] - 2026-08-25
- Gate obrigatório de implementação (seção 13 de `workflow-rules.yaml`):
  corrige gap crítico em que uma sessão de IA implementou ADRs aprovados
  indo direto para o código, tratando "Consequências" do ADR como
  especificação suficiente — PRD/Tech Spec/SDD escritos depois,
  retroativamente. Nenhuma implementação pode começar antes de PRD/TS
  (central) e SDD (projeto) existirem. É gate de ordem, não de tempo.
  Nova capability `enforce_implementation_gate`.

## [1.4.0] - 2026-08-15
- Campo `repository` de nível de projeto no registry central
  (`docs/{PROJECT_CODE}/registry.yaml`), com a URL do repositório de
  código: antes, rodar uma auditoria dependia de alguém lembrar de
  informar o link toda vez. Onboarding passa a gravá-lo na Fase 1, e a
  auditoria passa a lê-lo primeiro em vez de assumir que foi informado.

## [1.3.0] - 2026-08-15
- Guia opcional de paralelização por trilhas de negócio
  (`_framework/guides/paralelizacao-trilhas.md`): uma skill por trilha,
  uma sessão de IA/pessoa por trilha, grafo de dependências entre
  trilhas. Não altera o fluxo principal nem cria tipo novo — é padrão de
  execução, não de decisão.

## [1.2.0] - 2026-08-15
- Auditoria de aderência (commits/PRs x registry): como a adesão de todo
  o time à convenção de referenciar documentos em commits nunca pode ser
  garantida, o framework passa a oferecer uma auditoria sob demanda (sem
  CI, sem bloqueio de merge) que cruza o histórico do repositório do
  projeto com os registries conhecidos e reaproveita o mecanismo de
  reconstrução do onboarding para o que for arquiteturalmente
  significativo. Novo prompt `prompts/framework-audit.md` e novo comando
  `registry_tools.py audit`.
- Especificação convertida de `.docx` para Markdown nativo do
  repositório (`Framework_Documentacao_Rastreabilidade_v1.2.md` — desde a
  v1.7.0 consolidada em `Framework_Documentacao_Rastreabilidade.md`, sem
  versão no nome).

## [1.1.0] - 2026-08-15
- Modelo explícito de dois repositórios (central + por projeto); SDD
  passa a viver no repositório do projeto, com `source_docs` carregando
  `{id, url}` para atravessar repositórios.
- Onboarding de projeto já existente: tipo `BASE` + ADRs reconstruídos
  (`provenance: reconstructed`), com revisão humana obrigatória.
- Fluxo de incidentes e postmortem: tipos `INC`/`PM`, ciclo de vida
  operacional próprio para incidentes, escala de severidade SEV1–SEV4,
  regra de recorrência de 90 dias, triagem de action items reaproveitando
  o gate RFC→ADR.
- Dois guias de uso adicionados (técnico e não técnico).

## [1.0.0] - 2026-08-15
- Fluxo Strategy Doc → RFC → [gate] → ADR (condicional) → PRD + Tech
  Spec → SDD.
- Gate de decisão RFC→ADR com 5 critérios objetivos (corrige o fluxo
  original, que exigia ADR sempre).
- SDD definida como artefato de input para ferramentas de IA de
  implementação.
- Esquema de ID, front-matter e registry central para rastreabilidade.
- Kit de templates versionado para reuso multi-projeto.
- Prompt universal + variantes Cursor/Copilot + Claude Skill, todos
  derivados da mesma fonte canônica (`workflow-rules.yaml`).
