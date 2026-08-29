---
id: SDD-DTF-0002
type: SDD
title: "Modo greenfield: registry sem repositório de código e textos de entrada"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-08-29"
relates_to: [SPEC-DTF-0002, SDD-DTF-0001]
source_docs:
  - id: "SPEC-DTF-0002"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0002.md"
consumption_instructions: "Leia 'Requisitos consolidados' e 'Especificação técnica consolidada' antes de tocar em qualquer arquivo. Depende de SDD-DTF-0001 já implementada: AGENTS.md e QUICKSTART.md precisam existir como saída gerada antes de ganharem a seção de modo greenfield."
supersedes: null
superseded_by: null
tags: [adocao, greenfield]
---

# Modo greenfield: registry sem repositório de código e textos de entrada

## Resumo executivo

Um projeto que ainda não tem repositório de código já consegue rodar o
fluxo inteiro de decisão no repositório central — mas isso nunca foi
declarado: `multi_project.instructions` manda criar `docs/sdd/` no
repositório de código como parte de adicionar projeto, assumindo que ele
existe, e a ausência de `repository` produz um warning genérico que não
distingue "ainda não existe repositório" de "existe e ninguém preencheu".
Esta SDD promove o comportamento acidental a contrato, acrescenta o campo
que separa os dois estados, e corrige os textos que assumem repositório
existente.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — o sizing `medium` de `SPEC-DTF-0002` dispensou RFC e ADR, porque
nenhum critério de `decision_gates.rfc_to_adr` se aplica. `ADR-DTF-0001`
segue valendo como contexto (AGENTS.md e QUICKSTART.md são saída gerada,
nunca editada à mão), mas não é fonte desta SDD.

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0002`:

- **RF01** — registry central sem `repository` é estado válido: warning, e
  `framework_check.py --auto` sai 0.
- **RF02** — campo `repository_status` com os valores `active` e
  `none_yet` distingue "ainda não existe" de "existe e não foi
  informado"; a mensagem de warning nomeia qual estado está registrado.
- **RF03** — `multi_project.instructions` declara a criação de
  `docs/sdd/registry.yaml` como etapa condicional.
- **RF04** — `AGENTS.md` e `QUICKSTART.md` descrevem os dois passos de
  saída do modo greenfield.
- **RF05** — a auditoria (seção 11) declara a ausência e para, em vez de
  inferir URL.
- **RF06** — o `gate_implementation_before_code` continua valendo: SDD não
  pode ser criada em projeto greenfield, porque SDD vive em `docs/sdd/` do
  repositório de projeto.

Casos de borda consolidados:

- `repository` e `repository_status` ambos ausentes → warning tratando
  como `none_yet`, dizendo que o estado foi **assumido**, não declarado.
- `repository_status: none_yet` com `repository` preenchido → problema,
  não warning: os campos se contradizem.
- `repository_status` com valor fora de `{active, none_yet}` → problema,
  listando os valores aceitos.
- `repository` como string vazia → tratado como ausente.
- Projeto legado (`framework_version` < 2.1.0) sem `repository` →
  comportamento atual preservado, sem exigir `repository_status`.

## Especificação técnica consolidada

**Arquivos a alterar:**

- `_framework/scripts/registry_tools.py`
  - nova `check_repository_state(data: dict) -> tuple[list[str], list[str]]`,
    devolvendo `(problems, warnings)`;
  - `validate` chama `check_repository_state` no lugar da checagem inline
    de `repository` que hoje vive no corpo da função.
- `_framework/rules/workflow-rules.yaml`
  - `registry.central_registry.repository_field` ganha `states` com
    `active` e `none_yet`, e `populated_when` reescrito distinguindo os
    dois;
  - `multi_project.instructions` reescrita com a criação de
    `docs/sdd/registry.yaml` como etapa 2, condicional;
  - `audit` (seção 11) ganha pré-condição explícita: sem `repository`,
    declara e para.
- `_framework/scripts/render_prompts.py`
  - `build_agents` e `build_quickstart` ganham a seção "Ainda não tenho
    repositório de código", com os dois passos de virada. O conteúdo é
    gerado, nunca escrito direto no markdown.

**Rollout:** branch `sdd/SDD-DTF-0002-greenfield`, empilhada sobre
`sdd/SDD-DTF-0001-superficie-entrada`, nos dois repositórios, com PR e CI
verde. Rollback é `git revert`: nenhum documento emitido é alterado e
nenhum dado é migrado.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — ausência de `repository` é warning, não erro | Criar registry de teste sem `repository` e rodar `framework_check.py` sobre ele | Sai 0, com warning nomeando o estado |
| 2 | RF01 (sensor) — preencher `repository` silencia o warning | Acrescentar `repository` ao mesmo registry e reexecutar | Sai 0, sem warning de repositório |
| 3 | RF02 — contradição entre campos é problema | Registry com `repository_status: none_yet` e `repository` preenchido | Sai 1, mensagem nomeando os dois campos |
| 4 | RF02 — valor inválido é problema | Registry com `repository_status: talvez` | Sai 1, listando `active` e `none_yet` |
| 5 | RF02 — estado assumido é declarado como assumido | Registry sem `repository` e sem `repository_status` | Warning diz que o estado foi assumido |
| 6 | RF02 — `repository` vazio equivale a ausente | Registry com `repository: ""` | Mesmo warning do campo omitido |
| 7 | RF03, RF04 — textos gerados trazem o modo greenfield | `render_prompts.py && render_prompts.py --check`, depois `grep -c greenfield AGENTS.md QUICKSTART.md` | Exit 0; ≥ 1 ocorrência em cada |
| 8 | RF03 — instrução condicional no YAML | `python3 -c "import yaml;t=yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))['multi_project']['instructions'];assert 'condicional' in t"` | Sai 0, sem AssertionError |
| 9 | RF05 — pré-condição da auditoria declarada | `python3 -c "import yaml;a=yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))['audit'];assert 'repository' in str(a) and 'não' in str(a)"` | Sai 0, sem AssertionError |
| 10 | Compatibilidade — projetos já mapeados não reprovam | `framework_check.py --auto` | Sai 0 nos três projetos |
| 11 | RF04 (limite) — `AGENTS.md` segue dentro do teto | `wc -l < AGENTS.md` | Valor ≤ 120 |
| 12 | Paridade entre repositórios | `diff -r --exclude=__pycache__` entre os dois `_framework/` | Sem saída |

## Instruções específicas para a IA implementadora

- `AGENTS.md` e `QUICKSTART.md` continuam sendo **saída gerada**. A seção
  nova entra em `build_agents`/`build_quickstart`, nunca no markdown.
- `check_repository_state` recebe o registry já carregado e **não** lê
  disco nem conhece caminho — é função pura, para poder ser exercitada
  com dicionário em memória.
- Mensagens de warning em português, no formato das existentes.
- O teto de 120 linhas do `AGENTS.md` (RF01 de `SPEC-DTF-0001`) continua
  valendo: a seção nova precisa caber nele.
- **NÃO alterar:** `templates/`, `skills/`, `prompts/`, `check_renderings.py`,
  `.github/workflows/`. São as etapas 1 a 3 de `SPEC-DTF-0001`.
- **NÃO** preencher `repository_status` nos registries de ABSTRACTCLINIC e
  EVM — o campo é opcional e eles operam sob 1.6.0.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0002`.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem código correspondente.
- [ ] Todo arquivo tocado aparece em "Especificação técnica consolidada"
      ou "Instruções específicas".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que implementou. Registra
os comandos rodados de fato; não substitui a verificação independente
exigida pelo `gate_scope_verification` antes de `implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `registry_tools.py validate` em registry de teste sem `repository` | Warning "modo greenfield ASSUMIDO, não declarado"; `exit=0` | ver #2 | sim |
| 2 | mesmo registry, agora com `repository` e `repository_status: active` | `exit=0`, **sem** warning de repositório | **é o sensor**: o warning some quando o campo é preenchido | sim |
| 3 | registry com `repository_status: none_yet` **e** `repository` preenchido | `exit=1` — "contradiz o campo `repository`, que está preenchido" | contradição introduzida de propósito; passaria se a checagem não existisse | sim |
| 4 | registry com `repository_status: talvez` | `exit=1` — "valor inválido 'talvez' — aceitos: active, none_yet" | valor inválido introduzido de propósito | sim |
| 5 | registry com `repository_status: none_yet` e sem `repository` | Warning "modo greenfield DECLARADO"; `exit=0` — texto distinto do #1 | par com #1: os dois estados produzem mensagens diferentes | sim |
| 6 | registry com `repository: ""` | Mesmo warning do #1 | string vazia tratada como ausente, não como URL | sim |
| 7 | `render_prompts.py && render_prompts.py --check`; `grep -c -i greenfield` | `exit=0`; 1 ocorrência em `AGENTS.md`, 1 em `QUICKSTART.md` | `--check` reprova edição manual (verificado em SDD-DTF-0001 #8) | sim |
| 8 | `assert 'condicional' in multi_project['instructions']` | `ok`, sem AssertionError | assert falharia com o texto antigo, que assumia repositório existente | sim |
| 9 | `assert 'repository' in str(audit) and 'não' in str(audit)` | `ok`, sem AssertionError | assert falharia sem a `precondition` nova | sim |
| 10 | `framework_check.py --auto` no repositório central | `✅ Todas as verificações do framework passaram` — DTF (4), EVM (42), ABSTRACTCLINIC (12) | validador é o próprio teste | sim |
| 11 | `wc -l < AGENTS.md` | `119` (limite 120) | medição direta — margem de 1 linha, ver observação | sim |
| 12 | `diff -r --exclude=__pycache__` entre os dois `_framework/`; `diff` dos dois `AGENTS.md` | sem saída nos dois | diff vazio é o sinal | sim |

**Observação para a etapa 1:** `AGENTS.md` está em 119 de 120 linhas. A
próxima etapa que acrescentar conteúdo ao arquivo precisa cortar antes,
ou o critério RF01 de `SPEC-DTF-0001` reprova.

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0002 |
| Branch | `sdd/SDD-DTF-0002-greenfield` |
