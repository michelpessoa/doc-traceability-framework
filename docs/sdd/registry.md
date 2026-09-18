# Registry — Projeto DTF

_Gerado automaticamente a partir de `registry.yaml` em 2026-09-17 22:06. Não editar manualmente. Framework v2.1.0._

Total de documentos: **30**


## SDD (30)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `SDD-DTF-0001` | Superfície de entrada: AGENTS.md, QUICKSTART.md e expurgo de PRD/TS | implemented | Michel Pessoa | 2026-09-15 | SPEC-DTF-0001, ADR-DTF-0001 |
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
| `SDD-DTF-0016` | RULE_SINCE por data de criação do documento, não por framework_version do registry | implemented | Michel Pessoa | 2026-09-08 | — |
| `SDD-DTF-0017` | QUICKSTART e guia não-técnico ficam consistentes sobre os 4 níveis de sizing | implemented | Michel Pessoa | 2026-09-08 | — |
| `SDD-DTF-0018` | validate_state: não retroatividade por data de criação e checagem de evidência por coluna | implemented | Michel Pessoa | 2026-09-14 | SDD-DTF-0016 |
| `SDD-DTF-0019` | verify-sdd: a tabela de evidência vive na SDD e a checagem mecânica na SDD verificada vira passo obrigatório | implemented | Michel Pessoa | 2026-09-14 | SDD-DTF-0018 |
| `SDD-DTF-0020` | Hooks do harness que alcançam o modelo: SessionStart por stdout, PostToolUse por exit 2 e sensor de configuração | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0009, SDD-DTF-0018, SDD-DTF-0019 |
| `SDD-DTF-0021` | Guardrails sem falso positivo: guard_bash por subcomando e check_commit ignorando merge real | implemented | Michel Pessoa | 2026-09-14 | SDD-DTF-0009, SDD-DTF-0020 |
| `SDD-DTF-0023` | Varredura dos validadores em repositório de projeto: validation-*.md como artefato operacional e --auto sem node_modules nem worktrees | implemented | Michel Pessoa | 2026-09-14 | SDD-DTF-0019 |
| `SDD-DTF-0024` | table_with_header não conta linha de bloco cercado como linha de tabela | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0018 |
| `SDD-DTF-0025` | test_discover: fixture discrimina poda de worktrees fora de .claude/ e descida em .git | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0023 |
| `SDD-DTF-0026` | verify-sdd: sensor de mutação sem git stash compartilhado e diff ancorado em SHA fixo, não em origin/main | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0019, SDD-DTF-0023 |
| `SDD-DTF-0027` | check_hooks: tokenizar command com shlex pra aceitar variantes de shell de ${CLAUDE_PROJECT_DIR} | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0020 |
| `SDD-DTF-0028` | test_validate_state: tabela real depois de bloco cercado fechado discrimina mutação em in_fence | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0024 |
| `SDD-DTF-0029` | test_check_hooks: token com prefixo de variável falso (substring, não prefixo válido) continua reprovado | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0027 |
| `SDD-DTF-0030` | Paralelismo derivado: campo arquivos por RF, tabela de tasks na SDD, script parallel_plan.py | implemented | Michel Pessoa | 2026-09-15 | — |
| `SDD-DTF-0031` | check_ears confunde coluna Arquivos com critério em SPEC de 4 colunas | implemented | Michel Pessoa | 2026-09-15 | SDD-DTF-0030 |
