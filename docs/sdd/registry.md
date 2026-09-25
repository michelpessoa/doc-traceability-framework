# Registry — Projeto DTF

_Gerado automaticamente a partir de `registry.yaml`. Não editar manualmente. Framework v2.3.2._

Total de documentos: **48**


## SDD (48)

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
| `SDD-DTF-0032` | Gate de CI do verify-sdd: presença+veredito+cobertura de RF-ID, cross-check de evidência e override de incidente validado contra o registry | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0033` | Despacho do verify-sdd: seção de autoridade no procedimento, coluna de rodada na evidência, teto mecanizado em validate_state.py | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0034` | SKILL.md principal: corrige inconsistências, cobre lacunas de cobertura e enxuga (itens 3-5 de STRAT-DTF-0003) | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0035` | Skills finas (handover/pickup/verify-sdd): checklist mínimo inline + itens A e G do tlc-spec-lean | implemented | Michel Pessoa | 2026-09-22 | SDD-DTF-0034 |
| `SDD-DTF-0036` | Evidência de verificação com file:line da asserção e perfil declarado por critério | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0037` | verify-sdd ganha passo 0: fidelidade da SDD a source_docs (SPEC/ADR de origem) | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0038` | Selftest dos validadores por mutação (selftest.py) + mecanização da contagem de recorrência de lições (lessons_check.py) | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0039` | Sweep de requisitos transversais na SPEC (item 10 de STRAT-DTF-0003) | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0040` | guia-tecnico.md: corrige drift acumulado (7 adições recentes nunca refletidas) | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0041` | workflow-rules.yaml: frontmatter_schema não lista SPEC (tipo ativo desde 2.0.0) | implemented | Michel Pessoa | 2026-09-22 | — |
| `SDD-DTF-0042` | Corrigir defasagens do kit: gate_implementation_before_code em SPEC, espelho do sdd.template.md e teste de paridade de templates | implemented | Michel Pessoa | 2026-09-25 | — |
| `SDD-DTF-0043` | Índices gerados do kit: INDEX.md, mapa de seções do YAML, INDEX de SDDs e sumários navegáveis | implemented | Michel Pessoa | 2026-09-25 | SDD-DTF-0042 |
| `SDD-DTF-0044` | Skills enxutas: SKILL.md roteador, references sob demanda, descriptions curtas e procedimentos por caminho estável | implemented | Michel Pessoa | 2026-09-25 | — |
| `SDD-DTF-0045` | Higiene de busca e CI: caches fora da árvore de busca e etapa de CI para índices e paridade | implemented | Michel Pessoa | 2026-09-25 | SDD-DTF-0043 |
| `SDD-DTF-0046` | Bundle da skill como artefato gerado: .gitattributes com linguist-generated e templates sincronizados por render_prompts.py | implemented | Michel Pessoa | 2026-09-25 | SDD-DTF-0042, SDD-DTF-0043, SDD-DTF-0045 |
| `SDD-DTF-0047` | Leitor de tabelas markdown trata pipe escapado como conteúdo de célula, com um único helper compartilhado | implemented | Michel Pessoa | 2026-09-25 | SDD-DTF-0024, SDD-DTF-0042, SDD-DTF-0044, SDD-DTF-0045 |
| `SDD-DTF-0048` | Fechar a defasagem PRD/Tech Spec do YAML do kit: fluxo, gates 14, 15 e 17, capabilities e teste de regressão | approved | Michel Pessoa | 2026-09-25 | SDD-DTF-0042 |
| `SDD-DTF-0049` | Título completo e resumo útil no mapa de seções e linhas específicas no INDEX do kit | approved | Michel Pessoa | 2026-09-25 | SDD-DTF-0043 |
