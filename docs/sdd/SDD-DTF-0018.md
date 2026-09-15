---
id: SDD-DTF-0018
type: SDD
title: "validate_state: não retroatividade por data de criação e checagem de evidência por coluna"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-14"
updated: "2026-09-14"
relates_to: [SDD-DTF-0016]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Escopo mecânico em um script (validate_state.py) mais um arquivo de teste novo; a cópia da skill é sincronizada por render_prompts.py. Implementar em branch sdd/SDD-DTF-0018-* a partir de main, PR, commits com Refs: SDD-DTF-0018."
supersedes: null
superseded_by: null
tags: [tooling, gate_scope_verification, non_retroactive]
---

# validate_state: não retroatividade por data de criação e checagem de evidência por coluna

## Resumo executivo

`SDD-DTF-0016` trocou a decisão de "desde quando uma regra vale" de
versão do registry para data de criação do documento — mas só em
`validate_doc.py`. `validate_state.py` ficou com a regra antiga
(`rule_applies`, `_framework/scripts/validate_state.py:93`). Achado real
em 2026-09-14 rodando `validate_state.py` sobre
`/home/michel/projetos/viverMelhor/docs/sdd` (registry em
`framework_version: "2.1.0"`): 27 problemas, dos quais 18 são SDDs
0001–0009 criadas antes de 2026-08-29 (data da 1.7.0, que introduziu a
seção 16) e 3 são linhas da SDD-EVM-0012 com `n/a (checagem estática)` na
coluna **Sensor** — declaração permitida pelo procedimento
`verify-sdd.md` ("Critério sem teste automatizado: declare"). Só 6
problemas são reais (SDD-EVM-0013/0014/0015 com tabela de evidência
vazia em status `implemented`).

Consequência operacional: 21 falsos positivos em 27 enterram o sinal —
a checagem mecânica existia no projeto e não foi levada a sério. Também
impede tornar o validador bloqueante em qualquer projeto que suba
`framework_version`, repetindo o incidente de 2026-09-08
(`SDD-DTF-0016`).

Achado adicional na leitura do código: `check_evidence` assume que a
coluna 1 é o comando (`row[1]`). Na tabela de 6 colunas usada pelo próprio
kit (`SDD-DTF-0017`: `# | Critério | Comando | Saída | Sensor | Passou?`)
a coluna 1 é o critério — a checagem de "linha sem comando rodado" olha a
coluna errada.

`sizing: small` — 1 script alterado, 1 arquivo de teste novo, sem mudança
de regra, gate ou fluxo: corrige a mecanização para cumprir o que
`lessons_policy.non_retroactive` e `gate_scope_verification.evidence_standard`
já dizem em texto.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção de mecanização, nenhum critério do gate `rfc_to_adr`
se aplica. Reusa `framework_lib.rule_applies_since_date`, introduzida por
`SDD-DTF-0016`.

## Requisitos consolidados

- **RF1**: Quando `validate_state.check_sdd` decidir se uma exigência de
  `RULE_SINCE` vale para uma SDD, o sistema deve usar
  `rule_applies_since_date(rules, RULE_SINCE[rule], fm.get("created"),
  version)`, com `rules = load_rules()` lido uma vez por chamada — mesmo
  mecanismo de `validate_doc.check_document`.
- **RF2**: Quando `check_evidence` procurar evidência assumida (termos de
  `ASSUMED_EVIDENCE`), o sistema deve examinar só as colunas cujo
  cabeçalho contém "comando", "saída"/"saida" ou "passou", ignorando as
  colunas "#", "Critério" e "Sensor".
- **RF3**: Quando `check_evidence` checar "linha sem comando rodado", o
  sistema deve usar a coluna cujo cabeçalho contém "comando", não a
  posição fixa 1.
- **RF4**: Se a tabela de evidência não tiver cabeçalho com coluna
  reconhecível como comando, então o sistema deve aplicar as duas
  checagens à linha inteira (comportamento atual) — nunca ficar mais
  permissivo por falta de cabeçalho.
- **RF5**: O sistema deve ter teste automatizado em
  `_framework/scripts/tests/test_validate_state.py` cobrindo RF1–RF4 e um
  teste de guarda que falha se qualquer script de `_framework/scripts/`
  (fora `framework_lib.py`) chamar `rule_applies(` diretamente.

Casos de borda:
- SDD sem `created` ou versão do changelog sem `date` → fallback por
  versão do registry, herdado de `rule_applies_since_date` (igual a
  `SDD-DTF-0016`).
- SDD criada no mesmo dia da regra (`created: 2026-08-29`) → regra vale
  (comparação `>=`).
- "n/a" na coluna **Passou?** → problema (resultado não verificado não é
  evidência).
- Duas colunas com "comando" no cabeçalho → usa a primeira.

Fora de escopo:
- Corrigir os dados de SDD-EVM-0013/0014/0015 (repositório do projeto,
  fase separada, fora deste kit).
- Mudar a lista `ASSUMED_EVIDENCE` ou os critérios do gate 16.
- Sincronizar a cópia de `_framework/` do repositório central (PR de sync
  separado, depois do merge).
- Bump de `framework.version`.

## Especificação técnica consolidada

**`_framework/scripts/validate_state.py`**

- Import troca `rule_applies` por `load_rules` e `rule_applies_since_date`
  (de `framework_lib`).
- `check_sdd(path, version=None)`: ler o front-matter **antes** de
  definir `applies`; então:
  ```python
  rules = load_rules()

  def applies(rule: str) -> bool:
      return rule_applies_since_date(rules, RULE_SINCE[rule], fm.get("created"), version)
  ```
- Nova função que devolve cabeçalho e linhas (a atual `table_rows`
  descarta o cabeçalho e continua existindo para `n_criteria`):
  ```python
  def table_with_header(section: str) -> tuple[list[str], list[list[str]]]:
      """(cabeçalho normalizado em minúsculas, linhas de dados)."""
  ```
- `check_evidence(doc_id, evidence, n_criteria)`:
  ```python
  header, rows = table_with_header(evidence)
  cmd_idx = next((i for i, h in enumerate(header) if "comando" in h), None)
  checked_idx = [i for i, h in enumerate(header)
                 if any(k in h for k in ("comando", "saída", "saida", "passou"))]
  ```
  Para cada linha: `scope = [row[i] for i in checked_idx if i < len(row)]`
  se `checked_idx` não vazio, senão `row` inteira (RF4); busca de
  `ASSUMED_EVIDENCE` em `" | ".join(scope).lower()`. Comando vazio:
  `row[cmd_idx]` se `cmd_idx` não for `None`, senão `row[1]` (RF4).
  Mensagens de problema inalteradas.

**`_framework/scripts/tests/test_validate_state.py`** (novo) — fixtures
em `tmp_path` escrevendo SDDs mínimas; `check_sdd(path, version="2.1.0")`
com `load_rules()` real (datas do changelog são histórico fixo):

| Teste | Entrada | Esperado |
|---|---|---|
| `test_legado_antes_da_regra_nao_reprova` | `status: implemented`, `created: 2026-08-25`, sem seção de evidência nem de escopo | `problems == []` |
| `test_criada_depois_da_regra_reprova` | igual, `created: 2026-09-01` | problema citando "Evidência de verificação" |
| `test_mesmo_dia_da_regra_reprova` | `created: 2026-08-29`, tabela vazia | problema |
| `test_na_no_sensor_nao_reprova` | tabela 5 colunas, "n/a (checagem estática)" só em Sensor | nenhum problema de "resultado assumido" |
| `test_na_na_saida_reprova` | "n/a" na coluna Saída | problema "resultado assumido" |
| `test_na_no_passou_reprova` | "n/a" na coluna Passou? | problema "resultado assumido" |
| `test_tabela_seis_colunas_comando_vazio` | `# \| Critério \| Comando \| Saída \| Sensor \| Passou?` com Comando vazio e Critério preenchido | problema "sem comando rodado" |
| `test_tabela_seis_colunas_ok` | mesma tabela, todas preenchidas | nenhum problema |
| `test_sem_cabecalho_reconhecivel_linha_inteira` | cabeçalho `a \| b \| c`, "n/a" em qualquer coluna | problema (RF4) |
| `test_nenhum_validador_chama_rule_applies_direto` | leitura de texto de `_framework/scripts/*.py` exceto `framework_lib.py` | nenhuma ocorrência de `rule_applies(` |

**`_framework/skills/doc-traceability-framework/scripts/validate_state.py`**
— gerado por `python3 _framework/scripts/render_prompts.py`
(`sync_copies`), nunca editado à mão.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1–RF5 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | 10 testes `passed`, exit 0 |
| 2 | RF1 e RF2 no caso real (legado EVM + Sensor "n/a") | bloco C2 abaixo | `0` |
| 3 | Skill sincronizada | `python3 _framework/scripts/render_prompts.py --check` | exit 0 |
| 4 | Regressão geral (self-host) | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.` e suíte inteira `passed` |
| 5 | Paridade com o CI | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | exit 0 |

Bloco C2 (fora da tabela porque usa pipe de shell) — conta problemas
atribuídos às SDDs que são falso positivo hoje:

```bash
python3 _framework/scripts/validate_state.py /home/michel/projetos/viverMelhor/docs/sdd --report-only |
  grep -c -e "SDD-EVM-000" -e "SDD-EVM-0012"
```

Que o validador não ficou permissivo é coberto pelo critério 1
(`test_criada_depois_da_regra_reprova`, `test_mesmo_dia_da_regra_reprova`,
`test_na_na_saida_reprova`), independente do estado dos dados do
projeto.

## Instruções específicas para a IA implementadora

- Não alterar `rule_applies` nem `rule_applies_since_date` em
  `framework_lib.py` — só o chamador em `validate_state.py`.
- `table_rows` continua existindo e em uso para contar critérios; não
  remover.
- Rodar `python3 _framework/scripts/render_prompts.py` (sem `--check`)
  depois de editar `validate_state.py`, e commitar a cópia gerada da
  skill no mesmo PR.
- Sensor obrigatório do teste de guarda: reintroduzir temporariamente uma
  chamada `rule_applies(` em `validate_state.py` (espaço descartável,
  nunca commit), confirmar que
  `test_nenhum_validador_chama_rule_applies_direto` falha, desfazer.
- Critério 2 depende do repositório `viverMelhor` presente em
  `/home/michel/projetos/viverMelhor`; se ausente, registrar "não rodado —
  repositório ausente" na evidência e manter `approved` até rodar.
- Branch `sdd/SDD-DTF-0018-validate-state-data` a partir de `main`, PR —
  nunca commit direto (gate seção 14). Commits em Conventional Commits com
  `Refs: SDD-DTF-0018`.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Arquivos tocados: `_framework/scripts/validate_state.py`,
      `_framework/scripts/tests/test_validate_state.py` e a cópia gerada
      em `_framework/skills/doc-traceability-framework/scripts/validate_state.py`
      — qualquer outro arquivo é escopo não registrado ou scope creep.
- [x] Nenhuma abstração, config ou refactor extra sem requisito acima.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
A tabela fica **nesta seção**; `docs/sdd/validation.md` é o relatório
complementar.

**Verificador independente:** sim — subagente separado da sessão que implementou (PR #58), sem ler o histórico dela; entrada: esta SDD e `git diff bf1b6af 2c02209`. Verificação em 2026-09-14, branch `docs/sdd-dtf-0018-verificacao` a partir de `origin/main` (`2c02209`).

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -v` | `10 passed in 0.69s`, exit 0 | Seis mutações temporárias em `validate_state.py` (restauradas por cópia do original, nunca commitadas), cada uma derrubou exatamente 1 teste (`1 failed, 9 passed`): RF1 `created` trocado por `None` derruba `test_legado_antes_da_regra_nao_reprova`; RF2 escopo sempre linha inteira derruba `test_na_no_sensor_nao_reprova`; RF2 sem chave `passou` derruba `test_na_no_passou_reprova`; RF3 `col = 1` fixo derruba `test_tabela_seis_colunas_comando_vazio`; RF4 sem cabeçalho checando lista vazia derruba `test_sem_cabecalho_reconhecivel_linha_inteira`; RF5 comentário com `rule_applies(` anexado derruba `test_nenhum_validador_chama_rule_applies_direto`. Restaurado: `10 passed` | sim |
| 2 | Bloco C2: `python3 _framework/scripts/validate_state.py /home/michel/projetos/viverMelhor/docs/sdd --report-only` com saída filtrada por `grep -c -e "SDD-EVM-000" -e "SDD-EVM-0012"` | `0`; relatório completo: `✅ 20 documento(s) verificados: nenhuma SDD implemented sem evidência.` | Mesmo comando com o `validate_state.py` de `bf1b6af` (cópia temporária, removida): contagem `21` (18 linhas SDD-EVM-0001..0009 e 3 linhas SDD-EVM-0012 com resultado assumido em Sensor). Os 6 problemas reais citados no resumo (SDD-EVM-0013/0014/0015) já foram corrigidos no viverMelhor em `8bd6f85`; o não-afrouxamento fica com os testes do critério 1 | sim |
| 3 | `python3 _framework/scripts/render_prompts.py --check` | exit 0; `validate_state.py: sincronizado` e demais cópias em dia | Anexada linha `# drift` à cópia da skill (temporário): exit 1 com `validate_state.py: divergente`; restaurada, exit 0 | sim |
| 4 | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.` (docs/sdd 21 documentos ok, 3 exemplos); suíte `17 passed in 0.64s`, exit 0 | Regressão geral, sem sensor dedicado; lógica nova coberta pelos sensores do critério 1 | sim |
| 5 | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | `All checks passed!`, `11 files already formatted`, `Success: no issues found in 11 source files`, exit 0 | Checagem estática de paridade com o CI, sem sensor dedicado | sim |

Descompasso registrado (não bloqueante, decisão do humano): RF4 condiciona a checagem de linha inteira à ausência de coluna **comando**; a Especificação técnica consolidada (seguida à risca pelo código) condiciona à ausência de qualquer coluna reconhecida (comando, saída, passou). Com cabeçalho `# | Critério | Saída | Passou?`, um "n/a" em Critério não é apontado (antes era). A checagem de comando vazio cai corretamente para `row[1]`. Ver `docs/sdd/validation.md`.

Ajuste editorial feito na verificação: no bloco C2, o pipe passou do início da linha de continuação para o fim da linha anterior (mesma semântica). `table_rows` contava a linha `  | grep ...` do bloco de código como 6º critério de aceite (falso positivo pré-existente, fora do diff; detalhe em `validation.md`).

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0016 (mesma correção, aplicada só a `validate_doc.py`) |
