# Verificação — SDD-DTF-0056

- **Veredito:** PASS
- **Causa:** null
- **Diff verificado:** `012ff47..61ce3eb` no kit (branch `sdd/SDD-DTF-0056-registry-md-todos-os-tipos`, PR #146); espelho no central em `679876b` (branch `claude/laughing-galileo-d9nymc`, PR #204), comparado com `origin/main...679876b`
- **Rodada:** 2 (a rodada 1, sobre `a620b1c`, reprovou; ver "Rodada 1" abaixo)
- **Verificador independente:** sim (sessão separada da que implementou e da que verificou a rodada 1)

A tabela abaixo é só da rodada 2. As linhas das duas rodadas estão na seção
"Evidência de verificação" da SDD.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing small, `source_docs: []`) | SDD lida inteira; RF01, RF02, RF03, RF04, RF05 e RF06 têm código e teste correspondentes | n/a | Sim |
| A01 (RF01, RF02, RF03, RF04, RF05, RF06) | `pytest _framework/scripts/tests/test_generate_registry_md.py -q`, ANTES em worktree de `012ff47` com o teste atual copiado, DEPOIS em `61ce3eb` | ANTES 9 failed, 4 passed; DEPOIS 13 passed | A02, A03 e quatro mutações extras | Sim |
| A02 (RF03, RF05) | Linha `order += sorted(t for t in by_type if t not in order)` removida, em worktree descartável | 2 failed (tipo não declarado, soma das linhas); restaurado 13 passed | Derrubada | Sim |
| A03 (RF01, RF02, RF04) | `type_order` trocada por `return [t for t in TYPE_ORDER if t != "SPEC"]` | 4 failed (ordem do YAML, ordem embutida, rótulos, ordem diferente da embutida); restaurado 13 passed | Derrubada | Sim |
| Extra (RF01) | `type_order` fixa em `return list(TYPE_ORDER)` | 1 failed (`test_ordem_segue_o_yaml_mesmo_diferente_da_embutida`, linha 136); restaurado 13 passed | Derrubada (sobrevivia na rodada 1) | Sim |
| Extra (RF01) | `rules = {}` fixo em `render_registry` | 1 failed (`test_ordem_segue_o_yaml_mesmo_diferente_da_embutida`, linha 140: `['SPEC', 'SDD', 'Tech Spec'] != ['SDD', 'SPEC', 'Tech Spec']`); restaurado 13 passed | Derrubada (sobrevivia na rodada 1) | Sim |
| Extra (RF02) | `type_order` sem `or list(TYPE_ORDER)` | 1 failed (`test_type_order_sem_yaml_usa_ordem_embutida`); restaurado 13 passed | Derrubada | Sim |
| Extra (RF04) | `type_label` sem o `name` do YAML | 1 failed (`test_rotulo_cai_no_name_do_yaml_sem_rotulo_curto`); restaurado 13 passed | Derrubada | Sim |
| A04 | `render_prompts.py --check; echo exit=$?; cmp` script x cópia da skill | `_framework/INDEX.md: em dia`; `docs/sdd/INDEX.md: em dia`; `exit=0`; `cmp` sem saída | n/a (medição) | Sim |
| A05 | pytest das duas suítes; `ruff check`; `ruff format --check`; `mypy _framework/scripts` | 393 passed; All checks passed; 38 files already formatted; Success: no issues found in 38 source files | sem sensor próprio (suíte inteira) | Sim |
| A06 | `git diff --name-status origin/main` (= `012ff47`) | 9 arquivos: os 4 das tasks 1 a 3, a SDD, os 3 gerados de `docs/sdd/` e este relatório; `workflow-rules.yaml` intocado, `framework.version` 2.5.0 | n/a (medição) | Sim |
| A07 (RF06 no central) | No central: `cmp` dos 3 arquivos e de `_framework/INDEX.md`; `generate_registry_md.py docs/DTF --check`; `grep -c` de SPEC; `framework_check.py --auto`; `git diff --name-status origin/main...HEAD` | 4 `igual ...`; `em dia`; 29 = 29 SPECs no registry.yaml; `exit=0`; diff só com os 5 arquivos da task 4; teste espelhado 13 passed | n/a (medição; teste espelhado coberto por A02/A03) | Sim |

## Rodada 1 (histórico, em texto)

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

O que mudou entre as rodadas (conferido nesta sessão, `git diff a620b1c..61ce3eb`):

- `517277b`: `docs/sdd/INDEX.md` regenerado; a SDD e este relatório ganharam a
  rodada 1.
- `61ce3eb`: teste `test_ordem_segue_o_yaml_mesmo_diferente_da_embutida` (RF01),
  com regras sintéticas `SDD, SPEC, TS`, que a constante não tem nessa ordem;
  task 4 da SDD ganhou `central:_framework/INDEX.md`; linha "Ajuste
  pós-aprovação" na Rastreabilidade.
- Central `679876b`: o mesmo teste espelhado (`cmp` igual ao do kit).
- Código (`generate_registry_md.py` e cópia da skill): sem mudança desde a
  rodada 1. Critérios de aceite da SDD: sem mudança desde `fa87aa5`
  (aprovação).

## Descompassos encontrados

Nenhum descompasso de implementação na rodada 2. O item 4 bloqueia o passo 5 (mudança de status) até o owner corrigir uma linha da SDD.

1. **Descompasso 1 da rodada 1 (A04): resolvido.** `render_prompts.py --check`
   sai 0 e a linha da SDD-DTF-0056 em `docs/sdd/INDEX.md` começa por
   `_framework/INDEX.md`.
2. **Descompasso 2 da rodada 1 (edição da task 3 depois da aprovação):
   resolvido por registro.** A linha "Ajuste pós-aprovação" da Rastreabilidade
   diz que o owner aceitou a edição da task 3, o acréscimo à task 4 e o teste
   novo. A "Decomposição em tasks" entra no hash de `approval_policy`, mas a
   SDD não tem `approved_by` e `validate_state.py` não o cobra
   (`docs/sdd/registry.yaml` em `framework_version: "2.3.1"`, RF08 da
   SDD-DTF-0054, não-retroativo). `validate_state.py
   docs/sdd/SDD-DTF-0056.md` sai 0. Não há hash a recalcular.
3. **Descompasso 3 da rodada 1 (central `_framework/INDEX.md` fora da task 4):
   resolvido.** A task 4 lista `central:_framework/INDEX.md`, e o diff do
   central tem exatamente os 5 arquivos da task 4.

4. **Bloqueia o passo 5, não o veredito: pipe sem escape na linha A07 dos
   "Critérios de aceite".** O comando `grep -c '^| \`SPEC-DTF-' ...` tem um `|`
   cru dentro da célula. `split_table_row` só trata o par barra-pipe como
   conteúdo, então a linha ganha uma célula a mais e o "Perfil esperado" do A07
   passa a ser lido como o "Resultado esperado". Simulado nesta sessão, num
   worktree descartável do head com esta SDD e `status: implemented`:
   `validate_state.py docs/sdd/SDD-DTF-0056.md` sai 1 com `critério #A07 com
   'Perfil usado' ('automatizado') divergente do 'Perfil esperado' ('\`cmp\`
   sem saída; ...')` (duas vezes, uma por rodada). Com o pipe escapado
   (`'^\| \`SPEC-DTF-'`) só nessa linha, sai 0. O texto renderizado não muda,
   mas a linha está na seção de critérios aprovada, então a correção fica com
   o owner antes do passo 5. As duas linhas A07 da tabela de evidência da SDD
   tinham o mesmo pipe cru e davam ainda `resultado assumido ('n/a')`; nesta
   rodada eu escapei o pipe nelas (só formatação, conteúdo igual), inclusive na
   linha da rodada 1.

Observações que não violam critério:

5. **A06 e o relatório de verificação.** O diff do kit tem 9 arquivos. O nono é
   `docs/sdd/validation-SDD-DTF-0056.md`, que o texto do A06 não lista. Ele não é
   implementação: é a saída deste procedimento (passo 4) e o
   `ci_gate_verify_sdd.py` exige que ele esteja no PR (RF02). Tratado como
   previsto. Quando o A06 de uma SDD futura for redigido, convém listar o
   `validation-SDD-*.md` junto dos gerados.
6. **As duas mutações sobreviventes da rodada 1 agora caem.** `type_order` fixa
   cai na asserção de `type_order(rules)` (`test_generate_registry_md.py:136`);
   `rules = {}` em `render_registry` cai na asserção das seções
   (`test_generate_registry_md.py:140`). As 6 mutações rodadas nesta sessão
   foram todas derrubadas.
7. O teste novo cobre a ordem com regras parciais (3 dos 10 tipos). Os demais
   tipos presentes no registry e fora dessas regras vão para "Tipo não
   declarado", o que é coerente com o RF03; não há asserção disso nesse teste,
   mas o `test_tipo_nao_declarado_ganha_secao_propria` cobre o caminho.
8. Pré-existente e fora desta mudança: o aviso de 30 SDDs sem seção de arquivos
   do `render_prompts.py --check`.
9. A função auxiliar `_declared_types(rules)` segue sem nome na SDD, como na
   rodada 1. É a união das duas chaves descrita em `type_order` e `type_label`,
   sem comportamento extra.

## Próximo passo (owner)

PASS autoriza o passo 5 do procedimento: mudar `status` para `implemented` na
SDD e em `docs/sdd/registry.yaml` depois de escapar o pipe da linha A07 dos critérios (item 4), regenerar `docs/sdd/registry.md` e os
índices por script, e rodar `validate_state.py docs/sdd/SDD-DTF-0056.md`.
Esta verificação não alterou status nem gerados.

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
