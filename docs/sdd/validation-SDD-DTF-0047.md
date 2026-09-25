# Verificação — SDD-DTF-0047

- **Veredito:** PASS
- **Diff verificado:** 5f52c58658fa8c2b41029543648341f525d4f15a..7b71e15
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | pytest test_table_cells.py -v | 14 passed | logica antiga: 4 FAILED | Sim |
| 2 | pytest test_validate_state.py | 40 passed, 2 novos PASSED | logica antiga: 2 FAILED | Sim |
| 3 | pytest 4 arquivos de _framework/tests | 71 passed | por site: cada teste novo FAILED | Sim |
| 4 | logica antiga em copia descartada | 12 failed, 254 passed; restaurado 266 passed | sensor discrimina (falha por asserção) | Sim |
| 5 | teste de varredura RF07 | 1 passed | split direto reintroduzido em cada um dos 5 scripts: FAILED | Sim |
| 6 | render_prompts.py --check | sai 0 | n/a | Sim |
| 7 | pytest scripts/tests e tests | 266 passed (kit e central) | n/a | Sim |
| 8 | framework_check.py --auto | passou (kit e central) | n/a | Sim |
| 9 | ruff check, ruff format --check, mypy | limpos (kit e central) | n/a | Sim |
| 10 | diff -r scripts kit vs central | sem saida | n/a | Sim |

## Descompassos encontrados

Nenhum bloqueante. Criterio 4 executado com variante: o comando literal
(git stash) faz test_table_cells.py falhar na coleta com ImportError, e o
procedimento proibe stash; usada copia descartada com a logica antiga no
corpo do helper. RF03 conferido por fuzz (285443 linhas sem pipe escapado,
resultado identico ao split antigo). Diff do kit = arquivos planejados,
copias geradas do bundle, _framework/INDEX.md e a propria SDD; central: 19
arquivos, todos em _framework/.

## Lições

Critério de sensor baseado em git stash falha por ImportError quando o
helper e novo; especificar "copia descartada com a logica antiga" no lugar.
