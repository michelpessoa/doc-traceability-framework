---
id: SDD-DTF-0001
type: SDD
title: "Superfície de entrada: AGENTS.md, QUICKSTART.md e expurgo de PRD/TS"
status: approved
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
consumption_instructions: "Leia as seções 'Requisitos consolidados' e 'Especificação técnica consolidada' antes de tocar em qualquer arquivo. Não implemente as etapas 1, 2 ou 3 da SPEC-DTF-0001 — esta SDD cobre apenas a etapa 0."
supersedes: null
superseded_by: null
tags: [adocao, neutralidade]
---

# Superfície de entrada: AGENTS.md, QUICKSTART.md e expurgo de PRD/TS

## Resumo executivo

Etapa 0 de quatro da neutralização decidida em `ADR-DTF-0001`. Reduz a
barreira de entrada do framework: em vez de colar 455 linhas de
`prompts/universal.md` no início de cada conversa, o operador passa a ter
`AGENTS.md` na raiz do repositório — lido nativamente por Codex, Cursor,
Gemini CLI, Copilot e Aider — cobrindo o caminho `small`/`medium`
completo, mais um `QUICKSTART.md` de uma página. No mesmo movimento, PRD
e TS saem de `document_types` (legados desde 2.0.0, já fora do fluxo), com
`RULE_SINCE` garantindo que projetos já mapeados não sejam reprovados.

## Decisão(ões) de arquitetura aplicável(is)

`ADR-DTF-0001` — três camadas com fornecedor confinado a adaptadores
gerados. Desta etapa decorrem duas consequências diretas:

- `AGENTS.md` é o **alvo canônico da camada 3**. Ele não é escrito à mão:
  é gerado por `render_prompts.py` a partir do YAML canônico.
- Quando `AGENTS.md` e o YAML discordarem, **manda o YAML**. Divergência é
  falha de build, barrada por `render_prompts.py --check` no CI, não uma
  diferença de comportamento a ser tolerada.

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0001`, apenas os RFs da etapa 0:

- **RF01** — `AGENTS.md` gerado na raiz cobre o caminho `small` e
  `medium` completo: tipos de documento ativos, as quatro Iron Laws, os
  níveis de sizing e o ciclo de status, em no máximo 120 linhas.
- **RF02** — `QUICKSTART.md` de no máximo 80 linhas, citando `AGENTS.md`,
  o comando de validação e o fluxo `small`, sem citar tipo ou status
  inexistente no YAML.
- **RF03** — `PRD` e `TS` removidos de `document_types`, sem reprovar os
  documentos PRD/TS já emitidos em ABSTRACTCLINIC, EVM e DTF.

Casos de borda herdados da SPEC que esta etapa precisa honrar:

- Adaptador declarado mas ausente em disco: `render_prompts.py` cria; com
  `--check`, sai 1 informando a ausência — nunca ignora em silêncio.
- Id de tipo legado (`PRD-EVM-0001`, `TS-EVM-0001`) em `relates_to`,
  `source_docs` ou no corpo de um documento: continua sendo reconhecido
  como id válido depois da mudança.
- Documento já emitido com `type: PRD`/`type: TS`: validação passa,
  porque a regra nova declara `RULE_SINCE = 2.1.0` e só vale para projeto
  cujo registry declare `framework_version` ≥ 2.1.0.
- Repositório sem `_framework/`: o `AGENTS.md` do repositório de projeto
  é autocontido para o caminho `small` e cita a URL do central para o
  resto.

## Especificação técnica consolidada

**Arquivos a alterar:**

- `_framework/rules/workflow-rules.yaml`
  - mover as chaves `PRD` e `TS` de `document_types` para uma chave nova
    de topo `legacy_document_types`, com o conteúdo preservado
    integralmente;
  - `framework.version: "2.1.0"`;
  - registrar a mudança no changelog interno do próprio YAML, no mesmo
    formato das versões anteriores.
- `_framework/scripts/framework_lib.py`
  - `_derive_constants` passa a montar `DOC_TYPES` pela união de
    `document_types` e `legacy_document_types`. Sem isso o `ID_PATTERN`
    deixa de reconhecer ids `PRD-*` e `TS-*`, e os documentos já emitidos
    em ABSTRACTCLINIC e EVM perdem rastreabilidade — regressão que a
    `lessons_policy.non_retroactive` proíbe.
- `_framework/scripts/check_renderings.py`
  - `legacy_types` passa a ser lida de `legacy_document_types` em vez de
    filtrar `document_types` por `deprecated_since`. Alteração mínima e
    obrigatória: sem ela a checagem de tipo legado fica vazia. O restante
    do arquivo (ampliação de `RENDERINGS`) segue sendo etapa 3.
- `_framework/scripts/render_prompts.py`
  - formato `agents`: função que produz o conteúdo integral de
    `AGENTS.md` a partir de `build_block(rules)` mais o texto de
    caminho `small`/`medium`;
  - alvos novos `../AGENTS.md` e `../QUICKSTART.md`, relativos à raiz do
    repositório (os alvos atuais são relativos à raiz de `_framework`).

**Arquivos a criar:**

- `AGENTS.md` (raiz dos dois repositórios) — gerado, ≤ 120 linhas.
- `QUICKSTART.md` (raiz dos dois repositórios) — gerado, ≤ 80 linhas.

**Fora do escopo desta SDD** (etapas 1 a 3 da SPEC): `procedures/`,
`ai_capabilities` como contratos, stubs de `SKILL.md`, geração integral
dos adaptadores de fornecedor, `sync_copies`, ampliação de `RENDERINGS`,
remoção de `ai_targets`.

**Rollout:** branch `sdd/SDD-DTF-0001-superficie-entrada` a partir de
`docs/fluxo-spec-v2`, nos dois repositórios, com PR e CI verde. Rollback é
`git revert`: nenhum documento emitido é alterado e nenhum dado migrado.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — `AGENTS.md` gerado e em dia | `python3 _framework/scripts/render_prompts.py && python3 _framework/scripts/render_prompts.py --check` | Sai 0 nas duas execuções |
| 2 | RF01 — limite de tamanho | `wc -l < AGENTS.md` | Valor ≤ 120 |
| 3 | RF01 — conteúdo do caminho comum | `grep -c -E "small\|medium\|SDD\|SPEC" AGENTS.md` | ≥ 4 ocorrências, e leitura confirma as quatro Iron Laws presentes |
| 4 | RF02 — `QUICKSTART.md` dentro do limite | `wc -l < QUICKSTART.md` | Valor ≤ 80 |
| 5 | RF02 — não cita tipo/status inexistente | `python3 _framework/scripts/check_renderings.py` | Sai 0 |
| 6 | RF03 — PRD e TS fora do schema | `python3 -c "import yaml;d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))['document_types'];assert 'PRD' not in d and 'TS' not in d"` | Sai 0, sem AssertionError |
| 7 | RF03 — projetos já mapeados não reprovam | `python3 _framework/scripts/framework_check.py --auto` | Sai 0 nos três projetos (ABSTRACTCLINIC, EVM, DTF) |
| 7b | RF03 (borda) — id legado segue reconhecido | `cd _framework/scripts && python3 -c "from framework_lib import ID_PATTERN; assert ID_PATTERN.search('PRD-EVM-0001') and ID_PATTERN.search('TS-EVM-0001')"` | Sai 0, sem AssertionError |
| 8 | RF07 (borda) — edição manual é barrada | Editar uma linha de `AGENTS.md` à mão e rodar `python3 _framework/scripts/render_prompts.py --check` | Sai 1, nomeando `AGENTS.md` |
| 9 | RF11 — paridade entre repositórios | `diff -r doc-traceability-central/_framework doc-traceability-framework/_framework` | Sem saída |
| 10 | Determinismo | Rodar `render_prompts.py` duas vezes e comparar `git status --porcelain` | Segunda execução não produz diferença |

## Instruções específicas para a IA implementadora

- `AGENTS.md` e `QUICKSTART.md` são **saída gerada**. Não os edite à mão:
  mude o gerador em `render_prompts.py` ou o YAML canônico e regenere.
- Mantenha `build_block` como está — ela já é usada pelos três alvos
  existentes; a etapa 0 acrescenta um formato, não reescreve os atuais.
- A geração precisa ser determinística: nada de timestamp, ordem de
  `dict` não fixada ou caminho absoluto no conteúdo gerado. O CI compara
  bytes.
- Toda mudança em `_framework/` vale para os **dois** repositórios. A
  etapa só está pronta quando `diff -r` entre eles não reporta nada.
- **NÃO alterar:** `templates/`, `prompts/cursor/`, `prompts/copilot/`,
  `skills/`, `.github/workflows/`. São etapas 1 a 3. De
  `check_renderings.py`, altere **apenas** a origem de `legacy_types`;
  `RENDERINGS` e `check_capability_procedures` são etapa 3.
- `RULE_SINCE` **não** recebe entrada nesta etapa: com PRD e TS
  preservados em `legacy_document_types`, nenhum documento já emitido
  passa a violar regra alguma, então não há regra nova a datar. Desvio
  registrado em relação ao plano da SPEC-DTF-0001, cujo critério de
  aceite (RF03) continua satisfeito pela união de tipos.
- **NÃO** remover PRD/TS de `templates/` nem apagar documentos PRD/TS já
  emitidos — a remoção é do schema, não do histórico.
- Mensagens de commit em Conventional Commits, com `Refs: SDD-DTF-0001`.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem código correspondente.
- [ ] Todo arquivo tocado aparece em "Especificação técnica consolidada"
      ou "Instruções específicas".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que implementou. Esta
tabela registra os comandos rodados de fato na sessão de implementação;
não substitui a verificação independente exigida pelo
`gate_scope_verification`, que precisa acontecer antes de `implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `render_prompts.py` e em seguida `render_prompts.py --check` | `AGENTS.md: gerado` / `QUICKSTART.md: gerado`, depois `em dia` nos dois; exit 0 | ver #8 | sim |
| 2 | `wc -l < AGENTS.md` | `108` (limite 120) | sem teste — medição direta | sim |
| 3 | `grep -o -E "small\|medium\|SDD\|SPEC" AGENTS.md \| sort -u` | `SDD SPEC medium small` — os quatro termos presentes; `check_renderings.py` confirma 6 Iron Laws no arquivo | sem teste — medição direta | sim |
| 4 | `wc -l < QUICKSTART.md` | `45` (limite 80) | sem teste — medição direta | sim |
| 5 | `check_renderings.py` | `4 renderização(ões) concordam com workflow-rules.yaml (8 tipos ativos, 6 Iron Laws, 4 níveis)`; exit 0. 2 warnings pré-existentes em `prompts/cursor/doc-framework.mdc` (cita PRD/TS sem marcar como legado) — texto escrito à mão, some na etapa 2 | sem teste — comando é o próprio validador | sim |
| 6 | `python3 -c "...assert 'PRD' not in d and 'TS' not in d"` | `ok`, sem AssertionError | assert é o sensor: falharia se a chave permanecesse | sim |
| 7 | `framework_check.py --auto` | `✅ Todas as verificações do framework passaram` — 42 docs EVM, ABSTRACTCLINIC e DTF, incluindo documentos `type: PRD` e `type: TS` | sem teste — comando é o próprio validador | sim |
| 7b | `from framework_lib import ID_PATTERN; assert ID_PATTERN.search('PRD-EVM-0001') and ID_PATTERN.search('TS-EVM-0001')` | `ok`. Antes da união em `_derive_constants` o mesmo assert falhava | assert é o sensor: falha se os legados saírem de `DOC_TYPES` | sim |
| 8 | `echo "linha intrusa" >> AGENTS.md` e `render_prompts.py --check` | `exit=1`; regenerado em seguida | **é o sensor**: edição manual introduzida de propósito, check reprovou, estado restaurado | sim |
| 9 | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída | diff vazio é o sinal; divergência apareceria como lista de arquivos | sim |
| 10 | `render_prompts.py` duas vezes seguidas + `git status --porcelain` | segunda execução não produziu diferença nova | sem teste — comparação direta | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0001, ADR-DTF-0001 |
| Etapa | 0 de 4 (SPEC-DTF-0001, plano de implementação) |
| Branch | `sdd/SDD-DTF-0001-superficie-entrada` |
