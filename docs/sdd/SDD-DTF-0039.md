---
id: SDD-DTF-0039
type: SDD
title: "Sweep de requisitos transversais na SPEC (item 10 de STRAT-DTF-0003)"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "STRAT-DTF-0003"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md"
consumption_instructions: "Sizing small — sem SPEC/RFC, compilado direto do item 10 (último) da tabela de prioridade de STRAT-DTF-0003, seção 'Comparação com o tlc-spec-lean' (E8). Aplicar em _framework/templates/spec.template.md, _framework/scripts/validate_doc.py e _framework/rules/workflow-rules.yaml (gate_content_quality, seção 15), replicar via render_prompts.py e na cópia bundlada da skill, e cobrir com teste antes de implemented."
supersedes: null
superseded_by: null
tags: [spec, sweep, requisitos-transversais, tlc-spec-lean, qualidade]
---

# Sweep de requisitos transversais na SPEC

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar.

## Resumo executivo

A SPEC não força autora a considerar categorias transversais que
tipicamente ficam de fora por omissão silenciosa: autorização,
concorrência, idempotência, observabilidade, falha de dependência
externa, validação de entrada e limite de volume/rate. Esta SDD adiciona
ao `spec.template.md` uma seção fixa "Requisitos transversais (sweep)"
com uma linha por categoria, cada uma exigindo `Destino` (RF-ID que
cobre) ou `n/a` + motivo, e mecaniza a checagem em `validate_doc.py` —
célula vazia é gate, não estilo. É o item 10 (último) de STRAT-DTF-0003,
origem E8 da comparação com o `tlc-spec-lean`.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small` (STRAT-DTF-0003 já declara e nenhum critério de
`decision_gates.rfc_to_adr` se aplica: é convenção de preenchimento de
documento e checagem mecânica associada, não mudança de padrão
arquitetural nem de comportamento externo do produto).

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | `_framework/templates/spec.template.md` deve ganhar uma seção "## Requisitos transversais (sweep)" entre "Requisitos não funcionais" e "Fora de escopo", com tabela fixa de 7 categorias (autorização/permissão, concorrência, idempotência, observabilidade, falha de dependência externa, validação de entrada, limite de volume/rate) e colunas `Destino (RF-ID ou n/a)` e `Motivo (obrigatório se n/a)`. |
| RF02 | `_framework/scripts/validate_doc.py` deve mecanizar, para SPEC em `draft`/`in_review`, que a seção "Requisitos transversais (sweep)" existe, que as 7 categorias fixas têm linha própria, e que toda linha tem `Destino` preenchido (RF-ID válido ou `n/a` com motivo não vazio na coluna seguinte) — célula vazia é gate. |
| RF03 | A checagem de RF02 não deve ser retroativa: SPEC criada antes da data em que esta regra entrou no changelog do framework não pode ser reprovada por não ter a seção, que ainda não existia no template quando foi escrita. |
| RF04 | `_framework/rules/workflow-rules.yaml` deve versionar esta mudança (bump de `framework.version`, entrada de changelog) e citar a seção nova em `gate_content_quality` (seção 15), como item novo da regra. |
| RF05 | `render_prompts.py` deve continuar passando `--check` sem divergência após as mudanças (AGENTS.md, QUICKSTART.md, especificacao.md, CHANGELOG.md, universal.md, doc-framework.mdc, copilot-instructions.md e a cópia bundlada de `validate_doc.py`/`workflow-rules.yaml` da skill todos regenerados/sincronizados), e a cópia bundlada de `spec.template.md` na skill deve ficar idêntica à de `_framework/templates/`. |

## Especificação técnica consolidada

Arquivos tocados (produto):
- `_framework/templates/spec.template.md` — RF01.
- `_framework/skills/doc-traceability-framework/templates/spec.template.md` — cópia bundlada de RF01 (não coberta por `render_prompts.py`, que não sincroniza `templates/`; copiar manualmente byte a byte).
- `_framework/scripts/validate_doc.py` — RF02, RF03 (`RULE_SINCE["sweep"]`, `SWEEP_CATEGORIES`, `check_sweep_section`).
- `_framework/rules/workflow-rules.yaml` — RF04 (bump `framework.version` para `2.3.0`, changelog, item 7 de `gate_content_quality`).
- Arquivos gerados por `render_prompts.py` (RF05): `AGENTS.md`, `QUICKSTART.md`, `docs/especificacao.md`, `CHANGELOG.md`, `_framework/prompts/universal.md`, `_framework/prompts/doc-framework.mdc`, `_framework/prompts/copilot-instructions.md`, `_framework/skills/doc-traceability-framework/scripts/validate_doc.py`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`.

Contrato de `check_sweep_section(doc_id: str, body: str) -> list[str]`
(`_framework/scripts/validate_doc.py`): recebe o id do documento e o
corpo markdown já sem front-matter; devolve lista de mensagens de
problema (vazia se a seção está completa). Chamado de dentro de
`check_document` só quando `doc_type == "SPEC"`, `status` em
`DRAFTING_STATUSES` e `applies("sweep")` (checagem de não-retroatividade
via `rule_applies_since_date`, mesmo mecanismo já usado por `ears`,
`rf_id` etc.). `SWEEP_CATEGORIES` é a lista fixa das 7 categorias, em
minúsculas, comparada contra a primeira coluna de cada linha da tabela
(case-insensitive).

## Decomposição em tasks

Dispensada — sizing `small` (RF06/RF07 de SDD-DTF-0030 dispensam a seção
quando `sizing: small`).

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — seção nova presente no template, entre "Requisitos não funcionais" e "Fora de escopo", com as 7 categorias | `grep -n "Requisitos transversais (sweep)" _framework/templates/spec.template.md` | Ao menos 1 ocorrência | automatizado |
| 2 | RF02/RF03 — gate mecanizado, com sensor de discriminação (categoria faltando, Destino vazio, n/a sem motivo, não-retroatividade) | `python3 -m pytest _framework/tests/test_validate_doc.py -k sweep -v` | Todos os testes `sweep` passam | automatizado |
| 3 | RF04 — `gate_content_quality` (seção 15) cita a seção nova | `grep -n "Requisitos transversais (sweep)" _framework/rules/workflow-rules.yaml` | Ao menos 2 ocorrências (changelog + regra) | automatizado |
| 4 | RF05 — nenhuma divergência de renderização | `python3 _framework/scripts/render_prompts.py --check` | Todos os itens `✅` | automatizado |
| 5 | RF05 — cópia bundlada do template idêntica à cópia canônica | `diff _framework/templates/spec.template.md _framework/skills/doc-traceability-framework/templates/spec.template.md` | Sem saída (exit 0) | automatizado |
| 6 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam | automatizado |

## Instruções específicas para a IA implementadora

- Não alterar `docs/especificacao.md`, `AGENTS.md`, `QUICKSTART.md`,
  `CHANGELOG.md` ou os prompts (`universal.md`, `doc-framework.mdc`,
  `copilot-instructions.md`) manualmente — são gerados por
  `render_prompts.py` a partir do YAML; qualquer edição manual neles é
  sobrescrita e reprovada por `render_prompts.py --check`.
- A lista de 7 categorias (`SWEEP_CATEGORIES`) é fixa por esta SDD —
  não adicionar nem remover categoria sem nova mudança de regra
  (`workflow-rules.yaml`), mesmo que pareça faltar uma óbvia.
- Não tornar a seção obrigatória para SDD, apenas para SPEC — SDD já tem
  sua própria seção de verificação de escopo, e o sweep é especificamente
  sobre o requisito (Parte 1 da SPEC), não sobre o compilado de
  implementação.
- Ao editar `validate_doc.py`, seguir o padrão já usado por
  `check_files_column`/`check_tasks_section`: função pura que recebe o
  corpo já parseado e devolve lista de strings de problema, chamada só
  quando `drafting` (status em `DRAFTING_STATUSES`) para não reprovar
  documento já decidido.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] RF01-RF05 todos com trecho/arquivo correspondente na implementação.
- [ ] Nenhum arquivo tocado fora da lista de "Especificação técnica
      consolidada" — se tocar outro, atualizar esta SDD ou remover
      antes do commit.
- [ ] Nenhuma categoria de sweep adicionada/removida além das 7 listadas.
- [ ] `gate_content_quality` (workflow-rules.yaml) e `spec.template.md`
      (as duas cópias) não divergem entre si na descrição da seção nova.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** {sim | não — mesma sessão que implementou}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | STRAT-DTF-0003 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md) |
