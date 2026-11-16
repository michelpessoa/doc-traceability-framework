# Verificação — SDD-DTF-0053

- **Veredito:** PASS
- **Diff verificado:** `279b10a..c0e2c3b` no kit (branch `sdd/SDD-DTF-0053-contrato-do-executor`); espelho no central em `0fb03c3` (branch `sdd/SDD-DTF-0053-espelho`), contra o merge-base `d812311` com o `main` do central
- **Rodada:** 2
- **Verificador independente:** sim (sessão diferente da que implementou e da que corrigiu)

## Rodada 2

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py` contra a branch `docs/spec-dtf-0028-approved` e contra o `main` do central (`96c376f`, PR #193 mergeada); leitura do bloco `executor_contract` e do M4 da SPEC | exit 0 nos dois; SPEC igual à da rodada 1; chaves e campos iguais aos da SPEC | sem teste automatizado (leitura) | Sim |
| A01 (RF01, RF02) | `pytest _framework/scripts/tests/test_report_json.py -q`, ANTES em `279b10a` com teste, fixture e esquemas copiados | ANTES `ImportError ... json_flag`, 1 error; DEPOIS `26 passed` | ver A05 e A02 | Sim |
| A02 (RF01) | 12 casos de `test_saida_em_texto_igual_a_2_3_2` mais o de cobertura da fixture; `fixture_check.py` rodando os `CASOS` com os scripts de `279b10a`; mutações em worktree descartável | `12/12 casos iguais à fixture com scripts de 279b10a`; em `279b10a` `13 passed`; mutação do uso `5 failed`; mutação do OK do `validate_state.py` `1 failed`; restaurado `26 passed` | 2 de 2 derrubadas | Sim |
| A03 (RF03, RF04, RF05, RF07) | `pytest _framework/tests/test_executor_contract.py -q`, ANTES em `279b10a` com teste e esquemas copiados | ANTES `8 failed, 1 passed`; DEPOIS `9 passed`; `sdd_id` devolvido ao esquema: `2 failed` | ver A04 | Sim |
| A04 (RF05) | `sizing` renomeado; `schema` inexistente; `exit_codes: {}` acrescentado ao contrato | `1 failed`; `2 failed`; `1 failed`; restaurado `9 passed` | 3 de 3 derrubadas | Sim |
| A05 (RF02) | `_item` devolvendo sempre `documento: None` | `3 failed, 23 passed`; restaurado `26 passed` | derrubada | Sim |
| A06 (RF06) | `pytest _framework/scripts/tests/test_registry_entrega.py -q`, ANTES em `279b10a` | ANTES `2 failed, 2 passed`; DEPOIS `4 passed` | o antes derruba os dois testes de impressão | Sim |
| A07 (RF08) | `grep -n 'version: "2.4.0"'`; `framework_check.py --auto` no central (espelho) | linhas 17 e 20; `134 documento(s) ok`, `exit=0` | sem teste automatizado (medição) | Sim |
| A08 | `render_prompts.py --check; echo exit=$?` | `exit=0` | sem teste automatizado (medição) | Sim |
| A09 | `pytest -q`; `ruff format --check` nos 19 `.py` do diff; passos do CI; `selftest.py` | `339 passed`; `19 files already formatted`; ruff, mypy, `194 passed`, `145 passed`, `framework_check`, `render_prompts --check`, `check_renderings`, `render_indexes --check`, `generate_registry_md --check`, higiene de cache, `check_commit --range` (5 mensagens): todos exit 0; selftest `7 mutação(ões): todos os mutantes morreram` | suíte inteira | Sim |
| A10 | `diff -r -x __pycache__ <kit>/_framework _framework` no central; `cmp` dos arquivos de raiz; `git diff --name-only origin/main...HEAD` | `diff_exit=0`; arquivos de raiz iguais; 39 caminhos, os 33 de `_framework/` iguais aos do kit | sem teste automatizado (medição) | Sim |

### Achados da rodada 1, conferidos

1. **A02:** resolvido. `test_report_json.py:240-245` roda os cinco scripts
   como processo, em 12 casos (problema, `--report-only`, uso, OK), e compara
   stdout e código de saída com `fixtures/saida_texto_2_3_2.json`. A fixture
   corresponde à saída real do 2.3.2: os 12 casos rodados com os scripts de
   `279b10a` dão saída e código idênticos. As duas mutações que sobreviviam
   na rodada 1 agora reprovam (5 e 1 falhas).
2. **`executor_contract`:** resolvido. Chaves `contract_version`,
   `description`, `reads`, `machine_outputs`, `writes`, como no bloco da
   SPEC; `verification_output` e `exit_codes` removidos; o M4 não cita mais a
   chave removida (o YAML aponta o esquema da verificação só em comentário).
   `test_chaves_do_contrato_sao_as_da_spec` fixa isso, e o sensor o derruba.
3. **Esquema da verificação:** resolvido. `required` e `properties` são
   exatamente `status`, `causa`, `criterios`, `evidencias`, `descompassos`;
   `evidencias` é lista de strings sem padrão; o exemplo M4 não traz `sdd_id`
   e valida. `test_campos_da_verificacao_sao_os_da_spec` fixa isso.

### Descompassos encontrados (rodada 2)

Nenhum.

Escopo nas duas direções: os 42 arquivos de `git diff --name-only
origin/main` no kit (igual ao diff contra `279b10a`) aparecem na
decomposição em tasks ou são gerados por `render_prompts.py`; o único
arquivo novo desde a rodada 1, a fixture, entrou na task 1 da SDD no mesmo
commit da correção. No central, o diff de dois pontos contra o `main` atual
mostra também `docs/DTF/03-spec/SPEC-DTF-0028.md` e `docs/DTF/registry.yaml`
com `approved` → `in_review`: é só porque a PR #193 foi mergeada depois que
a branch do espelho saiu de `d812311`, não mudança da branch (o diff desde o
merge-base não os contém, e `git merge-tree` com o `main` não tem conflito).
Todo RF01 a RF08 tem código e teste.

Observações que não violam critério:

- Os valores de `writes` e o placeholder de `args` do `validate_doc.py`
  (`<documento>` em vez de `<arquivo>`) não são cópia literal do bloco da
  SPEC, que é ilustrativo; as chaves e a estrutura são as declaradas. O
  terceiro item de `writes` menciona também o `path` de SDD entregue, que é
  o `delivered` de RF06.
- O pré-requisito anotado na rodada 1 (PR #193 mergeada) está cumprido:
  `check_source_docs.py` contra o `main` do central sai com 0.
- O espelho no central ainda precisa da própria PR; os dois `E741` em
  `_framework/tests/test_procedures_structure.py` seguem pré-existentes e
  fora do lint do CI.

### Lições (rodada 2)

- Red flag: fixture "gravada na versão anterior" sem prova de que foi
  gravada lá. Rodar os mesmos casos contra o commit de base e comparar com a
  fixture custa um script; sem isso, uma fixture regravada com a saída nova
  passaria pelo mesmo teste.
- Red flag: diff de dois pontos contra um `main` que andou. Mudança de
  outra PR mergeada depois aparece invertida como se fosse da branch; o
  escopo se confere desde o merge-base.

---

## Rodada 1

- **Veredito da rodada 1:** FAIL

- **Causa:** implementacao
- **Diff verificado:** `279b10a..221d77f` no kit (branch `sdd/SDD-DTF-0053-contrato-do-executor`); espelho no central em `a8e54d3` (branch `sdd/SDD-DTF-0053-espelho`), contra `origin/main` do central
- **Rodada:** 1
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0053.md <worktree docs/spec-dtf-0028-approved>/docs/DTF`; leitura de SPEC-DTF-0028 e ADR-DTF-0008 contra a SDD | exit 0 contra a SPEC aprovada (exit 1 contra o central sem a PR #193: SPEC ainda `in_review`, ambiente); RF01 a RF08 representados, critérios EARS iguais, assinaturas iguais | sem teste automatizado (leitura) | Sim |
| A01 (RF01, RF02) | `pytest _framework/scripts/tests/test_report_json.py -q`, ANTES em `279b10a` com o teste copiado | ANTES `ImportError ... json_flag`, 1 error; DEPOIS `13 passed` | ver A05 | Sim |
| A02 (RF01) | 27 chamadas sem `--json` dos cinco scripts com o código de `279b10a` e do head, mesmas entradas e cwd; `diff`; mutações do texto em cópia descartável + pytest de A01 | stdout idêntico, 14 exit 0 e 13 exit 1 nos dois lados; as duas mutações (texto de uso, mensagem de OK do `validate_state.py`) deixam o pytest em `13 passed` | 2 de 2 mutações sobreviveram | Não |
| A03 (RF03, RF04, RF05, RF07) | `pytest _framework/tests/test_executor_contract.py -q`, ANTES em `279b10a` com o teste copiado | ANTES `7 failed`; DEPOIS `7 passed` | ver A04 | Sim |
| A04 (RF05) | `sizing` renomeado; primeiro `schema` de `machine_outputs` trocado por caminho inexistente; pytest de A03 | `1 failed, 6 passed`; `2 failed, 5 passed`; restaurado `7 passed` | derrubadas | Sim |
| A05 (RF02) | `_item` devolvendo sempre `documento: None`; pytest de A01 | `3 failed, 10 passed`; restaurado `13 passed` | derrubada | Sim |
| A06 (RF06) | `pytest _framework/scripts/tests/test_registry_entrega.py -q`, ANTES em `279b10a` com o teste copiado | ANTES `2 failed, 2 passed`; DEPOIS `4 passed` | o antes derruba os dois testes de impressão | Sim |
| A07 (RF08) | `grep -n 'version: "2.4.0"'`; `framework_check.py --auto` no central (espelho) | linhas 17 e 20; `134 documento(s) ok`, `exit=0`; central de `origin/main` dá o mesmo resultado sob 2.3.2 e sob 2.4.0 | sem teste automatizado (medição) | Sim |
| A08 | `render_prompts.py --check; echo exit=$?` | `exit=0` | sem teste automatizado (medição) | Sim |
| A09 | `pytest -q`; `ruff format --check` nos 19 `.py` do diff; passos do CI; `selftest.py` | `324 passed`; `19 files already formatted`; ruff, mypy, `181 passed`, `143 passed`, `framework_check`, `check_renderings`, `render_indexes --check`, `generate_registry_md --check`, `check_commit --range`: todos exit 0; selftest `7 mutação(ões): todos os mutantes morreram` | suíte inteira | Sim |
| A10 | `diff -r -x __pycache__ <kit>/_framework _framework` no central; `cmp` dos arquivos de raiz | `diff_exit=0`; arquivos de raiz iguais | sem teste automatizado (medição) | Sim |

### Descompassos encontrados (rodada 1)

1. **A02 sem a parte automatizada declarada (bloqueante).** A SDD diz que "o
   teste de A01 compara stdout e código de saída sem `--json` com os de
   `origin/main`, nos cinco scripts", com perfil `automatizado`; a SPEC pede
   a comparação "contra fixture gravada". `test_report_json.py` só compara o
   texto de `report()` (linha 82) e os códigos de saída dos cinco scripts.
   Prova: em cópia descartável, trocar o texto de uso impresso por
   `usage_error` e, noutra rodada, a mensagem de OK do `validate_state.py`
   deixa o pytest de A01 em `13 passed`. O comportamento hoje está certo
   (comparação manual de 27 chamadas: stdout idêntico), mas nada impede uma
   regressão futura, que é o risco que a SPEC nomeia.
2. **`executor_contract` diverge do formato da SPEC (bloqueante).** A SDD
   diz que o formato da chave está na SPEC e "é lei: não inventar campo".
   O YAML acrescenta `verification_output` (procedimento, modelo, esquema do
   M4) e `exit_codes`, que a SPEC não declara, e não tem `description`, que
   o bloco da SPEC traz (virou comentário). O M4 do `verify-sdd.md` cita
   `executor_contract.verification_output`, então a chave inventada já é
   referência normativa.
3. **`resultado-verificacao.schema.json` vai além da SPEC (bloqueante pela
   mesma regra).** Exige `sdd_id`, campo que a SPEC não lista (os campos
   são `status`, `causa`, `criterios`, `evidencias`, `descompassos`) e que
   não aparece em RFC-DTF-0009, ADR-DTF-0008 nem SPEC-DTF-0028; e restringe
   `evidencias` ao padrão `^.+:[0-9]+ — .+$`, também não descrito. O
   exemplo M4 carrega `sdd_id`.

Dois caminhos, escolha do humano: (a) emendar a SDD (e, se for o caso, a
SPEC) para declarar `verification_output`, `exit_codes`, `sdd_id` e o
padrão de `evidencias`, e aceitar `description` como comentário; ou (b)
remover do código o que a SPEC não declara e pôr `description` no YAML.
Em qualquer dos dois, o item 1 exige o teste que falta (stdout dos cinco
scripts contra fixture gravada ou contra a saída de `279b10a`).

Observações que não violam critério:

- As emendas de escopo se justificam: `requirements.txt` (task 4) leva o
  `jsonschema` que os testes importam, sem entrar nos scripts;
  `ci_gate_verify_sdd.py` (task 6) emitia texto com `--json` quando a PR não
  toca SDD, o que contraria RF01/RF05, e a mudança é só esse ramo;
  `kit-index.yaml` (tasks 6 e 8) registra os arquivos novos e o resumo da
  §20 do mapa; `test_procedures_structure.py` (task 7) tira do confronto só
  o bloco M4 e a frase que o cita, sem afrouxar o resto;
  `test_render_indexes.py` (task 8) passa de 22 para 23 seções, por causa da §20.
- `run_main` e `usage_error` em `framework_lib.py` não estão nomeados na
  SDD, mas implementam o tratamento de erro da SPEC (uso inválido e erro
  operacional viram problema no JSON, com exit 1, sem traceback no stdout).
  Conferido: `check_commit.py --range nao..existe --json` devolve JSON com
  `erro operacional: CalledProcessError ...`, exit 1.
- A SDD não copiou a tabela de casos de borda da SPEC; a implementação e os
  testes cobrem todos (report-only, sem argumentos, id no meio, erro
  operacional, `entrega` ausente ou incompleta, SDD em `arquivo/`).
- `delivered_note` e `optional_entry_fields_note` seguem a convenção
  `*_note` que o YAML já usa, fora de `executor_contract`.
- `ruff check` acusa dois E741 em `_framework/tests/test_procedures_structure.py:49,55`,
  pré-existentes em `279b10a` e fora do que o CI lint (`_framework/scripts`).
- Para `implemented`, a PR #193 do central (SPEC-DTF-0028 `approved`) tem de
  estar mergeada: contra o `main` de hoje, `check_source_docs.py` sai com 1.

### Lições (rodada 1)

- Red flag: critério de "saída igual à de antes" com perfil automatizado,
  verificado só por um teste unitário da função comum. Se o texto sai também
  de `main()` (uso, mensagem de OK), o teste tem de rodar o processo e
  comparar com fixture gravada; sem isso, a mutação do texto sobrevive.
- Red flag: SDD que diz "o formato está na SPEC e é lei" e implementação
  que acrescenta chave "útil" ao contrato publicado. Num contrato que só
  quebra em versão maior, todo campo a mais vira promessa; a emenda tem de
  vir antes, na SDD.
