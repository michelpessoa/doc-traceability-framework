# Verificação — SDD-DTF-0050

- **Veredito:** PASS
- **Diff verificado:** `524fa59..9c8dc23` no kit (PR #134 e PR #135); espelho no central em `a6d00a5` (PR #155 e PR #156)
- **Rodada:** 2
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing small, `source_docs: []`) | SDD lida inteira; RF01 a RF05 têm código e teste correspondentes | n/a | Sim |
| A01 | `check_renderings.py` filtrado por "tipo legado", ANTES em `524fa59`, DEPOIS em `9c8dc23` | ANTES `2`; DEPOIS `0` | n/a (medição; coberto por A03) | Sim |
| A02 | `grep -c` de `PRD+TS` e `TS-X` no Cursor | ANTES `2` e `1`; DEPOIS `0` e `0` | n/a (medição; coberto por A03) | Sim |
| A03 | `pytest _framework/tests/test_prompts_sem_prd_ts.py -v` | DEPOIS 3 passed; ANTES (teste sobre gerados de 524fa59): `test_gerados_sem_prd_ts` FAILED em `doc-framework.mdc:43`, `:44`, `:84` | A04, A09 e mutações do detector | Sim |
| A04 | ` PRD+TS` acrescentado à linha 5 do mdc em cópia; pytest | 1 failed com `doc-framework.mdc:5`; restaurado 3 passed | Derrubada. Detector: sem isenção de legado 2 failed; sem `TS-X` 1 failed; sem variante `PRD + TS` 1 failed; isenção total 1 failed; âncora vazia 1 failed; sem `PRD+TS` 1 failed. Nenhuma sobrevive | Sim |
| A05 | `render_prompts.py && render_prompts.py --check; echo exit=$?; cmp` | `exit=0`, sem "divergente", `cmp` sem saída | n/a (medição) | Sim |
| A06 | pytest das duas suítes; `ruff format --check` | 295 passed; 33 files already formatted; `exit=0` | sem sensor próprio (suíte inteira) | Sim |
| A07 | `git diff --name-status 524fa59 9c8dc23` | 8 arquivos, todos previstos; `render_prompts.py` com uma linha e três trocas; YAML com diff 0 | n/a (medição) | Sim |
| A08 | `cmp` dos 6 arquivos kit x central (`a6d00a5`); `--check` no central | 6 `igual ...`; `exit=0`; teste no central 3 passed; suíte 295 passed | n/a (medição) | Sim |
| A09 | `pytest -k gerados_cobrem`; mutações da tupla `GERADOS` | 1 passed; sem Copilot 1 failed; sem universal 1 failed; (extra) sem Cursor 1 failed; restaurado 3 passed | As duas mutações da rodada 1 agora são derrubadas | Sim |

## Descompassos encontrados

Nenhum requisito sem código, nenhum arquivo do diff fora da SDD e nenhum código sem requisito. Observações que não violam critério:

1. Os arquivos de A07 incluem `docs/sdd/INDEX.md`, regenerado por `render_indexes.py`; a SDD o prevê em "os gerados de `docs/sdd/`".
2. `test_gerados_cobrem_os_tres_prompts` compara o conjunto de nomes; `GERADOS` poderia apontar um `doc-framework.mdc` de outro diretório e o teste passaria (mutação de caminho, fora do que A09 pede; não testada).
3. `render_prompts.py --check` e `render_indexes.py` emitem o aviso pré-existente de 30 SDDs sem seção de arquivos; não é desta mudança.
4. O checkout do central estava 2 commits atrás de `origin/main`; a verificação usou worktree de `origin/main`.

## Lições

- Red flag: teste que verifica "todos os prompts" a partir de uma lista precisa afirmar a composição da lista; sem isso, encolhê-la é mutação sobrevivente (rodada 1).
- Red flag: linha de isenção (`legado`) num detector precisa de teste com a linha isenta e a não isenta, e a mutação "isenção total" precisa ser derrubada.
