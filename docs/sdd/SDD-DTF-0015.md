---
id: SDD-DTF-0015
type: SDD
title: "Consolida config do ruff em pyproject.toml (sensor de formatter só olha lá)"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-04"
updated: "2026-09-04"
relates_to: [SDD-DTF-0014]
source_docs: []
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada, não falha de processo. Escopo mecânico: move ruff.toml -> [tool.ruff] em pyproject.toml, mesma config, formato aninhado."
supersedes: null
superseded_by: null
tags: [tooling, higiene, kit-publico]
---

# Consolida config do ruff em pyproject.toml (sensor de formatter só olha lá)

## Resumo executivo

`SDD-DTF-0014` adicionou `[format]` a `ruff.toml` pra fechar SNS-04, mas
o achado persistiu na rodada seguinte. Usuário trouxe a regra exata do
sensor: SNS-04 procura `pyproject.toml` com seção `[tool.black]` ou
`[tool.ruff]` — não reconhece `ruff.toml` separado, mesmo com
`[format]` presente. Gap real, não falso positivo (confirmado com a
regra exata do sensor antes de agir, não só o texto do score).

`sizing: small` — 2 arquivos (`pyproject.toml`, remoção de
`ruff.toml`), sem mudança de comportamento (mesma config, arquivo
diferente).

## Decisão(ões) de arquitetura aplicável(is)

Nenhuma.

## Requisitos consolidados

- Config do `ruff` (lint + format) sai de `/ruff.toml` e entra em
  `/pyproject.toml` sob `[tool.ruff]`, `[tool.ruff.lint]` e
  `[tool.ruff.format]` (sintaxe aninhada exigida pelo `ruff` quando a
  config vive em `pyproject.toml`, diferente do formato "flat" de
  `ruff.toml`).
- `/ruff.toml` é removido — `ruff` prioriza `ruff.toml` sobre
  `pyproject.toml` quando os dois existem no mesmo diretório; manter
  os dois seria uma armadilha (editar um e o outro continuar valendo).
- Nenhum valor de config muda: `target-version`, `line-length`,
  `exclude`, `select`, `quote-style`, `indent-style` idênticos aos de
  `SDD-DTF-0014`.

Casos de borda: nenhum — mudança puramente de localização de config.

Fora de escopo: mudar qualquer valor de lint/format; mexer em
`pyproject.toml` além da seção `[tool.ruff]` (as seções `[tool.pytest.ini_options]`/`[tool.mypy]` de `SDD-DTF-0013` continuam intocadas).

## Especificação técnica consolidada

**`/pyproject.toml`** (seção nova, resto do arquivo intocado):
```toml
[tool.ruff]
target-version = "py312"
line-length = 120
exclude = ["examples/**"]

[tool.ruff.lint]
select = ["E", "F", "I", "W"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**`/ruff.toml`**: removido.

## Critérios de aceite / definição de pronto

| # | Critério | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | `ruff.toml` não existe mais | `test -f ruff.toml; echo $?` | `1` (arquivo ausente) |
| 2 | `pyproject.toml` tem `[tool.ruff]` | `grep -n "\[tool.ruff\]" pyproject.toml` | 1 ocorrência |
| 3 | `ruff check` continua limpo, mesma config | `ruff check --show-settings _framework/scripts \| grep -E "line-length\|target-version"` e `ruff check _framework/scripts` | mesmos valores de antes (`line-length = 120`, py312), `exit 0` |
| 4 | `ruff format` continua sem reformatar nada | `ruff format --check _framework/scripts` | `exit 0`, "10 files already formatted" |
| 5 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` e `pytest` | `exit 0` nos dois |

## Instruções específicas para a IA implementadora

- Não mudar nenhum valor — só realocar. Rodar `ruff check
  --show-settings` antes (com `ruff.toml`) e depois (com
  `pyproject.toml`) e comparar, não só rodar `ruff check` puro.
- `git rm ruff.toml`, não só deletar — precisa aparecer no diff do
  commit.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0015`.
- Branch dedicada a partir de `main`, PR — nunca commit direto em main
  (gate seção 14).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Requisito consolidado tem código correspondente.
- [x] Únicos 2 arquivos tocados (`pyproject.toml` editado,
      `ruff.toml` removido), ambos listados acima.
- [x] Nenhum valor de config mudou, nenhuma abstração extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** pendente — esta tabela é do
implementador, mesma sessão.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `test -f ruff.toml; echo $?` | `1` | — | Sim |
| 2 | `grep -n "\[tool.ruff\]" pyproject.toml` | 1 ocorrência (linha 1) | — | Sim |
| 3 | `ruff check --show-settings` (antes/depois) e `ruff check _framework/scripts` | `line_length = 120`, `target_version = 3.12` idênticos ao "antes"; `All checks passed!` | — | Sim |
| 4 | `ruff format --check _framework/scripts` | `10 files already formatted` | — | Sim |
| 5 | `framework_check.py --auto` e `pytest` | `✅ Todas as verificações do framework passaram.`, `7 passed` | — | Sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| Branch | `sdd/SDD-DTF-0015-ruff-config-pyproject` |
