---
id: SDD-DTF-0006
type: SDD
title: "Memória portável: procedimentos neutros e capacidades por contrato"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-08-29"
relates_to: [SPEC-DTF-0001, ADR-DTF-0001]
source_docs:
  - id: "SPEC-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0001.md"
  - id: "ADR-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0001.md"
consumption_instructions: "Leia 'Especificação técnica consolidada' inteira antes de tocar em arquivo. Esta é a etapa 1 de 4 de SPEC-DTF-0001 (RF04, RF05, RF06) — etapas 0 (SDD-DTF-0001) já implementada; etapas 2 e 3 (ADAPTERS gerados, sync_copies, RENDERINGS ampliada) ficam para SDDs seguintes e não devem ser antecipadas aqui."
supersedes: null
superseded_by: null
tags: [neutralidade, memoria, adocao]
---

# Memória portável: procedimentos neutros e capacidades por contrato

## Resumo executivo

As três capacidades de continuidade entre sessões (`handover`, `pickup`,
`verify-sdd`) só existem hoje como `SKILL.md` no formato específico do
Claude Code — normativa e formato de fornecedor misturados no mesmo
arquivo. Esta SDD move o conteúdo normativo para
`_framework/procedures/*.md` (markdown neutro, sem front-matter de
skill), reescreve a seção 12 do YAML canônico como contratos de
capacidade (`trigger`, `produces`, `invariants`, `procedure`) em vez de
nomear a skill diretamente, e reduz cada `SKILL.md` a um stub curto que
aponta para o procedimento — para que trocar de ferramenta de IA no meio
de um trabalho não perca a memória acumulada de onde parar e retomar.

## Decisão(ões) de arquitetura aplicável(is)

`ADR-DTF-0001` — três camadas, fornecedor confinado a adaptadores
gerados. Aplicado aqui: `_framework/procedures/` é camada 2 (editável por
gente, neutra de fornecedor); `skills/*/SKILL.md` é camada 3
(renderização por fornecedor). Nesta etapa a geração automática do stub
por `render_prompts.py` fica para a etapa 2/3 (`ADAPTERS`, RF07) — aqui o
stub é escrito à mão já no formato final que a etapa 2 vai passar a
gerar, para não bloquear RF04/RF05/RF06 na conclusão de RF07.

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0001`:

- **RF04** — Cada capacidade operacional tem procedimento neutro em
  `_framework/procedures/`. Deve existir `procedures/handover.md`,
  `procedures/pickup.md` e `procedures/verify-sdd.md`, em markdown sem
  front-matter de skill, cada um contendo as mesmas seções normativas do
  `SKILL.md` que substitui.
- **RF05** — A seção 12 do YAML declara capacidade por contrato, não por
  nome de skill. Onde uma capacidade de continuidade estiver declarada,
  o sistema deve expor os campos `trigger`, `produces`, `invariants` e
  `procedure`, e nenhum valor desses campos deve conter nome de
  fornecedor.
- **RF06** — Cada `skills/*/SKILL.md` é um stub que aponta para o
  procedimento. Corpo com no máximo 25 linhas, sem regra normativa
  própria.

Casos de borda consolidados (da Parte 1 de `SPEC-DTF-0001`, aplicáveis a
esta etapa):

- Procedimento referenciado por `ai_capabilities.procedure` inexistente:
  fora do escopo mecânico desta SDD — `check_capability_procedures` (que
  verifica isso em `check_renderings.py`) é RF09, etapa 3. Nesta etapa a
  conferência é manual: os três procedimentos são criados antes de a
  seção 12 referenciá-los.
- Perda de conteúdo normativo na migração `SKILL.md` → `procedures/`:
  mitigada por diff manual registrado na "Evidência de verificação"
  desta SDD antes de qualquer remoção de conteúdo do `SKILL.md` original
  (risco já registrado em `SPEC-DTF-0001`, seção "Riscos operacionais").

## Especificação técnica consolidada

**Arquivos novos — `_framework/procedures/`:**

- `handover.md` — migra o corpo normativo de
  `_framework/skills/handover/SKILL.md` (seções "Quando usar", "Onde o
  HANDOFF.md vai", "Template", "Regras", "Saída para o usuário|IA"),
  reescrito em markdown neutro: sem front-matter YAML de skill (`name`,
  `description`), sem instrução formatada como "print" de chat — vira
  "ao final, comunique apenas: ...". O `Template` (cabeçalhos fixos que
  `pickup` depende para parsear) é preservado byte a byte no bloco de
  código.
- `pickup.md` — migra o corpo normativo de
  `_framework/skills/pickup/SKILL.md` (seções "Onde procurar", "Ao
  carregar o HANDOFF", "Regras"), mesma regra de neutralidade.
- `verify-sdd.md` — migra o corpo normativo de
  `_framework/skills/verify-sdd/SKILL.md` (seções "Entrada",
  "Procedimento" 1-4, "Checagem mecânica complementar", "Red flags"),
  mesma regra de neutralidade. O aviso em blockquote
  ("QUEM IMPLEMENTOU NÃO VERIFICA...") é preservado como primeira linha
  do corpo.

**`_framework/rules/workflow-rules.yaml`:**

- Seção 12 (`capabilities`) — as três entradas de continuidade
  (`write_handover` e as duas capacidades implícitas de retomada e
  verificação que hoje só existem como skill, não como `capabilities.id`
  — `pickup` e `verify_sdd_independently`, já listado) passam do schema
  atual (`id`, `description`) para: `id`, `trigger` (texto: quando a
  capacidade dispara), `produces` (texto: artefato ou efeito gerado),
  `invariants` (lista: regras que não podem ser violadas ao executar),
  `procedure` (caminho relativo a partir de `_framework/`, ex.:
  `procedures/handover.md`). As demais entradas de `capabilities`
  (`create_document`, `evaluate_rfc_gate`, etc.) não são tocadas nesta
  SDD — a migração de schema aplica-se só às três capacidades cobertas
  por RF04 (`write_handover`, e as capacidades de pickup e
  verify-sdd, que ganham `id: pickup_handoff` e
  `id: verify_sdd_independently` já existente reaproveitado com o schema
  novo).
- Seção 17 (`handover_protocol`) — passa a referenciar
  `_framework/procedures/handover.md` e `_framework/procedures/pickup.md`
  como fonte normativa, mantendo o conteúdo estrutural
  (`when_to_trigger`, `artifact`, `content_rule`, `no_placeholder`,
  `pickup_rule`, `relationship_with_gates`) como resumo — não duplica o
  procedimento inteiro, aponta para ele.

**`_framework/skills/{handover,pickup,verify-sdd}/SKILL.md`:**

- Front-matter (`name`, `description`) mantido — é o que o Claude Code
  usa para descobrir a skill.
- Corpo reduzido a: uma frase dizendo o que a skill faz, uma linha
  "Procedimento normativo: `_framework/procedures/{nome}.md`" e, se
  necessário para o Claude Code localizar o arquivo a partir da skill,
  o caminho relativo de dentro de `skills/{nome}/` até
  `../../procedures/{nome}.md`. Máximo 25 linhas de corpo (fora
  front-matter).
- Nenhuma seção normativa própria (sem "Regras", sem "Template", sem
  "Procedimento" detalhado) — isso agora vive só em `procedures/`.

**Cópia dentro da skill** (`skills/doc-traceability-framework/`): a
sincronização automática (`sync_copies`) é RF08, etapa 3. Nesta etapa,
se `_framework/procedures/` precisar existir também como referência
dentro dessa skill, a cópia é feita manualmente e registrada aqui — mas
o escopo de RF04/05/06 não exige isso (a skill `doc-traceability-framework`
copia hoje `scripts/` e `workflow-rules.yaml`, não os `SKILL.md` de
outras skills), então **nenhuma alteração** é esperada em
`skills/doc-traceability-framework/`.

**Paridade entre repositórios (RF11):** todo arquivo acima é criado/
alterado nos dois repositórios (`doc-traceability-framework` e
`doc-traceability-central/_framework`), na mesma branch de trabalho,
antes do PR.

**Artefato derivado tocado como efeito colateral:** `docs/especificacao.md`
é regenerado por `render_prompts.py` sempre que `workflow-rules.yaml`
muda — a alteração da seção 12/17 nesta etapa o inclui no diff nos dois
repositórios, sem edição manual. Não é escopo de código desta SDD, é
consequência mecânica já coberta por `SDD-DTF-0005`; registrado aqui
para que "todo arquivo do diff aparece na SDD" não exija julgamento
extra do verificador. (Acrescentado após a verificação independente —
ver `validation.md`, "Descompassos encontrados".)

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF04 — os três procedimentos existem | `ls _framework/procedures/{handover,pickup,verify-sdd}.md` | 3 arquivos |
| 2 | RF04 — sem front-matter de skill | `head -1 _framework/procedures/handover.md \| grep -c '^---$'` | `0` |
| 3 | RF04 — template do HANDOFF preservado | `diff <(sed -n '/^```markdown$/,/^```$/p' _framework/skills/handover/SKILL.md.bak) <(sed -n '/^```markdown$/,/^```$/p' _framework/procedures/handover.md)` (`.bak` = cópia do `SKILL.md` original antes da edição) | sem saída |
| 4 | RF05 — schema de contrato nas 3 capacidades de continuidade | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); caps={c['id']:c for c in d['capabilities']}; assert all(k in caps['write_handover'] for k in ('trigger','produces','invariants','procedure'))"` | sem erro (exit 0) |
| 5 | RF05 — nenhum valor cita fornecedor | `grep -iE "claude|cursor|copilot|codex|gemini" _framework/rules/workflow-rules.yaml \| grep -A0 -B0 "trigger:\|produces:\|invariants:\|procedure:"` | sem saída |
| 6 | RF06 — stub dentro do limite | `for f in _framework/skills/{handover,pickup,verify-sdd}/SKILL.md; do awk '/^---$/{c++} c==2{n++} END{print n-1}' "$f"; done` | `≤ 25` nas 3 linhas |
| 7 | RF06 — stub sem seção normativa própria | `grep -c "^## Regras$\|^## Template$\|^## Procedimento$" _framework/skills/{handover,pickup,verify-sdd}/SKILL.md` | `0` nos 3 |
| 8 | RF06 — stub aponta para o procedimento | `grep -l "procedures/" _framework/skills/{handover,pickup,verify-sdd}/SKILL.md \| wc -l` | `3` |
| 9 | Regressão | `python3 _framework/scripts/framework_check.py --auto` | exit 0 |
| 10 | Paridade (RF11) | `diff -r --exclude=__pycache__ _framework/ /home/michel/doc-traceability-central/_framework/` | sem saída |

Sensor de discriminação: critérios 2, 6 e 7 têm o caso negativo
verificável na própria natureza do comando (front-matter presente,
contagem de linha, grep de seção) — não precisam de sensor de
regressão-introduzida-e-revertida porque medem uma propriedade estática
do arquivo final, não comportamento de código. Critério 4 é o único com
lógica executável (parse do YAML); seu sensor é: reverter um dos quatro
campos do contrato e reexecutar — deve falhar com `AssertionError`.

## Instruções específicas para a IA implementadora

- Migração é de **conteúdo**, não reescrita livre — o texto normativo dos
  três `SKILL.md` atuais vai para `procedures/`, com ajustes mínimos só
  para remover referência a "esta skill" e a formato de chat específico
  do Claude Code (ex.: instrução de "print" vira "comunique").
- **NÃO** implementar `ADAPTERS`, `render_adapter` nem `sync_copies` —
  são RF07/RF08, etapa 2/3, fora do escopo desta SDD. O stub do
  `SKILL.md` é escrito à mão aqui.
- **NÃO** alterar `RENDERINGS` em `check_renderings.py` nem criar
  `check_capability_procedures` — é RF09, etapa 3.
- **NÃO** tocar nas outras entradas de `capabilities` (seção 12) além das
  três de continuidade — `create_document`, `evaluate_rfc_gate` etc.
  ficam no schema atual (`id`, `description`) até SDD futura decidir
  migrá-las ou não.
- Antes de editar cada `SKILL.md`, salve uma cópia (`cp arquivo
  arquivo.bak` fora do controle de versão, ou `git show HEAD:caminho`)
  para o diff do critério 3 — **não use `git checkout <arquivo>`** para
  comparar nem desfazer teste, isso restaura o HEAD e apaga edição em
  andamento (lição registrada em `SDD-DTF-0005`).
- Replicar toda alteração nos dois repositórios antes de abrir PR — RF11
  é critério desta etapa, não só da última.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0006`.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Todo arquivo tocado aparece em "Especificação técnica consolidada"
      (`docs/especificacao.md` acrescentado após o descompasso encontrado
      na verificação — ver acima).
- [x] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** sim — subagente separado, sem leitura do
histórico da sessão implementadora. Tabela completa e sensor de
discriminação registrados em `docs/sdd/validation.md`; veredito **PASS**.
Resumo:

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `ls _framework/procedures/{handover,pickup,verify-sdd}.md` (kit e central) | 3 arquivos nos dois repos | estático | sim |
| 2 | `head -1 procedures/handover.md \| grep -c '^---$'` | `0` nos dois | estático | sim |
| 3 | diff do bloco `Template` entre `SKILL.md` (base) e `procedures/handover.md` | sem saída (diff vazio) nos dois | comparação textual | sim |
| 4 | parse do contrato (`trigger`/`produces`/`invariants`/`procedure`) em `write_handover` | exit 0 | **sensor**: campo renomeado via `Edit` → `AssertionError`; desfeito → exit 0 de novo | sim |
| 5 | grep por nome de fornecedor nos campos de contrato | sem saída nos dois | estático | sim |
| 6 | contagem de linhas de corpo dos 3 stubs | `5, 5, 7` (≤25) nos dois repos | estático | sim |
| 7 | grep por seção normativa própria nos stubs | `0` nos 3, nos dois repos | estático | sim |
| 8 | grep por referência a `procedures/` nos stubs | `3` nos dois | sem sensor previsto | sim |
| 9 | `framework_check.py --auto` | exit 0 nos dois repos | sem sensor previsto | sim |
| 10 | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída | sem sensor previsto | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0001, ADR-DTF-0001 |
| Etapa | 1 de 4 de SPEC-DTF-0001 (RF04, RF05, RF06) |
| Branch | `sdd/SDD-DTF-0006-memoria-portavel` |
