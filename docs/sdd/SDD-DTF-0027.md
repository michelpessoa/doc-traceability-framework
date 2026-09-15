---
id: SDD-DTF-0027
type: SDD
title: "check_hooks: tokenizar command com shlex pra aceitar variantes de shell de ${CLAUDE_PROJECT_DIR}"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0020]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Escopo mecânico em um script (check_hooks.py) mais o arquivo de teste correspondente; a cópia da skill é sincronizada por render_prompts.py. Implementar em branch sdd/SDD-DTF-0027-* a partir de main, PR, commits com Refs: SDD-DTF-0027."
supersedes: null
superseded_by: null
tags: [tooling, harness, hooks, check_hooks, bugfix]
---

# check_hooks: tokenizar command com shlex pra aceitar variantes de shell de ${CLAUDE_PROJECT_DIR}

## Resumo executivo

Achado em verificação independente registrada em `docs/sdd/LESSONS.md`
("2026-09-14 — Descompassos das verificações independentes de
SDD-DTF-0018 a 0023", item 3): a regra 3 de `check_hooks.check_settings`
(`_framework/scripts/check_hooks.py`, RF06 de `SDD-DTF-0020`) exige que a
string **inteira** do campo `command` comece literalmente por
`${CLAUDE_PROJECT_DIR}/`. Isso reprova comandos igualmente válidos e
seguros em forma de shell, como `"python3 ${CLAUDE_PROJECT_DIR}/x.py"` ou
`'python3 "$CLAUDE_PROJECT_DIR"/x.py'` — esta última é literalmente o
exemplo dado na documentação oficial do Claude Code para hooks. Também
mascara a regra 4 (script referenciado inexistente), porque a regra 3 já
reprova antes de a regra 4 rodar. O kit não é afetado na prática — seu
próprio gerador (`render_prompts.py`) usa a forma `args` em vez de
`command` com shell — mas um projeto que escreva `.claude/settings.json`
à mão com hooks nessa forma teria CI reprovado incorretamente.

`sizing: small` — 1 script alterado, 1 arquivo de teste, sem mudança de
regra, gate ou fluxo: a regra 3 continua garantindo que o comando
referencia `${CLAUDE_PROJECT_DIR}` de alguma forma reconhecível, só passa
a reconhecer mais formas válidas de shell que já eram seguras — não fica
mais permissiva.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção de mecanização de um validador existente, nenhum
critério do gate `rfc_to_adr` se aplica: não introduz padrão
arquitetural novo, é reversível por revert, não é cross-team, não troca
tecnologia (usa `shlex`, da biblioteca padrão do Python já disponível).

## Requisitos consolidados

- **RF1**: Quando `check_settings` avaliar o campo `command` de um hook
  para a regra 3 (referência a `${CLAUDE_PROJECT_DIR}`) e a regra 4
  (script inexistente), o sistema deve tokenizar `command` com
  `shlex.split` antes de procurar a referência, em vez de exigir que a
  string inteira comece pelo prefixo.
- **RF2**: O sistema deve aceitar como referência válida ao diretório do
  projeto tanto o token que começa por `${CLAUDE_PROJECT_DIR}/` (forma
  canônica do kit) quanto o que começa por `$CLAUDE_PROJECT_DIR/` (forma
  sem chaves, resultado de `shlex.split` sobre `"$CLAUDE_PROJECT_DIR"/...`
  depois da remoção de aspas — forma do exemplo oficial de hooks do
  Claude Code).
- **RF3**: Quando nenhum token de `command` (nem item de `args`, já
  tokenizado no JSON) referenciar `${CLAUDE_PROJECT_DIR}` de nenhuma das
  duas formas e algum deles contiver `_framework/`, o sistema deve
  continuar reprovando — o RF06 original ("caminho `_framework/` sem
  `${CLAUDE_PROJECT_DIR}/`") não afrouxa, só passa a reconhecer mais
  formas de referenciar o prefixo.
- **RF4**: Itens de `args` continuam tratados como tokens discretos (já
  chegam separados no JSON, não passam por shell) — não são
  retokenizados com `shlex`.
- **RF5**: Se `shlex.split(command)` levantar `ValueError` (aspas
  malformadas), o sistema deve cair de volta para tratar `command` como
  um único token — mesmo comportamento estrito de antes, nunca mais
  permissivo que a forma anterior.

Casos de borda:

| Caso | RF | Comportamento esperado |
|---|---|---|
| `command` já na forma atual, sem shell (`"${CLAUDE_PROJECT_DIR}/x.py"`) | RF1 | `shlex.split` devolve um único token igual à string — continua aceito (regressão coberta) |
| `command` com múltiplas palavras e prefixo com chaves (`"python3 ${CLAUDE_PROJECT_DIR}/x.py"`) | RF1, RF2 | Aceito |
| `command` com prefixo sem chaves entre aspas (`'python3 "$CLAUDE_PROJECT_DIR"/x.py'`) | RF1, RF2 | Aceito — token pós-tokenização vira `$CLAUDE_PROJECT_DIR/x.py` |
| `command` referenciando `_framework/` sem nenhuma das duas formas | RF3 | Reprovado, mesma mensagem (ajustada para citar as duas formas) |
| `args` com item de shell contendo espaços (não é o formato usado hoje) | RF4 | Tratado como token único, sem tokenizar — fora de escopo mudar esse contrato |
| `command` com aspas malformadas | RF5 | Cai para string inteira como token único (comportamento anterior) |

Fora de escopo:
- Mudar a regra 4 (script inexistente) além de operar sobre os mesmos
  tokens da regra 3 — a lógica de existência do arquivo não muda.
- Mudar `render_prompts.py`, `workflow-rules.yaml` ou qualquer outro
  script (`validate_state.py`, `test_discover.py`, `verify-sdd.md` —
  escopo de outros agentes em paralelo).
- Tokenizar `args` com `shlex` — itens de `args` não passam por shell no
  Claude Code, não têm o mesmo problema.
- Regras 1, 2 e 5 de `check_settings` (`type: "prompt"`, `--report-only`,
  JSON ilegível) — inalteradas.

## Especificação técnica consolidada

### `_framework/scripts/check_hooks.py`

- `import shlex` adicionado.
- `PROJECT_DIR_PREFIX` (constante única) vira `PROJECT_DIR_PREFIXES`
  (tupla): `("${CLAUDE_PROJECT_DIR}/", "$CLAUDE_PROJECT_DIR/")`.
- Nova função `_tokens(hook: dict) -> list[str]`: tokeniza `command`
  (se string) com `shlex.split`, com fallback para `[command]` em
  `ValueError`; estende com os itens de `args` (já tokens, sem
  retokenizar). `_items` (usada só pela regra 2, `--report-only`)
  permanece inalterada — substring funciona igual na string inteira, não
  precisa de tokenização.
- No laço de `check_settings`, as regras 3 e 4 passam a iterar
  `_tokens(hook)` em vez de `_items(hook)`: para cada token, calcula
  `prefix = next((p for p in PROJECT_DIR_PREFIXES if token.startswith(p)), None)`;
  regra 3 dispara se `"_framework/" in token and prefix is None`; regra 4
  dispara se `prefix is not None` e `project_dir / token[len(prefix):]`
  não existe.
- Mensagem da regra 3 ajustada para citar as duas formas aceitas.

### `_framework/scripts/tests/test_check_hooks.py`

Casos novos, além dos 7 existentes (que continuam passando):

| Teste | Entrada | Esperado |
|---|---|---|
| `test_command_shell_com_prefixo_com_chaves` | `command: "python3 ${CLAUDE_PROJECT_DIR}/_framework/scripts/hook.py"`, sem `args` | `[]` |
| `test_command_shell_com_prefixo_sem_chaves_entre_aspas` | `command: 'python3 "$CLAUDE_PROJECT_DIR"/_framework/scripts/hook.py'` | `[]` |
| `test_command_shell_sem_referencia_reprova` | `command: "python3 _framework/scripts/hook.py"` (sem nenhuma referência) | 1 problema citando "sem o prefixo" |

Caso existente (regra 3 na forma atual sem shell, via `args`) já coberto
por `test_valido_sem_problema` e `test_caminho_relativo` — não precisa de
teste novo.

### Cópia sincronizada

`_framework/skills/doc-traceability-framework/scripts/check_hooks.py`
gerada por `python3 _framework/scripts/render_prompts.py` (`sync_copies`),
nunca editada à mão.

### Plano de implementação

1. Editar `_framework/scripts/check_hooks.py` (RF1–RF5).
2. Adicionar os 3 testes novos em
   `_framework/scripts/tests/test_check_hooks.py`.
3. `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v`.
4. `python3 _framework/scripts/render_prompts.py` (sincroniza a cópia da
   skill) e conferir com `--check`.
5. Regressão: suíte inteira, `ruff`, `mypy`, `framework_check.py --auto`,
   `check_renderings.py`.

Rollout: PR no kit; sync para o central em PR separado depois do merge
(mesmo padrão de `SDD-DTF-0018`/`0020`).
Rollback: reverter o PR restaura a checagem estrita anterior (mais
restritiva, nunca insegura).
Observabilidade: `check_hooks.py` roda em `framework_check.py --auto` e
no CI do kit; nenhuma mudança de superfície observável além das
mensagens de problema.

Riscos:
- Um `command` malicioso poderia tentar se disfarçar como referência
  válida (ex. `"$CLAUDE_PROJECT_DIR_FALSO/x.py"`) — mitigado porque
  `startswith` exige o prefixo exato `$CLAUDE_PROJECT_DIR/` (barra
  incluída), não apenas conter a substring.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1–RF5 | `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | todos passam, 10 casos ou mais |
| 2 | Regra 3 não afrouxa (sensor) | ver bloco C2 abaixo | tokenizar apenas `command` inteiro (revertendo RF1) faz `test_command_shell_com_prefixo_com_chaves` e `test_command_shell_com_prefixo_sem_chaves_entre_aspas` falharem; restaurado, os dois voltam a passar |
| 3 | Cópia da skill sincronizada | `python3 _framework/scripts/render_prompts.py --check` | exit 0, `check_hooks.py: sincronizado` |
| 4 | Regressão geral (self-host) | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.` e suíte inteira `passed` |
| 5 | Paridade com o CI | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | exit 0 |
| 6 | Renderizações consistentes | `python3 _framework/scripts/check_renderings.py` | exit 0 |

Bloco C2 (fora da tabela — edita o arquivo temporariamente, não é um
comando único): reverter `PROJECT_DIR_PREFIXES` para só a forma com
chaves e rodar a suíte; restaurar o arquivo original e rodar de novo.

## Instruções específicas para a IA implementadora

- Não alterar `PROJECT_DIR_PREFIX` para permitir substring solta (ex.
  `"CLAUDE_PROJECT_DIR" in token`) — precisa continuar sendo prefixo
  exato (`startswith`), senão vira um afrouxamento real de RF06, não uma
  correção.
- Não tokenizar `args` com `shlex` — itens de `args` no JSON de
  `settings.json` já chegam como tokens discretos (o Claude Code os passa
  diretamente como argv, sem shell); tokenizá-los de novo pode quebrar um
  caminho legítimo com espaço.
- Não mexer em `validate_state.py`, `test_discover.py`, nem
  `verify-sdd.md` — escopo de agentes irmãos rodando em paralelo
  (SDD-DTF-0024, 0025, 0026).
- Não mexer nas regras 1, 2 e 5 de `check_settings`, nem em
  `render_prompts.py`, nem em `workflow-rules.yaml`.
- Rodar `python3 _framework/scripts/render_prompts.py` (sem `--check`)
  depois de editar `check_hooks.py`, e commitar a cópia gerada da skill
  no mesmo PR.
- Branch `sdd/SDD-DTF-0027-check-hooks-shlex` a partir de `main`, PR —
  nunca commit direto (gate seção 14). Conventional Commits com
  `Refs: SDD-DTF-0027`.
- Conflito de merge esperado em `docs/sdd/registry.yaml` (outros agentes
  em paralelo escrevendo 0024–0026) — não é bug desta SDD, resolvido pelo
  humano na hora do merge.

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF1–RF5 têm código e teste correspondentes.
- [x] Arquivos tocados só entre: `_framework/scripts/check_hooks.py`,
      `_framework/scripts/tests/test_check_hooks.py`, a cópia gerada
      `_framework/skills/doc-traceability-framework/scripts/check_hooks.py`,
      e esta SDD e o registry (status/evidência).
- [x] Nenhuma abstração, config ou refactor extra sem requisito acima —
      `_items` permanece intacta para a regra de `--report-only`,
      `_tokens` é função nova e mínima, só para as regras 3 e 4.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
A tabela fica **nesta seção**; `docs/sdd/validation.md` é o relatório
complementar.

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

**Verificador independente:** sim — sessão nova, sem ler o histórico da sessão que implementou. A tabela e os comandos abaixo foram refeitos do zero nesta sessão; a versão anterior (marcada "não independente") foi descartada como insumo.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | `12 passed in 0.58s`, exit 0 (11 do escopo desta SDD + 1 de SDD-DTF-0029, follow-up já mergeado no mesmo arquivo) | ver critério 2 | Sim |
| 2 | Bloco C2: `PROJECT_DIR_PREFIXES` editado para `("${CLAUDE_PROJECT_DIR}/",)` (só a forma com chaves), suíte rodada, depois restaurado com `git checkout -- _framework/scripts/check_hooks.py` | Mutação: `1 failed, 11 passed` — `test_command_shell_com_prefixo_sem_chaves_entre_aspas` falha (`assert ['PreToolUse ...OJECT_DIR/).'] == []`). Restaurado: `12 passed in 0.11s`, `PROJECT_DIR_PREFIXES` de volta com as duas formas | mutação manual, discrimina (falha estreitada, passa restaurada) | Sim |
| 3 | `python3 _framework/scripts/render_prompts.py --check` | exit 0; `.../scripts/check_hooks.py: sincronizado`, entre as demais renderizações "em dia"/"sincronizado" | checagem mecânica de sincronismo, sem sensor de mutação dedicado | Sim |
| 4 | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.`, exit 0; suíte `81 passed in 3.60s`, exit 0 | Regressão geral, sem sensor dedicado; lógica nova coberta pelo sensor do critério 2 | Sim |
| 5 | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | `All checks passed!`; `21 files already formatted`; `Success: no issues found in 21 source files`, exit 0 | Checagem estática de paridade com o CI, sem sensor dedicado | Sim |
| 6 | `python3 _framework/scripts/check_renderings.py` | `✅ 5 renderização(ões) concordam com workflow-rules.yaml (8 tipos ativos, 6 Iron Laws, 4 níveis).` (2 avisos pré-existentes sobre PRD/TS legados, não relacionados a esta SDD), exit 0 | Regressão geral, sem sensor dedicado | Sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0020 (RF06, origem da regra 3 corrigida aqui) |
