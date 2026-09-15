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

# Verificação — SDD-DTF-0021

- **Veredito:** PASS (com descompassos não bloqueantes, decisão do humano abaixo)
- **Diff verificado:** `36f05e2^1..36f05e2` (merge do PR #62; commits `42fce27`, `0a02f4a`)
- **Verificador independente:** sim (subagente separado; não li o histórico da sessão que implementou)

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1. RF07 guard por segmento | `python3 -m pytest _framework/scripts/tests/test_guard_bash.py -v` | `18 passed` | M1, M2, M3 falham (3, 3, 2 failed); M4 não falha (mutação equivalente, ver descompasso 1) | sim |
| 2. RF08 merge real | `python3 -m pytest _framework/scripts/tests/test_check_commit.py -v` | `4 passed` | M5, M6, M7 falham (1 failed cada) | sim |
| 3. Gerado bate e sem laço em pipe | `python3 _framework/scripts/render_prompts.py --check && grep -cF 'done <<<"$segments"' _framework/scripts/guard_bash.sh` | exit 0; `1` | M8 (gerador sem here-string): `--check` reprova; M4: grep dá `0` | sim |
| 4. Incidente real (bloco C4) | bloco C4 da SDD, executado de arquivo de script | `exit=0` / `guard_bash: bloqueado — push direto em main. Abra PR.` `exit=2` | coberto por M1/M2 | sim |
| 5. RF08 no histórico do kit | `python3 _framework/scripts/check_commit.py --last 30` | `✅ 17 mensagem(ns) de commit no formato esperado.`, exit 0 | histórico real, sem sensor próprio | sim |
| 6. Regressão e renderizações | `ruff check ... && ruff format --check ... && mypy ... && python3 -m pytest && check_renderings.py && framework_check.py --auto` | `All checks passed!`; `19 files already formatted`; `no issues found in 19 source files`; `68 passed`; `5 renderização(ões) concordam`; `Todas as verificações do framework passaram.` | sem sensor dedicado | sim |

Checagem mecânica: `python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0021.md` e `python3 _framework/scripts/framework_check.py --auto` depois de preencher a evidência e mudar o status (saídas no PR desta verificação).

### Sensores (mutações temporárias no disco, restauradas por cópia do original, nunca commitadas)

| Mutação | Arquivo | Resultado |
|---|---|---|
| M1: `re.split(...)` trocado por `[command]` (sem divisão) | `guard_bash.sh` | 3 failed, 15 passed |
| M2: sem normalizar `git -C <caminho>` | `guard_bash.sh` | 3 failed, 15 passed |
| M3: padrão push-main volta a ter `*` inicial | `guard_bash.sh` | 2 failed, 16 passed |
| M4: `done <<<"$segments"` trocado por `printf ... \| while ... done` | `guard_bash.sh` | 18 passed (não discrimina); grep do critério 3 dá `0` |
| M5: remove `if len(parents.split()) > 1: continue` | `check_commit.py` | 1 failed, 3 passed |
| M6: `merge_in_progress` retorna `False` | `check_commit.py` | 1 failed, 3 passed |
| M7: `merge_in_progress` retorna `True` | `check_commit.py` | 1 failed, 3 passed |
| M8: gerador emite `done` sem here-string | `render_prompts.py` | `render_prompts.py --check` com `❌ divergente` |

Depois das mutações: `22 passed` nos dois arquivos de teste, `git status --short` sem mudanças em código, `render_prompts.py --check` exit 0.

## Conformidade requisito ↔ código

- RF07: `enforcement_patterns` idênticos ao bloco da especificação técnica; `build_guard_bash` gera o trecho Python de divisão (`&&`, `||`, `;`, `|`, `\n`) e normalização de `git -C`, variável `segments`, `[ -z "$segments" ] && exit 0`, `while IFS= read -r segment` com `done <<<"$segments"`, linha de comentário citando SDD-DTF-0021. `guard_bash.sh` e cópias da skill batem com o gerador (`--check`). Mensagens de `deny` e `hook_command` intactos.
- RF08: `messages_from_range` com `%H%x00%P%x00%B%x00---END---` e descarte de commit com mais de um pai (assinatura e retorno inalterados, `--last` herda); `merge_in_progress()` via `git rev-parse --git-path MERGE_HEAD` + `is_file()`, chamado no modo arquivo antes de ler a mensagem; falha do git retorna False. `check_message` e regra `Merge `/`Revert ` intactas.
- Testes: os 17 casos + stdin inválido e os 4 casos de RF08 da tabela de testes, com os exits exigidos.
- Casos de borda conferidos à mão (script em arquivo): linha de heredoc começando por `git push origin main` → exit 2; `git push` sem argumentos → exit 0; payload sem `tool_input.command` → exit 0; `check_commit.py msg` fora de repositório git com mensagem fora do formato → exit 1. Sem teste automatizado para esses; não exigidos pela tabela de testes.

Direção inversa: `git diff --stat 36f05e2^1 36f05e2` lista 9 arquivos, todos na lista da verificação de escopo (`workflow-rules.yaml`, `render_prompts.py`, `guard_bash.sh`, `check_commit.py`, os dois testes novos e as cópias geradas `references/workflow-rules.yaml`, `scripts/check_commit.py`, `scripts/render_prompts.py` da skill). Nada em `.claude/`, `.githooks/`. Nenhuma abstração, dependência ou refactor além do descrito (`merge_in_progress` é a extração nomeada do passo que a especificação descreve em `main()`).

## Descompassos encontrados

1. **Premissa da SDD sobre o laço em pipe é falsa neste script (não bloqueante).** A especificação diz que com `printf ... | while` "o `exit` dentro do pipe só sai do subshell e o comando passaria". Executado num script mínimo com `deny` dentro de `printf | while`: com `set -euo pipefail` → exit 2, nada depois do pipe roda; com `set -eu` (sem pipefail) → exit 2 também; só sem `set -e` (`set -o pipefail` sozinho ou nenhum) → exit 0 e o script segue. Quem propaga é o `set -e`, não o `pipefail`: o `while` é o último elemento do pipe, então o status 2 do subshell já é o status do pipeline. Consequência: M4 é mutação equivalente com o cabeçalho atual, e os testes corretamente não a distinguem; a decisão do here-string só é protegida pelo grep do critério 3. Continua sendo a escolha mais robusta (não depende de `set -e`, que é frágil em funções e condicionais), mas a justificativa escrita está errada. Caminho sugerido: corrigir a frase na SDD/SPEC para "sem `set -e` o exit sairia só do subshell; o here-string não depende disso".
2. **Caso de borda "separador dentro de aspas" não se comporta como a SDD diz (não bloqueante, decisão do humano).** Tabela de casos de borda: `-m "a; git push origin main"` → "vira segmento e bloqueia". Executado: `git commit -m "a; git push origin main"` → **exit 0**. O segmento vira `git push origin main"` (aspas finais), e nenhum dos padrões especificados casa (`" main"` exige terminar em ` main`, `" main "*` exige espaço depois). O código segue os padrões da especificação técnica literalmente; a inconsistência é interna à SDD (exemplo do caso de borda vs padrões). A frase "falha para o lado seguro" (casos de borda e Riscos) também não vale para esse exemplo; na prática o texto entre aspas de um `commit -m` não executa push, mas `bash -c "cd x; git push origin main"` também passa — já coberto pelo risco aceito "forma não prevista" e pelo `.githooks/pre-push`. Caminhos: (a) corrigir o caso de borda na SDD para "segmento termina em aspas e não casa: passa; limite aceito, coberto pelo pre-push" (escopo real); (b) nova SDD apertando os padrões (ex.: `"git push"*" main"*` com fronteira que aceite aspas) com teste dedicado. Classifiquei como PASS seguindo o precedente da SDD-DTF-0018 (inconsistência interna, código conforme à especificação técnica e à tabela de testes aprovada); o humano pode reverter.
3. **Nome da branch de implementação (informativo).** Instruções específicas pediam `sdd/SDD-DTF-0021-guardrails`; a branch foi `sdd/SDD-DTF-0021-guard-subcomando`. Compatível com o `consumption_instructions` (`sdd/SDD-DTF-0021-*`) e com o gate de branch; sem efeito no código.
4. **Warning de assunto com 78 caracteres (informativo, não é desta implementação).** Em `36f05e2`, `check_commit.py --last 30` não emite warning. O warning aparece com janela maior (`--last 45`): `64800703: assunto com 78 caracteres (>72)` — commit antigo da SDD-DTF-0016, junto com `afeae144` (87) e `1a836267` (73). Os dois commits do PR #62 passam limpos (`--range 36f05e2^1..0a02f4a` → `2 mensagem(ns)`, exit 0). Warning não altera exit.

## Lições

- Red flag: justificativa de desenho sobre semântica de shell escrita sem rodar no cabeçalho real (`set -euo pipefail`). Ao afirmar "isso quebraria", o sensor precisa ser um teste que falhe com a alternativa; se nenhum teste consegue falhar, a alternativa é equivalente e a justificativa tem de ser outra — ou o critério vira um grep, como aqui.
- Red flag: exemplo de caso de borda que não está na tabela de testes. Os 17 casos simulados passaram; o único exemplo de borda com resultado afirmado e sem teste estava errado. Todo caso de borda com comportamento afirmado entra na tabela de testes ou é marcado "não testado".
