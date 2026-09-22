---
id: SDD-DTF-0041
type: SDD
title: "workflow-rules.yaml: frontmatter_schema não lista SPEC (tipo ativo desde 2.0.0)"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs: []
consumption_instructions: "Sizing small — sem SPEC/RFC/ADR, achado de auditoria (mesma rodada que originou SDD-DTF-0040). Fonte é o próprio YAML, comparado contra document_types (que já lista SPEC corretamente) e contra o uso real em templates/spec.template.md e nas SPECs existentes do projeto. Aplicar em _framework/rules/workflow-rules.yaml (fonte canônica) e replicar a cópia idêntica em doc-traceability-central/_framework/rules/workflow-rules.yaml — mesma regra de espelho de sempre."
supersedes: null
superseded_by: null
tags: [workflow-rules, frontmatter_schema, drift, spec]
---

# workflow-rules.yaml: frontmatter_schema não lista SPEC (tipo ativo desde 2.0.0)

> Este documento é COMPILADO a partir de achado de auditoria, não de
> `source_docs` — sizing `small`, sem SPEC/RFC de origem (ver
> `consumption_instructions`).

## Resumo executivo

`frontmatter_schema.common_fields.type` (seção 8 de
`_framework/rules/workflow-rules.yaml`) lista o enum
`[STRAT, RFC, ADR, PRD, TS, SDD, BASE, INC, PM]` — **sem `SPEC`**, o tipo
ativo que substituiu PRD+TS desde a v2.0.0. `type_specific_fields` tem
entradas para `PRD` e `TS` (legados) mas nenhuma para `SPEC`. A descrição
de `SDD.source_docs` também ainda fala só em "PRD(s), TS(s) e ADR(s)",
sem citar SPEC. Confirmado que isso é só documentação dentro do próprio
YAML — a validação real de tipo usa `document_types` +
`legacy_document_types` (seções separadas, já corretas, ver
`framework_lib.py:119-123`), então não há impacto funcional; é a fonte
canônica se contradizendo internamente.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`: correção textual de uma seção do YAML que já
está desatualizada em relação a outra seção do mesmo arquivo
(`document_types`), sem mudança de comportamento nem de validação.

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | `frontmatter_schema.common_fields.type` deve incluir `SPEC` no enum, na mesma posição relativa que `document_types` usa (entre `ADR` e `SDD`), mantendo `PRD`/`TS` para compatibilidade com projeto legado sob 1.x. |
| RF02 | `frontmatter_schema.type_specific_fields` deve ter uma entrada `SPEC:` com os campos reais usados pelo template (`_framework/templates/spec.template.md`): `parent_rfc`, `parent_adr`, `sizing`. |
| RF03 | A descrição de `SDD.source_docs` em `type_specific_fields` deve citar `SPEC` como a origem principal (documentos ativos desde 2.0.0), mantendo a menção a PRD/TS como caminho de projeto legado, não como se fossem a origem padrão. |

## Especificação técnica consolidada

Arquivo único tocado (produto): `_framework/rules/workflow-rules.yaml`,
replicado sem divergência em
`doc-traceability-central/_framework/rules/workflow-rules.yaml` (fora do
escopo desta SDD, tarefa separada no repositório central).

- RF01: editar a linha `type: "enum[STRAT, RFC, ADR, PRD, TS, SDD, BASE, INC, PM] — obrigatório"`
  para `type: "enum[STRAT, RFC, ADR, SPEC, PRD, TS, SDD, BASE, INC, PM] — obrigatório"`.
- RF02: adicionar, entre o bloco `TS:` e o bloco `SDD:` de
  `type_specific_fields`, uma entrada:
  ```yaml
  SPEC:
    parent_rfc: "id da RFC de origem, ou null se o sizing dispensou RFC"
    parent_adr: "id do ADR de origem, ou null se o gate dispensou ADR"
    sizing: "small | medium | large | complex — ver sizing (seção 19)"
  ```
- RF03: reescrever a linha de `SDD.source_docs` para deixar explícito que
  `SPEC` (e `ADR`, quando existir) é a origem em projeto sob 2.0.0+, e
  PRD/TS só em projeto ainda mapeado sob 1.x.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Adicionar SPEC ao enum de `type` | RF01 | `_framework/rules/workflow-rules.yaml` | |
| 2 | Adicionar entrada `SPEC:` em `type_specific_fields` | RF02 | `_framework/rules/workflow-rules.yaml` | |
| 3 | Corrigir descrição de `SDD.source_docs` | RF03 | `_framework/rules/workflow-rules.yaml` | |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — enum de `type` inclui SPEC | `grep -n "enum\[STRAT, RFC, ADR, SPEC, PRD, TS, SDD, BASE, INC, PM\]" _framework/rules/workflow-rules.yaml` | Ao menos 1 ocorrência |
| 2 | RF02 — entrada `SPEC:` existe em `type_specific_fields` com os 3 campos | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); f=d['frontmatter_schema']['type_specific_fields']['SPEC']; assert set(f)=={'parent_rfc','parent_adr','sizing'}, f"` | Sem erro |
| 3 | RF03 — descrição de `source_docs` cita SPEC | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); assert 'SPEC' in d['frontmatter_schema']['type_specific_fields']['SDD']['source_docs']"` | Sem erro |
| 4 | YAML continua parseável (sintaxe válida) | `python3 -c "import yaml; yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))"` | Sem erro |
| 5 | Suíte completa sem regressão (confirma que nada depende do enum textual de `frontmatter_schema`) | `python3 -m pytest _framework/ -q` | Todos os testes passam |
| 6 | `render_prompts.py --check` continua passando | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência reportada (AGENTS.md/QUICKSTART.md/especificacao.md/CHANGELOG.md não derivam desta seção, mas confirma que nada mais quebrou) |
| 7 | `framework_check.py --auto` roda limpo (confirma que a mudança não introduziu problema de validação em nenhum registry conhecido) | `python3 _framework/scripts/framework_check.py --auto` | Sem erro fatal |

## Instruções específicas para a IA implementadora

- Único arquivo de produto: `_framework/rules/workflow-rules.yaml`. Não
  editar `document_types`/`legacy_document_types` (já corretos) nem
  `framework_lib.py`/`validate_doc.py` — não há bug de validação, só de
  documentação dentro do próprio YAML.
- Não bump de `framework.version` — é correção textual, não mudança de
  regra observável por projeto nenhum (`RULE_SINCE` não se aplica: nada
  novo é exigido de documento existente).
- Replicar em
  `doc-traceability-central/_framework/rules/workflow-rules.yaml` é
  obrigatório (mirror), mas acontece em sessão separada nesse repositório.

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF03 todos com trecho correspondente em `workflow-rules.yaml`.
- [x] Único arquivo de produto tocado: `_framework/rules/workflow-rules.yaml`
      (mais a cópia bundlada da skill, regenerada por `render_prompts.py`,
      não editada à mão).
- [x] Nenhuma mudança em `document_types`, `legacy_document_types`,
      `framework_lib.py`, `validate_doc.py` ou `framework.version`.

## Evidência de verificação (preencher antes de status `implemented`)

(verificação independente pendente — tabela desta sessão implementadora
abaixo, não substitui a verificação independente exigida por
`gate_scope_verification`)

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado |
|---|---|---|---|
| 1 | RF01 | `grep -n "enum\[STRAT, RFC, ADR, SPEC, PRD, TS, SDD, BASE, INC, PM\]" _framework/rules/workflow-rules.yaml` | linha 663 |
| 2 | RF02 | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); f=d['frontmatter_schema']['type_specific_fields']['SPEC']; assert set(f)=={'parent_rfc','parent_adr','sizing'}"` | `OK`, sem erro |
| 3 | RF03 | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); assert 'SPEC' in d['frontmatter_schema']['type_specific_fields']['SDD']['source_docs']"` | `OK`, sem erro |
| 4 | YAML parseável | `python3 -c "import yaml; yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))"` | `OK`, sem erro |
| 5 | Suíte completa | `python3 -m pytest _framework/ -q` | `180 passed in 27.03s` |
| 6 | `render_prompts.py --check` | `python3 _framework/scripts/render_prompts.py --check \| grep "❌"` | 1ª rodada: falhou (cópia bundlada da skill divergente); rodado `render_prompts.py` (sem `--check`) para regenerar; 2ª rodada: sem saída (exit 1) |
| 7 | `framework_check.py --auto` | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` (kit + example project-repo-checkout) |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (vazio — achado de auditoria, sem documento de origem único) |
