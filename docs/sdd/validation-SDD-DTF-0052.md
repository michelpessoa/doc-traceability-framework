# Verificação — SDD-DTF-0052

- **Veredito:** PASS
- **Diff verificado:** `dd4a510..649d1f2` no kit (branch `sdd/SDD-DTF-0052-relatorio-nome-legado`); espelho no central em `c1d9ffe` (branch `sdd/SDD-DTF-0052-espelho`)
- **Rodada:** 1
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing small, `source_docs: []`) | SDD lida inteira; RF01 a RF05 têm código e teste ou grep correspondentes | n/a | Sim |
| A01 (RF01, RF02, RF03, RF04) | `pytest test_ci_gate_verify_sdd.py -q -k "legado or canonico or nenhum_relatorio"`, ANTES em `dd4a510` com o teste novo, DEPOIS em `649d1f2` | ANTES 3 failed, 1 passed; DEPOIS 4 passed | A02, A03 e mutação extra do RF04 | Sim |
| A02 (RF01) | Sem a tentativa do nome legado em `validation_paths`, em worktree descartável | 3 failed; restaurado 4 passed. Extra RF04 (mensagem com nome fixo): 1 failed; restaurado 4 passed | Derrubadas | Sim |
| A03 (RF02) | Ordem dos caminhos invertida (`reversed(paths)`) | 1 failed (precedência); restaurado 4 passed | Derrubada | Sim |
| A04 (RF05) | `grep -c "validation-{PROJ}-{SEQ}.md" docs/guias/gate-ci-verify-sdd.md` | `1` | sem teste automatizado (grep) | Sim |
| A05 | `render_prompts.py --check; echo exit=$?; cmp` script x cópia da skill | `exit=0`; `cmp` sem saída | n/a (medição) | Sim |
| A06 | pytest das duas suítes; ruff format/check nos arquivos alterados | 300 passed; 2 files already formatted; All checks passed | sem sensor próprio (suíte inteira) | Sim |
| A07 | `git diff --name-status origin/main` | 8 arquivos, todos previstos; `workflow-rules.yaml` intocado, versão 2.3.2 | n/a (medição) | Sim |
| A08 | `cmp` dos 4 arquivos kit x central (`c1d9ffe`); pytest no central | 4 `igual ...`; diff do central só os 4 arquivos; 17 passed | n/a (medição) | Sim |

## Descompassos encontrados

Nenhum requisito sem código, nenhum arquivo do diff fora da SDD e nenhum código sem requisito. Observações que não violam critério:

1. A implementação extraiu a função auxiliar `validation_paths(sdd_id)`, não nomeada na SDD; é a lista de caminhos que a especificação técnica descreve, sem comportamento extra, e `check_validation_presence` mantém a assinatura.
2. `test_relatorio_canonico_tem_precedencia_sobre_legado` passa também no código antigo (que só lia o canônico); o A01 pede pelo menos 3 failed no antes e teve 3. A discriminação desse teste vem do sensor A03, que o derruba.
3. `render_prompts.py --check` emite o aviso pré-existente de 30 SDDs sem seção de arquivos; não é desta mudança.

## Lições

- Red flag: teste de precedência entre duas fontes não falha no código que só conhece uma delas; o "antes" não o discrimina e só a mutação de ordem prova que ele testa algo.
