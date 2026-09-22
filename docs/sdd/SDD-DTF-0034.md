---
id: SDD-DTF-0034
type: SDD
title: "SKILL.md principal: corrige inconsistências, cobre lacunas de cobertura e enxuga (itens 3-5 de STRAT-DTF-0003)"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "STRAT-DTF-0003"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md"
consumption_instructions: "Sizing small — sem SPEC/RFC, compilado direto da tabela de prioridade e do texto de STRAT-DTF-0003 (itens 3, 4 e 5). Aplicar em _framework/skills/doc-traceability-framework/SKILL.md e replicar a mudança na cópia idêntica do kit público (mesmo path) antes de considerar a tarefa concluída — AGENTS.md do escopo _framework/ exige espelho arquivo a arquivo. Ordem interna: RF01-RF04 (item 3, correção) antes de RF10 (item 5, enxugamento), porque enxugar antes de corrigir reintroduziria o texto errado num lugar diferente."
supersedes: null
superseded_by: null
tags: [skill, doc-traceability-framework, consistencia, cobertura, enxugamento]
---

# SKILL.md principal: corrige inconsistências, cobre lacunas de cobertura e enxuga

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar.

## Resumo executivo

O `SKILL.md` da skill principal (`_framework/skills/doc-traceability-framework/SKILL.md`)
tem afirmações que contradizem `_framework/rules/workflow-rules.yaml`
(fonte canônica) e o `AGENTS.md` gerado, referências de path
inconsistentes dentro do próprio arquivo, uma linha gendrada, e deixa de
cobrir 5 capacidades que o framework já tem mas que a skill nunca
menciona — na prática invisíveis para quem só lê o SKILL.md. Ao mesmo
tempo o arquivo tem 392 linhas, boa parte delas duplicando conteúdo que
já está no YAML. Esta SDD corrige, cobre e enxuga tudo isso numa única
tacada, porque os três itens tocam o mesmo arquivo e a ordem importa
(enxugar antes de corrigir reintroduziria erro).

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small` (STRAT-DTF-0003 já declara e nenhum critério de
`decision_gates.rfc_to_adr` se aplica: é correção e reorganização de um
arquivo gerado por conteúdo, não mudança de padrão arquitetural).

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | O SKILL.md não deve afirmar um total numérico fixo de "tipos de documento" na abertura da seção de tipos, porque o total real depende de contar ou não os 2 tipos legados (`PRD`, `TS`) junto dos 8 ativos — a tabela deve listar os tipos por nome, sem título como "Os N tipos". |
| RF02 | O resumo do ciclo de vida de status no SKILL.md deve corresponder exatamente a `status_lifecycle.allowed_transitions` do YAML: não pode implicar que `approved` alcança `rejected` (só `in_review` alcança), e deve incluir a transição de volta `in_review → draft`. |
| RF03 | O SKILL.md não deve gendrar a IA que o executa (remover "vale para você mesma" e qualquer outra referência gendrada equivalente) — usar redação neutra. |
| RF04 | Toda referência a scripts, templates e ao arquivo de regras dentro do SKILL.md deve usar caminho relativo à raiz do bundle da própria skill (`scripts/...`, `references/...`, `templates/...`, `prompts/...`) — nunca o prefixo `_framework/`, que só existe no repositório central, não na cópia bundlada da skill. |
| RF05 | O SKILL.md deve mencionar `_framework/scripts/framework_check.py --auto` (ou o path relativo ao bundle, conforme RF04) como o comando que roda a auditoria de aderência (seção 11 do YAML) de forma mecanizada. |
| RF06 | O SKILL.md deve mencionar `parallel_plan.py` e o guia `docs/guias/paralelizacao-trilhas.md` como o mecanismo de derivação automática do grafo de dependências entre tasks (seção "Decomposição em tasks" do template de SDD). |
| RF07 | O SKILL.md deve mencionar a existência de hooks do framework (`guard_bash.sh`, pre-commit) como camada de enforcement que não depende da LLM seguir instrução — distinta da skill/procedimento, que depende. |
| RF08 | O SKILL.md deve mencionar o agente `sdd-verifier` como o mecanismo concreto de despacho da verificação de escopo (`gate_scope_verification`), citando a regra "quem implementou não verifica". |
| RF09 | O SKILL.md deve documentar o modo greenfield (`repository_status: none_yet`): quando se aplica, o que roda mesmo sem repositório de código (STRAT/RFC/ADR/SPEC) e o que fica bloqueado (SDD) até a transição para `active`. |
| RF10 | Após RF01-RF09, o SKILL.md deve ficar substancialmente mais enxuto: qualquer trecho que apenas repete, célula por célula ou linha por linha, conteúdo já completo no YAML (ex.: tabelas inteiras de gate, ciclo de vida) deve virar gatilho + ponteiro para `references/workflow-rules.yaml`, mantendo no SKILL.md só o que orienta a ação do dia a dia. |

## Especificação técnica consolidada

Arquivo único tocado (produto): `_framework/skills/doc-traceability-framework/SKILL.md`,
replicado sem divergência em `doc-traceability-framework` (kit público —
mesmo path, já que este repositório **é** o kit público; a cópia
espelhada fica em `_framework/skills/doc-traceability-framework/SKILL.md`
dentro do repositório central `doc-traceability-central`, que precisa
receber o mesmo diff numa tarefa separada, fora do escopo desta SDD, que
só cobre o repositório do kit).

- RF01: reescrever o cabeçalho da seção "Os 9 tipos de documento" para
  algo como "Os tipos de documento", sem número na frase, ou explicitar
  "8 tipos ativos + 2 legados (PRD, TS)" se um número for mantido.
- RF02: substituir o bloco de ciclo de vida resumido pelo texto exato
  das transições do YAML (seção 6), no mesmo formato usado em
  `AGENTS.md` gerado (linha "Transições válidas: ...") para não haver
  duas prosas divergentes descrevendo a mesma tabela.
- RF03: trocar "este gate vale para você mesma" por redação neutra, ex.
  "este gate vale para esta sessão" ou "vale para quem executa este
  framework".
- RF04: varrer o SKILL.md (`grep -n '_framework/' SKILL.md`) e remover o
  prefixo `_framework/` de toda referência a `scripts/`, `references/`,
  `templates/`, `prompts/` — a cópia bundlada da skill já vive dentro de
  `_framework/skills/doc-traceability-framework/`, então caminhos
  internos são relativos a essa raiz, não à raiz do repositório central.
- RF05-RF09: adicionar, na seção correspondente já existente do SKILL.md
  (auditoria → RF05; fluxo/tasks → RF06; gates → RF07; verificação de
  escopo → RF08; modelo de dois repositórios/onboarding → RF09), uma
  frase objetiva com o nome do script/agente/campo e o que ele faz —
  sem duplicar a explicação inteira, que já está no YAML ou no
  procedimento correspondente.
- RF10: depois de RF01-RF09 aplicados, reler o arquivo inteiro e cortar
  qualquer tabela ou bloco que reproduza o YAML sem adicionar orientação
  de ação — substituir por uma frase-gatilho + `Ver <seção> em
  references/workflow-rules.yaml`. Meta observável: o arquivo resultante
  deve ter menos linhas que o original (392) mesmo após as adições de
  RF05-RF09.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Corrigir contagem de tipos, ciclo de status, gênero e paths internos | RF01, RF02, RF03, RF04 | `_framework/skills/doc-traceability-framework/SKILL.md` | |
| 2 | Cobrir lacunas de cobertura (5 menções novas) | RF05, RF06, RF07, RF08, RF09 | `_framework/skills/doc-traceability-framework/SKILL.md` | 1 |
| 3 | Enxugar removendo duplicação do YAML | RF10 | `_framework/skills/doc-traceability-framework/SKILL.md` | 1, 2 |
| 4 | Escrever teste de regressão do ciclo de status | RF02 | `_framework/tests/test_skill_md_consistency.py` | 1 |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — nenhuma afirmação de contagem fixa de tipos que contradiga `document_types`+`legacy_document_types` | `grep -n "tipos de documento" _framework/skills/doc-traceability-framework/SKILL.md` | Nenhuma linha com padrão `Os [0-9]+ tipos` |
| 2 | RF02 — ciclo de status do SKILL.md bate com `allowed_transitions` do YAML | `python3 -m pytest _framework/tests/test_skill_md_consistency.py::test_status_lifecycle_matches_yaml -v` | Passa |
| 3 | RF03 — sem linguagem gendrada | `grep -inE "você mesma|voce mesma" _framework/skills/doc-traceability-framework/SKILL.md` | Sem saída (exit code 1) |
| 4 | RF04 — sem prefixo `_framework/` em referência a scripts/references/templates/prompts dentro do SKILL.md | `grep -n "_framework/\(scripts\|references\|templates\|prompts\)/" _framework/skills/doc-traceability-framework/SKILL.md` | Sem saída (exit code 1) |
| 5 | RF05 — menciona `framework_check.py --auto` | `grep -n "framework_check.py --auto" _framework/skills/doc-traceability-framework/SKILL.md` | Ao menos 1 ocorrência |
| 6 | RF06 — menciona `parallel_plan.py` | `grep -n "parallel_plan.py" _framework/skills/doc-traceability-framework/SKILL.md` | Ao menos 1 ocorrência |
| 7 | RF07 — menciona hooks (`guard_bash.sh` ou "pre-commit") | `grep -inE "guard_bash.sh|pre-commit" _framework/skills/doc-traceability-framework/SKILL.md` | Ao menos 1 ocorrência |
| 8 | RF08 — menciona agente `sdd-verifier` | `grep -n "sdd-verifier" _framework/skills/doc-traceability-framework/SKILL.md` | Ao menos 1 ocorrência |
| 9 | RF09 — menciona `repository_status` / modo greenfield | `grep -inE "repository_status|greenfield" _framework/skills/doc-traceability-framework/SKILL.md` | Ao menos 1 ocorrência |
| 10 | RF10 — arquivo mais enxuto que o original (392 linhas) mesmo com as adições | `wc -l < _framework/skills/doc-traceability-framework/SKILL.md` | Valor menor que 392 |
| 11 | Paridade entre as duas cópias do kit (bundle da skill vs `_framework/` do próprio kit — este repositório contém ambas) | `diff _framework/skills/doc-traceability-framework/SKILL.md _framework/skills/doc-traceability-framework/SKILL.md` (ajustar para o segundo caminho real caso exista cópia duplicada dentro do próprio repo do kit; caso não exista segunda cópia local, documentar aqui e a paridade fica só com o repositório central, fora desta SDD) | Sem saída, ou nota explícita se não houver segunda cópia local |
| 12 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam |
| 13 | `render_prompts.py --check` continua passando (SKILL.md não é gerado, mas AGENTS.md/QUICKSTART.md não podem ter sido tocados por engano) | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência reportada |

## Instruções específicas para a IA implementadora

- Antes de editar, confirmar se este repositório (`doc-traceability-framework`)
  tem uma única cópia de `SKILL.md` ou duas (kit + espelho interno) —
  o critério 11 acima assume a possibilidade de duas; se houver só uma
  aqui, ajuste o comando de paridade para comparar contra a cópia do
  repositório central (`doc-traceability-central`) e registre isso como
  nota na Evidência de verificação, não como criétrio pulado.
- Criar `_framework/tests/test_skill_md_consistency.py` com pelo menos
  o teste `test_status_lifecycle_matches_yaml` citado no critério 2:
  parseia o texto do ciclo de vida do SKILL.md e compara contra
  `workflow-rules.yaml` carregado (não hardcode a tabela esperada no
  teste — leia do YAML, senão o teste não pega divergência futura).
- Não usar esta tarefa para tocar em `AGENTS.md`, `QUICKSTART.md` ou
  `workflow-rules.yaml` — são gerados ou são a fonte canônica,
  respectivamente, e nenhum requisito acima pede mudança neles.
- Não aproveitar para reescrever seções que não estão listadas em
  RF01-RF10, mesmo que pareçam candidatas a enxugamento — RF10 é sobre
  remover duplicação do YAML, não sobre reescrita de estilo geral.
- Replicar a mudança na cópia do kit dentro do repositório central
  (`doc-traceability-central/_framework/skills/doc-traceability-framework/SKILL.md`)
  é obrigatório por `AGENTS.md` de `_framework/`, mas acontece em sessão
  separada aberta nesse outro repositório — esta SDD e sua verificação
  de escopo cobrem só o repositório do kit.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] RF01-RF10 todos com trecho correspondente no SKILL.md editado.
- [ ] Único arquivo de produto tocado: `SKILL.md` + o teste novo
      (`test_skill_md_consistency.py`) — qualquer outro arquivo tocado é
      escopo não registrado (atualizar esta SDD) ou scope creep (remover).
- [ ] Nenhuma mudança em `workflow-rules.yaml`, `AGENTS.md`, `QUICKSTART.md`
      ou nos scripts de render/validate.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** {preencher na sessão de verificação — quem implementou (esta sessão) não verifica}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `grep -n "Os [0-9]\+ tipos" SKILL.md` | sem saída (exit 1) | — | Sim |
| 2 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py::test_status_lifecycle_matches_yaml -v` | `1 passed in 0.12s` | — | Sim |
| 3 | `grep -inE "você mesma\|voce mesma" SKILL.md` | sem saída (exit 1) | — | Sim |
| 4 | `grep -n "_framework/\(scripts\|references\|templates\|prompts\)/" SKILL.md` | sem saída (exit 1) | — | Sim |
| 5 | `grep -c "framework_check.py --auto" SKILL.md` | `1` | — | Sim |
| 6 | `grep -c "parallel_plan.py" SKILL.md` | `1` | — | Sim |
| 7 | `grep -icE "guard_bash.sh\|pre-commit" SKILL.md` | `1` | — | Sim |
| 8 | `grep -c "sdd-verifier" SKILL.md` | `1` | — | Sim |
| 9 | `grep -icE "repository_status\|greenfield" SKILL.md` | `2` | — | Sim |
| 10 | `wc -l < SKILL.md` | `391` (< 392) | — | Sim |
| 11 | `find . -maxdepth 3 -iname "SKILL.md" -path "*doc-traceability-framework*" -not -path "*/worktrees/*"` | só `_framework/skills/doc-traceability-framework/SKILL.md` — nenhuma segunda cópia local neste repositório | — | Sim, com nota: paridade só existe com `doc-traceability-central`, fora do escopo desta SDD (repositório separado) |
| 12 | `python3 -m pytest _framework/ -q` | `121 passed in 4.87s` | — | Sim |
| 13 | `python3 _framework/scripts/render_prompts.py --check` | todos os itens `✅ ... em dia/sincronizado`, nenhuma divergência; AGENTS.md/QUICKSTART.md não tocados | — | Sim |

Sensor de discriminação (RF02): quebrei deliberadamente a frase
"Transições válidas" no SKILL.md (removi `draft` de `in_review →
approved, rejected, draft`) e confirmei que
`test_status_lifecycle_matches_yaml` falha
(`AssertionError: SKILL.md diz que 'in_review' vai para
{'approved', 'rejected'}, mas workflow-rules.yaml diz {'approved',
'rejected', 'draft'}`); revertido antes de rodar a suíte final acima.

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | STRAT-DTF-0003 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/00-strategy/STRAT-DTF-0003.md) |
