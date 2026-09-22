---
id: SDD-DTF-0037
type: SDD
title: "verify-sdd ganha passo 0: fidelidade da SDD a source_docs (SPEC/ADR de origem)"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0014"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0014.md"
  - id: "ADR-DTF-0007"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0007.md"
consumption_instructions: "Leia SPEC-DTF-0014 e ADR-DTF-0007 inteiros antes de tocar em qualquer arquivo — esta SDD consolida Parte 1/Parte 2 da SPEC, mas o texto completo dos 3 alternativas avaliadas (por que não diff estrutural 100% automático) só vive no ADR. RF02/RF03 exigem sensor de discriminação real. `check_source_fidelity` (RF04-06) usa comparação estrita `created > since_date` (não `>=`) em `RULE_SINCE['source_fidelity']` — não trocar por `rule_applies_since_date` puro sem reler por quê (regressão real testada: SDD-DTF-0036, criada no mesmo dia da versão 2.2.0, seria reprovada retroativamente com `>=`). Editar sempre as duas cópias do kit (_framework/scripts/ e _framework/skills/doc-traceability-framework/scripts/) no mesmo commit — ou deixar a sincronização para render_prompts.py, nunca editar a cópia bundlada à mão."
supersedes: null
superseded_by: null
tags: [verify-sdd, gate_scope_verification, tlc-ai-dev-flow, rastreabilidade, source_docs]
---

# verify-sdd ganha passo 0: fidelidade da SDD a source_docs (SPEC/ADR de origem)

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`).

## Resumo executivo

`verify-sdd` hoje verifica requisito↔código nas duas direções, mas nunca
verifica a SDD contra o(s) documento(s) que a originaram (`source_docs`:
SPEC e, quando existir, ADR) — isso já rendeu um descompasso real
(`relates_to` de SPEC-DTF-0009 apontando para as SDDs erradas por meses).
Esta SDD acrescenta um passo "0. Fidelidade à origem" ao procedimento,
antes do passo 1 atual: mecanizado onde é determinístico
(`check_source_docs.py` confere existência/status/url de cada entrada de
`source_docs`) e checklist estruturado onde não é (todo RF-ID
representado, nenhum critério relaxado, todo contrato técnico igual).
`validate_state.py` passa a exigir, em SDD `implemented` com
`source_docs` não vazio, uma linha de evidência identificável como
"Fidelidade à origem" — não-retroativo por construção.

## Decisão(ões) de arquitetura aplicável(is)

ADR-DTF-0007: `verify-sdd` ganha um passo de procedimento com checklist
estruturado + mecanização parcial (só existência/status/url de
`source_docs`), não um comparador estrutural automático SPEC↔SDD
completo. Alternativa rejeitada (diff estrutural 100% automático)
reprovaria SDD bem escrita que legitimamente resume/consolida a SPEC —
geraria ruído que a IA aprenderia a ignorar. Alternativa rejeitada
(checklist manual sem estrutura) é o status quo que já falhou
silenciosamente na lição do SPEC-DTF-0009.

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | `_framework/procedures/verify-sdd.md` ganha seção "0. Fidelidade à origem" antes de "1. Conformidade com a spec", com os 4 pontos do checklist nomeados (existência/status/url de `source_docs`; todo RF-ID representado; nenhum critério relaxado; todo contrato técnico igual). |
| RF02 | `check_source_docs.py` (novo): dado o path da SDD e o diretório do registry central, verifica para cada entrada de `source_docs` — id existe no registry, status `approved`/`implemented`, url aponta pro mesmo arquivo que o `path` do registry resolve. Reporta problema por entrada, identificando qual e por quê. |
| RF03 | `source_docs` vazio (sizing `small`) → `check_source_docs.py` não reporta nada. |
| RF04 | SDD `implemented` com `source_docs` não vazio e nenhuma linha de "Evidência de verificação" identificável como "Fidelidade à origem" (substring case-insensitive) → `validate_state.py` reporta problema. |
| RF05 | `source_docs` vazio → RF04 não se aplica. |
| RF06 | SDD anterior a esta convenção não é reprovada por RF04 (não-retroativo). |

## Especificação técnica consolidada

Arquivos tocados (produto):

- `_framework/scripts/check_source_docs.py` (novo), replicado em
  `_framework/skills/doc-traceability-framework/scripts/check_source_docs.py`
  via `render_prompts.py` (RF02/RF03): função
  `check_sdd_source_docs(sdd_path: Path, central_docs_dir: Path) -> list[str]`,
  CLI `python3 check_source_docs.py <SDD.md> <central_docs_dir>`. Reaproveita
  `load_registry`, `read_frontmatter` (`framework_lib.py`) e
  `check_source_docs_urls`, `resolve_doc_path` (`registry_tools.py`) já
  existentes — não duplica validação de url. `central_docs_dir` não
  acessível → `SystemExit` explícito (delegado a `load_registry`), nunca
  tratado como "passou".
- `_framework/scripts/validate_state.py`, replicado via `render_prompts.py`
  (RF04-06): nova função `check_source_fidelity(doc_id, source_docs, evidence) -> list[str]`,
  chamada por `check_sdd` só quando `fm.get("source_docs")` não vazio e
  `evidence` não `None` — devolve `[]` de cara se qualquer um dos dois
  faltar (RF05, e guard simétrico ao de `check_evidence` para seção
  ausente). Detecta a linha por substring `"fidelidade à origem"`
  (case-insensitive) em qualquer célula das linhas de `table_with_header(evidence)`,
  mesmo padrão de busca por conteúdo, não por posição fixa, já usado no
  resto do arquivo.
- `_framework/procedures/verify-sdd.md` (RF01): nova seção "0. Fidelidade
  à origem" antes de "1. Conformidade com a spec", citando o comando de
  `check_source_docs.py` e os 4 pontos do checklist (ADR-DTF-0007,
  Proposta da RFC-DTF-0007).
- `_framework/rules/workflow-rules.yaml`: novo changelog `2.2.0`
  (2026-09-22), `framework.version` bump de `2.1.0` para `2.2.0`.

**Não-retroatividade de RF04-06 (decisão de desenho desta SDD, não da
SPEC):** a técnica de "presença de coluna no cabeçalho" que
`check_evidence_profile` usa (SDD-DTF-0036) não é aplicável aqui porque
RF04 pede uma **linha** nova na tabela de Evidência, não uma **coluna**
nova — e a SDD que introduziu essa convenção (SDD-DTF-0037, este
documento) foi criada no mesmo dia calendário da SDD anterior mais
recente com `source_docs` não vazio (SDD-DTF-0036), o que torna
`created >= since_date` (o padrão usado por `evidence_required` e
`scope_checklist`, RULE_SINCE desde 1.7.0) insuficiente: reprovaria
SDD-DTF-0036 retroativamente, já `implemented` e mergeada antes desta
convenção existir. Resolução: nova entrada `RULE_SINCE["source_fidelity"] = "2.2.0"`
(changelog datado `2026-09-22`), mas comparação **estrita** (`created >
since_date`, não `>=`) via função local `applies_strict` em
`validate_state.py` — regra vale a partir do dia SEGUINTE ao changelog,
nunca no mesmo dia. Não chama `rule_applies` diretamente (só
`version_date` + `rule_applies_since_date` como fallback), para não
quebrar `test_nenhum_validador_chama_rule_applies_direto` (convenção já
estabelecida do arquivo).

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | `check_source_docs.py` novo, reaproveitando helpers existentes | RF02, RF03 | `_framework/scripts/check_source_docs.py` | |
| 2 | Testes de regressão de `check_source_docs.py` | RF02, RF03 | `_framework/scripts/tests/test_check_source_docs.py` | 1 |
| 3 | `check_source_fidelity` + `applies_strict` em `validate_state.py` | RF04, RF05, RF06 | `_framework/scripts/validate_state.py` | |
| 4 | Testes de regressão com sensor de discriminação (RF04-06) | RF04, RF05, RF06 | `_framework/scripts/tests/test_validate_state.py` | 3 |
| 5 | Seção "0. Fidelidade à origem" no procedimento | RF01 | `_framework/procedures/verify-sdd.md` | |
| 6 | Changelog 2.2.0 + bump de `framework.version` | RF04-06 (data de corte) | `_framework/rules/workflow-rules.yaml` | |
| 7 | Sincronizar bundle da skill principal | RF01-06 | `_framework/skills/doc-traceability-framework/` (scripts + references) | 1, 3, 6 |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — seção "0." antes de "1." com os 4 pontos nomeados | `grep -n "^### 0. Fidelidade à origem" -A1 _framework/procedures/verify-sdd.md && grep -n "^### 1. Conformidade com a spec" _framework/procedures/verify-sdd.md` | Linha de "0." tem número menor que a de "1." | manual |
| 2 | RF02/RF03 — `check_source_docs.py` mecaniza existência/status/url | `python3 -m pytest _framework/scripts/tests/test_check_source_docs.py -v` | 11 passed | automatizado |
| 3 | RF04 — `source_docs` não vazio sem linha "Fidelidade à origem" reprova (SDD nova) | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k "fidelidade or rf04 or rf05 or rf06" -v` | Todos passam | automatizado |
| 4 | RF05 — `source_docs` vazio não exige a linha | (mesmo comando do #3, inclui `test_rf05_source_docs_vazio_nao_exige_linha`) | Passa | automatizado |
| 5 | RF06 — não-retroativo (SDD-DTF-0036, criada no mesmo dia, não reprova) | (mesmo comando do #3, inclui `test_rf06_created_no_mesmo_dia_da_regra_nao_reprova_retroativamente`) | Passa | automatizado |
| 6 | Sem regressão nos validadores contra os documentos reais do projeto | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | Ambos ✅, 0 problemas (inclui SDD-DTF-0036 não reprovada) | automatizado |
| 7 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam | automatizado |
| 8 | Bundle da skill principal sincronizado | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência | automatizado |

## Instruções específicas para a IA implementadora

- Reaproveitar `load_registry`, `read_frontmatter`, `check_source_docs_urls`,
  `resolve_doc_path` já existentes — não duplicar lógica de validação de
  url em `check_source_docs.py`.
- `check_source_fidelity` busca a linha por substring em qualquer célula,
  não por coluna/posição fixa — mesma filosofia de `check_evidence`/
  `check_evidence_profile`.
- `applies_strict` (comparação `>`, não `>=`) é uma decisão de desenho
  desta SDD, não da SPEC — documentar o motivo no código (SDD-DTF-0036
  criada no mesmo dia da versão 2.2.0) para a próxima sessão não reverter
  achando que é bug.
- Não chamar `rule_applies(...)` diretamente em `validate_state.py` —
  `test_nenhum_validador_chama_rule_applies_direto` já existe e reprova
  isso; usar só `version_date` + `rule_applies_since_date` como fallback.
- Sensor de discriminação obrigatório para RF02-RF06: mutar a
  implementação, confirmar que o teste cai, reverter.
- Esta SDD não cobre item C da STRAT-DTF-0003 (nível de teste) nem
  mecaniza os itens 2-4 do checklist de RF01 (correspondência de
  requisito/critério/contrato) — continuam manuais/IA, por decisão
  explícita de ADR-DTF-0007.

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF06 todos com trecho correspondente no código/documento editado.
- [x] Nenhum arquivo tocado fora da lista de "Arquivos tocados" acima.
- [x] Nenhuma abstração/config/feature flag extra — `applies_strict` é
      requisito direto de RF06 (não-retroatividade), não scope creep.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0014 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0014.md), ADR-DTF-0007 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0007.md) |
