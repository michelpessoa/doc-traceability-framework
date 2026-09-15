---
id: SDD-DTF-0028
type: SDD
title: "test_validate_state: tabela real depois de bloco cercado fechado discrimina mutação em in_fence"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0024]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Escopo mecânico: um teste novo em test_validate_state.py, nenhuma mudança em validate_state.py. Implementar em branch sdd/SDD-DTF-0028-* a partir de main, PR, commits com Refs: SDD-DTF-0028."
supersedes: null
superseded_by: null
tags: [tooling, testes, validate_state, gate_scope_verification]
---

# test_validate_state: tabela real depois de bloco cercado fechado discrimina mutação em in_fence

## Resumo executivo

Gap de cobertura de teste, achado em verificação independente e
registrado em `docs/sdd/LESSONS.md`, seção mais recente sobre
`SDD-DTF-0024`: `SDD-DTF-0024` corrigiu `table_with_header`
(`_framework/scripts/validate_state.py`) para ignorar, com um flag
`in_fence`, toda linha dentro de um bloco cercado por crase tripla
(` ``` `) — mesmo que essa linha, depois de `strip()`, comece com `|`.
O código está correto (confirmado por verificação independente, fora
desta sessão) e não é alterado aqui.

O que falta é cobertura: dos 12 testes que `SDD-DTF-0024` deixou em
`test_validate_state.py`, nenhum tem uma tabela markdown real **depois**
de um bloco cercado já fechado na mesma seção. A mutação M2 — fazer
`in_fence` nunca voltar a `False`, ou seja, uma cerca de abertura que
nunca "fecha" de verdade no parser (ex.: trocar `in_fence = not
in_fence` por `in_fence = True` na linha que alterna o flag) — sobrevive
aos 12 testes atuais: com ela, `table_with_header`/`table_rows` passam a
ignorar toda linha depois da abertura do primeiro bloco cercado,
inclusive uma tabela de evidência real mais adiante, devolvendo menos
linhas do que devia. Um teste que só verifica que a linha *dentro* do
bloco cercado não é contada (caso já coberto) não pega esse defeito,
porque nunca chega a exercitar o "fim" do bloco cercado com algo real
depois dele.

`sizing: small` — 1 teste novo em 1 arquivo, sem mudança de código de
produção, regra, gate ou fluxo: fecha a lacuna de cobertura para que a
suíte volte a discriminar essa classe de mutação.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — reforço de cobertura de teste, nenhum critério do gate
`rfc_to_adr` se aplica.

## Requisitos consolidados

- **RF1**: `_framework/scripts/tests/test_validate_state.py` ganha um
  teste novo que chama `table_rows` (ou `table_with_header`) diretamente
  com uma seção contendo, nesta ordem: (a) uma linha de tabela real com
  cabeçalho/separador; (b) um bloco cercado por ` ``` ` com conteúdo
  `|`-like dentro (reaproveitando o caso real de `SDD-DTF-0024`, ex.:
  continuação de comando shell `  | grep -c ...`); (c) o fechamento do
  bloco cercado; (d) pelo menos uma linha de tabela real **depois** do
  fechamento, que deve ser contada como linha de dados.
- **RF2**: o teste novo faz uma asserção exata (`==`, não só "não está
  vazio" nem "contém") sobre o retorno de `table_rows`, incluindo a linha
  posterior ao bloco cercado — para que a ausência dela (o efeito da
  mutação M2) derrube o teste.
- **RF3**: o teste novo discrimina a mutação M2 — fazer `in_fence` nunca
  voltar a `False` no laço de `table_with_header`. Com a mutação
  aplicada, o teste novo falha; sem ela (código atual, já `approved` em
  `SDD-DTF-0024`), passa. Verificado nesta sessão em espaço descartável
  (`git checkout --` para restaurar, nunca stash).
- **RF4**: nenhuma mudança em `_framework/scripts/validate_state.py` —
  o código já está correto; esta SDD é só teste.
- **RF5**: os 12 testes existentes de `test_validate_state.py` continuam
  passando sem alteração.

Casos de borda:
- O teste novo reaproveita o padrão de fixture dos testes de
  `SDD-DTF-0024` (`HEADER_5` e o mesmo bloco cercado com `|`) para ficar
  consistente com o resto do arquivo — não inventa uma segunda
  convenção de fixture.
- Não é necessário um teste fim a fim via `check_sdd` para este gap: o
  gap está isolado em `table_with_header`/`table_rows`, e RF1-RF3 já
  isolam e discriminam a mutação diretamente na função. Um teste fim a
  fim adicional seria redundante com os dois que `SDD-DTF-0024` já tem.

Fora de escopo:
- Alterar `table_with_header`, `table_rows` ou qualquer outra função de
  `validate_state.py`.
- Alterar `check_hooks.py` ou seus testes — reservado a `SDD-DTF-0029`,
  em andamento em paralelo por outro agente.
- Sincronizar a cópia de `_framework/skills/doc-traceability-framework/`
  — a cópia sincronizada cobre `validate_state.py` (arquivo de origem),
  não `test_validate_state.py` (não há cópia de testes na skill); nenhuma
  mudança em `validate_state.py` significa nada a sincronizar aqui,
  confirmado por `render_prompts.py --check` já em dia antes e depois
  desta mudança.
- Bump de `framework.version`.

## Especificação técnica consolidada

**`_framework/scripts/tests/test_validate_state.py`** — um teste novo,
próximo dos dois testes de `SDD-DTF-0024` (`test_bloco_cercado_com_pipe_*`):

```python
def test_tabela_real_depois_de_bloco_cercado_fechado_e_contada():
    """SDD-DTF-0028: linha de tabela real que vem DEPOIS de um bloco
    cercado já fechado precisa ser contada. Discrimina a mutação M2
    (fazer `in_fence` nunca voltar a `False`)."""
    section = (
        HEADER_5
        + "| 1 | `pytest` | 3 passed | teste reintroduzido | sim |\n"
        + "\nBloco fora da tabela porque usa pipe de shell:\n\n"
        + "```bash\n"
        + "python3 script.py --report-only |\n"
        + "  | grep -c -e algo\n"
        + "```\n"
        + "\n"
        + "| 2 | `pytest -k outro` | 5 passed | segunda evidência | sim |\n"
    )
    assert table_rows(section) == [
        ["1", "`pytest`", "3 passed", "teste reintroduzido", "sim"],
        ["2", "`pytest -k outro`", "5 passed", "segunda evidência", "sim"],
    ]
```

- Reaproveita `table_rows`, já importado no topo do arquivo, e `HEADER_5`,
  já definido no arquivo — nenhum import ou fixture nova.
- Nenhuma outra função ou arquivo é tocado.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1–RF2, RF5 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | todos os testes `passed`, exit 0 (13 testes: 12 já existentes + 1 novo) |
| 2 | RF3 — sensor de discriminação | reverter `in_fence = not in_fence` para `in_fence = True` em `validate_state.py` (espaço descartável), rodar o comando do critério 1, restaurar com `git checkout --` | só o teste novo falha; os outros 12 continuam `passed` |
| 3 | RF4 — sem mudança de produção | `git diff --stat main -- _framework/scripts/validate_state.py` | saída vazia (nenhuma linha alterada) |
| 4 | Regressão geral (self-host) | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.` e suíte inteira `passed` |
| 5 | Paridade com o CI | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | exit 0 |

## Instruções específicas para a IA implementadora

- Não alterar `table_with_header`, `table_rows` nem qualquer outra função
  de `validate_state.py` — o código já está correto (verificação
  independente fora desta SDD confirmou).
- Não tocar `check_hooks.py` nem seus testes — reservado a
  `SDD-DTF-0029`, em andamento em paralelo por outro agente.
- Sensor de discriminação: reverter temporariamente `in_fence = not
  in_fence` para `in_fence = True` em `validate_state.py` (espaço
  descartável, nunca commit), confirmar que só o teste novo falha,
  restaurar com `git checkout -- _framework/scripts/validate_state.py`
  (nunca `git stash`, que é compartilhado entre sessões/worktrees).
- Branch `sdd/SDD-DTF-0028-*` a partir de `main`, PR — nunca commit
  direto (gate seção 14). Commits em Conventional Commits com
  `Refs: SDD-DTF-0028`.
- `docs/sdd/registry.yaml` pode conflitar no merge do PR com
  `SDD-DTF-0029`, sendo criada em paralelo por outro agente — é
  esperado, resolvido pelo humano no merge, não é bug desta SDD.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Arquivos tocados: `_framework/scripts/tests/test_validate_state.py`
      e este documento (`docs/sdd/SDD-DTF-0028.md`) mais a entrada
      correspondente em `docs/sdd/registry.yaml` — qualquer outro arquivo
      é escopo não registrado ou scope creep.
- [x] Nenhuma abstração, config ou refactor extra sem requisito acima.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida nesta mesma sessão porque o sizing é `small` e a verificação
mecânica (sensor de mutação) já foi rodada como parte da implementação;
a verificação independente completa (skill `verify-sdd`, quem
implementou não verifica) fica para outra sessão antes de mover para
`implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | `13 passed in 0.64s`, exit 0 (13º teste: `test_tabela_real_depois_de_bloco_cercado_fechado_e_contada`) | n/a (checagem estática) | sim |
| 2 | Editado `in_fence = not in_fence` → `in_fence = True` em `table_with_header` (espaço descartável, não commitado); rodado `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | `1 failed, 12 passed` — falhou só `test_tabela_real_depois_de_bloco_cercado_fechado_e_contada` com `AssertionError` (linha `['2', '\`pytest -k outro\`', '5 passed', 'segunda evidência', 'sim']` ausente do retorno); restaurado com `git checkout -- _framework/scripts/validate_state.py`, `13 passed` de novo | Mutação M2 aplicada de fato e revertida de fato, não simulada | sim |
| 3 | `git diff --stat main -- _framework/scripts/validate_state.py` | saída vazia, exit 0 | Confirma nenhuma mudança de produção nesta SDD | sim |
| 4 | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.`; suíte `80 passed in 3.13s`, exit 0 | Regressão geral; lógica nova coberta pelo sensor do critério 2 | sim |
| 5 | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | `All checks passed!`, arquivos já formatados, `Success: no issues found`, exit 0 | Checagem estática de paridade com o CI, sem sensor dedicado | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0024 (fecha o gap de cobertura de teste da mutação M2, achado em verificação independente da mesma) |
