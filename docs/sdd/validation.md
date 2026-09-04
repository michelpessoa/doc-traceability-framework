# Verificação — SDD-DTF-0011

- **Veredito:** PASS
- **Diff verificado:** `461b127..b7bfde3` (`feat(framework): SDD-DTF-0011 — ruff como linter do kit público`, mergeado em `main` como PR #36)
- **Verificador independente:** sim (sessão separada da que implementou; não li o histórico da sessão implementadora, só a SDD e o diff)

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 — RF01 config declarada | `ruff check --show-settings _framework/scripts \| grep -i "line.length\|target.version"` | `linter.line_length = 120`, `linter.unresolved_target_version = 3.12`, `formatter.unresolved_target_version = 3.12` | — | Sim |
| 2 — RF02 repositório limpo | `ruff check _framework/scripts` | `All checks passed!`, exit 0 | — | Sim |
| 3 — RF03 sensor de discriminação no CI | Prepended `import os` não usado em `_framework/scripts/generate_registry_md.py`, rodei `ruff check _framework/scripts` (6 erros incl. F401, exit 1), restaurei o arquivo original via `mv`, rodei de novo | exit 1 (achado citado: `F401 'os' imported but unused`) → exit 0 (`All checks passed!`); `git status --short` confirma arquivo restaurado sem diff | negativo→positivo | Sim |
| 4 — RF04 nenhuma linha acima do limite exceto as 3 com noqa | `ruff check _framework/scripts` (respeita os 3 `noqa: E501` documentados) | `All checks passed!`, exit 0 | — | Sim |
| 5 — Regressão pós-reflow | `python3 _framework/scripts/render_prompts.py --check` e `python3 -m pytest _framework/scripts/tests/ -v` | ambos exit 0; pytest `7 passed in 0.13s` | — | Sim |
| 6 — Regressão geral | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.`, exit 0 | — | Sim |

## Verificação adicional: byte-identidade do conteúdo gerado (desvio da spec)

A SDD alega que os 3 `# noqa: E501` em `render_prompts.py` (`build_universal`,
`build_cursor_mdc`, `build_copilot_instructions`) só silenciam o comprimento
de linha do código-fonte Python, sem alterar o conteúdo gerado. Verifiquei
isso de forma independente, fora da tabela de evidência da SDD:

- Criei duas worktrees git descartáveis a partir de `461b127` (antes do
  commit) e `b7bfde3` (depois), rodei `python3 _framework/scripts/render_prompts.py`
  em cada uma, e comparei os artefatos gerados
  (`_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`,
  `_framework/prompts/copilot/copilot-instructions.md`) com `sha256sum`.
- Resultado: os três arquivos têm hash **idêntico** antes e depois do commit
  (`universal.md` = `29942e5e...7958a`, `doc-framework.mdc` = `a4ae765f...bf9c9`,
  `copilot-instructions.md` = `b72b39ce...85e2c7` em ambos os lados).
- Também inspecionei o diff linha a linha de `render_prompts.py`: as 3
  strings literais gigantes (`prefix = '...'`) permanecem byte-idênticas
  entre antes e depois — o único acréscimo é o comentário
  `# noqa: E501 — ...` depois do fechamento da aspas, na mesma linha
  física. Nenhum caractere do conteúdo da string foi tocado.
- Diff também confirma que os 2 imports reordenados (`generate_registry_md.py`,
  `test_render_prompts_mechanization.py`) são só reordenação de `import`
  (regra `I001`), sem mudança de lógica.

Conclusão: o desvio documentado na SDD está corretamente justificado — os
`noqa` não escondem finding real de qualidade, e o comportamento de
`render_prompts.py` (conteúdo gerado) não mudou.

## Descompassos encontrados

Nenhum.

- Todo item de "Requisitos consolidados" (RF01–RF04) tem código
  correspondente identificável: `ruff.toml` (RF01), lint limpo (RF02),
  step novo no workflow entre "Instalar dependências" e "Testes de
  mechanization" (RF03), reflow das 6 linhas listadas (RF04, re-varridas
  nesta verificação via inspeção do diff — números batem com o que a SDD
  registrou).
- Todo arquivo do diff aparece coberto pela SDD, seja na "Especificação
  técnica consolidada" (`ruff.toml`, `.github/workflows/framework-check.yml`)
  ou no "Desvio da especificação técnica" (`generate_registry_md.py`,
  `test_render_prompts_mechanization.py` — reorder de import;
  `registry_tools.py`, `render_prompts.py`, `validate_doc.py` — reflow
  RF04 + os 3 `noqa`). As cópias mecanizadas em
  `_framework/skills/doc-traceability-framework/scripts/*.py` são saída
  determinística de `render_prompts.py` (confirmado por
  `render_prompts.py --check` = exit 0), não edição manual fora de
  escopo.
- Nenhuma abstração, dependência, feature flag ou refactor sem requisito
  correspondente — o único código novo é `ruff.toml` e o step de CI, o
  resto é formatação.

## Lições

- Um desvio de spec bem documentado ("achei N findings a mais, corrigi
  com --fix ou noqa pontual, aqui está o porquê") é mais rápido de
  verificar do que um "reflow" silencioso teria sido — a seção "Desvio
  da especificação técnica" deu ao verificador exatamente os 5 pontos a
  checar, sem precisar re-derivar o que mudou a partir do diff bruto.
- Para desvio que alega "comportamento não muda" em gerador de
  conteúdo (aqui, `render_prompts.py`), autorrevisão por leitura de
  string não basta como evidência forte — comparar hash do artefato
  gerado antes/depois do commit (via worktree descartável) é barato e
  fecha a dúvida de forma objetiva. Vale generalizar esse padrão para
  qualquer SDD futura que reflowe/refatore um gerador de conteúdo.
