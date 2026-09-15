---
id: SDD-DTF-0025
type: SDD
title: "test_discover: fixture discrimina poda de worktrees fora de .claude/ e descida em .git"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0023]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Só a fixture de teste muda; discover() em framework_check.py não é tocado (já está correto). Branch sdd/SDD-DTF-0025-* a partir de main, PR, commits com Refs: SDD-DTF-0025."
supersedes: null
superseded_by: null
tags: [tooling, testes, discover]
---

# test_discover: fixture discrimina poda de worktrees fora de .claude/ e descida em .git

## Resumo executivo

`docs/sdd/LESSONS.md`, seção "2026-09-14 — Descompassos das verificações
independentes de SDD-DTF-0018 a 0023", item 8 ("SDD-DTF-0023 —
`test_discover.py` não pega duas mutações"), registra que a verificação
independente de `SDD-DTF-0023` confirmou `discover()`
(`_framework/scripts/framework_check.py`) correto à mão, mas achou que
`test_discover.py` não discrimina duas mutações possíveis:

1. Podar (não descer em) qualquer diretório chamado `worktrees`, em
   qualquer nível da árvore, em vez de só `root/.claude/worktrees`
   (comparação `current / d != worktrees` em `discover`). A fixture
   original (`REGISTRY_DIRS` em `test_discover.py`) só cria um
   `.claude/worktrees/a/docs/sdd`; nunca um `worktrees` em outro lugar —
   então mutar a poda de "só esse caminho exato" para "qualquer
   diretório com esse nome" não muda o resultado esperado e o teste
   continua passando.
2. Tirar `.git` de `PRUNED_DIR_NAMES`. A fixture original nunca coloca
   um `registry.yaml` dentro de `.git/`, então essa mutação também não
   muda o resultado e o teste continua passando.

O código em si (`discover`, tocado por `SDD-DTF-0023`) já está correto —
confirmado à mão na verificação independente registrada em
`docs/sdd/validation.md` (seção SDD-DTF-0023) e reconfirmado nesta SDD
pelo sensor de discriminação (tabela de evidência abaixo). Só a fixture
de teste precisa de dois casos a mais para tornar esse comportamento
mecanicamente verificável, em vez de depender de conferência manual
registrada em `LESSONS.md`.

`sizing: small` — um arquivo de teste editado (dois casos novos
adicionados), nenhum critério do gate `rfc_to_adr` se aplica
(comportamento externo do `discover()` não muda: ele já fazia a coisa
certa), e o escopo é puramente mecanização de teste — exatamente o
padrão que `lessons_policy` (seção 18 de `workflow-rules.yaml`) descreve
como lição local que ainda não vira regra global do kit (aparece em um
só projeto até agora).

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — reforço de fixture de teste, nenhum critério do gate
`rfc_to_adr` se aplica; `discover()` não é alterado.

## Requisitos consolidados

- **RF1**: `test_discover.py` ganha um caso que cria
  `docs/worktrees/registry_dir/registry.yaml` (um diretório chamado
  `worktrees` que **não** é `root/.claude/worktrees`) e afirma que ele
  **é** descoberto. Discrimina a mutação "podar `worktrees` por nome em
  qualquer nível" (item 1 do achado).
- **RF2**: `test_discover.py` ganha um caso que cria
  `.git/x/registry.yaml` e afirma que `discover()` devolve lista vazia
  para essa árvore (nunca descobre nada dentro de `.git/`). Discrimina a
  mutação "tirar `.git` de `PRUNED_DIR_NAMES`" (item 2 do achado).
- **RF3**: o caso de teste original (`REGISTRY_DIRS`) ganha a entrada
  `docs/worktrees/registry_dir` na própria fixture combinada, e a
  asserção passa a incluir esse diretório entre os descobertos — o novo
  diretório convive com `node_modules`, `_framework`,
  `.claude/worktrees` e os diretórios de documento legítimos na mesma
  árvore, sem quebrar a poda deles.

Casos de borda:
- `docs/worktrees/registry_dir` fica em ordem alfabética depois de
  `docs/sdd` na lista ordenada (`d`, `n`, `s`, `w`) — a asserção do RF3
  reflete essa ordem.
- `.git/x` nunca aparece no resultado de nenhum caso, isolado ou
  combinado.

Fora de escopo:
- Alterar `discover()`, `PRUNED_DIR_NAMES` ou qualquer outro código de
  `framework_check.py` — já está correto.
- `validate_state.py`, `table_rows`, `verify-sdd.md`, `check_hooks.py` —
  escopo de outros agentes em paralelo (SDD-DTF-0024/0026/0027).
- Qualquer outro validador ou script além de `test_discover.py`.
- Registrar nova regra em `workflow-rules.yaml` — é lição local
  (`lessons_policy`), não critério de mecanização global ainda.

## Especificação técnica consolidada

**`_framework/scripts/tests/test_discover.py`**

- `REGISTRY_DIRS` ganha duas entradas novas (comentadas com
  `# SDD-DTF-0025`):
  - `"docs/worktrees/registry_dir"` — worktrees fora de `.claude/`.
  - `".git/x"` — dentro de `.git`.
- O teste original (`test_discover_poda_node_modules_framework_e_worktrees`)
  passa a afirmar
  `found == ["docs/EVM", "docs/node_modules_notes", "docs/sdd", "docs/worktrees/registry_dir"]`
  (a entrada `.git/x` nunca aparece, por definição da poda).
- Dois testes novos, isolados (fixture própria, sem o resto de
  `REGISTRY_DIRS`), para não depender da combinação para provar a
  discriminação:
  - `test_discover_poda_worktrees_so_relativo_a_root`: cria só
    `docs/worktrees/registry_dir/registry.yaml`; afirma
    `found == ["docs/worktrees/registry_dir"]`.
  - `test_discover_nunca_desce_em_git`: cria só
    `.git/x/registry.yaml`; afirma `found == []`.

Nenhum outro arquivo é tocado.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1–RF3, suite completa do arquivo | `python3 -m pytest _framework/scripts/tests/test_discover.py -v` | 3 casos, todos passam |
| 2 | RF1 discrimina a mutação "podar worktrees em qualquer nível" | mutar `PRUNED_DIR_NAMES` para incluir `"worktrees"` em `_framework/scripts/framework_check.py`, rodar o comando do critério 1, restaurar o arquivo por cópia (nunca commitar a mutação) | com a mutação: `test_discover_poda_worktrees_so_relativo_a_root` (e o teste combinado) falham; restaurado: os 3 voltam a passar |
| 3 | RF2 discrimina a mutação "tirar .git de PRUNED_DIR_NAMES" | remover `".git"` de `PRUNED_DIR_NAMES` em `_framework/scripts/framework_check.py`, rodar o comando do critério 1, restaurar o arquivo por cópia (nunca commitar a mutação) | com a mutação: `test_discover_nunca_desce_em_git` (e o teste combinado) falham; restaurado: os 3 voltam a passar |
| 4 | Regressão | `python3 -m pytest && ruff check _framework/scripts && ruff format --check _framework/scripts` | exit 0 em todos |

## Instruções específicas para a IA implementadora

- Só editar `_framework/scripts/tests/test_discover.py`. Não tocar em
  `framework_check.py`, `validate_state.py`, `table_rows`,
  `verify-sdd.md` nem `check_hooks.py` — escopo de agentes irmãos
  (SDD-DTF-0024/0026/0027) rodando em paralelo em worktrees próprios.
- A mutação dos critérios 2 e 3 é temporária: editar
  `framework_check.py` localmente, rodar o teste, restaurar por cópia do
  git (`git checkout -- _framework/scripts/framework_check.py` ou cópia
  de backup) antes de qualquer commit. A mutação nunca aparece em nenhum
  commit desta branch.
- Branch `sdd/SDD-DTF-0025-*` a partir de `main`, PR — nunca commit
  direto (gate seção 14). Conventional Commits com `Refs: SDD-DTF-0025`.
- Conflito de merge em `docs/sdd/registry.yaml` no momento do PR é
  esperado (outros agentes mexendo na mesma lista em paralelo) —
  resolvido pelo humano depois, não pela IA implementadora.
- Verificação de escopo e evidência ficam nesta mesma SDD — sizing
  small, sem `verify-sdd` em sessão separada (mudança só de teste, sem
  requisito de produto a verificar-cross-check).

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF1–RF3 têm código e teste correspondentes (são o próprio teste).
- [x] Arquivo tocado: só `_framework/scripts/tests/test_discover.py`,
      mais esta SDD e o registry (status/evidência).
- [x] Nenhuma mudança em `discover()`, `PRUNED_DIR_NAMES` ou qualquer
      outro script.

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md` (seção
SDD-DTF-0025). Veredito: **PASS**.

**Verificador independente:** sim — subagente separado, contexto limpo,
sem ler o histórico da sessão que implementou; entrada foi esta SDD e o
diff `ae3fb0e..2c3f931` (commit de implementação `2c3f931`, PR #71).
Verificação em 2026-09-15 na branch `docs/sdd-dtf-0025-verificacao` a
partir de `a415235`. Todos os comandos abaixo foram rodados nesta sessão
de verificação; as saídas são literais.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/scripts/tests/test_discover.py -v` | `3 passed in 1.07s` — `test_discover_poda_node_modules_framework_e_worktrees PASSED`, `test_discover_poda_worktrees_so_relativo_a_root PASSED`, `test_discover_nunca_desce_em_git PASSED` (reexecutado após cada restauração de mutação: `3 passed in 0.10s` e `3 passed in 0.09s`) | n/a (execução limpa; os sensores são as linhas 2 e 3) | Sim |
| 2 | Mutação temporária `PRUNED_DIR_NAMES = {".git", "_framework", "node_modules", "worktrees"}` em `_framework/scripts/framework_check.py` (backup por `cp` no scratchpad, nunca `git stash`, nunca commitada), depois o comando do critério 1 | `2 failed, 1 passed in 1.88s` — falham `test_discover_poda_worktrees_so_relativo_a_root` (`AssertionError: assert [] == ['docs/worktrees/registry_dir']`) e `test_discover_poda_node_modules_framework_e_worktrees`; `test_discover_nunca_desce_em_git` passa (não é alvo desta mutação). Restaurado por `cp` do backup (`diff` idêntico, `git status --porcelain` vazio) → `3 passed in 0.10s` | Sim — a mutação "podar `worktrees` por nome em qualquer nível" é pega | Sim |
| 3 | Mutação temporária `PRUNED_DIR_NAMES = {"_framework", "node_modules"}` (sem `.git`) em `_framework/scripts/framework_check.py` (backup por `cp`, nunca `git stash`, nunca commitada), depois o comando do critério 1 | `2 failed, 1 passed in 0.10s` — falham `test_discover_nunca_desce_em_git` (`AssertionError: assert ['.git/x'] == []`) e `test_discover_poda_node_modules_framework_e_worktrees`; `test_discover_poda_worktrees_so_relativo_a_root` passa (não é alvo desta mutação). Restaurado por `cp` do backup (`diff` idêntico, `git status --porcelain` vazio) → `3 passed in 0.09s` | Sim — a mutação "tirar `.git` de `PRUNED_DIR_NAMES`" é pega | Sim |
| 4 | `python3 -m pytest && ruff check _framework/scripts && ruff format --check _framework/scripts` | pytest: `79 passed in 3.10s`; `All checks passed!`; `21 files already formatted`; cadeia com exit 0 | sem sensor próprio (regressão) | Sim |

Nota sobre a linha 4: a SDD foi redigida quando a suíte tinha 74 testes;
`main` em `a415235` já traz os testes de SDD-DTF-0024/0026/0027, daí
`79 passed`. O critério pede exit 0 na cadeia, satisfeito.

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0023 (mesmo teste; achado registrado em `LESSONS.md` na verificação independente de SDD-DTF-0023) |
