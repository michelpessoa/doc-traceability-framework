# Mapa de seções do workflow-rules.yaml

Gerado por `render_indexes.py` — não edite à mão. Ids `§N` = numeração dos banners do YAML.
YAML: 91181 bytes; mapa + maior seção: 12638 (13.9% de 15%)
Total: 22 seções

| § | Seção | Chaves | Linhas | Bytes | Resumo |
|---|---|---|---|---|---|
| §0 | preâmbulo | `framework` | 1-191 | 11135 | Cabeçalho e bloco `framework:` (versão e changelog) |
| §1 | TOPOLOGIA DE REPOSITÓRIOS (MODELO MULTI-REPO) | `repository_topology` | 193-245 | 3318 | Este framework assume DOIS tipos de repositório git, nunca um só |
| §2 | TIPOS DE DOCUMENTO | `document_types` | 247-369 | 5443 | Os oito tipos de documento: STRAT, RFC, ADR, SPEC, SDD, BASE, INC e PM, com pasta e repositório |
| §3 | FLUXO PRINCIPAL (TO-BE) E GATE DE DECISÃO | (nenhuma) | 371-383 | 686 | Fluxo textual: Strategy Doc -> RFC -> [GATE: exige ADR?] -> sim: ADR -> PRD + Tech Spec… |
| §3b | TIPOS LEGADOS | `legacy_document_types` | 385-428 | 1975 | PRD e TS saíram de `document_types` na v2.1.0: não são mais caminho possível para trabalho… |
| §3c | ARTEFATOS OPERACIONAIS | `operational_artifacts` +1 | 430-505 | 4302 | Vivem nas mesmas pastas dos documentos, mas não têm front-matter, id nem entrada no registry. |
| §4 | ONBOARDING DE PROJETO JÁ EXISTENTE | `onboarding` | 507-564 | 3373 | Aplica-se quando um projeto que já tem código em produção, sem nenhum documento deste… |
| §5 | INCIDENTES E POSTMORTEM (FLUXO APARTADO) | `incident_lifecycle` +3 | 566-631 | 3594 | Incidentes não seguem o ciclo de vida padrão (draft/review/approved) — são… |
| §6 | CICLO DE VIDA DE STATUS PADRÃO | `status_lifecycle` | 633-657 | 1525 | Estados do ciclo de vida de status, transições permitidas e notas de uso |
| §7 | ESQUEMA DE ID | `id_scheme` | 659-668 | 726 | Padrão do id de documento: tipo, código do projeto e sequência de 4 dígitos |
| §8 | METADADOS (FRONT-MATTER) | `frontmatter_schema` | 670-727 | 3614 | TODO documento começa com este bloco YAML |
| §9 | REGISTRY (RASTREABILIDADE) | `registry` | 729-785 | 3257 | Registry central e de projeto: campos das entradas, regra de atualização e consulta de rastreio |
| §10 | REUSO MULTI-PROJETO | `multi_project` | 787-813 | 1668 | _framework/ existe em UMA cópia só, dentro do repositório central. |
| §11 | AUDITORIA DE ADERÊNCIA (COMMITS/PRS x REGISTRY) | `audit` | 815-883 | 5108 | O framework NUNCA assume que todo commit/PR nasce de um documento aprovado —… |
| §12 | CAPACIDADES QUE QUALQUER FERRAMENTA DE IA DEVE OFERECER AO EXECUTAR… | `capabilities` | 885-983 | 8733 | Lista das 18 capacidades que a IA deve ter, de criar… |
| §13 | GATE OBRIGATÓRIO: NENHUMA IMPLEMENTAÇÃO PULA SPEC/SDD | `gate_implementation_before_code` | 985-1072 | 5802 | Este gate foi adicionado depois de um incidente real… |
| §14 | GATE OBRIGATÓRIO: NENHUM COMMIT DE IMPLEMENTAÇÃO DIRETO EM MAIN | `gate_branch_before_commit` | 1074-1131 | 3711 | Mesmo incidente EVM da seção 13 —… |
| §15 | GATE OBRIGATÓRIO: QUALIDADE DE CONTEÚDO DO PRD/TECH SPEC/SDD | `gate_content_quality` | 1133-1225 | 6205 | Os gates 13/14 garantem ORDEM (documento antes… |
| §16 | GATE OBRIGATÓRIO: VERIFICAÇÃO DE ESCOPO ANTES DE SDD "IMPLEMENTED" | `gate_scope_verification` | 1227-1319 | 6281 | Gate 13 garante que a SDD existe antes do código. |
| §17 | SKILL DE TRANSFERÊNCIA DE CONTEXTO: HANDOVER / PICKUP | `handover_protocol` | 1321-1377 | 3710 | O fluxo deste framework frequentemente separa quem planeja (compila… |
| §18 | LIÇÕES LOCAIS E CONGELAMENTO DO NÚCLEO | `lessons_policy` | 1379-1435 | 3563 | Entre a v1.4.0 e a v1.7.0 — duas semanas — cada falha de execução de um agente… |
| §19 | SIZING: A PROFUNDIDADE DO FLUXO É FUNÇÃO DO BLAST RADIUS | `sizing` | 1437-1495 | 3452 | Até a v1.7.0 o funil era fixo — toda mudança atravessava… |
