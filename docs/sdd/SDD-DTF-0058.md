---
id: SDD-DTF-0058
type: SDD
title: "Coluna Projeto na SPEC: RFs de uma SPEC divididos por projeto, conferidos no validate_doc e no check_source_docs, kit 2.8.0"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-21"
updated: "2026-11-21"
relates_to: [SDD-DTF-0057]
source_docs:
  - id: "SPEC-DTF-0032"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0032.md"
  - id: "ADR-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0008.md"
sizing: "large"
consumption_instructions: "Compilada da SPEC-DTF-0032 (approved), só a parte do kit: RF01 a RF03, os RFs com Projeto DTF. Os RF04 a RF10 são da fábrica (Projeto FAB) e ficam numa SDD-FAB própria, depois da tag 2.8.0. As mensagens, chaves e assinaturas de 'Especificação técnica consolidada' são lei: não inventar campo, chave ou mensagem nova. Teste primeiro, visto falhar. A regra vale pela presença da coluna Projeto, sem RULE_SINCE: nenhum documento existente pode reprovar nem mudar de hash. Gerados só por render_prompts.py e generate_registry_md.py. O central espelha por branch e PR próprios."
supersedes: null
superseded_by: null
tags: [spec, coluna-projeto, check_source_docs, validate_doc, multi-repo]
---

# Coluna Projeto na SPEC: RFs de uma SPEC divididos por projeto, conferidos no validate_doc e no check_source_docs, kit 2.8.0

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar.

## Resumo executivo

Parte do kit da SPEC-DTF-0032, a segunda SPEC da fase 4 da RFC-DTF-0009.
Na 2.7.0, o `check_source_docs.py` exige que a SDD enxuta cubra todos os
RFs da SPEC de origem. Uma SPEC que divide os RFs entre dois repositórios,
como a própria SPEC-DTF-0032 (RF01 a RF03 no kit, RF04 a RF10 na
fábrica), faria reprovar a SDD enxuta de cada lado. Esta SDD entrega no
kit, na versão 2.8.0 e sem efeito sobre documento existente:

- **Coluna `Projeto`:** coluna opcional, a última da tabela "Requisitos
  funcionais" da SPEC, depois de `Arquivos`, com a lista de
  `PROJECT_CODE` do RF. O `validate_doc.py` reprova célula vazia e código
  fora de `^[A-Z][A-Z0-9]*$`.
- **Fidelidade por projeto:** com a coluna na SPEC, o
  `check_source_docs.py` compara a SDD enxuta só com os RFs do `project`
  do `docs/sdd/registry.yaml` dela, nas duas direções, e reprova RF de
  outro projeto e SPEC sem RF do projeto.
- **2.8.0:** versão minor, changelog, template da SPEC e item 2 do passo
  0 do `verify-sdd`.

## Decisão(ões) de arquitetura aplicável(is)

Da ADR-DTF-0008, valem os itens 1, 2 e 6: o kit não cita executor, o
contrato do executor é versionado e nada é retroativo. `contract_version`
fica 1, porque a coluna só acrescenta. A decisão de desenho da SPEC
também é lei:

- a divisão fica na SPEC, numa coluna da tabela, e não no front-matter da
  SDD, para o `check_source_docs.py` não depender do que a SDD declara
  sobre si mesma;
- a coluna é a última, depois de `Arquivos`, porque `check_ears` e
  `check_files_column` leem as colunas pela posição (índices 2 e 3);
- o código do projeto é conferido só pelo formato, porque projeto como o
  FAB tem registry só no próprio repositório;
- a regra vale pela presença da coluna, sem `since` por data: nenhuma
  SPEC aprovada antes da 2.8.0 tem a coluna, e a SPEC-DTF-0032, que a
  tem, já passa nela.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | A SPEC declara de que projeto é cada RF | Onde a tabela "Requisitos funcionais" de uma SPEC tiver a coluna `Projeto`, `validate_doc.py` deve exigir em cada linha uma lista não vazia de códigos de projeto separados por vírgula, cada um no formato `^[A-Z][A-Z0-9]*$`, e deve reprovar célula vazia ou código fora do formato, nomeando o RF e o código; sem a coluna, nada muda em relação à 2.7.0 |
| RF02 | A fidelidade de RFs considera só os do projeto da SDD | Quando a SPEC de origem tiver a coluna `Projeto`, `check_source_docs.py` deve comparar os RFs da SDD com origem nessa SPEC só com os RFs cuja célula `Projeto` contém o `project` do `docs/sdd/registry.yaml` da SDD, nas duas direções, e deve reprovar a SDD que traga RF de outro projeto ou que tenha origem numa SPEC sem nenhum RF do seu projeto |
| RF03 | Versão minor e procedimento | O sistema deve declarar `framework.version` `2.8.0`, com entrada no changelog, citar a coluna `Projeto` no item 2 do passo 0 de `_framework/procedures/verify-sdd.md` e manter verde o `framework_check.py --auto` do central sem mudar nenhum documento existente |

Casos de borda da SPEC que a implementação e os testes cobrem (os da
fábrica ficam na SDD da fábrica):

| Caso | RF | Comportamento esperado |
|---|---|---|
| Célula `Projeto` com `DTF, FAB` | RF01, RF02 | O RF vale para as duas SDDs |
| Célula `Projeto` vazia, `-` ou `—` | RF01 | Reprova: `RF07: coluna Projeto vazia` |
| Código `fab` ou `FAB-1` | RF01 | Reprova nomeando o código; o código não é conferido contra o central |
| Célula `DTF,,FAB` | RF01 | Aceita: item vazio entre vírgulas é ignorado, e sobram `DTF` e `FAB` |
| SPEC sem a coluna `Projeto` | RF01, RF02 | Comportamento da 2.7.0: a SDD enxuta cobre todos os RFs |
| SPEC em qualquer status com a coluna | RF01 | A regra vale pela presença da coluna, não pelo status nem pela data |
| SDD completa (sem `source_docs`, ou projeto abaixo de 2.7.0) de SPEC com a coluna | RF02 | Sem mudança: a fidelidade de RFs só vale para a SDD enxuta |
| SDD enxuta cujo registry não declara `project` | RF02 | Comportamento da 2.7.0: todos os RFs da SPEC |
| SDD da fábrica cita RF01 do kit numa SPEC com a coluna | RF02 | Reprova: `RF01 de SPEC-X é do projeto DTF, não de FAB` |
| SDD com origem numa SPEC sem nenhum RF do seu projeto | RF02 | Reprova nomeando a SPEC e o projeto |
| SDD que deixa de fora RF do seu projeto | RF02 | Reprova com a mensagem de 2.7.0, só com os RFs do projeto na lista |
| SPEC com duas tabelas na seção | RF01, RF02 | Só a primeira tabela conta (`first_table_lines`) |

Requisitos não funcionais: só biblioteca padrão e `pyyaml`, sem rede,
nenhum script novo. A saída em texto e `--json` dos scripts alterados
continua válida contra os esquemas de hoje
(`resultado-validador.schema.json`); só aparecem mensagens novas. A
docstring dos scripts, que é a saída de uso congelada desde a 2.3.2
(`test_report_json.py`), não muda.

Fora de escopo, da SPEC e deste recorte: tudo o que é da fábrica (RF04 a
RF10: vigia do central, compilação e aprovação por política); acrescentar
a coluna às SPECs já aprovadas, inclusive à SPEC-DTF-0031; conferir o
código do projeto contra o registry central; exigir que `Projeto` seja a
última coluna (a posição é instrução do template, não check); mudar
`REQUIRED_SECTIONS`, o sweep, `approval_policy` ou o ciclo de status.

## Especificação técnica consolidada

Contratos completos na SPEC-DTF-0032, seção "Contratos técnicos", na
parte do kit. O que a implementação precisa acertar, com as mensagens
exatas:

- **`workflow-rules.yaml`.**
  - `document_types.SPEC` ganha, depois de `optional_sections`, a chave
    `rf_optional_columns`, com um comentário que cita SPEC-DTF-0032, RF01:

    ```yaml
    rf_optional_columns:
      - column: "Projeto"
        position: "última, depois de Arquivos"
        value: "lista de PROJECT_CODE separados por vírgula"
        format: "^[A-Z][A-Z0-9]*$"
    ```

  - `framework.version: "2.8.0"`, `last_updated: "2026-11-21"` e entrada
    no changelog com SPEC-DTF-0032 / ADR-DTF-0008 / RFC-DTF-0009
    (SDD-DTF-0058), dizendo que a regra vale pela presença da coluna, que
    nenhum documento existente muda e que gate, sizing, ciclo de status,
    política e `contract_version` não mudam.
- **`validate_doc.py`.**
  - `PROJECT_COLUMN = "Projeto"`,
    `PROJECT_CODE = re.compile(r"^[A-Z][A-Z0-9]*$")` e
    `PROJECT_EMPTY = {"", "-", "—"}`, num bloco de comentário fora da
    docstring.
  - `rf_projects(section: str | None) -> dict[str, list[str]] | None`,
    pura. Lê a primeira tabela da seção (`first_table_lines`). Devolve
    `None` se a seção faltar ou se o cabeçalho, sem espaços nas pontas
    das células, não tiver a célula `Projeto`. Senão, para cada linha de
    dados com `RF_ID` na primeira célula, a chave é o RF sem hífen
    (`RF-01` vira `RF01`) e o valor é a lista dos itens da célula
    `Projeto` separados por vírgula, sem espaços nas pontas e sem os
    itens vazios, na ordem da célula. Célula inteira em `PROJECT_EMPTY`
    dá lista vazia.
  - `check_project_column(doc_id: str, section: str | None) -> list[str]`,
    chamado em `check_document` para toda SPEC, em qualquer status e sem
    `RULE_SINCE`. Com `rf_projects` igual a `None`, devolve `[]`. Senão,
    por RF, na ordem da tabela:
    - lista vazia: `{doc_id}: {rf}: coluna Projeto vazia.`;
    - cada código fora de `PROJECT_CODE`:
      `{doc_id}: {rf}: projeto {codigo} fora do formato ^[A-Z][A-Z0-9]*$.`
  - `check_ears` e `check_files_column` não mudam: a coluna nova fica
    depois dos índices 2 e 3.
- **`check_source_docs.py`.**
  - `_project(sdd_path: Path) -> str | None`, privada: o campo `project`
    do `registry.yaml` mais próximo subindo a árvore, como
    `project_version`; `None` se o registry não declarar.
  - `check_rf_fidelity(doc_id: str, rows: list[dict], spec_paths: dict[str, Path], project: str | None = None) -> list[str]`.
    Sem `project`, ou com `rf_projects` da SPEC igual a `None`,
    comportamento da 2.7.0, com a mesma mensagem. Com os dois, para cada
    SPEC, em ordem de id:
    - RFs do projeto: os de `rf_projects` cuja lista contém `project`.
      Se nenhum, uma mensagem e nada mais para essa SPEC:
      `{doc_id}: {spec} não tem RF do projeto {project} na coluna Projeto.`;
    - para cada RF da SDD com `Origem` igual à SPEC que existe na SPEC
      mas não é do projeto, em ordem:
      `{doc_id}: {rf} de {spec} é do projeto {lista da célula, separada por ", "}, não de {project}.`;
    - os RFs do projeto fora da SDD e os RFs da SDD que não existem na
      SPEC saem na mensagem da 2.7.0, com `RFs de {spec} fora da SDD`
      calculado só sobre os RFs do projeto.
  - `check_sdd_source_docs` passa `project=_project(sdd_path)` a
    `check_rf_fidelity`; o resto não muda.
  - A docstring do módulo não muda.
- **`spec.template.md`.** No bloco de instrução de "Requisitos
  funcionais", depois do parágrafo da coluna `Arquivos`, um parágrafo
  novo: coluna `Projeto` opcional, só quando a SPEC divide os RFs entre
  projetos; a última, depois de `Arquivos`; `PROJECT_CODE` separados por
  vírgula; a SDD enxuta de cada projeto cobre só os RFs do seu código
  (SPEC-DTF-0032). O cabeçalho da tabela do template não muda.
- **`verify-sdd.md`.** O item 2 do passo 0 acrescenta a frase:
  `Quando a SPEC tem a coluna Projeto, contam só os RFs do project do registry da SDD; o check_source_docs.py já confere isso na SDD enxuta.`

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes de `rf_projects` e `check_project_column` (coluna válida, `DTF, FAB`, vazia, `-`, `fab`, `FAB-1`, `DTF,,FAB`, sem coluna, SPEC `approved` com a coluna, duas tabelas), vistos falhar; implementação | RF01 | `_framework/scripts/tests/test_validate_doc.py`, `_framework/scripts/validate_doc.py` | |
| 2 | Testes de `check_rf_fidelity` com `project` (SDD de cada projeto passa, `DTF, FAB` vale para os dois, RF de outro projeto reprova, SPEC sem RF do projeto reprova, RF do projeto faltando reprova, SPEC sem coluna e `project` `None` iguais à 2.7.0) e de `_project`, vistos falhar; implementação | RF02 | `_framework/scripts/tests/test_check_source_docs.py`, `_framework/scripts/check_source_docs.py` | 1 |
| 3 | Mutantes dos dois checks novos no `selftest.py` | RF01, RF02 | `_framework/scripts/tests/mutations.yaml` | 2 |
| 4 | YAML: `rf_optional_columns`, 2.8.0 e changelog | RF01, RF03 | `_framework/rules/workflow-rules.yaml` | |
| 5 | Template da SPEC e `verify-sdd.md`; teste da estrutura do procedimento com a linha nova | RF01, RF03 | `_framework/templates/spec.template.md`, `_framework/procedures/verify-sdd.md`, `_framework/tests/test_procedures_structure.py` | 4 |
| 6 | Manifesto, gerados e `registry.md` do kit | RF03 | `_framework/rules/kit-index.yaml`, gerados por `render_prompts.py`, `docs/sdd/registry.yaml`, `docs/sdd/registry.md` | 3, 5 |
| 7 | Espelho no central, branch e PR próprios, com os `registry.md` regenerados; `fabrica-central-teste` em 2.8.0 | RF03 | `central:_framework/`, `central:docs/*/registry.md`, `fabrica-central-teste:_framework/` | 6 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01: coluna `Projeto` | `python3 -m pytest _framework/scripts/tests/test_validate_doc.py -q -k projeto` | ANTES da task 1: falha; DEPOIS: todos passam | automatizado |
| A02 | RF02: fidelidade por projeto | `python3 -m pytest _framework/scripts/tests/test_check_source_docs.py -q -k projeto` | ANTES da task 2: falha; DEPOIS: todos passam | automatizado |
| A03 | RF01: sensor do formato | Em cópia descartável, trocar `PROJECT_CODE` por `re.compile(r".+")`; rodar o pytest de A01; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A04 | RF02: sensor do filtro por projeto | Em cópia descartável, ignorar `project` em `check_rf_fidelity` (usar todos os RFs da SPEC); rodar o pytest de A02; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A05 | RF02: sensor do RF de outro projeto | Em cópia descartável, tirar de `check_rf_fidelity` a mensagem `é do projeto`; rodar o pytest de A02; restaurar | Pelo menos 1 failed; restaurado, 0 failed | automatizado |
| A06 | RF01, RF02: sem a coluna, igual à 2.7.0 | `python3 -m pytest _framework/scripts/tests/test_sdd_lean.py _framework/scripts/tests/test_check_source_docs.py _framework/scripts/tests/test_validate_doc.py -q` | Todos passam, inclusive os testes da 2.7.0 sem alteração | automatizado |
| A07 | RF01: a SPEC de origem passa | No central: `python3 <kit>/_framework/scripts/validate_doc.py docs/DTF/03-spec/SPEC-DTF-0032.md; echo "exit=$?"` | `exit=0` | automatizado |
| A08 | Não funcional: saída dos validadores | `python3 -m pytest _framework/scripts/tests/test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` | Todos passam; diff vazio | automatizado |
| A09 | RF03: versão, procedimento e central | `grep -n 'version: "2.8.0"' _framework/rules/workflow-rules.yaml`; `grep -n 'coluna Projeto' _framework/procedures/verify-sdd.md`; no central, com `_framework/` desta branch e os `registry.md` regenerados: `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` e `git status --porcelain docs/ \| grep -v registry.md` | A linha da versão; a linha do procedimento; `exit=0`; nenhum documento alterado além dos `registry.md` | automatizado |
| A10 | Gerados em dia | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/generate_registry_md.py docs/sdd --check; echo "exit=$?"`; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `exit=0` nos três | automatizado |
| A11 | Suíte e formatação | `python3 -m pytest -q`; `ruff format --check` e `ruff check` nos `.py` do diff; `python3 _framework/scripts/selftest.py` | 0 failed; formatados; sem erro; mutantes mortos | automatizado |
| A12 | Espelho | No central: `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | Sem diferença | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0058-coluna-projeto`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0058`. Nunca em `main`.
- **Teste primeiro** em cada task, com a falha guardada.
- **Não acrescentar** chave, campo ou mensagem que esta SDD não declara.
  `executor_contract` não muda.
- **Não mudar** mensagem existente dos validadores, docstring de script,
  `REQUIRED_SECTIONS`, `RULE_SINCE`, gate, sizing, ciclo de status,
  `approval_policy` nem `hash_excluded_sections`.
- **Não editar** SPEC ou ADR aprovada, nem acrescentar a coluna à
  SPEC-DTF-0031. No central, só `_framework/` e os `registry.md` gerados
  mudam.
- **Testes de fidelidade** usam SDD enxuta: `created` igual ou posterior
  à data da 2.7.0 e registry de projeto com `framework_version: "2.7.0"`
  e `project` declarado.
- **Sem citar executor específico** no kit (ADR-DTF-0008, item 1). Nos
  testes, use códigos como `AAA` e `BBB`, não `FAB`.
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

**Verificador independente:** pendente

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0032, ADR-DTF-0008 |
| parent RFC | RFC-DTF-0009 |
| SDD irmã | SDD-FAB da SPEC-DTF-0032 (RF04 a RF10), depois da tag 2.8.0 |
