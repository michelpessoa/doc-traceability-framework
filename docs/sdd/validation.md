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
