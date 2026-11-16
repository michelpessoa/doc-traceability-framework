# Mapa de seções do workflow-rules.yaml

Gerado por `render_indexes.py` — não edite à mão. Ids `§N` = numeração dos banners do YAML.
YAML: 95189 bytes; mapa + maior seção: 12769 (13.4% de 15%)
Total: 23 seções

| § | Seção | Chaves | Linhas | Bytes | Resumo |
|---|---|---|---|---|---|
| §0 | preâmbulo | `framework` | 1-214 | 12436 | Cabeçalho e bloco `framework:` (versão e changelog) |
| §1 | TOPOLOGIA DE REPOSITÓRIOS (MODELO MULTI-REPO) | `repository_topology` | 216-273 | 3599 | Este framework assume DOIS tipos de repositório git, nunca um só |
| §2 | TIPOS DE DOCUMENTO | `document_types` | 275-397 | 5422 | Os oito tipos de documento: STRAT, RFC, ADR, SPEC, SDD, BASE, INC e PM, com pasta e repositório |
| §3 | FLUXO PRINCIPAL (TO-BE) E GATE DE DECISÃO | (nenhuma) | 399-411 | 655 | Fluxo textual: Strategy Doc -> RFC -> [GATE: exige ADR?] -> sim: ADR -> SPEC -> SDD… |
| §3b | TIPOS LEGADOS | `legacy_document_types` | 413-456 | 1975 | PRD e TS saíram de `document_types` na v2.1.0: não são mais caminho possível para trabalho… |
| §3c | ARTEFATOS OPERACIONAIS | `operational_artifacts` +1 | 458-533 | 4295 | Vivem nas mesmas pastas dos documentos, mas não têm front-matter, id nem entrada no registry. |
| §4 | ONBOARDING DE PROJETO JÁ EXISTENTE | `onboarding` | 535-592 | 3347 | Aplica-se quando um projeto que já tem código em produção, sem nenhum documento deste… |
| §5 | INCIDENTES E POSTMORTEM (FLUXO APARTADO) | `incident_lifecycle` +3 | 594-659 | 3594 | Incidente e postmortem têm ciclo próprio (open a closed), fora do padrão |
| §6 | CICLO DE VIDA DE STATUS PADRÃO | `status_lifecycle` | 661-685 | 1525 | Estados do ciclo de vida de status, transições permitidas e notas de uso |
| §7 | ESQUEMA DE ID | `id_scheme` | 687-696 | 726 | Padrão do id de documento: tipo, código do projeto e sequência de 4 dígitos |
| §8 | METADADOS (FRONT-MATTER) | `frontmatter_schema` | 698-755 | 3614 | TODO documento começa com este bloco YAML |
| §9 | REGISTRY (RASTREABILIDADE) | `registry` | 757-817 | 3438 | Registry central e de projeto: campos das entradas, regra de atualização e consulta de rastreio |
| §10 | REUSO MULTI-PROJETO | `multi_project` | 819-845 | 1668 | _framework/ existe em UMA cópia só, dentro do repositório central. |
| §11 | AUDITORIA DE ADERÊNCIA (COMMITS/PRS x REGISTRY) | `audit` | 847-915 | 5099 | O framework NUNCA assume que todo commit/PR nasce de um documento aprovado… |
| §12 | CAPACIDADES QUE QUALQUER FERRAMENTA DE IA DEVE OFERECER AO EXECUTAR… | `capabilities` | 917-1015 | 8704 | Lista das 18 capacidades que a IA deve ter, de criar… |
| §13 | GATE OBRIGATÓRIO: NENHUMA IMPLEMENTAÇÃO PULA SPEC/SDD | `gate_implementation_before_code` | 1017-1104 | 5802 | Este gate foi adicionado depois de um incidente real… |
| §14 | GATE OBRIGATÓRIO: NENHUM COMMIT DE IMPLEMENTAÇÃO DIRETO EM MAIN | `gate_branch_before_commit` | 1106-1163 | 3705 | Gate: sem commit de implementação direto em main |
| §15 | GATE OBRIGATÓRIO: QUALIDADE DE CONTEÚDO DA SPEC E DA SDD | `gate_content_quality` | 1165-1257 | 6196 | Gate de conteúdo: SPEC e SDD sem placeholder antes de in_review |
| §16 | GATE OBRIGATÓRIO: VERIFICAÇÃO DE ESCOPO ANTES DE SDD "IMPLEMENTED" | `gate_scope_verification` | 1259-1351 | 6281 | Gate 13 garante que a SDD existe antes do código. |
| §17 | SKILL DE TRANSFERÊNCIA DE CONTEXTO: HANDOVER / PICKUP | `handover_protocol` | 1353-1409 | 3698 | O fluxo deste framework frequentemente separa quem planeja… |
| §18 | LIÇÕES LOCAIS E CONGELAMENTO DO NÚCLEO | `lessons_policy` | 1411-1467 | 3563 | Entre a v1.4.0 e a v1.7.0 — duas semanas — cada falha de execução de um agente… |
| §19 | SIZING: A PROFUNDIDADE DO FLUXO É FUNÇÃO DO BLAST RADIUS | `sizing` | 1469-1528 | 3453 | Até a v1.7.0 o funil era fixo — toda mudança atravessava… |
| §20 | CONTRATO DO EXECUTOR | `executor_contract` | 1530-1572 | 2394 | O que um executor lê, as saídas --json com esquema e o que pode escrever no central |
