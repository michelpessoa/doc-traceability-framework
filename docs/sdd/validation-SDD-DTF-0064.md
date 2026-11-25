# Verificação — SDD-DTF-0064

- **Veredito:** PASS
- **Diff verificado:** `2a4c5c9..e5ac326` no kit (`2a4c5c9` = `git merge-base HEAD origin/main`, SHA fixo, igual a `origin/main` no momento da verificação, já com a SDD-DTF-0063 em main; o intervalo contém a SDD e o status, os merges de main, a aprovação sobre `57454fa` pela review do owner na PR #159, e a implementação em `2430f9a`, `f96ce4c`, `cbdbcfd` e `e5ac326`, todos com `Refs: SDD-DTF-0064`)
- **Rodada:** 1
- **Verificador independente:** sim (subagente separado; não implementou e não leu o relatório nem o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão, com `PYTHONDONTWRITEBYTECODE=1` nos sensores. Sensores e `selftest.py` em cópias descartáveis feitas com `git archive` em subpastas de um diretório próprio do scratchpad (`verify-0064/`: `antes` de `2430f9a`, `sensor` e `a03` de `e5ac326`, `st-head` de `e5ac326`, `st-base` de `2a4c5c9`), sem `git stash` e sem commit na worktree. `git status --short` do kit ficou vazio antes da edição da SDD. O central foi só lido.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0064.md /home/user/doc-traceability-central/docs/DTF`; `git diff 57454fa HEAD -- docs/sdd/SDD-DTF-0064.md` | `✅ source_docs ... conferem`, `exit=0`; `source_docs: []`, sizing `small`; desde `57454fa` só mudou `status: in_review` → `approved` | sem teste automatizado (leitura) | Sim |
| A01 | comando literal da SDD, em `e5ac326` e em cópia de `2430f9a` | `18 passed`; em `2430f9a` (antes da task 2): `1 failed, 17 passed` | `(?!\w)` removido: `1 failed` no negativo (`XYZ-EVM-00012`); restaurado `18 passed`; `findall` no teste antigo: novo `['SPEC', 'SDD', 'ADR', 'PRD', 'TS']`, antigo `['SDD', 'ADR', 'PRD']` | Sim |
| A02 | `\b` final de volta em `ID_PREFIX`, em cópia; pytest do A01; restaurar | `1 failed, 17 passed` (`test_sdd0064_placeholders_de_sequencia_reprovam_tipo_inexistente`); restaurado: `18 passed` | o próprio critério é o sensor | Sim |
| A03 | `` Veja `FOO-{PROJECT_CODE}-{SEQ4}`. `` no `SKILL.md`, em cópia; `check_renderings.py` | `cita o tipo inexistente 'FOO'`, `exit=1` | mesma linha com o script de `2430f9a`: `✅`, `exit=0` (antes não detectava) | Sim |
| A04 | `check_renderings.py` no kit | `✅ 5 renderização(ões) concordam com workflow-rules.yaml (8 tipos ativos, 6 Iron Laws, 4 níveis).` `exit=0` | `test_rf04_kit_real_passa` passa na suíte do A01 | Sim |
| A05 | `selftest.py` em cópia de `e5ac326` e em cópia de `2a4c5c9` | `13 mutação(ões): todos os mutantes morreram.` `exit=0`; base: `12` | a mutação nova, aplicada à mão, mata um teste de comportamento (`:127`), não um erro de import | Sim |
| A06 | comando literal da SDD, com `<base>` = `origin/main` | `--check` `exit=0`; `cmp` sem saída; `556 passed`; ruff, format e mypy sem erro; `framework_check --auto` `exit=0`; diff com os 8 arquivos previstos | sem mutação própria | Sim |
| A07 | `cmp` dos cinco arquivos da task 5, central (`048251a`) contra o kit | script, cópia da skill, teste e `mutations.yaml` diferem; `_framework/INDEX.md` igual | sem teste automatizado nesta etapa (espelho pós-merge) | Pendente: etapa pós-merge no kit |

## Descompassos encontrados

Requisito ↔ código: RF01 `check_renderings.py:163` (`ID_PREFIX`, igual à regex do requisito, só o `\b` final trocado por `(?!\w)`; mensagem de falha e `check_unknown_names` intocados); RF02 `test_check_renderings_unknown.py:130-131`; RF03 A04 e `test_rf04_kit_real_passa` (`:137-145`); RF04 os dois testes novos (`:125-131`), na ordem de aparição pedida, e nenhum teste antigo alterado (o diff do arquivo só acrescenta linhas); RF05 `mutations.yaml:80-84`, com `find` `|X|N)(?!\w)")` aparecendo uma única vez no script. Nenhum requisito sem código.

Arquivo tocado ↔ SDD: `git diff --name-only 2a4c5c9..e5ac326` dá os quatro arquivos das tasks 1 a 4 que mudaram (teste, script, `mutations.yaml`, cópia da skill) e, de `docs/sdd/`, a SDD, `INDEX.md`, `registry.md` e `registry.yaml`. Não há código sem requisito.

Achados não bloqueantes:

1. **`_framework/INDEX.md` não mudou.** A task 4 o lista, mas o índice não depende da regex, e `render_prompts.py --check` dá `_framework/INDEX.md: em dia`. Não é lacuna. No central, ele já é igual ao do kit.
2. **O caso `ADR-EVM-Xy` do negativo do RF02 não discrimina.** Sem o lookahead, `ID_PREFIX.findall("ADR-EVM-Xy")` devolve `['ADR']`, mas `ADR` é tipo conhecido e não gera falha. Quem segura o negativo é `XYZ-EVM-00012`. O caso segue a SDD ao pé da letra; um `XYZ-EVM-Xy` discriminaria.
3. **O `selftest.py` só imprime o total.** A morte da mutação nova por teste de comportamento foi conferida aplicando a mesma troca à mão (A02), não pela saída do selftest.
4. **A07 ainda não aplicável.** O central (`048251a`) não tem o espelho. O critério deve ser rodado por quem espelhar, depois do merge no kit.

## Lições

- **Red flag: negativo com tipo conhecido.** Um caso negativo de "não é id" cujo prefixo é um tipo válido passa com ou sem a regra, porque mesmo casando não gera falha. Nos negativos de extração de id, use prefixo inexistente.
- **Confirmar o que a regex extrai.** O sensor mais direto para "caso válido passa" é imprimir o `findall` antes e depois: aqui mostrou que `SPEC-{PROJECT_CODE}-{SEQ4}` e `TS-EVM-{SEQ}` só passaram a ser conferidos com esta SDD.
