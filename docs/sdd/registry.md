# Registry — Projeto DTF

_Gerado automaticamente a partir de `registry.yaml` em 2026-09-04 20:59. Não editar manualmente. Framework v2.1.0._

Total de documentos: **16**


## SDD (16)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `SDD-DTF-0001` | Superfície de entrada: AGENTS.md, QUICKSTART.md e expurgo de PRD/TS | approved | Michel Pessoa | 2026-08-29 | SPEC-DTF-0001, ADR-DTF-0001 |
| `SDD-DTF-0002` | Modo greenfield: registry sem repositório de código e textos de entrada | implemented | Michel Pessoa | 2026-09-04 | SPEC-DTF-0002, SDD-DTF-0001 |
| `SDD-DTF-0003` | Datação das exigências do gate 16 em validate_state.py | implemented | Michel Pessoa | 2026-09-04 | SPEC-DTF-0003 |
| `SDD-DTF-0004` | Exclusão de artefatos operacionais na varredura de documentos | implemented | Michel Pessoa | 2026-09-04 | SPEC-DTF-0005 |
| `SDD-DTF-0005` | Porta de entrada única e documentação gerada | implemented | Michel Pessoa | 2026-09-04 | SPEC-DTF-0004, ADR-DTF-0001 |
| `SDD-DTF-0006` | Memória portável: procedimentos neutros e capacidades por contrato | implemented | Michel Pessoa | 2026-08-29 | SPEC-DTF-0001, ADR-DTF-0001 |
| `SDD-DTF-0007` | Adaptadores por fornecedor gerados integralmente | implemented | Michel Pessoa | 2026-08-29 | SPEC-DTF-0001, ADR-DTF-0001, SDD-DTF-0006 |
| `SDD-DTF-0008` | Fim da duplicação manual e cobertura de renderizações | implemented | Michel Pessoa | 2026-08-29 | SPEC-DTF-0001, ADR-DTF-0001, SDD-DTF-0006, SDD-DTF-0007 |
| `SDD-DTF-0009` | Mecanização de capacidades: hooks, agent e command gerados por fornecedor | implemented | Michel Pessoa | 2026-09-03 | SDD-DTF-0007, SDD-DTF-0006 |
| `SDD-DTF-0010` | Fecha lacuna do harness score: skills expostas + teste real prometido em SDD-DTF-0009 | implemented | Michel Pessoa | 2026-09-03 | SDD-DTF-0009 |
| `SDD-DTF-0011` | Linter (ruff) para os scripts Python do kit público | implemented | Michel Pessoa | 2026-09-04 | SDD-DTF-0009, SDD-DTF-0010 |
| `SDD-DTF-0012` | Adiciona .env ao .gitignore do kit público | implemented | Michel Pessoa | 2026-09-03 | — |
| `SDD-DTF-0013` | Tooling de dev completo no kit público: test runner declarado, typecheck, formatter, pre-commit framework | implemented | Michel Pessoa | 2026-09-03 | SDD-DTF-0011 |
| `SDD-DTF-0014` | Lockfile de dependências dev + config de formatter explícita | implemented | Michel Pessoa | 2026-09-04 | SDD-DTF-0013 |
| `SDD-DTF-0015` | Consolida config do ruff em pyproject.toml (sensor de formatter só olha lá) | implemented | Michel Pessoa | 2026-09-04 | SDD-DTF-0014 |
| `SDD-DTF-0016` | RULE_SINCE por data de criação do documento, não por framework_version do registry | draft | Michel Pessoa | 2026-09-04 | — |
