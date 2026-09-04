---
id: SDD-DTF-0011
type: SDD
title: "Linter (ruff) para os scripts Python do kit público"
status: draft
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-04"
updated: "2026-09-04"
relates_to: [SDD-DTF-0009, SDD-DTF-0010]
source_docs:
  - id: "SPEC-DTF-0007"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0007.md"
consumption_instructions: "Leia SPEC-DTF-0007 inteira antes de tocar em arquivo. RF04 lista linhas exatas a reflowar — re-varra antes de aplicar (número pode ter mudado desde a SPEC)."
supersedes: null
superseded_by: null
tags: [tooling, qualidade, kit-publico]
---

# Linter (ruff) para os scripts Python do kit público

## Resumo executivo

Fecha o último item do harness score isolado no kit: introduz `ruff`
como linter dos scripts Python (`_framework/scripts/*.py`), com config
em `ruff.toml`, checagem no CI, e reflow das linhas hoje acima de 120
colunas.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — `SPEC-DTF-0007` já registrou que nenhum critério do gate
`rfc_to_adr` se aplica (não é arquitetura, não é alto custo, não é
cross-team).

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0007`:

- **RF01** — `ruff.toml` na raiz do kit: `line-length = 120`,
  `target-version = "py312"`, `select = ["E", "F", "I", "W"]`,
  `exclude = ["examples/**"]`.
- **RF02** — `ruff check _framework/scripts` retorna `exit 0`.
- **RF03** — CI roda `ruff check _framework/scripts` como step novo em
  `.github/workflows/framework-check.yml`, antes do step de teste já
  existente (`SDD-DTF-0010`), bloqueando o job se houver finding.
- **RF04** — reflow das linhas hoje acima de 120 colunas (re-varridas
  nesta sessão, mesmas 6 da SPEC): `registry_tools.py:94`,
  `render_prompts.py:94`, `render_prompts.py:103`,
  `render_prompts.py:112`, `render_prompts.py:280`,
  `validate_doc.py:212` — sem mudar comportamento.

Casos de borda consolidados:

- `ruff` ausente no runner CI → step de instalação (`pip install ruff`)
  precede a checagem; falha de instalação já é coberta pelo
  comportamento padrão do runner.
- Novo `.py` futuro sem passar por `ruff` localmente → CI reprova no
  step de lint, sem bypass.
- Arquivo em `examples/**` → fora do escopo do linter (`exclude`).
- `noqa` para silenciar finding → fora de escopo; a implementação
  corrige o código. Se algum finding for falso-positivo genuíno, `noqa`
  pontual é desvio a registrar na "Especificação técnica consolidada"
  desta SDD antes do commit (não decidido antecipadamente aqui).

Fora de escopo (herdado de `SPEC-DTF-0007`): `ruff format`/formatação
automática; type checking; lint de Markdown/YAML; integração com
`pre-commit`/`pre-push` locais.

## Especificação técnica consolidada

**`/ruff.toml`** (raiz do kit, arquivo novo):
```toml
target-version = "py312"
line-length = 120
exclude = ["examples/**"]

[lint]
select = ["E", "F", "I", "W"]
```

**`.github/workflows/framework-check.yml`:** novo step "Lint (ruff)",
entre "Instalar dependências" e "Testes de mechanization" (o step de
teste já existe desde `SDD-DTF-0010`):
```yaml
- name: Lint (ruff)
  run: |
    pip install ruff
    ruff check _framework/scripts
```

**Reflow (RF04):** as 6 linhas listadas, quebradas para caber em 120
colunas — sem alterar nome de variável, lógica ou string literal, só
formatação (parênteses/continuação de linha). Depois do reflow,
`render_prompts.py --check` e `pytest _framework/scripts/tests/`
confirmam ausência de regressão de comportamento (requisito da
"Estratégia de teste" da SPEC).

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — config declarada corretamente | `ruff check --show-settings _framework/scripts \| grep -E "line-length|target-version"` | `line-length = 120`, `target_version = Py312` (ou equivalente reportado pelo `ruff`) |
| 2 | RF02 — repositório passa limpo | `ruff check _framework/scripts` | `exit 0`, "All checks passed!" |
| 3 | RF03 — sensor de discriminação no CI | Introduzir import não usado num arquivo descartável em `_framework/scripts/`, rodar `ruff check _framework/scripts` (falha), remover, rodar de novo (passa) | `exit 1` com a violação, `exit 0` depois de remover |
| 4 | RF04 — nenhuma linha acima do limite | `awk '{ if (length($0) > 120) print FILENAME":"NR }' _framework/scripts/*.py` | sem saída |
| 5 | Regressão pós-reflow | `python3 _framework/scripts/render_prompts.py --check` e `python3 -m pytest _framework/scripts/tests/ -v` | `exit 0` nos dois, `7 passed` |
| 6 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` | `exit 0` |

Sensor de discriminação: critério 3 tem caso negativo explícito (import
não usado) — falha antes da correção, passa depois.

## Instruções específicas para a IA implementadora

- Re-varra as linhas de RF04 antes de reflowar — o número pode ter
  mudado desde a SPEC se algo mais tiver sido commitado entre ela e esta
  SDD.
- Reflow é só formatação — nenhuma mudança de nome, lógica ou string.
  Se `ruff` apontar qualquer coisa além das 6 linhas conhecidas
  (import não usado de verdade, etc.), corrija também, mas documente o
  achado extra aqui antes do commit (é escopo não previsto na SPEC, não
  scope creep — mesma diferença que `SDD-DTF-0009` já tratou para o
  desvio do `check_renderings.py`).
- Não adicionar `pyproject.toml`, `mypy`, `ruff format` — fora de escopo
  (ver "Fora de escopo" herdado da SPEC).
- Commits em Conventional Commits, com `Refs: SDD-DTF-0011`.
- Branch dedicada a partir de `main`, PR — **nunca commit direto em
  main** (gate seção 14 — já houve um deslize nesse gate nesta série de
  mudanças, ver `LESSONS.md`).
- **Ordem obrigatória:** esta SDD existe antes de qualquer `.py` ser
  tocado ou `ruff.toml` ser criado (gate seção 13) — diferente do que
  aconteceu em `SDD-DTF-0010`, onde o código foi escrito antes do
  documento.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem código correspondente.
- [ ] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** {sim | não — mesma sessão que implementou}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0007 |
| Branch | `sdd/SDD-DTF-0011-ruff-linter` |
