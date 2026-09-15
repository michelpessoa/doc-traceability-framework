# Verificação — SDD-DTF-0018

- **Veredito:** PASS
- **Diff verificado:** `bf1b6af..2c02209` (commit `16ae117`, mergeado via PR #58)
- **Verificador independente:** sim — subagente separado da sessão implementadora, sem ler o histórico dela; entrada foi só `docs/sdd/SDD-DTF-0018.md` e o diff acima. Verificação em 2026-09-14 na branch `docs/sdd-dtf-0018-verificacao` (a partir de `origin/main` em `2c02209`).

A tabela de evidência canônica está dentro da SDD (seção "Evidência de verificação"); este arquivo é o relatório complementar.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1. RF1–RF5 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | `10 passed in 0.69s`, exit 0 | 6 mutações temporárias, cada uma derruba exatamente o teste esperado (detalhe abaixo); restaurado, `10 passed` | sim |
| 2. Caso real viverMelhor | bloco C2 (`validate_state.py .../viverMelhor/docs/sdd --report-only` filtrado por `grep -c -e SDD-EVM-000 -e SDD-EVM-0012`) | `0`; relatório completo `✅ 20 documento(s) verificados` | com o `validate_state.py` de `bf1b6af` a mesma contagem dá `21` | sim |
| 3. Skill sincronizada | `python3 _framework/scripts/render_prompts.py --check` | exit 0, `validate_state.py: sincronizado` | cópia da skill com linha extra: exit 1 `divergente`; restaurada, exit 0 | sim |
| 4. Regressão geral | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.`; `17 passed` | regressão geral, sem sensor dedicado | sim |
| 5. Paridade CI | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | `All checks passed!`, `11 files already formatted`, `Success: no issues found in 11 source files` | estático, sem sensor dedicado | sim |

Checagem mecânica na SDD verificada, depois de preencher a evidência e mudar o status: `python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0018.md` → `✅ 1 documento(s) verificados: nenhuma SDD implemented sem evidência.`, exit 0 (primeira execução deu exit 1, ver descompasso 3). `python3 _framework/scripts/framework_check.py --auto` → `✅ Todas as verificações do framework passaram.` (docs/sdd: 21 documentos ok), exit 0.

### Sensores do critério 1 (mutações em `_framework/scripts/validate_state.py`, restauradas por cópia do original, nunca commitadas)

| Mutação | Teste que falhou | Resultado |
|---|---|---|
| RF1: `fm.get("created")` → `None` (força fallback por versão) | `test_legado_antes_da_regra_nao_reprova` | 1 failed, 9 passed |
| RF2: escopo sempre a linha inteira | `test_na_no_sensor_nao_reprova` | 1 failed, 9 passed |
| RF2: remove `"passou"` das chaves verificadas | `test_na_no_passou_reprova` | 1 failed, 9 passed |
| RF3: `col = 1` fixo | `test_tabela_seis_colunas_comando_vazio` | 1 failed, 9 passed |
| RF4: sem cabeçalho reconhecível checa lista vazia | `test_sem_cabecalho_reconhecivel_linha_inteira` | 1 failed, 9 passed |
| RF5: anexa `# rule_applies(x)` ao script | `test_nenhum_validador_chama_rule_applies_direto` | 1 failed, 9 passed |

Não houve sensor para a comparação `>=` do mesmo dia (`test_mesmo_dia_da_regra_reprova`): ela mora em `framework_lib.rule_applies_since_date`, que a SDD proíbe alterar e que está fora do diff.

## Conformidade requisito ↔ código

- RF1: `check_sdd` lê o front-matter antes, chama `load_rules()` uma vez e define `applies` com `rule_applies_since_date(rules, RULE_SINCE[rule], fm.get("created"), version)`. Import trocado.
- RF2/RF3: `table_with_header` nova; `table_rows` mantida (delegando) e usada em `n_criteria`; `cmd_idx` e `checked_idx` exatamente como na especificação técnica.
- RF4: sem colunas reconhecidas, linha inteira para termos assumidos e `row[1]` para comando vazio.
- RF5: arquivo de teste com os 10 testes da tabela da SDD, nomes idênticos.
- Caso de borda "duas colunas comando → primeira": conferido por chamada direta a `check_evidence` (primeira vazia, segunda preenchida → `sem comando rodado`). Sem teste automatizado dedicado; não exigido pela tabela de testes da SDD.

Direção inversa: `git diff --stat bf1b6af 2c02209` lista exatamente os 3 arquivos previstos (`validate_state.py`, `tests/test_validate_state.py`, cópia gerada da skill). `framework_lib.py` intocado. Nenhuma abstração, dependência ou refactor extra.

## Descompassos encontrados

1. **Inconsistência interna da SDD em RF4 (não bloqueante, decisão do humano).** RF4 diz: sem coluna reconhecível **como comando**, aplicar as duas checagens à linha inteira. A especificação técnica consolidada diz: linha inteira só se `checked_idx` (comando, saída ou passou) estiver vazio. O código segue a especificação técnica literalmente. Efeito observável: cabeçalho `# | Critério | Saída | Passou?` com "n/a" em Critério → `[]` (o código anterior apontava). A checagem de comando vazio cai corretamente para `row[1]`. Como RF2 já manda ignorar Critério/Sensor/#, o afrouxamento real se limita a tabelas sem coluna Comando que tenham colunas de resultado com nome fora das chaves. Caminhos: (a) ajustar o texto de RF4 para "sem nenhuma coluna reconhecida" (escopo real); (b) nova SDD pequena apertando o código para a letra de RF4 (se não houver `cmd_idx`, linha inteira). Classifiquei como PASS porque todo item da especificação técnica tem código conforme e a tabela de testes aprovada foi cumprida; o humano pode reverter.
2. **Dado de contexto desatualizado (informativo).** O resumo executivo cita 6 problemas reais em SDD-EVM-0013/0014/0015; hoje o viverMelhor já os corrigiu (`8bd6f85`), então o relatório completo dá zero. O critério 2 continua válido (baseline antigo 21 → 0), e o não-afrouxamento é coberto pelos testes do critério 1, como a SDD prevê.

3. **Falso positivo pré-existente de `table_rows` encontrado ao validar esta própria SDD (fora do diff, não bloqueante).** `validate_state.py docs/sdd/SDD-DTF-0018.md` saiu com exit 1: "6 critério(s) de aceite mas só 5 linha(s) de evidência". Causa: `table_rows` faz `strip()` e aceita qualquer linha que comece com `|`, inclusive dentro de bloco de código cercado — a continuação `  | grep -c ...` do bloco C2 foi contada como 6º critério. O comportamento já existia antes de `bf1b6af` (a SDD mandou manter `table_rows`). Correção aplicada nesta verificação, só editorial: o pipe do bloco C2 foi movido para o fim da linha anterior (`--report-only |`), mesma semântica de shell (rodado de novo: `0`). Depois disso, exit 0. Sugestão para o humano: SDD pequena para `table_rows`/`table_with_header` ignorarem linhas dentro de blocos cercados.

## Lições

- Red flag: requisito em prosa e pseudocódigo da especificação técnica descrevendo a mesma condição com gatilhos diferentes ("sem coluna comando" vs "sem nenhuma coluna reconhecida"). O implementador segue o pseudocódigo e o teste só cobre o caso em que os dois coincidem (`a | b | c`). Ao escrever SDD, o caso de borda de fallback precisa de um teste que separe as duas leituras.
- Red flag: parser de tabela markdown baseado em "linha começa com `|`" sem saber de blocos de código. Comando de shell com pipe em linha de continuação dentro de uma SDD vira linha de tabela. Até corrigir, em SDD, pipe de shell no fim da linha, nunca no começo.

---

# Verificação — SDD-DTF-0020

- **Veredito:** PASS nos critérios automatizáveis 1–8; critério 9 (manual) **pendente** → status permanece `approved`.
- **Diff verificado:** `9d98af0..de1c893` (commits `0185688`, `d119055`, mergeados via PR #61)
- **Verificador independente:** sim — subagente separado da sessão implementadora, sem ler o histórico dela; entrada foi só `docs/sdd/SDD-DTF-0020.md` e o diff acima. Verificação em 2026-09-14 na branch `docs/sdd-dtf-0020-verificacao` (a partir de `origin/main` em `de1c893`).

A tabela de evidência canônica está dentro da SDD (seção "Evidência de verificação"); esta seção é o relatório complementar.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1. RF01, RF02 | `python3 -m pytest _framework/scripts/tests/test_hook_session_start.py -v` | `8 passed`, exit 0 | M1–M5 derrubam a suíte | sim |
| 2. RF03 | `python3 -m pytest _framework/scripts/tests/test_hook_post_edit.py -v` | `8 passed`, exit 0 | M6–M10 derrubam a suíte | sim |
| 3. RF04, RF05 | `python3 -m pytest _framework/scripts/tests/test_render_prompts_mechanization.py -v` | `12 passed`, exit 0 | M11–M14 derrubam a suíte | sim |
| 4. RF06 | `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | `8 passed`, exit 0 | M15–M20 derrubam a suíte | sim |
| 5. RF05 gerado | one-liner da SDD sobre `.claude/settings.json` | `['PostToolUse', 'PreToolUse', 'SessionStart'] {'command'} True` | via critério 3 + `render_prompts.py --check` | sim |
| 6. RF06 `--auto` | `check_hooks.py && framework_check.py --auto` | `hooks ok`, `-- hooks do harness`, `Todas as verificações do framework passaram`, exit 0 | M21 remove a linha `-- hooks do harness` | sim |
| 7. RF03 caso real | bloco C7 literal | `exit=2` com stderr citando `SDD-DTF-0017`; depois `exit=0` sem saída | M22, M23 impedem `exit=2` | sim |
| 8. Regressão | ruff, ruff format, mypy, pytest, `render_prompts.py --check`, `check_renderings.py` | `All checks passed!`, `17 files already formatted`, `no issues found in 17 source files`, `46 passed`, `sincronizado`, `5 renderização(ões) concordam`; todos exit 0 | estático/regressão, sem sensor dedicado | sim |
| 9. Sessão real | não rodado — manual, requer sessão real do usuário | sem saída | sem sensor — manual | pendente |

### Sensores (mutações temporárias em `_framework/scripts/`, restauradas com `git checkout --`, nunca commitadas; `git status --short` vazio ao final)

Cada linha: mutado → comando do critério com exit diferente de 0; restaurado → exit 0.

| Id | Arquivo | Mutação | Critério |
|---|---|---|---|
| M1 | `hook_session_start.py` | `find_handoffs` sem `docs/*/HANDOFF.md` | 1 |
| M2 | `hook_session_start.py` | `docs/*` antes da raiz | 1 |
| M3 | `hook_session_start.py` | `post-compact` não imprime | 1 |
| M4 | `hook_session_start.py` | imprime mesmo sem HANDOFF | 1 |
| M5 | `hook_session_start.py` | ignora `CLAUDE_PROJECT_DIR` e `cwd` | 1 |
| M6 | `hook_post_edit.py` | `return 2` → `return 0` | 2 |
| M7 | `hook_post_edit.py` | problemas em stdout | 2 |
| M8 | `hook_post_edit.py` | `check_sdd` pulado | 2 |
| M9 | `hook_post_edit.py` | filtro de tipo do framework removido | 2 |
| M10 | `hook_post_edit.py` | warnings somados aos problemas | 2 |
| M11 | `render_prompts.py` | `prompt` aceito em hook | 3 |
| M12 | `render_prompts.py` | caminho `_framework/` relativo aceito | 3 |
| M13 | `render_prompts.py` | checagem aplicada também a `artifact_type: command` | 3 |
| M14 | `render_prompts.py` | todos os matchers colapsados em um grupo | 3 |
| M15–M19 | `check_hooks.py` | regras 1, 2, 3, 4, 5 desligadas uma a uma | 4 |
| M20 | `check_hooks.py` | regra 3 reprova também prefixo correto | 4 |
| M21 | `framework_check.py` | integração `--auto` desligada | 6 |
| M22, M23 | `hook_post_edit.py` | `return 0` / `check_sdd` pulado, rodando o bloco C7 | 7 |

Provas extras (sem teste automatizado dedicado):
- RF04 "antes de escrever qualquer arquivo": `hook_command` relativo injetado no `workflow-rules.yaml` real → `render_prompts.py` exit 1 citando `enforce_content_quality_gate`; `git status` só mostrava o YAML mutado (restaurado).
- RF06 retorno antecipado: diretório sem `registry.yaml` com `prompt` em SessionStart → `framework_check.py --auto` exit 1 (`❌ 1 verificação(ões) falharam.`); com `--report-only`, exit 0.
- Casos de borda de RF03: exceção no validador → stderr `hook_post_edit: erro interno — boom`, exit 1; payload não-dict → exit 0; `file_path` relativo resolvido pelo `cwd` do payload; SDD real validada em 0,26 s (RNF < 2 s).
- Contrato do harness conferido na documentação oficial (`https://code.claude.com/docs/en/hooks`, 2026-09-14): `args` é forma exec (sem shell) com `${CLAUDE_PROJECT_DIR}` substituído em `command` e em cada item de `args`; SessionStart aceita `*` e `compact` e injeta stdout no contexto; PostToolUse com exit 2 mostra stderr ao modelo. O `.claude/settings.json` gerado está nesse contrato.

## Conformidade requisito ↔ código (SDD-DTF-0020)

- RF01/RF02: `hook_session_start.py` com `project_root`, `find_handoffs`, `main` e mensagens idênticas à especificação; modo desconhecido e stdin inválido → exit 0 sem saída.
- RF03: `hook_post_edit.py` com `framework_types`, `problems_for`, `main`; soma só `problems`; formato de stderr idêntico. Não filtra `tool_name` (confia no matcher `Edit|Write`) — coerente com a especificação técnica.
- RF04: `validate_mechanizations` estendida só para `artifact_type` iniciando em `hook_`; chamada antes de qualquer escrita (`render_prompts.py:736`).
- RF05: os quatro blocos de `workflow-rules.yaml` exatamente como na SDD; `enforcement_patterns` intocado; `.claude/settings.json` gerado bate com o esperado.
- RF06: `check_hooks.py` com as 5 regras; `framework_check.py --auto` roda antes de `discover` e o retorno antecipado respeita falhas.
- Cópias da skill (`scripts/*.py`, `references/workflow-rules.yaml`) byte-idênticas às fontes (`cmp`).

Direção inversa: `git diff --stat 9d98af0 de1c893` lista 17 arquivos, todos na checklist de escopo da SDD. `guard_bash.sh`, `check_commit.py` e `framework_lib.py` fora do diff. Nenhuma dependência ou abstração sem requisito.

## Descompassos encontrados (SDD-DTF-0020)

1. **`check_hooks.py` regra 3 dá falso positivo em comando shell-form escrito à mão (não bloqueante para 1–8; decisão do humano).** O código segue literalmente a especificação técnica ("contendo `_framework/` sem **começar** por `${CLAUDE_PROJECT_DIR}/`") e avalia `command` inteiro como um item. RF06 diz só "com caminho `_framework/` sem `${CLAUDE_PROJECT_DIR}/`". Provas nesta verificação, com o script existente em `tmp`:
   - `"command": "python3 ${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_post_edit.py"` → exit 1 "sem o prefixo" (o caminho **tem** o prefixo: falso positivo contra a letra de RF06);
   - `"command": "python3 \"$CLAUDE_PROJECT_DIR\"/_framework/scripts/hook_post_edit.py"` → exit 1 (forma shell que a documentação oficial exemplifica, ex.: `node "${CLAUDE_PROJECT_DIR}"/scripts/format.js --fix`; funciona após `cd`);
   - `"command": "${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_post_edit.py"` → exit 0.
   - Efeito colateral: em shell-form com script inexistente (`python3 ${CLAUDE_PROJECT_DIR}/_framework/scripts/nao_existe.py`) só sai o problema de prefixo — a regra 4 nunca avalia o token (mensagem enganosa).
   Impacto: projeto que escreva `settings.json` à mão na forma shell documentada tem `framework_check.py --auto` (CI/pre-commit) reprovado. O kit não é afetado (o gerador usa forma exec). Caminhos: (a) aceitar o escopo real e ajustar RF06 para "hooks do framework devem usar forma exec, com item iniciando por `${CLAUDE_PROJECT_DIR}/`", documentando a restrição na mensagem; (b) SDD pequena para a regra 3 tokenizar `command` shell-form (`shlex.split`) e aceitar `${CLAUDE_PROJECT_DIR}/`, `$CLAUDE_PROJECT_DIR/` e `"$CLAUDE_PROJECT_DIR"/`, com a regra 4 aplicada ao token.
2. **Critério 9 não verificado (bloqueia `implemented`).** É manual e exige sessão real do usuário.

## Pendente para fechar o critério 9 da SDD-DTF-0020 (usuário)

No checkout principal do kit, em `main` com PR #61 (`de1c893` ou posterior) e Claude Code instalado:

1. Garanta um `HANDOFF.md` na raiz (o checkout principal já tinha um não rastreado; senão crie um com uma linha qualquer).
2. Rode `claude --debug` numa **sessão nova** (não `--resume`/`--continue`) e mande como primeira mensagem, por exemplo, `oi`.
   - Esperado: a primeira resposta cita a skill `pickup` / o `HANDOFF.md`; no log de debug, execução do hook SessionStart `hook_session_start.py pickup` com exit 0 e stdout `HANDOFF.md encontrado em: HANDOFF.md. …`.
3. Na mesma sessão, peça: `copie docs/sdd/SDD-DTF-0017.md para docs/sdd/SDD-DTF-0017-copia.md e depois, com a ferramenta Edit, apague todas as linhas de dados da tabela "Evidência de verificação" da cópia, mantendo cabeçalho e separador`.
   - Esperado: após o Edit, o modelo relata o feedback `framework: … viola gate(s)` / `'Evidência de verificação' está vazia e o status é implemented`; no debug, `hook_post_edit.py` com exit 2 e esse stderr.
   - Depois apague `docs/sdd/SDD-DTF-0017-copia.md` sem commitar.
4. Registre na SDD-DTF-0020, linha 9 da "Evidência de verificação": `claude --debug` + os dois prompts; o trecho do log com os dois hooks (comando, exit code, stdout/stderr); a frase do modelo que cita pickup e a que relata o stderr; Sensor "sem sensor — manual"; Passou? `sim`. Só então mover o status para `implemented` (SDD e registry) e rodar `python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0020.md` e `python3 _framework/scripts/framework_check.py --auto`.

## Lições (SDD-DTF-0020)

- Red flag: sensor de configuração que compara prefixo de string num campo que o harness aceita em duas formas (exec e shell). A regra precisa ser escrita por forma, com teste para cada exemplo da documentação oficial, ou o requisito precisa restringir explicitamente uma forma.
- Red flag: especificação técnica que troca "sem o prefixo" (RF) por "sem começar por" (pseudocódigo) — o implementador segue o pseudocódigo e os testes só cobrem o caso em que as duas leituras coincidem.
