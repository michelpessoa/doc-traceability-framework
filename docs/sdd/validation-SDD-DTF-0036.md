# Verificação — SDD-DTF-0036

## Rodada 2 (commit `05018cd`)

- **Veredito:** FAIL
- **Diff verificado:** `bc88c9419bc51d44c02bdae1fead031bd877e12f..05018cd1df7b1ab9f096cf9093986d4368be565e` (merge-base recapturado com `git merge-base HEAD origin/main`, branch `sdd/SDD-DTF-0036`, agora no commit `05018cd`)
- **Verificador independente:** sim (sessão separada da rodada 1 e da que implementou/corrigiu o fixture; histórico de nenhuma das duas foi lido)

Rodada 1 (abaixo) achou FAIL: o teste `test_perfil_manual_nao_exige_assertion`
usava `n/a` literal na célula "Assertion (file:line)" em vez de uma célula
de fato vazia, então a mutação que remove a guarda `esperado ==
"automatizado"` (RF05) não derrubava o teste — ruído verde, mesmo com
`check_evidence_profile` funcionalmente correto.

Uma sessão de implementação corrigiu o fixture no commit `05018cd`
("fix(test): sensor real de RF05"), trocando a célula `n/a` por uma
célula de fato vazia (`\|  \|`). Esta rodada reverificou essa correção
do zero, sem assumir que estava certa:

1. **Releitura da SDD e do diff do commit `05018cd`** — a única mudança
   de produto é no arquivo de teste (`test_validate_state.py`, célula
   de fixture); `check_evidence_profile` em `validate_state.py` não foi
   tocado nesta correção. `docs/sdd/SDD-DTF-0036.md` e
   `docs/sdd/validation-SDD-DTF-0036.md` também mudaram (registro da
   rodada 1), sem impacto em código de produção.

2. **Todos os 10 critérios de aceite rodados de novo nesta sessão**
   (não só o #5) — ver tabela de "Evidência de verificação" da SDD,
   linhas "Rodada 2". Nenhuma regressão nos que já passavam na rodada 1.

3. **Sensor de discriminação de RF05, núcleo desta rodada:**
   - Mutação: removida a guarda `esperado == "automatizado"` da
     condição em `check_evidence_profile` (`_framework/scripts/validate_state.py:301`),
     tornando a exigência de "Assertion (file:line)" preenchida válida
     para todo perfil, não só `automatizado`.
   - Rodado `pytest _framework/scripts/tests/test_validate_state.py -k
     "perfil or colunas_novas" -v` sob a mutação:
     `test_perfil_manual_nao_exige_assertion` **FALHOU** —
     `assert ['SDD-TST-0001: critério #1 com perfil esperado
     'automatizado' e 'Assertion (file:line)' vazia ...'] == []`. O
     sensor agora discrimina de fato: a rodada 1 estava correta em
     apontar ruído verde, e a correção do commit `05018cd` resolveu o
     problema.
   - Revertido por `cp` da cópia guardada antes da mutação (nunca `git
     stash`, nunca commit); `diff` entre a cópia e o arquivo restaurado
     sem saída (idênticos); `pytest` da mesma seleção voltou a `7
     passed`.

4. **RF03, RF04 e RF06 reconfirmados nesta rodada** (o arquivo de teste
   mudou desde a rodada 1, então nada foi assumido):
   - RF03: guarda completa neutralizada (mesma mutação de RF05, já que
     a implementação usa a mesma condição) → `test_perfil_automatizado_sem_assertion_reprova`
     continua coberto pelo mesmo bloco de mutação da rodada 1;
     comportamento inalterado.
   - RF04: linha 309, `!=` trocado por `==` → `test_perfil_divergente_sem_justificativa_reprova`
     FALHOU; revertido → voltou a passar.
   - RF06: duas mutações — guarda `assertion_idx is None or
     perfil_usado_idx is None` (linha 290) neutralizada → `test_sem_colunas_novas_nao_reprova_retroativamente`
     FALHOU (`TypeError`, por ausência de curto-circuito, mas é falha
     de qualquer forma); guarda `perfil_esperado_idx is None` (linha
     278) neutralizada → `test_criterios_sem_coluna_perfil_esperado_nao_reprova`
     FALHOU (`TypeError`). Ambas revertidas → voltaram a passar.

5. **Duas cópias do kit sincronizadas:** `_framework/scripts/validate_state.py`
   e `_framework/skills/doc-traceability-framework/scripts/validate_state.py`
   idênticas (`render_prompts.py --check` reporta "sincronizado" para
   ambas, critério #10).

6. **Checagem mecânica de fechamento (passo 5 do procedimento) —
   achado bloqueante novo.** Ao mudar `status` para `implemented` no
   front-matter e no registry (ainda em cópia de trabalho, revertido em
   seguida) e rodar
   `python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0036.md`,
   o comando saiu com **exit 1** e 16 problemas, todos do tipo:

   ```
   SDD-DTF-0036: critério #2 com 'Perfil usado' ('manual') divergente do
   'Perfil esperado' ('ao menos 2 ocorrências') sem justificativa entre
   parênteses (STRAT-DTF-0003 item 7/E5).
   ```

   Investigação (chamando `table_with_header` diretamente sobre a seção
   "Critérios de aceite" desta SDD): as linhas de critério **#2** e
   **#7** contêm, na célula "Comando de verificação", um `grep` com
   alternância regex escrita como `\|` (ex.: `grep -n "Assertion
   (file:line)\|Perfil usado" ...`). O parser de tabela usado por
   `validate_state.py` (`table_with_header`) faz um split ingênuo por
   `|` linha a linha, sem tratar `\|` como pipe escapado — o `|` do
   meio do comando é interpretado como delimitador de coluna real,
   quebrando a célula em duas e deslocando todas as colunas
   subsequentes daquela linha. Confirmado com uma chamada direta:

   ```python
   header, rows = table_with_header(criteria)
   # linha do critério #2, 6 células em vez de 5:
   # ['2', 'RF02 — colunas "Assertion (file:line)" e "Perfil usado" no template',
   #  '`grep -n "Assertion (file:line)\\', 'Perfil usado" _framework/templates/sdd.template.md`',
   #  'Ao menos 2 ocorrências', 'manual']
   ```

   Como resultado, `esperado_por_criterio["2"]` (e `["7"]`) captura o
   texto de "Resultado esperado" (`"ao menos 2 ocorrências"` /
   `">= 2"`) em vez de `"manual"` — e toda linha de evidência associada
   ao critério #2 ou #7 é comparada contra esse valor errado, gerando
   falso "Perfil usado divergente" (RF04) para qualquer perfil real
   (`manual`, `automatizado`, `n/a`, e até valores de outras colunas
   como `"Sim"` quando a linha de evidência também tem células
   deslocadas pelo mesmo motivo).

   **Isto nunca apareceu nas rodadas anteriores** porque
   `check_evidence_profile` só é chamado por `check_sdd` quando
   `status == "implemented"` — com a SDD em `approved`, o gate fica
   dormente e o defeito de parsing não tem como aparecer. É a primeira
   vez que alguém tenta de fato fechar esta SDD.

   **Isto não é um defeito da implementação de `check_evidence_profile`
   em si** (RF03-RF06 seguem corretos e com sensor confirmado — ver
   itens 1-4 acima) — é um defeito de robustez do parser de tabela
   compartilhado (`table_with_header`, usado também por `check_evidence`
   e outras checagens) diante de células com `|` literal/escapado, e um
   problema de formatação nas duas linhas específicas da própria SDD
   (critérios #2 e #7 usam grep com alternância sem reformular a
   célula para evitar `|` cru).

   Revertido antes de qualquer commit: `status` de volta para
   `approved` na SDD e no registry, `registry.md` regenerado, e
   `validate_state.py docs/sdd/SDD-DTF-0036.md` rodado de novo — volta
   a `exit 0` (o gate fica dormente outra vez com `status: approved`).

**Veredito final: FAIL.** Achado diferente do da rodada 1 (aquele foi
corrigido com sucesso). `status` mantido em `approved` — não avança
para `implemented` enquanto este defeito não for resolvido.

## Descompasso encontrado nesta rodada (bloqueante)

**Células de tabela com `|` cru/escapado quebram `table_with_header`
quando o gate está ativo.** Dois caminhos possíveis, decisão do
humano:

1. Reformular as células de "Comando de verificação" dos critérios #2
   e #7 (e revisar outras SDDs/templates que usem o mesmo padrão de
   `grep -n "A\|B"` dentro de tabela) para evitar `|` cru na célula —
   por exemplo, citar o padrão sem o operador de alternância na
   tabela (só na explicação em prosa), ou usar duas buscas separadas
   por vírgula/`;` no comando, ou envolver a célula inteira em um jeito
   que o parser reconheça como uma unidade (o parser atual não suporta
   nenhuma forma de escaping de `|` dentro de célula, então a única
   correção sem tocar no parser é evitar `|` cru na célula).
2. Corrigir `table_with_header` (`_framework/scripts/validate_state.py`,
   replicado em `_framework/skills/doc-traceability-framework/scripts/validate_state.py`)
   para tratar `\|` como pipe literal escapado antes de fazer o split
   — mudança de escopo maior, pois a função é compartilhada por outras
   checagens (`check_evidence`, `check_verification_rounds`, etc.) e
   afetaria todo o parsing de tabelas do framework; exigiria SDD
   própria (mudança de comportamento em componente já `implemented`
   noutras SDDs).

Não escolhi nenhum caminho nem editei tabela ou parser — a escolha é
do humano, conforme `verify-sdd.md` seção 4.

## Lições desta rodada

- Red flag reaproveitável: um gate que só é exercido quando
  `status == "implemented"` pode esconder defeitos de parsing por
  todo o tempo em que a SDD está em `approved` — a primeira tentativa
  real de fechamento é a primeira vez que o código é de fato testado
  contra o conteúdo real do documento. Vale considerar rodar
  `check_evidence_profile` (e checagens equivalentes) também em modo
  "dry run" sobre SDDs `approved`, como aviso, antes da tentativa de
  fechamento — não bloqueante, mas visível antes da rodada de
  verificação.
- Tabelas markdown com células que citam comandos de shell contendo
  `|` (grep com alternância é o caso mais comum neste projeto) são um
  ponto cego estrutural para qualquer parser de tabela que faça split
  ingênuo por `|` sem reconhecer escaping — vale um grep preventivo por
  `\|` dentro de células de tabela em SDDs antes de tentar fechar
  qualquer uma.

---

## Rodada 1

- **Veredito:** FAIL
- **Diff verificado:** `bc88c9419bc51d44c02bdae1fead031bd877e12f..HEAD` (merge-base capturado com `git merge-base HEAD origin/main`, branch `sdd/SDD-DTF-0036`)
- **Verificador independente:** sim (sessão separada da que implementou; histórico da sessão de implementação não foi lido)

## Conformidade com a spec (as duas direções)

Arquivos tocados pelo diff (`git diff --stat <merge-base>..HEAD`):

- `_framework/templates/sdd.template.md` — RF01, RF02
- `_framework/scripts/validate_state.py` — RF03-RF06 (`check_evidence_profile`)
- `_framework/skills/doc-traceability-framework/scripts/validate_state.py` — cópia bundlada, idêntica byte a byte à de `_framework/scripts/` (`diff` sem saída)
- `_framework/scripts/tests/test_validate_state.py` — testes de regressão (task 3)
- `_framework/procedures/verify-sdd.md` — RF07
- `docs/sdd/SDD-DTF-0036.md`, `docs/sdd/registry.yaml`, `docs/sdd/registry.md` — a própria SDD e seu registro

Todos os arquivos do diff aparecem na lista "Arquivos tocados" da SDD ou
são os artefatos esperados de registro/self-doc. Nenhum arquivo fora de
escopo, nenhum refactor sem requisito correspondente. RF01-RF07 têm
trecho de código/documento correspondente identificável.

## Evidência (comandos rodados nesta sessão)

| # | Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF01 | `grep -n "Perfil esperado" _framework/templates/sdd.template.md` | 3 ocorrências | sem teste automatizado | Sim |
| 2 | RF02 | `grep -n -e "Assertion (file:line)" -e "Perfil usado" _framework/templates/sdd.template.md` | 3 ocorrências | sem teste automatizado | Sim |
| 3 | RF03 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k "perfil or colunas_novas" -v` | 7 passed | mutação (neutralizar `esperado == "automatizado"` em `check_evidence_profile`, linha 301): `test_perfil_automatizado_sem_assertion_reprova` **falhou**; revertido (cópia de backup) → voltou a passar | Sim |
| 4 | RF04 | (mesmo comando) | inclui `test_perfil_divergente_sem_justificativa_reprova` | mutação (inverter `!=` para `==` na comparação de divergência, linha 309): teste **falhou**; revertido → voltou a passar | Sim |
| 5 | RF05 | (mesmo comando) | inclui `test_perfil_manual_nao_exige_assertion` | mutação (remover a guarda `esperado == "automatizado"`, aplicando a exigência de Assertion a todo perfil, linha 301): `test_perfil_manual_nao_exige_assertion` **NÃO falhou**. Rodei a suíte inteira com a mesma mutação (`pytest _framework/ -q`) — o único teste que quebrou foi `test_kit_parity.py` (porque só editei uma das cópias), nenhum teste de `test_validate_state.py` capturou a regressão. Confirmei em separado, chamando `check_sdd` diretamente com uma célula de Assertion **de fato vazia** (não `n/a`) e perfil `manual`: a implementação original se comporta corretamente (não reprova) — o requisito funcional RF05 está certo. O problema é só do teste empacotado: `test_perfil_manual_nao_exige_assertion` usa `n/a` (string não vazia) na célula de Assertion, então a condição `not row[assertion_idx].strip()` já é `False` com ou sem a guarda — o teste passa até com a guarda removida. **Ruído verde**, conforme a própria seção 3 do procedimento define. | **Não** |
| 6 | RF06 | (mesmo comando) | inclui `test_sem_colunas_novas_nao_reprova_retroativamente` e `test_criterios_sem_coluna_perfil_esperado_nao_reprova` | duas mutações: (a) neutralizar a guarda de colunas ausentes (linha 290) → `test_sem_colunas_novas_nao_reprova_retroativamente` falhou; revertido → voltou a passar. (b) neutralizar a guarda `perfil_esperado_idx is None` (linha 278) → `test_criterios_sem_coluna_perfil_esperado_nao_reprova` falhou; revertido → voltou a passar | Sim |
| 7 | RF07 | `grep -icE -e "file:line" -e "perfil esperado" -e "perfil usado" _framework/procedures/verify-sdd.md` | `3` (>= 2) | sem teste automatizado | Sim |
| 8 | Sem regressão nos validadores | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | ambos ✅, 0 problemas, exit 0 | checagem de integração, sem mutação nesta rodada | Sim |
| 9 | Suíte completa | `python3 -m pytest _framework/ -q` | `133 passed` | ver sensores das linhas 3-6 | Sim |
| 10 | Bundle sincronizado | `python3 _framework/scripts/render_prompts.py --check` | todos os arquivos "sincronizado"/"em dia", exit 0 | sem mutação nesta rodada | Sim |

Todas as mutações foram feitas em cópia de trabalho (`cp
_framework/scripts/validate_state.py /tmp/validate_state.py.orig` antes
de mutar, restauração por `cp` de volta — nunca `git stash` nem
commit), com limpeza de `__pycache__` entre rodadas (havia cache stale
que mascarou uma restauração na primeira tentativa da mutação de RF04;
detectado e corrigido dentro da mesma rodada, sem afetar o veredito).
Repositório restaurado ao estado original ao final: `diff
/tmp/validate_state.py.orig _framework/scripts/validate_state.py`
sem saída, `pytest _framework/ -q` → `133 passed`.

## Descompassos encontrados

**RF05 — sensor de discriminação não discrimina (bloqueante).** A SDD
exige explicitamente (seção "Instruções específicas para a IA
implementadora": "Sensor de discriminação obrigatório para RF03, RF04,
RF05 e RF06: mutar a implementação, confirmar que o teste cai,
reverter.") e o procedimento `verify-sdd.md` (seção 3) trata teste que
não cai sob mutação como não-verificação ("ruído verde"). O teste
`test_perfil_manual_nao_exige_assertion`
(`_framework/scripts/tests/test_validate_state.py:291-294`) usa `n/a`
literal na célula "Assertion (file:line)" em vez de uma célula
realmente vazia. Como resultado, ele não distingue a implementação
correta (guarda `esperado == "automatizado"` presente) de uma
implementação quebrada (guarda removida, exigindo Assertion para todo
perfil) — ambas produzem `problems == []` para esse fixture, porque
`"n/a".strip()` já é truthy independente da guarda.

Importante: **o comportamento da implementação está correto** — RF05
funciona (confirmei com célula de fato vazia + perfil manual, ver
tabela acima). O defeito é só no teste de regressão da task 3, que não
cumpre o requisito de sensor de discriminação que a própria SDD impõe
para RF05.

Nenhum outro descompasso: RF01-RF04, RF06, RF07 todos com
código/teste/documento correspondente e sensor confirmado; nenhum
arquivo fora da lista da SDD; as duas cópias do kit
(`_framework/scripts/validate_state.py` e
`_framework/skills/doc-traceability-framework/scripts/validate_state.py`)
são idênticas byte a byte.

## Caminhos possíveis (decisão do humano)

1. Corrigir `test_perfil_manual_nao_exige_assertion` (ou acrescentar um
   teste irmão) para usar uma célula de Assertion realmente vazia em
   vez de `n/a`, de modo que a mutação de remover a guarda
   `esperado == "automatizado"` derrube o teste — sem alterar o código
   de produção, que já está correto. Depois, reverificar RF05 com o
   mesmo procedimento de mutação.
2. Aceitar o risco documentado (implementação correta, teste fraco) e
   registrar a limitação explicitamente na SDD antes de avançar — não
   recomendado, porque contraria a exigência textual da própria SDD
   para RF05.

Não alterei o teste nem o código de produção — a escolha é do humano,
conforme o procedimento (`verify-sdd.md`, seção 4: "FAIL não avança
status... A escolha é dele, não sua.").

## Lições

- Red flag reaproveitável: um teste de "perfil manual/n-a aceita
  Assertion vazia" que preenche a célula com `n/a` (valor válido, não
  vazio) em vez de deixá-la de fato vazia não testa o caso que o
  requisito descreve ("aceita vazio ou `n/a`") — testa só a metade
  "aceita `n/a`", nunca a metade "aceita vazio". Ao escrever um sensor
  de discriminação para uma condição do tipo `not campo.strip()`, o
  fixture do teste "caminho feliz" precisa incluir pelo menos um caso
  com o campo realmente vazio (string vazia), não só valores
  sinalizadores como `n/a`.
