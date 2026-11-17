---
id: SDD-DTF-0055
type: SDD
title: "Aprovação por review no kit: review_approval.py, approvers no registry central e actor conferido no validate_state"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-17"
updated: "2026-11-17"
relates_to: [SDD-DTF-0054]
source_docs:
  - id: "SPEC-DTF-0030"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0030.md"
  - id: "ADR-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0008.md"
sizing: "large"
consumption_instructions: "Compilada da SPEC-DTF-0030 (approved), só a parte do kit: RF01 a RF07. Os RF08 a RF13 são da fábrica e ficam numa SDD-FAB própria. O formato de approvers, a regra da review válida, a CLI e o JSON de review_approval.py e as linhas do executor_contract estão em 'Especificação técnica consolidada' e são lei: não inventar campo, chave ou mensagem nova. Teste primeiro, visto falhar. A saída em texto dos validadores não muda para projeto sem approvers. Gerados só por render_prompts.py. O central espelha por branch e PR próprios."
supersedes: null
superseded_by: null
tags: [integracao, executor, aprovacao, review, approvers, approved_by]
---

# Aprovação por review no kit: review_approval.py, approvers no registry central e actor conferido no validate_state

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar.

## Resumo executivo

Parte do kit da SPEC-DTF-0030, a primeira SPEC da fase 4 da RFC-DTF-0009.
A SPEC-DTF-0029 tornou a aprovação um dado, mas ninguém confere a review
que dá origem ao `approved_by` humano. Esta SDD entrega três peças:

- o script `review_approval.py`, que decide sem rede se as reviews de uma
  PR aprovam o documento e monta o `approved_by`;
- o campo `approvers` no registry central, a lista de logins que podem
  aprovar, validado pelo `registry_tools.py`;
- a conferência do `actor` contra essa lista no `validate_state.py`.

O `executor_contract` só ganha entradas e a versão vai para 2.6.0.
Projeto sem `approvers` não muda de comportamento.

## Decisão(ões) de arquitetura aplicável(is)

Da ADR-DTF-0008, valem os itens 3 e 5: a aprovação humana se faz por
review de PR, e o executor escreve no central só por PR. Os itens 1, 2 e
6 também valem: o kit não cita executor, o contrato é versionado e nada
é retroativo. `contract_version` fica 1. A decisão de desenho da SPEC
também é lei: o kit decide quais reviews aprovam, e o executor só busca
as reviews e age conforme a saída.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | O registry central declara quem aprova | O sistema deve aceitar no topo de `docs/{PROJECT_CODE}/registry.yaml` o campo opcional `approvers`, uma lista não vazia de logins do GitHub (texto sem espaço), declarado em `registry.central_registry` do `workflow-rules.yaml`; `registry_tools.py validate` deve reprovar `approvers` que não seja lista de textos não vazios e sem espaço |
| RF02 | O `actor` humano é um aprovador declarado | Se um documento em `approved`, `implemented` ou `superseded` tiver `approved_by.kind: human` e o registry central do projeto declarar `approvers` sem o `approved_by.actor`, então `validate_state.py` deve reprovar nomeando o documento, o `actor` e a lista; sem `approvers` declarado, nada muda em relação à 2.5.0 |
| RF03 | A decisão sobre as reviews é mecânica e sem rede | Quando chamado como `review_approval.py <documento> --reviews <arquivo> --head <sha> --pr-url <url> [--json]`, o sistema deve decidir pela regra do RF04, sair com 0 quando a aprovação for válida e com 1 quando não for, e com `--json` imprimir um objeto válido contra `_framework/schemas/review-approval.schema.json` |
| RF04 | Regra da review válida | O sistema deve considerar só reviews de logins em `approvers`. Uma review aprova quando o estado é `APPROVED`, ou quando o estado é `COMMENTED` e o corpo, sem espaços nas pontas, é exatamente `Aprovado`. A review decisiva é a mais recente, por `submitted_at`, entre as que aprovam e as `CHANGES_REQUESTED`. A aprovação só vale se a review decisiva aprova e se o `commit_id` dela é o `--head` |
| RF05 | A aprovação válida já sai como `approved_by` | Quando a aprovação for válida, o sistema deve devolver `approved_by` com `kind: human`, o login do revisor em `actor`, o `submitted_at` da review em `at`, o `content_sha256` calculado por `approval_hash.content_hash` sobre o documento e `evidence` igual a `<pr-url>#pullrequestreview-<id da review>` |
| RF06 | O contrato do executor acompanha | O sistema deve declarar no `executor_contract`: em `machine_outputs`, `review_approval.py`; em `writes`, a PR de documento novo em `in_review` e, na mesma PR, `status: approved` com `approved_by` `kind: human`, só a partir de saída válida de `review_approval.py` e antes do merge. `contract_version` continua 1, porque só acrescenta |
| RF07 | Versão minor | O sistema deve declarar `framework.version` `2.6.0`, com entrada no changelog, e manter verde o `framework_check.py --auto` do central sem mudar nenhum documento existente |

Casos de borda da SPEC que a implementação e os testes cobrem (os da
fábrica ficam na SDD da fábrica):

| Caso | RF | Comportamento esperado |
|---|---|---|
| Nenhuma review | RF04 | Inválida: `nenhuma review de aprovador` |
| Review `APPROVED` de login fora de `approvers` | RF04 | Ignorada; sem outra, inválida |
| Review `COMMENTED` com corpo `aprovado`, `Aprovado.` ou `Aprovado, mas...` | RF04 | Não aprova: o corpo precisa ser exatamente `Aprovado`, sem espaços nas pontas |
| Aprovação seguida de `CHANGES_REQUESTED` do mesmo ou de outro aprovador | RF04 | Inválida: a decisiva é a `CHANGES_REQUESTED` |
| `CHANGES_REQUESTED` seguida de aprovação | RF04 | Válida, se a aprovação for sobre o head |
| Review `DISMISSED`, ou `COMMENTED` com outro texto | RF04 | Ignorada na escolha da decisiva |
| Aprovação sobre commit anterior ao head | RF04 | Inválida: `review sobre <commit_id>, head é <sha>: nova review necessária` |
| Registry central sem `approvers` | RF03 | `review_approval.py` sai com 1, `approvers não declarado no registry` |
| Documento não está em `in_review` | RF03 | Inválida, com o status encontrado |
| Arquivo de reviews que não é lista JSON, ou item sem `id`, `user.login`, `state`, `commit_id` ou `submitted_at` | RF03 | Sai com 2 e nomeia o campo; não decide |
| `--pr-url` fora do formato `https://github.com/<dono>/<repo>/pull/<n>` | RF03, RF05 | Sai com 2 |
| Owner autor da própria PR | RF04 | A review `COMMENTED` com `Aprovado` vale igual |

Requisitos não funcionais: só biblioteca padrão e `pyyaml`;
`review_approval.py` não usa rede.

Fora de escopo, da SPEC e deste recorte: tudo o que é da fábrica (RF08 a
RF13: descoberta, `EscritaNoCentral`, `fabrica central conferir`, login
do token); declarar `approvers` em registry de projeto real; vigia,
release dupla, organização; migrar documento existente.

## Especificação técnica consolidada

Contratos completos na SPEC-DTF-0030, seção "Contratos técnicos". O que a
implementação precisa acertar:

- **`approvers` no `workflow-rules.yaml`.** Em `registry.central_registry`,
  ao lado de `repository_field`, a chave nova `approvers_field`, com
  `field: "approvers"`, `level` (topo do arquivo, ao lado de `project` e
  `framework_version`), `description` (lista não vazia de logins do
  GitHub que podem aprovar por review os documentos do projeto;
  conferida por `review_approval.py` na hora e por `validate_state.py`
  depois; opcional; sem ela, `approved_by` humano não é conferido contra
  lista) e `since: "2.6.0"`. Exemplo da SPEC:

  ```yaml
  project: "ZERO"
  framework_version: "2.6.0"
  approvers: [michelpessoa]
  ```

- **`registry_tools.py`.** Função nova `check_approvers(data: dict) -> list[str]`,
  pura, chamada em `cmd_validate` só em `mode == "central"`, logo depois
  de `check_repository_state`. Sem a chave: `[]`. Com a chave e valor que
  não é lista não vazia de textos não vazios sem espaço (`str` e
  `not any(c.isspace() for c in v)`): um problema, exatamente
  `registry.yaml: \`approvers\` deve ser uma lista não vazia de logins do GitHub, sem espaço.`
  Nenhuma outra mensagem.
- **`_framework/scripts/review_approval.py`** (novo, só biblioteca padrão
  e `pyyaml`, via `framework_lib` e `approval_hash`):
  - `SCHEMA_ID = "dtf.review-approval/1"`.
  - `approvers_for(path: Path) -> list[str] | None`: sobe a árvore a
    partir do diretório do documento até o primeiro `registry.yaml`, como
    `framework_lib.project_version`, e devolve `approvers` quando for
    lista; senão `None`.
  - `approves(review: dict) -> bool`: `state == "APPROVED"`, ou
    `state == "COMMENTED"` e `(body or "").strip() == "Aprovado"`.
  - `decide(reviews: list[dict], head: str, approvers: list[str]) -> dict`
    devolve `{"valida": bool, "motivos": list[str], "review": dict | None}`:
    1. só reviews com `user.login` em `approvers`;
    2. delas, só as que aprovam (`approves`) ou têm
       `state == "CHANGES_REQUESTED"`; nenhuma →
       `nenhuma review de aprovador`;
    3. decisiva = a de maior `submitted_at` (comparação de texto ISO
       8601; empate, vale a que vem depois na lista);
    4. decisiva `CHANGES_REQUESTED` →
       `a review decisiva de <login> pede mudanças (<submitted_at>)`;
    5. decisiva com `commit_id != head` →
       `review sobre <commit_id>, head é <head>: nova review necessária`;
    6. senão, `valida: true`, `motivos: []`, `review` = a decisiva.
  - CLI, com `json_flag` para `--json` e `argparse` para o resto
    (posicional `documento`; `--reviews`, `--head` e `--pr-url`
    obrigatórios). Ordem: argumento faltando ou inválido → saída 2 (a do
    `argparse`); documento inexistente ou sem front-matter → saída 2 com
    o motivo; `--pr-url` que não casa
    `^https://github\.com/[^/\s]+/[^/\s]+/pull/[0-9]+$` → saída 2,
    `--pr-url fora do formato https://github.com/<dono>/<repo>/pull/<n>`;
    arquivo de reviews ilegível, que não é lista JSON, ou item sem `id`,
    `user.login`, `state`, `commit_id` ou `submitted_at` → saída 2
    nomeando o campo e o índice do item (`review 0 sem submitted_at`);
    `approvers_for` `None` → saída 1, `approvers não declarado no registry`;
    status do documento diferente de `in_review` → saída 1,
    `documento está <status>, não in_review`; senão `decide`, saída 0 se
    válida e 1 se não.
  - Saída sem `--json`: válida, o bloco `approved_by:` em YAML (o mesmo
    mapa do JSON), pronto para colar no front-matter; inválida ou saída
    2, cada motivo numa linha no stderr.
  - Saída com `--json`, em 0, 1 e 2 (exceto erro do próprio `argparse`):
    só o objeto abaixo no stdout. `documento` é o `id` do front-matter ou
    o nome do arquivo; `head` é o `--head` recebido; `approved_by` é
    `null` quando `valida` é `false`.

    ```json
    {
      "schema": "dtf.review-approval/1",
      "documento": "SPEC-ZERO-0001",
      "valida": true,
      "motivos": [],
      "head": "<sha>",
      "approved_by": {
        "kind": "human",
        "actor": "michelpessoa",
        "at": "2026-11-18T10:00:00Z",
        "content_sha256": "<64 hex>",
        "evidence": "https://github.com/<dono>/<repo>/pull/<n>#pullrequestreview-<id>"
      }
    }
    ```

- **`_framework/schemas/review-approval.schema.json`** (novo, JSON Schema
  2020-12, mesmo estilo de `approval-hash.schema.json`): objeto com
  exatamente `schema` (const `dtf.review-approval/1`), `documento`
  (string), `valida` (boolean), `motivos` (array de strings), `head`
  (string) e `approved_by`, todos obrigatórios,
  `additionalProperties: false`. `approved_by` é `null` ou objeto com
  exatamente `kind` (const `human`), `actor` (string), `at` (string),
  `content_sha256` (padrão `^[0-9a-f]{64}$`) e `evidence` (string), todos
  obrigatórios, `additionalProperties: false`.
- **`validate_state.check_approval`.** Depois da checagem de política e
  antes da do hash: quando `data["kind"] == "human"` e
  `review_approval.approvers_for(path)` devolve lista sem
  `data["actor"]`, acrescenta exatamente
  `<id>: approved_by.actor <actor> não está em approvers (<logins separados por ", ">) do registry central.`
  `approvers_for` `None`: nada. A assinatura e as outras mensagens não
  mudam. `framework_check.py` já chama `check_approval` e não muda.
- **`executor_contract`.** Em `machine_outputs`, depois de
  `approval_hash.py`:
  `{script: review_approval.py, args: ["<documento>", "--reviews", "<arquivo>", "--head", "<sha>", "--pr-url", "<url>", "--json"], schema: _framework/schemas/review-approval.schema.json}`.
  Em `writes`, depois das linhas existentes, exatamente:
  - `"PR de documento novo (SPEC, RFC) no central com status in_review, de branch docs/<id>."`
  - `"Na mesma PR, antes do merge: status approved e approved_by com kind: human, só com saída válida de review_approval.py sobre o head revisado."`

  `contract_version` fica 1; nenhuma outra chave muda.
- **Versão.** `framework.version: "2.6.0"`, `last_updated` e entrada nova
  no topo de `changelog`, com a data do dia da implementação.
- **Gerados.** Cópias da skill, `references/workflow-rules.yaml` da skill,
  `AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, o
  mapa do YAML e os índices, todos por `render_prompts.py`. O
  `kit-index.yaml` ganha `scripts/review_approval.py` e
  `scripts/tests/test_review_approval.py`.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes de `decide` (um caso por linha do RF04 nos casos de borda), da CLI (saídas 0, 1 e 2; JSON válido contra o esquema; `content_sha256` igual ao de `approval_hash.py`; texto sem `--json`) e de `check_approvers` (válido, vazio, não lista, com espaço, ausente), vistos falhar | RF01, RF03, RF04, RF05 | `_framework/scripts/tests/test_review_approval.py` | |
| 2 | `review_approval.py` e o esquema | RF03, RF04, RF05 | `_framework/scripts/review_approval.py`, `_framework/schemas/review-approval.schema.json` | 1 |
| 3 | `check_approvers` em `registry_tools.py` | RF01 | `_framework/scripts/registry_tools.py` | 1 |
| 4 | Testes do `actor` contra `approvers` (dentro passa, fora reprova com a mensagem, sem `approvers` não muda), vistos falhar; `check_approval` estendido | RF02 | `_framework/scripts/tests/test_approval.py`, `_framework/scripts/validate_state.py` | 2 |
| 5 | Teste de contrato com a saída nova, os marcadores `<arquivo>`, `<sha>` e `<url>` e as duas linhas de `writes`, visto falhar; `executor_contract`, `approvers_field`, 2.6.0 e changelog | RF01, RF06, RF07 | `_framework/tests/test_executor_contract.py`, `_framework/rules/workflow-rules.yaml` | 4 |
| 6 | Manifesto e gerados | RF06, RF07 | `_framework/rules/kit-index.yaml`, gerados por `render_prompts.py` | 5 |
| 7 | Espelho no central, branch e PR próprios | RF01 a RF07 | `central:_framework/`, mesmos caminhos | 6 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF03, RF04, RF05: decisão, CLI e esquema | `python3 -m pytest _framework/scripts/tests/test_review_approval.py -q -k "not approvers"` | ANTES da task 2: falha; DEPOIS: todos passam | automatizado |
| A02 | RF01: `approvers` validado | `python3 -m pytest _framework/scripts/tests/test_review_approval.py -q -k approvers` | ANTES da task 3: falha; DEPOIS: todos passam | automatizado |
| A03 | RF02: `actor` conferido | `python3 -m pytest _framework/scripts/tests/test_approval.py -q` | ANTES da task 4: falha; DEPOIS: todos passam | automatizado |
| A04 | RF04: sensor do head | Em cópia descartável, tirar o passo 5 de `decide`; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A05 | RF04: sensor do corpo exato | Em cópia descartável, trocar `== "Aprovado"` por `.lower().startswith("aprovado")`; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A06 | RF04: sensor da decisiva | Em cópia descartável, fazer `decide` ignorar `CHANGES_REQUESTED`; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A07 | RF02: sensor do `actor` | Em cópia descartável, tirar a conferência do `actor` de `check_approval`; rodar o pytest de A03; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A08 | RF06: contrato | `python3 -m pytest _framework/tests/test_executor_contract.py -q` | ANTES da task 5: falha; DEPOIS: todos passam | automatizado |
| A09 | Não funcional: saída em texto dos validadores | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` | Todos passam; diff vazio | automatizado |
| A10 | RF07: versão e central | `grep -n 'version: "2.6.0"' _framework/rules/workflow-rules.yaml`; no central, com `_framework/` desta branch: `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` e `git status --porcelain docs/` | A linha da versão; `exit=0`; nenhum documento alterado | automatizado |
| A11 | Gerados em dia | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `exit=0` | automatizado |
| A12 | Suíte e formatação | `python3 -m pytest -q`; `ruff format --check` e `ruff check` nos `.py` do diff; `python3 _framework/scripts/selftest.py` | 0 failed; formatados; sem erro; mutantes mortos | automatizado |
| A13 | Espelho | No central: `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | Sem diferença | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0055-review-approval`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0055`. Nunca em `main`.
- **Teste primeiro** em cada task, com a falha guardada.
- **Não acrescentar** chave, campo ou mensagem que esta SDD não declara
  (lição da rodada 1 da SDD-DTF-0053). `executor_contract` continua com
  exatamente `contract_version`, `description`, `reads`,
  `machine_outputs` e `writes`.
- **Não mudar** mensagem existente dos validadores, gate, sizing, ciclo
  de status, template, campo obrigatório do front-matter nem a política.
- **Não declarar** `approvers` em nenhum registry do kit nem do central
  real, e não migrar documento.
- **Sem citar executor específico** no kit (ADR-DTF-0008, item 1).
- **Gerados só por script.**
- **Evidência de verificação** só por verificador independente.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF07) tem código
      correspondente.
- [x] Todo arquivo tocado aparece na "Decomposição em tasks" ou é gerado
      por `render_prompts.py`.
- [x] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 1: todas as linhas abaixo foram rodadas nesta sessão, no kit na
branch `sdd/SDD-DTF-0055-review-approval` (head `96969e6`), com base fixa
`012ff47` (= `origin/main`), e no central na branch
`sdd/SDD-DTF-0055-espelho` (head `0f4f842`). Os "antes" de A01, A02, A03 e
A08 rodaram numa cópia descartável de `012ff47` (`git archive`) com os
testes novos copiados por cima. Os sensores mutaram o arquivo da worktree
com cópia guardada no scratchpad e restauraram por ela; `git status
--porcelain` vazio depois de cada um.

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0055.md`. Veredito: **PASS**.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0055.md /home/user/doc-traceability-central/docs/DTF; echo "exit=$?"`; leitura da SPEC-DTF-0030 (approved) do `main` do central (`5c5cee5`) | `✅ source_docs de SDD-DTF-0055.md conferem com o registry central.` `exit=0`; RF01 a RF07 com texto e EARS idênticos aos da SPEC; os 12 casos de borda do kit e os requisitos não funcionais iguais; formato de `approvers`, `decide`, `approvers_for`, CLI, JSON, esquema, mensagem de `check_approval` e linhas do `executor_contract` iguais aos da Parte 2, só detalhados; RF08 a RF13 declaradamente fora (fábrica) | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 1 | A01 | `python3 -m pytest _framework/scripts/tests/test_review_approval.py -q -k "not approvers"` | ANTES (base `012ff47` com os testes novos): `ImportError: cannot import name 'check_approvers' from 'registry_tools'`, 1 error na coleta; DEPOIS: `33 passed, 10 deselected` | ver A04, A05 e A06 | Sim | `_framework/scripts/tests/test_review_approval.py:168` | automatizado |
| 1 | A02 | `python3 -m pytest _framework/scripts/tests/test_review_approval.py -q -k approvers` | ANTES (mesma base): o mesmo `ImportError`, 1 error; DEPOIS: `10 passed, 33 deselected` | `if valid:` trocado por `if True:` em `check_approvers` → `8 failed, 2 passed`; restaurado `10 passed` | Sim | `_framework/scripts/tests/test_review_approval.py:265` | automatizado |
| 1 | A03 | `python3 -m pytest _framework/scripts/tests/test_approval.py -q` | ANTES (mesma base): `1 failed, 34 passed` (`test_actor_fora_da_lista_reprova_com_a_mensagem`); DEPOIS: `35 passed` | ver A07 | Sim | `_framework/scripts/tests/test_approval.py:319` | automatizado |
| 1 | A04 | Em `review_approval.py`, removido o passo 5 de `decide` (`commit_id != head`); pytest de A01; restaurado pela cópia | `2 failed, 31 passed` (`test_aprovacao_sobre_commit_anterior_e_invalida`, `test_cli_invalida_sai_1_com_motivo`); restaurado `33 passed` | derrubada | Sim | `_framework/scripts/tests/test_review_approval.py:149` | automatizado |
| 1 | A05 | Em `approves`, `.strip() == "Aprovado"` trocado por `.strip().lower().startswith("aprovado")`; pytest de A01; restaurado pela cópia | `3 failed, 30 passed` (`test_commented_com_outro_corpo_nao_aprova[aprovado]`, `[Aprovado.]`, `[Aprovado, mas ajuste X]`); restaurado `33 passed` | derrubada | Sim | `_framework/scripts/tests/test_review_approval.py:98` | automatizado |
| 1 | A06 | Em `decide`, filtro `(approves(r) or r.get("state") == "CHANGES_REQUESTED")` trocado por `approves(r)`; pytest de A01; restaurado pela cópia | `1 failed, 32 passed` (`test_aprovacao_seguida_de_changes_requested_e_invalida`); restaurado `33 passed` | derrubada | Sim | `_framework/scripts/tests/test_review_approval.py:116` | automatizado |
| 1 | A07 | Em `validate_state.check_approval`, removido o bloco do `actor` contra `approvers`; pytest de A03; restaurado pela cópia | `1 failed, 34 passed` (`test_actor_fora_da_lista_reprova_com_a_mensagem`); restaurado `35 passed` | derrubada | Sim | `_framework/scripts/tests/test_approval.py:319` | automatizado |
| 1 | A08 | `python3 -m pytest _framework/tests/test_executor_contract.py -q` | ANTES (mesma base): `3 failed, 10 passed` (`KeyError`; `test_saidas_declaradas_validam_contra_o_esquema`, `test_aprovacao_por_review_no_contrato`, `test_approvers_declarado_no_registry_central`); DEPOIS: `13 passed` | segunda linha nova de `writes` removida do YAML → `1 failed, 12 passed` (`test_aprovacao_por_review_no_contrato`); restaurado `13 passed` | Sim | `_framework/tests/test_executor_contract.py:213` | automatizado |
| 1 | A09 | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` e o mesmo contra `012ff47` | `26 passed`; os dois diffs vazios (`origin/main` = `012ff47` nesta sessão) | a fixture do 2.3.2 compara stdout e exit dos validadores; sem mutação própria (o requisito é não mudar) | Sim | `_framework/scripts/tests/test_report_json.py:244` | automatizado |
| 1 | A10 | `grep -n 'version: "2.6.0"' _framework/rules/workflow-rules.yaml`; no central (branch `sdd/SDD-DTF-0055-espelho`, `0f4f842`): `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"`; `git status --porcelain docs/` | linhas 17 e 20; `✅ 134 documento(s) ok.` nas duas verificações, `✅ Todas as verificações do framework passaram.`, `exit=0`; porcelain vazio | sem teste automatizado (medição) | Sim | `n/a` | automatizado (medição por comando, sem asserção em arquivo) |
| 1 | A11 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | todos `em dia`/`sincronizado`, incluindo `review_approval.py` da skill; `exit=0` | sem teste automatizado (medição) | Sim | `n/a` | automatizado (medição por comando, sem asserção em arquivo) |
| 1 | A12 | `python3 -m pytest -q`; `ruff format --check` e `ruff check` nos 9 `.py` do diff; `python3 _framework/scripts/selftest.py` | `433 passed`; `9 files already formatted`; `All checks passed!`; `✅ 7 mutação(ões): todos os mutantes morreram.` | suíte inteira; sensores de A02 e A04 a A08 | Sim | `_framework/scripts/tests/test_review_approval.py:168` | automatizado |
| 1 | A13 | No central: `diff -r -x __pycache__ -x .pytest_cache /home/user/doc-traceability-framework/_framework _framework; echo "diff exit=$?"` | `diff exit=0` | sem teste automatizado (medição) | Sim | `n/a` | automatizado (medição por comando, sem asserção em arquivo) |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0030, ADR-DTF-0008 |
| RFC de origem | RFC-DTF-0009 (fase 4, primeira SPEC) |
| Branch | `sdd/SDD-DTF-0055-review-approval` |
