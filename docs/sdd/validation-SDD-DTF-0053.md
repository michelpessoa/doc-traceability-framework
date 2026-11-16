# Verificação — SDD-DTF-0053

- **Veredito:** FAIL
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

## Descompassos encontrados

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

## Lições

- Red flag: critério de "saída igual à de antes" com perfil automatizado,
  verificado só por um teste unitário da função comum. Se o texto sai também
  de `main()` (uso, mensagem de OK), o teste tem de rodar o processo e
  comparar com fixture gravada; sem isso, a mutação do texto sobrevive.
- Red flag: SDD que diz "o formato está na SPEC e é lei" e implementação
  que acrescenta chave "útil" ao contrato publicado. Num contrato que só
  quebra em versão maior, todo campo a mais vira promessa; a emenda tem de
  vir antes, na SDD.
