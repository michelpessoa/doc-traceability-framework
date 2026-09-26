# Verificação — SDD-DTF-0051

- **Veredito:** PASS
- **Diff verificado:** `551b928..6f42e45` no kit (PR #139 e PR #140); espelho no central em `9cd0f0d` (PR #159 e PR #160)
- **Rodada:** 2
- **Verificador independente:** sim (subagente `sdd-verifier`, contexto próprio, worktrees de `origin/main`)

A rodada 1 (kit `6e265f1`, central `e2a7b08`) deu PASS com uma ressalva: a mutação "override em 2º lugar, depois do corpo do banner" sobrevivia (50 passed), porque a fixture do teste de precedência não tinha `banner_body`. O PR #140 acrescentou o caso (mutação agora falha) e o PR #160 espelhou o teste; a rodada 2 confirma.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0051.md <central>/docs/DTF` | `source_docs ... conferem com o registry central`, `exit=0`; RF01 a RF04 da 0026 e RF01/RF02 da 0027 presentes; textos do RF02 são os da 0027 | n/a | Sim |
| A01 | `grep` das linhas §5, §14 e §15 do mapa e `wc -c` | DEPOIS: 171, 179 e 180 bytes, nenhuma com `…`; ANTES (`551b928`): 3 linhas com `…` | Sem asserção automatizada (ver Descompassos, item 1); `--check` pega divergência sem regeneração | Sim |
| A02 | `pytest -k "cut_words or precedencia_override" -v` | DEPOIS `2 passed, 48 deselected`; testes novos sobre o código antigo: `precedencia_override` FAILED, `cut_words` passed | Precedência falha com o código antigo | Sim |
| A03 | Cópia: `sed` remove ` or words[-1][-1] in "(:,;"`; `pytest test_render_indexes.py -q` | ANTES (`551b928`): `49 passed` com e sem a mutação; DEPOIS com a mutação: `1 failed, 49 passed` | X3 derrubada; cada um de `:`, `,`, `;`, `(` removido sozinho também falha | Sim |
| A04 | Cópia com `override` em 4º; `pytest -k precedencia_override` | Ordem antiga `1 failed`; nova `1 passed` | Mutação derrubada; override em 2º, 3º e 5º também derrubados | Sim |
| A05 | `git diff -U0 551b928 HEAD -- workflow-rules.map.md` filtrado por §2, §6, §7, §9, §12 | Sem linhas, `exit=1`; só §5, §14, §15 mudaram | n/a | Sim |
| A06 | `render_indexes.py --check; echo exit=$?` | mapa, INDEX e `docs/sdd/INDEX.md` em dia, `exit=0` | `--check` sai 1 com mapa divergente | Sim |
| A07 | pytest das duas suítes; `ruff format --check`; `render_prompts.py --check`; `cmp` | 296 passed; 33 files already formatted; `--check` em dia; `cmp` sem saída; `exit=0` | Sensores de A03 e A04 | Sim |
| A08 | `git diff --name-only 551b928 HEAD` | 5 arquivos previstos; nenhum `workflow-rules.yaml`, nenhum `prompts/` | n/a | Sim |
| A09 | `git diff -U0 551b928 HEAD -- render_indexes.py` | 1 hunk (`@@ -268 +268 @@`), só reordena a tupla | n/a | Sim |
| A10 | `cmp` dos 6 arquivos kit x central; `--check` no central | 6 `igual ...`; `exit=0` | n/a | Sim |
| A11 | constantes e diff filtrado por `SUMMARY_M` e `TITLE_M` | `28 100`, nenhuma linha de diff, `exit=1` | n/a | Sim |

Mutações tentadas pelo verificador (todas em cópia): na cadeia de fontes, override em cada posição, permutações das demais fontes e remoção de cada fonte, todas derrubadas; em `_cut_words`, cada pontuação de `"(:,;"`, `[-1]` por `[0]`, ramificação sem o pop e contagem de parêntese, todas derrubadas exceto as listadas em Descompassos.

## Descompassos encontrados

Nenhum requisito sem código, nenhum arquivo do diff fora da SDD e nenhum código sem requisito. Observações:

1. **A01 e as entradas de `kit-index.yaml` sem asserção automatizada (ressalva aceita).** Nenhum teste compara o mapa real aos três textos: cinco mutações do manifesto sobrevivem à suíte (`50 passed`). O `--check` derruba as que não são seguidas de regeneração; remover a entrada do §14 e regenerar volta a linha a `Mesmo incidente EVM da seção 13…`, com `--check` em `exit=0`, e só a leitura do grep do A01 pega. A SPEC-DTF-0026 desenhou E03 como comando, não como teste; com a folga zero do §15 (180 bytes) a regressão por crescimento de título seria silenciosa. Um teste ou linha de `--check` que afirme os três textos exigiria nova SPEC.
2. O "ANTES" do A02 não é executável literalmente (em `551b928` o `-k` seleciona 0 testes); a leitura válida é rodar os testes novos sobre o código antigo.
3. A05, A08, A09 e A11 dizem `main`, que avançou; a verificação usou o SHA fixo `551b928`.
4. Sobreviveram mutações de `_cut_words` fora dos quatro caracteres do RF03 e anteriores a esta SDD: acrescentar `.` ao conjunto, `text[:limit-1]` por `text[:limit]`, `<=` por `<`, `idx > 0` por `>=`, remover `.lower()` do teste de DANGLING e `rfind("(")` por `find("(")` (provável equivalente).
5. Dois testes antigos mudaram por consequência inevitável do RF01: `test_map_summaries_so_sem_fonte_automatica` foi substituído e `test_map_summaries_perde_para_fonte_3` renomeado; a SDD cita só o primeiro.
6. O aviso pré-existente "30 SDD(s) sem seção de arquivos" não é desta mudança.

## Lições

- Red flag: teste de precedência precisa exercitar cada fonte que o override supera; fixture com uma só fonte deixa passar mutação de posição intermediária (rodada 1, fonte 1).
- Red flag: SPEC que mede o teto de bytes por comando na implementação, e não na própria SPEC, gerou errata (0027): medir a linha do mapa antes de fixar o texto.
- Guarda do texto final do mapa depende do `render_indexes.py --check` e de leitura; deixar isso explícito na coluna Sensor.
