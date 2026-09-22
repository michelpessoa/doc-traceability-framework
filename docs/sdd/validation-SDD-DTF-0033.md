# Verificação — SDD-DTF-0033

- **Veredito:** PASS
- **Diff verificado:** `9e789fd..fe6ce57` (commit único `fe6ce57`, mergeado via PR #101 / merge commit `df8cb5a`)
- **Verificador independente:** sim (sessão separada da que implementou; histórico de sessão de implementação não foi lido)

## Conformidade com a spec (as duas direções)

Arquivos tocados pelo diff (`git diff 9e789fd..fe6ce57 --name-only`):

- `_framework/procedures/verify-sdd.md` — tasks 1, 2, 3 (RF01, RF02, RF03, RF04, RF05, RF06)
- `_framework/scripts/validate_state.py` — task 4 (RF07)
- `_framework/skills/doc-traceability-framework/scripts/validate_state.py` — task 5 (RF08)
- `_framework/scripts/tests/test_validate_state.py` — task 6 (RF07), **caminho diferente do citado na tabela "Decomposição em tasks"/"Critérios de aceite" da SDD** (que diz `_framework/tests/test_validate_state.py`)
- `_framework/tests/test_kit_parity.py` — task 6 (RF08), estendido em vez de duplicado (instrução específica da SDD seguida corretamente)

Todos os 5 arquivos do diff aparecem na SDD (nenhum scope creep, nenhum
arquivo fora da lista). RF01-RF08 têm código/texto correspondente
identificável — nenhum requisito consolidado ficou sem implementação.
Nenhuma abstração, flag ou refactor sem requisito (task 7 confirmou
`.claude/agents/sdd-verifier.md` sem necessidade de mudança, conforme
esperado pela própria SDD).

**Único descompasso:** a SDD e a SPEC-DTF-0012 de origem citam o
caminho `_framework/tests/test_validate_state.py` nos comandos de
verificação dos critérios #5-#10 e na tabela "Decomposição em tasks"
(task 6). Esse arquivo não existe nesse caminho — os testes de
`validate_state.py` sempre viveram em
`_framework/scripts/tests/test_validate_state.py` (mesmo diretório do
script, padrão já estabelecido antes desta SDD). O comando literal da
SDD falha com `ERROR: file or directory not found`. A implementação
usou o caminho correto e já existente, não o da SDD — ou seja, o
código está certo e o texto da SDD/SPEC está com o path errado.

## Evidência (comandos rodados nesta sessão)

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| RF01/RF02 | `grep -n "Autoridade de despacho\|merge-base" _framework/procedures/verify-sdd.md` | linhas 19, 24, 25, 30 presentes | n/a (checagem estática) | Sim |
| RF03 | `grep -n "Rodada" _framework/procedures/verify-sdd.md` | linhas 92, 97, 104 presentes | n/a (checagem estática) | Sim |
| RF04/RF05 | `grep -n "Escalonado ao humano\|3 rodadas\|3ª rodada" _framework/procedures/verify-sdd.md` | linhas 98, 103 presentes | n/a (checagem estática) | Sim |
| RF06 | `grep -n "despachou a própria verificação\|fatia de task paralela" _framework/procedures/verify-sdd.md` | linhas 170, 171 presentes | n/a (checagem estática) | Sim |
| RF07 (reprova 3 rodadas sem escalonamento) | `python3 -m pytest _framework/scripts/tests/test_validate_state.py::test_tres_rodadas_sem_escalonamento_reprova -v` | `1 passed in 0.13s` | mutação `>= 3` → `> 3` em `check_verification_rounds`: teste **falhou** (`assert False`) com a mutação; restaurado via cópia de backup (`cp /tmp/validate_state.py.bak ...`); voltou a passar | Sim |
| RF07 (com escalonamento passa) | `python3 -m pytest _framework/scripts/tests/test_validate_state.py::test_tres_rodadas_com_escalonamento_passa -v` | `1 passed in 0.16s` | cobertura indireta pelo mesmo sensor de mutação acima (função única) | Sim |
| RF07 (2 rodadas, abaixo do teto) | `python3 -m pytest _framework/scripts/tests/test_validate_state.py::test_duas_rodadas_sem_escalonamento_passa -v` | `1 passed in 0.15s` | idem | Sim |
| RF07 (sem coluna Rodada) | `python3 -m pytest _framework/scripts/tests/test_validate_state.py::test_tabela_sem_coluna_rodada_trata_como_unica -v` | `1 passed in 0.13s` | idem | Sim |
| RF08 (paridade) | `python3 -m pytest _framework/tests/test_kit_parity.py::test_validate_state_paridade -v` | `1 passed in 0.01s` | mutação: `echo "# tmp" >>` no arquivo bundlado: teste **falhou** (`AssertionError`); restaurado com `git checkout --`; voltou a passar | Sim |
| Regressão gate 16 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | `18 passed in 0.82s` | ver sensores acima | Sim |
| `.claude/agents/sdd-verifier.md` consistente | `grep -n "verify-sdd.md" .claude/agents/sdd-verifier.md` | linha 6 presente | n/a (checagem estática) | Sim |
| Diretório limpo pós-sensores | `git status --short` | só `HANDOFF.md` (untracked, não relacionado) | n/a | Sim |

## Descompassos encontrados

Um descompasso, não bloqueante: caminho `_framework/tests/test_validate_state.py`
citado na SDD (tabela "Decomposição em tasks" e comandos dos critérios
#5-#10) não corresponde ao caminho real
(`_framework/scripts/tests/test_validate_state.py`), que já era o
padrão do repositório antes desta SDD. A implementação seguiu o padrão
correto; é a redação da SDD/SPEC-DTF-0012 que tem o path errado.
Recomenda-se corrigir o texto da SDD (e, se a SPEC-DTF-0012 ainda não
tiver sido consumida por outra SDD, o texto da SPEC também) numa
próxima revisão — não justifica manter `approved` porque o requisito
funcional (RF07/RF08) está de fato implementado e testado, só o
comando documentado usa o caminho errado.

Nenhum outro descompasso: todo RF01-RF08 tem código correspondente,
nenhum arquivo fora da lista da SDD, nenhuma task sem RF de origem.

## Lições

- Red flag reaproveitável: **comando de verificação com caminho que
  nunca existiu no repositório não foi rodado antes de entrar na
  SDD/SPEC** — quem redige critérios de aceite deveria rodar o comando
  ao menos uma vez (mesmo que a implementação ainda não exista, dá para
  confirmar o caminho do arquivo de teste alvo) antes de fixá-lo como
  critério. Aqui não teve efeito prático porque o verificador rodou o
  comando, viu o erro de caminho, e buscou o caminho real — mas em um
  gate mais automatizado (CI rodando o comando literal da SDD) isso
  teria reprovado por motivo errado.
