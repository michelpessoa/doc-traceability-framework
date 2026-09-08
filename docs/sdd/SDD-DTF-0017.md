---
id: SDD-DTF-0017
type: SDD
title: "QUICKSTART e guia não-técnico ficam consistentes sobre os 4 níveis de sizing"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-08"
updated: "2026-09-08"
relates_to: []
source_docs: []
consumption_instructions: "Sizing small — STRAT-DTF-0002 já concluiu que não precisa de RFC/ADR. Toca 2 arquivos: função build_quickstart() em render_prompts.py (QUICKSTART.md é gerado, não editar à mão) e docs/guias/guia-nao-tecnico.md (escrito à mão). Depois de implementar no kit, sincronizar _framework/ e docs/guias/ pra cópia do repo central (doc-traceability-central) em PR separado — mesmo padrão já usado pra SDD-DTF-0016."
supersedes: null
superseded_by: null
tags: [documentacao, ux, onboarding]
---

# QUICKSTART e guia não-técnico ficam consistentes sobre os 4 níveis de sizing

## Resumo executivo

`STRAT-DTF-0002` levantou 2 furos nos documentos de entrada: `QUICKSTART.md`
só explica `small`/`medium`, nunca menciona `large`/`complex`/RFC/ADR;
`guia-nao-tecnico.md` funde `large` e `complex` numa única categoria em
prosa ("Grande"), perdendo a distinção que dispara STRAT. Os outros 3
documentos de entrada (`README.md`, `guia-tecnico.md`,
`docs/especificacao.md`) já cobrem os 4 níveis corretamente — não são
tocados aqui.

`sizing: small` — 2 arquivos, sem impacto arquitetural, sem mudar
comportamento do framework, só conteúdo de documentação. `source_docs: []`
por decisão (STRAT-DTF-0002 já concluiu que não precisa de RFC/ADR), não
omissão.

## Decisão(ões) de arquitetura aplicável(is)

Nenhuma — correção de conteúdo de documentação, sem ADR.

## Requisitos consolidados

- **RF1**: `QUICKSTART.md` (gerado por `build_quickstart()` em
  `_framework/scripts/render_prompts.py`), seção "Primeiro trabalho", item
  2, passa a mencionar `large`/`complex` → RFC (e ADR, se aplicável) antes
  da SPEC, com referência a `docs/guias/guia-tecnico.md` para a tabela
  completa.
- **RF2**: `docs/guias/guia-nao-tecnico.md`, seção "Nem toda mudança gera
  todos esses documentos", separa "Grande" (`large`) de uma categoria nova
  em prosa pra `complex` — mesmo critério de `guia-tecnico.md` (vários
  critérios ao mesmo tempo, cross-team, ou direção estratégica ainda
  inexistente), com a mesma consequência prática: registrar a direção
  antes da RFC.

Casos de borda: nenhum — mudança é aditiva em ambos os arquivos, não
remove nem reordena conteúdo existente.

Fora de escopo: `README.md`, `guia-tecnico.md`, `docs/especificacao.md`
(já corretos, confirmado por `grep -i sizing` na sessão que gerou
`STRAT-DTF-0002`); qualquer mudança ao mecanismo de `sizing` em si
(`_framework/rules/workflow-rules.yaml`), só à prosa que o explica.

## Especificação técnica consolidada

**`_framework/scripts/render_prompts.py`**, dentro de `build_quickstart()`,
item 2 da lista "Primeiro trabalho" (linhas atuais ~512-513):

```python
"2. `small` → só a SDD, em `docs/sdd/` do repositório de código.",
"   `medium` → SPEC no repositório central, depois a SDD. `large`/",
"   `complex` → RFC (e ADR, se aplicável) antes da SPEC — ver",
"   `docs/guias/guia-tecnico.md` para a tabela completa.",
```

Depois de editar, rodar `python3 _framework/scripts/render_prompts.py`
(sem `--check`) pra regenerar `QUICKSTART.md` — nunca editar o `.md`
gerado à mão.

**`docs/guias/guia-nao-tecnico.md`**, seção "Nem toda mudança gera todos
esses documentos" — troca o bullet único "Grande" por dois bullets:

```markdown
- **Grande** (mexe em como o sistema é montado, é cara de desfazer, afeta
  vários times, ou troca uma tecnologia): ganha RFC e ADR antes.
- **Muito grande** (mais de um desses motivos ao mesmo tempo, afeta vários
  times ao mesmo tempo, ou a ideia ainda nem tem direção definida): antes
  da RFC, o time registra a direção num documento separado — só então
  parte pra RFC e ADR.
```

## Tratamento de erro por contrato

Não aplicável — documentação estática, sem lógica de execução além da
geração mecânica de `QUICKSTART.md`.

## Estratégia de teste

| RF-ID | Tipo de teste | Comando |
|---|---|---|
| RF1 | Leitura direta + regeneração | `python3 _framework/scripts/render_prompts.py --check` (confirma que o `.md` commitado bate com a função) |
| RF2 | Leitura direta | `grep -c "Muito grande" docs/guias/guia-nao-tecnico.md` → `1` |

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1 — QUICKSTART.md menciona large/complex | `grep -A3 "small.*só a SDD" QUICKSTART.md` | Linhas citam `large`/`complex` e RFC/ADR |
| 2 | RF1 — arquivo gerado bate com a função | `python3 _framework/scripts/render_prompts.py --check` | `exit 0` |
| 3 | RF2 — guia não-técnico separa large/complex | `grep -c "Muito grande" docs/guias/guia-nao-tecnico.md` | `1` |
| 4 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` | `exit 0` |

## Plano de implementação

1. Editar `build_quickstart()` em `render_prompts.py` (item 2, RF1).
2. Rodar `render_prompts.py` (sem `--check`) pra regenerar `QUICKSTART.md`.
3. Editar `docs/guias/guia-nao-tecnico.md` (RF2).
4. Rodar `render_prompts.py --check` e `framework_check.py --auto` — os
   dois `exit 0` antes do commit, no kit.
5. Após merge no kit: sincronizar `_framework/` (RF1) e
   `docs/guias/guia-nao-tecnico.md` (RF2) para a cópia em
   `doc-traceability-central`, em PR separado — mesmo padrão de sync já
   usado para `SDD-DTF-0016`. `Refs: SDD-DTF-0017` também no commit de
   sync.

## Riscos operacionais e mitigação

Risco: esquecer o passo 5 (sync pro central) e a cópia real usada no dia a
dia ficar desatualizada — já aconteceu antes com `_framework/` (ver
`SDD-DTF-0016`/`LESSONS.md`). Mitigação: passo 5 é parte explícita desta
SDD, não trabalho separado — só fecha `implemented` depois do PR de sync
também mergeado.

## Plano de rollout / rollback

Rollout: 1 PR no kit (RF1+RF2), depois 1 PR de sync no central. Rollback:
reverter os 2 commits — nenhum efeito colateral, é só prosa.

## Observabilidade (métricas, logs, alertas)

Nenhuma — conteúdo de documentação, sem métrica de execução.

## Times consumidores impactados

Nenhum — mudança interna à documentação de onboarding do próprio kit.

## Instruções específicas para a IA implementadora

- Não editar `QUICKSTART.md` à mão — só `render_prompts.py`, depois
  regenerar.
- Não tocar `README.md`, `guia-tecnico.md`, `docs/especificacao.md` — já
  corretos, fora de escopo.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0017`.
- Branch dedicada a partir de `main`, PR — nunca commit direto em main
  (gate seção 14), nos dois repos.
- Não esquecer o PR de sync pro central (passo 5 do plano de
  implementação) — só então marcar `implemented`.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Os 2 requisitos consolidados têm código/conteúdo correspondente.
- [x] Único arquivo de código tocado é `render_prompts.py`; único `.md`
      editado à mão é `guia-nao-tecnico.md`; `QUICKSTART.md` só regenerado.
- [x] Nenhuma abstração, config extra ou refactor além do texto pedido.

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

- **Diff verificado:** `dec1b9f` (PR #49) + `a0b9f11` (PR #50, correção de status sem mudança de conteúdo), ambos em `main`. Sync para `doc-traceability-central`: `5b75ae2` (PR #46 do central).
- **Verificador independente:** sim.

| # | Critério | Comando | Saída | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF1 — QUICKSTART.md menciona large/complex | `grep -A3 "small.*só a SDD" QUICKSTART.md` | cita `large`/`complex`, RFC/ADR, `guia-tecnico.md` | Sim — reverter `build_quickstart()` + regenerar fez o texto sumir; restaurado, volta | Sim |
| 2 | RF1 — arquivo gerado bate com a função | `python3 _framework/scripts/render_prompts.py --check` | `exit 0` | trivial (idempotência) | Sim |
| 3 | RF2 — guia não-técnico separa large/complex | `grep -c "Muito grande" docs/guias/guia-nao-tecnico.md` | `1` | Sim — bullet removido temporariamente, `grep -c` caiu a `0`; restaurado, volta a `1` | Sim |
| 4 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` | sem sensor dedicado (regressão geral) | Sim |

Detalhe completo, conformidade requisito↔código nas duas direções e ressalvas em `docs/sdd/validation.md`.

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small, STRAT-DTF-0002 dispensou RFC/ADR) |
| Branch | `sdd/SDD-DTF-0017-sizing-docs-consistentes` |
