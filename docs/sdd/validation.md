# Verificação — SDD-DTF-0015

- **Veredito:** PASS
- **Diff verificado:** `main..sdd/SDD-DTF-0015-ruff-config-pyproject` (commit `6c6f6be` "fix(tooling): consolida config do ruff em pyproject.toml", PR #44, ainda não mergeada em `main`).
- **Verificador independente:** sim — sessão separada da implementação, sem contexto herdado (leu só a SDD e o diff). A tabela de evidência preenchida pelo implementador dentro da SDD **não** foi usada como fonte de verdade — todos os comandos abaixo foram rodados de novo, nesta sessão.

| # | Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | `ruff.toml` não existe mais | `test -f ruff.toml; echo $?` | `1` (ausente) | trivial — existência de arquivo, sem lógica a discriminar | Sim |
| 2 | `pyproject.toml` tem `[tool.ruff]` | `grep -n "\[tool.ruff\]" pyproject.toml` | `1:[tool.ruff]` — 1 ocorrência | trivial — grep literal, sem lógica a discriminar | Sim |
| 3 | `ruff check` continua limpo, mesma config de antes | `ruff check --show-settings _framework/scripts \| grep -E "line_length\|target_version"` e `ruff check _framework/scripts` | `linter.line_length = 120`, `target_version = 3.12` (idêntico ao `ruff.toml` do commit-base `58d0e2a`, confirmado via `git show 58d0e2a:ruff.toml` + `ruff check --show-settings --config <cópia>`); `All checks passed!`, exit 0 | copiei `pyproject.toml` pra dir descartável, mudei `line-length` de 120 pra 79 e confirmei que `--show-settings` reporta `linter.line_length = 79` — o comando reage à config real, não é saída fixa/cacheada | Sim |
| 4 | `ruff format` continua sem reformatar nada | `ruff format --check _framework/scripts` | `10 files already formatted`, exit 0 | copiei `_framework/scripts` + `pyproject.toml` pra dir descartável, apendei `x =    1` (mal formatado) num script → `ruff format --check` relatou `1 file would be reformatted` com diff da linha, exit 1; desfeito → volta a `10 files already formatted`, exit 0. Discrimina de verdade | Sim |
| 5 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto`; `python3 -m pytest -q` | `✅ Todas as verificações do framework passaram.` (exit 0); `7 passed in 0.12s` (exit 0) | sem sensor dedicado nesta rodada — nenhuma lógica nova introduzida por esta SDD que os sensores dos critérios 3/4 já não cubram; gate geral já tem cobertura de SDDs anteriores | Sim |

## Conformidade com a spec (as duas direções)

- Os 3 requisitos consolidados (config sai de `ruff.toml` e entra em
  `pyproject.toml` sob `[tool.ruff]`/`[tool.ruff.lint]`/`[tool.ruff.format]`;
  `ruff.toml` removido; nenhum valor muda) têm código correspondente
  identificável, um a um — confirmado por diff literal linha a linha entre
  o `ruff.toml` do commit-base (`git show 58d0e2a:ruff.toml`) e a seção
  nova em `pyproject.toml`: mesmos valores (`target-version = "py312"`,
  `line-length = 120`, `exclude = ["examples/**"]`,
  `select = ["E","F","I","W"]`, `quote-style = "double"`,
  `indent-style = "space"`), só a sintaxe aninhada muda (exigência do
  `ruff` para config em `pyproject.toml`, documentada na própria SDD).
- Arquivos do diff `main..sdd/SDD-DTF-0015-ruff-config-pyproject`:
  `pyproject.toml` (editado) e `ruff.toml` (removido) — os 2 declarados
  na "Especificação técnica consolidada" — mais `docs/sdd/SDD-DTF-0015.md`
  e `docs/sdd/registry.yaml`, que são bookkeeping padrão do próprio fluxo
  de SDD (criação/registro do documento), não scope creep.
- Nenhuma abstração, dependência, feature flag ou refactor sem requisito
  correspondente. `git status --short` limpo ao final — nenhum resíduo
  dos experimentos de sensor (todos rodados em diretórios descartáveis
  fora do repo).

## Descompassos encontrados

Nenhum.

## Lições

- Durante a comparação "antes/depois" do critério 3, cheguei a rodar
  `git checkout 58d0e2a -- .` para inspecionar o `ruff.toml` antigo — isso
  sobrescreveu arquivos do working tree (inclusive recriando `ruff.toml`
  staged) em vez de só ler o conteúdo antigo. Corrigido na hora com
  `git checkout HEAD -- .` + `git reset HEAD -- ruff.toml` + `rm -f
  ruff.toml`, sem deixar resíduo (confirmado por `git status --short`
  limpo). **Red flag reaproveitável:** pra ler um arquivo de um commit
  antigo sem tocar o working tree, usar sempre `git show
  <commit>:<path>` (ou copiar pra um dir descartável) — nunca `git
  checkout <commit> -- <path-ou-.>` num repo com working tree que
  precisa continuar limpo; esse comando muda o índice/working tree de
  verdade, não é uma leitura somente-visualização.
