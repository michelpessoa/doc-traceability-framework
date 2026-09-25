# Mapa de seções do workflow-rules.yaml

Gerado por `render_indexes.py` — não edite à mão. Ids `§N` = numeração dos banners do YAML.
YAML: 91181 bytes; mapa + maior seção: 12520 (13.7% de 15%)
Total: 22 seções

| § | Seção | Chaves | Linhas | Bytes | Resumo |
|---|---|---|---|---|---|
| §0 | preâmbulo | `framework` | 1-191 | 11135 | Cabeçalho e bloco `framework:` (versão e changelog) |
| §1 | TOPOLOGIA DE REPOSITÓRIOS (MODELO MULTI-REPO) | `repository_topology` | 193-245 | 3318 | Este framework assume DOIS tipos de repositório git, nunca um só: |
| §2 | TIPOS DE DOCUMENTO | `document_types` | 247-369 | 5443 | TIPOS DE DOCUMENTO |
| §3 | FLUXO PRINCIPAL (TO-BE) E GATE DE… | (nenhuma) | 371-383 | 686 | Fluxo textual: Strategy Doc -> RFC -> [GATE: exige ADR?] -> sim: ADR -> PRD + Tech Spec -> SDD (no… |
| §3b | TIPOS LEGADOS — não fazem parte do fluxo, mas con… | `legacy_document_types` | 385-428 | 1975 | TIPOS LEGADOS — não fazem parte do fluxo, mas continuam válidos |
| §3c | ARTEFATOS OPERACIONAIS — arquivos que o frame… | `operational_artifacts` +1 | 430-505 | 4302 | ARTEFATOS OPERACIONAIS — arquivos que o framework manda criar e que |
| §4 | ONBOARDING DE PROJETO JÁ… | `onboarding` | 507-564 | 3373 | Aplica-se quando um projeto que já tem código em produção, sem nenhum documento deste framework, pr… |
| §5 | INCIDENTES E POST… | `incident_lifecycle` +3 | 566-631 | 3594 | Incidentes não seguem o ciclo de vida padrão (draft/review/approved) — são eventos operacionais,… |
| §6 | CICLO DE VIDA DE STATUS PADRÃO (STRAT, RFC, ADR, P… | `status_lifecycle` | 633-657 | 1525 | CICLO DE VIDA DE STATUS PADRÃO (STRAT, RFC, ADR, PRD, TS, SDD, BASE, PM) |
| §7 | ESQUEMA DE ID | `id_scheme` | 659-668 | 726 | ESQUEMA DE ID |
| §8 | METADADOS (FRONT-MATTER) — TODO documento começa… | `frontmatter_schema` | 670-727 | 3614 | METADADOS (FRONT-MATTER) — TODO documento começa com este bloco YAML |
| §9 | REGISTRY (RASTREABILIDADE) | `registry` | 729-785 | 3257 | REGISTRY (RASTREABILIDADE) |
| §10 | REUSO MULTI-PROJETO | `multi_project` | 787-813 | 1668 | REUSO MULTI-PROJETO |
| §11 | AUDITORIA DE ADERÊNCIA (COMM… | `audit` | 815-883 | 5108 | O framework NUNCA assume que todo commit/PR nasce de um documento aprovado — na prática sempre exis… |
| §12 | CAPACIDADES QUE QUALQUER FERRAMENTA DE IA (CLAUDE, CURSOR, C… | `capabilities` | 885-983 | 8733 | CAPACIDADES QUE QUALQUER FERRAMENTA DE IA (CLAUDE, CURSOR, COPILOT, |
| §13 | GATE OBRIGATÓRIO:… | `gate_implementation_before_code` | 985-1072 | 5802 | Motivação (registrado para não se perder): este gate foi adicionado depois de um in… |
| §14 | GATE OBRIGATÓRIO:… | `gate_branch_before_commit` | 1074-1131 | 3711 | Origem: mesmo incidente EVM da seção 13 — com PRD/TS/SDD já no lugar, o código ainda… |
| §15 | GATE OBRIGATÓRIO:… | `gate_content_quality` | 1133-1225 | 6205 | Motivação: os gates 13/14 garantem ORDEM (documento antes de código, branch antes de commit)… |
| §16 | GATE OBRIGATÓRIO: VERIFICAÇÃO DE ESCOPO ANTES DE… | `gate_scope_verification` | 1227-1319 | 6281 | Motivação: gate 13 garante que a SDD existe antes do código. |
| §17 | SKILL DE TRANSFERÊN… | `handover_protocol` | 1321-1377 | 3710 | Motivação: o fluxo deste framework frequentemente separa quem planeja (compila PRD/TS/SDD) de q… |
| §18 | LIÇÕES LOCAIS E CON… | `lessons_policy` | 1379-1435 | 3563 | Motivação: entre a v1.4.0 e a v1.7.0 — duas semanas — cada falha de execução de um agente vi… |
| §19 | SIZING: A PROFUNDIDADE DO F… | `sizing` | 1437-1495 | 3452 | Motivação: até a v1.7.0 o funil era fixo — toda mudança atravessava STRAT, RFC, ADR, PRD, TS e SDD. |
