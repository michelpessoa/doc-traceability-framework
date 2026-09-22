# Verificação — SDD-DTF-0038

- **Veredito:** PASS
- **Diff verificado:** b59c011..0e7c3b5 (merge-base `sdd/SDD-DTF-0038` × `origin/main`, capturado antes de qualquer merge desta mudança)
- **Verificador independente:** sim (sessão sem histórico da implementação, despachada só para esta verificação)

## Passo 0 — Fidelidade à origem

- `check_source_docs.py` confirmou `source_docs` (SPEC-DTF-0015) existente, `approved`, url batendo com o registry central.
- SPEC-DTF-0015 lida inteira. RF01-RF07 todos representados na SDD, nenhum RF ausente. Casos de borda e contratos técnicos da Parte 2 (assinaturas `apply_mutation`, `run_mutation`, `extract_entries`, `find_candidates`, CLIs) idênticos entre SPEC e SDD.
- RF01 diverge do texto literal da SPEC de forma **deliberada e registrada**: a SPEC pede reaproveitar exatamente os pares find/replace de SDD-DTF-0036/0037 para os 4 validadores, mas essas duas SDDs só documentam mutação para `validate_state.py` (2 pares, RF03/RF04) e `check_source_docs.py` (1 par, RF02/RF03). A SDD-DTF-0038 registra em `consumption_instructions` e na tabela "Mutações de `mutations.yaml`" que a mutação de `check_hooks.py` (par 6) vem de SDD-DTF-0029 (fora do escopo literal de RF01, mesma técnica) e a de `check_commit.py` (par 7) é nova, sem fonte anterior, confirmada com o humano antes da redação.
- Conferi cada uma das 7 citações de proveniência contra o documento de origem citado (find/replace/test_file exatos):
  - #1, #2 → SDD-DTF-0036.md linhas 194-195 (RF03/RF04, Evidência #3/#4): batem.
  - #3, #4 → SDD-DTF-0037.md linhas 180-181 (RF05/RF06, Evidência #4/#5): batem.
  - #5 → SDD-DTF-0037.md linha 178 / validation-SDD-DTF-0037.md linha 34 (RF02/RF03, Evidência #2): batem.
  - #6 → SDD-DTF-0029.md linha 141 (Evidência #2): bate.
  - #7 → sem fonte anterior, como declarado; verificado nesta sessão que a mutação de fato mata os testes de `check_commit.py`.
- Nenhum arquivo do diff fora da lista "Arquivos tocados" da SDD. Nenhuma abstração/config extra sem requisito correspondente.
- Conclusão: registro de proveniência é fiel, não é omissão a sinalizar — é exatamente o que o enunciado da tarefa descreveu.

## Passo 1/2/3 — Evidência fresca + sensor de discriminação

Ver tabela "Evidência de verificação" em `docs/sdd/SDD-DTF-0038.md` — 9 critérios + fidelidade à origem, todos com comando rodado nesta sessão, saída real e sensor de discriminação real (mutação aplicada em espaço descartável via `cp` de cópia guardada, nunca `git stash`; confirmado que o teste cai; restaurado; `git diff --stat` vazio confirmado após cada restauração).

Resumo de sensores aplicados nesta sessão (todos mataram o teste correspondente e foram restaurados):

| Alvo mutado | Mutação | Teste que caiu |
|---|---|---|
| `mutations.yaml` | remoção da entrada `check_commit.py` | `test_mutations_yaml_cobre_os_4_validadores_com_5_campos` |
| `selftest.py::apply_mutation` | guarda de `find` ausente neutralizada | `test_apply_mutation_find_ausente_levanta_erro`, `test_run_mutation_find_ausente_reporta_erro_nao_sobrevivente` |
| `mutations.yaml` (entrada real `check_commit.py`) | `find` corrompido (simula drift de código-fonte) | `selftest.py` real reportou erro + exit 1 (critério #4, sensor com dados reais) |
| `lessons_check.py::find_candidates` | filtro `confirmed` neutralizado | `test_find_candidates_exclui_confirmada` |
| `lessons_check.py::find_candidates` | limiar `>= 2` relaxado para `>= 1` | `test_find_candidates_slug_em_um_arquivo_so_nao_e_candidata`, `test_find_candidates_duas_ocorrencias_mesmo_arquivo_nao_conta`, `test_find_candidates_exclui_confirmada` |
| cópia bundlada `_framework/skills/.../lessons_check.py` | linha extra só na cópia | `render_prompts.py --check` reportou `divergente` |

Critério #7 (regressão de `validate_doc.py`/`validate_state.py`) não recebeu sensor novo nesta sessão — são validadores pré-existentes, não tocados por esta SDD, já sensor-testados em SDD-DTF-0036/SDD-DTF-0037; rodar de novo aqui é checagem de regressão, não de código novo.

## Passo 4 — Checagem mecânica

```
python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0038.md
```

`✅ 1 documento(s) verificados: nenhuma SDD implemented sem evidência.` exit 0.

## Descompassos encontrados

Nenhum. RF01-RF07 todos com código correspondente. Nenhum arquivo do diff fora da lista "Arquivos tocados". Nenhuma abstração extra. A única divergência em relação ao texto literal da SPEC (RF01, proveniência dos pares de mutação) já vinha registrada e confirmada com o humano antes da redação da SDD — não é um descompasso desta verificação, é o objeto que a verificação confirmou como fielmente documentado.

## Lições

Nenhuma lição nova — verificação transcorreu sem achado bloqueante. A técnica de sensor "mutação real em dado de configuração" (`mutations.yaml`, critério #1) e "mutação real com dado real end-to-end" (critério #4, corromper `find` de uma entrada real em vez de só testar com fixture sintética) reforça um padrão já em uso nas SDDs anteriores (0036/0037/0029): vale manter.
