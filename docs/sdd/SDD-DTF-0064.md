---
id: SDD-DTF-0064
type: SDD
title: "check_renderings.py acusa tipo inexistente também em id com placeholder de sequência ({SEQ4}, {SEQ})"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0063]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção da regex do RF03 da SDD-DTF-0063, achada na verificação independente dela (validation-SDD-DTF-0063.md, achado do ponto da regex e achado não bloqueante 1); ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0056). Depende da SDD-DTF-0063: a branch sai da dela, e a implementação só começa com a SDD-DTF-0063 em main ou com merge da branch dela. Leia esta SDD inteira; ela nomeia a regex, os testes e a mutação. Teste primeiro, visto falhar; depois o código. A cópia do script na skill e os índices são gerados por render_prompts.py, nunca à mão. O central espelha em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [check_renderings, tooling, tipos, renderizacoes, regex]
---

# check_renderings.py acusa tipo inexistente também em id com placeholder de sequência ({SEQ4}, {SEQ})

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

A SDD-DTF-0063 fez `check_renderings.py` reprovar prefixo de id que não é
tipo, com a regex fixada no RF03 dela e guardada em `ID_PREFIX`:
`\b([A-Z]+)-(?:\{PROJECT_CODE\}|[A-Z][A-Z0-9]*)-(?:\d{4}|\{SEQ4?\}|X|N)\b`.
O `\b` final exige um caractere de palavra logo depois do `}`, então as
alternativas `\{SEQ4?\}` quase nunca casam: `FOO-{PROJECT_CODE}-{SEQ4}`,
`FOO-DTF-{SEQ4}` e `FOO-{PROJECT_CODE}-{SEQ}.` passam sem aviso, embora o
RF03 prometa "todo prefixo de id". É justamente o formato dos templates e
das renderizações (`SKILL.md`: `` `{TYPE}-{PROJECT_CODE}-{SEQ4}` ``). Por
isso, dois casos de `test_rf03_tipos_ativos_e_legados_passam`
(`SPEC-{PROJECT_CODE}-{SEQ4}` e `TS-EVM-{SEQ}`) não testam nada. A
verificação da SDD-DTF-0063 registrou isso como defeito de especificação
não bloqueante e conferiu, nas cinco renderizações, que trocar o `\b`
final por `(?!\w)` casa os mesmos 8 ids e não dá falso positivo. Esta SDD
faz essa troca.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: uma regex de um validador existente e os testes dela.
`workflow-rules.yaml`, `kit-index.yaml` e `framework.version` não mudam
(`lessons_policy`: é falha de execução, não desenho). A SDD-DTF-0063 está
`implemented` e não é editada: o texto do RF03 dela continua como
registro do que foi aprovado e implementado, e esta SDD é a correção.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Em `ID_PREFIX` (`_framework/scripts/check_renderings.py`), o `\b` final vira `(?!\w)`, e só ele: a regex fica `\b([A-Z]+)-(?:\{PROJECT_CODE\}\|[A-Z][A-Z0-9]*)-(?:\d{4}\|\{SEQ4?\}\|X\|N)(?!\w)`. A mensagem de falha continua `{rel}: cita o tipo inexistente '{prefixo}'.` | Quando uma renderização tiver `FOO-{PROJECT_CODE}-{SEQ4}`, o script deve sair com 1 e imprimir `cita o tipo inexistente 'FOO'` |
| RF02 | O que já não era id continua sem acusar: sequência de dígitos diferente de quatro (`XYZ-EVM-12`, `XYZ-EVM-00012`) e `X` ou `N` seguidos de letra (`ADR-EVM-Xy`) | Quando o texto tiver só `XYZ-EVM-12`, `XYZ-EVM-00012` e `ADR-EVM-Xy`, a checagem não deve devolver falha |
| RF03 | As renderizações atuais continuam sem falso positivo | Quando `check_renderings.py` rodar no kit, deve sair com 0 |
| RF04 | Testes em `_framework/scripts/tests/test_check_renderings_unknown.py` cobrem RF01 e RF02: um teste novo com `FOO-{PROJECT_CODE}-{SEQ4}`, `BAR-DTF-{SEQ4}.` e `BAZ-{PROJECT_CODE}-{SEQ}` reprovando os três prefixos, e os negativos do RF02. Os testes que já existem não mudam | Quando o pytest do arquivo rodar, todos devem passar, e com o `\b` final de volta pelo menos um deve falhar |
| RF05 | `_framework/scripts/tests/mutations.yaml` ganha uma mutação que devolve o `\b` final de `ID_PREFIX`, morta por `test_check_renderings_unknown.py` | Quando `python3 _framework/scripts/selftest.py` rodar, a mutação nova deve morrer, e a contagem de mutações deve subir em uma unidade |

Fora de escopo: os outros achados não bloqueantes da verificação da
SDD-DTF-0063 (chamada da checagem no `main` sem teste automatizado; a
união com `legacy_document_types` não discriminada; a alternativa de
quebra de linha redundante em `STATUS_CHAIN`); as regras dos RF01 e RF02
da SDD-DTF-0063; o texto das renderizações; `render_prompts.py`.

## Especificação técnica consolidada

- **Onde.** `_framework/scripts/check_renderings.py`, constante
  `ID_PREFIX`. Nada mais muda no script: `check_unknown_names` continua
  usando `ID_PREFIX.findall`.
- **Por que `(?!\w)`.** Ele recusa o mesmo que o `\b` recusava depois de
  `\d{4}`, `X` e `N` (um caractere de palavra a mais), e deixa de exigir
  um caractere de palavra depois do `}` dos placeholders.
- **Testes.** No padrão dos testes de RF03 que já existem no arquivo
  (`_check` e `_tipo`): um teste novo para os três placeholders do RF04,
  na ordem de aparição; um teste novo para os negativos do RF02.
- **Mutação.** No formato da entrada da SDD-DTF-0063: `validator`
  `_framework/scripts/check_renderings.py`, `test_file`
  `_framework/scripts/tests/test_check_renderings_unknown.py`, `find` o
  trecho final `|X|N)(?!\w)")` da linha de `ID_PREFIX` e `replace` o
  mesmo trecho com `\b` no lugar de `(?!\w)`. O `find` tem de aparecer uma
  única vez no script.
- **Gerados.** A cópia `_framework/skills/doc-traceability-framework/scripts/check_renderings.py`
  e `_framework/INDEX.md` saem de `render_prompts.py`.
- **Espelho no central.** O script, a cópia da skill, o teste,
  `mutations.yaml` e `_framework/INDEX.md`, em branch e PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar | RF01, RF02, RF04 | `_framework/scripts/tests/test_check_renderings_unknown.py` | |
| 2 | Trocar o `\b` final de `ID_PREFIX` | RF01 a RF03 | `_framework/scripts/check_renderings.py` | 1 |
| 3 | Mutação do selftest | RF05 | `_framework/scripts/tests/mutations.yaml` | 2 |
| 4 | Regenerar a cópia da skill e o índice | RF01 | `_framework/skills/doc-traceability-framework/scripts/check_renderings.py`, `_framework/INDEX.md` | 2 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF05 | `central:_framework/scripts/check_renderings.py`, `central:_framework/skills/doc-traceability-framework/scripts/check_renderings.py`, `central:_framework/scripts/tests/test_check_renderings_unknown.py`, `central:_framework/scripts/tests/mutations.yaml`, `central:_framework/INDEX.md` | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A07.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01, RF02, RF04: testes | `python3 -m pytest _framework/scripts/tests/test_check_renderings_unknown.py -q` | ANTES da task 2: pelo menos 1 failed; DEPOIS: todos passam | automatizado |
| A02 | RF04: sensor | Em cópia descartável, devolver o `\b` final de `ID_PREFIX`; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF01: o kit real reprova tipo inventado com placeholder | Em cópia descartável do kit, acrescentar `` Veja `FOO-{PROJECT_CODE}-{SEQ4}`. `` ao `SKILL.md`; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `cita o tipo inexistente 'FOO'` e `exit=1` | automatizado |
| A04 | RF03: sem falso positivo | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `✅` e `exit=0` | automatizado |
| A05 | RF05: selftest | `python3 _framework/scripts/selftest.py; echo "exit=$?"` | `N mutação(ões): todos os mutantes morreram.`, com N uma unidade acima do da base da branch, e `exit=0` | automatizado |
| A06 | Gerados, suíte, lint e escopo | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/check_renderings.py _framework/skills/doc-traceability-framework/scripts/check_renderings.py; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only <base>`, com `<base>` = `origin/main` se a SDD-DTF-0063 já estiver em main, ou o head da branch dela | `exit=0`; `cmp` sem saída; 0 failed; ruff e mypy sem erro; `exit=0`; só os arquivos das tasks 1 a 4, esta SDD, o seu `validation-SDD-DTF-0064.md`, `docs/sdd/registry.yaml` e os gerados de `docs/sdd/` | automatizado |
| A07 | Central: espelho idêntico | No central: `cmp` dos arquivos da task 5 contra o kit; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` nos dois | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0064-regex-placeholder-check-renderings`,
  aberta a partir da branch da SDD-DTF-0063. Se a SDD-DTF-0063 já estiver
  em main, comece por `git fetch origin main && git merge origin/main`;
  senão, por `git merge` da branch dela. Regenere os gerados se houver
  conflito em `docs/sdd/`. Commits com `Refs: SDD-DTF-0064`. Nunca em
  `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Não mudar** os testes que já existem em
  `test_check_renderings_unknown.py`, `STATUS_CHAIN`, `STATUS_DECLARED`,
  `check_unknown_names` além do uso de `ID_PREFIX`, `workflow-rules.yaml`,
  `kit-index.yaml`, as renderizações nem a SDD-DTF-0063.
- **Gerados só por script:** `render_prompts.py` para a cópia da skill e os
  índices; `generate_registry_md.py` para `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF05) tem código ou teste
      correspondente.
- [x] Todo arquivo tocado aparece nas tasks ou nas instruções.
- [x] Nenhuma abstração, config ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** sim

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0064.md`. Veredito: **PASS**.

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0064.md /home/user/doc-traceability-central/docs/DTF; echo "exit=$?"`; `git diff 57454fa HEAD -- docs/sdd/SDD-DTF-0064.md` | `✅ source_docs de SDD-DTF-0064.md conferem com o registry central.` `exit=0`; `source_docs: []`, sizing `small`: RF01 a RF05 escritos na própria SDD, itens 2 a 4 do passo 0 não se aplicam; desde `57454fa` (commit da review de aprovação do owner na PR #159, "Aprovado") o único diff da SDD é `status: in_review` → `approved` | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 1 | A01 | `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest _framework/scripts/tests/test_check_renderings_unknown.py -q`, no kit em `e5ac326` e numa cópia de `2430f9a` (testes antes da task 2) | `e5ac326`: `18 passed`; `2430f9a`: `1 failed, 17 passed` (`test_sdd0064_placeholders_de_sequencia_reprovam_tipo_inexistente`) | ver A02; `(?!\w)` removido (sem fronteira alguma): `1 failed` (`test_sdd0064_negativo_sequencia_que_nao_e_id_nao_acusa`, por `XYZ-EVM-00012`); restaurado: `18 passed`. `ID_PREFIX.findall` no texto de `test_rf03_tipos_ativos_e_legados_passam`: novo `['SPEC', 'SDD', 'ADR', 'PRD', 'TS']`, antigo `['SDD', 'ADR', 'PRD']`, ou seja, `SPEC-{PROJECT_CODE}-{SEQ4}` e `TS-EVM-{SEQ}` agora casam e passam | Sim | `_framework/scripts/tests/test_check_renderings_unknown.py:127`, `:131` | automatizado |
| 1 | A02 | cópia descartável (`git archive e5ac326`): `\|X\|N)(?!\w)")` → `\|X\|N)\b")` em `ID_PREFIX` (trecho único no script); pytest do A01; restaurado pela cópia guardada (`cmp` igual ao kit) | com a mutação: `1 failed, 17 passed` (`test_sdd0064_placeholders_de_sequencia_reprovam_tipo_inexistente`); restaurado: `18 passed` | o próprio critério é o sensor | Sim | `_framework/scripts/tests/test_check_renderings_unknown.py:127` | automatizado |
| 1 | A03 | cópia descartável (`git archive e5ac326`): `` Veja `FOO-{PROJECT_CODE}-{SEQ4}`. `` acrescentado a `_framework/skills/doc-traceability-framework/SKILL.md`; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `❌ 1 problema(s) encontrado(s):` `skills/doc-traceability-framework/SKILL.md: cita o tipo inexistente 'FOO'.` `exit=1` | mesma linha numa cópia de `2430f9a` (regex antiga): `✅ 5 renderização(ões) concordam`, `exit=0`, ou seja, o critério discrimina | Sim | `_framework/scripts/check_renderings.py:163` (via script) | automatizado |
| 1 | A04 | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `✅ 5 renderização(ões) concordam com workflow-rules.yaml (8 tipos ativos, 6 Iron Laws, 4 níveis).` `exit=0` | `test_rf04_kit_real_passa` na suíte do A01: passa; sem mutação nova específica | Sim | `_framework/scripts/tests/test_check_renderings_unknown.py:145` | automatizado |
| 1 | A05 | `PYTHONDONTWRITEBYTECODE=1 python3 _framework/scripts/selftest.py; echo "exit=$?"` em cópia de `e5ac326` e em cópia de `2a4c5c9` (`origin/main` = merge-base) | `e5ac326`: `✅ 13 mutação(ões): todos os mutantes morreram.` `exit=0`; base: `✅ 12 mutação(ões): todos os mutantes morreram.` `exit=0` (N sobe uma unidade) | a mutação nova, aplicada à mão (A02), mata `test_sdd0064_placeholders_de_sequencia_reprovam_tipo_inexistente`, teste de comportamento (regex válida, sem erro de import) | Sim | `_framework/scripts/tests/mutations.yaml:80` | automatizado |
| 1 | A06 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/check_renderings.py _framework/skills/doc-traceability-framework/scripts/check_renderings.py; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` (SDD-DTF-0063 em main; `origin/main` = merge-base `2a4c5c9`) | `exit=0`, 0 `❌` (`check_renderings.py: sincronizado`, `_framework/INDEX.md: em dia`); `cmp` sem saída; `556 passed in 75.14s`; `All checks passed!`; `44 files already formatted`; `Success: no issues found in 44 source files`; `✅ Todas as verificações do framework passaram.` `exit=0`; diff: script, cópia da skill, teste, `mutations.yaml`, `SDD-DTF-0064.md`, `docs/sdd/INDEX.md`, `registry.md`, `registry.yaml` | sem mutação própria (suíte e lista do diff) | Sim | `n/a` (suíte inteira e lista do diff) | automatizado |
| 1 | A07 | no central `/home/user/doc-traceability-central` (`048251a`, só leitura): `cmp` de cada arquivo da task 5 contra o kit | `check_renderings.py` e a cópia da skill `differ: char 7060, line 163`; `test_check_renderings_unknown.py` `differ: char 3836, line 122`; `mutations.yaml` `EOF ... after byte 4282, line 78`; `_framework/INDEX.md` igual (`cmp=0`). O central ainda não tem o espelho desta SDD | sem teste automatizado nesta etapa: o espelho vem depois do merge no kit (task 5), e o critério é rodado por quem espelhar | Pendente: etapa pós-merge no kit | `n/a` (`cmp`) | automatizado (estado pré-espelho) |
