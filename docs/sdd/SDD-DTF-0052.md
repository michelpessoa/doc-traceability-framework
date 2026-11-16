---
id: SDD-DTF-0052
type: SDD
title: "Gate de CI do verify-sdd aceita o relatório com o nome legado validation-{PROJ}-{SEQ}.md, além do canônico"
status: draft
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-16"
updated: "2026-11-16"
relates_to: [RFC-DTF-0009, SDD-DTF-0032]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção avulsa decidida pelo owner em 2026-11-16, fora da cadeia da RFC-DTF-0009 (que só a cita como origem do achado); ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0047). Leia esta SDD inteira; ela nomeia a função, o nome aceito e os testes. Teste primeiro, visto falhar; depois o código. A cópia do script na skill é gerada por render_prompts.py, nunca à mão. O central espelha os mesmos arquivos em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [ci, verify-sdd, gate, relatorio, compatibilidade]
---

# Gate de CI do verify-sdd aceita o relatório com o nome legado validation-{PROJ}-{SEQ}.md, além do canônico

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`_framework/scripts/ci_gate_verify_sdd.py` só procura o relatório em
`docs/sdd/validation-{sdd_id}.md`, ou seja, `validation-SDD-EVM-0068.md`. O
EVM grava `validation-EVM-0068.md`, nome que o próprio `workflow-rules.yaml`
usa como exemplo em `operational_artifacts` (`validation-EVM-0013.md`).
Ligado no EVM como está, o gate reprovaria SDDs verificadas corretamente.
Achado pela fábrica agêntica (proposta 003) e citado na RFC-DTF-0009. Esta
SDD faz o gate aceitar os dois nomes, com o canônico tendo precedência, sem
exigir renomear relatórios existentes.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica. Decisão do owner em 2026-11-16: aceitar os dois nomes, não renomear
os relatórios do EVM (regra de não retroatividade da `lessons_policy`).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | O gate aceita o relatório no nome canônico `validation-{sdd_id}.md` (ex.: `validation-SDD-EVM-0068.md`) ou no nome legado `validation-{sdd_id sem o prefixo "SDD-"}.md` (ex.: `validation-EVM-0068.md`) | Quando só o nome legado existir no head com `**Veredito:** PASS` e cobertura completa, o gate deve passar |
| RF02 | Com os dois nomes presentes, vale o canônico | Quando os dois existirem e só o legado tiver PASS, o gate deve reprovar citando o caminho canônico |
| RF03 | Sem nenhum dos dois, a mensagem cita os dois caminhos procurados | Quando nenhum existir, o motivo de reprovação deve conter os dois caminhos e `(RF02)` |
| RF04 | As mensagens de cobertura de RF-ID citam o caminho realmente lido | Quando o relatório lido for o legado e faltar um RF-ID, o motivo deve citar `validation-{PROJ}-{SEQ}.md` |
| RF05 | O guia de adoção do gate documenta os dois nomes e a precedência | Quando `grep` procurar o nome legado em `docs/guias/gate-ci-verify-sdd.md`, deve encontrar |

Fora de escopo: o texto de `workflow-rules.yaml` (o canônico continua o
que está escrito lá), a skill e o procedimento `verify-sdd`, o
`verify-sdd-gate.yml.example` e qualquer renomeação nos projetos.

## Especificação técnica consolidada

- **Onde.** `check_validation_presence(sdd_id, head)` em
  `_framework/scripts/ci_gate_verify_sdd.py`. Passa a tentar, em ordem,
  `docs/sdd/validation-{sdd_id}.md` e, se `sdd_id` começar com `SDD-`,
  `docs/sdd/validation-{sdd_id[4:]}.md`. Devolve `(path, texto)` do primeiro
  que existir em `head`; se nenhum, a lista com um motivo que cita os dois
  caminhos. A assinatura não muda.
- **Mensagem do RF03 de cobertura.** `check_rf_coverage` ganha o parâmetro
  `validation_path: str` e o usa na mensagem no lugar do nome montado;
  `evaluate_gate` passa o caminho devolvido pela presença.
- **Testes.** Em `_framework/tests/test_ci_gate_verify_sdd.py`, três testes
  novos no padrão dos existentes (repositório git real, sem mock): legado
  sozinho passa; os dois presentes com PASS só no legado reprova citando o
  canônico; ausência total cita os dois caminhos. Mais um para RF04.
- **Docstring e guia.** A docstring do módulo e o item 1 de "O que o gate
  confere" em `docs/guias/gate-ci-verify-sdd.md` citam os dois nomes e a
  precedência.
- **Cópia da skill.** `_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py`
  é regenerada por `render_prompts.py`.
- **Espelho no central.** Os mesmos quatro arquivos: o script, a cópia da
  skill, o teste e o guia.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar com o código atual | RF01, RF02, RF03, RF04 | `_framework/tests/test_ci_gate_verify_sdd.py` | |
| 2 | Presença com os dois nomes e caminho real nas mensagens | RF01, RF02, RF03, RF04 | `_framework/scripts/ci_gate_verify_sdd.py` | 1 |
| 3 | Regenerar a cópia da skill e atualizar o guia | RF05 | `_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py`, `docs/guias/gate-ci-verify-sdd.md` | 2 |
| 4 | Espelhar no central em branch e PR próprios | RF01 a RF05 | `central:_framework/scripts/ci_gate_verify_sdd.py`, `central:_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py`, `central:_framework/tests/test_ci_gate_verify_sdd.py`, `central:docs/guias/gate-ci-verify-sdd.md` | 3 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01, RF02, RF03, RF04: testes novos | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py -q -k "legado or canonico or nenhum_relatorio"` | ANTES da task 2: pelo menos 3 failed; DEPOIS: todos passam | automatizado |
| A02 | RF01: sensor de mutação | Em cópia descartável, remover a tentativa do nome legado em `check_validation_presence`; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF02: sensor da precedência | Em cópia descartável, inverter a ordem dos dois caminhos; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A04 | RF05: guia | `grep -c "validation-{PROJ}-{SEQ}.md" docs/guias/gate-ci-verify-sdd.md` | Pelo menos `1` | automatizado |
| A05 | Gerados em dia e cópia da skill idêntica | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/ci_gate_verify_sdd.py _framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py` | `exit=0` e `cmp` sem saída | automatizado |
| A06 | Suíte completa sem regressão | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | 0 failed | automatizado |
| A07 | Só os arquivos previstos mudaram | `git diff --name-only origin/main` | Só os arquivos das tasks 1 a 3, esta SDD e os gerados de `docs/sdd/` (`registry.yaml`, `registry.md`, `INDEX.md`) | automatizado |
| A08 | Espelho no central | No central: `for f in _framework/scripts/ci_gate_verify_sdd.py _framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py _framework/tests/test_ci_gate_verify_sdd.py docs/guias/gate-ci-verify-sdd.md; do cmp <kit>/$f $f && echo "igual $f"; done` | 4 linhas `igual ...` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0052-relatorio-nome-legado`, a partir
  de `origin/main`. Commits com `Refs: SDD-DTF-0052`. Nunca em `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Não mudar** `workflow-rules.yaml`, a skill `verify-sdd`, os
  procedimentos nem o `.yml.example`.
- **Gerados só por script:** `render_prompts.py` para a cópia da skill e os
  índices; `generate_registry_md.py docs/sdd` para o `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  separada.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF05) tem código
      correspondente.
- [ ] Todo arquivo tocado pela implementação aparece na "Decomposição em
      tasks".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado.
- [ ] `workflow-rules.yaml` intocado e `framework.version` igual ao de
      `origin/main`.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** a preencher pela verificação.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | nenhum (sizing small, precedente SDD-DTF-0047) |
| relates_to | RFC-DTF-0009 (origem do achado, proposta 003 da fábrica), SDD-DTF-0032 (criou o gate) |
| Gate RFC → ADR | Nenhum critério de `decision_gates.rfc_to_adr` se aplica |
