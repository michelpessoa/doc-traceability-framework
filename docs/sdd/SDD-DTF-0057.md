---
id: SDD-DTF-0057
type: SDD
title: "Documentação enxuta no kit: SDD que referencia a SPEC, molde na SDD small, seções opcionais da SPEC, Documentos originados gerados e approved_by.transitions"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-19"
updated: "2026-11-19"
relates_to: [SDD-DTF-0055, SDD-DTF-0056]
source_docs:
  - id: "SPEC-DTF-0031"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0031.md"
  - id: "ADR-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0008.md"
sizing: "large"
consumption_instructions: "Compilada da SPEC-DTF-0031 (approved), só a parte do kit: RF01 a RF14. Os RF15 a RF17 são da fábrica e ficam numa SDD-FAB própria. As mensagens, chaves, colunas e assinaturas de 'Especificação técnica consolidada' são lei: não inventar campo, chave ou mensagem nova. Teste primeiro, visto falhar. Toda regra nova é não-retroativa (RULE_SINCE sdd_lean = 2.7.0); nenhum documento existente pode reprovar nem mudar de hash. Gerados só por render_prompts.py e generate_registry_md.py. O central espelha por branch e PR próprios."
supersedes: null
superseded_by: null
tags: [documentacao-enxuta, sdd, spec, sizing, molde, registry, approved_by]
---

# Documentação enxuta no kit: SDD que referencia a SPEC, molde na SDD small, seções opcionais da SPEC, Documentos originados gerados e approved_by.transitions

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar.

## Resumo executivo

Parte do kit da SPEC-DTF-0031, a fase 5 da RFC-DTF-0009 (P5,
"Documentação enxuta"), que absorve a proposta 004 da fábrica. Hoje a
SDD repete a origem: copia a ADR, a Parte 2 da SPEC e os critérios EARS,
e a SDD `small` repete no corpo um padrão do projeto. Na SPEC, cinco
seções ficam vazias quase sempre, e "Documentos originados" fica parada
em "Nenhum ainda". Esta SDD entrega no kit, na versão 2.7.0 e sem efeito
sobre documento existente:

- **SDD enxuta:** com `source_docs`, a SDD declara `sizing`, traz os
  requisitos por RF-ID com origem, resumo e arquivos, e não pode ter as
  seções que copiam a SPEC e a ADR. O `check_source_docs.py` confere os
  RF-IDs contra a SPEC nas duas direções.
- **`molde`:** campo opcional, só em SDD `small`.
- **SPEC por sizing:** cinco seções opcionais declaradas no YAML e
  marcadas no template, com um check que impede divergência.
- **"Documentos originados" gerada:** o `generate_registry_md.py` monta
  a tabela a partir dos campos `parent_*`, e a seção sai dos templates de
  RFC e SPEC.
- **`approved_by.transitions`:** com `kind: policy`, o caminho
  `draft → in_review → approved` num commit só, conferido pelo
  `validate_state.py`.

## Decisão(ões) de arquitetura aplicável(is)

Da ADR-DTF-0008, valem os itens 1, 2 e 6: o kit não cita executor, o
contrato do executor é versionado e nada é retroativo. `contract_version`
fica 1, porque só acrescenta. A decisão de desenho da SPEC também é lei:
a referência entre SDD e SPEC é conferida por script
(`check_source_docs.py`), não só por leitura no `verify-sdd`, e a
não-retroatividade usa o mecanismo de sempre (`RULE_SINCE` e
`rule_applies_since_date`). "Documentos originados" continua em
`approval_policy.hash_excluded_sections`, para nenhum documento aprovado
mudar de hash.

## Requisitos consolidados

"SDD enxuta" é a SDD com `source_docs` não vazio, criada a partir da data
da 2.7.0, em projeto sob 2.7.0 ou maior (`rule_applies_since_date` com
`RULE_SINCE["sdd_lean"] = "2.7.0"`). SDD anterior, ou SDD sem
`source_docs`, segue o formato da 2.6.0.

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | A SDD declara sizing | O sistema deve aceitar em `frontmatter_schema.type_specific_fields.SDD` o campo `sizing`, com os níveis de `sizing.levels`. Quando a SDD enxuta estiver em `draft` ou `in_review`, `validate_doc.py` deve reprovar `sizing` ausente ou fora dos níveis |
| RF02 | Requisitos por referência | Enquanto a SDD enxuta estiver em `draft` ou `in_review`, `validate_doc.py` deve exigir em "Requisitos consolidados" uma tabela com as colunas `RF-ID`, `Origem`, `Requisito (resumo)` e `Arquivos`. Toda linha deve ter um RF-ID, um id presente em `source_docs` em `Origem` e um caminho em `Arquivos`. O resumo não pode passar de 200 caracteres |
| RF03 | Molde só na SDD `small` | O sistema deve aceitar em `frontmatter_schema.type_specific_fields.SDD` o campo opcional `molde`, com o nome de um padrão do projeto que a SDD referencia em vez de repetir. Se uma SDD criada a partir da 2.7.0 declarar `molde` com `sizing` diferente de `small`, ou com nome fora de `^[a-z0-9][a-z0-9-]*$`, então `validate_doc.py` deve reprovar |
| RF04 | A SDD enxuta não copia a origem | Se a SDD enxuta tiver a seção "Especificação técnica consolidada" ou "Decisão(ões) de arquitetura aplicável(is)", então `validate_doc.py` deve reprovar, nomeando a seção e dizendo que o conteúdo fica na SPEC ou na ADR por referência |
| RF05 | Fidelidade de RF nas duas direções | Quando a SDD enxuta tiver uma SPEC em `source_docs`, `check_source_docs.py` deve reprovar o RF-ID de "Requisitos consolidados" que não exista em "Requisitos funcionais" da SPEC citada em `Origem` e o RF-ID da SPEC que não apareça na SDD. As duas listas saem na mensagem |
| RF06 | Template da SDD enxuto | O sistema deve publicar `templates/sdd.template.md` com as seções, nesta ordem: "Resumo executivo", "Requisitos consolidados", "Decomposição em tasks", "Critérios de aceite / definição de pronto", "Instruções específicas para a IA implementadora", "Verificação de escopo (nada a mais, nada a menos)", "Evidência de verificação" e "Rastreabilidade". O bloco de instrução deve dizer três coisas: os arquivos permitidos são a união da coluna `Arquivos` dos requisitos e das tasks; em SDD sem `source_docs` o requisito é escrito na própria SDD, com critério EARS e `Origem` igual a `—`; e `molde` vale só em `small`, com um exemplo |
| RF07 | Os consumidores da SDD leem o formato novo | O sistema deve fazer `render_indexes.extract_sdd_files` ler também a coluna `Arquivos` de "Requisitos consolidados". `gate_scope_verification` deve dizer nos itens 1 e 2 que, na SDD enxuta, o desenho a conferir é a Parte 2 da SPEC de `source_docs`, e o procedimento do `verify-sdd` deve mandar ler essa Parte 2 pela URL |
| RF08 | Seções opcionais da SPEC | O sistema deve declarar em `document_types.SPEC.optional_sections` as seções "Usuários / personas afetadas", "Observabilidade (métricas, logs, alertas)", "Plano de rollout / rollback", "Times consumidores impactados" e "Dependências", cada uma com `returns_when` em texto. O template da SPEC deve marcar cada uma como opcional e repetir o `returns_when`. `validate_doc.py` não deve exigir nenhuma delas |
| RF09 | Template e YAML não divergem | Se uma seção de `optional_sections` não estiver no template da SPEC marcada como opcional, ou se o template marcar como opcional uma seção fora da lista, então `check_renderings.py` deve reprovar, nomeando a seção |
| RF10 | Documentos originados gerados | Quando gerar o `registry.md`, `generate_registry_md.py` deve ler o front-matter de cada documento do registry, pelo `path`, e acrescentar a seção "Documentos originados", com uma linha por documento que tem pai. A linha traz o pai, o filho, o tipo e o status do filho. Pai é o valor de `parent_strategy`, `parent_postmortem`, `parent_rfc`, `parent_adr` ou `source_incident`. Documento sem filho não aparece. Sem nenhuma linha, a seção diz `Nenhum documento com pai declarado.` |
| RF11 | A seção sai dos templates | O sistema deve retirar "Documentos originados" dos templates de RFC e SPEC e apontar, no bloco de instrução, para a visão gerada no `registry.md`. "Documentos originados" continua em `approval_policy.hash_excluded_sections`, para que os documentos que já têm a seção não mudem de hash |
| RF12 | Transições da política num commit só | O sistema deve aceitar em `approved_by`, só com `kind: policy`, o campo opcional `transitions`: uma lista de `{from, to, at}`. Quando o campo existir, `validate_state.py` deve exigir que o primeiro `from` seja `draft`, que cada `to` seja o `from` seguinte, que cada passo esteja em `status_lifecycle.allowed_transitions`, que o último `to` seja `approved` e que os `at` não decresçam. Com `kind: human`, `transitions` deve ser reprovado |
| RF13 | Contrato do executor acompanha | O sistema deve acrescentar em `executor_contract.writes` a linha `"Com kind: policy, draft → in_review → approved num único commit, com approved_by.transitions."` e manter `contract_version` 1, porque só acrescenta |
| RF14 | Versão minor | O sistema deve declarar `framework.version` `2.7.0`, com entrada no changelog, e manter verde o `framework_check.py --auto` do central sem mudar nenhum documento existente |

Casos de borda da SPEC que a implementação e os testes cobrem (os da
fábrica ficam na SDD da fábrica):

| Caso | RF | Comportamento esperado |
|---|---|---|
| SDD criada antes da 2.7.0, ou em projeto sob 2.6.0 | RF01 a RF05 | Nada muda: formato antigo aceito, sem aviso |
| SDD sem `source_docs` (`small` ou descoberta sem origem) | RF02, RF04, RF05 | Não é enxuta: segue a 2.6.0 e escreve requisito e desenho na própria SDD |
| `Origem` com id fora de `source_docs`, ou só com a ADR | RF02 | Reprova a linha, com o id encontrado e a lista de `source_docs` |
| Linha de requisito com `Arquivos` vazio | RF02 | Reprova a linha: sem arquivos, o gate de escopo não confere nada |
| `source_docs` com duas SPECs | RF05 | Cada RF é conferido contra a SPEC da sua linha; o RF que falta é cobrado de cada SPEC |
| SPEC citada fora do registry central ou sem o arquivo no `path` | RF05 | Problema já existente de `check_source_docs.py`; a comparação de RF não roda para ela |
| RF da SPEC escrito como `RF-01` e na SDD como `RF01` | RF05 | Iguais: a comparação tira o hífen, como `RF_ID` já aceita |
| Resumo com mais de 200 caracteres | RF02 | Reprova a linha: sinal de que a SDD voltou a copiar a SPEC |
| `molde` em SDD `medium`, ou `molde: Crud_Novo` | RF03 | Reprova, com o sizing ou o nome |
| `molde` que não existe no projeto | RF03 | O framework não confere; quem resolve o molde é o executor |
| SPEC nova com "Documentos originados" escrita à mão | RF10, RF11 | Aceita. A seção está fora do hash e a visão gerada é a fonte |
| Documento do registry cujo `path` não existe | RF10 | Fica fora da visão; `registry_tools.py validate` já reprova o `path` |
| `parent_rfc` de ADR reconstruído apontando para um BASE | RF10 | Entra como filho do BASE |
| `transitions` com `in_review → draft → in_review → approved` | RF12 | Reprova: o primeiro `from` precisa ser `draft` |
| `transitions` com `draft → in_review → draft → in_review → approved` | RF12 | Aceito: todos os passos são permitidos |
| `transitions` saltando de `draft` para `approved` | RF12 | Reprova: `draft → approved` não está em `allowed_transitions` |
| `transitions` com `at` fora de ordem ou fora de ISO 8601 | RF12 | Reprova, com o índice do passo |

Requisitos não funcionais: só biblioteca padrão e `pyyaml`, sem rede. A
saída em texto e `--json` dos scripts alterados continua válida contra
os esquemas de hoje (`resultado-validador.schema.json`); só aparecem
mensagens novas.

Fora de escopo, da SPEC e deste recorte: tudo o que é da fábrica (RF15 a
RF17: rascunho da descoberta, `redacao.montar_sdd`, compilador e versão
fixada); compilação automática da SDD e aprovação por política pelo
vigia; release dupla; SDD na visão "Documentos originados"; pasta dos
moldes; migrar SDD ou SPEC existente, ou apagar "Documentos originados"
de documento que já a tem; mudar `REQUIRED_SECTIONS` da SPEC, o sweep,
`approval_policy.rules` ou o ciclo de status.

## Especificação técnica consolidada

Contratos completos na SPEC-DTF-0031, seção "Contratos técnicos". O que a
implementação precisa acertar, com as mensagens exatas:

- **`workflow-rules.yaml`.**
  - `document_types.SPEC.optional_sections`, com as cinco entradas
    `{heading, returns_when}` exatamente como na SPEC (mesmo texto de
    `heading` e de `returns_when`).
  - `frontmatter_schema.type_specific_fields.SDD` ganha `sizing`
    (`"small | medium | large | complex — herdado da SPEC; obrigatório na SDD enxuta (2.7.0)"`)
    e `molde` (`"opcional, só com sizing small — nome (^[a-z0-9][a-z0-9-]*$) de um padrão do projeto que a SDD referencia em vez de repetir; onde o molde mora é decisão do executor"`).
  - `frontmatter_schema.common_fields.approved_by`: o texto acrescenta
    `transitions` (lista de `{from, to, at}`, só com `kind: policy`,
    desde a 2.7.0).
  - `gate_scope_verification.rule`, itens 1 e 2: acrescentam a frase
    `Na SDD enxuta (2.7.0, com source_docs), o desenho a conferir é a Parte 2 da SPEC de source_docs, lida pela url.`
  - `executor_contract.writes`: a linha nova do RF13, ao fim da lista.
  - `framework.version: "2.7.0"`, `last_updated` e entrada no
    changelog com SPEC-DTF-0031 / ADR-DTF-0008 / RFC-DTF-0009
    (SDD-DTF-0057), dizendo que é não-retroativa e que gate, sizing,
    ciclo de status e política não mudam.
- **`validate_doc.py`.**
  - `RULE_SINCE["sdd_lean"] = "2.7.0"`.
  - `LEAN_COLUMNS = ["RF-ID", "Origem", "Requisito (resumo)", "Arquivos"]`,
    `LEAN_SUMMARY_MAX = 200`, `MOLDE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")`,
    `LEAN_FORBIDDEN = {"Especificação técnica consolidada": "SPEC", "Decisão(ões) de arquitetura aplicável(is)": "ADR"}`.
  - `is_lean_sdd(fm: dict, applies) -> bool`: `fm.get("type") == "SDD"`,
    `fm.get("source_docs")` não vazio e `applies("sdd_lean")`.
  - `first_table_lines(section: str) -> list[str]`: as linhas da
    primeira tabela da seção, o bloco contínuo de linhas `|`; usada por
    `consolidated_rf_rows` e por `check_rf_fidelity`, para uma segunda
    tabela na seção não virar requisito (achado 1 da rodada 1 do
    verify-sdd).
  - `consolidated_rf_rows(body: str) -> list[dict] | None`: a primeira
    tabela de "Requisitos consolidados"; `None` se o cabeçalho, sem
    espaços nas pontas das células, não for exatamente `LEAN_COLUMNS`.
    Cada linha de dados vira
    `{"rf": str, "origem": str, "resumo": str, "arquivos": str}` (células
    sem espaços nas pontas; `rf` é o primeiro `RF_ID` da célula, ou `""`).
  - `check_lean_sdd(doc_id: str, fm: dict, body: str) -> list[str]`,
    chamado em `check_document` só quando `is_lean_sdd` e o status está
    em `DRAFTING_STATUSES`. Mensagens, nesta ordem:
    - sizing: `{doc_id}: SDD enxuta sem \`sizing\` válido ({valor!r}); use small, medium, large ou complex (SPEC-DTF-0031, RF01).`,
      com os níveis lidos de `sizing.levels`;
    - tabela: `{doc_id}: 'Requisitos consolidados' sem a tabela RF-ID | Origem | Requisito (resumo) | Arquivos (SPEC-DTF-0031, RF02).`
      (sem a tabela, nenhuma das mensagens de linha);
    - por linha `n` (contada a partir de 1):
      `{doc_id}: linha {n} de 'Requisitos consolidados' sem RF-ID.`;
      `{doc_id}: {rf} com Origem '{origem}' que não é SPEC de source_docs ({ids das SPECs de source_docs, separados por vírgula}).`
      (SPEC é o id que começa com `SPEC-`);
      `{doc_id}: {rf} com resumo de {n} caracteres; o limite é 200 (o resto fica na SPEC).`;
      `{doc_id}: {rf} sem caminho na coluna Arquivos.`;
    - para cada seção de `LEAN_FORBIDDEN` presente:
      `{doc_id}: SDD enxuta com a seção '{heading}': o conteúdo fica na {SPEC|ADR} de source_docs, por referência (SPEC-DTF-0031, RF04).`
  - `check_molde(doc_id: str, fm: dict) -> list[str]`, chamado em
    `check_document` para toda SDD com `molde` e `applies("sdd_lean")`,
    em qualquer status:
    `{doc_id}: \`molde\` só vale em SDD small (sizing {sizing}).` e
    `{doc_id}: \`molde\` com nome inválido ({nome!r}); use ^[a-z0-9][a-z0-9-]*$.`
  - Nada muda para SDD sem `source_docs` nem para SDD anterior à 2.7.0:
    `check_files_column` e `check_tasks_section` seguem como hoje.
- **`check_source_docs.py`.**
  - `check_rf_fidelity(doc_id: str, rows: list[dict], spec_paths: dict[str, Path]) -> list[str]`,
    pura. Para cada SPEC de `spec_paths`, em ordem de id: RFs da SPEC
    são os `RF_ID` da primeira célula das linhas de dados da tabela de
    "Requisitos funcionais"; RFs da SDD são os `rf` das linhas com
    `origem` igual ao id. Comparação sem hífen (`RF-01` == `RF01`). Com
    diferença, uma mensagem só:
    `{doc_id}: RFs de {spec} fora da SDD: {lista ou "nenhum"}; RFs da SDD fora de {spec}: {lista ou "nenhum"}.`
    (listas ordenadas, separadas por `, `).
  - `check_sdd_source_docs` chama `check_rf_fidelity` ao fim, só quando
    `is_lean_sdd` (com o `applies` de `rule_applies_since_date` e a versão
    do projeto da SDD) e só com as SPECs de `source_docs` que passaram
    nas checagens de existência e `path` (as que deram problema ficam
    fora). Linhas sem tabela válida (`consolidated_rf_rows` `None`): não
    roda; é problema do `validate_doc.py`.
- **`validate_state.py`.**
  - `check_transitions(doc_id: str, approved_by: dict, allowed: dict) -> list[str]`,
    pura, chamada de `check_approval` logo depois de `approved_by_format`
    quando `transitions` existe, em qualquer status. Mensagens:
    - `{doc_id}: approved_by.transitions só vale com kind policy.` (e
      não confere o resto);
    - `{doc_id}: approved_by.transitions deve ser uma lista não vazia de {from, to, at}.`
      (lista vazia, não lista, ou item sem `from`, `to` ou `at`);
    - `{doc_id}: approved_by.transitions começa em {from}; deve começar em draft.`;
    - `{doc_id}: approved_by.transitions[{i}] parte de {from}, mas o passo anterior terminou em {to anterior}.`;
    - `{doc_id}: approved_by.transitions[{i}] {from} → {to} não está em allowed_transitions.`;
    - `{doc_id}: approved_by.transitions[{i}] com \`at\` fora de ISO 8601 ({at!r}).`;
    - `{doc_id}: approved_by.transitions[{i}] com \`at\` anterior ao passo {i-1}.`;
    - `{doc_id}: approved_by.transitions termina em {to}; deve terminar em approved.`
  - `allowed` vem de `status_lifecycle.allowed_transitions`. `at` usa
    `_iso_8601`; a ordem compara os valores convertidos em `datetime`
    (data sem hora conta como meia-noite).
- **`generate_registry_md.py`.**
  - `PARENT_FIELDS = ("parent_strategy", "parent_postmortem", "parent_rfc", "parent_adr", "source_incident")`.
  - `originated(data: dict, docs_dir: Path) -> list[tuple[str, str, str, str]]`:
    para cada documento do registry com `path` que resolve
    (`registry_tools.resolve_doc_path`), lê o front-matter e, para cada
    campo de `PARENT_FIELDS` com valor texto não vazio, uma tupla
    `(pai, id, type, status)` do registry. Ordenado por `(pai, id)`.
    `path` que não resolve, ou front-matter ilegível: fica de fora, sem
    exceção.
  - `render_originated(rows) -> str`: `## Documentos originados`, linha
    em branco e a tabela `| Pai | Documento | Tipo | Status |` com
    `` `{pai}` `` e `` `{id}` `` entre crases; sem linhas, o texto
    `Nenhum documento com pai declarado.`
  - `render_registry(data, docs_dir)` acrescenta a seção ao fim. A
    assinatura ganha `docs_dir: Path | None = None`; sem `docs_dir`, não
    gera a seção (chamadas antigas não mudam). `main` passa o
    `docs_dir`. `--check` compara o arquivo inteiro, como hoje.
- **`check_renderings.py`.**
  - `OPTIONAL_MARK = "> Opcional (SPEC por sizing). Volta quando: "`.
  - `check_optional_sections(rules: dict, template: Path) -> list[str]`:
    uma seção é marcada quando a primeira linha não vazia depois de
    `## {heading}` começa com `OPTIONAL_MARK`. Mensagens:
    `spec.template.md: seção opcional '{heading}' de optional_sections sem a marca de opcional no template.`;
    `spec.template.md: '{heading}' marcada como opcional no template e fora de optional_sections.`;
    `spec.template.md: '{heading}' com "Volta quando" diferente de returns_when.`
  - `main` chama com `root / "templates/spec.template.md"` e soma aos
    `problems`.
- **`render_indexes.py`.** `extract_sdd_files(body)`, item (c) novo: a
  coluna `Arquivos` da primeira tabela de "Requisitos consolidados",
  com o `_paths_in` de hoje.
- **`procedures/verify-sdd.md`.** No passo 0, item 4, e no passo 1,
  primeiro item: na SDD enxuta, o desenho a conferir é a Parte 2 da SPEC,
  lida pela url de `source_docs`, porque a SDD não tem "Especificação
  técnica consolidada".
- **Templates.**
  - `templates/sdd.template.md`: as seções do RF06, na ordem; a tabela
    de requisitos com `| RF-ID | Origem | Requisito (resumo) | Arquivos |`;
    `sizing` no front-matter; o bloco de instrução com as três frases do
    RF06 e o exemplo `molde: crud` comentado no front-matter.
  - `templates/spec.template.md`: a linha `OPTIONAL_MARK + returns_when`
    logo abaixo de cada uma das cinco seções; sem "Documentos
    originados", com a frase `Documentos originados: visão gerada no registry.md (generate_registry_md.py), a partir de parent_rfc e parent_adr.`
    no bloco de instrução do topo.
  - `templates/rfc.template.md`: sem "Documentos originados", com a
    mesma frase, citando `parent_strategy` e `parent_postmortem` no
    lugar de `parent_rfc` e `parent_adr`.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes de SDD enxuta e de molde (um caso por linha de RF01 a RF04 nos casos de borda; SDD anterior à 2.7.0 e sem `source_docs` sem mudança; template preenchido passa), vistos falhar | RF01, RF02, RF03, RF04, RF06 | `_framework/scripts/tests/test_sdd_lean.py` | |
| 2 | `RULE_SINCE`, `is_lean_sdd`, `consolidated_rf_rows`, `check_lean_sdd` e `check_molde` | RF01, RF02, RF03, RF04 | `_framework/scripts/validate_doc.py` | 1 |
| 3 | Testes de `check_rf_fidelity` (faltando, sobrando, `RF-01` contra `RF01`, duas SPECs, SPEC fora do registry), vistos falhar; implementação | RF05 | `_framework/scripts/tests/test_sdd_lean.py`, `_framework/scripts/check_source_docs.py` | 2 |
| 4 | Testes de `check_transitions` (caminho válido, começo fora de `draft`, salto proibido, elo quebrado, `at` decrescente e inválido, fim fora de `approved`, `kind: human`), vistos falhar; implementação | RF12 | `_framework/scripts/tests/test_approval.py`, `_framework/scripts/validate_state.py` | |
| 5 | Testes de `originated` e `render_originated` (RFC, ADR, SPEC, BASE e ADR reconstruído; idempotência; `path` inexistente; sem linhas), vistos falhar; implementação | RF10 | `_framework/scripts/tests/test_generate_registry_md.py`, `_framework/scripts/generate_registry_md.py` | |
| 6 | Testes de `check_optional_sections` (template real passa; seção a menos, a mais e `returns_when` diferente reprovam) e de `extract_sdd_files` com a coluna `Arquivos`, vistos falhar; implementação | RF07, RF09 | `_framework/scripts/tests/test_spec_optional_sections.py`, `_framework/tests/test_render_indexes.py`, `_framework/scripts/check_renderings.py`, `_framework/scripts/render_indexes.py` | |
| 7 | YAML: `optional_sections`, `sizing` e `molde` da SDD, `transitions`, `gate_scope_verification`, `executor_contract.writes`, 2.7.0 e changelog; teste de contrato com a linha nova, visto falhar | RF07, RF08, RF12, RF13, RF14 | `_framework/rules/workflow-rules.yaml`, `_framework/tests/test_executor_contract.py` | 6 |
| 8 | Templates de SDD, SPEC e RFC, e `verify-sdd.md`; testes de RF06, RF08 e RF11 | RF06, RF07, RF08, RF11 | `_framework/templates/sdd.template.md`, `_framework/templates/spec.template.md`, `_framework/templates/rfc.template.md`, `_framework/procedures/verify-sdd.md`, `_framework/scripts/tests/test_spec_optional_sections.py`, `_framework/tests/test_procedures_structure.py` (desconta as linhas novas do `verify-sdd.md`, como fez a SDD-DTF-0053 com o M4) | 7 |
| 9 | Manifesto, gerados e `registry.md` do kit | RF10, RF14 | `_framework/rules/kit-index.yaml`, gerados por `render_prompts.py`, `docs/sdd/registry.md` | 8 |
| 10 | Espelho no central, branch e PR próprios, com os `registry.md` regenerados | RF01 a RF14 | `central:_framework/`, `central:docs/*/registry.md` | 9 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01 a RF04, RF06: SDD enxuta e molde | `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py -q -k "not fidelity"` | ANTES da task 2: falha; DEPOIS: todos passam | automatizado |
| A02 | RF05: fidelidade de RF | `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py -q -k fidelity` | ANTES da task 3: falha; DEPOIS: todos passam | automatizado |
| A03 | RF12: transições | `python3 -m pytest _framework/scripts/tests/test_approval.py -q -k transitions` | ANTES da task 4: falha; DEPOIS: todos passam | automatizado |
| A04 | RF10: Documentos originados | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -q` | ANTES da task 5: falha; DEPOIS: todos passam | automatizado |
| A05 | RF07, RF09: consumidores e divergência de template | `python3 -m pytest _framework/scripts/tests/test_spec_optional_sections.py _framework/tests/test_render_indexes.py -q` | ANTES da task 6: falha; DEPOIS: todos passam | automatizado |
| A06 | RF02: sensor da origem | Em cópia descartável, aceitar em `check_lean_sdd` qualquer id de `source_docs` em `Origem`; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A07 | RF05: sensor das duas direções | Em cópia descartável, tirar de `check_rf_fidelity` a lista "fora da SDD"; rodar o pytest de A02; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A08 | RF12: sensor do caminho | Em cópia descartável, tirar de `check_transitions` a conferência contra `allowed_transitions`; rodar o pytest de A03; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A09 | RF01 a RF05: não-retroatividade | Em cópia descartável, trocar `RULE_SINCE["sdd_lean"]` por `"1.0.0"`; rodar `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py -q`; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A10 | RF08, RF11, RF13: YAML, templates e contrato | `python3 -m pytest _framework/tests/test_executor_contract.py _framework/scripts/tests/test_spec_optional_sections.py -q`; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | Todos passam; `exit=0` | automatizado |
| A11 | Não funcional: saída dos validadores | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` | Todos passam; diff vazio | automatizado |
| A12 | RF14: versão e central | `grep -n 'version: "2.7.0"' _framework/rules/workflow-rules.yaml`; no central, com `_framework/` desta branch e os `registry.md` regenerados: `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` e `git status --porcelain docs/ \| grep -v registry.md` | A linha da versão; `exit=0`; nenhum documento alterado além dos `registry.md` | automatizado |
| A13 | Gerados em dia | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/generate_registry_md.py docs/sdd --check; echo "exit=$?"` | `exit=0` nos dois | automatizado |
| A14 | Suíte e formatação | `python3 -m pytest -q`; `ruff format --check` e `ruff check` nos `.py` do diff; `python3 _framework/scripts/selftest.py` | 0 failed; formatados; sem erro; mutantes mortos | automatizado |
| A15 | Espelho | No central: `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | Sem diferença | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0057-documentacao-enxuta`, a partir
  de `origin/main`. Commits com `Refs: SDD-DTF-0057`. Nunca em `main`.
- **Teste primeiro** em cada task, com a falha guardada.
- **Não acrescentar** chave, campo ou mensagem que esta SDD não declara
  (lição da rodada 1 da SDD-DTF-0053). `executor_contract` continua com
  exatamente `contract_version`, `description`, `reads`,
  `machine_outputs` e `writes`.
- **Não mudar** mensagem existente dos validadores, `REQUIRED_SECTIONS`,
  gate, sizing, ciclo de status, `approval_policy.rules` nem
  `hash_excluded_sections`.
- **Não migrar** documento existente, nem apagar "Documentos originados"
  de documento que já a tem. No central, só `_framework/` e os
  `registry.md` gerados mudam.
- **Testes com data:** os casos de SDD enxuta usam `created` igual ou
  posterior à data da 2.7.0 no changelog e um registry de projeto com
  `framework_version: "2.7.0"`; o caso não-retroativo usa data anterior.
- **Sem citar executor específico** no kit (ADR-DTF-0008, item 1).
- **Gerados só por script.**
- **Evidência de verificação** só por verificador independente.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima tem código correspondente (nada
      da SPEC ficou de fora).
- [ ] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", "Decomposição em tasks" ou "Instruções
      específicas" — se a implementação tocou um arquivo não listado
      aqui, ou é escopo que faltou registrar na SDD (atualize-a) ou é
      scope creep a remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado ("já que estava ali").

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 1: todas as linhas abaixo foram rodadas nesta sessão, no kit na
branch `sdd/SDD-DTF-0057-documentacao-enxuta` (head `17075b8`), com base
fixa `efe1c71` (`git merge-base HEAD origin/main`, = `origin/main` nesta
sessão), e no central na branch `claude/pickup-wkpglg` (head `faf53e5`).
Os "antes" de A01 a A05 e de A10 rodaram numa cópia descartável de
`efe1c71` (`git archive`) com os testes novos copiados por cima. Os
sensores A06 a A09 mutaram uma cópia descartável de `17075b8` (`git
archive`) no scratchpad e restauraram pela cópia guardada; o checkout do
kit e o do central ficaram com `git status --porcelain` vazio.

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0057.md`. Veredito: **FAIL** (rodada 1; status mantido em `approved`).

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0057.md /home/user/doc-traceability-central/docs/DTF; echo "exit=$?"`; comparação por script das colunas Requisito e EARS de RF01 a RF14 entre a SDD e a SPEC-DTF-0031 (approved, central `faf53e5`); leitura dos casos de borda, não funcionais e da Parte 2 | `✅ source_docs de SDD-DTF-0057.md conferem com o registry central.` `exit=0`; RF01 a RF14 com requisito e EARS idênticos (14/14 `True`); RF15 a RF17 fora, declaradamente (fábrica); 17 casos de borda iguais aos da SPEC sem a parte da fábrica (2 casos de RF15/RF16 retirados, RF16 tirado das colunas); contratos da Parte 2 (`is_lean_sdd`, `check_lean_sdd`, `check_molde`, `consolidated_rf_rows`, `check_rf_fidelity`, `check_optional_sections`, `OPTIONAL_MARK`, `PARENT_FIELDS`, `originated`, `render_originated`, `check_transitions`, `extract_sdd_files`, YAML) descritos da mesma forma, só detalhados (`consolidated_rf_rows` ganha `\| None` para tabela ausente) | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 1 | A01 | `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py -q -k "not fidelity"` | ANTES (`efe1c71` com os testes novos): `16 failed, 9 passed, 8 deselected`; DEPOIS: `25 passed, 8 deselected` | ver A06 e A09 | Sim | `_framework/scripts/tests/test_sdd_lean.py:150` | automatizado |
| 1 | A02 | `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py -q -k fidelity` | ANTES: `3 failed, 5 passed, 25 deselected`; DEPOIS: `8 passed, 25 deselected` | ver A07 | Sim | `_framework/scripts/tests/test_sdd_lean.py:327` | automatizado |
| 1 | A03 | `python3 -m pytest _framework/scripts/tests/test_approval.py -q -k transitions` | ANTES: `ImportError: cannot import name 'check_transitions' from 'validate_state'`, 1 error na coleta; DEPOIS: `11 passed, 35 deselected` | ver A08 | Sim | `_framework/scripts/tests/test_approval.py:389` | automatizado |
| 1 | A04 | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -q` | ANTES: `4 failed, 14 passed`; DEPOIS: `18 passed` | o ANTES é a implementação ausente (4 testes novos caem) | Sim | `_framework/scripts/tests/test_generate_registry_md.py:174` | automatizado |
| 1 | A05 | `python3 -m pytest _framework/scripts/tests/test_spec_optional_sections.py _framework/tests/test_render_indexes.py -q` | ANTES: `ImportError: cannot import name 'OPTIONAL_MARK' from 'check_renderings'`, 1 error na coleta; DEPOIS: `61 passed` | o ANTES é a implementação ausente; os testes não cobrem seção com mais de uma tabela (ver a última linha) | Sim | `_framework/tests/test_render_indexes.py:824` | automatizado |
| 1 | A06 | Na cópia, em `check_lean_sdd`, filtro `startswith("SPEC-")` dos ids de `source_docs` retirado (qualquer id aceito em `Origem`); pytest de A01; restaurado pela cópia | `1 failed, 24 passed, 8 deselected` (`test_origem_so_com_a_adr_reprova`); restaurado `25 passed, 8 deselected` | derrubada | Sim | `_framework/scripts/tests/test_sdd_lean.py:157` | automatizado |
| 1 | A07 | Na cópia, em `check_rf_fidelity`, `missing` trocado por `[]` (lista "fora da SDD" retirada); pytest de A02; restaurado pela cópia | `2 failed, 6 passed, 25 deselected` (`test_fidelity_rf_da_spec_fora_da_sdd_reprova`, `test_fidelity_duas_specs_cada_rf_contra_a_sua`); restaurado `8 passed, 25 deselected` | derrubada | Sim | `_framework/scripts/tests/test_sdd_lean.py:327` | automatizado |
| 1 | A08 | Na cópia, em `check_transitions`, `if target not in (allowed.get(origin) or []):` trocado por `if False:`; pytest de A03; restaurado pela cópia | `2 failed, 9 passed, 35 deselected` (`test_transitions_salto_proibido_reprova`, `test_transitions_conferido_pelo_check_approval`); restaurado `11 passed, 35 deselected` | derrubada | Sim | `_framework/scripts/tests/test_approval.py:389` | automatizado |
| 1 | A09 | Na cópia, `RULE_SINCE["sdd_lean"]` trocado por `"1.0.0"`; `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py -q`; restaurado pela cópia | `2 failed, 31 passed` (`test_rule_since_sdd_lean_e_2_7_0`, `test_sdd_em_projeto_sob_2_6_0_nao_muda`); restaurado `33 passed` | derrubada (só 1 teste de comportamento cai; o outro é a constante) | Sim | `_framework/scripts/tests/test_sdd_lean.py:211` | automatizado |
| 1 | A10 | `python3 -m pytest _framework/tests/test_executor_contract.py _framework/scripts/tests/test_spec_optional_sections.py -q`; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `24 passed`; `✅ 5 renderização(ões) concordam com workflow-rules.yaml (8 tipos ativos, 6 Iron Laws, 4 níveis).` `exit=0`. ANTES de `test_executor_contract.py` em `efe1c71`: `3 failed, 12 passed` | o ANTES é a implementação ausente | Sim | `_framework/tests/test_executor_contract.py:232` | automatizado |
| 1 | A11 | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` e o mesmo contra `efe1c71` | `26 passed`; os dois diffs vazios | a fixture do 2.3.2 compara stdout e exit; sem mutação própria (o requisito é não mudar) | Sim | `_framework/scripts/tests/test_report_json.py:244` | automatizado |
| 1 | A12 | `grep -n 'version: "2.7.0"' _framework/rules/workflow-rules.yaml`; no central (`claude/pickup-wkpglg`, `faf53e5`): `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"`; `git status --porcelain docs/ \| grep -v registry.md` | linhas 17 e 20; `✅ 134 documento(s) ok.`, `✅ Todas as verificações do framework passaram.`, `exit=0`; porcelain vazio; `generate_registry_md.py docs/<P> --check` em dia nos 4 projetos; fora de `_framework/`, a PR do central muda só os 4 `registry.md` e gerados de `render_prompts.py` (`AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`) | sem teste automatizado (medição) | Sim | `n/a` | automatizado (medição por comando, sem asserção em arquivo) |
| 1 | A13 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/generate_registry_md.py docs/sdd --check; echo "exit=$?"` | tudo `em dia`/`sincronizado` (o aviso `30 SDD(s) sem seção de arquivos` já existe em `efe1c71`), `exit=0`; `✅ docs/sdd/registry.md: em dia.` `exit=0` | sem teste automatizado (medição) | Sim | `n/a` | automatizado (medição por comando, sem asserção em arquivo) |
| 1 | A14 | `python3 -m pytest -q`; `ruff format --check` e `ruff check` nos 19 `.py` do diff; `python3 _framework/scripts/selftest.py` | `504 passed`; `19 files already formatted`; `All checks passed!`; `✅ 7 mutação(ões): todos os mutantes morreram.` | suíte inteira | Sim | `n/a` | automatizado |
| 1 | A15 | No central: `diff -r -x __pycache__ -x .pytest_cache /home/user/doc-traceability-framework/_framework _framework; echo "diff exit=$?"` | `diff exit=0` | sem teste automatizado (medição) | Sim | `n/a` | automatizado (medição por comando, sem asserção em arquivo) |
| 1 | Contrato de `consolidated_rf_rows` (RF02, RF05, RF07) | Reprodução no scratchpad: SDD enxuta válida em `draft`, montada com os helpers de `test_sdd_lean.py`, com uma segunda tabela (`\| Caso \| RF \| Comportamento esperado \|`) dentro de "Requisitos consolidados"; `check_document` | `SDD-TST-0001: linha 3 de 'Requisitos consolidados' sem RF-ID.`, `linha 4 ...`, `linha 5 ...`: as linhas da segunda tabela (cabeçalho, separador, dado) viram linhas de requisito. O contrato manda ler só "a primeira tabela" (`validate_doc.py:227`, `:231`; mesmo padrão em `check_source_docs.py:61`, `:63` e `render_indexes.py:619`) | sem teste automatizado que cubra o caso | Não | `n/a` | manual (reprodução; nenhum teste do diff cobre o caso) |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0031, ADR-DTF-0008 |
