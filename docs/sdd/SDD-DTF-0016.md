---
id: SDD-DTF-0016
type: SDD
title: "RULE_SINCE por data de criação do documento, não por framework_version do registry"
status: draft
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-04"
updated: "2026-09-04"
relates_to: []
source_docs: []
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada, não falha de processo. Escopo mecânico: framework_lib.py ganha version_date/rule_applies_since_date, validate_doc.py passa a comparar fm.created em vez do framework_version único do registry."
supersedes: null
superseded_by: null
tags: [tooling, gate_content_quality, non_retroactive]
---

# RULE_SINCE por data de criação do documento, não por framework_version do registry

## Resumo executivo

Achado real ao migrar o projeto EVM (repo `doc-traceability-central`,
`docs/EVM/registry.yaml`) de `framework_version: "1.6.0"` para `"2.1.0"`
(decisão do dono do projeto de usar SPEC daqui pra frente): o bump
quebrou o `pre-commit` e o CI (`framework-check`) reprovando
retroativamente 11 PRD/TS já `implemented`/`approved`, criadas antes da
regra RF-ID existir (RF-ID é regra desde 1.7.0). Causa raiz:
`validate_doc.check_document` decide se uma regra de `RULE_SINCE` vale
comparando a `framework_version` ÚNICA do `registry.yaml` do projeto
contra a versão que introduziu a regra — não há granularidade por
documento. Bumpar o registry pra adotar SPEC em trabalho novo arrasta
consigo, sem querer, todo o histórico do projeto para debaixo do gate
novo.

`sizing: small` — 3 arquivos de framework (`workflow-rules.yaml`,
`framework_lib.py`, `validate_doc.py`), sem novo tipo de documento, sem
mudança de fluxo/gate — só corrige a granularidade de uma checagem
mecânica existente para bater com o que `lessons_policy.non_retroactive`
já promete em texto.

## Decisão(ões) de arquitetura aplicável(is)

Nenhuma — correção de mecanização, não decisão de desenho novo.

## Requisitos consolidados

- Cada entrada de `framework.changelog` em `workflow-rules.yaml` ganha
  campo `date` (`YYYY-MM-DD`, data em que a versão foi introduzida —
  obtida do histórico git do próprio commit que criou a entrada).
- `framework_lib.py` ganha `version_date(rules, version)` (lê a `date`
  de uma versão do changelog) e `rule_applies_since_date(rules,
  rule_since, doc_created, project)`: regra vale se `doc_created >=
  version_date(rule_since)`; sem `date` conhecida ou sem `created` no
  documento, cai no comportamento anterior (`rule_applies` por versão
  do registry) — nunca fica mais permissivo que hoje, só mais preciso
  quando há dado suficiente.
- `validate_doc.check_document` troca a chamada de `rule_applies` por
  `rule_applies_since_date`, usando `fm.get("created")` do próprio
  documento.
- `render_prompts.py` sincroniza a cópia de `framework_lib.py`,
  `validate_doc.py` e `workflow-rules.yaml` para
  `_framework/skills/doc-traceability-framework/` (mecanismo já
  existente, sem mudança).

Casos de borda:
- Documento sem `created` (não deveria existir — é campo obrigatório de
  front-matter) → cai no fallback por versão do registry, igual hoje.
- Versão do changelog sem `date` (não deveria existir após esta SDD,
  mas é tolerado) → mesmo fallback.
- Documento `created` no mesmo dia em que a regra nasceu → comparação
  `>=`, ou seja, conta como já sob a regra (consistente com o texto de
  `rule_applies` atual, que usa `>=` na versão).

Fora de escopo: mudar qualquer regra do `gate_content_quality` em si
(quais placeholders são banidos, o que é EARS, etc.) — só a forma como
"desde quando" é calculado. Não migra nenhum documento existente, não
adiciona campo novo ao front-matter de documento (o campo novo é só no
changelog do framework).

## Especificação técnica consolidada

**`_framework/rules/workflow-rules.yaml`** — cada item de
`framework.changelog` ganha `date`, ex.:
```yaml
    - version: "1.7.0"
      date: "2026-08-29"
      summary: >
        ...
```
Datas obtidas via `git log -S'version: "X.Y.Z"' --oneline -- _framework/rules/workflow-rules.yaml`
e `git log -1 --format=%ad --date=short <sha>` (histórico real do
próprio repositório do framework).

**`_framework/scripts/framework_lib.py`** (funções novas, `rule_applies`
existente intocada — outros chamadores podem seguir usando):
```python
def version_date(rules: dict, version: str) -> str | None:
    fw = rules.get("framework") or {}
    for entry in fw.get("changelog") or []:
        if entry.get("version") == version:
            return entry.get("date")
    return None

def rule_applies_since_date(rules, rule_since, doc_created, project) -> bool:
    since_date = version_date(rules, rule_since)
    if since_date and doc_created:
        return str(doc_created) >= since_date
    return rule_applies(rule_since, project)
```

**`_framework/scripts/validate_doc.py`** — em `check_document`:
`rules = load_rules()` lido uma vez após o front-matter; `applies(rule)`
passa a chamar `rule_applies_since_date(rules, RULE_SINCE[rule],
fm.get("created"), version)` em vez de `rule_applies(RULE_SINCE[rule],
version)`. Import troca `rule_applies` por `load_rules` +
`rule_applies_since_date`.

## Critérios de aceite / definição de pronto

| # | Critério | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | Changelog tem `date` em toda entrada | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); print(all('date' in e for e in d['framework']['changelog']))"` | `True` |
| 2 | EVM (registry em 2.1.0, PRD/TS criadas 2026-08-25, antes de 1.7.0/2026-08-29) deixa de reprovar | `python3 _framework/scripts/framework_check.py /home/michel/doc-traceability-central/docs/EVM` | `✅ Todas as verificações do framework passaram.` |
| 3 | Documento hipotético criado depois de 1.7.0 sob registry antigo continua reprovando por RF-ID ausente | Copiar um PRD sem RF-ID pra dir descartável, mudar `created` pra depois de 2026-08-29, rodar `validate_doc.py` nele | Reprova (regressão negativa: fallback não ficou permissivo demais) |
| 4 | Skill fica sincronizada | `python3 _framework/scripts/render_prompts.py` | Todas as linhas `sincronizado`/`em dia`, exit 0 |
| 5 | Regressão geral do framework (self-host) | `python3 _framework/scripts/framework_check.py --auto` e `python3 _framework/scripts/framework_check.py /home/michel/doc-traceability-framework/docs/sdd`, e `docs/DTF`, `docs/ABSTRACTCLINIC` no central | Todos `✅`, nenhum novo problema |

## Instruções específicas para a IA implementadora

- Datas do changelog vêm do histórico git real do commit que introduziu
  cada versão — não inventar nem usar `last_updated` do bloco
  `framework` (que só reflete a versão atual).
- Não mudar a assinatura nem o comportamento de `rule_applies` — ela
  continua existindo como fallback e pode ter outros usos fora deste
  escopo.
- Rodar `render_prompts.py` depois de editar `framework_lib.py`/
  `validate_doc.py`/`workflow-rules.yaml` pra sincronizar a cópia da
  skill — sem isso a skill fica com a lógica antiga.
- Branch dedicada a partir de `main`, PR — nunca commit direto (gate
  seção 14). Commits em Conventional Commits, `Refs: SDD-DTF-0016`.
- Não alterar `docs/EVM/registry.yaml` do repositório central como
  parte desta SDD — o bump pra 2.1.0 já foi decisão e commit
  separados; esta SDD só corrige o mecanismo que reagiu mal a ele.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Requisito consolidado tem código correspondente.
- [x] Arquivos tocados: `workflow-rules.yaml`, `framework_lib.py`,
      `validate_doc.py`, mais a sincronização automática em
      `_framework/skills/doc-traceability-framework/` (mecanismo
      existente, não escopo novo) e `CHANGELOG.md`/demais
      renderizações regeneradas por `render_prompts.py`.
- [x] Nenhuma abstração extra — `rule_applies` original mantida, só
      complementada por uma função nova mais precisa.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que implementou
(gate 13 violado, ver `LESSONS.md`; evidência abaixo é do
implementador, sujeita a reverificação independente antes de qualquer
outra decisão se apoiar nela).

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); print(all('date' in e for e in d['framework']['changelog']))"` | `True` | trivial (checagem estrutural) | Sim |
| 2 | `python3 _framework/scripts/framework_check.py /home/michel/doc-traceability-central/docs/EVM` | `✅ Todas as verificações do framework passaram.` (antes desta SDD: `❌ 11 problema(s)`) | Sim — reproduzi o `❌` original checando out do commit anterior ao fix, depois voltei e confirmei `✅` | Sim |
| 3 | Doc `PRD-SENSOR-0001` (`created: 2026-09-01`, depois de 1.7.0/2026-08-29) sem RF-ID, sem `registry.yaml` de projeto real no caminho (fallback puro) | `python3 _framework/scripts/validate_doc.py <path>` → `❌ 2 problema(s)`, incluindo RF-ID | Sim — documento criado depois da regra reprova mesmo sem contexto de registry, prova que o fallback não ficou permissivo | Sim |
| 4 | `python3 _framework/scripts/render_prompts.py` | Todas as linhas `✅ .../sincronizado`/`em dia` | trivial (idempotência do sync) | Sim |
| 5 | `python3 -m pytest -q` e `python3 _framework/scripts/framework_check.py --auto` | `7 passed in 0.18s`; `✅ Todas as verificações do framework passaram.` | sem sensor dedicado — regressão geral, não lógica nova desta SDD | Sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| Branch | `sdd/SDD-DTF-0016-rule-since-por-data` |
