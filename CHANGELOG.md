# Changelog

Este projeto segue versionamento semântico. Ver `framework.version` em
`_framework/rules/workflow-rules.yaml` como fonte da verdade da versão
atual.

## [Unreleased]
- Especificação convertida de `.docx` para
  `Framework_Documentacao_Rastreabilidade_v1.1.md` (documento nativo do
  repositório, sem dependência de Word).

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
