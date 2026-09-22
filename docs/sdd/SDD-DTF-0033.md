---
id: SDD-DTF-0033
type: SDD
title: "Despacho do verify-sdd: seção de autoridade no procedimento, coluna de rodada na evidência, teto mecanizado em validate_state.py"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0012"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0012.md"
  - id: "ADR-DTF-0006"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0006.md"
consumption_instructions: "Leia SPEC-DTF-0012 inteira antes de tocar em qualquer arquivo — os blocos de texto normativo exatos (seções Entrada/4. Veredito/Red flags) vivem na SPEC, aqui só o essencial. Se `_framework/tests/test_kit_parity.py` já existir quando esta SDD for implementada (criado por SDD-DTF-0032, que ainda não estava implemented no momento desta compilação), a task 5 estende esse arquivo em vez de criar um novo — confira antes de escrever."
supersedes: null
superseded_by: null
tags: [verify-sdd, sdd-verifier, paralelismo, autonomia, enforcement]
---

# Despacho do verify-sdd: seção de autoridade no procedimento, coluna de rodada na evidência, teto mecanizado em validate_state.py

## Resumo executivo

Fixa três regras de despacho do `sdd-verifier` decididas em
ADR-DTF-0006: só quem tem a feature inteira despacha (nunca builder de
trilha isolada), o diff de entrada é sempre `<merge-base>..HEAD` da
branch consolidada (nunca fatia de task paralela), e há teto de 3
rodadas de correção-e-reverificação antes de escalonamento obrigatório
ao humano — como texto normativo em `verify-sdd.md`, coluna `Rodada` na
tabela de evidência, e checagem mecânica nova em `validate_state.py`.

## Decisão(ões) de arquitetura aplicável(is)

ADR-DTF-0006: despacho único do `verify-sdd`, por quem tem a feature
inteira, sobre a branch consolidada, com teto de 3 rodadas e veredito
sempre reportado ao humano — nunca decidido só internamente pela
sessão. Trade-off aceito: "quem tem a feature inteira" pode ser ambíguo
em orquestração multi-agente complexa além do caso comum; não resolvido
aqui, fica para o guia de adoção do paralelismo. Teto de 3 rodadas é
ponto de partida, não medição — ajuste futuro depende de
`lessons_policy`.

## Requisitos consolidados

(Consolidado de SPEC-DTF-0012, Parte 1.)

| RF-ID | Requisito |
|---|---|
| RF01 | Procedimento declara autoridade de despacho: só quem tem visão da feature inteira que vai a PR, nunca sessão que implementou só uma trilha/task paralela isolada. |
| RF02 | Procedimento fixa escopo do diff em features paralelas: sempre `<merge-base>..HEAD` da branch consolidada, nunca diff de task isolada. |
| RF03 | Tabela de evidência (seção "4. Veredito") ganha coluna `Rodada` (número da tentativa de correção-e-reverificação, começando em 1). |
| RF04 | Teto de 3 rodadas: se veredito não for `PASS` na 3ª rodada, a sessão para de tentar sozinha e escreve seção `## Escalonado ao humano` com histórico das 3 rodadas, em vez de despachar uma 4ª tentativa. |
| RF05 | Histórico de rodadas anteriores não é sobrescrito — `validation-SDD-{ID}.md` mantém veredito e achados principais de todas as rodadas, não só a última. |
| RF06 | "Red flags" ganha 2 linhas novas: "builder despachou a própria verificação da feature" e "diff de entrada é fatia de task paralela, não a feature consolidada". |
| RF07 | `validate_state.py` reprova quando houver 3+ linhas com `Rodada` preenchida e veredito != PASS sem seção `## Escalonado ao humano` presente, mesmo com `**Veredito:**` do topo dizendo PASS. |
| RF08 | Paridade das duas cópias do script (`_framework/scripts/validate_state.py` e `_framework/skills/doc-traceability-framework/scripts/validate_state.py`), mesmo mecanismo já usado pelos demais scripts do kit. |

Casos de borda consolidados (ver SPEC-DTF-0012 para detalhe completo):
SDD sem trilha paralela — RF01 vale trivialmente, RF02 não se aplica;
verificação de rodada única com PASS de primeira — `Rodada` = 1,
RF04/RF07 não disparam; rodada 2 corrige e passa — escalonamento não
exigido, mas RF05 exige manter o registro da rodada 1 (FAIL); tabela
sem coluna `Rodada` (arquivo pré-SPEC) — tratada como rodada única,
não-retroativo, sem falha adicional só pela ausência da coluna; seção
`Escalonado ao humano` presente com menos de 3 rodadas — não é erro,
escalonar cedo por julgamento próprio é permitido.

## Especificação técnica consolidada

(Consolidado de SPEC-DTF-0012, Parte 2 — contratos, plano de
implementação e rollout completos estão na SPEC; aqui só o necessário
para implementar sem reabrir o documento de origem.)

**Mudanças em `_framework/procedures/verify-sdd.md`:**
- Seção "Entrada" ganha item: "Autoridade de despacho: só quem tem a
  feature inteira que vai a PR despacha esta verificação — nunca uma
  sessão que implementou só uma trilha/task paralela isolada
  (RFC-DTF-0006/ADR-DTF-0006)." (RF01) — e a exigência de que o diff de
  entrada seja `<merge-base>..HEAD` da branch consolidada (RF02).
- Seção "4. Veredito": tabela de evidência ganha `Rodada` como primeira
  coluna:
  ```
  | Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? |
  |---|---|---|---|---|---|
  | 1 | 1 | `<comando>` | `<saída real>` | <resultado> | Sim |
  ```
  (RF03) — e texto novo logo após, explicando o teto de 3 rodadas
  (RF04) e o formato da seção a acrescentar quando atingido:
  ```
  ## Escalonado ao humano
  Rodadas tentadas: 3. Veredito de cada uma: <FAIL, FAIL, FAIL | resumo>.
  Motivo de cada falha: <resumo por rodada>.
  ```
  RF05 (histórico preservado) é regra de conteúdo na mesma seção — não
  sobrescrever rodadas anteriores.
- Seção "Red flags": 2 linhas novas na tabela (RF06).

**Mudança em `validate_state.py`:**
- Função nova `check_verification_rounds(validation_path: Path) ->
  list[str]` (mensagens de erro, vazia se ok), chamada a partir da
  checagem já existente do gate 16:
  1. Parseia a tabela de evidência linha a linha, lê coluna `Rodada`
     (ausente → trata tabela inteira como rodada 1).
  2. Agrupa por número de rodada; qualquer linha != PASS numa rodada
     torna aquela rodada "não-PASS".
  3. Se houver 3+ rodadas "não-PASS" e a string `## Escalonado ao
     humano` não aparecer no arquivo, retorna erro citando `SDD-ID` e o
     número de rodadas sem escalonamento.
- Replicar em `_framework/skills/doc-traceability-framework/scripts/validate_state.py`
  (RF08).

**Fora de escopo desta SDD** (herdado da SPEC): automatizar contagem de
rodadas via commit/timestamp; definir "quem tem a feature inteira" além
do caso comum; mudar o valor do teto (3); integração com o gate de CI
(SPEC-DTF-0011/SDD-DTF-0032 — scripts diferentes, sem sobreposição);
retroatividade em `validation-*.md` já existentes.

**Rollout:** não retroativo — vale a partir da próxima verificação
despachada após o merge; `validation-*.md` existentes não são
reabertos. Rollback: reverter os commits de procedimento/script; sem
migração de dado.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Texto normativo em `verify-sdd.md`: seção "Entrada" (autoridade + escopo do diff) | RF01, RF02 | `_framework/procedures/verify-sdd.md` | |
| 2 | Texto normativo em `verify-sdd.md`: coluna `Rodada` na tabela de evidência (seção "4. Veredito") e regra do teto/escalonamento | RF03, RF04, RF05 | `_framework/procedures/verify-sdd.md` | |
| 3 | Texto normativo em `verify-sdd.md`: 2 linhas novas em "Red flags" | RF06 | `_framework/procedures/verify-sdd.md` | |
| 4 | `check_verification_rounds()` em `validate_state.py`, chamada a partir do gate 16 existente | RF07 | `_framework/scripts/validate_state.py` | |
| 5 | Cópia bundlada byte-idêntica | RF08 | `_framework/skills/doc-traceability-framework/scripts/validate_state.py` | 4 |
| 6 | Testes de `check_verification_rounds()` (inclui sensor de discriminação RF07) e teste de paridade | RF07, RF08 | `_framework/tests/test_validate_state.py`, `_framework/tests/test_kit_parity.py` | 4, 5 |
| 7 | Confirmar `.claude/agents/sdd-verifier.md` continua consistente após RF01-RF06 (sem mudança de conteúdo esperada — só verificação) | (decisão pura) | `.claude/agents/sdd-verifier.md` (leitura; edita só se inconsistente) | 1, 2, 3 |

Tasks 1, 2 e 3 tocam o mesmo arquivo (`verify-sdd.md`) — não
paralelizáveis entre si apesar de RFs diferentes (interseção de
arquivo força bloqueio, `parallel_plan.py`). Task 4 é independente das
1-3 (arquivo diferente), paralelizável com elas. Task 5 depende de 4.
Task 6 depende de 4 e 5 (testa o resultado das duas). Task 7 depende de
1-3 (só faz sentido checar depois do texto normativo definido).

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01/RF02 — item de autoridade e escopo do diff na seção "Entrada" | `grep -n "Autoridade de despacho\|merge-base" _framework/procedures/verify-sdd.md` | Ambos os termos presentes na seção "Entrada" |
| 2 | RF03 — coluna `Rodada` na tabela de evidência da seção "4. Veredito" | `grep -n "Rodada" _framework/procedures/verify-sdd.md` | Coluna `Rodada` presente no bloco de exemplo da tabela |
| 3 | RF04/RF05 — regra do teto e formato da seção de escalonamento documentados | `grep -n "Escalonado ao humano\|3 rodadas\|3ª rodada" _framework/procedures/verify-sdd.md` | Termos presentes, com o bloco de exemplo de "Escalonado ao humano" |
| 4 | RF06 — 2 linhas novas em "Red flags" | `grep -n "despachou a própria verificação\|fatia de task paralela" _framework/procedures/verify-sdd.md` | Ambas as linhas presentes na tabela de "Red flags" |
| 5 | RF07 — 3 rodadas não-PASS sem escalonamento reprova (sensor de discriminação) | `python3 -m pytest _framework/tests/test_validate_state.py::test_tres_rodadas_sem_escalonamento_reprova -v` | Teste passa |
| 6 | RF07 — 3 rodadas não-PASS COM escalonamento passa | `python3 -m pytest _framework/tests/test_validate_state.py::test_tres_rodadas_com_escalonamento_passa -v` | Teste passa |
| 7 | RF07 — 2 rodadas não-PASS sem escalonamento, abaixo do teto, passa | `python3 -m pytest _framework/tests/test_validate_state.py::test_duas_rodadas_sem_escalonamento_passa -v` | Teste passa |
| 8 | RF07 — tabela sem coluna `Rodada` não quebra o script | `python3 -m pytest _framework/tests/test_validate_state.py::test_tabela_sem_coluna_rodada_trata_como_unica -v` | Teste passa |
| 9 | RF08 — paridade das duas cópias de `validate_state.py` | `python3 -m pytest _framework/tests/test_kit_parity.py::test_validate_state_paridade -v` | Teste passa |
| 10 | Nenhuma regressão no restante do gate 16 | `python3 -m pytest _framework/tests/test_validate_state.py -v` | Todos os testes (novos e existentes) passam |
| 11 | `.claude/agents/sdd-verifier.md` consistente com o procedimento atualizado | `grep -n "verify-sdd.md" .claude/agents/sdd-verifier.md` | Referência ao procedimento normativo continua presente e correta |

## Instruções específicas para a IA implementadora

- Editar `verify-sdd.md` uma vez só, cobrindo as 3 mudanças (tasks 1-3)
  — não são independentes na prática porque tocam o mesmo arquivo;
  agrupar não é scope creep.
- RF07 exige sensor de discriminação real: aplicar mutação que quebra
  `check_verification_rounds()` (ex.: trocar `>= 3` por `> 3`, ou
  ignorar a checagem de "Escalonado ao humano"), confirmar que o teste
  falha, reverter, confirmar que volta a passar. Teste verde sem
  mutação testada não conta como "Sim" na tabela de evidência final.
- Antes de criar `_framework/tests/test_kit_parity.py` (task 6),
  confira se SDD-DTF-0032 já o criou (ela também tem RF10 de paridade,
  para `ci_gate_verify_sdd.py`) — se existir, estenda com
  `test_validate_state_paridade` em vez de duplicar o mecanismo.
- `check_verification_rounds()` entra no mesmo loop de checklist já
  existente do gate 16 em `validate_state.py` — não criar função de
  validação paralela e desconectada das demais (mesmo padrão de
  SDD-DTF-0030 para `check_files_column`/`check_tasks_section`).
- Não alterar `ci_gate_verify_sdd.py` nem qualquer arquivo de
  SDD-DTF-0032 — scripts diferentes, sem sobreposição de escopo (ver
  "Fora de escopo").
- Não implementar contagem automática de rodadas via commit/timestamp
  nem mudar o valor do teto (3) — fora de escopo explícito da SPEC.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima (RF01-RF08) tem código correspondente.
- [ ] Todo arquivo tocado pela implementação aparece na tabela "Decomposição em tasks" acima.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra sem requisito consolidado (ex.: não automatizar contagem de rodadas, não mudar o teto — fora de escopo, ver "Instruções específicas").

## Evidência de verificação (preencher antes de status `implemented`)

(Preencher pela skill `verify-sdd`, em sessão separada da que implementou.)

**Verificador independente:** {a preencher}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0012, ADR-DTF-0006 |
