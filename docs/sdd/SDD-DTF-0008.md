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
  procedimentos. `RENDERINGS` deve incluir todo adaptador gerado, e todo
  arquivo de `procedures/` deve ser coberto por alguma checagem
  automática — não necessariamente o mesmo laço de `RENDERINGS` (ver
  "Especificação técnica consolidada" para o porquê).
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
- **Documento com `ai_targets` no front-matter** (RF10) — validação passa
  sem alteração: confirmado nesta SDD que `validate_doc.py` nunca rejeita
  campo de front-matter fora de `REQUIRED_FRONTMATTER`. Nenhuma SDD deste
  repositório tem hoje `ai_targets` de fato no front-matter (checado por
  `grep`) — o campo nunca foi obrigatório, só documentado; o teste do
  critério 6 insere o campo manualmente para verificar o comportamento.
  Não há comportamento novo a escrever, só a promessa de schema a remover da
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

- `RENDERINGS` ganha só `"../AGENTS.md"` — cita todo tipo ativo
  (confirmado: `core_facts` já lista os 8), passa pelo mesmo laço de
  cobertura total que já vale para os três adaptadores.
  **Não** entram nesse laço, apesar de a intenção original desta SDD
  incluir mais candidatos — descoberto durante a implementação que o
  laço de `RENDERINGS` exige que a renderização cite **todo** tipo ativo
  e **toda** Iron Law, e três casos reais não satisfazem isso por
  desenho, não por defeito:
  - `../QUICKSTART.md` — deliberadamente uma página, sem o bloco de
    Iron Laws nem a tabela de sizing (`build_quickstart` não chama
    `core_facts`).
  - `skills/{handover,pickup,verify-sdd}/SKILL.md` — stub de 5-7 linhas,
    não tem por que citar tipo de documento.
  - `procedures/*.md` — procedimento de continuidade, mesmo motivo.
  Incluir qualquer um desses no laço reprovaria sempre — falso positivo
  estrutural, não divergência real. A cobertura desses arquivos vem de
  duas checagens já corretas para o que cada um é: `check_links` (já
  escaneia todo `.md` do repositório, cobre link quebrado nos quatro) e
  `check_capability_procedures` (abaixo, cobre existência do arquivo que
  cada `procedure` referencia).
- `check_capability_procedures(rules: dict, root: Path) -> list` —
  itera `rules["capabilities"]`; para cada entrada que tiver a chave
  `procedure`, resolve `root / procedure` (`root` já é `_framework/`
  neste script — mesma convenção de `framework_root()`) e, se o arquivo
  não existir, acrescenta a string `"<id>: procedure aponta para
  <caminho> (não existe)."` à lista devolvida. Isto cobre
  `procedures/handover.md`, `procedures/pickup.md` e
  `procedures/verify-sdd.md` (as três capacidades que ganharam o campo
  em `SDD-DTF-0006`) sem duplicar o laço de cobertura de tipos.
- `main()` chama `check_capability_procedures` depois de `check_links`,
  imprime cada problema com `❌`, e conta para o código de saída (sai 1
  se a lista não for vazia).

**`_framework/templates/sdd.template.md`:**
- Remove a linha `ai_targets: []            # ex: [claude-code, cursor, copilot]`
  do front-matter de exemplo.
- Remove a linha `| ai_targets | {lista de ferramentas} |` da tabela de
  Rastreabilidade.

**`_framework/skills/doc-traceability-framework/templates/sdd.template.md`:**
mesma edição, replicada à mão. Esta cópia não é coberta por
`sync_copies` (RF08 só sincroniza `scripts/*.py` e o YAML, não
`templates/`) — ficou divergente da edição acima até ser sincronizada
manualmente nesta implementação. `templates/` inteiro sincronizado por
mecanismo automático é lacuna fora do escopo desta SDD, não corrigida
aqui.

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
| 3 | RF09 — `RENDERINGS` ganha AGENTS.md e `check_capability_procedures` cobre `procedures/` | `grep -c '"\.\./AGENTS.md"' _framework/scripts/check_renderings.py` e `grep -c "def check_capability_procedures" _framework/scripts/check_renderings.py` | `1` e `1` |
| 4 | RF09 (sensor) — `procedure` inexistente reprova | Apontar `capabilities` → `write_handover.procedure` para caminho inexistente, rodar `check_renderings.py`, reverter | exit 1 nomeando `write_handover`, depois exit 0 |
| 5 | RF10 — `ai_targets` fora do template e do YAML | `grep -c "ai_targets" _framework/templates/sdd.template.md _framework/rules/workflow-rules.yaml` | `0` nos dois |
| 6 | RF10 — documento com `ai_targets` continua válido | Inserir `ai_targets: [claude-code]` no front-matter de uma SDD existente (ex.: `docs/sdd/SDD-DTF-0001.md`), rodar `framework_check.py --auto`, depois remover a linha inserida | exit 0, sem erro relacionado a `ai_targets`, nos dois lados do teste |
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
