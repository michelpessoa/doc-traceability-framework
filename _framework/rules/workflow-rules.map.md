# Mapa de seções do workflow-rules.yaml

Gerado por `render_indexes.py` — não edite à mão. Ids `§N` = numeração dos banners do YAML.
YAML: 91557 bytes; mapa + maior seção: 12493 (13.6% de 15%)
Total: 22 seções

| § | Seção | Chaves | Linhas | Bytes | Resumo |
|---|---|---|---|---|---|
| §0 | preâmbulo | `framework` | 1-201 | 11658 | Cabeçalho e bloco `framework:` (versão e changelog) |
| §1 | TOPOLOGIA DE REPOSITÓRIOS (MODELO MULTI-REPO) | `repository_topology` | 203-255 | 3321 | Este framework assume DOIS tipos de repositório git, nunca um só: |
| §2 | TIPOS DE DOCUMENTO | `document_types` | 257-379 | 5422 | TIPOS DE DOCUMENTO |
| §3 | FLUXO PRINCIPAL (TO-BE) E GATE DE… | (nenhuma) | 381-393 | 655 | Fluxo textual: Strategy Doc -> RFC -> [GATE: exige ADR?] -> sim: ADR -> SPEC -> SDD (no repo do pro… |
| §3b | TIPOS LEGADOS — não fazem parte do fluxo, mas con… | `legacy_document_types` | 395-438 | 1975 | TIPOS LEGADOS — não fazem parte do fluxo, mas continuam válidos |
| §3c | ARTEFATOS OPERACIONAIS — arquivos que o frame… | `operational_artifacts` +1 | 440-515 | 4295 | ARTEFATOS OPERACIONAIS — arquivos que o framework manda criar e que |
| §4 | ONBOARDING DE PROJETO JÁ… | `onboarding` | 517-574 | 3347 | Aplica-se quando um projeto que já tem código em produção, sem nenhum documento deste framework, pr… |
| §5 | INCIDENTES E POST… | `incident_lifecycle` +3 | 576-641 | 3594 | Incidentes não seguem o ciclo de vida padrão (draft/review/approved) — são eventos operacionais,… |
| §6 | CICLO DE VIDA DE STATUS PADRÃO (STRAT, RFC, ADR, P… | `status_lifecycle` | 643-667 | 1525 | CICLO DE VIDA DE STATUS PADRÃO (STRAT, RFC, ADR, PRD, TS, SDD, BASE, PM) |
| §7 | ESQUEMA DE ID | `id_scheme` | 669-678 | 726 | ESQUEMA DE ID |
| §8 | METADADOS (FRONT-MATTER) — TODO documento começa… | `frontmatter_schema` | 680-737 | 3614 | METADADOS (FRONT-MATTER) — TODO documento começa com este bloco YAML |
| §9 | REGISTRY (RASTREABILIDADE) | `registry` | 739-795 | 3257 | REGISTRY (RASTREABILIDADE) |
| §10 | REUSO MULTI-PROJETO | `multi_project` | 797-823 | 1668 | REUSO MULTI-PROJETO |
| §11 | AUDITORIA DE ADERÊNCIA (COMM… | `audit` | 825-893 | 5099 | O framework NUNCA assume que todo commit/PR nasce de um documento aprovado — na prática sempre exis… |
| §12 | CAPACIDADES QUE QUALQUER FERRAMENTA DE IA (CLAUDE, CURSOR, C… | `capabilities` | 895-993 | 8704 | CAPACIDADES QUE QUALQUER FERRAMENTA DE IA (CLAUDE, CURSOR, COPILOT, |
| §13 | GATE OBRIGATÓRIO:… | `gate_implementation_before_code` | 995-1082 | 5802 | Motivação (registrado para não se perder): este gate foi adicionado depois de um in… |
| §14 | GATE OBRIGATÓRIO:… | `gate_branch_before_commit` | 1084-1141 | 3705 | Origem: mesmo incidente EVM da seção 13 — com PRD/TS/SDD já no lugar, o código ainda… |
| §15 | GATE OBRIGATÓRIO:… | `gate_content_quality` | 1143-1235 | 6196 | Motivação: os gates 13/14 garantem ORDEM (documento antes de código, branch antes de commit)… |
| §16 | GATE OBRIGATÓRIO: VERIFICAÇÃO DE ESCOPO ANTES DE… | `gate_scope_verification` | 1237-1329 | 6281 | Motivação: gate 13 garante que a SDD existe antes do código. |
| §17 | SKILL DE TRANSFERÊN… | `handover_protocol` | 1331-1387 | 3698 | Motivação: o fluxo deste framework frequentemente separa quem planeja (compila SPEC/SDD) de quem… |
| §18 | LIÇÕES LOCAIS E CON… | `lessons_policy` | 1389-1445 | 3563 | Motivação: entre a v1.4.0 e a v1.7.0 — duas semanas — cada falha de execução de um agente vi… |
| §19 | SIZING: A PROFUNDIDADE DO F… | `sizing` | 1447-1505 | 3452 | Motivação: até a v1.7.0 o funil era fixo — toda mudança atravessava STRAT, RFC, ADR, PRD, TS e SDD. |
