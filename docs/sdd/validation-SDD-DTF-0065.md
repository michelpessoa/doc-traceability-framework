# Verificação — SDD-DTF-0065

- **Veredito:** PASS
- **Diff verificado:** `10e6d6a..e53603c` no kit (`10e6d6a` = `git merge-base HEAD origin/main`, SHA fixo, igual a `origin/main` no momento da verificação; o intervalo contém a SDD em `in_review` em `5a6202a`, o status `approved` em `e6dced9`, a emenda em `1297594` e a implementação em `fe38d08`, `a085132`, `ad128a5` e `e53603c`, todos com `Refs: SDD-DTF-0065`)
- **Rodada:** 1
- **Verificador independente:** sim (subagente separado; não implementou e não leu o relatório nem o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão, com `PYTHONDONTWRITEBYTECODE=1` nos sensores. Sensores e `selftest.py` em cópias descartáveis feitas com `git archive` em subpastas de um diretório próprio do scratchpad (`verify-0065/`: `antes` de `fe38d08`; `head`, `m1` a `m6` e `st-head` de `e53603c`; `semclaude` de `e53603c` só com `_framework/` e `AGENTS.md`; `st-base` de `10e6d6a`), sem `git stash` e sem commit na worktree. `git status --short` do kit ficou vazio antes da edição da SDD. O central foi só lido.

Aprovações conferidas pela API (`gh api repos/michelpessoa/doc-traceability-framework/pulls/161/reviews`): review `6066031431`, de `michelpessoa` (owner), `COMMENTED` com corpo `Aprovado`, sobre `5a6202a`; review `6066076150`, do mesmo login, `COMMENTED` com corpo `Aprovado`, sobre `1297594`. Entre `5a6202a` e `e6dced9` só mudou `status`; entre `e6dced9` e `1297594`, só a emenda. `git diff 1297594 HEAD -- docs/sdd/SDD-DTF-0065.md` é vazio (antes da edição da evidência).

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0065.md /home/user/doc-traceability-central/docs/DTF`; `git diff 1297594 HEAD -- docs/sdd/SDD-DTF-0065.md`; reviews da PR #161 | `✅ source_docs ... conferem`, `exit=0`; `source_docs: []`, sizing `small`; corpo sem mudança desde `1297594`; as duas reviews `Aprovado` do owner nos SHAs certos | sem teste automatizado (leitura) | Sim |
| A01 | comando literal da SDD, em `e53603c` e em cópia de `fe38d08` | `29 passed`; em `fe38d08` (antes da task 2): `1 failed, 28 passed` (`test_sdd0065_item_de_checks_da_regra_sdd_com_yaml_real`) | laço do RF01 desligado: `1 failed, 8 passed` | Sim |
| A02 | as duas mutações de `check_renderings.py` do RF06, uma por cópia; pytest de `test_check_renderings_unknown.py` | `pass`: `1 failed` (`..._reprova_status_inexistente_na_copia`, `assert 0 == 1`); `set(types)`: `1 failed` (`..._aceita_tipos_legados_na_copia`, `assert 1 == 0`, `PRD` e `TS` inexistentes); restaurado: `29 passed` | cópia sem edição: `exit=0`; sem `.claude/`: `exit=1`; mensagem trocada: `1 failed` no `in`; código de saída 2: `1 failed` (`assert 2 == 1`) | Sim |
| A03 | `(?!\w)` final de `ID_PREFIX` removido, em cópia; pytest | `1 failed, 19 passed` (`test_sdd0064_negativo_sequencia_que_nao_e_id_nao_acusa`); restaurado: `29 passed` | `_check("XYZ-EVM-Xy")` acusa `XYZ`, `_check("ADR-EVM-Xy")` não: o caso novo discrimina sozinho | Sim |
| A04 | laço `grep -qF` da SDD nos cinco gerados | nenhum `falta`; `grep -c` = `1` em cada | mutação do laço morre (A01) | Sim |
| A05 | leitura lado a lado do diff de `AGENTS.md` e de `approval_policy` em `workflow-rules.yaml` | um único item, o da regra SDD (`:1709`), com os quatro checks na ordem do YAML; nenhum item para as duas regras sem `checks` | sem teste automatizado (leitura) | Sim |
| A06 | `selftest.py` em cópia de `e53603c` e em cópia de `10e6d6a` | `16 mutação(ões): todos os mutantes morreram.` `exit=0`; base: `13` | as três mutações novas, aplicadas à mão, matam testes de comportamento | Sim |
| A07 | comando literal da SDD, com `origin/main` = merge-base | `--check` `exit=0`; `check_renderings.py` `exit=0`; `560 passed`; ruff, format e mypy sem erro; `framework_check --auto` `exit=0`; diff com 14 arquivos, todos previstos | sem mutação própria | Sim |
| A08 | `cmp` dos arquivos da task 5, central (`7c00806`) contra o kit; `grep -c "Checks de SDD (policy)" AGENTS.md` no central | os dois `render_prompts.py`, os dois testes, `mutations.yaml` e `AGENTS.md` diferem; `grep -c` = `0` | sem teste automatizado nesta etapa (espelho pós-merge) | Pendente: etapa pós-merge no kit |

## Descompassos encontrados

Requisito ↔ código: RF01 `render_prompts.py:205-210` (laço sobre as regras com `checks`, uma linha em branco antes, só se houver ao menos uma; tabela, `Sem regra que case` e frase de `approved_by` intactas); RF02 `test_check_renderings_unknown.py:184-195` (troca da primeira `→ in_review →`, que existe no `SKILL.md`; `returncode == 1` e mensagem); RF03 `:198-204`; helper da cópia `:155-181`, com `_framework/` sem `__pycache__`, `.claude/` e `AGENTS.md`, como na emenda, e guarda de que a cópia sem edição sai com 0 (`:180`); RF04 `:132`, só o texto do caso mudou; RF05 `test_render_prompts_core.py:109-129`, testes antigos intocados (o diff do arquivo só acrescenta linhas); RF06 `mutations.yaml:86-102`, cada `find` único no script. Nenhum requisito sem código.

Arquivo tocado ↔ SDD: `git diff --name-only 10e6d6a..e53603c` dá os 14 arquivos: os dois testes (task 1), `render_prompts.py` (task 2), `mutations.yaml` (task 3), seis gerados da task 4 (`AGENTS.md`, `docs/especificacao.md`, os três prompts e a cópia de `render_prompts.py` na skill) e, de `docs/sdd/`, a SDD, `INDEX.md`, `registry.md` e `registry.yaml`. Não há código sem requisito.

Achados não bloqueantes:

1. **Dois arquivos da task 4 não mudaram.** A cópia de `check_renderings.py` na skill e `_framework/INDEX.md` estão na lista, mas o script não mudou e o índice não depende do núcleo. `render_prompts.py --check` dá `sincronizado` e `em dia`. Não é lacuna.
2. **O ramo de fallback do RF02 não é exercitado.** O `SKILL.md` tem duas ocorrências de `→ in_review →`, então a linha `` `draft` → `obsolete` → `approved` `` nunca é acrescentada. Segue a SDD, e o ramo só importa se a renderização mudar.
3. **`review_approval.py` não se aplica no kit.** Rodado com as reviews da PR, dá `approvers não declarado no registry`, `exit=1`, porque o registry do kit não declara `approvers`. As duas aprovações foram conferidas pela API (login, estado `COMMENTED`, corpo `Aprovado`, `commit_id`).
4. **O `selftest.py` só imprime o total.** A morte de cada mutação nova por teste de comportamento foi conferida aplicando a troca à mão (A01, A02).
5. **A suíte regrava arquivos do kit com o mesmo conteúdo.** Depois do pytest completo, o mtime de `check_renderings.py` e de outros scripts mudou, mas `git status --short` seguiu vazio. Não afeta o resultado, mas quem rodar sensores na worktree em paralelo com a suíte pode ter a mutação sobrescrita.
6. **A08 ainda não aplicável.** O central (`7c00806`) não tem o espelho. O critério deve ser rodado por quem espelhar, depois do merge no kit.

## Lições

- **Red flag: teste de `main` numa cópia parcial do kit.** Uma cópia que não leva tudo o que o `main` confere (aqui, `.claude/`) sai com 1 sem edição, e um teste que espera 1 passa por acaso. Antes de editar a cópia, afirme que ela sem edição sai com 0.
- **Discriminar mensagem e código de saída separadamente.** Para um teste que afirma os dois, troque só a mensagem e, noutra cópia, só o código de saída: cada asserção tem de reprovar sozinha.
