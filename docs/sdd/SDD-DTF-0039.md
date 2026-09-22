---
id: SDD-DTF-0039
type: SDD
title: "Sweep de requisitos transversais na SPEC (item 10 de STRAT-DTF-0003)"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "STRAT-DTF-0003"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md"
consumption_instructions: "Sizing small — sem SPEC/RFC, compilado direto do item 10 (último) da tabela de prioridade de STRAT-DTF-0003, seção 'Comparação com o tlc-spec-lean' (E8). Aplicar em _framework/templates/spec.template.md, _framework/scripts/validate_doc.py e _framework/rules/workflow-rules.yaml (gate_content_quality, seção 15), replicar via render_prompts.py e na cópia bundlada da skill, e cobrir com teste antes de implemented."
supersedes: null
superseded_by: null
tags: [spec, sweep, requisitos-transversais, tlc-spec-lean, qualidade]
---

# Sweep de requisitos transversais na SPEC

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar.

## Resumo executivo

A SPEC não força autora a considerar categorias transversais que
tipicamente ficam de fora por omissão silenciosa: autorização,
concorrência, idempotência, observabilidade, falha de dependência
externa, validação de entrada e limite de volume/rate. Esta SDD adiciona
ao `spec.template.md` uma seção fixa "Requisitos transversais (sweep)"
com uma linha por categoria, cada uma exigindo `Destino` (RF-ID que
cobre) ou `n/a` + motivo, e mecaniza a checagem em `validate_doc.py` —
célula vazia é gate, não estilo. É o item 10 (último) de STRAT-DTF-0003,
origem E8 da comparação com o `tlc-spec-lean`.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small` (STRAT-DTF-0003 já declara e nenhum critério de
`decision_gates.rfc_to_adr` se aplica: é convenção de preenchimento de
documento e checagem mecânica associada, não mudança de padrão
arquitetural nem de comportamento externo do produto).

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | `_framework/templates/spec.template.md` deve ganhar uma seção "## Requisitos transversais (sweep)" entre "Requisitos não funcionais" e "Fora de escopo", com tabela fixa de 7 categorias (autorização/permissão, concorrência, idempotência, observabilidade, falha de dependência externa, validação de entrada, limite de volume/rate) e colunas `Destino (RF-ID ou n/a)` e `Motivo (obrigatório se n/a)`. |
| RF02 | `_framework/scripts/validate_doc.py` deve mecanizar, para SPEC em `draft`/`in_review`, que a seção "Requisitos transversais (sweep)" existe, que as 7 categorias fixas têm linha própria, e que toda linha tem `Destino` preenchido (RF-ID válido ou `n/a` com motivo não vazio na coluna seguinte) — célula vazia é gate. |
| RF03 | A checagem de RF02 não deve ser retroativa: SPEC criada antes da data em que esta regra entrou no changelog do framework não pode ser reprovada por não ter a seção, que ainda não existia no template quando foi escrita. |
| RF04 | `_framework/rules/workflow-rules.yaml` deve versionar esta mudança (bump de `framework.version`, entrada de changelog) e citar a seção nova em `gate_content_quality` (seção 15), como item novo da regra. |
| RF05 | `render_prompts.py` deve continuar passando `--check` sem divergência após as mudanças (AGENTS.md, QUICKSTART.md, especificacao.md, CHANGELOG.md, universal.md, doc-framework.mdc, copilot-instructions.md e a cópia bundlada de `validate_doc.py`/`workflow-rules.yaml` da skill todos regenerados/sincronizados), e a cópia bundlada de `spec.template.md` na skill deve ficar idêntica à de `_framework/templates/`. |

## Especificação técnica consolidada

Arquivos tocados (produto):
- `_framework/templates/spec.template.md` — RF01.
- `_framework/skills/doc-traceability-framework/templates/spec.template.md` — cópia bundlada de RF01 (não coberta por `render_prompts.py`, que não sincroniza `templates/`; copiar manualmente byte a byte).
- `_framework/scripts/validate_doc.py` — RF02, RF03 (`RULE_SINCE["sweep"]`, `SWEEP_CATEGORIES`, `check_sweep_section`).
- `_framework/rules/workflow-rules.yaml` — RF04 (bump `framework.version` para `2.3.0`, changelog, item 7 de `gate_content_quality`).
- Arquivos gerados por `render_prompts.py` (RF05): `AGENTS.md`, `QUICKSTART.md`, `docs/especificacao.md`, `CHANGELOG.md`, `_framework/prompts/universal.md`, `_framework/prompts/doc-framework.mdc`, `_framework/prompts/copilot-instructions.md`, `_framework/skills/doc-traceability-framework/scripts/validate_doc.py`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`.

Contrato de `check_sweep_section(doc_id: str, body: str) -> list[str]`
(`_framework/scripts/validate_doc.py`): recebe o id do documento e o
corpo markdown já sem front-matter; devolve lista de mensagens de
problema (vazia se a seção está completa). Chamado de dentro de
`check_document` só quando `doc_type == "SPEC"`, `status` em
`DRAFTING_STATUSES` e `applies("sweep")` (checagem de não-retroatividade
via `rule_applies_since_date`, mesmo mecanismo já usado por `ears`,
`rf_id` etc.). `SWEEP_CATEGORIES` é a lista fixa das 7 categorias, em
minúsculas, comparada contra a primeira coluna de cada linha da tabela
(case-insensitive).

## Decomposição em tasks

Dispensada — sizing `small` (RF06/RF07 de SDD-DTF-0030 dispensam a seção
quando `sizing: small`).

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — seção nova presente no template, entre "Requisitos não funcionais" e "Fora de escopo", com as 7 categorias | `grep -n "Requisitos transversais (sweep)" _framework/templates/spec.template.md` | Ao menos 1 ocorrência | automatizado |
| 2 | RF02/RF03 — gate mecanizado, com sensor de discriminação (categoria faltando, Destino vazio, n/a sem motivo, não-retroatividade) | `python3 -m pytest _framework/tests/test_validate_doc.py -k sweep -v` | Todos os testes `sweep` passam | automatizado |
| 3 | RF04 — `gate_content_quality` (seção 15) cita a seção nova | `grep -n "Requisitos transversais (sweep)" _framework/rules/workflow-rules.yaml` | Ao menos 2 ocorrências (changelog + regra) | automatizado |
| 4 | RF05 — nenhuma divergência de renderização | `python3 _framework/scripts/render_prompts.py --check` | Todos os itens `✅` | automatizado |
| 5 | RF05 — cópia bundlada do template idêntica à cópia canônica | `diff _framework/templates/spec.template.md _framework/skills/doc-traceability-framework/templates/spec.template.md` | Sem saída (exit 0) | automatizado |
| 6 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam | automatizado |

## Instruções específicas para a IA implementadora

- Não alterar `docs/especificacao.md`, `AGENTS.md`, `QUICKSTART.md`,
  `CHANGELOG.md` ou os prompts (`universal.md`, `doc-framework.mdc`,
  `copilot-instructions.md`) manualmente — são gerados por
  `render_prompts.py` a partir do YAML; qualquer edição manual neles é
  sobrescrita e reprovada por `render_prompts.py --check`.
- A lista de 7 categorias (`SWEEP_CATEGORIES`) é fixa por esta SDD —
  não adicionar nem remover categoria sem nova mudança de regra
  (`workflow-rules.yaml`), mesmo que pareça faltar uma óbvia.
- Não tornar a seção obrigatória para SDD, apenas para SPEC — SDD já tem
  sua própria seção de verificação de escopo, e o sweep é especificamente
  sobre o requisito (Parte 1 da SPEC), não sobre o compilado de
  implementação.
- Ao editar `validate_doc.py`, seguir o padrão já usado por
  `check_files_column`/`check_tasks_section`: função pura que recebe o
  corpo já parseado e devolve lista de strings de problema, chamada só
  quando `drafting` (status em `DRAFTING_STATUSES`) para não reprovar
  documento já decidido.

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF05 todos com trecho/arquivo correspondente na implementação.
- [x] Nenhum arquivo tocado fora da lista de "Especificação técnica
      consolidada" — se tocar outro, atualizar esta SDD ou remover
      antes do commit. (`HANDOFF.md`, novo no diff, é artefato descartável
      da skill `handover`, não produto — não conta como escopo tocado.)
- [x] Nenhuma categoria de sweep adicionada/removida além das 7 listadas.
- [x] `gate_content_quality` (workflow-rules.yaml) e `spec.template.md`
      (as duas cópias) não divergem entre si na descrição da seção nova.

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS** (rodada 2 — passo 0 reaberto depois de STRAT-DTF-0003 virar `approved`).

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0039.md /home/michel/doc-traceability-central/docs/DTF` + leitura integral de STRAT-DTF-0003 (item 10 e seção "Comparação com o tlc-spec-lean", linha E8) | `❌ 1 problema(s) encontrado(s): SDD-DTF-0039: source_docs 'STRAT-DTF-0003' está com status 'draft' — esperado approved ou implemented.` Itens 2-4 do passo 0 (RF-ID↔requisito, nenhum critério relaxado, contratos técnicos) verificados por leitura: RF01-RF05 da SDD conferem fielmente com a descrição do item 10/E8 da STRAT (mesmas 7 categorias, mesma exigência de preencher Destino (RF-ID) ou declarar "não aplicável" com motivo), sem relaxamento identificado — mas não há "Parte 2" formal na STRAT para comparar contrato técnico byte a byte, pois é doc de direção, não SPEC (compatível com sizing `small`, que pula a SPEC). | n/a (checagem documental de status do source_doc, não de código) | **Não** — achado bloqueante | `_framework/scripts/check_source_docs.py:59-64` | automatizado |
| 2 | Fidelidade à origem (recheck) | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0039.md /home/michel/doc-traceability-central/docs/DTF` — rodado depois de STRAT-DTF-0003 virar `approved` no arquivo e no `registry.yaml` do repositório central (PR michelpessoa/doc-traceability-central#121, ainda não mergeado, mas já refletido em disco em `/home/michel/doc-traceability-central`, que é a árvore que o script lê) | `✅ source_docs de SDD-DTF-0039.md conferem com o registry central.` Confirmado em disco: `docs/DTF/registry.yaml:28` e front-matter de `docs/DTF/00-strategy/STRAT-DTF-0003.md:4` ambos `status: approved`. Itens 2-4 do passo 0 (ver rodada 1) continuam válidos — nada mudou no conteúdo da STRAT além do `status`. | n/a (checagem documental de status do source_doc, não de código) | Sim | `_framework/scripts/check_source_docs.py:59-64` | automatizado |
| 1 | 1 | `grep -n "Requisitos transversais (sweep)" _framework/templates/spec.template.md` | `75:## Requisitos transversais (sweep)` — 1 ocorrência | Mutação real: heading renomeado para "Requisitos transversais TEMP-SENSOR" via Edit → hook `hook_post_edit.py` (roda `validate_doc.py` no arquivo salvo) acusou `seção obrigatória ausente: 'Requisitos transversais (sweep)'`; restaurado o heading original, `git diff` vazio confirmado, hook voltou a não acusar ausência (avisos residuais de "Destino vazia" são esperados — é o próprio template com placeholders, não uma SPEC real) | Sim | `_framework/scripts/validate_doc.py:390-394` | automatizado |
| 1 | 2 | `python3 -m pytest _framework/tests/test_validate_doc.py -k sweep -v` | `6 passed` | Mutação de código isolada: cópia de `validate_doc.py` em diretório fora do repositório (edição in-place do arquivo real foi bloqueada pelo classificador de segurança do ambiente de execução) com `check_sweep_section` forçado a `return []` incondicional, exercida via harness standalone reproduzindo as 6 fixtures do arquivo de teste → 4 de 6 (`test_sweep_ausente_falha`, `test_sweep_categoria_faltando_falha`, `test_sweep_destino_vazio_falha`, `test_sweep_na_sem_motivo_falha`) viraram FAIL; com a cópia original (não mutada) do módulo, as mesmas 4 voltaram a PASS. As 2 restantes (`completo_passa`, `nao_retroativo`) não discriminaram nesse harness isolado por dependerem de `workflow-rules.yaml` resolvido por caminho relativo ao script (ausente na cópia de scratchpad) — a execução real do pytest, dentro do repositório, já confirma as 6 passando (linha "Saída" desta própria linha). | Sim (4/6 diretas; 2/6 cobertas pela execução real in-repo) | `_framework/tests/test_validate_doc.py:224` (e 231/242/250/260/269) | automatizado |
| 1 | 3 | `grep -n "Requisitos transversais (sweep)" _framework/rules/workflow-rules.yaml` | linhas 24 e 1181 — 2 ocorrências | Mutação real: linha 1181 alterada para "Requisitos transversais TEMP-SENSOR" via Edit → contagem caiu para 1 (abaixo do "ao menos 2" exigido); restaurado, `git diff` vazio confirmado, contagem voltou a 2 | Sim | n/a (grep de string literal, sem asserção de código) | automatizado |
| 1 | 4 | `python3 _framework/scripts/render_prompts.py --check` | Todos os itens `✅`, `EXIT=0` (25 verificações, incl. cópias bundladas de `validate_doc.py` e `workflow-rules.yaml`) | Mutação real: linha extra `# TEMP-SENSOR-DTF-0039` acrescentada só na cópia bundlada de `validate_doc.py` via Edit → `❌ .../validate_doc.py: divergente de .../validate_doc.py.`, `EXIT=1`; restaurado, `git diff` vazio confirmado, `EXIT=0` de novo | Sim | `_framework/scripts/render_prompts.py:708` | automatizado |
| 1 | 5 | `diff _framework/templates/spec.template.md _framework/skills/doc-traceability-framework/templates/spec.template.md` | Sem saída, exit 0 | Mutação real: sufixo " TEMP-SENSOR" acrescentado só na cópia bundlada via Edit → diff mostrou divergência na linha 75, exit 1; restaurado, `git diff` vazio confirmado, exit 0 de novo | Sim | n/a (diff de arquivo, sem asserção de código) | automatizado |
| 1 | 6 | `python3 -m pytest _framework/ -q` | `180 passed in 26.44s` | Coberto pelos sensores individuais das linhas #1-5 acima; nenhuma mutação nova aplicada para esta linha | Sim | n/a | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | STRAT-DTF-0003 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md) |
