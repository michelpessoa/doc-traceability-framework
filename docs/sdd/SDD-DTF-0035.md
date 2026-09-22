---
id: SDD-DTF-0035
type: SDD
title: "Skills finas (handover/pickup/verify-sdd): checklist mínimo inline + itens A e G do tlc-spec-lean"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: [SDD-DTF-0034]
source_docs:
  - id: "STRAT-DTF-0003"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md"
consumption_instructions: "Sizing small — sem SPEC/RFC, compilado direto do item 6 da tabela de prioridade de STRAT-DTF-0003 (revisar descriptions e checklist mínimo inline das skills handover/pickup/verify-sdd; incluir os itens A e G da comparação com tlc-spec-lean, seção 2ª rodada)."
supersedes: null
superseded_by: null
tags: [skills, handover, pickup, verify-sdd, tlc-spec-lean, qualidade]
---

# Skills finas: checklist mínimo inline + itens A e G do tlc-spec-lean

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`).

## Resumo executivo

As três skills finas (`handover`, `pickup`, `verify-sdd`) têm SKILL.md
que só apontam para o procedimento normativo, sem nenhum resumo
acionável inline — quem abre a skill não vê o essencial sem abrir o
procedimento inteiro. Ao mesmo tempo, dois itens da comparação com o
`tlc-spec-lean` (STRAT-DTF-0003, 2ª rodada) ainda não estavam
mecanizados: item A (um teste nunca provado capaz de falhar não é
evidência — a coluna "Sensor" da tabela de evidência existia por
convenção, mas nada conferia que estava preenchida) e item G
(adjetivos que descrevem o resultado desejado de um critério sem dizer
como verificá-lo não estavam na lista de placeholder banido de
`validate_doc.py`). Esta SDD resolve os três de uma vez porque tocam os
mesmos arquivos (skills finas + os dois validadores que elas invocam).

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, declarado em STRAT-DTF-0003 (item 6). Nenhum
critério de `decision_gates.rfc_to_adr` se aplica: é extensão de
validador mecânico já existente e prosa inline em skill já existente,
não novo padrão arquitetural, não troca de tecnologia, sem trade-off
técnico a registrar.

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | O SKILL.md de `handover`, `pickup` e `verify-sdd` deve ter um checklist mínimo inline (bullets) antes do pointer ao procedimento normativo, cobrindo os pontos de maior risco de cada skill sem exigir abrir o procedimento para saber o essencial. |
| RF02 | `validate_state.py` deve reprovar uma SDD `implemented` cuja tabela de "Evidência de verificação" tenha uma coluna com "sensor" no cabeçalho e alguma linha com essa célula vazia — célula em branco não é declaração, "sem teste automatizado" é. |
| RF03 | Tabela de evidência sem coluna "Sensor" no cabeçalho (formato anterior a esta convenção) não deve ser reprovada retroativamente por RF02 — só a presença vazia da coluna é erro. |
| RF04 | `validate_doc.py` deve reprovar (mesma mecânica de `BANNED_PLACEHOLDERS`, mesmo status-gating: `problems` em `approved`/`implemented`, `warnings` antes disso) vocabulário vago em critério de aceite — no mínimo os 9 termos (3 em inglês, 6 em português) citados no anexo de comparação com o tlc-spec-lean em STRAT-DTF-0003, item G, cada um descrevendo o resultado desejado sem dizer como verificá-lo. |
| RF05 | O procedimento `_framework/procedures/verify-sdd.md` deve citar explicitamente, na seção do sensor de discriminação, que a coluna "Sensor" vazia é mecanizada por `validate_state.py` (RF02), e na seção de conformidade com a spec, que vocabulário vago no critério é sinal a reportar mesmo sendo gate distinto (`gate_content_quality`, RF04). |

## Especificação técnica consolidada

Arquivos tocados (produto):
- `_framework/skills/handover/SKILL.md`, `_framework/skills/pickup/SKILL.md`,
  `_framework/skills/verify-sdd/SKILL.md` (RF01) — estas três skills não
  têm bundle próprio de scripts/references, então não há segunda cópia
  local a espelhar.
- `_framework/scripts/validate_state.py`, replicado em
  `_framework/skills/doc-traceability-framework/scripts/validate_state.py`
  via `render_prompts.py` (RF02, RF03).
- `_framework/scripts/validate_doc.py`, replicado no mesmo bundle (RF04).
- `_framework/procedures/verify-sdd.md` (RF05) — procedimento não é
  bundlado por nenhuma skill, vive só no repositório central deste kit.

Réplica obrigatória no repositório central `doc-traceability-central`
(mesma AGENTS.md de `_framework/`) fica fora do escopo desta SDD, como
já registrado em SDD-DTF-0034.

- RF01: adicionar, em cada um dos três SKILL.md, uma seção curta antes
  do pointer ao procedimento, título "Checklist mínimo, antes de abrir
  o procedimento inteiro:", com 3-5 bullets dos pontos citados no
  próprio procedimento normativo que mais custam se esquecidos (ex.:
  para `verify-sdd`: diff fixo, sensor de discriminação, teto de 3
  rodadas).
- RF02: em `check_evidence` (validate_state.py), localizar o índice da
  coluna cujo cabeçalho contém "sensor" (case-insensitive, mesma técnica
  já usada para `cmd_idx`) e, para cada linha, reportar problema se essa
  coluna existir e a célula estiver vazia depois de `.strip()`.
- RF03: a checagem de RF02 só dispara se o índice da coluna "sensor" foi
  encontrado no cabeçalho — tabela sem essa coluna não entra no loop.
- RF04: acrescentar os termos de STRAT-DTF-0003 item G à lista
  `BANNED_PLACEHOLDERS` existente — reaproveita o mecanismo de status
  (`DECIDED_STATUSES`) e tipo (`CONTENT_GATE_TYPES`) já implementado,
  sem função nova.
- RF05: duas frases objetivas nas seções "3. Sensor de discriminação" e
  "1. Conformidade com a spec" do procedimento, citando os scripts e o
  item do STRAT de origem.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Checklist mínimo inline nas 3 skills finas | RF01 | `_framework/skills/handover/SKILL.md`, `_framework/skills/pickup/SKILL.md`, `_framework/skills/verify-sdd/SKILL.md` | |
| 2 | Mecanizar coluna Sensor vazia | RF02, RF03 | `_framework/scripts/validate_state.py` | |
| 3 | Ampliar lista de vocabulário vago | RF04 | `_framework/scripts/validate_doc.py` | |
| 4 | Citar as duas mecanizações no procedimento verify-sdd | RF05 | `_framework/procedures/verify-sdd.md` | 2, 3 |
| 5 | Testes de regressão para RF02-RF04 | RF02, RF03, RF04 | `_framework/scripts/tests/test_validate_state.py`, `_framework/tests/test_validate_doc.py` | 2, 3 |
| 6 | Sincronizar bundle da skill principal | RF02, RF04 | `_framework/skills/doc-traceability-framework/scripts/validate_state.py`, `_framework/skills/doc-traceability-framework/scripts/validate_doc.py` | 2, 3 |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — checklist inline presente nas 3 skills | `grep -l "Checklist mínimo" _framework/skills/handover/SKILL.md _framework/skills/pickup/SKILL.md _framework/skills/verify-sdd/SKILL.md` | 3 arquivos listados |
| 2 | RF02 — Sensor vazio reprova | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k sensor -v` | Todos passam |
| 3 | RF03 — tabela sem coluna Sensor não reprova retroativamente | (mesmo comando do critério 2, inclui `test_tabela_sem_coluna_sensor_nao_reprova_retroativamente`) | Passa |
| 4 | RF04 — vocabulário vago reprova em status decidido, é warning em draft | `python3 -m pytest _framework/tests/test_validate_doc.py -k vocabulario_vago -v` | Todos passam |
| 5 | RF05 — procedimento cita as duas mecanizações | `grep -c "validate_state.py\|STRAT-DTF-0003 item" _framework/procedures/verify-sdd.md` | >= 2 |
| 6 | Sem regressão nos validadores contra os documentos reais do projeto | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | Ambos ✅, 0 problemas |
| 7 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam |
| 8 | Bundle da skill principal sincronizado | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência |

## Instruções específicas para a IA implementadora

- RF04 (vocabulário vago) reaproveita `BANNED_PLACEHOLDERS`: não crie
  lista nova nem função nova, ou o teste de paridade de padrão de
  código do próprio projeto fica inconsistente com o resto do arquivo.
- RF02 usa a mesma técnica de `cmd_idx` (linha já existente em
  `check_evidence`): busca por substring no cabeçalho, não por posição
  fixa de coluna.
- Não confundir esta SDD com `gate_content_quality` (seção 15) em si —
  RF04 é uma extensão do mecanismo que já existe para esse gate, não
  uma seção nova no YAML. Nenhuma mudança em `workflow-rules.yaml`.
- Não tocar no item 7-10 da tabela de STRAT-DTF-0003 (fora de escopo
  desta SDD).

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF05 todos com trecho correspondente no código/documento editado.
- [x] Nenhum arquivo tocado fora da lista de "Arquivos tocados" acima.
- [x] Nenhuma mudança em `workflow-rules.yaml`, `AGENTS.md`, `QUICKSTART.md`.

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

**Verificador independente:** sim (sessão separada, sem histórico da sessão que implementou)

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | 1 | `grep -l "Checklist mínimo" _framework/skills/handover/SKILL.md _framework/skills/pickup/SKILL.md _framework/skills/verify-sdd/SKILL.md` | 3 arquivos listados | sem teste automatizado | Sim |
| 1 | 2 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k sensor -v` | 4 passed | condição `sensor_idx`/`row[sensor_idx].strip()` comentada em `check_evidence`; `test_sensor_vazio_reprova` falhou; restaurado e voltou a passar | Sim |
| 1 | 3 | (mesmo comando do #2, inclui `test_tabela_sem_coluna_sensor_nao_reprova_retroativamente`) | incluído no `4 passed` acima | mesmo sensor do #2 (guard `sensor_idx is not None`) | Sim |
| 1 | 4 | `python3 -m pytest _framework/tests/test_validate_doc.py -k vocabulario_vago -v` | 2 passed | 9 termos novos removidos de `BANNED_PLACEHOLDERS`; os 2 testes falharam; restaurado e voltaram a passar | Sim |
| 1 | 5 | `grep -c "validate_state.py\|STRAT-DTF-0003 item" _framework/procedures/verify-sdd.md` | `3` (>= 2) | sem teste automatizado | Sim |
| 1 | 6 | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | `✅ 34 documento(s) passaram no gate de qualidade de conteúdo.` / `✅ 34 documento(s) verificados: nenhuma SDD implemented sem evidência.` | sem teste automatizado | Sim |
| 1 | 7 | `python3 -m pytest _framework/ -q` | `126 passed in 4.80s` | n/a (suíte completa; sensores por critério cobertos individualmente acima) | Sim |
| 1 | 8 | `python3 _framework/scripts/render_prompts.py --check` | Todas as linhas `✅ ... sincronizado.`/`✅ ... em dia.` | sem teste automatizado | Sim |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | STRAT-DTF-0003 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md) |
| relates_to | SDD-DTF-0034 (mesma STRAT, itens 3-5) |
