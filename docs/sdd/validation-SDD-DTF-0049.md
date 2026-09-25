# Verificação — SDD-DTF-0049

- **Veredito:** PASS (A01 a A16 e A18 a A27 passam sem ressalva; A17 e A28, manuais, passam com ressalvas de julgamento que o humano deve decidir, ver abaixo)
- **Diff verificado:** `1fe4f68..9c62fad` no kit (PR #127 e PR #131; ANTES da errata: `08f5b1e`); espelho no central em `91b69bf` (PR #154)
- **Rodada:** 2
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0049.md ../central/docs/DTF` e leitura RF a RF | `✅ source_docs ... conferem com o registry central.`, exit 0; nenhum RF sem representação | n/a | Sim |
| A01 | `python3 -m pytest _framework/tests/test_render_indexes.py -k titulo_completo -v` | 3 passed, 46 deselected | Mutação R1c (`_clean_title` sem descartar a cauda ` — `) derrubou `test_titulo_completo_junta_continuacao_e_descarta_cauda` e `test_metricas_mapa_real...`; restaurado, 49 passed | Sim |
| A02 | `python3 -m pytest _framework/tests/test_render_indexes.py -k resumo_cadeia -v` | 2 passed, 47 deselected | Mutação R1b (cadeia sem a fonte 3) derrubou `test_resumo_cadeia_fontes_em_ordem` e `test_resumo_cadeia_rotulo_frase_completa_e_bloco_vazio` | Sim |
| A03 | `python3 -m pytest _framework/tests/test_render_indexes.py -k corte_fronteira_palavra -v` | 2 passed, 47 deselected | Mutação R1a (`_cut_words` sem recuo ao espaço) derrubou `test_corte_fronteira_palavra_limite_e_conectivo`, `test_metricas_mapa_real...` e `test_corte_descarta_travessao...` | Sim |
| A04 | `python3 -m pytest _framework/tests/test_render_indexes.py -k map_summaries -v` | 8 passed, 41 deselected | Mutação R1d (sem validar id de `map_summaries`) derrubou `test_map_summaries_id_inexistente_sai_2_citando_id`; extra X5 (valor vazio aceito) derrubou `..._valor_vazio_ou_nao_textual_sai_2[""]` | Sim |
| A05 | `python3 -m pytest _framework/tests/test_render_indexes.py -k kit_index_o_que_e_distinto -v` | 3 passed, 46 deselected | Mutação R1e (sem expansão de `{name}`) derrubou `..._expande_name_e_stem` e `..._no_index_real` | Sim |
| A06 | `python3 -m pytest _framework/tests/test_render_indexes.py -k metricas_mapa_real -v` | 1 passed, 48 deselected | Mutações R1a, R1c, X1 (sem `DASHES`) e X2 (sem recuo de parêntese) derrubaram `test_metricas_mapa_real...` | Sim |
| A07 | awk de A07 sobre o mapa: ANTES `git show 1fe4f68:_framework/rules/workflow-rules.map.md \| awk ...`; DEPOIS `awk ... _framework/rules/workflow-rules.map.md` (kit em 9c62fad) | ANTES (1fe4f68): `9 16`; DEPOIS: `0 1` (meta: 0 e ≤ 1) | n/a (comando de medição; coberto por A06) | Sim |
| A08 | MEDE-CORTE (script da SDD) sobre YAML e mapa: ANTES com `git show 1fe4f68:` dos dois; DEPOIS com os arquivos do kit em 9c62fad | ANTES (1fe4f68): `5 ['§4', '§11', '§13', '§17', '§18']`; DEPOIS: `0 []` | n/a (comando de medição; coberto por A06) | Sim |
| A09 | awk de A09 sobre o INDEX: ANTES `git show 1fe4f68:_framework/INDEX.md \| awk ...`; DEPOIS `awk ... _framework/INDEX.md` | ANTES (1fe4f68): `98 27`; DEPOIS: `0 111`; cabeçalho `Total: 111 arquivos` | n/a (comando de medição; coberto por A05) | Sim |
| A10 | `python3 _framework/scripts/render_indexes.py --check; echo exit=$?` e `python3 _framework/scripts/render_prompts.py --check; echo exit=$?` | `✅` em cada índice; `mapa+maior seção = 12567 (13.7% do YAML)` (YAML 91557 bytes, teto 13733); INDEX ≤ 24576 e linhas ≤ 200 (o `--check` reprova acima disso); `exit=0` nos dois | n/a (comando de medição; tetos cobertos por `test_tetos`) | Sim |
| A11 | `python3 -m pytest _framework/tests/test_render_indexes.py -k "manifesto_orfao or mapa_ids_batem or tetos or idempotente" -v` | 14 passed, 35 deselected | sem sensor próprio nesta rodada (testes pré-existentes da SDD-DTF-0043) | Sim |
| A12 | `git diff --stat origin/main -- _framework/rules/workflow-rules.yaml _framework/scripts/render_prompts.py` e leitura de `framework.version` no worktree e em `origin/main` | Primeiro comando sem saída; versão `2.3.2` nos dois (a SDD cita `2.3.1` na data da SPEC-DTF-0022; a 2.3.2 veio da SDD-DTF-0048, mergeada antes; o critério pede a versão de `origin/main`) | n/a (comando de medição) | Sim |
| A13 | `diff -r -x __pycache__ -x .pytest_cache -x .ruff_cache -x .mypy_cache _framework ../central/_framework; echo exit=$?`, com worktree do kit em 9c62fad e worktree do central em 91b69bf (não os checkouts em `/home/michel`, o central está em outra branch) | Sem saída de diff, `exit=0` | n/a (comando de medição) | Sim |
| A14 | `python3 -m pytest _framework/tests/test_kit_parity.py -k render_indexes -v` | 1 passed, 2 deselected | sem sensor próprio nesta rodada | Sim |
| A15 | `python3 _framework/scripts/render_indexes.py sdd docs/sdd --check; echo exit=$?` | `✅ docs/sdd/INDEX.md: em dia.`, `exit=0` (aviso pré-existente de 30 SDDs sem seção de arquivos) | n/a (comando de medição) | Sim |
| A16 | `python3 -m pytest _framework/ -q` | 292 passed in 29.66s | sem sensor próprio nesta rodada (suíte inteira; sensores por critério em A01 a A06 e A22) | Sim |
| A17 | Leitura humana do mapa inteiro (22 linhas) e de 10 linhas de `_framework/INDEX.md` sorteadas com `random.seed(4909)` | Mapa: 22 linhas lidas. INDEX: 10 de 10 linhas descrevem o arquivo e são distintas entre si (conferidas 3 contra o arquivo: `test_repo_hygiene.py`, `mutations.yaml`, `test_ci_gate_verify_sdd.py`). Ressalvas no mapa, para decisão humana: §14 (`Mesmo incidente EVM da seção 13…`) não distingue o §14 do §13 no Resumo (a coluna Seção distingue); §15 (`Os gates 13/14 garantem ORDEM…`) corta a frase num ponto que sugere o oposto do que o gate trata (qualidade de conteúdo); §5 termina em `são…` (o corte da SPEC-DTF-0024 não o alcança); §13, §16, §18, §19 descrevem histórico ou outra seção (limite reconhecido da SPEC-DTF-0022, fora de escopo da 0024) | n/a (critério manual) | Sim, com ressalvas (decisão humana) |
| A18 | ANTES em `08f5b1e` (main antes do PR #131): `python3 -m pytest _framework/tests/test_render_indexes.py -k corte_descarta_travessao -v`; DEPOIS em `9c62fad`: mesmo comando | ANTES: `45 deselected`, 0 selected; DEPOIS: 1 passed, 48 deselected | Mutações X1 (sem `DASHES`) e X2 (sem recuo de parêntese) derrubaram o teste | Sim |
| A19 | `python3 -m pytest _framework/tests/test_render_indexes.py -k "conectivo_pendurado_exercido or map_summaries_perde_para_fonte_3 or piso_summary_min" -v` | 3 passed, 46 deselected | R2a, R2b e R2c derrubaram cada um o teste correspondente (ver A22) | Sim |
| A20 | `python3 -c "rows=[...]; print(...)"` do critério, ANTES em `08f5b1e` e DEPOIS em `9c62fad` | ANTES (08f5b1e): `2 3`; DEPOIS: `0 0` | n/a (comando de medição; coberto por `test_metricas_mapa_real`) | Sim |
| A21 | `python3 _framework/scripts/render_indexes.py --check; echo exit=$?` e `python3 _framework/scripts/render_prompts.py --check; echo exit=$?` | Os dois `exit=0`; `mapa+maior seção = 12567 (13.7% do YAML)`, abaixo de 15% | n/a (comando de medição) | Sim |
| A22 | Cópia descartável do worktree (`cp -r`), 3 mutações da errata + as 5 da rodada 1 + 6 extras; `python3 -m pytest _framework/tests/test_render_indexes.py -q` em cada | Base: 49 passed. (a) R2a `DANGLING` removido do laço final: FAILED `test_corte_descarta_conectivo_pendurado_exercido` e `test_corte_descarta_travessao...`; (b) R2b `override` antes da fonte 3: FAILED `test_map_summaries_perde_para_fonte_3`; (c) R2c `SUMMARY_MIN` 28 para 10: FAILED `test_piso_summary_min_no_encurtamento_da_linha`. Rodada 1: R1a a R1e todas derrubadas. Extra: X1, X2, X4, X5, X6 derrubadas; X3 (sem descarte de palavra final terminada em `( : , ;`) SOBREVIVE (49 passed). Restaurado: 49 passed | As 3 lacunas anteriores agora são pegas; 1 mutação extra (X3) sobrevive, fora dos critérios | Sim |
| A23 | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | 292 passed in 29.46s | sem sensor próprio (suíte inteira) | Sim |
| A24 | `grep -c 'references/\*' docs/sdd/SDD-DTF-0049.md; grep -c "SPEC-DTF-0024" docs/sdd/SDD-DTF-0049.md` | `2` e `23` | n/a (comando de medição) | Sim |
| A25 | `cmp _framework/scripts/render_indexes.py _framework/skills/doc-traceability-framework/scripts/render_indexes.py; ruff format --check _framework/scripts; echo exit=$?` | `cmp` sem saída; `33 files already formatted`; `exit=0` | n/a (comando de medição; paridade coberta por A14) | Sim |
| A26 | `git diff --name-only 08f5b1e 9c62fad` (baseline: main antes do PR #131) | 5 arquivos: `_framework/INDEX.md`, `_framework/rules/workflow-rules.map.md`, `_framework/scripts/render_indexes.py`, cópia dele na skill, `_framework/tests/test_render_indexes.py`; nenhum `workflow-rules.yaml` nem `render_prompts.py` (os gerados de `docs/sdd/` não mudaram nesse intervalo) | n/a (comando de medição) | Sim |
| A27 | Loop de `cmp` dos 6 arquivos entre kit (9c62fad) e central (91b69bf), e `python3 _framework/scripts/render_prompts.py --check; echo exit=$?` no central | 6 linhas `igual ...` (scripts/render_indexes.py, cópia da skill, tests/test_render_indexes.py, rules/kit-index.yaml, rules/workflow-rules.map.md, INDEX.md); `exit=0` | n/a (comando de medição; espelho também coberto por A13) | Sim |
| A28 | Leitura humana das 22 linhas do mapa regenerado e saída de A20 | Literalmente cumprido: nenhum resumo termina em travessão nem parêntese aberto (A20 `0 0`); §13, §16, §18, §19 seguem como limite reconhecido. Mesmas ressalvas do A17 (§14, §15, §5) | n/a (critério manual) | Sim, com ressalvas (decisão humana) |

## Descompassos encontrados

Nenhum requisito sem código, nenhum arquivo do diff fora da SDD (os arquivos de `AGENTS.md`, prompts, YAML e `docs/especificacao.md` no diff `1fe4f68..9c62fad` vêm da SDD-DTF-0048) e nenhum código sem requisito. Fidelidade à origem: `check_source_docs.py` sai 0 (`✅ source_docs de SDD-DTF-0049.md conferem com o registry central.`); RF01 a RF07 da 0022, RF01 a RF05 da 0024 e RF01 a RF04 da 0025 têm representação na SDD; `SUMMARY_MIN = 28` prevalece (SPEC-DTF-0025).

Achados que não violam critério escrito, para decisão humana:

1. **§14** resume `Mesmo incidente EVM da seção 13…`: o Resumo não distingue o §14 do §13 (a coluna Seção distingue). Causa: a fonte 2 é o comentário `Origem: mesmo incidente EVM da seção 13 — ...`, e o corte em travessão deixa só a referência.
2. **§15** resume `Os gates 13/14 garantem ORDEM…`: a frase cortada sugere o oposto do foco do gate (qualidade de conteúdo). É o recuo até antes do parêntese (0024 RF02) que produz isso; cumpre A20 e o piso 28 (0025).
3. **§5** termina em `são…` depois de `... — são…`; o corte da 0024 só trata travessão como última palavra, então este caso, citado no Objetivo da 0024, continua com frase incompleta. A20 não o conta.
4. **§3, §11, §17**: resumos legíveis e sem travessão nem parêntese aberto (§3 `... -> SDD…`, §11 `... nasce de um documento aprovado…`, §17 `... separa quem planeja…`), embora cortados. **§13, §16, §18, §19** descrevem histórico ou outra seção: limite reconhecido pela SPEC-DTF-0022 e fora de escopo da 0024.
5. Sensor extra **X3** (remover o descarte de palavra final terminada em `(`, `:`, `,`, `;` no laço de `_cut_words`) sobrevive: 49 passed. Não é lacuna de critério da SDD, mas é uma linha do contrato de RF03 sem teste que a derrube.
6. A12: a SDD cita versão `2.3.1`, mas `origin/main` está em `2.3.2` (SDD-DTF-0048). O critério pede a versão de `origin/main`, que confere.

Se a decisão for que os itens 1 e 2 violam A17 (`cada linha distingue o alvo dos vizinhos, sem frase cortada que mude o sentido`), o veredito de A17 vira FAIL e o caminho é ou aceitar o limite por escrito na SDD ou abrir `map_summaries` para §14 e §15 (a fonte 3 vence `map_summaries` só onde existe; §14 e §15 têm fonte 2, então `map_summaries` não os alcançaria sem mudar a cadeia).

## Lições

- Red flag: regra de corte que só olha a última palavra deixa frases incompletas cujo sentido é decidido pelo que foi cortado (§5, §14, §15). Medir por métrica mecânica (travessão, parêntese) não substitui a leitura manual de A17.
- Red flag: critério manual aprovado 'com ressalvas' precisa dizer se a ressalva viola o critério escrito; senão vira PASS silencioso.
- Mutação extra sobrevivente (X3) mostra que sensores dos critérios cobrem só as mutações listadas; vale enumerar as linhas do laço final de `_cut_words` como mutações.

## Decisão humana sobre A17 e A28 (2026-09-25)

O revisor humano (Michel Pessoa) aceitou A17 e A28 com as ressalvas acima:
nenhum critério escrito é violado (A20 dá `0 0`), e o índice melhorou de 98
linhas com "O que é" repetido para 0. Ficam registrados como limites
conhecidos, sem correção nesta SDD:

- §14 (`Mesmo incidente EVM da seção 13…`) não distingue o §14 do §13 no Resumo.
- §15 (`Os gates 13/14 garantem ORDEM…`) corta a frase num ponto que sugere o
  oposto do foco do gate (qualidade de conteúdo), efeito do recuo do
  parêntese (SPEC-DTF-0024 RF02) com o piso 28 (SPEC-DTF-0025).
- §5 termina em `são…`: o corte da SPEC-DTF-0024 só trata travessão como
  última palavra.

Pendência sem documento: a mutação X3 (remover o descarte de palavra final
terminada em `(`, `:`, `,` ou `;` no laço de `_cut_words`) sobrevive à suíte;
é linha do contrato do RF03 sem teste que a derrube. Corrigir os resumos do
§14, §15 e §5 pede mudar a regra de corte ou a cadeia de fontes, ou seja,
outra SPEC.
