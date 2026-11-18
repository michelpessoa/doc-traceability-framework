# Verificação — SDD-DTF-0056

- **Veredito:** PASS
- **Causa:** null
- **Diff verificado:** `0ba638a..62a0faf` no kit (branch `sdd/SDD-DTF-0056-registry-md-todos-os-tipos`, PR #147; `0ba638a` = `origin/main`, merge da #145); espelho no central em `3fe0863` (branch `claude/laughing-galileo-d9nymc`), comparado com `origin/main` = `4e6d37b` (merge da #203)
- **Rodada:** 3 (a rodada 1 reprovou e a rodada 2 aprovou, ambas sobre heads da branch antiga, antes do rebase e da renumeração; ver "Rodadas 1 e 2" abaixo)
- **Verificador independente:** sim (sessão separada da que implementou e das que verificaram as rodadas 1 e 2)

A tabela abaixo é só da rodada 3. As linhas das três rodadas estão na seção
"Evidência de verificação" da SDD.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing small, `source_docs: []`) | SDD lida inteira; RF01, RF02, RF03, RF04, RF05 e RF06 têm código e teste correspondentes | n/a | Sim |
| A01 (RF01, RF02, RF03, RF04, RF05, RF06) | `pytest _framework/scripts/tests/test_generate_registry_md.py -q`, ANTES em worktree de `0ba638a` com o teste atual copiado, DEPOIS em `62a0faf` | ANTES 9 failed, 4 passed; DEPOIS 13 passed | A02, A03 e quatro mutações extras | Sim |
| A02 (RF03, RF05) | Linha `order += sorted(t for t in by_type if t not in order)` removida, em worktree descartável de `62a0faf` | 2 failed (tipo não declarado, soma das linhas); restaurado 13 passed | Derrubada | Sim |
| A03 (RF01, RF02, RF04) | `type_order` trocada por `return [t for t in TYPE_ORDER if t != "SPEC"]`, mesmo worktree | 4 failed (ordem do YAML, ordem embutida, rótulos, ordem diferente da embutida); restaurado 13 passed | Derrubada | Sim |
| Extra (RF01) | `type_order` fixa em `return list(TYPE_ORDER)` | 1 failed (`test_ordem_segue_o_yaml_mesmo_diferente_da_embutida`); restaurado 13 passed | Derrubada | Sim |
| Extra (RF01) | `rules = {}` fixo em `render_registry` | 1 failed (`test_ordem_segue_o_yaml_mesmo_diferente_da_embutida`); restaurado 13 passed | Derrubada | Sim |
| Extra (RF02) | `type_order` sem `or list(TYPE_ORDER)` | 1 failed (`test_type_order_sem_yaml_usa_ordem_embutida`); restaurado 13 passed | Derrubada | Sim |
| Extra (RF04) | `type_label` sem o `name` do YAML | 1 failed (`test_rotulo_cai_no_name_do_yaml_sem_rotulo_curto`); restaurado 13 passed | Derrubada | Sim |
| A04 | `render_prompts.py --check; echo exit=$?; cmp` script x cópia da skill; `generate_registry_md.py docs/sdd --check` | `_framework/INDEX.md: em dia`; `docs/sdd/INDEX.md: em dia`; `exit=0`; `cmp` sem saída; `docs/sdd/registry.md: em dia` | n/a (medição) | Sim |
| A05 | pytest das duas suítes; `ruff check`; `ruff format --check`; `mypy _framework/scripts` | 442 passed; All checks passed; 40 files already formatted; Success: no issues found in 40 source files | sem sensor próprio (suíte inteira) | Sim |
| A06 | `git diff --name-status origin/main` (= `0ba638a`); `workflow-rules.yaml`; entradas 0055 e 0056 no `registry.yaml`; interseção com os arquivos da #145 | 9 arquivos: os 4 das tasks 1 a 3, a SDD, os 3 gerados de `docs/sdd/` e este relatório; `workflow-rules.yaml` intocado, `framework.version` 2.6.0 nos dois lados; uma SDD-DTF-0055 (a da #145, intocada) e uma SDD-DTF-0056; interseção com a #145 só nos 4 gerados | n/a (medição) | Sim |
| A07 (RF06 no central) | No central: `cmp` do script, da cópia da skill, do teste e de `_framework/INDEX.md` contra `git show 62a0faf:<arquivo>`; `generate_registry_md.py docs/DTF --check`; `grep -c` de SPEC; `framework_check.py --auto`; `git diff --name-only origin/main` | 4 `igual ...`; `em dia`; 30 = 30 SPECs no registry.yaml; seções 3 + 10 + 9 + 30 = 52 = total; `exit=0`; diff só com os 5 arquivos da task 4; teste espelhado 13 passed | n/a (medição; teste espelhado idêntico, coberto por A02/A03) | Sim |

## Rodadas 1 e 2 (histórico, em texto)

Rodada 2, sobre `012ff47..61ce3eb` no kit e `679876b` no central: veredito
PASS. A01 9 failed antes e 13 passed depois; A02 2 failed; A03 4 failed; as
quatro mutações extras derrubadas; A04 exit 0; A05 393 passed; A06 9 arquivos;
A07 em dia, 29 = 29. Apontou o pipe cru na linha A07 dos critérios, que
bloqueava o `validate_state.py`; o owner o escapou depois (ajuste
pós-aprovação). Esses heads deixaram de valer com o rebase sobre `0ba638a` e a
renumeração para SDD-DTF-0056.

Rodada 1, sobre `012ff47..a620b1c` no kit e `e41dc71` no central: veredito
FAIL, causa `implementacao`. O A04 reprovou porque `render_prompts.py
--check` saiu `exit=1` com `docs/sdd/INDEX.md: divergente do gerado`: a edição
pós-aprovação da task 3 acrescentou `_framework/INDEX.md` à "Decomposição em
tasks", e a coluna "Arquivos de código" do índice vem dessa tabela. Os demais
critérios passaram (A01 8 failed antes e 12 passed depois; A02 2 failed; A03
3 failed; A05 392 passed; A06 8 arquivos; A07 em dia, 29 = 29). Também foram
apontados `central:_framework/INDEX.md` fora da task 4 (não bloqueante) e duas
mutações sobreviventes: `type_order` fixa em `list(TYPE_ORDER)` e `rules = {}`
em `render_registry`. A linha reprovada fica só aqui e na tabela da SDD,
porque `ci_gate_verify_sdd.py` (RF04) recusa, neste relatório, qualquer linha
de tabela que não seja PASS, inclusive de rodada antiga.

O que mudou entre a rodada 2 e a 3 (conferido nesta sessão, `git diff 61ce3eb 62a0faf` e `git log 0ba638a..62a0faf`):

- Rebase sobre `0ba638a` (merge da #145, framework 2.6.0) e renumeração de
  SDD-DTF-0055 para SDD-DTF-0056 em arquivo, registry, índices e mensagens de
  commit (todos com `Refs: SDD-DTF-0056`).
- Código, cópia da skill e teste: só o id citado em comentário mudou (uma
  linha em cada). A lógica é a mesma das rodadas 1 e 2.
- `62a0faf`: a frase sobre `framework.version` deixou de citar `2.5.0`
  (ajuste pós-aprovação registrado na Rastreabilidade).
- Central `3fe0863` sobre `4e6d37b`: espelho refeito para o kit atual.

## Descompassos encontrados

Nenhum na rodada 3.

Observações que não violam critério:

1. **A #145 está intocada.** `docs/sdd/SDD-DTF-0055.md` e
   `docs/sdd/validation-SDD-DTF-0055.md` não aparecem no diff. Os quatro
   arquivos que a branch e a #145 compartilham são gerados (`_framework/INDEX.md`,
   `docs/sdd/INDEX.md`, `docs/sdd/registry.md`, `docs/sdd/registry.yaml`), e o
   diff só acrescenta a linha da SDD-DTF-0056, ajusta as contagens e a faixa
   de tamanho do teste; nenhuma linha da SDD-DTF-0055 é removida ou alterada.
2. **A06 e este relatório.** Como na rodada 2, o nono arquivo do diff é este
   relatório, exigido pelo `ci_gate_verify_sdd.py` (RF02). Tratado como
   previsto.
3. **Status já `implemented` antes desta rodada.** O commit `1046fd7` mudou o
   status com base na rodada 2, feita sobre heads que não valem mais. Esta
   rodada o sustenta para `62a0faf`; não alterei status nem gerados.
4. Pré-existente e fora desta mudança: o aviso de 30 SDDs sem seção de
   arquivos do `render_prompts.py --check`.
5. A função auxiliar `_declared_types(rules)` segue sem nome na SDD, como nas
   rodadas anteriores: é a união das duas chaves descrita em `type_order` e
   `type_label`, sem comportamento extra.

## Próximo passo (owner)

PASS na rodada 3 sustenta o `implemented` já gravado na SDD e em
`docs/sdd/registry.yaml`. `validate_state.py docs/sdd/SDD-DTF-0056.md` sai 0
com esta evidência. Commit e push desta atualização ficam com quem despachou a
verificação.

## Lições

- Red flag (rodada 1): editar a "Decomposição em tasks" de uma SDD já gerada
  no índice sem rodar `render_prompts.py --check` de novo. A coluna "Arquivos
  de código" do `docs/sdd/INDEX.md` vem dessa tabela, então mudar o escopo da
  SDD é mudar um gerado.
- Red flag (rodada 1): um teste que compara a ordem embutida com o YAML por
  `sorted(...)` não discrimina "ordem derivada do YAML" de "ordem fixa no
  código" enquanto as duas coincidirem. Para provar a origem da ordem, use
  regras sintéticas numa ordem que a constante não tem. A rodada 2 confirma:
  com esse teste, as duas mutações caem.
- Red flag (rodada 2): critério de escopo do tipo "só os arquivos previstos"
  que não lista o `validation-SDD-*.md`. O relatório entra no PR por exigência
  do gate de CI, e o verificador precisa decidir se ele conta; melhor deixá-lo
  escrito no critério.
- Red flag (rodada 3): dois ramos que reservam o mesmo próximo id de SDD em
  paralelo. A colisão só aparece no merge do primeiro, e o segundo precisa
  renumerar e rebasear, o que invalida todas as rodadas de verificação feitas
  sobre os heads antigos. Confira o `registry.yaml` de `origin/main` ao
  reservar o id e de novo antes de pedir a verificação.
