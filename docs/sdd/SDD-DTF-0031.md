---
id: SDD-DTF-0031
type: SDD
title: "check_ears confunde coluna Arquivos com critério em SPEC de 4 colunas"
status: draft
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0030]
source_docs: []
consumption_instructions: "Bug fix pontual, sizing small — sem SPEC/RFC. Aplicar o fix nas duas cópias do kit (_framework/scripts e _framework/skills/doc-traceability-framework/scripts) e rodar a suíte completa antes de commitar."
supersedes: null
superseded_by: null
tags: [bugfix, validate_doc, ears, gate_content_quality]
---

# check_ears confunde coluna Arquivos com critério em SPEC de 4 colunas

## Resumo executivo

`check_ears` (`validate_doc.py`) usava `cells[-1]` (última coluna) como
o critério de aceite de um RF. Isso era certo enquanto a tabela de
"Requisitos funcionais" da SPEC tinha 3 colunas (RF-ID, Requisito,
Critério). SDD-DTF-0030 acrescentou uma 4a coluna (`Arquivos`) — a
partir daí, `cells[-1]` passou a ser `Arquivos`, não o critério, e toda
SPEC que adota a coluna nova (o padrão que a própria 0030 introduziu)
passa a ser reprovada com uma mensagem de erro que cita o conteúdo de
`Arquivos` em vez do critério real. Achado ao escrever SPEC-EVM-0010
(primeira SPEC de projeto a usar a coluna nova em produção).

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — bug fix pontual, sizing `small`, nenhum critério do gate
`rfc_to_adr` se aplica.

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | `check_ears` deve identificar o critério de aceite pela 3a coluna (índice 2) da tabela de "Requisitos funcionais", não pela última — funciona tanto para tabela de 3 colunas (RF-ID, Requisito, Critério) quanto de 4 (mais Arquivos, SDD-DTF-0030). |

## Especificação técnica consolidada

`_framework/scripts/validate_doc.py`, função `check_ears`: trocar
`rf_id, criterion = cells[0], cells[-1]` por
`rf_id, criterion = cells[0], cells[2]`. Como a função já garante
`len(cells) >= 3` antes desse ponto, `cells[2]` sempre existe e é
sempre o critério, independente de haver ou não a 4a coluna
`Arquivos` depois dele.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — critério correto com tabela de 4 colunas, EARS válido | `python3 -m pytest _framework/tests/test_validate_doc.py::test_ears_nao_confunde_coluna_arquivos_com_criterio -v` | Passa |
| 2 | RF01 — critério malformado ainda é pego, citando o texto certo | `python3 -m pytest _framework/tests/test_validate_doc.py::test_ears_ainda_pega_criterio_malformado_com_coluna_arquivos -v` | Passa |
| 3 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam |
| 4 | Paridade entre as duas cópias do kit | `diff _framework/scripts/validate_doc.py _framework/skills/doc-traceability-framework/scripts/validate_doc.py` | Sem saída |

## Instruções específicas para a IA implementadora

- Fix de uma linha (`cells[2]` em vez de `cells[-1]`) — não aproveitar
  para refatorar `check_ears` além disso.
- Aplicar nas duas cópias do kit.
- Adicionar teste de regressão que discrimina o bug (sensor: reverter o
  fix e confirmar que o teste novo falha).

## Verificação de escopo (nada a mais, nada a menos)

- [ ] RF01 com código correspondente.
- [ ] Único arquivo de produto tocado: `validate_doc.py` (2 cópias) + arquivo de teste.
- [ ] Nenhuma mudança em `check_files_column` nem em qualquer outra função — escopo é só `check_ears`.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** {a preencher}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
