---
id: SDD-DTF-0053
type: SDD
title: "Contrato do executor: executor_contract no YAML, --json nos validadores, esquemas publicados, SDD entregue e modelo M4"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-16"
updated: "2026-11-16"
relates_to: [SDD-DTF-0052]
source_docs:
  - id: "SPEC-DTF-0028"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0028.md"
  - id: "ADR-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0008.md"
sizing: "large"
consumption_instructions: "Compilada da SPEC-DTF-0028 (approved) e da ADR-DTF-0008 (approved). Os requisitos e critérios abaixo são os da SPEC; os esquemas JSON e o formato da chave executor_contract estão em 'Contratos técnicos' da SPEC e são lei: não inventar campo. Teste primeiro, visto falhar. A saída sem --json não pode mudar um caractere. Gerados (cópias da skill, índices, AGENTS.md, CHANGELOG.md, mapa do YAML) só por render_prompts.py. O central espelha por branch e PR próprios."
supersedes: null
superseded_by: null
tags: [integracao, executor, contrato, json, schema]
---

# Contrato do executor: executor_contract no YAML, --json nos validadores, esquemas publicados, SDD entregue e modelo M4

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar.

## Resumo executivo

Fase 1 da RFC-DTF-0009. Um executor passa a depender do framework só pelo
que a chave `executor_contract` do `workflow-rules.yaml` declara. Os cinco
validadores ganham `--json` com um esquema único; os esquemas de todas as
saídas de máquina ficam em `_framework/schemas/`; um teste de contrato
reprova o CI quando algo declarado quebra. A SDD entregue ganha local
(`docs/sdd/arquivo/`) e o registry ganha o campo opcional `entrega`. O
`verify-sdd` ganha o modelo M4 em JSON, com `causa`. Versão 2.4.0, sem
regra nova para documento.

## Decisão(ões) de arquitetura aplicável(is)

ADR-DTF-0008, itens 1, 2 e 6: kit sem citar executor específico;
`executor_contract` versionado, com quebra só em versão maior; mudança não
retroativa. Os itens 3 a 5 (aprovação como dado, review, escrita por PR)
são da fase 2 e não entram aqui.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | `validate_doc.py`, `validate_state.py`, `check_source_docs.py`, `registry_tools.py validate` e `check_commit.py` aceitam `--json` | Quando chamado com `--json`, o script deve escrever no stdout só um objeto JSON válido contra `_framework/schemas/resultado-validador.schema.json`, com o mesmo código de saída da execução sem `--json` |
| RF02 | Problema e aviso separados, com o documento identificado | Quando uma mensagem começar por um id do framework seguido de `:`, o objeto deve trazer esse id em `documento`; senão, `documento` deve ser `null` |
| RF03 | Esquemas publicados | O sistema deve ter em `_framework/schemas/` um JSON Schema 2020-12 para o resultado dos validadores, para o `--json` de `ci_gate_verify_sdd.py`, para o `--json` de `parallel_plan.py` e para o resultado da verificação |
| RF04 | Contrato declarado no YAML | O `workflow-rules.yaml` deve ter `executor_contract` com `contract_version`, `reads`, `machine_outputs` e `writes`, e cada chave de `reads` deve existir como chave de topo do YAML |
| RF05 | Teste de contrato | Se um script de `machine_outputs` sumir, recusar o argumento declarado ou produzir saída inválida contra o esquema, ou se uma chave de `reads` sumir, então `_framework/tests/test_executor_contract.py` deve falhar |
| RF06 | SDD entregue e `entrega` | `repository_topology.project_repo.delivered` deve ser `docs/sdd/arquivo/`, `registry.optional_entry_fields` deve conter `entrega`, e `registry_tools.py trace <id>` deve imprimir a entrega quando existir |
| RF07 | Modelo M4 | O `verify-sdd` deve ter o modelo M4, opcional, cujo exemplo valida contra `resultado-verificacao.schema.json`, com `causa` em `implementacao`, `especificacao`, `ambiente` ou `null` quando aprovado; M1 a M3 continuam iguais |
| RF08 | Versão 2.4.0 sem regra nova | `framework.version` deve ser `2.4.0`, com entrada no changelog, e o `framework_check.py --auto` do central deve continuar verde |

## Especificação técnica consolidada

Contratos completos na SPEC-DTF-0028, seção "Contratos técnicos". Resumo do
que a implementação precisa acertar:

- **`framework_lib.py`:** `json_flag(argv: list[str]) -> tuple[list[str], bool]`
  e `report(problems, warnings, ok_message, report_only=False, *, as_json=False, script="") -> int`.
  Com `as_json`, imprime só o objeto `{"schema": "dtf.resultado-validador/1",
  "script", "framework_version", "ok", "exit_code", "problemas", "avisos"}`,
  cada item de `problemas` e `avisos` como `{"documento": str|null,
  "mensagem": str}`. `documento` vem de `ID_PATTERN` ancorado no começo da
  mensagem e seguido de `:`. A versão vem de `load_rules()`.
- **Os cinco `main()`:** chamam `json_flag(sys.argv[1:])` antes do resto e
  repassam `as_json` e o nome do script a `report`. Com `--json`, o texto de
  uso que hoje sai por `print(__doc__)` vira um problema no JSON, com o
  mesmo código de saída. `registry_tools.py` só aceita `--json` em
  `validate`.
- **Esquemas em `_framework/schemas/`:** `resultado-validador.schema.json`,
  `ci-gate-verify-sdd.schema.json` (forma de `GateResult.to_dict()`),
  `parallel-plan.schema.json` (`parallel_groups`, `blocked_pairs` com `a`,
  `b`, `files`) e `resultado-verificacao.schema.json` (`status`, `causa`,
  `criterios`, `evidencias`, `descompassos`, campos de `criterios` como na
  SPEC).
- **YAML:** chave de topo `executor_contract` (formato da SPEC; `reads`
  com `sizing`, `decision_gates`, `status_lifecycle`,
  `repository_topology`, `frontmatter_schema`, `registry`; uma entrada de
  `machine_outputs` por script, sete no total); `delivered` em
  `repository_topology.project_repo`; `optional_entry_fields: ["entrega"]`
  em `registry`; `framework.version: "2.4.0"`, `last_updated`, entrada no
  `changelog`.
- **`registry_tools.py trace`:** depois da linha de cada documento, se a
  entrada tiver `entrega`, imprime `entrega: PR #<pr>, <data>, <resultado>`
  com o que existir.
- **`_framework/procedures/verify-sdd.md`:** modelo M4 em "Modelos de
  registro", com um exemplo JSON completo de aprovado e a regra da `causa`.
- **Gerados:** cópias da skill, `references/workflow-rules.yaml` da skill,
  `AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, o
  mapa do YAML e os índices, todos por `render_prompts.py`.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes de `report`/`json_flag` e dos cinco scripts, incluindo a saída sem `--json` igual à de antes, vistos falhar | RF01, RF02 | `_framework/scripts/tests/test_report_json.py` | |
| 2 | `json_flag` e `report` com JSON | RF01, RF02 | `_framework/scripts/framework_lib.py` | 1 |
| 3 | `--json` nos cinco `main()` | RF01 | `_framework/scripts/validate_doc.py`, `_framework/scripts/validate_state.py`, `_framework/scripts/check_source_docs.py`, `_framework/scripts/registry_tools.py`, `_framework/scripts/check_commit.py` | 2 |
| 4 | Os quatro esquemas e `jsonschema` como dependência de teste | RF03 | `_framework/schemas/resultado-validador.schema.json`, `_framework/schemas/ci-gate-verify-sdd.schema.json`, `_framework/schemas/parallel-plan.schema.json`, `_framework/schemas/resultado-verificacao.schema.json`, `requirements.txt` | 2 |
| 5 | Teste de `trace` com e sem `entrega`, visto falhar; `trace` imprime a entrega | RF06 | `_framework/scripts/tests/test_registry_entrega.py`, `_framework/scripts/registry_tools.py` | 3 |
| 6 | Teste de contrato, visto falhar; `executor_contract`, `delivered`, `optional_entry_fields`, 2.4.0 e changelog; `ci_gate_verify_sdd.py --json` passa a emitir JSON também quando a PR não toca SDD (hoje emite texto, o que o teste de contrato pegou) | RF04, RF05, RF06, RF08 | `_framework/tests/test_executor_contract.py`, `_framework/rules/workflow-rules.yaml`, `_framework/rules/kit-index.yaml`, `_framework/scripts/ci_gate_verify_sdd.py` | 4 |
| 7 | Modelo M4 e o teste do exemplo; o teste que guarda a reordenação do procedimento passa a ignorar o bloco do M4 | RF07 | `_framework/procedures/verify-sdd.md`, `_framework/tests/test_executor_contract.py`, `_framework/tests/test_procedures_structure.py` | 6 |
| 8 | Manifesto e gerados; o teste do mapa passa a contar 23 seções | RF04 | `_framework/rules/kit-index.yaml`, `_framework/tests/test_render_indexes.py`, gerados por `render_prompts.py` | 7 |
| 9 | Espelho no central, branch e PR próprios | RF01 a RF08 | `central:_framework/`, mesmos caminhos | 8 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01, RF02: testes de `report` e dos scripts | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q` | ANTES da task 2: falha; DEPOIS: todos passam | automatizado |
| A02 | RF01: saída sem `--json` igual | O teste de A01 compara stdout e código de saída sem `--json` com os de `origin/main`, nos cinco scripts | Igual, caractere por caractere | automatizado |
| A03 | RF03, RF04, RF05, RF07: contrato | `python3 -m pytest _framework/tests/test_executor_contract.py -q` | ANTES da task 6: falha; DEPOIS: todos passam | automatizado |
| A04 | RF05: sensor do contrato | Em cópia descartável: renomear a chave de topo `sizing` do YAML; noutra rodada, trocar o `schema` de uma entrada de `machine_outputs` por um caminho inexistente; rodar o pytest de A03 a cada vez; restaurar | Pelo menos 1 failed em cada mutação; restaurado, 0 failed | automatizado |
| A05 | RF02: sensor do `documento` | Em cópia descartável, fazer `report` gravar sempre `documento: null`; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A06 | RF06: `trace` e `entrega` | `python3 -m pytest _framework/scripts/tests/test_registry_entrega.py -q` | ANTES da task 5: falha; DEPOIS: todos passam | automatizado |
| A07 | RF08: versão e central | `grep -n 'version: "2.4.0"' _framework/rules/workflow-rules.yaml`; no central, com `_framework/` desta branch: `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | A linha da versão; `exit=0` | automatizado |
| A08 | Gerados em dia | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `exit=0` | automatizado |
| A09 | Suíte e formatação | `python3 -m pytest -q; ruff format --check` nos arquivos tocados | 0 failed; arquivos tocados formatados | automatizado |
| A10 | Espelho | No central: `diff -r <kit>/_framework _framework` | Sem diferença | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0053-contrato-do-executor`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0053`. Nunca em `main`.
- **Teste primeiro** em cada task, com a falha guardada.
- **Não mudar** o texto de nenhuma mensagem dos validadores, nenhum gate,
  sizing, ciclo de status ou campo de front-matter obrigatório.
- **`jsonschema` só nos testes.** Os scripts continuam com biblioteca
  padrão e `pyyaml`.
- **Sem citar executor específico** no kit (ADR-DTF-0008, item 1).
- **Gerados só por script.** Nunca editar à mão as cópias da skill, os
  índices, `AGENTS.md`, `CHANGELOG.md` nem o mapa.
- **Evidência de verificação** só por verificador independente.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF08) tem código
      correspondente.
- [x] Todo arquivo tocado aparece na "Decomposição em tasks" ou é gerado
      por `render_prompts.py`.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado. (Não confirmado:
      `executor_contract` ganhou `verification_output` e `exit_codes`,
      que a SPEC não declara, e perdeu `description`, que ela declara;
      `resultado-verificacao.schema.json` exige `sdd_id`, que a SPEC não
      lista. Ver `validation-SDD-DTF-0053.md`.)

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 1: todas as linhas abaixo foram rodadas nesta sessão, no kit na
branch `sdd/SDD-DTF-0053-contrato-do-executor` (head `221d77f`), com base
fixa `279b10a` (`origin/main` = merge-base no momento da verificação), e no
central na branch `sdd/SDD-DTF-0053-espelho` (head `a8e54d3`). Os "antes"
de A01, A03 e A06 rodaram em worktree descartável de `279b10a` com os
testes novos (e o esquema que eles importam) copiados por cima; os
sensores A04 e A05 rodaram numa cópia descartável do head, nunca no
checkout. A SPEC-DTF-0028 foi lida no worktree descartável da branch
`docs/spec-dtf-0028-approved` do central (PR #193 ainda não mergeada).

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0053.md`.
Veredito: **FAIL** (causa `implementacao`): A02 não tem a parte
automatizada que a SDD declara, e `executor_contract` e o esquema da
verificação divergem do contrato da SPEC, que a SDD manda seguir sem
inventar campo.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0053.md <central-spec>/docs/DTF` (worktree de `docs/spec-dtf-0028-approved`); idem contra o central na branch do espelho; leitura de SPEC-DTF-0028 e ADR-DTF-0008 contra a SDD | Worktree da SPEC aprovada: `✅ source_docs de SDD-DTF-0053.md conferem com o registry central.`, exit 0. Contra o central sem a PR #193: `SDD-DTF-0053: source_docs 'SPEC-DTF-0028' está com status 'in_review'`, exit 1 (ambiente: PR pendente). RF01 a RF08 todos representados; nenhum critério EARS afrouxado (RF08 da SDD, "central continua verde", conferido também como na SPEC: central de `origin/main` com 2.3.2 e com 2.4.0 dão o mesmo resultado, exit 0 nos dois); assinaturas de `report`/`json_flag` iguais às da SPEC; a lista `reads` segue a SPEC (a ADR citava `approval_policy`, que é fase 2). Casos de borda da SPEC não foram copiados para a SDD, que aponta para a SPEC | sem teste automatizado (leitura e comando de medição) | Sim | `_framework/scripts/check_source_docs.py:96` | manual (passo 0, itens 2 a 4, é leitura, ADR-DTF-0007) |
| 1 | A01 | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q`, ANTES em worktree de `279b10a` com o teste copiado; DEPOIS no head | ANTES: `ImportError: cannot import name 'json_flag' from 'framework_lib'`, `1 error during collection`. DEPOIS: `13 passed in 3.67s` | Ver A05 | Sim | `_framework/scripts/tests/test_report_json.py:54`, `_framework/scripts/tests/test_report_json.py:103` | automatizado |
| 1 | A02 | Script em `scratchpad/a02.sh`: 27 chamadas sem `--json` dos cinco scripts (sem argumentos, documentos reais do kit e do central, `--report-only`, `--require-refs`, `--range`, caminhos inexistentes), rodadas com o código de `279b10a` e com o do head, mesmo cwd e mesmas entradas; `diff` do stdout e dos `exit=`. Sensor: em cópia descartável, `usage_error` passou a imprimir `USO ALTERADO` e, noutra rodada, a mensagem de OK do `validate_state.py` mudou; pytest de A01 | stdout das 27 chamadas idêntico (`STDOUT_IDENTICO`, 200 linhas cada lado), códigos iguais (14 exit 0, 13 exit 1); stderr só difere no traceback do `--range` com git falhando (um quadro a mais, `run_main`). Sensor: as duas mutações deixam o pytest de A01 em `13 passed`: o teste não compara a saída dos cinco scripts com a de `origin/main` nem com fixture gravada, só o `report()` (linha 82) e os códigos de saída | Mutações NÃO derrubadas (2 de 2 sobreviveram) | Não | `_framework/scripts/tests/test_report_json.py:82` (cobre só `report()`, não os cinco `main()`) | manual (o perfil esperado era automatizado; a comparação automatizada dos cinco scripts não existe) |
| 1 | A03 | `python3 -m pytest _framework/tests/test_executor_contract.py -q`, ANTES em worktree de `279b10a` com o teste copiado; DEPOIS no head | ANTES: `7 failed in 0.65s`. DEPOIS: `7 passed in 2.00s` | Ver A04 | Sim | `_framework/tests/test_executor_contract.py:83`, `_framework/tests/test_executor_contract.py:118`, `_framework/tests/test_executor_contract.py:128` | automatizado |
| 1 | A04 | Cópia descartável do head: `sed 's/^sizing:$/sizing_renomeado:/'` no YAML; noutra rodada, o primeiro `schema:` de `machine_outputs` trocado por `_framework/schemas/nao-existe.schema.json`; pytest de A03 a cada vez; restaurado do backup | `sizing` renomeado: `1 failed, 6 passed` (`test_reads_existem_no_yaml`). Esquema inexistente: `2 failed, 5 passed` (`test_esquemas_declarados_existem_e_sao_validos`, `test_saidas_declaradas_validam_contra_o_esquema`). Restaurado: `7 passed` | Mutações derrubadas | Sim | `_framework/tests/test_executor_contract.py:83`, `_framework/tests/test_executor_contract.py:89` | automatizado |
| 1 | A05 | Cópia descartável do head: `_item` passa a devolver sempre `{"documento": None, ...}` em `framework_lib.py`; pytest de A01; restaurado | Com a mutação: `3 failed, 10 passed` (`test_report_json_com_problema`, `test_validate_doc_json`, `test_registry_tools_validate_json`). Restaurado: `13 passed` | Mutação derrubada | Sim | `_framework/scripts/tests/test_report_json.py:54`, `_framework/scripts/tests/test_report_json.py:150` | automatizado |
| 1 | A06 | `python3 -m pytest _framework/scripts/tests/test_registry_entrega.py -q`, ANTES em worktree de `279b10a` com o teste copiado; DEPOIS no head | ANTES: `2 failed, 2 passed` (os dois testes que exigem a linha `entrega:` falham). DEPOIS: `4 passed in 0.54s` | O "antes" derruba os dois testes de impressão; os dois que passam no antes (sem entrega, validate com `arquivo/`) são guardas de não regressão | Sim | `_framework/scripts/tests/test_registry_entrega.py:31`, `_framework/scripts/tests/test_registry_entrega.py:51` | automatizado |
| 1 | A07 | `grep -n 'version: "2.4.0"' _framework/rules/workflow-rules.yaml`; no central (branch do espelho): `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `17:  version: "2.4.0"` e `20:    - version: "2.4.0"`; central: `✅ 134 documento(s) ok.`, `✅ Todas as verificações do framework passaram.`, `exit=0`, nenhum `❌` | sem teste automatizado (comando de medição) | Sim | `_framework/rules/workflow-rules.yaml:17` | automatizado |
| 1 | A08 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `✅ _framework/INDEX.md: em dia.`, `✅ docs/sdd/INDEX.md: em dia.` (mais o aviso pré-existente de 30 SDDs sem seção de arquivos); `exit=0` | sem teste automatizado (comando de medição) | Sim | n/a (comando de medição, sem asserção em teste) | automatizado |
| 1 | A09 | `python3 -m pytest -q`; `ruff format --check` nos 19 `.py` do diff; o que o CI roda: `ruff check`/`ruff format --check`/`mypy` em `_framework/scripts`, as duas suítes, `framework_check.py --auto`, `check_renderings.py`, `render_indexes.py sdd docs/sdd --check`, `generate_registry_md.py docs/sdd --check`, `check_commit.py --range origin/main..HEAD`; `_framework/scripts/selftest.py` | `324 passed in 44.02s`; `19 files already formatted`; `All checks passed!`; `Success: no issues found in 35 source files`; `35 files already formatted`; `181 passed`; `143 passed`; `Todas as verificações do framework passaram`; `5 renderização(ões) concordam`; `docs/sdd/INDEX.md: em dia`; `docs/sdd/registry.md: em dia`; `3 mensagem(ns) de commit no formato esperado`; `7 mutação(ões): todos os mutantes morreram`; todos exit 0 | Suíte inteira; sensores próprios em A02, A04 e A05 | Sim | `_framework/tests/test_executor_contract.py:118` | automatizado |
| 1 | A10 | No central: `diff -r -x __pycache__ <kit>/_framework _framework; echo diff_exit=$?`; `cmp` de `AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, `requirements.txt` | `diff_exit=0` (sem `-x`, só diferem `.pyc` de cache, não versionados); os cinco arquivos iguais; diff do central contra `origin/main` = os mesmos caminhos do kit fora de `docs/sdd/`, mais `docs/DTF/registry.md` regerado (cabeçalho v2.4.0) | sem teste automatizado (comando de medição) | Sim | n/a (comando de medição, sem asserção em teste) | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0028, ADR-DTF-0008 |
| relates_to | SDD-DTF-0052 (resolveu a proposta 003 antes desta frente) |
| Gate RFC → ADR | RFC-DTF-0009 exigiu ADR; ADR-DTF-0008 aprovada |
