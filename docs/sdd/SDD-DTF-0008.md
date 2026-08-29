---
id: SDD-DTF-0008
type: SDD
title: "Fim da duplicação manual e cobertura de renderizações"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-08-29"
relates_to: [SPEC-DTF-0001, ADR-DTF-0001, SDD-DTF-0006, SDD-DTF-0007]
source_docs:
  - id: "SPEC-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0001.md"
  - id: "ADR-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0001.md"
consumption_instructions: "Leia 'Especificação técnica consolidada' inteira antes de tocar em arquivo. Etapa 3 de 4 (última) de SPEC-DTF-0001 — fecha RF08/RF09/RF10; RF11 (paridade) já é prática corrente desde a etapa 0, formalizada aqui como checagem mecânica full-time, não introduzida agora."
supersedes: null
superseded_by: null
tags: [neutralidade, adocao, limpeza]
---

# Fim da duplicação manual e cobertura de renderizações

## Resumo executivo

Três lacunas remanescentes de `SPEC-DTF-0001`: (1) as cópias de
`scripts/*.py` e `workflow-rules.yaml` dentro de
`skills/doc-traceability-framework/` divergiram silenciosamente desde a
v2.0.0 — confirmado nesta sessão, `diff` mostra 5 scripts e o YAML
desatualizados; (2) `check_renderings.py` não cobre `AGENTS.md`,
`QUICKSTART.md`, os stubs `SKILL.md` nem `procedures/*.md`, então uma
divergência ali passaria sem alarme no CI; (3) `ai_targets` continua
documentado em `sdd.template.md` e na prosa de dois adaptadores, apesar
de nunca ter sido campo obrigatório no validador — promessa de schema
que o código nunca cobrou. Esta SDD fecha as três, encerrando a etapa 3
(última) de `SPEC-DTF-0001`.

## Decisão(ões) de arquitetura aplicável(is)

`ADR-DTF-0001` — três camadas, fornecedor confinado a adaptadores
gerados. Consequência aplicada: a cópia dentro da skill Claude é camada
3 (renderização), não deveria nunca ser editada à mão — `sync_copies`
fecha o mesmo tipo de lacuna que `SDD-DTF-0001` e `SDD-DTF-0007` já
fecharam para os outros adaptadores.

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0001`:

- **RF08** — As cópias dentro da skill são sincronizadas, não mantidas à
  mão. Quando `render_prompts.py` for executado, o sistema deve copiar
  `_framework/scripts/*.py` e `_framework/rules/workflow-rules.yaml`
  para `skills/doc-traceability-framework/{scripts,references}/`; com
  `--check` deve sair 1 se alguma cópia divergir da origem.
- **RF09** — `check_renderings.py` cobre todos os adaptadores e
  procedimentos. `RENDERINGS` deve incluir todo adaptador gerado e todo
  arquivo de `procedures/`, e sair 1 se qualquer um citar tipo ou status
  inexistente no YAML.
- **RF10** — `ai_targets` sai do schema de SDD. O sistema não deve exigir
  nem documentar `ai_targets` no schema de SDD nem no `sdd.template.md`;
  documento já emitido com o campo é aceito sem erro.

Casos de borda consolidados (aplicáveis a esta etapa):

- **Cópia da skill divergiu porque alguém editou a cópia** (RF08) —
  `--check` sai 1 apontando origem e cópia; a correção é regenerar,
  nunca editar a cópia.
- **Procedimento referenciado por `capabilities.<id>.procedure`
  inexistente** (RF09) — `check_renderings.py` sai 1 nomeando a
  capacidade e o caminho ausente. Cobre as três capacidades de
  continuidade que ganharam o campo em `SDD-DTF-0006`
  (`write_handover`, `pickup_handoff`, `verify_sdd_independently`).
- **Documento já emitido contém `ai_targets`** (RF10) — validação passa
  sem alteração: confirmado nesta SDD que `validate_doc.py` nunca rejeita
  campo de front-matter fora de `REQUIRED_FRONTMATTER` — não há
  comportamento novo a escrever, só a promessa de schema a remover da
  documentação.

RF11 (paridade das duas cópias de `_framework/`) não gera código nesta
etapa — já é prática seguida desde `SDD-DTF-0001` (`diff -r` antes de
cada commit). Fica registrado aqui como fechamento formal do requisito,
não como mecanismo novo.

## Especificação técnica consolidada

**`_framework/scripts/render_prompts.py`:**

- `sync_copies(root: Path, check: bool) -> bool` — copia
  `_framework/scripts/*.py` (exceto `__pycache__`) e
  `_framework/rules/workflow-rules.yaml` para
  `_framework/skills/doc-traceability-framework/{scripts,references}/`.
  Com `check=True`, não escreve: para cada arquivo, se o conteúdo em
  disco da cópia divergir do original (ou a cópia não existir), imprime
  `❌ <cópia>: divergente de <origem>.` e retorna `False` ao final; sem
  `--check`, sobrescreve e imprime `✅ <cópia>: sincronizado.`.
- Chamada em `main()`, depois do laço de `FULL_TARGETS`: `ok &=
  sync_copies(root, check)`.

**`_framework/scripts/check_renderings.py`:**

- `RENDERINGS` ganha: `"../AGENTS.md"`, `"../QUICKSTART.md"`,
  `"skills/handover/SKILL.md"`, `"skills/pickup/SKILL.md"`,
  `"skills/verify-sdd/SKILL.md"`, `"procedures/handover.md"`,
  `"procedures/pickup.md"`, `"procedures/verify-sdd.md"` — além da
  entrada já existente `"skills/doc-traceability-framework/SKILL.md"` e
  dos três adaptadores já cobertos (`universal.md`,
  `doc-framework.mdc`, `copilot-instructions.md`).
- `check_capability_procedures(rules: dict, root: Path) -> list` —
  itera `rules["capabilities"]`; para cada entrada que tiver a chave
  `procedure`, resolve `root / "_framework" / procedure` e, se o arquivo
  não existir, acrescenta a string `"<id>: procedure aponta para
  <caminho> (não existe)."` à lista devolvida.
- `main()` chama `check_capability_procedures` depois de `check_links`,
  imprime cada problema com `❌`, e conta para o código de saída (sai 1
  se a lista não for vazia).

**`_framework/templates/sdd.template.md`:**
- Remove a linha `ai_targets: []            # ex: [claude-code, cursor, copilot]`
  do front-matter de exemplo.
- Remove a linha `| ai_targets | {lista de ferramentas} |` da tabela de
  Rastreabilidade.

**`_framework/rules/workflow-rules.yaml`:**
- Remove a chave `ai_targets` do bloco `SDD` em
  `document_types.SDD` → schema de campos adicionais (linha com
  `ai_targets: "lista de ferramentas de IA..."`).

**Builders regenerados (efeito mecânico, sem edição manual):**
`build_universal` e `build_copilot_instructions`
(`_framework/scripts/render_prompts.py`) transcrevem hoje a frase
"Preencha também `ai_targets` e `consumption_instructions`" e a menção
de `ai_targets` no front-matter obrigatório — como esses builders
migraram para transcrição literal em `SDD-DTF-0007`, a remoção do
YAML **não** propaga sozinha: as duas strings-prefixo dos builders
precisam da mesma edição manual (removendo a menção a `ai_targets`,
mantendo `consumption_instructions`), replicada nos dois repositórios.
`docs/especificacao.md` não menciona `ai_targets` (confirmado por grep)
— não precisa de edição, só regeneração.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF08 — cópias sincronizadas | `render_prompts.py && diff -rq _framework/scripts _framework/skills/doc-traceability-framework/scripts --exclude=__pycache__ && diff _framework/rules/workflow-rules.yaml _framework/skills/doc-traceability-framework/references/workflow-rules.yaml` | sem saída de diff |
| 2 | RF08 (sensor) — cópia editada à mão reprova | Alterar `skills/doc-traceability-framework/scripts/framework_lib.py`, rodar `--check`, regenerar | exit 1, depois exit 0 |
| 3 | RF09 — `RENDERINGS` ampliada | `grep -c "AGENTS.md\|QUICKSTART.md\|procedures/handover.md\|skills/handover/SKILL.md" _framework/scripts/check_renderings.py` | ≥ 4 |
| 4 | RF09 (sensor) — `procedure` inexistente reprova | Apontar `capabilities` → `write_handover.procedure` para caminho inexistente, rodar `check_renderings.py`, reverter | exit 1 nomeando `write_handover`, depois exit 0 |
| 5 | RF10 — `ai_targets` fora do template e do YAML | `grep -c "ai_targets" _framework/templates/sdd.template.md _framework/rules/workflow-rules.yaml` | `0` nos dois |
| 6 | RF10 — documento já emitido com `ai_targets` continua válido | `framework_check.py --auto` sobre um documento fixture com `ai_targets` no front-matter (`docs/sdd/SDD-DTF-0001.md`, que já tem o campo) | exit 0, sem erro relacionado a `ai_targets` |
| 7 | RF11 — paridade | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída |
| 8 | Regressão | `framework_check.py --auto` e `render_prompts.py --check` | exit 0 nos dois repositórios |

Sensor de discriminação: critérios 2 e 4 têm o caso negativo explícito
(cópia editada à mão, `procedure` apontando para caminho inexistente) —
comando tem que falhar antes da correção e voltar a passar depois.

## Instruções específicas para a IA implementadora

- `sync_copies` copia por igualdade de conteúdo, não por timestamp —
  compare bytes, não `mtime`.
- **NÃO** alterar `templates/` além das duas linhas de `ai_targets` em
  `sdd.template.md` — sem reescrever outras seções do template "já que
  estava ali".
- **NÃO** remover `ai_targets` de SDDs já emitidas
  (`SDD-DTF-0001.md`, que tem o campo) — não-retroatividade,
  `RULE_SINCE` não existe aqui porque nunca houve regra de código
  exigindo o campo, só documentação a apagar.
- Ao editar as strings-prefixo de `build_universal` e
  `build_copilot_instructions` para remover a menção a `ai_targets`,
  altere só essa frase — não retranscreva o resto do prefixo.
- Replicar toda alteração nos dois repositórios antes de abrir PR.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0008`.

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
| Etapa | 3 de 4 (última) de SPEC-DTF-0001 (RF08, RF09, RF10, RF11) |
| Branch | `sdd/SDD-DTF-0008-limpeza-cobertura` |
