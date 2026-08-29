# Changelog

Arquivo GERADO por `_framework/scripts/render_prompts.py` a partir de
`framework.changelog` em `_framework/rules/workflow-rules.yaml`. Não
edite à mão — para registrar uma versão, acrescente a entrada no YAML.

Versão corrente: **2.1.0** (`2026-08-29`).

## 2.1.0

Primeira etapa da neutralização de fornecedor (SPEC-DTF-0001, ADR-DTF-0001): o framework deixa de depender de prompt colado para ser usado. `AGENTS.md` na raiz do repositório passa a ser o alvo canônico das renderizações — lido nativamente por Codex, Cursor, Gemini CLI, Copilot e Aider — acompanhado de um `QUICKSTART.md` de uma página; ambos são gerados por render_prompts.py, nunca escritos à mão, e o CI barra divergência. PRD e TS saem de `document_types` para a chave nova `legacy_document_types`: somem do caminho oferecido a trabalho novo sem perder validade nem rastreabilidade de id nos projetos já mapeados. Mudança de superfície e de empacotamento, não de regra: fluxo, gates, sizing e ciclo de vida seguem idênticos.

## 2.0.0

BREAKING. Três mudanças de desenho, todas para cortar volume sem perder rastreabilidade. (1) PRD e Tech Spec fundem-se no tipo SPEC: eram dois documentos com o mesmo autor, o mesmo parent e às vezes o mesmo título, revisados juntos e nunca separadamente — nenhuma referência de mercado (GitHub Spec Kit, AWS Kiro, tlc-spec-driven) os separa em arquivos de repositórios diferentes. PRD e TS seguem válidos como tipos legados: projeto já mapeado não migra (lessons_policy.non_retroactive). (2) Nova seção 19 (sizing): a profundidade do fluxo passa a ser função do blast radius da mudança, não fixa — mudança de ≤3 arquivos sem critério de gate vai direto a SDD, e a ausência do artefato É o registro de que a fase foi pulada. Corrige o custo observado de ~620 linhas de documento para configurar ESLint e CI. (3) STRAT deixa de ser tipo obrigatório do funil e vira seção opcional da RFC — em uso real, nenhum STRAT chegou a `approved`. Acompanha o congelamento do núcleo declarado na seção 18: daqui em diante, versão nova é para mudança de desenho, não para reagir a violação de agente.

## 1.7.0

Corrige gap de qualidade (não de ordem): os gates 13/14 garantiam que PRD/TS/SDD existissem antes do código e que o código nascesse em branch — mas nada garantia que o CONTEÚDO desses documentos fosse específico o suficiente para implementação sem ambiguidade, nem que a SDD, ao virar `implemented`, tivesse sido de fato verificada contra evidência (não memória) e não tivesse crescido além do que foi pedido. Templates de PRD/Tech Spec/SDD ganham estrutura granular (requisito↔critério 1:1, contratos com Consumes/Produces e "onde" exato, casos de borda explícitos), marcador `NEEDS CLARIFICATION` para não inventar silenciosamente, autorrevisão obrigatória antes de `in_review`, e a SDD ganha seção de evidência de verificação e checklist de escopo (nada a mais, nada a menos) antes de `implemented`. Novas seções 15 (gate_content_quality) e 16 (gate_scope_verification). Inspirado em práticas de github.com/obra/superpowers (self-review contra placeholder, "Iron Law" de evidência antes de afirmar conclusão) — adaptado, não copiado, pois este framework opera em dois repositórios e por documentos versionados, não por sessão única. Nova skill `handover` (par com `pickup`, seção 17) para transferir contexto de quem planejou (PRD/TS/SDD) para quem implementa sem herdar a sessão inteira — pensada para manter o agente implementador abaixo de ~45% de uso de contexto da sessão.

## 1.6.0

Corrige segundo gap do mesmo incidente EVM: mesmo com PRD/TS/SDD no lugar (gate da seção 13 respeitado), a implementação foi commitada direto na branch main do repositório de projeto, sem branch dedicada nem PR — fere o princípio de desenvolvimento isolado que sustenta qualquer pipeline de CI/CD (revisão antes de integrar, checks obrigatórios, histórico limpo por decisão). Nova seção 14 (gate_branch_before_commit) torna obrigatório que toda implementação de código coberta por este framework nasça em branch própria e vá a main via PR, nunca commit direto. Nova capability `enforce_branch_before_commit`.

## 1.5.0

Corrige gap crítico: uma sessão de IA implementou 3 ADRs aprovados do projeto EVM indo direto pro código, sem PRD/Tech Spec/SDD — documentos escritos só depois, retroativamente, quando o dono do projeto percebeu a lacuna. Nova seção 13 (gate_implementation_before_code) torna explícito e OBRIGATÓRIO que nenhuma implementação pode começar antes de PRD/TS (central) e SDD (projeto) existirem — um ADR com "Consequências" detalhada não é especificação suficiente. Diferente da auditoria (seção 11, que tolera desvio de terceiros e descobre depois), este gate vale para a própria IA operando sob o framework: pular a ordem é erro a evitar, não desvio a tolerar. Nova capability `enforce_implementation_gate`.

## 1.4.0

Corrige gap: nem onboarding nem auditoria registravam a URL do repositório de código do projeto em lugar nenhum, então rodar uma auditoria dependia de alguém lembrar de informar o link toda vez. Agora todo registry central (docs/{PROJECT_CODE}/registry.yaml) carrega um campo `repository` de nível de projeto com a URL do repositório de código; onboarding passa a gravá-lo na Fase 1, e auditoria passa a lê-lo primeiro em vez de assumir que já foi informado.

## 1.3.0

Guia opcional de paralelização por trilhas de negócio (docs/guias/paralelizacao-trilhas.md): padrão de organização (uma skill por trilha, uma sessão de IA/pessoa por trilha, grafo de dependências) para projetos com módulos independentes que podem ser implementados em paralelo. Não altera o fluxo principal de documentos nem cria tipo novo — é um padrão de execução, não de decisão.

## 1.2.0

Auditoria de aderência (seção 11): como a adesão de todo o time à convenção de referenciar documentos em commits/PRs não pode ser garantida, o framework passa a oferecer uma auditoria periódica e sob demanda (sem CI, sem bloqueio de merge) que cruza o histórico do repositório do projeto com os registries, classifica commits em coberto/referência quebrada/não documentado, e reaproveita o mecanismo de reconstrução do onboarding para propor ADRs quando o commit não documentado for arquiteturalmente significativo.

## 1.1.0

Modelo multi-repositório explícito (repo central + repo por projeto, SDD vive no repo do projeto); onboarding de projeto já existente (tipo BASE + ADRs reconstruídos); fluxo de incidentes e postmortem (tipos INC/PM, severidade, regra de recorrência).

## 1.0.0

Fluxo Strategy->RFC->[gate]->ADR->PRD/TS->SDD, registry, IDs, kit multi-projeto.

## Histórico anterior ao changelog canônico

As versões 1.0.0 a 1.3.0 existiram antes de `framework.changelog` virar a
fonte de verdade. O registro delas vive no histórico do git.
