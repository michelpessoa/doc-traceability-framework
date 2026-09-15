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
