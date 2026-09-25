---
id: SDD-DTF-0047
type: SDD
title: "Leitor de tabelas markdown trata pipe escapado como conteúdo de célula, com um único helper compartilhado"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0024, SDD-DTF-0042, SDD-DTF-0044, SDD-DTF-0045]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0024). Leia esta SDD inteira; ela nomeia os oito pontos de código que hoje repetem a mesma linha de split e o helper único que os substitui. Escrever os testes primeiro e ver falhar no parser antigo, depois implementar. Copias em _framework/skills/doc-traceability-framework/scripts/ são geradas por render_prompts.py, nunca editadas à mão. O central espelha por PR próprio (task 8, prefixo central:). Implementar em sessão separada, worktree próprio no kit, branch sdd/SDD-DTF-0047-*; verificação por sdd-verifier em outra sessão."
supersedes: null
superseded_by: null
tags: [tooling, parser, tabela, pipe-escapado, validate_state, frente-tooling]
---

# Leitor de tabelas markdown trata pipe escapado como conteúdo de célula, com um único helper compartilhado

> Este documento é COMPILADO a partir de `source_docs` — aqui não há
> upstream (sizing small), então os requisitos são escritos nesta SDD.
> Vive no repositório do kit `doc-traceability-framework` porque é o
> artefato lido pela IA no momento de implementar.

## Resumo executivo

Toda leitura de tabela markdown dos scripts do framework quebra a linha
com `line.strip("|").split("|")`, sem reconhecer o pipe escapado
(barra invertida seguida de pipe), que em GFM é conteúdo da célula e não
separador. Uma célula de comando de verificação como um `grep` com
alternância, escrita com o pipe escapado, vira duas células; todas as
colunas seguintes deslocam uma posição, e o `validate_state.py` lê a
coluna errada como "Perfil esperado" ou "Perfil usado" e reprova a SDD.
Isso reprovou `validate_state.py` nas SDDs 0042, 0044 e 0045, e os
implementadores contornaram reescrevendo os comandos sem pipe (o mesmo
contorno editorial que a SDD-DTF-0024 já tinha documentado para outro
bug do mesmo parser). A causa está duplicada em oito pontos de cinco
scripts; esta SDD cria um helper único em `framework_lib.py` e faz os
oito pontos usá-lo, para que a correção valha uma vez só, sem mudar o
comportamento de tabelas sem pipe escapado.

`sizing: small`: tooling, 1 helper novo, 5 scripts com troca de uma linha
cada, testes; nenhum critério de `decision_gates.rfc_to_adr` se aplica e o
comportamento externo do produto não muda.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção de mecanização, nenhum critério do gate `rfc_to_adr`
se aplica. Decisões de desenho, tomadas aqui:

- **Pipe escapado vira `|` na célula devolvida (desescapado), não fica
  literal `\|`.** Motivo: é o que o leitor humano e o renderizador GFM
  veem (a célula de `grep -E 'a\|b'` renderiza `a|b`, inclusive dentro de
  crases), então a célula devolvida é o conteúdo real. Os consumidores
  comparam e copiam esse conteúdo (comando rodado, perfil, caminho de
  arquivo); manter a barra faria o comando copiado da SDD não ser o
  comando que o leitor vê. Não há consumidor atual que precise do texto
  bruto da fonte.
- **Helper único em `framework_lib.py`**, que todos os scripts já
  importam ou podem importar pelo mesmo idioma (`sys.path.insert` do
  diretório do script). Alternativa descartada: corrigir a linha em cada
  script, o que reproduz a duplicação que causou o defeito.
- **Implementação por sentinela, para não alterar o que já funciona:** o
  helper troca o par barra-pipe por um caractere sentinela `"\x00"`, roda
  exatamente a lógica antiga (`strip("|")`, `split("|")`, `strip()` por
  célula) e devolve o sentinela como `|`. Assim, para linha sem pipe
  escapado o resultado é idêntico ao de hoje, inclusive o descarte de
  pipes repetidos nas pontas.
- Limitação aceita e documentada: `\\|` (barra escapada seguida de
  delimitador) é lido como pipe escapado, igual ao GFM; não há caso real.

## Requisitos consolidados

| RF-ID | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | `framework_lib.py` expõe `split_table_row(line: str) -> list[str]`, único ponto de divisão de linha de tabela markdown. | Quando `split_table_row` receber uma linha de tabela, o sistema deve devolver a lista de células com `strip()` aplicado a cada uma. |
| RF02 | Par barra-pipe é conteúdo de célula, devolvido desescapado como `|`. | Quando a linha contiver barra invertida seguida de pipe, o sistema deve manter o par dentro da mesma célula e devolvê-lo como um pipe simples, sem alterar a contagem de células. |
| RF03 | Linha sem pipe escapado tem resultado idêntico ao do split antigo. | Quando a linha não contiver barra invertida seguida de pipe, o sistema deve devolver exatamente o que o split antigo (strip do pipe nas pontas, divisão por pipe, strip por célula) devolvia. |
| RF04 | `validate_state.table_with_header` (e por herança `table_rows`) usa o helper; célula com pipe escapado não desloca colunas. | Quando uma tabela de critérios ou de evidência tiver pipe escapado em qualquer célula, o sistema deve ler "Perfil esperado", "Perfil usado" e "Assertion (file:line)" pelas mesmas posições de uma linha sem pipe. |
| RF05 | Os três leitores de linha de `validate_doc.py` usam o helper. | Quando uma tabela de RF, de Arquivos ou de categoria de sweep de SPEC ou SDD tiver pipe escapado numa célula, o sistema deve devolver as células nas posições corretas e não gerar problema espúrio. |
| RF06 | `parallel_plan.py`, `render_indexes.py` (leitor da coluna "Arquivos tocados") e `ci_gate_verify_sdd.py` (`table_with_header`) usam o helper. | Quando a tabela de tasks tiver pipe escapado numa célula, o sistema deve ler as colunas "Arquivos tocados" e "Depende de" nas posições corretas; quando a tabela de evidência lida pelo gate de CI tiver pipe escapado, deve contar as mesmas linhas de dados. |
| RF07 | Nenhum script sob `_framework/scripts/`, exceto `framework_lib.py`, contém a divisão de linha de tabela por pipe. | O sistema deve falhar o teste de varredura se algum script (exceto `framework_lib.py`) contiver uma chamada `split` cujo único argumento seja um pipe entre aspas. |
| RF08 | Testes escritos antes da implementação, cada um falhando contra o parser antigo. | Se o helper for substituído pela lógica antiga de split, então os testes de RF02, RF04, RF05 e RF06 devem falhar. |
| RF09 | As cópias em `_framework/skills/doc-traceability-framework/scripts/` são regeneradas, não editadas à mão. | Quando `render_prompts.py --check` rodar, o sistema deve sair com código 0, com as seis cópias (`framework_lib.py`, `validate_state.py`, `validate_doc.py`, `parallel_plan.py`, `render_indexes.py`, `ci_gate_verify_sdd.py`) sincronizadas. |
| RF10 | O central recebe o mesmo diff em `_framework/` (regra do `_framework/AGENTS.md`). | Quando o PR do central for aberto, o sistema deve deixar `diff -r` entre os `_framework/` de kit e central sem diferença nos arquivos desta SDD. |

Casos de borda:

| Caso | RF | Comportamento esperado |
|---|---|---|
| Célula com dois pipes escapados no mesmo texto | RF02 | Uma única célula, com os dois como pipes simples |
| Pipe escapado dentro de crases (comando grep com alternância) | RF02, RF04 | Mesma célula, conteúdo com pipe simples, é o caso real das SDDs 0042, 0044 e 0045 |
| Pipe escapado no fim da última célula, antes do delimitador final | RF02, RF03 | O par escapado fica na célula; o delimitador final é removido como antes |
| Linha separadora (`|---|---|`) | RF03 | Continua reconhecida como separador por `table_with_header` |
| Linha de tabela dentro de bloco cercado | RF04 | Continua ignorada (comportamento de SDD-DTF-0024 inalterado) |
| Linha sem pipe algum além dos delimitadores | RF03 | Resultado idêntico ao antigo |
| Barra invertida sem pipe depois (`C:\dir`) | RF03 | Preservada literalmente na célula |
| Caractere NUL na linha | RF01 | Fora de escopo; NUL não ocorre em markdown de documento do framework |

Requisitos não funcionais: sem dependência nova (o helper usa só a stdlib);
sem mudança de assinatura pública de `table_rows`, `table_with_header`,
`parse_tasks` ou de qualquer função existente; mypy e ruff limpos.

Fora de escopo: `_table_rows` de `render_indexes.py` (devolve linhas
cruas dos índices GERADOS, que o próprio gerador escreve sem pipe
escapado; os testes de `test_render_indexes.py` que dividem essas linhas
não mudam); reescrever comandos das SDDs 0042, 0044 e 0045 (já
implementadas; ficam como estão); suporte a célula multilinha; alterar
`workflow-rules.yaml`, templates, skills ou procedures; bump de
`framework.version`.

## Especificação técnica consolidada

**`_framework/scripts/framework_lib.py`** — função nova, sem tocar as
existentes:

```python
_ESCAPED_PIPE = "\\|"
_SENTINEL = "\x00"

def split_table_row(line: str) -> list[str]:
    """Células de uma linha de tabela markdown, com strip() em cada uma.

    O par barra-pipe é conteúdo de célula (GFM) e volta desescapado como
    um pipe simples. Sem par escapado, equivale a
    [c.strip() for c in line.strip("|").split("|")].
    """
    masked = line.replace(_ESCAPED_PIPE, _SENTINEL)
    return [c.strip().replace(_SENTINEL, "|") for c in masked.strip("|").split("|")]
```

Nota: o `strip("|")` acontece sobre a linha mascarada, então um par
escapado nunca é confundido com o delimitador final. Quem chama continua
responsável por `line.strip()` e por checar `line.startswith("|")` antes.

**Pontos de uso a trocar** (uma linha cada; em todos, o import é
`from framework_lib import split_table_row`, com o mesmo idioma de
`sys.path` que o arquivo já usa):

| Script | Onde | Linha atual (antes da edição) |
|---|---|---|
| `_framework/scripts/validate_state.py` | `table_with_header` | 88 |
| `_framework/scripts/validate_doc.py` | três leitores de tabela (RF, Arquivos, categoria) | 307, 341, 398 |
| `_framework/scripts/parallel_plan.py` | `parse_tasks` | 82 |
| `_framework/scripts/render_indexes.py` | leitor da coluna "Arquivos tocados" | 449 |
| `_framework/scripts/ci_gate_verify_sdd.py` | `table_with_header` | 196 |

`ci_gate_verify_sdd.py` já importa `FRONTMATTER_RE` de `framework_lib`;
acrescentar `split_table_row` ao mesmo import. `validate_state.py`,
`validate_doc.py` e `parallel_plan.py` já importam de `framework_lib`.

**Testes** (test-first):

- `_framework/scripts/tests/test_table_cells.py` (novo):
  `test_split_sem_pipe_escapado_igual_ao_antigo` (parametrizado, RF03),
  `test_pipe_escapado_fica_na_celula_e_desescapado` (RF02),
  `test_dois_pipes_escapados_uma_celula` (RF02),
  `test_pipe_escapado_dentro_de_crases` (RF02),
  `test_pipe_escapado_antes_do_delimitador_final` (RF02, RF03),
  `test_barra_sem_pipe_preservada` (RF03),
  `test_nenhum_script_divide_linha_por_pipe_direto` (RF07: varre
  `_framework/scripts/*.py`, exceto `framework_lib.py`, com a regex
  `split\(\s*["']\|["']\s*\)`; falha listando arquivo e linha).
- `_framework/scripts/tests/test_validate_state.py`:
  `test_pipe_escapado_nao_desloca_perfil_esperado` (`table_with_header`
  devolve o "Perfil esperado" na coluna certa) e
  `test_check_sdd_pipe_escapado_em_comando_nao_reprova` (fim a fim via
  `check_sdd`, SDD `implemented` com comando escapado nas tabelas de
  critérios e de evidência; sem problema, RF04).
- `_framework/tests/test_validate_doc.py`:
  `test_pipe_escapado_em_tabela_de_rf` e um caso para a coluna Arquivos
  (RF05).
- `_framework/tests/test_parallel_plan.py`:
  `test_pipe_escapado_na_celula_de_task_nao_desloca_arquivos` (RF06).
- `_framework/tests/test_render_indexes.py`:
  `test_arquivos_tocados_com_pipe_escapado` (RF06).
- `_framework/tests/test_ci_gate_verify_sdd.py`:
  `test_table_with_header_pipe_escapado` (RF06).

Cada teste de RF04 a RF06 monta a tabela com o par barra-pipe em uma
célula anterior à coluna lida, de modo que o parser antigo devolva a
coluna deslocada (sensor natural de discriminação).

**Cópias e espelho.** Depois de editar `_framework/scripts/`, rodar
`python3 _framework/scripts/render_prompts.py` (sem `--check`) e
commitar as cópias geradas em `_framework/skills/doc-traceability-framework/scripts/`
no mesmo PR; nunca editá-las à mão. O repositório central recebe o mesmo
diff de `_framework/` (scripts, testes e cópias do bundle) em PR próprio;
o central não tem `docs/sdd`, então lá vale `render_prompts.py --check` e
a suíte do `_framework/`.

Tratamento de erro por contrato: o helper é total (não levanta exceção
para nenhuma string); linha vazia devolve `[""]`, igual ao split antigo.

Rollout e rollback: direto, PR no kit e PR no central, sem feature flag.
Rollback: reverter o commit; nenhum dado é migrado. Observabilidade:
nenhuma nova.

## Decomposição em tasks

Arquivos do central usam o prefixo `central:` para não colidir por nome
com os do kit em `parallel_plan.py`. A task 1 vem primeiro (helper e seus
testes escritos antes do código: os testes falham sem o helper, e os das
tasks 2 a 6 falham contra o parser antigo). As tasks 2 a 6 tocam arquivos
disjuntos e rodam em paralelo depois da 1. A task 7 regenera as cópias
depois de todas as edições. A task 8 espelha no central.

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes de `split_table_row` e da varredura de RF07 (falham), depois o helper em `framework_lib.py` (passam, exceto a varredura de RF07 até as tasks 2 a 6) | RF01, RF02, RF03, RF07, RF08 | _framework/scripts/framework_lib.py, _framework/scripts/tests/test_table_cells.py | |
| 2 | `validate_state.py`: `table_with_header` usa o helper; testes de RF04 escritos antes | RF04, RF08 | _framework/scripts/validate_state.py, _framework/scripts/tests/test_validate_state.py | 1 |
| 3 | `validate_doc.py`: três leitores usam o helper; testes antes | RF05, RF08 | _framework/scripts/validate_doc.py, _framework/tests/test_validate_doc.py | 1 |
| 4 | `parallel_plan.py`: `parse_tasks` usa o helper; teste antes | RF06, RF08 | _framework/scripts/parallel_plan.py, _framework/tests/test_parallel_plan.py | 1 |
| 5 | `render_indexes.py`: leitor de "Arquivos tocados" usa o helper; teste antes | RF06, RF08 | _framework/scripts/render_indexes.py, _framework/tests/test_render_indexes.py | 1 |
| 6 | `ci_gate_verify_sdd.py`: `table_with_header` usa o helper; teste antes | RF06, RF08 | _framework/scripts/ci_gate_verify_sdd.py, _framework/tests/test_ci_gate_verify_sdd.py | 1 |
| 7 | Regenerar as cópias do bundle com `render_prompts.py` (sem editar à mão) | RF09 | _framework/skills/doc-traceability-framework/scripts/framework_lib.py, _framework/skills/doc-traceability-framework/scripts/validate_state.py, _framework/skills/doc-traceability-framework/scripts/validate_doc.py, _framework/skills/doc-traceability-framework/scripts/parallel_plan.py, _framework/skills/doc-traceability-framework/scripts/render_indexes.py, _framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py | 2, 3, 4, 5, 6 |
| 8 | Central: espelhar scripts, testes e cópias do bundle da task 1 a 7 | RF10 | central:_framework/scripts/framework_lib.py, central:_framework/scripts/validate_state.py, central:_framework/scripts/validate_doc.py, central:_framework/scripts/parallel_plan.py, central:_framework/scripts/render_indexes.py, central:_framework/scripts/ci_gate_verify_sdd.py, central:_framework/scripts/tests/test_table_cells.py, central:_framework/scripts/tests/test_validate_state.py, central:_framework/tests/test_validate_doc.py, central:_framework/tests/test_parallel_plan.py, central:_framework/tests/test_render_indexes.py, central:_framework/tests/test_ci_gate_verify_sdd.py, central:_framework/skills/doc-traceability-framework/scripts/framework_lib.py | 7 |

Paralelismo esperado de `parallel_plan.py`: grupo A = task 1; grupo B =
tasks 2, 3, 4, 5, 6 (paralelas entre si, todas dependem só da 1); depois
task 7; depois task 8. (A task 8 lista as cópias do bundle que mudam no
central; o `render_prompts.py` do central as regenera, então a lista pode
crescer para as seis cópias, igual ao kit, e isso é registro, não
scope creep.)

## Critérios de aceite / definição de pronto

Rodados na raiz do kit (e, nos critérios 1 a 5 e 7, na raiz do central
depois da task 8). Nenhum é verificado por leitura de código. Nenhuma
célula desta tabela usa pipe, escapado ou não.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01, RF02, RF03, RF07 | `python3 -m pytest _framework/scripts/tests/test_table_cells.py -v` | sai 0; os sete testes listados na especificação aparecem `PASSED` | automatizado |
| 2 | RF04 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | sai 0; `test_pipe_escapado_nao_desloca_perfil_esperado` e `test_check_sdd_pipe_escapado_em_comando_nao_reprova` `PASSED`, e todos os testes anteriores continuam `PASSED` | automatizado |
| 3 | RF05, RF06 | `python3 -m pytest _framework/tests/test_validate_doc.py _framework/tests/test_parallel_plan.py _framework/tests/test_render_indexes.py _framework/tests/test_ci_gate_verify_sdd.py -v` | sai 0; os testes novos de pipe escapado `PASSED` e nenhum teste anterior `FAILED` | automatizado |
| 4 | RF08 (sensor: os testes discriminam) | `git stash push -- _framework/scripts/framework_lib.py _framework/scripts/validate_state.py` seguido de `python3 -m pytest _framework/scripts/tests/test_table_cells.py _framework/scripts/tests/test_validate_state.py -q` e de `git stash pop` | com o código antigo, os testes de pipe escapado `FAILED` (ao menos `test_pipe_escapado_fica_na_celula_e_desescapado` e `test_pipe_escapado_nao_desloca_perfil_esperado`); depois do `pop` voltam a passar | automatizado |
| 5 | RF07 — nenhum split direto restante | `python3 -m pytest _framework/scripts/tests/test_table_cells.py::test_nenhum_script_divide_linha_por_pipe_direto -v` | sai 0, `1 passed` | automatizado |
| 6 | RF09 — bundle regenerado | `python3 _framework/scripts/render_prompts.py --check` | sai 0; as seis cópias listadas como `sincronizado` | automatizado |
| 7 | RF04 a RF06, regressão geral | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | sai 0; `passed` sem `failed` | automatizado |
| 8 | Regressão do framework (self-host, inclui as SDDs 0042, 0044 e 0045 implementadas) | `python3 _framework/scripts/framework_check.py --auto` | sai 0 e `Todas as verificações do framework passaram.` | automatizado |
| 9 | Paridade com o CI | `ruff check _framework/scripts` e `ruff format --check _framework/scripts` e `mypy _framework/scripts` | os três saem 0 (`All checks passed!`, `already formatted`, `Success: no issues found`) | automatizado |
| 10 | RF10 — espelho no central | `diff -r _framework/scripts /home/michel/doc-traceability-central/_framework/scripts -x __pycache__` | sem saída, sai 0 (rodado na raiz do kit, com o central na branch da task 8) | automatizado |

## Instruções específicas para a IA implementadora

- Branch nomeada pelo id que a originou (`sdd/SDD-DTF-0047-pipe-escapado`),
  levada a main por PR; nunca commit de implementação direto em main. Todo
  commit carrega `Refs: SDD-DTF-0047`. Não mergear o PR.
- Implementar em sessão separada da que compilou esta SDD, em worktree
  próprio (`git worktree add` explícito). O central é um segundo
  repositório com PR próprio (task 8).
- Test-first: escrever os testes de cada task, rodar e registrar que
  FALHAM contra o parser antigo, só então trocar a linha de split. O
  mesmo vale para o helper: os testes da task 1 falham com `ImportError`
  antes de ele existir; use um commit de testes e um de implementação, se
  ajudar a provar a ordem.
- O helper é exatamente o da "Especificação técnica consolidada"; não
  generalizar (sem parser de tabela novo, sem regex de célula, sem
  tratamento de `\\|`). Mudar só a linha de split de cada ponto de uso;
  não tocar em nada mais das funções vizinhas.
- Não editar `_framework/skills/doc-traceability-framework/scripts/*` à
  mão: rodar `python3 _framework/scripts/render_prompts.py` e commitar o
  resultado. Não alterar `workflow-rules.yaml`, templates, skills,
  procedures, `registry.yaml` ou `registry.md`/INDEX fora do fluxo do
  framework (o registry recebe só a entrada desta SDD, já feita).
- Sensor de discriminação: além dos testes falharem antes da correção,
  registrar o critério 4 (código antigo restaurado em espaço descartável,
  nunca commit).
- Não reescrever os comandos das SDDs 0042, 0044 e 0045 para usar pipe
  escapado; elas ficam como estão.
- Espelhar no central byte a byte os arquivos da task 8; no central,
  rodar `python3 _framework/scripts/render_prompts.py --check` e a suíte
  do `_framework/` antes do PR.
- Verificação (status `implemented`) por `sdd-verifier` em sessão
  separada; quem implementou não preenche a Evidência.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirmar as duas direções:

- [ ] Todo requisito consolidado (RF01 a RF10) tem código, teste ou arquivo
      correspondente, no kit e no central.
- [ ] Todo arquivo tocado aparece na "Decomposição em tasks" ou nas
      "Instruções específicas"; arquivo não listado é escopo faltando (atualizar
      a SDD) ou scope creep a remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra além do
      helper `split_table_row`.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Para cada critério da tabela acima: comando rodado de fato nesta sessão e
saída real, nunca "deve passar" nem resultado de memória.

**Verificador independente:** {sim | não — mesma sessão que implementou}

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0024 (mesma função, outro defeito do parser); SDD-DTF-0042, SDD-DTF-0044 e SDD-DTF-0045 (SDDs em que o defeito reprovou o `validate_state.py` e os comandos foram reescritos sem pipe) |
