---
id: SDD-DTF-0040
type: SDD
title: "guia-tecnico.md: corrige drift acumulado (7 adições recentes nunca refletidas)"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs: []
consumption_instructions: "Sizing small — sem SPEC/RFC/ADR, achado de auditoria (usuário pediu para avaliar README/guias/exemplos vs. estado real do kit em 2.3.0). Fonte de cada RF é o próprio código/YAML atual, não um documento de origem único; por isso source_docs vazio. Aplicar em docs/guias/guia-tecnico.md e replicar a mudança na cópia idêntica do repositório central (doc-traceability-central/docs/guias/guia-tecnico.md) antes de considerar a tarefa concluída — docs/AGENTS.md do central declara docs/guias/ como espelhado."
supersedes: null
superseded_by: null
tags: [guia-tecnico, documentacao, drift, verify-sdd, gate-ci]
---

# guia-tecnico.md: corrige drift acumulado (7 adições recentes nunca refletidas)

> Este documento é COMPILADO a partir de achado de auditoria, não de
> `source_docs` — sizing `small`, sem SPEC/RFC de origem (ver
> `consumption_instructions`).

## Resumo executivo

`docs/guias/guia-tecnico.md` não foi atualizado nas últimas 8 SDDs do
kit (SDD-DTF-0032 a 0039, todas `implemented`). Duas classes de drift:
(a) uma afirmação hoje **falsa** — "nenhum [gate] é imposto por CI"
(linha 165), quando `ci_gate_verify_sdd.py` (SDD-DTF-0032) já bloqueia
merge de PR; (b) seis lacunas de cobertura — scripts novos, passo 0 do
`verify-sdd`, colunas novas da tabela de evidência, seção "sweep" do
gate de qualidade de conteúdo, e `lessons_check.py` — nunca mencionados.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`: é correção e cobertura de um guia narrativo já
existente, sem mudança de padrão arquitetural, sem alternativa técnica
concorrente a registrar, reversão trivial (reverter commit).

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
| RF01 | A frase de abertura da seção "7. Os gates obrigatórios" não deve afirmar que nenhum gate é imposto por CI — desde SDD-DTF-0032, `ci_gate_verify_sdd.py` bloqueia merge de PR que muda SDD para `implemented` sem verificação independente válida. |
| RF02 | A seção "9. Scripts disponíveis" deve citar os 5 scripts hoje ausentes da lista: `check_source_docs.py`, `ci_gate_verify_sdd.py`, `lessons_check.py`, `selftest.py`, `parallel_plan.py` — um comando de exemplo + comentário de uma linha cada, mesmo formato dos existentes. |
| RF03 | A árvore de pastas da seção "2. Estrutura de pastas" deve corrigir o nome do diretório de guias (hoje escrito `guides/`, o caminho real usado no resto do documento e no repositório é `docs/guias/`) e incluir `gate-ci-verify-sdd.md` na lista de guias. |
| RF04 | A seção "9.1 Verificação independente antes de `implemented`" deve descrever o passo "0. Fidelidade à origem" do procedimento `verify-sdd` (checagem de `source_docs` antes do passo de conformidade com a spec), a autoridade de despacho (só quem tem a feature inteira que vai a PR despacha a verificação) e o teto de 3 rodadas com escalonamento explícito na SDD quando a 3ª rodada não for PASS. |
| RF05 | A mesma seção 9.1 deve mencionar que a tabela de evidência de verificação tem, desde SDD-DTF-0036, colunas de `file:line` da asserção que resolve cada critério e do perfil declarado — não só "comando + saída real". |
| RF06 | O checklist da seção "7. Os gates obrigatórios" (gate de qualidade de conteúdo) deve incluir o item "sweep de requisitos transversais" (autorização, concorrência, idempotência, observabilidade, falha de dependência externa, validação de entrada, limite de volume/rate — cada um com `Destino` ou `n/a` + motivo), adicionado à SPEC pela SDD-DTF-0039. |
| RF07 | A seção "9.2 Quando um gate for violado" deve mencionar `lessons_check.py` e o campo opcional `**Chave de recorrência:**` como o mecanismo que já mecaniza a contagem de "2 projetos diferentes" da `lessons_policy`, hoje descrita só como decisão manual. |

## Especificação técnica consolidada

Arquivo único tocado (produto): `docs/guias/guia-tecnico.md`, replicado
sem divergência em `doc-traceability-central/docs/guias/guia-tecnico.md`
(fora do escopo desta SDD, tarefa separada no repositório central —
`docs/guias/` é espelhado igual a `_framework/`).

- RF01: reescrever a frase de abertura da seção 7 para distinguir os
  quatro gates narrativos (seguidos pela LLM/hook local) do gate de
  verificação de escopo, que desde SDD-DTF-0032 **também** tem uma
  camada de CI obrigatória (`ci_gate_verify_sdd.py`) — não remover a
  frase, corrigi-la para não afirmar o oposto do real.
- RF02: adicionar ao bloco de código da seção 9, mesmo estilo das
  entradas existentes (comentário de uma linha + comando), os 5 scripts
  listados, na ordem em que aparecem no fluxo (fidelidade à origem →
  gate de CI → selftest → lessons → paralelismo).
- RF03: trocar `guides/` por `docs/guias/` na árvore da seção 2 (linha
  47 atual) e adicionar `gate-ci-verify-sdd.md` à lista entre parênteses.
- RF04: acrescentar um parágrafo ou item de lista à seção 9.1, antes ou
  depois do item "3." existente, descrevendo passo 0 (fidelidade à
  origem via `check_source_docs.py` + checklist estruturado de
  correspondência SPEC↔SDD), autoridade de despacho e teto de 3 rodadas
  — sem reescrever `_framework/procedures/verify-sdd.md` em prosa
  completa, só nomear os três pontos e apontar para o procedimento.
- RF05: uma frase adicional no mesmo item "2." da lista (ou item novo)
  citando as colunas `file:line` e `perfil` da tabela de evidência.
- RF06: adicionar uma linha ao bloco de checklist da seção 7 (gate de
  qualidade de conteúdo), mesmo formato `[ ] ...` das existentes.
- RF07: uma frase adicional na seção 9.2 citando `lessons_check.py` e o
  campo `**Chave de recorrência:**`, sem reescrever a política de
  promoção já descrita ali.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Corrigir afirmação falsa sobre CI (seção 7) | RF01 | `docs/guias/guia-tecnico.md` | |
| 2 | Corrigir path de guias e árvore de pastas (seção 2) | RF03 | `docs/guias/guia-tecnico.md` | |
| 3 | Cobrir os 5 scripts novos (seção 9) | RF02 | `docs/guias/guia-tecnico.md` | |
| 4 | Cobrir passo 0, despacho, teto de rodadas e colunas novas de evidência (seção 9.1) | RF04, RF05 | `docs/guias/guia-tecnico.md` | |
| 5 | Cobrir checklist de sweep (seção 7) | RF06 | `docs/guias/guia-tecnico.md` | 1 |
| 6 | Cobrir lessons_check.py (seção 9.2) | RF07 | `docs/guias/guia-tecnico.md` | |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — seção 7 não afirma mais que nenhum gate é imposto por CI | `grep -n "nenhum é imposto por CI" docs/guias/guia-tecnico.md` | Sem saída (exit code 1) |
| 2 | RF01 — seção 7 menciona `ci_gate_verify_sdd.py` | `grep -n "ci_gate_verify_sdd.py" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 3 | RF02 — os 5 scripts citados | `grep -cE "check_source_docs\.py\|ci_gate_verify_sdd\.py\|lessons_check\.py\|selftest\.py\|parallel_plan\.py" docs/guias/guia-tecnico.md` | 5 ou mais |
| 4 | RF03 — path de guias corrigido | `grep -n "guides/" docs/guias/guia-tecnico.md` | Sem saída (exit code 1) |
| 5 | RF03 — gate-ci-verify-sdd.md citado na árvore/lista de guias | `grep -n "gate-ci-verify-sdd.md" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 6 | RF04 — passo 0 mencionado | `grep -inE "fidelidade . origem\|passo 0" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 7 | RF04 — autoridade de despacho mencionada | `grep -in "autoridade de despacho" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 8 | RF04 — teto de 3 rodadas mencionado | `grep -in "3 rodadas" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 9 | RF05 — colunas file:line e perfil mencionadas | `grep -in "file:line" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 10 | RF06 — sweep no checklist da seção 7 | `grep -in "sweep" docs/guias/guia-tecnico.md` | Ao menos 1 ocorrência |
| 11 | RF07 — lessons_check.py e Chave de recorrência mencionados | `grep -cE "lessons_check\.py\|Chave de recorrência" docs/guias/guia-tecnico.md` | 2 ou mais |
| 12 | Nenhuma regressão de sintaxe Markdown (links/blocos de código balanceados) | `python3 -c "import re,sys; t=open('docs/guias/guia-tecnico.md').read(); assert t.count('\`\`\`')%2==0, 'blocos de código desbalanceados'"` | Sem `AssertionError` |
| 13 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam |
| 14 | `render_prompts.py --check` continua passando (arquivo não é gerado, mas nada mais pode ter sido tocado por engano) | `python3 _framework/scripts/render_prompts.py --check` | Sem divergência reportada |

## Instruções específicas para a IA implementadora

- Único arquivo de produto: `docs/guias/guia-tecnico.md`. Não editar
  `guia-nao-tecnico.md`, `paralelizacao-trilhas.md`,
  `gate-ci-verify-sdd.md`, `workflow-rules.yaml`, `AGENTS.md` nem
  `QUICKSTART.md` — nenhum RF pede mudança neles.
- RF01-RF07 são adições/correções pontuais, não reescrita de estilo —
  preservar tom, estrutura de seções e numeração existentes.
- Replicar a mudança em
  `doc-traceability-central/docs/guias/guia-tecnico.md` é obrigatório
  (`docs/AGENTS.md` do central: `docs/guias/` é espelhado), mas acontece
  em sessão separada nesse outro repositório — esta SDD e sua
  verificação de escopo cobrem só este repositório (o kit).

## Verificação de escopo (nada a mais, nada a menos)

- [x] RF01-RF07 todos com trecho correspondente em `guia-tecnico.md`.
- [x] Único arquivo de produto tocado: `docs/guias/guia-tecnico.md`.
- [x] Nenhuma mudança em `workflow-rules.yaml`, scripts ou outros guias.

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

**Verificador independente:** sim

Tabela desta sessão implementadora abaixo (rodada 0, informativa) seguida
da rodada de verificação independente (rodada 1, autoritativa para o
gate `gate_scope_verification`).

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado |
|---|---|---|---|
| 1 | RF01 | `grep -n "nenhum é imposto por CI" docs/guias/guia-tecnico.md` | Sem saída (exit 1) |
| 2 | RF01 | `grep -n "ci_gate_verify_sdd.py" docs/guias/guia-tecnico.md \| wc -l` | `3` |
| 3 | RF02 | `grep -cE "check_source_docs\.py\|ci_gate_verify_sdd\.py\|lessons_check\.py\|selftest\.py\|parallel_plan\.py" docs/guias/guia-tecnico.md` | `10` |
| 4 | RF03 | `grep -n "guides/" docs/guias/guia-tecnico.md` | Sem saída (exit 1) |
| 5 | RF03 | `grep -n "gate-ci-verify-sdd.md" docs/guias/guia-tecnico.md` | linha 51 |
| 6 | RF04 | `grep -inE "fidelidade . origem\|passo 0" docs/guias/guia-tecnico.md \| wc -l` | `3` |
| 7 | RF04 | `grep -in "autoridade de despacho" docs/guias/guia-tecnico.md` | linha 357 |
| 8 | RF04 | `grep -in "3 rodadas" docs/guias/guia-tecnico.md` | linha 360 |
| 9 | RF05 | `grep -in "file:line" docs/guias/guia-tecnico.md` | linha 349 |
| 10 | RF06 | `grep -in "sweep" docs/guias/guia-tecnico.md` | linha 198 |
| 11 | RF07 | `grep -cE "lessons_check\.py\|Chave de recorrência" docs/guias/guia-tecnico.md` | `5` |
| 12 | Markdown balanceado | `python3 -c "t=open('docs/guias/guia-tecnico.md').read(); assert t.count('\`\`\`')%2==0"` | Sem `AssertionError` |
| 13 | Suíte completa | `python3 -m pytest _framework/ -q` | `180 passed in 27.17s` |
| 14 | `render_prompts.py --check` | `python3 _framework/scripts/render_prompts.py --check \| grep "❌"` | Sem saída (exit 1) |

### Rodada 1 — verificação independente

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | 1 | `grep -n "nenhum é imposto por CI" docs/guias/guia-tecnico.md` | sem saída, exit 1 | Reversão manual da frase (seção 7) fez o grep casar (exit 0); restaurado, voltou a exit 1 | Sim | `docs/guias/guia-tecnico.md:167` | manual |
| 1 | 2 | `grep -n "ci_gate_verify_sdd.py" docs/guias/guia-tecnico.md` | linhas 46, 170, 295 | coberto pelo sensor do #1 (mesma edição) | Sim | `docs/guias/guia-tecnico.md:170` | manual |
| 1 | 3 | `grep -cE "check_source_docs\.py\|ci_gate_verify_sdd\.py\|lessons_check\.py\|selftest\.py\|parallel_plan\.py" docs/guias/guia-tecnico.md` | `10` | sem teste automatizado | Sim | `docs/guias/guia-tecnico.md:46` | manual |
| 1 | 4 | `grep -n "guides/" docs/guias/guia-tecnico.md` | sem saída, exit 1 | Reversão manual `docs/guias/`→`guides/` fez o grep casar (exit 0); restaurado, voltou a exit 1 | Sim | `docs/guias/guia-tecnico.md:50` | manual |
| 1 | 5 | `grep -n "gate-ci-verify-sdd.md" docs/guias/guia-tecnico.md` | linha 51 | coberto pelo sensor do #4 | Sim | `docs/guias/guia-tecnico.md:51` | manual |
| 1 | 6 | `grep -inE "fidelidade . origem\|passo 0" docs/guias/guia-tecnico.md` | 3 ocorrências (289, 336, 343) | sem teste automatizado | Sim | `docs/guias/guia-tecnico.md:336` | manual |
| 1 | 7 | `grep -in "autoridade de despacho" docs/guias/guia-tecnico.md` | linha 357 | sem teste automatizado | Sim | `docs/guias/guia-tecnico.md:357` | manual |
| 1 | 8 | `grep -in "3 rodadas" docs/guias/guia-tecnico.md` | linha 360 | sem teste automatizado | Sim | `docs/guias/guia-tecnico.md:360` | manual |
| 1 | 9 | `grep -in "file:line" docs/guias/guia-tecnico.md` | linha 349 | sem teste automatizado | Sim | `docs/guias/guia-tecnico.md:349` | manual |
| 1 | 10 | `grep -in "sweep" docs/guias/guia-tecnico.md` | linha 198 | Reversão manual "Sweep de requisitos transversais"→"Requisitos transversais" fez o grep falhar (exit 1); restaurado, voltou a casar | Sim | `docs/guias/guia-tecnico.md:198` | manual |
| 1 | 11 | `grep -cE "lessons_check\.py\|Chave de recorrência" docs/guias/guia-tecnico.md` | `5` | sem teste automatizado | Sim | `docs/guias/guia-tecnico.md:377` | manual |
| 1 | 12 | `python3 -c "t=open('docs/guias/guia-tecnico.md').read(); assert t.count('\`\`\`')%2==0"` | sem `AssertionError`, exit 0 | n/a — checagem estrutural | Sim | `n/a` | n/a |
| 1 | 13 | `python3 -m pytest _framework/ -q` | `180 passed in 26.88s` | n/a — suíte pré-existente | Sim | `n/a` | automatizado |
| 1 | 14 | `python3 _framework/scripts/render_prompts.py --check` | todos os arquivos "sincronizado", exit 0 | n/a | Sim | `n/a` | automatizado |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (vazio — achado de auditoria, sem documento de origem único) |
