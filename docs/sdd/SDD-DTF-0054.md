---
id: SDD-DTF-0054
type: SDD
title: "Aprovação como dado: approval_policy no YAML, approved_by preso ao hash do conteúdo, approval_hash.py e cobrança no validate_state"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-17"
updated: "2026-11-17"
relates_to: [SDD-DTF-0053]
source_docs:
  - id: "SPEC-DTF-0029"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0029.md"
  - id: "ADR-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0008.md"
sizing: "large"
consumption_instructions: "Compilada da SPEC-DTF-0029 (approved) e da ADR-DTF-0008 (approved). Os requisitos e critérios abaixo são os da SPEC; o formato de approval_policy, de approved_by e do --json de approval_hash.py está em 'Especificação técnica consolidada' e é lei: não inventar campo, chave ou mensagem de sucesso nova. Teste primeiro, visto falhar. A saída em texto dos validadores não pode mudar para documento fora da regra nova. Gerados (cópias da skill, índices, AGENTS.md, CHANGELOG.md, mapa do YAML) só por render_prompts.py. O central espelha por branch e PR próprios."
supersedes: null
superseded_by: null
tags: [integracao, executor, aprovacao, approved_by, approval_policy]
---

# Aprovação como dado: approval_policy no YAML, approved_by preso ao hash do conteúdo, approval_hash.py e cobrança no validate_state

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar.

## Resumo executivo

Fase 2 da RFC-DTF-0009. Hoje o ciclo de status diz quais transições valem,
mas não quem as fez. Esta SDD faz a aprovação virar dado verificável: o
`workflow-rules.yaml` ganha `approval_policy`, que declara por tipo e
sizing quem pode aprovar; o front-matter ganha o campo opcional
`approved_by`, preso ao sha256 do corpo aprovado; `approval_hash.py`
calcula esse hash; e `validate_state.py` reprova o campo ausente, o
`kind` que a política não permite e o conteúdo que mudou depois da
aprovação. Não retroativo. Versão 2.5.0.

## Decisão(ões) de arquitetura aplicável(is)

ADR-DTF-0008, itens 3 e 4: aprovação como dado no front-matter, com quem
aprovou e sobre qual conteúdo, e aprovação humana por review de PR para
os tipos que a política reserva ao owner. Os itens 1, 2 e 6 (kit sem
citar executor, contrato versionado, não retroatividade) seguem valendo:
`executor_contract` só ganha entradas, `contract_version` fica 1. O item
5 (escrita do executor no central por PR) é da fase 4 e não entra aqui.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | O YAML declara quem aprova cada tipo e sizing | O sistema deve ter no `workflow-rules.yaml` a chave de topo `approval_policy` com `rules` (lista de `{types, sizing, approver, checks}`), `default_approver: human` e `hash_excluded_sections`; a primeira regra que casa vale |
| RF02 | Valores iniciais decididos pelo owner em 2026-11-16 | O sistema deve declarar na política `human` para STRAT, RFC, ADR, BASE e PM em qualquer sizing e para SPEC em `medium`, `large` e `complex`, e `policy` para SDD em qualquer sizing, com `checks` da SDD: `validate_doc.py`, `registry_tools.py validate`, `check_source_docs.py` quando houver `source_docs`, e o passo 0 do `verify-sdd` quando houver `source_docs` |
| RF03 | O front-matter registra a aprovação | O sistema deve declarar no `frontmatter_schema` o campo comum opcional `approved_by: {kind, actor, at, content_sha256, evidence}`, com `kind` em `human` ou `policy`, `at` em data ou data-hora ISO 8601, `content_sha256` com 64 caracteres hexadecimais e `evidence` obrigatório quando `kind: human` |
| RF04 | O hash do conteúdo é reproduzível | Quando chamado como `approval_hash.py <documento>`, o sistema deve imprimir o sha256 do corpo do documento (sem o front-matter), com quebras de linha normalizadas para `\n` e sem as seções de `hash_excluded_sections`; com `--json`, um objeto válido contra `_framework/schemas/approval-hash.schema.json` |
| RF05 | `validate_state.py` cobra o campo | Se um documento em `approved`, `implemented` ou `superseded`, sob as regras desta versão, não tiver `approved_by` válido, então `validate_state.py` deve reprovar nomeando o documento e o motivo |
| RF06 | A política é respeitada | Se `approved_by.kind` for `policy` num tipo e sizing que a política reserva a `human`, então `validate_state.py` deve reprovar |
| RF07 | Conteúdo alterado depois da aprovação reprova | Se o `content_sha256` gravado diferir do hash atual calculado por `approval_hash.py`, então `validate_state.py` deve reprovar dizendo que o documento mudou depois da aprovação |
| RF08 | Não retroativo | Enquanto o documento tiver `created` anterior à data da versão 2.5.0, ou o projeto declarar `framework_version` anterior a 2.5.0, `validate_state.py` não deve cobrar `approved_by`; quando o campo existir mesmo assim, deve validá-lo |
| RF09 | O contrato do executor acompanha | O sistema deve declarar no `executor_contract` `approval_policy` em `reads`, `approval_hash.py` em `machine_outputs` e, em `writes`, `approved_by` com `kind: policy` só onde a política permite; `contract_version` continua 1, porque só acrescenta |
| RF10 | Versão minor | O sistema deve declarar `framework.version` `2.5.0`, com entrada no changelog, e manter verde o `framework_check.py --auto` do central sem mudar nenhum documento existente |

Casos de borda, da SPEC, que a implementação e os testes cobrem:

| Caso | RF | Comportamento esperado |
|---|---|---|
| Documento sem `sizing` (RFC, ADR) | RF01 | Casa por `types`; regra com `sizing` ausente vale para qualquer sizing |
| Tipo que nenhuma regra cobre | RF01 | Vale `default_approver: human` |
| INC | RF05 | Fora da cobrança: o ciclo do INC não tem `approved` |
| Documento em `draft`, `in_review`, `rejected` ou `archived` | RF05 | Não cobra; se o campo existir, valida só o formato |
| `approved_by` com `kind` fora de `human`/`policy` ou hash que não é hexadecimal de 64 | RF03, RF05 | Reprova com o campo inválido nomeado |
| `kind: human` sem `evidence` | RF03 | Reprova |
| Seção excluída do hash preenchida depois da aprovação | RF04, RF07 | O hash não muda e não reprova |
| Mudança de status ou do próprio `approved_by` no front-matter | RF04 | O hash não muda: o front-matter fica fora |
| Arquivo com CRLF | RF04 | Mesmo hash do arquivo com LF |
| Documento criado antes da 2.5.0, aprovado depois e já com o campo | RF08 | O campo é validado, sem tornar o restante retroativo |

Requisitos não funcionais: só biblioteca padrão e `pyyaml` nos scripts; a
saída em texto dos validadores existentes não muda para documento que não
está sob a regra nova (a fixture do 2.3.2 continua passando).

Fora de escopo, da SPEC: conferir no GitHub o revisor e o commit
aprovado (fase 4); gravar `approved_by` automaticamente (é do executor);
migrar documentos existentes; mudar o ciclo de status; mudar os
templates (a SPEC admite só um comentário sobre o campo, e esta SDD não o
faz).

## Especificação técnica consolidada

Contratos completos na SPEC-DTF-0029, seção "Contratos técnicos". O que a
implementação precisa acertar:

- **`approval_policy` em `_framework/rules/workflow-rules.yaml`**, chave
  de topo nova, exatamente:

  ```yaml
  approval_policy:
    default_approver: human
    hash_excluded_sections: ["Evidência de verificação", "Verificação de escopo (nada a mais, nada a menos)", "Gate de decisão: esta RFC exige um ADR?", "Documentos originados"]
    rules:
      - {types: [STRAT, RFC, ADR, BASE, PM], approver: human}
      - {types: [SPEC], sizing: [medium, large, complex], approver: human}
      - types: [SDD]
        approver: policy
        checks: ["validate_doc.py", "registry_tools.py validate", "check_source_docs.py (com source_docs)", "verify-sdd passo 0 (com source_docs)"]
  ```

  Casamento: percorre `rules` em ordem; uma regra casa quando o `type` do
  documento está em `types` e, se a regra tiver `sizing`, o `sizing` do
  documento está nele. A primeira que casa dá o `approver`; nenhuma casa,
  vale `default_approver`. Consequência literal: SPEC sem `sizing` ou com
  `small` não casa a segunda regra e cai em `default_approver: human`.
- **`approved_by` em `frontmatter_schema.common_fields`**, como texto
  descritivo igual aos demais campos comuns, declarando: opcional; mapa
  `{kind, actor, at, content_sha256, evidence}`; `kind` em `human` ou
  `policy`; `actor` login do revisor ou nome do executor; `at` data
  `YYYY-MM-DD` ou data-hora ISO 8601; `content_sha256` de
  `approval_hash.py`; `evidence` obrigatório se `kind: human` (URL da
  review). Exemplo da SPEC:

  ```yaml
  approved_by:
    kind: human
    actor: "michelpessoa"
    at: "2026-11-16T16:07:25Z"
    content_sha256: "<64 hex de approval_hash.py>"
    evidence: "https://github.com/<org>/<repo>/pull/<n>#pullrequestreview-<id>"
  ```

  `validate_doc.py` não muda: os obrigatórios dele são a lista fixa
  `REQUIRED_FRONTMATTER`, e `approved_by` não entra nela.
- **`_framework/scripts/approval_hash.py`** (novo, só biblioteca padrão e
  `pyyaml`, via `framework_lib`):
  - `content_hash(path: Path, excluded: list[str] | None = None) -> str`.
    `excluded=None` lê `approval_policy.hash_excluded_sections` de
    `load_rules()`; chave ausente, sem exclusão.
  - Corpo = texto depois do front-matter (o que `read_frontmatter` devolve
    como corpo); CRLF vira LF; cada seção cuja linha de
    título comece por `## ` seguido de um item de `hash_excluded_sections`
    sai inteira, do título até a próxima linha que começa por `## ` ou o
    fim do arquivo; espaços no fim das linhas e linhas em branco no fim
    saem; o hash é o sha256 hexadecimal minúsculo dos bytes UTF-8 do
    resultado.
  - CLI `approval_hash.py <documento> [--json]`: sem `--json`, imprime só
    o hash e sai com 0; com `--json`, imprime só
    `{"schema": "dtf.approval-hash/1", "documento": <id do front-matter>,
    "content_sha256": <hex>, "secoes_excluidas": [<títulos de
    hash_excluded_sections>]}`. Documento sem front-matter ou inexistente:
    sai com 1 e diz o motivo no stderr; sem argumento, imprime o uso e
    sai com 1.
- **`_framework/schemas/approval-hash.schema.json`** (novo, JSON Schema
  2020-12, mesmo estilo dos da fase 1): objeto com exatamente `schema`
  (const `dtf.approval-hash/1`), `documento` (string), `content_sha256`
  (padrão `^[0-9a-f]{64}$`) e `secoes_excluidas` (array de strings),
  todos obrigatórios, `additionalProperties: false`.
- **`_framework/scripts/validate_state.py`:**
  - `RULE_SINCE["approved_by"] = "2.5.0"`.
  - `check_approval(path: Path, version: str | None = None) -> tuple[list[str], list[str]]`,
    ao lado de `check_sdd`. Sem front-matter ou `type: INC`: `([], [])`.
    Cobrança vale quando o status é `approved`, `implemented` ou
    `superseded` **e** `rule_applies_since_date(rules, "2.5.0", created, version)`
    **e** `rule_applies("2.5.0", version)` — as duas condições do RF08,
    com as funções que já existem em `framework_lib`.
  - Com cobrança e sem o campo: reprova `"{id}: approved_by ausente
    (obrigatório em {status} desde a 2.5.0)."`.
  - Campo presente, em qualquer status: valida o formato — não é mapa →
    `"{id}: approved_by deve ser um mapa."`; campo de `actor`, `at`,
    `content_sha256`, `kind` ausente → nomeia o campo; `kind` fora de
    `human`/`policy`, `at` fora de ISO 8601, hash que não é hexadecimal de
    64, `evidence` ausente com `kind: human` → nomeia o campo inválido.
  - Campo presente e status `approved`, `implemented` ou `superseded`
    (cobrado ou não, RF08): além do formato, política (`kind: policy`
    onde o `approver` casado é `human` reprova, nomeando tipo e sizing) e
    hash (`content_sha256` diferente de `approval_hash.content_hash(path)`
    reprova com `"{id}: o documento mudou depois da aprovação (gravado
    <hex>, atual <hex>)."`). Em `draft`, `in_review`, `rejected` ou
    `archived`, só o formato.
  - Toda mensagem começa por `{id}:` para o `documento` do `--json` da
    fase 1 sair preenchido.
  - `main()` chama `check_approval` no mesmo laço de `check_sdd` e soma
    problemas e avisos; a mensagem de sucesso não muda.
- **`_framework/scripts/framework_check.py`:** no laço existente da
  "verificação de escopo (seção 16)", chama também
  `validate_state.check_approval(path)` e soma ao mesmo `problems` e
  `warnings`; nenhum cabeçalho nem mensagem nova, para a saída em texto
  não mudar quando nada reprova.
- **`executor_contract`:** `reads` ganha `approval_policy`;
  `machine_outputs` ganha `{script: approval_hash.py, args:
  ["<documento>", "--json"], schema:
  _framework/schemas/approval-hash.schema.json}`; `writes` ganha a linha
  `"Campo approved_by com kind: policy só onde approval_policy permite."`;
  `contract_version` fica 1.
- **Versão:** `framework.version: "2.5.0"`, `last_updated` e entrada nova
  no topo de `changelog`, com `date` do dia da implementação — é essa data
  que `version_date` usa no RF08.
- **Gerados:** cópias da skill, `references/workflow-rules.yaml` da skill,
  `AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, o
  mapa do YAML e os índices, todos por `render_prompts.py`.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes do hash (estável com CRLF, com front-matter mudado e com seção excluída preenchida; muda com o corpo mudado; CLI com e sem `--json`, sem front-matter sai com 1), vistos falhar | RF04 | `_framework/scripts/tests/test_approval_hash.py` | |
| 2 | `approval_hash.py` e o esquema | RF04 | `_framework/scripts/approval_hash.py`, `_framework/schemas/approval-hash.schema.json` | 1 |
| 3 | Testes de `check_approval` e da política no YAML real (regras, ordem e valores iniciais; um caso por motivo de reprovação; um que passa; INC; status sem cobrança; documento antigo e projeto em 2.4.0; campo presente validado), vistos falhar | RF01, RF02, RF03, RF05, RF06, RF07, RF08 | `_framework/scripts/tests/test_approval.py` | 2 |
| 4 | `approval_policy`, `approved_by` em `frontmatter_schema`, 2.5.0 e changelog | RF01, RF02, RF03, RF10 | `_framework/rules/workflow-rules.yaml` | 3 |
| 5 | `check_approval`, `RULE_SINCE` e a chamada no `main()`; chamada no `framework_check.py` | RF05, RF06, RF07, RF08 | `_framework/scripts/validate_state.py`, `_framework/scripts/framework_check.py` | 4 |
| 6 | Teste de contrato com `approval_policy` em `reads`, `approval_hash.py` em `machine_outputs` e `hash_excluded_sections` presente, visto falhar; `executor_contract` atualizado | RF09 | `_framework/tests/test_executor_contract.py`, `_framework/rules/workflow-rules.yaml` | 5 |
| 7 | Manifesto e gerados; o teste do mapa passa a contar 24 seções | RF01, RF10 | `_framework/rules/kit-index.yaml`, `_framework/tests/test_render_indexes.py`, gerados por `render_prompts.py` | 6 |
| 8 | Espelho no central, branch e PR próprios | RF01 a RF10 | `central:_framework/`, mesmos caminhos | 7 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF04: hash reproduzível e CLI | `python3 -m pytest _framework/scripts/tests/test_approval_hash.py -q` | ANTES da task 2: falha; DEPOIS: todos passam | automatizado |
| A02 | RF01, RF02, RF03, RF05 a RF08: política e cobrança | `python3 -m pytest _framework/scripts/tests/test_approval.py -q` | ANTES da task 5: falha; DEPOIS: todos passam | automatizado |
| A03 | RF07: sensor do hash | Em cópia descartável, fazer `check_approval` ignorar a comparação de `content_sha256`; rodar o pytest de A02; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A04 | RF06: sensor da política | Em cópia descartável, trocar o `approver` da regra de SPEC para `policy` no YAML; rodar o pytest de A02; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A05 | RF04: sensor da exclusão | Em cópia descartável, esvaziar `hash_excluded_sections` no YAML; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A06 | RF09: contrato | `python3 -m pytest _framework/tests/test_executor_contract.py -q` | ANTES da task 6: falha; DEPOIS: todos passam | automatizado |
| A07 | Não funcional: saída em texto | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q` | Todos passam, fixture do 2.3.2 sem alteração (`git diff --stat origin/main -- _framework/scripts/tests/fixtures/` vazio) | automatizado |
| A08 | RF10: versão e central | `grep -n 'version: "2.5.0"' _framework/rules/workflow-rules.yaml`; no central, com `_framework/` desta branch: `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` e `git status --porcelain docs/` | A linha da versão; `exit=0`; nenhum documento alterado | automatizado |
| A09 | Gerados em dia | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `exit=0` | automatizado |
| A10 | Suíte e formatação | `python3 -m pytest -q; ruff format --check` nos arquivos tocados | 0 failed; arquivos tocados formatados | automatizado |
| A11 | Espelho | No central: `diff -r <kit>/_framework _framework` | Sem diferença | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0054-aprovacao-como-dado`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0054`. Nunca em `main`.
- **Teste primeiro** em cada task, com a falha guardada.
- **Não acrescentar** chave, campo ou mensagem de sucesso que a SPEC não
  declara (lição da rodada 1 da SDD-DTF-0053). `executor_contract`
  continua com exatamente `contract_version`, `description`, `reads`,
  `machine_outputs` e `writes`.
- **Não mudar** o texto de nenhuma mensagem existente dos validadores,
  nenhum gate, sizing, ciclo de status, template nem campo obrigatório do
  front-matter.
- **Não migrar** nem editar documento existente, no kit ou no central.
- **Sem citar executor específico** no kit (ADR-DTF-0008, item 1).
- **Gerados só por script.** Nunca editar à mão as cópias da skill, os
  índices, `AGENTS.md`, `CHANGELOG.md` nem o mapa.
- **Evidência de verificação** só por verificador independente.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF10) tem código
      correspondente.
- [ ] Todo arquivo tocado aparece na "Decomposição em tasks" ou é gerado
      por `render_prompts.py`.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** a preencher pelo verificador

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0029, ADR-DTF-0008 |
| RFC de origem | RFC-DTF-0009 (fase 2) |
| Branch | `sdd/SDD-DTF-0054-aprovacao-como-dado` |
