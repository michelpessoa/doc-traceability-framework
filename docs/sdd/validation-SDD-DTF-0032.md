# Verificação — SDD-DTF-0032

- **Veredito:** PASS
- **Diff verificado:** 22ea0c63a30f195c485a256addb7d44fc08eddfd..839317abeda9f152589298505cffc639675e6865
- **Verificador independente:** sim (sessão separada, sem histórico da sessão que implementou; só leu a SDD, o diff e o código)

| # | Critério (RF-ID) | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF01 — parse via `git show`, base vs head | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_parse_frontmatter_base_head -v` | `1 passed in 0.4s` (rodado como parte da suíte completa, 12 passed) | Sem mutação manual — comportamento já coberto indiretamente pelos sensores de RF04/RF05/RF07 abaixo, que dependem do mesmo parser | Sim |
| 2 | RF02 — validation ausente reprova transição | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_validation_ausente_reprova -v` | `PASSED` (suíte completa: 12 passed in 3.80s) | Sem mutação manual nesta rodada | Sim |
| 3 | RF03 — RF-ID sem linha de evidência reprova | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_rf_sem_cobertura_reprova -v` | `PASSED` | Sem mutação manual nesta rodada | Sim |
| 4 | RF04 — linha != PASS reprova apesar de veredito global PASS | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_linha_fail_reprova_apesar_de_veredito_pass -v` | `PASSED` | **Sensor real aplicado:** `check_evidence_rows()` mutado para `return []` antes do loop (cópia de backup em `/tmp`, sem git stash/commit) — teste falhou (`AssertionError: assert True is False`, `gate.passed` virou `True`). Restaurado a partir do backup; teste voltou a passar | Sim |
| 5 | RF05 — critério afrouxado sem justificativa reprova | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_criterio_afrouxado_reprova -v` | `PASSED` | **Sensor real aplicado:** `check_criteria_frozen()` mutado para forçar `justified = True` sempre — teste falhou (`gate.passed` virou `True` mesmo com critério alterado e sem justificativa). Restaurado; teste voltou a passar | Sim |
| 6 | RF05 — critério reordenado, texto idêntico, não reprova | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_criterio_reordenado_nao_reprova -v` | `PASSED` | Sem mutação manual nesta rodada (edge case complementar ao sensor do item 5, que já exercita `check_criteria_frozen`) | Sim |
| 7 | RF06/RF07 — override com INC válido libera | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_override_inc_valido_libera -v` | `PASSED` | Sem mutação manual nesta rodada | Sim |
| 8 | RF07 — override com INC `closed` reprova | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_override_inc_invalido_reprova -v` | `PASSED` | **Sensor real aplicado:** em `validate_incident_override()`, a checagem `if status not in OPEN_INCIDENT_STATUSES:` substituída por `if False:` (nunca reprova por status) — teste falhou (`gate.passed` virou `True` para INC `closed`). Restaurado a partir do backup, confirmado byte-idêntico (`diff` sem saída); teste voltou a passar | Sim |
| 9 | RF07 — falha de credencial vira exit 2 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_falha_credencial_exit_2 -v` | `PASSED` | Sem mutação manual nesta rodada | Sim |
| 10 | RF08 — log de override aceito (id, status, timestamp) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_log_override_aceito -v` | `PASSED` | Sem mutação manual nesta rodada | Sim |
| 11 | RF09 — front-matter malformado vira exit 2 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_frontmatter_malformado_exit_2 -v` | `PASSED` | Sem mutação manual nesta rodada | Sim |
| 12 | RF10 — paridade das duas cópias | `python3 -m pytest _framework/tests/test_kit_parity.py::test_ci_gate_verify_sdd_paridade -v` | `1 passed in 0.01s` | Checagem estrutural (`original.read_bytes() == bundled.read_bytes()`) — sem sensor comportamental aplicável | Sim |
| 13 | CLI ponta a ponta (fixture com 2 SDDs, uma pass uma fail) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_cli_pr_fixture_duas_sdds -v` | `PASSED` | Sem mutação manual nesta rodada | Sim |
| 14 | Ponteiro no `workflow-rules.yaml` seção 16 | `grep -n "ci_gate_verify_sdd" _framework/rules/workflow-rules.yaml` | `1255: _framework/scripts/ci_gate_verify_sdd.py bloqueia merge de PR que` | Checagem textual — sem sensor aplicável | Sim |
| 15 | `AGENTS.md`/`especificacao.md` regenerados sem divergência | `python3 _framework/scripts/render_prompts.py --check` | `exit=0`; todos os alvos (`AGENTS.md`, `especificacao.md`, cópias do kit incl. `references/workflow-rules.yaml` e `ci_gate_verify_sdd.py`) `em dia`/`sincronizado` | Checagem mecânica de sincronia — sem sensor comportamental aplicável | Sim |
| 16 | Workflow de exemplo existe e é YAML válido | `python3 -c "import yaml; yaml.safe_load(open('_framework/templates/ci/verify-sdd-gate.yml.example'))"` | Sem exceção | Checagem estrutural — sem sensor aplicável | Sim |
| 17 | Guia de adoção cobre credencial cross-repo + label | `grep -n "incident-override\|credencial" docs/guias/gate-ci-verify-sdd.md` | 6 ocorrências (linhas 34, 41, 47, 58, 63, e o título da seção "Credencial cross-repo") | Checagem textual — sem sensor aplicável | Sim |
| — | Suíte completa (regressão) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py _framework/tests/test_kit_parity.py -v` | `13 passed in 3.58s` | Rodado logo após restaurar o arquivo do sensor do item 8, confirmando ausência de regressão cruzada | Sim |

Ambiente: `pytest`/`pyyaml` não estavam disponíveis no Python global desta
sessão (`ModuleNotFoundError: No module named 'yaml'` na primeira
tentativa); criado venv isolado com `uv venv` + `uv pip install -r
requirements.txt` (`pytest==9.1.1`, `pyyaml==6.0.1`, conforme
`requirements.txt` do repositório) e todos os comandos acima foram
executados com esse interpretador.

Todas as mutações desta verificação foram aplicadas em
`_framework/scripts/ci_gate_verify_sdd.py` a partir de uma cópia de
backup guardada em `/tmp` (nunca `git stash`, nunca commit) e revertidas
com `cp` de volta antes do próximo item; `git status --short` confirmado
vazio ao final.

## Descompassos encontrados

Nenhum. RF01-RF10 têm código correspondente identificável em
`_framework/scripts/ci_gate_verify_sdd.py` (e cópia bundlada
byte-idêntica). Todo arquivo tocado pelo diff (`_framework/rules/workflow-rules.yaml`,
`_framework/scripts/ci_gate_verify_sdd.py`,
`_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`,
`_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py`,
`_framework/templates/ci/verify-sdd-gate.yml.example`,
`_framework/tests/test_ci_gate_verify_sdd.py`,
`_framework/tests/test_kit_parity.py`, `docs/guias/gate-ci-verify-sdd.md`)
corresponde a uma task da "Decomposição em tasks" da SDD. A cópia
`references/workflow-rules.yaml` não está listada explicitamente na
tabela de tasks, mas é gerada mecanicamente por `sync_copies()` em
`render_prompts.py` a partir de `_framework/rules/workflow-rules.yaml`
(mesmo mecanismo que gera `AGENTS.md`/`especificacao.md` da task 7) — não
é edição manual nem escopo não registrado. `AGENTS.md` e
`docs/especificacao.md` (task 7) não mudaram porque a seção
`gate_scope_verification` desses arquivos gerados usa prosa fixa
(itens 1-6) que não enumera sub-chaves arbitrárias do YAML — confirmado
lendo `render_prompts.py`/`especificacao.md` e reproduzido pelo
`--check` com exit 0 acima; não é tarefa pulada. Nenhuma abstração,
dependência, feature flag ou refactor sem requisito correspondente:
Camada 1 (hook de sessão) e o despacho do `sdd-verifier`
(SDD-DTF-0033) não foram tocados, como as "Instruções específicas" da
SDD exigiam.

## Lições

Nenhum red flag novo. O parâmetro `project_code` de
`validate_incident_override()`/`evaluate_gate()` é recebido mas não
usado dentro da função (o caminho do registry já vem resolvido em
`--central-registry-path`) — não é um descompasso porque a assinatura
bate exatamente o contrato publicado na SDD (`evaluate_gate(base, head,
changed_sdd_paths, pr_labels, pr_body, project_code,
central_registry_path)`); registrado aqui só para quem for estender o
script no futuro não estranhar o parâmetro aparentemente morto.
