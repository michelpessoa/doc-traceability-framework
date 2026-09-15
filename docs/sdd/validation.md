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

# Verificação — SDD-DTF-0019

- **Veredito:** PASS
- **Diff verificado:** `de1c893..ccd5c1d` restrito ao que o merge #59 trouxe = commit `0d8575c` (`git show --stat 0d8575c`: 3 arquivos, 41 inserções, 14 remoções)
- **Verificador independente:** sim — subagente separado da sessão implementadora, sem ler o histórico dela; entrada foi só `docs/sdd/SDD-DTF-0019.md` e o diff acima. Verificação em 2026-09-14 na branch `docs/sdd-dtf-0019-verificacao` (a partir de `origin/main` em `36f05e2`), em worktree própria.

A tabela de evidência canônica está dentro da SDD (seção "Evidência de verificação"); esta seção é o relatório complementar.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1. RF1, RF2 | `grep -n "da própria SDD" ...; grep -n "não a substitui" ...` (em `verify-sdd.md`) | linha 41 (passo 2) e linha 82 (passo 4) | frases removidas: ambas vazias, exit 1; restaurado, 2 ocorrências | sim |
| 2. RF3 | `grep -n "### 5. Checagem mecânica antes de mudar status" ...; grep -c "Checagem mecânica complementar" ...` | `111:### 5. ...`; `0` | cabeçalho antigo restaurado: vazio e `1`; desfeito, `0` | sim |
| 3. RF3 por arquivo | `grep -c "validate_state.py docs/sdd$" _framework/procedures/verify-sdd.md` | `0` | comando por diretório reinserido: `1`; desfeito, `0` | sim |
| 4. RF4, RF5 | `python3 -c "import yaml; ..."` (literal da SDD) | `True True` | trechos novos removidos do YAML: `False False`; desfeito, `True True` | sim |
| 5. Caso real | bloco C5, com a cópia de `docs/sdd` no scratchpad em vez de `mktemp -d` | cópia sem evidência: `❌ ... 'Evidência de verificação' está vazia e o status é implemented`, `exit=1`; original: `✅ 1 documento(s) verificados`, `exit=0` | o bloco é o sensor (procedimento é texto) | sim |
| 6. Renderizações e regressão | `render_prompts.py --check && check_renderings.py && framework_check.py --auto` | `5 renderização(ões) concordam`; `✅ Todas as verificações do framework passaram.`; exit 0 | YAML mutado sem regenerar: `--check` exit 1 `divergente`; restaurado, exit 0 | sim |

Todas as mutações foram feitas no working tree da worktree de verificação e desfeitas com `git checkout -- <arquivo>`; `git status --short` vazio antes de editar a SDD. Nenhuma mutação commitada.

Checagem mecânica (passo 5 do procedimento novo, aplicado a ele mesmo): status para `implemented` na SDD e no `registry.yaml`, `python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0019.md` → `✅ 1 documento(s) verificados: nenhuma SDD implemented sem evidência.`, exit 0 na primeira execução. `registry.md` regenerado com `generate_registry_md.py docs/sdd`; `framework_check.py --auto` → `✅ Todas as verificações do framework passaram.`

## Conformidade requisito ↔ código

- RF1: passo 2 (linhas 39–41) com "**da própria SDD** — é essa tabela que o gate 16 e `validate_state.py` leem."
- RF2: passo 4 abre com o modelo da seção da SDD (ponteiro para `validation.md` com veredito, `**Verificador independente:**`, tabela com uma linha por critério) e o parágrafo "complementa ... **não a substitui** ... gate 16 violado", antes do modelo de `validation.md`. Texto idêntico ao da especificação técnica.
- RF3: `### 5. Checagem mecânica antes de mudar status` com (a) status no front-matter e registry, (b) `validate_state.py docs/sdd/SDD-{PROJETO}-{SEQ}.md`, (c) volta para `approved` com exit ≠ 0 antes de commit, (d) não commitar `implemented` sem exit 0. Seção antiga removida; ressalva "necessário e não suficiente" mantida. Última frase do passo 4 virou "`PASS` autoriza o passo 5."
- Red flag nova na tabela: presente, texto literal.
- RF4, RF5: `produces` e `purpose` com o texto literal da especificação técnica; cópia da skill idêntica (render `--check` exit 0).

Direção inversa: `git show --stat 0d8575c` lista exatamente `verify-sdd.md`, `workflow-rules.yaml` e a cópia gerada da skill. No YAML, só as duas linhas previstas. Passos 1 e 3 sem alteração. Nenhum script, regra ou gate alterado.

## Descompassos encontrados

Nenhum bloqueante. Avaliação dos dois achados conhecidos da implementação:

1. **Quebra de linha do passo 2 deslocada (conforme).** A especificação técnica cita o parágrafo como blockquote com quebras próprias; a implementação mantém o texto palavra por palavra e só junta "leem." à linha de `**da própria SDD**`. Quebra de linha em markdown não altera o conteúdo normativo, e o critério 1 é `grep` por linha — com "da própria" e "SDD" em linhas diferentes o critério falharia sem que o requisito estivesse descumprido. Aceito.
2. **"Escreva `validation.md` ao lado da SDD:" mantido no passo 4 (conforme).** A especificação manda inserir o novo trecho "antes do bloco do `validation.md`", o que pressupõe o bloco mantido; nenhum RF manda removê-lo. O modelo de `validation.md` ainda repete a tabela de evidência, mas agora subordinado ao parágrafo "não a substitui". Aceito.

Informativos (fora do escopo desta SDD, sem ação aqui):

3. O modelo da seção da SDD aponta para `docs/sdd/validation.md` literal, enquanto o viverMelhor usa `validation-EVM-00XX.md` e este kit acumula várias seções num mesmo `validation.md`. A SDD declara a convenção de nome fora de escopo; há SDD-DTF-0023 em rascunho em outra branch (ainda não em `main`) tratando do assunto.
4. `docs/guias/guia-tecnico.md:263` ainda lista `validate_state.py docs/sdd` por diretório, mas numa lista geral de ferramentas (auditoria), não no fluxo de verificação; não contradiz o passo 5.
5. O passo 3 do procedimento sugere `git stash` como espaço descartável; em ambiente com várias worktrees e sessões em paralelo o stash é compartilhado. Esta verificação usou `git checkout -- <arquivo>` na worktree própria. Candidato a SDD pequena, não é descompasso desta.

## Lições

- Red flag: critério de aceite por `grep` de linha sobre texto normativo reflowable. A quebra de linha passa a fazer parte do contrato sem estar escrita em nenhum RF. Ao escrever SDD de procedimento em texto, buscar trechos curtos que caibam numa linha, ou usar `grep -z`/Python sobre o arquivo inteiro.
- Red flag: sensor de procedimento em texto é naturalmente fraco (a mutação é o inverso literal do `grep`). O bloco C5, que exercita o comando que o texto manda rodar contra um caso real, é o que dá discriminação de comportamento; SDD de procedimento deve ter pelo menos um critério desse tipo.

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

# Verificação — SDD-DTF-0023

- **Veredito:** PASS
- **Diff verificado:** 756c83b..e31be1e (PR #67, commit de implementação 291d548)
- **Verificador independente:** sim (sub-agent separado, sem ler a sessão que implementou)

A tabela completa de evidência (comandos, saídas e sensores dos critérios 1–6) está na seção "Evidência de verificação" da própria `SDD-DTF-0023.md`. Resumo:

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `pytest test_operational_artifacts.py -v` | 3 passed | M1a, M1b, M1c, M3 → falham; restaurado → passa | Sim |
| 2 | `python3 -c "... 'validation-*.md' in d['operational_artifacts'] ..."` | `True True` | chave renomeada → `False True` | Sim |
| 3 | bloco C3 (antes = `756c83b`) | antes `exit=1` com `validation-EVM-0013.md: sem bloco de front-matter`; depois `exit=0` | o bloco é o sensor | Sim |
| 4 | `pytest test_discover.py -v` | 1 passed | M4a–M4e → falham; 2 mutações sobrevivem (ver lições) | Sim |
| 5 | bloco C5 (antes = `756c83b`) | antes 3 diretórios (`.claude/worktrees/a/docs/sdd`, `docs/sdd`, `node_modules/pkg/docs`); depois `['docs/sdd']` | o bloco é o sensor | Sim |
| 6 | ruff check, ruff format --check, mypy, pytest, render_prompts --check, check_renderings, framework_check --auto | exit 0 na cadeia; 72 passed | regressão | Sim |

## Conformidade requisito ↔ código (SDD-DTF-0023)

- RF1: `framework_lib.is_operational_artifact` com `fnmatch.fnmatchcase`; `iter_documents` usa a função. Docstring atualizada.
- RF2: `workflow-rules.yaml` ganha só `validation-*.md` (purpose e `declared_in` idênticos à spec), depois de `validation.md`.
- RF3: `_FALLBACK_OPERATIONAL_ARTIFACTS = ("LESSONS.md", "HANDOFF.md", "validation.md", "validation-*.md")`.
- RF4: `framework_check.discover` com `os.walk` e poda de `.git`, `_framework`, `node_modules` e `root/.claude/worktrees`; `sorted` nos dirnames e no retorno.
- Cópias em `_framework/skills/doc-traceability-framework/` byte-idênticas às fontes (`cmp`), `render_prompts.py --check` exit 0.
- Direção inversa: `git diff --stat 756c83b e31be1e` lista 8 arquivos, todos na checklist de escopo. Nenhuma dependência, abstração ou flag sem requisito.

Casos de borda conferidos à mão (sem teste automatizado próprio):
- `.claude/agents/x/registry.yaml` descoberto; `docs/.claude/worktrees/b/registry.yaml` (worktrees não relativo à raiz) descoberto; `.git/y/registry.yaml` podado. Saída: `['.claude/agents/x', 'docs/.claude/worktrees/b']`.
- `Validation-EVM-0013.md` maiúsculo via `framework_check.py <dir>`: reprovado com "sem bloco de front-matter", enquanto `validation-EVM-0014.md` no mesmo diretório é pulado.
- `registry_tools.py validate <dir>`: aviso "existe em disco mas não está em nenhuma entrada" só para `Validation-EVM-0013.md`; herda o comportamento.
- `framework_check.py <dir>` explícito em `.../.claude/worktrees/a/docs`: valida o diretório (cabeçalho `===` e problema reportado).
- `docs/node_modules_notes`: coberto pelo teste do critério 4.
- Evidência real no checkout principal do kit (só leitura, com o `framework_check.py` desta branch, cwd = raiz principal com 1 worktree em `.claude/worktrees/`): `discover` de `756c83b` acha 8 diretórios, 4 deles dentro de `.claude/worktrees`; o de `e31be1e` acha 4, nenhum em worktree. `framework_check.py --auto` lá: 4 diretórios, exit 0.

## Descompassos encontrados (SDD-DTF-0023)

Nenhum descompasso de implementação. Observações:

1. **Formatação (não é descompasso):** `ruff` colapsou o `dirnames[:] = sorted(...)` da spec numa linha só e deixou uma linha em branco (não duas) entre os imports e `PRUNED_DIR_NAMES`. Sem efeito de comportamento; `ruff check` e `ruff format --check` passam.
2. **Blocos C3 e C5 da SDD envelheceram no merge:** usam `origin/main` como "antes", o que só vale antes do merge do PR. Depois do merge, a primeira execução usaria o código novo e o critério não discriminaria. Nesta verificação o "antes" foi `756c83b`.
3. **Cobertura do teste de RF4 incompleta, sem impacto no veredito:** duas mutações sobrevivem a `test_discover.py`: podar `worktrees` por nome em qualquer nível (em vez de só `root/.claude/worktrees`) e tirar `.git` da poda. RF4 exige as duas coisas; o comportamento correto foi conferido à mão acima. O teste segue exatamente a spec da SDD, que não prevê esses casos.

## Lições (SDD-DTF-0023)

- Red flag: critério de aceite "antes/depois" que referencia `origin/main` como estado anterior. Ele só discrimina até o merge; use o SHA da base (ou `git merge-base`) para que a verificação pós-merge continue válida.
- Red flag: requisito com qualificador ("relativo a `root`", lista de nomes podados) cujo teste só exercita os casos sem ambiguidade. Cada qualificador precisa de um caso que falhe se ele for ignorado; senão o sensor mostra mutações sobreviventes.
