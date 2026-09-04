# Verificação — SDD-DTF-0013

- **Veredito:** PASS
- **Diff verificado:** `b90b023..13e206d` (commit `13e206d` "feat(tooling): test runner declarado, mypy, ruff format, pre-commit"), mergeado em `main` via PR #40 (merge commit `83d30bc`).
- **Verificador independente:** sim — subagente `sdd-verifier` dedicado, sem contexto herdado da sessão que implementou (leu só a SDD e o diff). Ambiente já tinha `pytest`/`mypy`/`ruff`/`pre-commit` instalados via `pip install --user --break-system-packages`; não precisou instalar nada.

| # | Critério (RF-ID) | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF01 — pytest descobre a suíte via config (`testpaths`) | `pytest -v` (raiz, sem argumento) | `configfile: pyproject.toml`, `testpaths: _framework/scripts/tests`, `7 passed in 0.14s` | — | Sim |
| 2 | RF02 — mypy modo permissivo, `exit 0` | `mypy _framework/scripts` | `Success: no issues found in 10 source files` | — | Sim |
| 3 | RF03 — `ruff format --check` reprova divergência | `ruff format --check _framework/scripts` (baseline) → `10 files already formatted`, exit 0 | ver sensor abaixo | negativo→positivo (rodado) | Sim |
| 4 | RF04 — pre-commit roda os 3 hooks novos, `.githooks/pre-commit` preservado | `pre-commit run --all-files -c .pre-commit-config.yaml`; `cat .githooks/pre-commit` | `ruff Passed`, `ruff format Passed`, `framework-check Passed`; hook original intacto, sem alteração | — | Sim |
| 5 | RF05 — CI ganha steps novos, na ordem certa | Inspeção de `.github/workflows/framework-check.yml` + replay local de `mypy _framework/scripts` e `ruff format --check _framework/scripts` | Steps "Typecheck (mypy)" e "Formatter (ruff format --check)" presentes, nesta ordem, entre "Lint (ruff)" e "Testes de mechanization"; ambos os comandos `exit 0` isolados | — | Sim |
| 6 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto`; `pytest _framework/scripts/tests/ -v` | `✅ Todas as verificações do framework passaram.`; `7 passed` | — | Sim |
| 7 | `ruff check` (lint, não regressão de SDD-DTF-0011) | `ruff check _framework/scripts` | `All checks passed!`, exit 0 | — | Sim |
| 8 | Sincronização das cópias mecanizadas (`_framework/skills/.../scripts/*.py`) | `python3 _framework/scripts/render_prompts.py --check` | Todos os 9 scripts + `references/workflow-rules.yaml` reportados sincronizados, exit 0 | — | Sim |

## Sensor de discriminação (critério 3)

Backup de `_framework/scripts/validate_doc.py`, quebrei formatação
(`import re` → `import   re`), rodei `ruff format --check _framework/scripts`
→ **exit 1** (`unformatted: File would be reformatted`, aponta exatamente a
linha alterada). Restaurei o arquivo do backup, rodei de novo → **exit 0**
(`10 files already formatted`). `git diff --stat` confirma zero diff
residual. Discrimina corretamente.

## Verificação do desvio de mypy (implicit_optional + disable_error_code)

Removidas temporariamente `implicit_optional = true` e
`disable_error_code = [...]` de `pyproject.toml` (restauradas depois) e
rodado `mypy _framework/scripts` sem o desvio: **10 erros reais** em 7
arquivos — 3 de PEP 484 implicit-optional (`framework_lib.py:26,43,137`),
5 de `var-annotated` (`validate_state.py:88`, `validate_doc.py:149`,
`registry_tools.py:141`, `check_commit.py:47`, `render_prompts.py:220` — a
SDD cita "4", o real é 5; descompasso na prosa, não no código), 1
`union-attr` (`check_renderings.py:171`) e 1 `index`
(`render_prompts.py:724`). Todos em anotações parciais pré-existentes, não
em código do PR (confirmado: nenhum desses arquivos teve linha de tipo
alterada no diff — só reflow, ver seção "Conformidade" abaixo). Com o
desvio restaurado, `mypy` volta a `Success: no issues found`. Desvio é
funcionalmente justificado — evita 10 erros reais sem tocar nenhum `.py` —
mesmo com a contagem "4" (var-annotated) desatualizada frente ao "5" real.

## Conformidade com a spec (as duas direções)

- RF01–RF05: cada um tem código correspondente identificável
  (`pyproject.toml` seções `[tool.pytest.ini_options]`/`[tool.mypy]`; steps
  novos em `framework-check.yml`; `.pre-commit-config.yaml`; scripts
  reformatados).
- Arquivos do diff `b90b023..13e206d`: `.github/workflows/framework-check.yml`,
  `.pre-commit-config.yaml`, `pyproject.toml`, `docs/sdd/SDD-DTF-0013.md`,
  `docs/sdd/registry.yaml`, 9 scripts em `_framework/scripts/*.py` + 1
  arquivo de teste (`test_render_prompts_mechanization.py`, 1 linha —
  import reordenado), e as 9 cópias mecanizadas espelho em
  `_framework/skills/doc-traceability-framework/scripts/*.py`. Todos
  cobertos pela SDD (especificação técnica consolidada, ou as cópias
  mecanizadas, que são saída determinística de `render_prompts.py`, não
  edição manual). Nenhum arquivo fora da lista.
- Reformatação dos 9 scripts de produção + arquivo de teste: comparadas as
  linhas adicionadas/removidas de cada arquivo (multiset insensível a
  espaço) — em todos os 9 scripts, adds e dels são o mesmo conteúdo
  normalizado (só reflow de linha/quebra de string, característico de
  `ruff format`), nenhum token de código novo ou removido. Confirma "sem
  mudança de comportamento" por leitura direta do diff, além da suíte de
  teste e do `render_prompts.py --check`.
- Nenhuma abstração, dependência, feature flag ou refactor sem requisito
  correspondente.
- `.githooks/pre-commit` intacto — RF04 é aditivo, como exigido.

## Descompassos encontrados

- Prosa da SDD ("4 variáveis locais sem anotação inferível") diverge do
  real (5 ocorrências de `var-annotated` ao rodar mypy sem o desvio) —
  contagem errada na narrativa do desvio, sem efeito no resultado (o
  `disable_error_code` cobre a categoria toda, não uma contagem fixa, e
  `mypy` passa limpo com o desvio ativo). Não bloqueia `implemented`, mas
  vale corrigir o número na SDD por precisão histórica.

## Lições

- Confiar na tabela "Evidência de verificação" preenchida pelo
  implementador não teria pego o erro de contagem "4 vs 5" no desvio de
  mypy — só rodar `mypy` sem o desvio (reproduzindo os findings do zero)
  revelou. Generalizar: todo desvio que alega "N findings motivaram esta
  config" merece reproduzir os N findings, não só confiar no número
  citado.
- `validation.md` como arquivo único ao lado da SDD (sem sufixo por ID)
  cria risco de colisão quando sessões de verificação rodam em paralelo
  sobre o mesmo checkout (aconteceu durante esta verificação: uma sessão
  concorrente verificando SDD-DTF-0012 trocou o branch do checkout
  compartilhado e sobrescreveu este arquivo antes do commit). Vale
  considerar nomear `validation-SDD-{ID}.md` no procedimento, ou pelo
  menos alertar o verificador para conferir `git status` nesse arquivo
  antes de sobrescrever.
