---
id: SDD-DTF-0032
type: SDD
title: "Gate de CI do verify-sdd: presença+veredito+cobertura de RF-ID, cross-check de evidência e override de incidente validado contra o registry"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0011"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0011.md"
  - id: "ADR-DTF-0004"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0004.md"
  - id: "ADR-DTF-0005"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0005.md"
consumption_instructions: "Leia SPEC-DTF-0011 inteira antes de tocar em qualquer arquivo — esta SDD consolida Parte 1/Parte 2, mas os casos de borda e o texto completo de erro por RF vivem só na SPEC. RF04, RF05 e RF07 exigem sensor de discriminação real (mutação que quebra o comportamento e volta a passar depois) — não aceite teste verde sem mutação testada. Editar sempre as duas cópias do kit (_framework/scripts/ e _framework/skills/doc-traceability-framework/scripts/) no mesmo commit."
supersedes: null
superseded_by: null
tags: [ci, gate_scope_verification, sdd-verifier, enforcement, incidente]
---

# Gate de CI do verify-sdd: presença+veredito+cobertura de RF-ID, cross-check de evidência e override de incidente validado contra o registry

## Resumo executivo

Adiciona a Camada 2 (obrigatória, tool-agnostic) do gate `verify-sdd`:
um script de CI (`ci_gate_verify_sdd.py`) que bloqueia merge de PR que
muda uma SDD para `implemented` sem `validation-SDD-{ID}.md` de
veredito `PASS` real, cobertura completa de RF-ID e critérios de aceite
não afrouxados entre `approved` e `implemented`, com válvula de escape
para incidente ativo validada contra o registry central via checkout
raso (não só texto do PR).

## Decisão(ões) de arquitetura aplicável(is)

- ADR-DTF-0004: duas camadas independentes — Camada 1 (opt-in, por
  ferramenta, hook de sessão) e Camada 2 (obrigatória, tool-agnostic,
  script de CI que parseia front-matter via `git show` real, nunca
  regex sobre diff textual). Esta SDD implementa só a Camada 2.
- ADR-DTF-0005: a válvula de escape do gate (label `incident-override` +
  `INC-{ID}`) é validada por checkout raso (`--depth 1`) do
  `registry.yaml` do repositório central, não aceita label+texto por si
  só. Override aceito é logado (id, status, timestamp).

## Requisitos consolidados

(Consolidado de SPEC-DTF-0011, Parte 1.)

| RF-ID | Requisito |
|---|---|
| RF01 | Parsear front-matter das SDDs tocadas no PR via YAML real (`git show <base>:<path>` / `git show <head>:<path>`), nunca regex sobre diff. |
| RF02 | SDD que muda para `implemented` no PR exige `docs/sdd/validation-SDD-{ID}.md` com a linha `**Veredito:** PASS`. |
| RF03 | Cobertura de RF-ID: todo RF-ID da SDD tem linha de evidência correspondente no `validation-*.md`; sem correspondência reprova. |
| RF04 | Recusar PASS contradito por linha (tlc-spec-lean E1): qualquer linha da tabela de evidência com resultado != PASS reprova o check, mesmo com `**Veredito:**` global dizendo PASS. |
| RF05 | Congelar critérios de aceite entre `approved` e `implemented` (tlc-spec-lean E2): critério removido ou alterado sem `**Justificativa de mudança:**` citando o RF-ID no corpo do PR reprova. |
| RF06 | Válvula de escape textual: label `incident-override` + `INC-{ID}` no corpo do PR libera o check sem exigir RF02-RF05, sujeito a RF07. |
| RF07 | Override validado contra o registry central: checkout raso (`--depth 1`) de `docs/{PROJECT_CODE}/registry.yaml`; só libera se `INC-{ID}` existir e estiver `open`/`mitigated`; senão reprova e volta a exigir RF02-RF05. |
| RF08 | Override aceito é logado no stdout do CI: id do INC, status encontrado, timestamp. |
| RF09 | Front-matter que não parseia como YAML válido reprova com mensagem citando arquivo e exceção — nunca tratado como ausência silenciosa de mudança de status. |
| RF10 | `_framework/scripts/ci_gate_verify_sdd.py` e `_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py` byte-idênticos, checado por mecanismo de paridade automatizado. |

Casos de borda consolidados (ver SPEC-DTF-0011 para detalhe completo):
PR sem SDD tocada passa trivialmente; rename de SDD resolvido via `git
diff --find-renames` antes de comparar status (path novo tratado como
"nasceu implemented" se não resolver); múltiplas SDDs no mesmo PR são
avaliadas independentemente, relatório final lista resultado por
SDD-ID; `validation-*.md` cujo nome de arquivo não bate o ID é tratado
como ausente (casamento por nome do arquivo, não por conteúdo); falha
de checkout do registry central por credencial é erro operacional
(exit 2), nunca confundido com "INC não encontrado"; critério
reordenado com texto idêntico não conta como alteração (comparação por
conteúdo normalizado, não posição); label presente sem `INC-{ID}` no
corpo não libera a válvula — RF02-RF05 continuam exigidos.

## Especificação técnica consolidada

(Consolidado de SPEC-DTF-0011, Parte 2 — contratos, plano de
implementação e rollout completos estão na SPEC; aqui só o necessário
para implementar sem reabrir o documento de origem.)

**Fluxo:** três fases, na ordem — (1) detectar SDDs tocadas com
transição de status para `implemented` (RF01); (2) para cada uma,
validar presença + veredito + cobertura + não-afrouxamento (RF02-RF05),
a menos que a válvula de escape se aplique (RF06-RF08); (3) emitir
resultado agregado com mensagem por SDD. Sem componente de runtime
persistente.

**Contratos:**
- `_framework/scripts/ci_gate_verify_sdd.py` — função pública
  `evaluate_gate(base: str, head: str, changed_sdd_paths: list[str],
  pr_labels: list[str], pr_body: str, project_code: str,
  central_registry_path: str | None) -> GateResult`:
  ```
  GateResult = {
      passed: bool,
      per_sdd: list[SddCheckResult],
      overrides_used: list[OverrideLog],
  }
  SddCheckResult = {
      sdd_id: str,
      status_transition: str | None,   # ex.: "approved -> implemented"
      outcome: "pass" | "fail" | "skipped",
      reasons: list[str],
  }
  OverrideLog = {inc_id: str, status: str, timestamp: str}
  ```
  Funções internas por contrato de erro: `parse_frontmatter_at_revision()`,
  `check_validation_presence()`, `check_rf_coverage()`,
  `check_evidence_rows()`, `check_criteria_frozen()`,
  `validate_incident_override()`.
  CLI: `python3 _framework/scripts/ci_gate_verify_sdd.py --base <sha>
  --head <sha> --project-code <CODE> [--central-registry-path <path>]
  --pr-labels <label1,label2,...> --pr-body-file <path>` — texto legível
  por padrão, `--json` para `GateResult` serializado.
- `_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py`
  — cópia bundlada, byte-idêntica (RF10).
- `_framework/templates/ci/verify-sdd-gate.yml.example` — workflow de
  GitHub Actions de exemplo (adoção opt-in), documentando o passo de
  checkout raso do repositório central e a credencial necessária.
- Códigos de saída: `0` = passou; `1` = reprovado (RF02-RF05, RF07,
  RF09 — falha de conteúdo/evidência); `2` = erro operacional
  (credencial cross-repo inacessível, front-matter que quebra o parser
  de forma irrecuperável).

**Tratamento de erro por contrato** (RF-ID → exit code → onde):
RF02 → exit 1, `check_validation_presence()`; RF03 → exit 1,
`check_rf_coverage()`; RF04 → exit 1, `check_evidence_rows()`; RF05 →
exit 1, `check_criteria_frozen()`; RF07 (INC inválido) → exit 1,
`validate_incident_override()`; RF07 (falha de checkout) → exit 2,
mesma função; RF09 → exit 2, `parse_frontmatter_at_revision()`. Toda
mensagem cita SDD-ID/RF-ID/INC-ID específico (NFR).

**Rollout:** opt-in por projeto — o gate só se aplica quando o workflow
de CI do projeto invoca o script; nenhum projeto existente é afetado
automaticamente. Rollback: remover o step do workflow; sem migração de
dado (script somente leitura).

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Implementar `ci_gate_verify_sdd.py` (parser via `git show`, as 6 funções de checagem, `evaluate_gate`, CLI, exit codes 0/1/2) | RF01-RF09 | `_framework/scripts/ci_gate_verify_sdd.py` | |
| 2 | Cópia bundlada byte-idêntica | RF10 | `_framework/skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py` | 1 |
| 3 | Workflow de exemplo do GitHub Actions | (decisão pura) | `_framework/templates/ci/verify-sdd-gate.yml.example` | |
| 4 | Testes unitários + integração (inclui sensores de discriminação RF04, RF05, RF07) | RF01-RF09 | `_framework/tests/test_ci_gate_verify_sdd.py` | 1 |
| 5 | Mecanismo de paridade entre as duas cópias (não existe ainda no kit — criar mínimo: diff byte a byte) | RF10 | `_framework/tests/test_kit_parity.py` | 1, 2 |
| 6 | Ponteiro no `workflow-rules.yaml` (seção 16, `gate_scope_verification`) para o gate de CI como Camada 2, sem duplicar prosa | (decisão pura) | `_framework/rules/workflow-rules.yaml` | |
| 7 | Regenerar `AGENTS.md` a partir do YAML alterado na task 6 (`render_prompts.py` — arquivo gerado, não editar à mão) | (decisão pura) | `AGENTS.md`, `docs/especificacao.md` | 6 |
| 8 | Guia de adoção: workflow de exemplo, credencial cross-repo (RF07), label `incident-override` | (decisão pura) | `docs/guias/gate-ci-verify-sdd.md` | 3 |

Tasks 1, 3 e 6 não compartilham arquivo entre si — paralelizáveis. Task
2 depende de 1 (cópia byte-idêntica do que a 1 produzir). Task 4 depende
de 1. Task 5 depende de 1 e 2 (precisa das duas cópias existirem para
comparar). Task 7 depende de 6 (regeneração roda sobre o YAML já
alterado). Task 8 depende de 3 (documenta o workflow de exemplo já
escrito).

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — parse via `git show`, base vs head, sem regex sobre diff | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_parse_frontmatter_base_head -v` | Teste passa |
| 2 | RF02 — validation ausente reprova transição para `implemented` | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_validation_ausente_reprova -v` | Teste passa |
| 3 | RF03 — RF-ID sem linha de evidência reprova | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_rf_sem_cobertura_reprova -v` | Teste passa |
| 4 | RF04 — linha != PASS reprova mesmo com veredito global PASS (sensor de discriminação) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_linha_fail_reprova_apesar_de_veredito_pass -v` | Teste passa |
| 5 | RF05 — critério alterado sem justificativa reprova (sensor de discriminação) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_criterio_afrouxado_reprova -v` | Teste passa |
| 6 | RF05 — critério reordenado, texto idêntico, não reprova | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_criterio_reordenado_nao_reprova -v` | Teste passa |
| 7 | RF06/RF07 — override com INC válido libera | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_override_inc_valido_libera -v` | Teste passa |
| 8 | RF07 — override com INC inexistente/closed reprova (sensor de discriminação) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_override_inc_invalido_reprova -v` | Teste passa |
| 9 | RF07 — falha de credencial vira exit 2, não exit 1 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_falha_credencial_exit_2 -v` | Teste passa |
| 10 | RF08 — log de override aceito (id, status, timestamp) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_log_override_aceito -v` | Teste passa |
| 11 | RF09 — front-matter malformado vira exit 2 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_frontmatter_malformado_exit_2 -v` | Teste passa |
| 12 | RF10 — paridade das duas cópias | `python3 -m pytest _framework/tests/test_kit_parity.py::test_ci_gate_verify_sdd_paridade -v` | Teste passa |
| 13 | CLI ponta a ponta (PR de fixture com 2 SDDs, uma pass uma fail) | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_cli_pr_fixture_duas_sdds -v` | Teste passa |
| 14 | Ponteiro no `workflow-rules.yaml` seção 16 | `grep -n "ci_gate_verify_sdd" _framework/rules/workflow-rules.yaml` | Ao menos uma ocorrência na seção `gate_scope_verification` |
| 15 | `AGENTS.md` regenerado sem divergência do YAML | `python3 _framework/scripts/render_prompts.py --check` | Exit 0 |
| 16 | Workflow de exemplo existe e é YAML válido | `python3 -c "import yaml; yaml.safe_load(open('_framework/templates/ci/verify-sdd-gate.yml.example'))"` | Sem exceção |
| 17 | Guia de adoção existe e cobre credencial cross-repo + label | `grep -n "incident-override\|credencial" docs/guias/gate-ci-verify-sdd.md` | Ao menos uma ocorrência de cada termo |

## Instruções específicas para a IA implementadora

- Editar `ci_gate_verify_sdd.py` nas **duas cópias** listadas na task 2
  — esquecer uma delas falha o critério 12 (paridade).
- RF04, RF05 e RF07 exigem sensor de discriminação real nos testes:
  aplicar uma mutação que quebra o comportamento, confirmar que o teste
  falha, reverter, confirmar que volta a passar. Teste verde sem
  mutação testada não conta como "Sim" na tabela de evidência final.
- `parse_frontmatter_at_revision()` usa YAML real (`PyYAML` ou
  equivalente já usado pelos outros scripts do kit, ex.:
  `validate_doc.py`) sobre o conteúdo obtido via `git show` — nunca
  regex sobre texto de diff (RF01, requisito explícito da SPEC).
- Checkout raso do registry central (RF07) é só leitura de um arquivo
  (`--depth 1`, sparse quando possível) — nunca clone completo do
  repositório central.
- `_framework/rules/workflow-rules.yaml` é a fonte canônica; após
  editar a seção 16, rodar `render_prompts.py` (sem `--check`) para
  regenerar `AGENTS.md`/`docs/especificacao.md` antes de commitar — os
  gerados nunca são editados à mão.
- Não implementar a Camada 1 (hook de sessão / regra por ferramenta,
  RFC-DTF-0004) nem o item 2 da STRAT-DTF-0003 (despacho do
  `sdd-verifier`, escopo de SPEC-DTF-0012 / SDD futura) — fora de
  escopo desta SDD.
- Não aplicar retroativamente a SDDs já `implemented` sem
  `validation-*.md` — não há nenhuma nessa situação hoje; mesmo que
  houvesse, não seria alcançada por este gate.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima (RF01-RF10) tem código correspondente.
- [x] Todo arquivo tocado pela implementação aparece na tabela "Decomposição em tasks" acima.
- [x] Nenhuma abstração, config, feature flag ou refactor extra sem requisito consolidado (ex.: não implementar Camada 1 nem o despacho do `sdd-verifier` — fora de escopo, ver "Instruções específicas").

## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0032.md`. Veredito: **PASS**.

**Verificador independente:** sim

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_parse_frontmatter_base_head -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 2 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_validation_ausente_reprova -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 3 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_rf_sem_cobertura_reprova -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 4 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_linha_fail_reprova_apesar_de_veredito_pass -v` | 1 passed | `check_evidence_rows()` mutado p/ `return []`: teste falhou (`gate.passed` virou True); restaurado, voltou a passar | Sim |
| 5 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_criterio_afrouxado_reprova -v` | 1 passed | `check_criteria_frozen()` mutado p/ `justified = True` sempre: teste falhou; restaurado, voltou a passar | Sim |
| 6 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_criterio_reordenado_nao_reprova -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 7 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_override_inc_valido_libera -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 8 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_override_inc_invalido_reprova -v` | 1 passed | checagem de status `closed` mutada p/ `if False:`: teste falhou; restaurado, voltou a passar | Sim |
| 9 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_falha_credencial_exit_2 -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 10 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_log_override_aceito -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 11 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_frontmatter_malformado_exit_2 -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 12 | `python3 -m pytest _framework/tests/test_kit_parity.py::test_ci_gate_verify_sdd_paridade -v` | 1 passed | checagem estrutural, sem sensor aplicável | Sim |
| 13 | `python3 -m pytest _framework/tests/test_ci_gate_verify_sdd.py::test_cli_pr_fixture_duas_sdds -v` | 1 passed | sem mutação manual nesta rodada | Sim |
| 14 | `grep -n "ci_gate_verify_sdd" _framework/rules/workflow-rules.yaml` | linha 1255, seção `gate_scope_verification` | checagem textual | Sim |
| 15 | `python3 _framework/scripts/render_prompts.py --check` | exit 0, todos os alvos "em dia"/"sincronizado" | checagem mecânica de sincronia | Sim |
| 16 | `python3 -c "import yaml; yaml.safe_load(open('_framework/templates/ci/verify-sdd-gate.yml.example'))"` | sem exceção | checagem estrutural | Sim |
| 17 | `grep -n "incident-override\|credencial" docs/guias/gate-ci-verify-sdd.md` | 6 ocorrências | checagem textual | Sim |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0011, ADR-DTF-0004, ADR-DTF-0005 |
