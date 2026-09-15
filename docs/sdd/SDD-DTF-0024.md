---
id: SDD-DTF-0024
type: SDD
title: "table_with_header não conta linha de bloco cercado como linha de tabela"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0018]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Escopo mecânico em uma função de um script (validate_state.py) mais teste novo; a cópia da skill é sincronizada por render_prompts.py. Implementar em branch sdd/SDD-DTF-0024-* a partir de main, PR, commits com Refs: SDD-DTF-0024."
supersedes: null
superseded_by: null
tags: [tooling, gate_scope_verification, validate_state]
---

# table_with_header não conta linha de bloco cercado como linha de tabela

## Resumo executivo

Bug real, achado em verificação independente e registrado em
`docs/sdd/LESSONS.md`, seção "2026-09-14 — Descompassos das verificações
independentes de SDD-DTF-0018 a 0023", item 2 ("`table_rows` conta linha
de bloco de código como linha de tabela"): `table_with_header`
(`_framework/scripts/validate_state.py`) decide se uma linha pertence a
uma tabela markdown só por "a linha, depois de `strip()`, começa com
`|`". Ela não sabe distinguir blocos de código cercados por crase tripla
(` ``` `). Se uma linha de evidência dentro de um bloco cercado por acaso
começa com `|` — por exemplo, a continuação de um comando shell como
`  | grep -c ...` — ela é contada como linha de tabela, inflando
artificialmente a contagem de critérios de aceite e, no pior caso,
disparando o problema "N critério(s) de aceite mas só M linha(s) de
evidência" mesmo com a tabela correta.

Achado concreto: ao verificar `SDD-DTF-0018`, cujo critério 2 usa um
bloco de código fora da tabela (porque usa pipe de shell) contendo
`  | grep -c -e "SDD-EVM-000" -e "SDD-EVM-0012"`, `validate_state.py`
contou 6 "critérios" para 5 linhas de evidência reais. O verificador
contornou o problema editorialmente, movendo o pipe para o fim da linha
anterior — sem tocar no código, porque na época o bug ainda não tinha SDD
própria. Esta SDD fecha essa lacuna.

`sizing: small` — 1 função alterada (`table_with_header`, da qual
`table_rows` já é derivada), 1 arquivo de teste com casos novos, sem
mudança de regra, gate ou fluxo: corrige a mecanização para que ela pare
de contar como tabela o que não é tabela.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção de mecanização, nenhum critério do gate `rfc_to_adr`
se aplica.

## Requisitos consolidados

- **RF1**: Quando `table_with_header` percorrer as linhas de uma seção
  para extrair uma tabela markdown, o sistema deve ignorar toda linha que
  esteja entre um par de linhas cuja versão `strip()`-ada comece com
  ` ``` ` (abertura e fechamento de bloco cercado) — mesmo que a linha
  ignorada, depois de `strip()`, comece com `|`.
- **RF2**: A própria linha de abertura/fechamento do bloco cercado (a que
  começa com ` ``` `) nunca é tratada como linha de tabela, esteja ou não
  dentro de outro bloco (não há aninhamento de blocos cercados em
  Markdown padrão — cada ` ``` ` alterna dentro/fora).
- **RF3**: O comportamento para linhas de tabela reais, fora de blocos
  cercados, não muda — inclusive linhas de tabela que venham antes ou
  depois de um bloco cercado na mesma seção.
- **RF4**: `table_rows` (que apenas descarta o cabeçalho do retorno de
  `table_with_header`) herda o comportamento sem mudança de assinatura.
- **RF5**: Teste automatizado em
  `_framework/scripts/tests/test_validate_state.py` cobrindo: (a)
  `table_with_header`/`table_rows` isolando corretamente uma tabela real
  quando a seção também contém um bloco cercado com uma linha shell que
  começa com `|`; (b) o mesmo cenário rodado fim a fim via `check_sdd`,
  confirmando que não dispara o problema "critério(s) de aceite mas só
  N linha(s) de evidência" por causa da linha do bloco cercado.

Casos de borda:
- Bloco cercado sem nenhuma linha começando com `|` dentro → resultado
  idêntico ao comportamento anterior (nada muda pra esse caso, mas o
  teste do item (a) já cobre bloco com linha problemática).
- Bloco cercado não fechado (crase tripla de abertura sem fechamento até
  o fim da seção) → tudo depois da abertura é tratado como dentro do
  bloco (comportamento conservador: mais linhas ignoradas, nunca menos
  seguras — nunca conta como tabela algo potencialmente não-tabela).
- Tabela real com uma linha que contém ` ``` ` dentro de uma célula (ex.:
  célula com um crase triplo escapado) → fora de escopo; Markdown não
  usa isso dentro de célula de tabela de uma linha, e não há caso real
  observado.

Fora de escopo:
- Mudar `check_evidence`, `check_scope` ou qualquer outra função de
  `validate_state.py` além de `table_with_header`.
- Corrigir o ajuste editorial já feito em `SDD-DTF-0018` (o pipe já foi
  movido lá; esta SDD só corrige o parser para o caso geral).
- Sincronizar a cópia de `_framework/` do repositório central (PR de sync
  separado, depois do merge).
- Bump de `framework.version`.

## Especificação técnica consolidada

**`_framework/scripts/validate_state.py`**

- `table_with_header(section: str) -> tuple[list[str], list[list[str]]]`:
  adiciona um flag `in_fence: bool = False` no laço sobre
  `section.splitlines()`. Para cada linha (já com `strip()`):
  - se `line.startswith("```")`: alterna `in_fence = not in_fence` e
    `continue` (a própria linha da crase nunca vira linha de tabela);
  - se `in_fence` for `True`: `continue` (linha ignorada, não entra em
    `rows`);
  - senão, segue o comportamento existente (`if not line.startswith("|"):
    continue`, etc.).
- `table_rows` não muda — continua delegando para
  `table_with_header(section)[1]`.
- Nenhuma outra função do arquivo é tocada.

**`_framework/scripts/tests/test_validate_state.py`** — dois testes
novos:
- Um chamando `table_rows` (ou `table_with_header`) diretamente com uma
  seção que tem uma tabela válida seguida de um bloco cercado contendo
  uma linha shell começando com `|` (reproduzindo o caso real do
  critério 2 de `SDD-DTF-0018`), confirmando que a contagem de linhas
  reflete só a tabela.
- Um fim a fim via `check_sdd`, com uma SDD `implemented` cuja seção
  "Critérios de aceite" tem 1 linha e "Evidência de verificação" tem 1
  linha de tabela real mais o mesmo bloco cercado problemático,
  confirmando que não aparece o problema "critério(s) de aceite mas só
  N linha(s) de evidência".

**`_framework/skills/doc-traceability-framework/scripts/validate_state.py`**
— gerado por `python3 _framework/scripts/render_prompts.py`
(`sync_copies`), nunca editado à mão.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1–RF5 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | todos os testes `passed`, exit 0 |
| 2 | Skill sincronizada | `python3 _framework/scripts/render_prompts.py --check` | exit 0 |
| 3 | Regressão geral (self-host) | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.` e suíte inteira `passed` |
| 4 | Paridade com o CI | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | exit 0 |

## Instruções específicas para a IA implementadora

- Não alterar `check_evidence`, `check_scope`, `check_sdd` nem qualquer
  outra função além de `table_with_header`.
- `table_rows` continua existindo com a mesma assinatura; não remover
  nem renomear.
- Rodar `python3 _framework/scripts/render_prompts.py` (sem `--check`)
  depois de editar `validate_state.py`, e commitar a cópia gerada da
  skill no mesmo PR.
- Sensor de discriminação: reverter temporariamente a mudança em
  `table_with_header` (espaço descartável, nunca commit), confirmar que
  o teste novo do item (a) falha, restaurar a versão corrigida.
- Branch `sdd/SDD-DTF-0024-*` a partir de `main`, PR — nunca commit
  direto (gate seção 14). Commits em Conventional Commits com
  `Refs: SDD-DTF-0024`.
- `docs/sdd/registry.yaml` pode conflitar no merge do PR com outras SDDs
  (0025, 0026, 0027) sendo criadas em paralelo por outros agentes — é
  esperado, resolvido pelo humano no merge, não é bug desta SDD.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Arquivos tocados: `_framework/scripts/validate_state.py`,
      `_framework/scripts/tests/test_validate_state.py` e a cópia gerada
      em `_framework/skills/doc-traceability-framework/scripts/validate_state.py`
      — qualquer outro arquivo é escopo não registrado ou scope creep.
- [x] Nenhuma abstração, config ou refactor extra sem requisito acima.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou
(esta sessão implementou e não marca `implemented` — só `approved`).

**Verificador independente:** ainda não rodado — pendente, sessão
separada.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | `12 passed in 0.62s`, exit 0 (2 testes novos: `test_bloco_cercado_com_pipe_nao_conta_como_linha_de_tabela` e `test_bloco_cercado_nao_gera_descompasso_criterios_x_evidencia`, mais os 10 já existentes de SDD-DTF-0018) | Reverti temporariamente `table_with_header` para a versão sem o flag `in_fence` (espaço descartável, não commitado): `test_bloco_cercado_com_pipe_nao_conta_como_linha_de_tabela` falhou (`AssertionError`, linha extra `['grep -c -e algo']` contada), os outros 11 continuaram passando; restaurada a versão corrigida, `12 passed` | sim |
| 2 | `python3 _framework/scripts/render_prompts.py --check` | Antes de sincronizar: `❌ .../validate_state.py: divergente`, exit 1. Depois de rodar `render_prompts.py` sem `--check`: `✅ .../validate_state.py: sincronizado`, exit 0 | Estado divergente observado de fato antes da sincronização (não simulado) | sim |
| 3 | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.`; suíte `74 passed in 3.41s`, exit 0 | Regressão geral, sem sensor dedicado; lógica nova coberta pelos sensores do critério 1 | sim |
| 4 | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | `All checks passed!`, `21 files already formatted`, `Success: no issues found in 21 source files`, exit 0 | Checagem estática de paridade com o CI, sem sensor dedicado | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0018 (mesma família de correção de `validate_state.py`; o bug foi achado na verificação independente dessa SDD) |
