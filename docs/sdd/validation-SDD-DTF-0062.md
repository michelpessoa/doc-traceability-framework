# Verificação — SDD-DTF-0062

- **Veredito:** PASS
- **Diff verificado:** `7c86bb9..bbb5b80` no kit (`7c86bb9` = `git merge-base HEAD origin/main`, SHA fixo, igual a `origin/main` no momento da verificação; o intervalo contém o merge `878a10d`, os testes em `e24a193`, o código em `b7beaa4`, a emenda da SDD em `643d566` e o kit-index e os gerados em `bbb5b80`)
- **Rodada:** 1
- **Verificador independente:** sim (subagente separado; não implementou e não leu o relatório nem o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão. Sensores numa cópia descartável feita com `git archive HEAD` em `verify-0062/` no scratchpad, e a base em `verify-0062/base` (`git archive 7c86bb9`), sem `git stash` e sem commit. O `selftest.py` rodou no kit sem merge em andamento, e `git status --short` ficou vazio depois. O central foi só lido. A emenda da task 1b foi conferida: a review `6064605026` da PR #157 é `COMMENTED`, de `michelpessoa`, sobre `643d566`, com o corpo `Aprovado`. O `approval_hash.py` da SDD dá o mesmo valor antes e depois do preenchimento da evidência (`63f5c16c…`).

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0062.md /home/user/doc-traceability-central/docs/DTF` | `✅ source_docs ... conferem`, `exit=0`; `source_docs: []`, sizing `small`, RFs escritos na própria SDD | sem teste automatizado (leitura) | Sim |
| A01 | comando literal da SDD, em `bbb5b80` e em cópia com o `render_prompts.py` de `7c86bb9` | `7 passed`; antes da task 2: `6 failed, 1 passed` | ver A02 | Sim |
| A02 | bloco `approval_policy` removido de `core_facts` em cópia; pytest do A01 | `5 failed, 2 passed`; restaurado `7 passed` | executor desligado, ciclo de volta à cadeia, regras fixas em `[:3]`, `hash_excluded_sections` fora da frase: `1 failed` cada | Sim |
| A03 | comando literal da SDD | nenhum `falta` | na base `7c86bb9`: 25 `falta` | Sim |
| A04 | comando literal da SDD | `0` nos três | na base: `1` nos três | Sim |
| A05 | `git diff 7c86bb9..HEAD -- AGENTS.md` lado a lado com `approval_policy`, `executor_contract` e `status_lifecycle` | toda linha nova tem chave correspondente, na ordem do YAML; nenhuma contradiz | sem teste automatizado (leitura) | Sim |
| A06 | comando literal da SDD e `selftest.py` | `exit=0` três vezes; `533 passed`; ruff, format e mypy sem erro; diff com os 9 arquivos das tasks 1, 1b, 2 e 3 e os 4 de `docs/sdd/`; selftest `10 mutação(ões): todos os mutantes morreram.` | `AGENTS.md` editado à mão em cópia: `divergente do gerado`, `exit=1` | Sim |
| A07 | `cmp` do script, da cópia da skill, do teste e do `kit-index.yaml`, central (`8798155`) contra o kit; `grep -c "### Aprovação" AGENTS.md` no central | os quatro diferem (o teste não existe no central); `0` | sem teste automatizado nesta etapa (espelho pós-merge) | Pendente: etapa pós-merge no kit |

## Descompassos encontrados

Requisito ↔ código: RF01 `render_prompts.py:195-208` (tabela de `approval_policy.rules`, `default_approver` e a frase); RF02 `:210-215` (`contract_version` e um item por `writes`); RF03 `:184` (`Estados:` com todos os `states`; "Transições válidas" e INC inalteradas); RF04 o laço sobre `policy.get("rules")`, sem prosa fixa, e o teste `test_render_prompts_core.py:79-86`; RF05 `test_render_prompts_core.py` (7 testes); RF06 os cinco gerados, a cópia da skill e `_framework/INDEX.md` regenerados, com `render_prompts.py --check` e `check_renderings.py` em `exit=0`. Nenhum requisito sem código.

Arquivo tocado ↔ SDD: `git diff --name-only 7c86bb9..bbb5b80` dá o teste (task 1), `kit-index.yaml` (task 1b, emenda), `render_prompts.py` (task 2), `AGENTS.md`, `docs/especificacao.md`, os três prompts, a cópia da skill e `_framework/INDEX.md` (task 3) e, de `docs/sdd/`, a SDD, `INDEX.md`, `registry.md` e `registry.yaml`. `workflow-rules.map.md`, que a task 3 lista com "se mudar", não mudou e segue `em dia`. Não há código sem requisito: o diff de `render_prompts.py` só troca a linha do ciclo e acrescenta os dois blocos.

A frase fixa do RF01 (`A aprovação fica em \`approved_by\`, presa ao \`content_sha256\` do documento, calculado por \`approval_hash.py\` sem as seções …; \`review_approval.py\` confere a review humana.`) cita todos os termos pedidos, e confere com as docstrings de `approval_hash.py` (hash do corpo sem as `hash_excluded_sections`, valor de `approved_by.content_sha256`) e de `review_approval.py` (decide se as reviews aprovam e monta o `approved_by`). As seções excluídas saem do YAML, não da prosa.

Achados não bloqueantes:

1. **`checks` da regra de SDD não aparece.** A regra `SDD | policy` do YAML tem uma lista `checks` (`validate_doc.py`, `registry_tools.py validate`, `check_source_docs.py`, verify-sdd passo 0) que a tabela não mostra. O RF01 pede só tipos, sizing e quem aprova, então não é lacuna, mas a IA que lê `AGENTS.md` não sabe o que a `policy` exige.
2. **`check_renderings.py` não confere os fatos novos.** Numa cópia com `Sem regra que case: policy.` em `AGENTS.md`, `check_renderings.py` sai com 0; só `render_prompts.py --check` acusa. É o que a SDD põe fora de escopo (SDD-DTF-0063), registrado aqui para quem for estender.
3. **`registry.yaml` no diff do A06.** Como na SDD-DTF-0061, o texto do A06 fala em "os gerados de `docs/sdd/`", e `registry.yaml` não é gerado; o diff dele é só a entrada desta SDD. Imprecisão de redação, sem efeito no veredito.
4. **Selftest sem mutação desta SDD.** O selftest segue com 10 mutações, nenhuma em `core_facts`. A SDD não pede uma; a discriminação está provada pelo A02.
5. **A07 ainda não aplicável.** O central (`8798155`) não tem o espelho nem branch dele. O critério deve ser rodado por quem espelhar, depois do merge no kit, incluindo o `kit-index.yaml` que a emenda acrescentou à task 4.

## Lições

- **Red flag: arquivo novo sem entrada no manifesto.** Um teste novo em `_framework/scripts/tests/` precisa de entrada em `kit-index.yaml`, ou `render_prompts.py` sai com 1. Uma SDD que cria arquivo no kit deve listar o `kit-index.yaml` nas tasks desde o começo; aqui faltou e exigiu emenda (task 1b).
- **Red flag: mutação aplicada na árvore errada.** Ao reaproveitar uma cópia descartável para o "antes" e depois para o sensor, restaure a versão de `HEAD` e confira com `cmp` antes de mutar; senão a mutação não casa e o vermelho vem da versão antiga, não da mutação.
