# Verificação — SDD-DTF-0036

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
| 2 | RF02 | `grep -n "Assertion (file:line)\|Perfil usado" _framework/templates/sdd.template.md` | 3 ocorrências | sem teste automatizado | Sim |
| 3 | RF03 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k "perfil or colunas_novas" -v` | 7 passed | mutação (neutralizar `esperado == "automatizado"` em `check_evidence_profile`, linha 301): `test_perfil_automatizado_sem_assertion_reprova` **falhou**; revertido (cópia de backup) → voltou a passar | Sim |
| 4 | RF04 | (mesmo comando) | inclui `test_perfil_divergente_sem_justificativa_reprova` | mutação (inverter `!=` para `==` na comparação de divergência, linha 309): teste **falhou**; revertido → voltou a passar | Sim |
| 5 | RF05 | (mesmo comando) | inclui `test_perfil_manual_nao_exige_assertion` | mutação (remover a guarda `esperado == "automatizado"`, aplicando a exigência de Assertion a todo perfil, linha 301): `test_perfil_manual_nao_exige_assertion` **NÃO falhou**. Rodei a suíte inteira com a mesma mutação (`pytest _framework/ -q`) — o único teste que quebrou foi `test_kit_parity.py` (porque só editei uma das cópias), nenhum teste de `test_validate_state.py` capturou a regressão. Confirmei em separado, chamando `check_sdd` diretamente com uma célula de Assertion **de fato vazia** (não `n/a`) e perfil `manual`: a implementação original se comporta corretamente (não reprova) — o requisito funcional RF05 está certo. O problema é só do teste empacotado: `test_perfil_manual_nao_exige_assertion` usa `n/a` (string não vazia) na célula de Assertion, então a condição `not row[assertion_idx].strip()` já é `False` com ou sem a guarda — o teste passa até com a guarda removida. **Ruído verde**, conforme a própria seção 3 do procedimento define. | **Não** |
| 6 | RF06 | (mesmo comando) | inclui `test_sem_colunas_novas_nao_reprova_retroativamente` e `test_criterios_sem_coluna_perfil_esperado_nao_reprova` | duas mutações: (a) neutralizar a guarda de colunas ausentes (linha 290) → `test_sem_colunas_novas_nao_reprova_retroativamente` falhou; revertido → voltou a passar. (b) neutralizar a guarda `perfil_esperado_idx is None` (linha 278) → `test_criterios_sem_coluna_perfil_esperado_nao_reprova` falhou; revertido → voltou a passar | Sim |
| 7 | RF07 | `grep -icE "file:line\|perfil (esperado\|usado)" _framework/procedures/verify-sdd.md` | `3` (>= 2) | sem teste automatizado | Sim |
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
