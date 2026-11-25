---
name: doc-traceability-framework
description: >
  Gerencia documentos de decisão (STRAT, RFC, ADR, SPEC, SDD) com ids, front-matter e registry: criar, avaliar, avançar status, rastrear, validar; também incidentes, onboarding de legado e auditoria. Use when pedirem "cria uma RFC", "precisa de ADR?", "monta a spec", "abre um incidente", e SEMPRE antes de implementar decisão aprovada. Do NOT use for verificar SDD (`verify-sdd`), passar contexto (`handover`/`pickup`), nem README ou changelog.
---

# Framework de Documentação & Rastreabilidade para IA

Fonte canônica das regras: `references/workflow-rules.yaml`. Este arquivo
é o roteador; abra o YAML na chave citada quando precisar do detalhe exato.

## Dois repositórios — confirme onde você está antes de agir

- **Central**: `docs/{PROJECT_CODE}/` de todos os projetos (STRAT, RFC, ADR, SPEC, BASE, INC, PM).
- **Projeto**: só `docs/sdd/` — a SDD é o único tipo lido por IA ao implementar.

Sem saber em qual está, pergunte antes de criar documento.

**Greenfield** (`repository_status: none_yet` no registry central): STRAT,
RFC, ADR e SPEC rodam no central; SDD fica bloqueada. Ao criar o
repositório, num único ato: preencha `repository` e `repository_status:
active` no central, e crie `docs/sdd/registry.yaml` vazio no novo.

## Tipos (8 ativos; PRD e TS só como legado de projeto sob 1.x)

| Tipo | Quando usar | Repo | Pasta |
|---|---|---|---|
| STRAT | Opcional: direção sem RFC associada | central | `00-strategy/` |
| RFC | Decisão relevante: transversal, custo alto, nova tecnologia | central | `01-rfc/` |
| ADR | Registro imutável de UMA decisão de arquitetura | central | `02-adr/` |
| SPEC | Requisito (o QUÊ) + desenho (o COMO) | central | `03-spec/` |
| SDD | Compilada da SPEC, pronta para a IA implementar | projeto | `docs/sdd/` |
| BASE | Retrato do estado atual no onboarding | central | `06-baseline/` |
| INC | Evento em produção | central | `07-incidents/` |
| PM | Postmortem e action items | central | `08-postmortems/` |

Parta sempre de `templates/*.template.md`, nunca do zero.

## Fluxo e sizing

Declare o nível no campo `sizing` antes de tudo (`workflow-rules.yaml:sizing`):
`small` -> SDD; `medium` -> SPEC -> SDD; `large` -> RFC -> [gate] -> ADR ->
SPEC -> SDD; `complex` acrescenta STRAT antes da RFC. Um critério acima
sobe o nível inteiro. Gate RFC→ADR: qualquer critério verdadeiro exige
ADR (`workflow-rules.yaml:decision_gates`); registre `decision_gate_criteria_met`.
A ausência do documento É o registro de que a fase foi pulada. A SDD nasce
no repositório do projeto, compilada de SPEC/ADR `approved`, com
`source_docs` `{id, url}`; tasks em paralelo: `scripts/parallel_plan.py`.
Em projeto sob 2.7.0 ou maior, a SDD com `source_docs` é enxuta: requisitos por
referência à SPEC (RF-ID | Origem | Requisito (resumo) | Arquivos), `sizing`
obrigatório, RF-IDs conferidos contra a SPEC nas duas direções por
`scripts/check_source_docs.py`. Com a coluna `Projeto` na SPEC (2.8.0), só
contam os RFs do `project` da SDD (`workflow-rules.yaml:document_types.SPEC.rf_optional_columns`).

## Gates

> **TAMANHO DECIDE QUAIS DOCUMENTOS, NUNCA SE A ORDEM VALE.** Tamanho pequeno tem menos documento, não menos gate. `workflow-rules.yaml:sizing`.

> **NENHUMA LINHA DE CÓDIGO ANTES DA SPEC E DA SDD EXISTIREM.** Ao implementar decisão aprovada, confirme SPEC e SDD antes de tocar código; se pedirem para pular, avise e peça confirmação explícita. `workflow-rules.yaml:gate_implementation_before_code`.

> **NENHUM COMMIT DE IMPLEMENTAÇÃO DIRETO EM MAIN.** Branch nomeada pelo id de origem, levada a main por PR; não mergeie sem sinal do humano. `workflow-rules.yaml:gate_branch_before_commit`.

> **NENHUM DOCUMENTO VAI A `in_review` COM PLACEHOLDER OU AMBIGUIDADE PENDENTE.** Rode `scripts/validate_doc.py`; ambiguidade real vira `NEEDS CLARIFICATION`. `workflow-rules.yaml:gate_content_quality`.

> **NENHUM `implemented` SEM COMANDO RODADO NESTA SESSÃO E SAÍDA REAL.** Quem implementou não verifica: use `verify-sdd` em sessão separada. `workflow-rules.yaml:gate_scope_verification`.

> **FALHA DE EXECUÇÃO VIRA LIÇÃO LOCAL, NÃO VERSÃO NOVA DO FRAMEWORK.** Registre em `LESSONS.md`; não mude o YAML por violação. `workflow-rules.yaml:lessons_policy`.

## Ciclo de vida de status

`draft → in_review → approved → rejected → implemented → superseded →
archived`. Transições válidas: draft → in_review, archived; in_review →
approved, rejected, draft; approved → implemented, superseded, archived;
rejected → archived; implemented → superseded, archived; superseded →
archived. ADR `approved` é imutável: mudança gera ADR novo
(`workflow-rules.yaml:status_lifecycle`). INC usa `open → mitigated →
resolved → closed`.

## Aprovação

Quem aprova cada tipo e sizing: `workflow-rules.yaml:approval_policy`.
Vale a primeira regra que casa; nenhuma casa, vale `default_approver`
(`human`). STRAT, RFC, ADR, BASE, PM e SPEC `medium` ou maior: `human`. SDD:
`policy`, com os `checks` declarados na regra.

- Registro em `approved_by` (`workflow-rules.yaml:frontmatter_schema`): `kind` (`human` | `policy`), `actor`, `at`, `content_sha256` e, com `kind: human`, `evidence` (URL da review). `validate_state.py` cobra o campo em `approved`, `implemented` e `superseded` desde a 2.5.0, sem retroagir.
- `content_sha256` sai de `scripts/approval_hash.py`, sem as `hash_excluded_sections`. Mudar o corpo depois da aprovação invalida o `content_sha256`, e `validate_state.py` reprova.
- Por review da PR: `scripts/review_approval.py` decide, sem rede, se as reviews aprovam sobre o head e monta o `approved_by`. Só contam logins de `approvers`, no topo do registry central (`workflow-rules.yaml:registry.central_registry.approvers_field`).
- Com `kind: policy`, `draft → in_review → approved` num único commit, com `approved_by.transitions`.

## IDs e registry

- ID `{TYPE}-{PROJECT_CODE}-{SEQ4}`, sequencial por tipo, nunca reutilizado.
- Registry: `docs/{PROJECT_CODE}/registry.yaml` (central) ou
  `docs/sdd/registry.yaml`; `scripts/generate_registry_md.py <docs_dir>`.
- `scripts/registry_tools.py`: `validate`, `trace <ID>`, `audit <log> <docs>`.
- Front-matter e registry atualizam juntos, na mesma resposta.

## O que fazer em cada pedido comum

- **Cria RFC/ADR/SPEC/SDD/STRAT**: template do tipo, repo certo, próximo ID pelo registry, front-matter, registry.
- **"Precisa de ADR?"**: aplique o gate, mostre os critérios e o próximo documento.
- **"Implementa o que foi decidido"**: pare antes de código; SPEC e SDD primeiro.
- **Muda o status**: valide no ciclo certo; documento e registry juntos.
- **Monta a SDD**: SPEC/ADR `approved`, compile no repo do projeto, `source_docs` com id+url; sob 2.7.0 ou maior, enxuta (ver "Fluxo e sizing").
- **Registra a aprovação**: seção "Aprovação"; pela PR, `approved_by` humano só com saída válida de `review_approval.py` sobre o head revisado.
- **Executor (ferramenta que roda o fluxo)**: `workflow-rules.yaml:executor_contract`: o que lê, os scripts com `--json` e o esquema de cada saída, e o que escreve: no central por PR, nunca em main; no registry de projeto, `entrega` e `path` da SDD entregue; `approved_by` com `kind: policy` só onde `approval_policy` permite.
- **De onde veio X / rastreia**: percorra `relates_to`, `parent_*`, `source_docs`.
- **Valida o registry**: `scripts/registry_tools.py validate`.
- **Terminei de implementar**: skill `verify-sdd` antes de mudar o status.
- **Faz o handover**: skill `handover`.

## Leia sob demanda

| Pedido envolve | Leia |
|---|---|
| incidente, severidade, postmortem, action items | `references/incidents.md` |
| projeto com código já em produção, baseline | `references/onboarding.md` |
| auditar commits/PRs contra o registry | `references/audit.md` |
| aprovação, review, hash, executor | `references/workflow-rules.yaml`, chaves `approval_policy` e `executor_contract` |
| detalhe exato de campo, transição, critério | `references/workflow-rules.yaml`, na chave citada |

## Handover e novo projeto

Contexto entre sessões: `handover`/`pickup` (`workflow-rules.yaml:handover_protocol`);
não substituem gate. Novo projeto: só muda o `PROJECT_CODE`; não invente
campo, status ou critério fora do YAML.
