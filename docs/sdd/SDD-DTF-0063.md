---
id: SDD-DTF-0063
type: SDD
title: "check_renderings.py cumpre a checagem 4: status e tipo inexistentes nas renderizações reprovam"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0060]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção de tooling achada na verificação da SDD-DTF-0060 (rodada 1, item 5: status inexistente no SKILL.md passou com exit 0); ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0056). Leia esta SDD inteira; ela nomeia as três regras, as mensagens e os testes. As regras foram desenhadas para não acusar nada nas cinco renderizações de origin/main em 2026-11-25: se acusarem, a regra está errada, não a renderização. Teste primeiro, visto falhar. A cópia do script na skill é gerada por render_prompts.py. O central espelha em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [check_renderings, tooling, status, tipos, renderizacoes]
---

# check_renderings.py cumpre a checagem 4: status e tipo inexistentes nas renderizações reprovam

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

A docstring de `_framework/scripts/check_renderings.py` promete quatro
checagens. A quarta é "Nenhuma renderização cita tipo ou status que não
existe no YAML", mas `main` não a implementa: compara tipos ativos, Iron
Laws, sizing e tipos legados, e não confere status nem tipo inexistente.
Na verificação da SDD-DTF-0060, um status inventado (`obsolete`) inserido
no `SKILL.md` passou com `exit=0`. Esta SDD implementa a checagem com três
regras estreitas, que não acusam nada nas renderizações atuais e acusam o
erro que importa: um status que não está em `status_lifecycle.states` nem
em `incident_lifecycle.states`, e um prefixo de id que não é tipo.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: uma checagem nova num validador existente, cumprindo o que a
docstring já promete. `workflow-rules.yaml` e `framework.version` não
mudam.

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Status em cadeia: no texto normalizado do jeito que `main` já faz (sem `` ` `` e `*`) e com as quebras de linha trocadas por espaço, toda palavra minúscula (`[a-z_]+`) de uma cadeia de três ou mais palavras ligadas por `→` (aceitando alternativas com `\|`, como `implemented\|rejected`) tem de estar em `status_lifecycle.states` ou em `incident_lifecycle.states`; se não estiver, a falha é `{rel}: cita o status inexistente '{palavra}'.` | Quando uma renderização tiver `draft → obsolete → approved`, `check_renderings.py` deve sair com 1 e imprimir `cita o status inexistente 'obsolete'` |
| RF02 | Status declarado: no texto bruto, todo `` `status: <palavra>` `` entre crases tem de estar nos mesmos estados; a falha usa a mesma mensagem do RF01 | Quando uma renderização tiver `` `status: obsolete` ``, o script deve sair com 1 e imprimir a mensagem |
| RF03 | Tipo em id: no texto normalizado, todo prefixo de id no formato `{TIPO}-{PROJETO}-{SEQ}` (regex `\b([A-Z]+)-(?:\{PROJECT_CODE\}\|[A-Z][A-Z0-9]*)-(?:\d{4}\|\{SEQ4?\}\|X\|N)\b`) tem de estar em `document_types` ou em `legacy_document_types`; se não estiver, a falha é `{rel}: cita o tipo inexistente '{prefixo}'.` | Quando uma renderização tiver `XYZ-EVM-0001`, o script deve sair com 1 e imprimir `cita o tipo inexistente 'XYZ'` |
| RF04 | As cinco renderizações de `RENDERINGS` em `origin/main` continuam passando, sem falha nova | Quando `check_renderings.py` rodar no kit sem mutação, deve sair com 0 |
| RF05 | Testes num arquivo novo, `_framework/scripts/tests/test_check_renderings_unknown.py`, cobrem RF01 a RF04, e incluem um caso negativo para cada regra (cadeia de dois termos, `repository_status: none_yet` sem crases e uma palavra como `feature/x → develop`, que não podem acusar) | Quando o pytest do arquivo rodar, todos devem passar, e com a regra do RF01 desligada pelo menos um deve falhar |
| RF06 | `_framework/scripts/tests/mutations.yaml` ganha uma mutação que desliga a regra do RF01, morta por `test_check_renderings_unknown.py` | Quando `selftest.py` rodar, a mutação nova deve morrer e a contagem de mutações deve subir em uma unidade |

Fora de escopo: exigir em `check_renderings.py` os fatos novos do núcleo
canônico (SDD-DTF-0062); a sincronização dos prompts da skill
(SDD-DTF-0061); checar status em `QUICKSTART.md`, que já fica fora de
`RENDERINGS` por desenho.

## Especificação técnica consolidada

- **Onde.** `_framework/scripts/check_renderings.py`: uma função nova,
  `check_unknown_names(rel: str, raw: str, statuses: set[str], types: set[str]) -> list[str]`,
  chamada no laço de `RENDERINGS` em `main`, somando ao `problems`.
- **Conjuntos.** `statuses` = `status_lifecycle.states` ∪
  `incident_lifecycle.states`; `types` = chaves de `document_types` ∪ chaves
  de `legacy_document_types`.
- **Regras.** RF01: `re.finditer(r"(?<![\w/-])[a-z_]+(?:\s*→\s*[a-z_]+(?:\|[a-z_]+)*){2,}", texto)`
  sobre o texto sem `` ` ``/`*` e com `\s*\n\s*` trocado por espaço; cada
  `[a-z_]+` do trecho é conferido. RF02: `re.findall(r"`status:\s*([a-z_]+)`", raw)`.
  RF03: a regex do requisito sobre o texto normalizado. Cada palavra é
  reportada uma vez por renderização.
- **Docstring.** O item 4 passa a dizer como a checagem é feita (cadeias de
  status, `status:` entre crases e prefixo de id).
- **Testes.** `test_check_renderings_unknown.py` chama
  `check_unknown_names` com textos curtos (casos positivos e negativos do
  RF05) e roda `check_renderings.py` como subprocesso no kit real (RF04).
- **Gerado.** `_framework/skills/doc-traceability-framework/scripts/check_renderings.py`
  e `_framework/INDEX.md` saem de `render_prompts.py`.
- **Espelho no central.** O script, a cópia da skill, o teste,
  `mutations.yaml` e `_framework/INDEX.md`, em branch e PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar | RF01 a RF05 | `_framework/scripts/tests/test_check_renderings_unknown.py` | |
| 2 | Função nova, chamada no laço e docstring | RF01 a RF04 | `_framework/scripts/check_renderings.py` | 1 |
| 3 | Mutação do selftest | RF06 | `_framework/scripts/tests/mutations.yaml` | 2 |
| 4 | Regenerar a cópia da skill e o índice | RF01 a RF04 | `_framework/skills/doc-traceability-framework/scripts/check_renderings.py`, `_framework/INDEX.md` | 2 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF06 | `central:_framework/scripts/check_renderings.py`, `central:_framework/skills/doc-traceability-framework/scripts/check_renderings.py`, `central:_framework/scripts/tests/test_check_renderings_unknown.py`, `central:_framework/scripts/tests/mutations.yaml`, `central:_framework/INDEX.md` | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A07.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01 a RF05: testes novos | `python3 -m pytest _framework/scripts/tests/test_check_renderings_unknown.py -q` | ANTES da task 2: pelo menos 3 failed; DEPOIS: todos passam | automatizado |
| A02 | RF01: o kit real reprova status inventado | Em cópia descartável do kit, trocar `in_review` por `obsolete` numa cadeia de status do `SKILL.md`; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `cita o status inexistente 'obsolete'` e `exit=1` | automatizado |
| A03 | RF03: o kit real reprova tipo inventado | Em cópia descartável do kit, acrescentar `XYZ-EVM-0001` ao `SKILL.md`; rodar o script | `cita o tipo inexistente 'XYZ'` e `exit=1` | automatizado |
| A04 | RF04: sem falso positivo | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"` | `exit=0` | automatizado |
| A05 | RF06: selftest | `python3 _framework/scripts/selftest.py; echo "exit=$?"` | `N mutação(ões): todos os mutantes morreram.`, com N uma unidade acima do de `origin/main` antes da branch, e `exit=0` | automatizado |
| A06 | Gerados, suíte, lint e escopo | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/check_renderings.py _framework/skills/doc-traceability-framework/scripts/check_renderings.py; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0`; `cmp` sem saída; 0 failed; ruff e mypy sem erro; `exit=0`; só os arquivos das tasks 1 a 4, esta SDD, o seu `validation-SDD-DTF-0063.md` e os gerados de `docs/sdd/` | automatizado |
| A07 | Central: espelho idêntico e sem falso positivo | No central: `cmp` dos arquivos da task 5 contra o kit; `python3 _framework/scripts/check_renderings.py; echo "exit=$?"`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` nos dois | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0063-check-renderings-status-tipo`,
  já aberta com esta SDD. Comece por `git fetch origin main && git merge
  origin/main` e regenere os gerados se houver conflito. Commits com
  `Refs: SDD-DTF-0063`. Nunca em `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Se a SDD-DTF-0062 entrar antes,** o `AGENTS.md` deixa de ter a cadeia
  de status, e o A04 tem de continuar passando sobre o texto novo.
- **Não mudar** `workflow-rules.yaml`, as renderizações, `render_prompts.py`
  nem as outras checagens de `check_renderings.py`.
- **Gerados só por script:** `render_prompts.py` para a cópia da skill e os
  índices; `generate_registry_md.py` para `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF06) tem código ou teste
      correspondente.
- [ ] Todo arquivo tocado aparece nas tasks ou nas instruções.
- [ ] Nenhuma abstração, config ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** {sim | não — mesma sessão que implementou}

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
