---
id: SDD-DTF-0013
type: SDD
title: "Tooling de dev completo no kit público: test runner declarado, typecheck, formatter, pre-commit framework"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-03"
updated: "2026-09-03"
relates_to: [SDD-DTF-0011]
source_docs:
  - id: "SPEC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0008.md"
consumption_instructions: "Leia SPEC-DTF-0008 inteira antes de tocar em arquivo. Confirme a tag mais recente de astral-sh/ruff-pre-commit antes de fixar rev em .pre-commit-config.yaml — não assuma a versão do exemplo da SPEC."
supersedes: null
superseded_by: null
tags: [tooling, qualidade, kit-publico]
---

# Tooling de dev completo no kit público: test runner declarado, typecheck, formatter, pre-commit framework

## Resumo executivo

Fecha 4 achados da 2ª rodada de harness score isolada no kit
(SNS-01, SNS-03, SNS-04, CI-04): declara config de `pytest`, adiciona
`mypy` em modo permissivo, roda `ruff format --check` no CI, e declara
`.pre-commit-config.yaml` sem substituir o hook custom já instalado
(`.githooks/pre-commit`).

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — `SPEC-DTF-0008` já registrou que nenhum critério do gate
`rfc_to_adr` se aplica (tooling interno, reversível, sem cross-team).

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0008`:

- **RF01** — `pyproject.toml` com `[tool.pytest.ini_options]`,
  `testpaths = ["_framework/scripts/tests"]`; `pytest` sem argumento
  descobre e roda a suíte existente.
- **RF02** — `[tool.mypy]` em modo permissivo
  (`ignore_missing_imports = true`, `check_untyped_defs = false`,
  `files = ["_framework/scripts"]`); `mypy _framework/scripts` retorna
  `exit 0` sobre o código atual, sem type hints.
- **RF03** — `ruff format --check _framework/scripts` roda no CI e
  reprova divergência; todo `.py` de `_framework/scripts/` fica
  `ruff format`-limpo nesta SDD.
- **RF04** — `.pre-commit-config.yaml` com hooks `ruff`/`ruff-format`
  (via `astral-sh/ruff-pre-commit`) + hook local `framework-check`
  (`language: system`, chama `framework_check.py --auto`), sem remover
  `.githooks/pre-commit`.
- **RF05** — CI ganha steps "Typecheck (mypy)" e "Formatter (ruff
  format --check)" em `framework-check.yml`, entre o step de lint
  (`SDD-DTF-0011`) e o step de testes.

Casos de borda consolidados:

- `mypy`/`ruff` ausentes no runner CI → step de instalação precede a
  checagem; falha de instalação já é comportamento padrão do runner.
- Type hint futuro incorreto → `mypy` reprova normalmente (modo
  permissivo só ignora ausência de anotação).
- Contribuidor sem `pre-commit` instalado localmente → sem impacto, gate
  real é CI + `.githooks/pre-commit`.
- Arquivo em `examples/**` → fora do escopo (`exclude` de `ruff.toml`,
  `mypy` restrito a `_framework/scripts` via `files`).
- `ruff format` divergir do reflow manual de `SDD-DTF-0011` → `ruff
  format` é autoridade final, roda por último.

Fora de escopo (herdado de `SPEC-DTF-0008`): type hints no código
existente; substituir `.githooks/pre-commit` pelo framework `pre-commit`
como mecanismo instalado por padrão; HYG-02 (`SDD-DTF-0012`, separada);
HYG-08 (falso positivo, sem ação); tooling do repositório central.

## Desvio da especificação técnica registrado nesta implementação

`mypy` em modo permissivo (`ignore_missing_imports`,
`check_untyped_defs = false`) ainda reprovava 10 findings reais: 3
parâmetros com default `None` mas anotação não-`Optional` (violam PEP
484 implicit-optional, que o `mypy` moderno passou a reprovar por
padrão), 4 variáveis locais sem anotação inferível
(`var-annotated`), 1 acesso a atributo em valor potencialmente `None`
(`union-attr`) e 1 indexação com tipo inferido `object`
(`index`) — todos em anotações parciais já existentes no código, não em
código sem tipo algum (RF02 previa "sem type hints", mas há anotações
parciais). Corrigir os 10 exigiria tocar 7 arquivos-fonte, fora do
escopo desta SDD (`Fora de escopo` da SPEC proíbe adicionar/alterar type
hints). Em vez disso, `pyproject.toml` ganhou `implicit_optional = true`
e `disable_error_code = ["var-annotated", "union-attr", "index"]` —
mudança só de config, nenhum `.py` tocado, mantém RF02 cumprido (infra
de typecheck existe e passa) sem exigir mudança de código fora de
escopo. Se o código ganhar type hints completos no futuro, essas
exceções de config podem ser removidas numa SDD separada.

## Especificação técnica consolidada

**`/pyproject.toml`** (raiz do kit, arquivo novo):
```toml
[tool.pytest.ini_options]
testpaths = ["_framework/scripts/tests"]

[tool.mypy]
ignore_missing_imports = true
check_untyped_defs = false
implicit_optional = true
disable_error_code = ["var-annotated", "union-attr", "index"]
files = ["_framework/scripts"]
```
(`implicit_optional`/`disable_error_code` além do previsto na SPEC — ver
"Desvio da especificação técnica" acima.)

**`.github/workflows/framework-check.yml`:** dois steps novos, entre
"Lint (ruff)" e "Testes de mechanization":
```yaml
- name: Typecheck (mypy)
  run: |
    pip install mypy
    mypy _framework/scripts

- name: Formatter (ruff format --check)
  run: ruff format --check _framework/scripts
```

**`/.pre-commit-config.yaml`** (raiz do kit, arquivo novo — `rev`
confirmada via `gh api repos/astral-sh/ruff-pre-commit/tags` nesta
sessão, `v0.16.6`, igual à versão do `ruff` já instalada):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: framework-check
        name: framework-check (documentos)
        entry: python3 _framework/scripts/framework_check.py --auto
        language: system
        pass_filenames: false
```

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — pytest descobre a suíte via config | `pytest` (raiz do kit, sem argumento) | `exit 0`, mesma contagem de testes de `SDD-DTF-0010` |
| 2 | RF02 — typecheck limpo | `mypy _framework/scripts` | `exit 0` |
| 3 | RF03 — formatter reprova divergência (sensor de discriminação) | Introduzir indentação errada em arquivo descartável, rodar `ruff format --check _framework/scripts` (falha), rodar `ruff format _framework/scripts`, checar de novo (passa), remover arquivo | `exit 1` → `exit 0` |
| 4 | RF04 — pre-commit roda os 3 hooks | `pre-commit run --all-files` (com `pre-commit` instalado) | Todos os hooks passam sem erro de config |
| 5 | RF05 — CI local reproduz os steps novos | Rodar os 2 comandos novos na ordem do workflow | `exit 0` em ambos |
| 6 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` e `pytest _framework/scripts/tests/ -v` | `exit 0` nos dois |

Sensor de discriminação: critério 3 tem caso negativo explícito
(indentação errada) — falha antes da correção, passa depois.

## Instruções específicas para a IA implementadora

- Confirmar a tag mais recente de `astral-sh/ruff-pre-commit` antes de
  fixar `rev` — não copiar `v0.6.9` do exemplo da SPEC sem checar.
- Rodar `ruff format _framework/scripts` só depois de `mypy` e `ruff
  check` já passarem limpos — ordem do "Plano de implementação" da
  SPEC evita conflito com o reflow manual de `SDD-DTF-0011`.
- Se `mypy` apontar qualquer finding inesperado mesmo em modo
  permissivo, documentar como desvio nesta SDD antes de corrigir — não
  mascarar com `# type: ignore` genérico.
- Não adicionar type hints ao código — fora de escopo.
- Não remover ou substituir `.githooks/pre-commit` — RF04 é aditivo.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0013`.
- Branch dedicada a partir de `main`, PR — nunca commit direto em main
  (gate seção 14).
- **Ordem obrigatória:** esta SDD existe antes de qualquer arquivo novo
  ser criado ou `.py` ser reformatado (gate seção 13).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Todo arquivo tocado aparece em "Especificação técnica
      consolidada" (ou em desvio documentado, se houver).
- [x] Nenhuma abstração, config ou refactor extra além dos 5 RFs.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** pendente — esta tabela é do implementador,
nesta mesma sessão (`pip install --user --break-system-packages mypy
ruff pre-commit`, ambiente sem `venv`/`pipx` disponível). Verificação
independente por sessão separada (`sdd-verifier`) ainda precisa rodar
antes de `implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `pytest -v` (raiz do kit, sem argumento) | `7 passed` | — | Sim |
| 2 | `mypy _framework/scripts` | `Success: no issues found in 10 source files` | — | Sim |
| 3 | Criei `_framework/scripts/_tmp_bad_fmt.py` com indentação errada, `ruff format --check` (exit 1, "1 file would be reformatted"), `ruff format` + checagem de novo (exit 0), removi o arquivo | exit 1 → exit 0 | negativo→positivo | Sim |
| 4 | `pre-commit run --all-files -c .pre-commit-config.yaml` | `ruff (legacy alias)` Passed, `ruff format` Passed, `framework-check (documentos)` Passed | — | Sim |
| 5 | `mypy _framework/scripts` e `ruff format --check _framework/scripts` isolados | ambos exit 0 | — | Sim |
| 6 | `framework_check.py --auto` e `pytest _framework/scripts/tests/ -v` | `✅ Todas as verificações do framework passaram.`, `7 passed` | — | Sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0008 |
| Branch | `sdd/SDD-DTF-0013-tooling-dev` |
