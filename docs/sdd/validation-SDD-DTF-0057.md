# Verificação — SDD-DTF-0057

- **Veredito:** FAIL
- **Diff verificado:** `efe1c71..17075b8` no kit (branch `sdd/SDD-DTF-0057-documentacao-enxuta`; `efe1c71` = `git merge-base HEAD origin/main` = `origin/main` nesta sessão); espelho no central em `faf53e5` (branch `claude/pickup-wkpglg`)
- **Rodada:** 1
- **Verificador independente:** sim (sessão diferente da que implementou; histórico dela não lido)

## Rodada 1

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0057.md <central>/docs/DTF`; comparação por script de RF01 a RF14 contra a SPEC-DTF-0031 (approved); leitura dos casos de borda, não funcionais e Parte 2 | `exit=0`; RF01 a RF14 com requisito e EARS idênticos (14/14); RF15 a RF17 declaradamente fora (fábrica); 17 casos de borda iguais aos da SPEC sem a parte da fábrica; contratos da Parte 2 descritos da mesma forma, só detalhados | sem teste automatizado (leitura) | Sim |
| A01 (RF01-RF04, RF06) | `pytest test_sdd_lean.py -q -k "not fidelity"`, ANTES em cópia de `efe1c71` com os testes novos | ANTES `16 failed, 9 passed`; DEPOIS `25 passed, 8 deselected` | ver A06 e A09 | Sim |
| A02 (RF05) | `pytest test_sdd_lean.py -q -k fidelity`, ANTES na mesma cópia | ANTES `3 failed, 5 passed`; DEPOIS `8 passed, 25 deselected` | ver A07 | Sim |
| A03 (RF12) | `pytest test_approval.py -q -k transitions`, ANTES na mesma cópia | ANTES `ImportError: cannot import name 'check_transitions'`; DEPOIS `11 passed, 35 deselected` | ver A08 | Sim |
| A04 (RF10) | `pytest test_generate_registry_md.py -q`, ANTES na mesma cópia | ANTES `4 failed, 14 passed`; DEPOIS `18 passed` | ANTES = implementação ausente | Sim |
| A05 (RF07, RF09) | `pytest test_spec_optional_sections.py test_render_indexes.py -q`, ANTES na mesma cópia | ANTES `ImportError: cannot import name 'OPTIONAL_MARK'`; DEPOIS `61 passed` | ANTES = implementação ausente; nenhum teste com mais de uma tabela na seção | Sim |
| A06 (RF02) | filtro `startswith("SPEC-")` tirado de `check_lean_sdd`; pytest de A01 | `1 failed, 24 passed` (`test_origem_so_com_a_adr_reprova`); restaurado `25 passed` | derrubada | Sim |
| A07 (RF05) | `missing = []` em `check_rf_fidelity`; pytest de A02 | `2 failed, 6 passed`; restaurado `8 passed` | derrubada | Sim |
| A08 (RF12) | conferência contra `allowed_transitions` trocada por `if False:`; pytest de A03 | `2 failed, 9 passed`; restaurado `11 passed` | derrubada | Sim |
| A09 (RF01-RF05) | `RULE_SINCE["sdd_lean"] = "1.0.0"`; `pytest test_sdd_lean.py -q` | `2 failed, 31 passed`; restaurado `33 passed` | derrubada | Sim |
| A10 (RF08, RF11, RF13) | `pytest test_executor_contract.py test_spec_optional_sections.py -q`; `check_renderings.py; echo exit=$?` | `24 passed`; `exit=0`; ANTES do contrato `3 failed, 12 passed` | ANTES = implementação ausente | Sim |
| A11 (não funcional) | `pytest test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` e contra `efe1c71` | `26 passed`; os dois diffs vazios | fixture do 2.3.2 compara stdout e exit | Sim |
| A12 (RF14) | `grep -n 'version: "2.7.0"'`; no central `framework_check.py --auto; echo exit=$?`; `git status --porcelain docs/ \| grep -v registry.md` | linhas 17 e 20; `134 documento(s) ok`, `exit=0`; porcelain vazio | sem teste automatizado (medição) | Sim |
| A13 | `render_prompts.py --check`; `generate_registry_md.py docs/sdd --check` | `em dia`/`sincronizado`, `exit=0` nos dois | sem teste automatizado (medição) | Sim |
| A14 | `pytest -q`; `ruff format --check` e `ruff check` nos 19 `.py` do diff; `selftest.py` | `504 passed`; `19 files already formatted`; `All checks passed!`; `7 mutação(ões): todos os mutantes morreram` | suíte inteira | Sim |
| A15 | no central `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | `diff exit=0` | sem teste automatizado (medição) | Sim |
| Contrato de `consolidated_rf_rows` | reprodução: SDD enxuta válida em `draft` (helpers de `test_sdd_lean.py`) com uma segunda tabela em "Requisitos consolidados"; `check_document` | três problemas espúrios `linha 3/4/5 de 'Requisitos consolidados' sem RF-ID.` | sem teste automatizado que cubra o caso | Não |

Os sensores mutaram uma cópia descartável de `17075b8` extraída com `git
archive` no scratchpad e foram restaurados pela cópia guardada de cada
arquivo. Os "antes" rodaram em cópia de `efe1c71` (`git archive`) com os
testes novos copiados por cima. O checkout do kit e o do central ficaram
com `git status --porcelain` vazio.

## Descompassos encontrados

1. **`consolidated_rf_rows` lê todas as tabelas da seção, não só a
   primeira** (`_framework/scripts/validate_doc.py:227` e `:231`). O
   contrato da SDD ("Especificação técnica consolidada", `validate_doc.py`)
   diz: "a primeira tabela de 'Requisitos consolidados'". O código junta
   toda linha da seção que começa com `|` e trata `lines[2:]` como dados,
   então cabeçalho, separador e linhas de uma segunda tabela viram
   requisitos. Uma SDD enxuta válida em `draft` com uma tabela de casos de
   borda nessa seção (formato que a própria SDD-DTF-0057 usa) reprova no
   `validate_doc.py` com `linha N de 'Requisitos consolidados' sem RF-ID.`
   uma vez por linha extra. Como `check_lean_sdd` roda em `draft` e
   `in_review`, esse falso positivo bloqueia o documento antes da
   aprovação. A docstring da função (linha 222) promete a primeira tabela.
   Nenhum teste do diff cobre seção com mais de uma tabela. Requisitos
   afetados: RF02 (e, pela reutilização, RF05).
2. **O mesmo padrão em dois consumidores**, de impacto menor:
   - `_framework/scripts/check_source_docs.py:61` e `:63`: os RFs da SPEC
     saem de toda linha `|` de "Requisitos funcionais", não só da tabela.
     O contrato diz "as linhas de dados da tabela de 'Requisitos
     funcionais'". Hoje só faz diferença se a SPEC tiver uma segunda tabela
     com RF-ID na primeira coluna dentro da seção.
   - `_framework/scripts/render_indexes.py:619`: o item (c) de
     `extract_sdd_files` segue lendo a coluna `Arquivos` nas tabelas
     seguintes da seção. O contrato diz "a coluna `Arquivos` da primeira
     tabela". Só faz diferença quando a segunda tabela tem coluna no mesmo
     índice com caminho entre crases.

Escopo nas duas direções, sem descompasso: os 42 arquivos de `git diff
--stat efe1c71..HEAD` aparecem na decomposição em tasks, são gerados por
`render_prompts.py` (cópias da skill, `references/workflow-rules.yaml`,
`AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`,
prompts, mapa, índices; `--check` em dia) ou são a própria SDD e o
registry de SDD. RF01 a RF14 têm código e teste. Fora isso, a única
mudança sem requisito próprio é a troca de `l` por `ln` em duas
comprehensions de `_framework/tests/test_procedures_structure.py`, um
arquivo que a task 8 lista; é lint para o `ruff check` do A14, sem efeito
no comportamento.

Observações que não violam critério:

- A SPEC dá `consolidated_rf_rows(body) -> list[dict]`. A SDD detalha para
  `list[dict] | None`, com `None` para tabela ausente. Aceito como
  detalhamento: a SPEC não diz o que acontece sem tabela.
- Na mensagem de `Origem` inválida, o caso de borda da SPEC pede "a lista
  de `source_docs`". A SDD e o código listam só as SPECs de `source_docs`,
  porque só SPEC vale em `Origem` (o caso "só com a ADR" reprova). Aceito
  como detalhamento.
- `check_molde` usa `applies("sdd_lean")`, que pede também projeto sob
  2.7.0. O EARS do RF03 fala só em "SDD criada a partir da 2.7.0". Isso
  segue a definição geral de não-retroatividade da SPEC
  (`rule_applies_since_date`).
- Em A09, só um teste de comportamento cai
  (`test_sdd_em_projeto_sob_2_6_0_nao_muda`); o outro é a asserção da
  constante. Os casos com `created` antigo não caem, porque a data da
  1.0.0 também é anterior a 2026-01-01.
- Os comandos de A11 usam `origin/main`, uma ref móvel. Nesta sessão
  `origin/main` = `efe1c71`, e o diff contra a base fixa também é vazio.
  Depois do merge, use `efe1c71`.
- No central, a PR também regenera `docs/especificacao.md`, `AGENTS.md`,
  `CHANGELOG.md` e `QUICKSTART.md`. São gerados de `render_prompts.py`,
  não documentos de decisão.

## Caminhos propostos (decisão do humano)

1. Corrigir a implementação: `consolidated_rf_rows` (e os dois
   consumidores) param na primeira linha que não começa com `|` depois do
   início da tabela, com um teste por função para seção com duas tabelas.
   Depois disso, rodada 2 desta verificação.
2. Ou atualizar a SDD (e a SPEC) para dizer "todas as tabelas da seção" e
   proibir uma segunda tabela em "Requisitos consolidados" da SDD enxuta,
   com uma mensagem própria.

## Lições

- Red flag: um contrato que diz "a primeira tabela", implementado como
  "toda linha da seção que começa com `|`". Os testes usam seções com uma
  tabela só, então passam com os dois comportamentos. Quando o contrato
  diz "primeira", um teste precisa ter duas.
- Red flag: sensor de não-retroatividade que só derruba um teste de
  comportamento. Se esse teste sumir, só sobra a asserção da constante.
