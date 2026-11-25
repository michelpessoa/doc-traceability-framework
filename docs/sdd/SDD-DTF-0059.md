---
id: SDD-DTF-0059
type: SDD
title: "Guias técnico e não técnico cobrem a 2.4.0 a 2.8.0: aprovação como dado, aprovação por review, contrato do executor, SDD enxuta e coluna Projeto"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0040, SDD-DTF-0053, SDD-DTF-0054, SDD-DTF-0055, SDD-DTF-0057, SDD-DTF-0058]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção de documentação narrativa pedida pelo owner em 2026-11-25, sem mudança de regra, script ou template; ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0040). A fonte de cada afirmação nova é a chave de workflow-rules.yaml citada no RF, nunca memória: abra a chave antes de escrever. Dois arquivos de produto; o sumário do guia técnico e o _framework/INDEX.md são gerados (render_indexes.py e render_prompts.py), nunca à mão. A SDD-DTF-0060 cobre a skill e os prompts, em branch própria. O central espelha os dois guias em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [guia-tecnico, guia-nao-tecnico, documentacao, drift, aprovacao, executor, sdd-enxuta]
---

# Guias técnico e não técnico cobrem a 2.4.0 a 2.8.0: aprovação como dado, aprovação por review, contrato do executor, SDD enxuta e coluna Projeto

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`docs/guias/guia-tecnico.md` e `docs/guias/guia-nao-tecnico.md` não mudam
desde setembro (última versão coberta: 2.3.x). As cinco versões seguintes,
2.4.0 a 2.8.0 (SDD-DTF-0053, 0054, 0055, 0057 e 0058), não aparecem em
nenhum dos dois: `approved_by`, `approval_policy`, `approval_hash.py`,
`review_approval.py`, `approvers`, `executor_contract`, saída `--json`,
`docs/sdd/arquivo/`, SDD enxuta, `molde`, seções opcionais da SPEC e a
coluna `Projeto` têm zero menções. Sete dos 22 scripts de
`_framework/scripts/` não aparecem no guia técnico, o exemplo de registry
da seção 3 ainda declara `framework_version: "1.7.0"` e o modo greenfield
(`repository_status: none_yet`) não é citado em nenhum guia. Esta SDD
fecha essas lacunas sem mudar regra nenhuma.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: dois guias narrativos, reversão trivial (reverter o commit), sem
alternativa técnica a registrar. `workflow-rules.yaml`, scripts, templates
e `framework.version` não mudam (`lessons_policy`: é falha de execução —
documentação que não acompanhou a regra —, não desenho).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Guia técnico, seção 2: a árvore do central lista `schemas/` e os 22 scripts de `_framework/scripts/`; a árvore do repositório de projeto mostra `docs/sdd/arquivo/` para SDD entregue (`repository_topology.project_repo.delivered`) | Quando a seção 2 for lida, cada arquivo `*.py` e `*.sh` de `_framework/scripts/` (exceto `tests/`) deve aparecer no guia, e `docs/sdd/arquivo/` também |
| RF02 | Guia técnico, seção 3: o exemplo de registry usa a versão corrente (`framework.version`), mostra `repository_status` (`active` ou `none_yet`, `registry.central_registry.repository_field`) e o campo opcional `approvers` (`registry.central_registry.approvers_field`), e o texto explica o modo greenfield em até um parágrafo | Quando a seção 3 for lida, ela não deve conter `"1.7.0"` e deve conter `repository_status`, `none_yet` e `approvers` |
| RF03 | Guia técnico, seção 4.1: a SPEC pode omitir as seções de `document_types.SPEC.optional_sections` conforme o sizing, e cada uma volta quando o seu `returns_when` se aplica; o sweep segue obrigatório | Quando a seção 4.1 for lida, ela deve citar `optional_sections` e dizer que o sweep segue obrigatório |
| RF04 | Guia técnico, seção 6: descreve a SDD enxuta (2.7.0): `sizing` obrigatório, "Requisitos consolidados" com `RF-ID \| Origem \| Requisito (resumo) \| Arquivos`, sem "Especificação técnica consolidada" nem "Decisão(ões) de arquitetura aplicável(is)", RF-IDs conferidos contra a SPEC nas duas direções por `check_source_docs.py`; `molde` só em `small`; e a coluna `Projeto` (2.8.0, `document_types.SPEC.rf_optional_columns`), com a SDD conferida só contra os RFs do seu `project` | Quando a seção 6 for lida, ela deve conter `enxuta`, `molde` e a coluna `Projeto` |
| RF05 | Guia técnico, seção nova "7.1 Aprovação como dado", depois da seção 7: quem aprova cada tipo e sizing (`approval_policy.rules`), os campos de `approved_by` (`frontmatter_schema`), o hash de `approval_hash.py` e as `hash_excluded_sections`, a aprovação por review de `review_approval.py` (`APPROVED`, ou `COMMENTED` com o corpo exatamente `Aprovado`; a mais recente entre aprovação e `CHANGES_REQUESTED` decide; presa ao head), `approvers`, `approved_by.transitions` só com `kind: policy`, e a não-retroatividade desde a 2.5.0 | Quando o guia for lido, deve existir o título `## 7.1 Aprovação como dado` e ele deve citar `approval_policy`, `approved_by`, `approval_hash.py`, `review_approval.py`, `approvers` e `transitions` |
| RF06 | Guia técnico, seção nova "7.2 Executores", depois da 7.1: o que um executor pode ler, os scripts com `--json` e os esquemas de `_framework/schemas/`, o que pode escrever (sempre por PR, nunca em `main`), `contract_version` e a regra de quebra só em versão maior (`executor_contract`); SDD entregue em `docs/sdd/arquivo/` com o campo `entrega` | Quando o guia for lido, deve existir o título `## 7.2 Executores` e ele deve citar `executor_contract`, `--json`, `contract_version` e `entrega` |
| RF07 | Guia técnico, seção 9: o bloco de scripts ganha `approval_hash.py`, `review_approval.py`, `render_indexes.py` e `check_hooks.py`, no formato das entradas existentes (comentário de uma linha e comando), e o texto diz que os scripts de `executor_contract.machine_outputs` aceitam `--json` | Quando a seção 9 for lida, ela deve conter os quatro nomes e `--json` |
| RF08 | Guia técnico, seção 15: dois erros novos — editar documento aprovado sem nova aprovação (o hash de `approved_by` deixa de bater) e aprovar por comentário fora do formato que `review_approval.py` aceita | Quando a seção 15 for lida, ela deve citar `content_sha256` e `Aprovado` |
| RF09 | Guia não técnico, seção nova "Quem aprova, e como": em linguagem sem jargão, a aprovação humana é uma review "Aprovado" na PR do documento; a SDD pode ser aprovada por política depois das checagens automáticas; mudar o documento depois da aprovação exige aprovar de novo | Quando o guia não técnico for lido, deve existir o título `## Quem aprova, e como` |
| RF10 | Guia não técnico, seção nova "Quando uma ferramenta automática executa o fluxo": o executor lê as decisões aprovadas, escreve só por PR, não aprova documento que cabe a uma pessoa e não faz merge em `main` | Quando o guia não técnico for lido, deve existir o título `## Quando uma ferramenta automática executa o fluxo` |
| RF11 | Guia não técnico: um parágrafo sobre projeto que ainda não tem código (greenfield): as decisões começam no central e a SDD espera o repositório existir | Quando o guia não técnico for lido, ele deve conter a palavra `greenfield` |

Fora de escopo: `workflow-rules.yaml`, scripts, templates, `AGENTS.md`,
`QUICKSTART.md`, `docs/especificacao.md`, os outros guias
(`paralelizacao-trilhas.md`, `gate-ci-verify-sdd.md`), a skill e os
prompts (SDD-DTF-0060), e a origem local em `source_docs`
(RFC-DTF-0010, ADR-DTF-0009), que ainda não está no kit.

## Especificação técnica consolidada

- **Onde.** `docs/guias/guia-tecnico.md` (RF01 a RF08) e
  `docs/guias/guia-nao-tecnico.md` (RF09 a RF11).
- **Forma.** Adições e correções pontuais; tom, numeração e estrutura
  existentes preservados. As seções novas 7.1 e 7.2 entram entre a 7 e a
  8, sem renumerar as demais. Nas seções novas, cada regra aponta a chave
  do YAML entre crases (ex.: `approval_policy.rules`) e não a reescreve
  inteira: o YAML manda.
- **Sumário gerado.** O bloco `<!-- BEGIN GENERATED: sumário -->` do guia
  técnico é refeito por `render_indexes.py` (via `render_prompts.py`),
  nunca à mão; `_framework/INDEX.md` também.
- **Espelho no central.** Os dois guias são copiados sem divergência para
  `doc-traceability-central/docs/guias/`, com `_framework/INDEX.md`, em
  branch e PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Seções 2, 3, 4.1, 6, 9 e 15 do guia técnico | RF01 a RF04, RF07, RF08 | `docs/guias/guia-tecnico.md` | |
| 2 | Seções novas 7.1 e 7.2 do guia técnico | RF05, RF06 | `docs/guias/guia-tecnico.md` | 1 |
| 3 | Seções novas do guia não técnico | RF09 a RF11 | `docs/guias/guia-nao-tecnico.md` | |
| 4 | Regenerar sumário e índice | RF01 a RF11 | `docs/guias/guia-tecnico.md`, `_framework/INDEX.md` | 2, 3 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF11 | `central:docs/guias/guia-tecnico.md`, `central:docs/guias/guia-nao-tecnico.md`, `central:_framework/INDEX.md` | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A12.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01: todo script na seção 2 | `for s in $(cd _framework/scripts && ls *.py *.sh); do grep -q "$s" docs/guias/guia-tecnico.md \|\| echo "falta $s"; done; grep -c "docs/sdd/arquivo/" docs/guias/guia-tecnico.md` | Nenhum `falta` e contagem ≥ 1 | automatizado |
| A02 | RF02: exemplo de registry | `grep -c '"1.7.0"' docs/guias/guia-tecnico.md; grep -cE "repository_status\|none_yet\|approvers" docs/guias/guia-tecnico.md` | `0` e ≥ 3 | automatizado |
| A03 | RF03: seções opcionais da SPEC | `grep -c "optional_sections" docs/guias/guia-tecnico.md` | ≥ 1 | automatizado |
| A04 | RF04: SDD enxuta, molde e coluna Projeto | `grep -cE "enxuta\|molde\|coluna \`Projeto\`" docs/guias/guia-tecnico.md` | ≥ 3 | automatizado |
| A05 | RF05: seção 7.1 | `grep -n "^## 7.1 Aprovação como dado" docs/guias/guia-tecnico.md; for t in approval_policy approved_by approval_hash.py review_approval.py approvers transitions; do grep -q "$t" docs/guias/guia-tecnico.md \|\| echo "falta $t"; done` | Uma linha de título e nenhum `falta` | automatizado |
| A06 | RF06: seção 7.2 | `grep -n "^## 7.2 Executores" docs/guias/guia-tecnico.md; for t in executor_contract --json contract_version entrega; do grep -qF -e "$t" docs/guias/guia-tecnico.md \|\| echo "falta $t"; done` | Uma linha de título e nenhum `falta` | automatizado |
| A07 | RF07 e RF08: scripts na seção 9 e erros na seção 15 | `grep -cE "render_indexes.py\|check_hooks.py" docs/guias/guia-tecnico.md; grep -c "content_sha256" docs/guias/guia-tecnico.md` | ≥ 2 e ≥ 1 | automatizado |
| A08 | RF09 a RF11: guia não técnico | `grep -cE "^## Quem aprova, e como\|^## Quando uma ferramenta automática executa o fluxo" docs/guias/guia-nao-tecnico.md; grep -c "greenfield" docs/guias/guia-nao-tecnico.md` | `2` e ≥ 1 | automatizado |
| A09 | RF01 a RF11: cada afirmação nova bate com a chave do YAML que ela cita (`approval_policy`, `frontmatter_schema.approved_by`, `executor_contract`, `document_types.SPEC`, `registry.central_registry`) | Leitura lado a lado do diff dos dois guias e das chaves citadas de `_framework/rules/workflow-rules.yaml` | Nenhuma afirmação sem chave correspondente ou que a contradiga | manual |
| A10 | Gerados em dia e renderizações coerentes | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `exit=0` nos dois | automatizado |
| A11 | Suíte, validação e escopo | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | 0 failed; `exit=0`; só os dois guias, `_framework/INDEX.md`, esta SDD e os gerados de `docs/sdd/` (`registry.yaml`, `registry.md`, `INDEX.md`) | automatizado |
| A12 | Central: espelho idêntico | No central: `cmp` dos dois guias e de `_framework/INDEX.md` contra o kit; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0059-guias-2.4-a-2.8`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0059`. Nunca em `main`.
- **Fonte:** cada afirmação nova vem da chave do YAML citada no RF, aberta
  na hora de escrever; os exemplos de review usam o texto de
  `review_approval.py`, não paráfrase.
- **Não mudar** `workflow-rules.yaml`, scripts, templates, os outros guias,
  a skill nem os prompts.
- **Gerados só por script:** `render_prompts.py` para o sumário e
  `_framework/INDEX.md`; `generate_registry_md.py` para `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF11) tem trecho
      correspondente nos dois guias.
- [ ] Todo arquivo tocado aparece nas tasks ou nas instruções.
- [ ] Nenhuma mudança em regra, script, template, outro guia, skill ou
      prompt.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** {sim | não — mesma sessão que implementou}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
