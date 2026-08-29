---
id: SDD-DTF-0007
type: SDD
title: "Adaptadores por fornecedor gerados integralmente"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-08-29"
relates_to: [SPEC-DTF-0001, ADR-DTF-0001, SDD-DTF-0006]
source_docs:
  - id: "SPEC-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0001.md"
  - id: "ADR-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0001.md"
consumption_instructions: "Leia 'Especificação técnica consolidada' inteira antes de tocar em arquivo. Etapa 2 de 4 de SPEC-DTF-0001 (RF07) — etapas 0 e 1 já implementadas (SDD-DTF-0001, SDD-DTF-0006); etapa 3 (sync_copies, RENDERINGS ampliada, ai_targets fora do schema) fica para SDD seguinte."
supersedes: null
superseded_by: null
tags: [neutralidade, adocao, geracao]
---

# Adaptadores por fornecedor gerados integralmente

## Resumo executivo

`prompts/universal.md`, `prompts/cursor/doc-framework.mdc` e
`prompts/copilot/copilot-instructions.md` só têm o "núcleo canônico"
gerado — o resto (18 seções de prosa em cada um, quase idênticas entre
si) é mantido à mão em três lugares. É a mesma falha que `ADR-DTF-0001`
já resolveu para `AGENTS.md`/`QUICKSTART.md`: divergência entre cópias
que deveriam dizer a mesma coisa. Esta SDD estende `render_prompts.py`
para gerar os três arquivos por inteiro (`FULL_TARGETS`), com o texto
hoje escrito à mão virando conteúdo literal de função builder — mesmo
padrão já usado em `build_agents`/`build_quickstart`, que também
misturam prosa fixa com trechos computados do YAML.

## Decisão(ões) de arquitetura aplicável(is)

`ADR-DTF-0001` — três camadas, fornecedor confinado a adaptadores
gerados. Consequência aplicada aqui: os três arquivos passam de
"renderização parcial" (`TARGETS`, bloco entre marcadores) para
"renderização integral" (`FULL_TARGETS`, arquivo inteiro), fechando a
lacuna que a v2.1.0 deixou (`SDD-DTF-0001` só cobriu `AGENTS.md`/
`QUICKSTART.md`).

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0001`:

- **RF07** — `render_prompts.py` gera arquivo inteiro para adaptadores.
  Quando `render_prompts.py` for executado sem `--check`, o sistema deve
  reescrever integralmente cada adaptador declarado em `FULL_TARGETS`; e
  com `--check` deve sair 1 e nomear o arquivo se o conteúdo em disco
  divergir do gerado.

Casos de borda consolidados (aplicáveis a esta etapa):

- **Renderização editada à mão fora dos limites gerados** — `--check`
  sai 1 e nomeia o arquivo; o CI bloqueia o merge (já é o comportamento
  de `write_full`, reaproveitado aqui).
- **Adaptador declarado que não existe em disco** — `render_prompts.py`
  cria o arquivo; com `--check`, sai 1 informando ausência.
- **Conteúdo gerado idêntico ao hoje escrito à mão** — a migração não
  pode mudar o texto visível para quem lê o arquivo; só muda de onde ele
  vem. Verificado por diff byte a byte antes do commit (ver "Evidência
  de verificação").

## Especificação técnica consolidada

**`_framework/scripts/render_prompts.py`:**

- Três funções novas, mesmo padrão de `build_agents`/`build_quickstart`
  (recebem `rules: dict`, devolvem `str`; prosa fixa entremeada com
  chamadas a `core_facts(rules)` e outros trechos já computados do
  YAML):
  - `build_universal(rules) -> str` — conteúdo integral de
    `prompts/universal.md`: as 18 seções atuais (papel, dois
    repositórios, tipos de documento, fluxo e gate, os dois gates
    obrigatórios, ciclo de status, onboarding, incidentes, auditoria,
    esquema de id, front-matter, registry, "o que fazer quando",
    qualidade de conteúdo, verificação de escopo, handover/pickup, reuso
    em outro projeto) seguidas do bloco `core_facts(rules)` — mesmo texto
    hoje presente no arquivo, hospedado na função em vez de editado
    manualmente.
  - `build_cursor_mdc(rules) -> str` — conteúdo integral de
    `prompts/cursor/doc-framework.mdc`, incluindo o front-matter YAML do
    `.mdc` (`description`, `globs`, `alwaysApply`) como parte do string
    gerado — não é front-matter de documento do framework, é metadado do
    Cursor, portanto fora do schema de `validate_doc.py`.
  - `build_copilot_instructions(rules) -> str` — conteúdo integral de
    `prompts/copilot/copilot-instructions.md`.
  - Versão do framework (`v{fw.get('version')}`) no título de cada um
    passa a vir de `rules['framework']['version']` em vez de string fixa
    — corrige a divergência já presente hoje (os três arquivos dizem
    "v1.7.0" à mão, desatualizado; `core_facts` já usa a versão certa).
- `FULL_TARGETS` ganha três entradas:
  - `("prompts/universal.md", "build_universal")`
  - `("prompts/cursor/doc-framework.mdc", "build_cursor_mdc")`
  - `("prompts/copilot/copilot-instructions.md", "build_copilot_instructions")`
- `TARGETS`, `apply()` e `BEGIN`/`END` (mecanismo de bloco) são
  removidos — não sobra nenhum adaptador em modo "renderização parcial"
  depois desta etapa. `build_block(rules)` continua existindo só como
  chamada interna dentro de `core_facts`, se ainda for usada por algum
  builder; caso nenhuma função a chame mais diretamente após a migração,
  ela é removida também (verificado na implementação, não decidido
  antecipadamente aqui).
- `main()` perde o laço `for rel in TARGETS`; os três novos builders
  entram no laço existente `for rel, builder in FULL_TARGETS`.

**`_framework/scripts/check_renderings.py`:** nenhuma alteração nesta
etapa — `RENDERINGS` ampliada para cobrir os três arquivos é RF09,
etapa 3. Continuam cobertos pela checagem de tipo/status já existente,
que já os lista (confirmado: `RENDERINGS` atual inclui os três
caminhos).

**Arquivos gerados (sem edição manual daqui em diante):**
`_framework/prompts/universal.md`,
`_framework/prompts/cursor/doc-framework.mdc`,
`_framework/prompts/copilot/copilot-instructions.md`.

**Paridade entre repositórios (RF11):** os três arquivos, mais
`render_prompts.py`, alterados nos dois repositórios na mesma branch,
antes do PR.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF07 — os três viram `FULL_TARGETS` | `grep -c "build_universal\|build_cursor_mdc\|build_copilot_instructions" _framework/scripts/render_prompts.py` | ≥ 6 (3 na tupla `FULL_TARGETS`, 3 na `def`) |
| 2 | RF07 — geração não muda o texto visível | `git diff --stat` dos três arquivos antes/depois de rodar `render_prompts.py` pela primeira vez (migração) | só a linha de versão (`v1.7.0` → `v2.1.0`) e, se houver, a normalização de espaço em branco — sem mudança de conteúdo normativo |
| 3 | RF07 — `--check` reprova edição manual | Acrescentar linha a `prompts/universal.md`, rodar `--check`, regenerar | exit 1, depois exit 0 |
| 4 | RF07 — `--check` reprova ausência | Renomear temporariamente `prompts/cursor/doc-framework.mdc`, rodar `--check`, restaurar o nome | exit 1 nomeando o arquivo, depois exit 0 |
| 5 | Mecanismo de bloco removido | `grep -c "^TARGETS = \|^def apply(" _framework/scripts/render_prompts.py` | `0` |
| 6 | Regressão | `framework_check.py --auto` e `check_renderings.py` | exit 0 nos dois |
| 7 | Paridade | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída |

Sensor de discriminação: critérios 3 e 4 têm o caso negativo explícito
(edição manual, arquivo ausente) — comando tem que falhar antes da
correção e passar depois, nas duas pontas.

## Instruções específicas para a IA implementadora

- O conteúdo de cada builder é **transcrição**, não reescrita — comece
  copiando o texto atual de cada arquivo (linhas antes do marcador
  `BEGIN GENERATED`) para dentro da função como string Python, ajustando
  só a versão para vir de `rules['framework']['version']` em vez de
  literal. Reescrever a prosa "já que estava mexendo" é escopo fora
  desta SDD.
- Depois de gerar, rode `git diff` nos três arquivos e confirme que a
  única mudança de conteúdo é a versão (e formatação mecânica, se
  houver) — se aparecer diferença de sentido, é sinal de erro de
  transcrição, não de melhoria intencional.
- **NÃO** alterar `check_renderings.py`/`RENDERINGS` — RF09, etapa 3.
- **NÃO** tocar em `sync_copies` — RF08, etapa 3.
- **NÃO** remover `ai_targets` do schema de SDD — RF10, etapa 3.
- Replicar toda alteração nos dois repositórios antes de abrir PR.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0007`.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem código correspondente.
- [ ] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não preenchido — a preencher em sessão
separada da que implementou.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0001, ADR-DTF-0001 |
| Etapa | 2 de 4 de SPEC-DTF-0001 (RF07) |
| Branch | `sdd/SDD-DTF-0007-adaptadores-gerados` |
