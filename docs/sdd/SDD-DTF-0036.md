---
id: SDD-DTF-0036
type: SDD
title: "Evidência de verificação com file:line da asserção e perfil declarado por critério"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0013"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0013.md"
consumption_instructions: "Leia SPEC-DTF-0013 inteira antes de tocar em qualquer arquivo — esta SDD consolida Parte 1/Parte 2, mas o texto completo de cada caso de borda vive só na SPEC. RF03/RF04/RF06 exigem sensor de discriminação real (mutação que quebra o comportamento e volta a passar depois). Editar sempre as duas cópias do kit (_framework/scripts/ e _framework/skills/doc-traceability-framework/scripts/) no mesmo commit — ou deixar a sincronização para render_prompts.py, nunca editar a cópia bundlada à mão."
supersedes: null
superseded_by: null
tags: [verify-sdd, gate_scope_verification, tlc-spec-lean, evidencia]
---

# Evidência de verificação com file:line da asserção e perfil declarado por critério

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`).

## Resumo executivo

A evidência de verificação hoje prova que um comando rodou e teve
saída — não prova que a asserção testada é a que realmente resolve o
critério (E4, tlc-spec-lean), nem impede que um critério perca
silenciosamente seu teste automatizado e passe a ser verificado
manualmente entre uma rodada de correção e outra (E5). Esta SDD
acrescenta duas colunas por tabela (Perfil esperado nos Critérios de
aceite; Assertion file:line + Perfil usado na Evidência) e mecaniza as
duas checagens em `validate_state.py`, não-retroativamente.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — SPEC-DTF-0013 já declara sizing `medium` e nenhum critério de
`decision_gates.rfc_to_adr` se aplica (extensão de validador existente,
sem novo padrão arquitetural, sem troca de tecnologia).

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | Template de SDD ganha coluna "Perfil esperado" (`automatizado` \| `manual` \| `n/a`) na tabela de Critérios de aceite / definição de pronto. |
| RF02 | Template de SDD ganha colunas "Assertion (file:line)" e "Perfil usado" na tabela de Evidência de verificação. |
| RF03 | SDD `implemented` com linha de evidência cujo critério correspondente tem perfil esperado `automatizado` e célula "Assertion (file:line)" vazia → `validate_state.py` reporta problema. |
| RF04 | "Perfil usado" divergente de "Perfil esperado" do critério correspondente, sem justificativa entre parênteses na célula → `validate_state.py` reporta problema. |
| RF05 | Perfil esperado `manual` ou `n/a` → `validate_state.py` não exige "Assertion (file:line)" preenchida (aceita `n/a`). |
| RF06 | Tabela de Evidência sem as colunas novas no cabeçalho (formato anterior) → RF03/RF04 não se aplicam a essa SDD (não retroativo, mesma técnica de `RULE_SINCE`). |
| RF07 | `_framework/procedures/verify-sdd.md` cita `file:line` da asserção e a regra de divergência de perfil, referenciando STRAT-DTF-0003 E4/E5. |

## Especificação técnica consolidada

Arquivos tocados (produto):
- `_framework/templates/sdd.template.md` (RF01, RF02).
- `_framework/scripts/validate_state.py`, replicado em
  `_framework/skills/doc-traceability-framework/scripts/validate_state.py`
  via `render_prompts.py` (RF03-RF06): nova função
  `check_evidence_profile(doc_id, criteria, evidence) -> list[str]`,
  chamada por `check_sdd` junto de `check_evidence`; `check_sdd` passa a
  extrair `criteria` (já extraído hoje só para `n_criteria`) e repassá-lo.
  Nova entrada `"evidence_profile": "<versão corrente>"` em `RULE_SINCE`.
- `_framework/procedures/verify-sdd.md` (RF07).

Detecção de coluna por substring no cabeçalho, case-insensitive — mesmo
padrão de `cmd_idx`/`sensor_idx` já existentes em `check_evidence`,
nunca por posição fixa. Correspondência entre linha de critério e linha
de evidência pela célula "#" (primeira coluna de cada tabela).

- RF01/RF02: acrescentar as colunas nas duas tabelas do template, com
  uma linha de instrução curta acima de cada uma.
- RF03: em `check_evidence_profile`, localizar `perfil_esperado_idx` no
  cabeçalho de `criteria` (substring "perfil esperado") e
  `assertion_idx`/`perfil_usado_idx` no cabeçalho de `evidence`
  (substring "assertion"/"file:line" e "perfil usado"). Montar
  `esperado_por_criterio: dict[str, str]` a partir de `criteria` (chave =
  célula "#"). Para cada linha de `evidence`, se
  `esperado_por_criterio.get(row["#"]) == "automatizado"` e
  `row[assertion_idx]` vazio → problema.
- RF04: mesma correspondência; se `row[perfil_usado_idx].strip()` não
  vazio, diferente (case-insensitive) do esperado, e não contém `(` →
  problema.
- RF05: guard — só aplica RF03 quando esperado é `automatizado`
  (implícito na condição acima).
- RF06: guard no início de `check_evidence_profile` — se
  `assertion_idx is None or perfil_usado_idx is None`, retorna `[]`
  imediatamente (colunas não existem no cabeçalho de evidência).
- RF07: duas frases objetivas no procedimento `verify-sdd.md`, seções
  "3. Sensor de discriminação" (file:line) e uma nova observação sobre
  perfil, citando STRAT-DTF-0003 item 7 (E4/E5).

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Colunas novas no template de SDD | RF01, RF02 | `_framework/templates/sdd.template.md` | |
| 2 | Mecanizar `check_evidence_profile` em validate_state.py | RF03, RF04, RF05, RF06 | `_framework/scripts/validate_state.py` | |
| 3 | Testes de regressão com sensor de discriminação | RF03, RF04, RF05, RF06 | `_framework/scripts/tests/test_validate_state.py` | 2 |
| 4 | Citar file:line + perfil no procedimento verify-sdd | RF07 | `_framework/procedures/verify-sdd.md` | |
| 5 | Sincronizar bundle da skill principal | RF03-RF06 | `_framework/skills/doc-traceability-framework/scripts/validate_state.py` | 2 |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — coluna "Perfil esperado" no template | `grep -n "Perfil esperado" _framework/templates/sdd.template.md` | Ao menos 1 ocorrência | manual |
| 2 | RF02 — colunas "Assertion (file:line)" e "Perfil usado" no template | `grep -n "Assertion (file:line)\|Perfil usado" _framework/templates/sdd.template.md` | Ao menos 2 ocorrências | manual |
| 3 | RF03 — Assertion vazia com perfil automatizado reprova | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k "perfil or colunas_novas" -v` | Todos passam (7) | automatizado |
| 4 | RF04 — perfil divergente sem justificativa reprova | (mesmo comando do #3, inclui `test_perfil_divergente_sem_justificativa_reprova`) | Passa | automatizado |
| 5 | RF05 — perfil manual/n-a com Assertion vazia não reprova | (mesmo comando do #3, inclui `test_perfil_manual_nao_exige_assertion`) | Passa | automatizado |
| 6 | RF06 — tabela sem colunas novas não reprova retroativamente | (mesmo comando do #3, inclui `test_sem_colunas_novas_nao_reprova_retroativamente` e `test_criterios_sem_coluna_perfil_esperado_nao_reprova`) | Passa | automatizado |
| 7 | RF07 — procedimento cita file:line e regra de perfil | `grep -icE "file:line|perfil (esperado\|usado)" _framework/procedures/verify-sdd.md` | >= 2 | manual |
| 8 | Sem regressão nos validadores contra os documentos reais do projeto | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | Ambos ✅, 0 problemas | automatizado |
| 9 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam | automatizado |
| 10 | Bundle da skill principal sincronizado | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência | automatizado |

## Instruções específicas para a IA implementadora

- Reaproveitar exatamente o padrão de `cmd_idx`/`sensor_idx` (busca por
  substring no cabeçalho) — não introduzir parsing por posição fixa.
- Correspondência entre tabelas é pela célula "#", não pela ordem das
  linhas — uma tabela de evidência pode ter mais linhas que a de
  critérios quando há múltiplas rodadas (coluna "Rodada", SDD-DTF-0033).
- Não tocar em `check_evidence`, `check_verification_rounds` ou
  `check_scope` além do necessário para `check_sdd` passar `criteria`
  para a nova função — são funções de outro RF/SDD.
- Adicionar `"evidence_profile"` a `RULE_SINCE` com a versão do
  framework vigente no `framework:version` de `workflow-rules.yaml` no
  momento do commit (ler o valor, não hardcode um número arbitrário).
- Sensor de discriminação obrigatório para RF03, RF04, RF05 e RF06:
  mutar a implementação, confirmar que o teste cai, reverter.
- Esta SDD não cobre o item C da STRAT-DTF-0003 (nível de teste) — não
  invente lógica de "qual perfil um critério deveria ter", só declare e
  compare o que já está escrito nas tabelas.

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF07 todos com trecho correspondente no código/documento editado.
- [x] Nenhum arquivo tocado fora da lista de "Arquivos tocados" acima.
- [x] Nenhuma mudança em `workflow-rules.yaml` — nem changelog (RF06
      tornou a checagem não-retroativa por detecção de coluna, sem
      precisar de `RULE_SINCE`/versão nova, mesmo padrão de
      `check_verification_rounds`, SDD-DTF-0033).

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** {preencher na sessão de verificação}

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0013 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0013.md) |
