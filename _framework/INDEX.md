# Índice do kit

Gerado por `render_indexes.py` — não edite à mão. Fonte: `rules/kit-index.yaml`.
Total: 109 arquivos

| Caminho (relativo a `_framework/`) | O que é | Quando ler | Tamanho |
|---|---|---|---|
| `AGENTS.md` | Instruções do agente para o próprio kit | Ao editar arquivos dentro de _framework/ | <2 KB |
| `procedures/handover.md` | Procedimento passo a passo de uma skill | Ao executar handover, pickup ou verify-sdd | 2-8 KB |
| `procedures/pickup.md` | Procedimento passo a passo de uma skill | Ao executar handover, pickup ou verify-sdd | 2-8 KB |
| `procedures/verify-sdd.md` | Procedimento passo a passo de uma skill | Ao executar handover, pickup ou verify-sdd | 8-32 KB |
| `prompts/copilot/copilot-instructions.md` | Renderização do núcleo para o Copilot | Ao configurar o Copilot no repositório | 8-32 KB |
| `prompts/cursor/doc-framework.mdc` | Renderização do núcleo para o Cursor | Ao configurar o Cursor no repositório | 8-32 KB |
| `prompts/framework-audit.md` | Prompt de fluxo específico (audit, onboarding) | Ao auditar commits ou onboardar projeto legado | 2-8 KB |
| `prompts/onboarding-bootstrap.md` | Prompt de fluxo específico (audit, onboarding) | Ao auditar commits ou onboardar projeto legado | 2-8 KB |
| `prompts/universal.md` | Prompt universal gerado, colável em qualquer IA | Ao usar uma IA sem AGENTS.md nem skill | 8-32 KB |
| `rules/kit-index.yaml` | Manifesto escrito à mão deste INDEX.md | Ao criar ou remover arquivo do kit | 2-8 KB |
| `rules/workflow-rules.map.md` | Mapa gerado de seções do YAML (ids, linhas) | Antes de ler o YAML: achar a seção certa | 2-8 KB |
| `rules/workflow-rules.yaml` | Fonte canônica das regras do framework | Ao mudar ou consultar regra; leia pelo mapa | >32 KB |
| `scripts/check_commit.py` | Checagem de commit, hooks, cópias ou origem | Ao depurar a checagem correspondente | 2-8 KB |
| `scripts/check_hooks.py` | Checagem de commit, hooks, cópias ou origem | Ao depurar a checagem correspondente | 2-8 KB |
| `scripts/check_renderings.py` | Checagem de commit, hooks, cópias ou origem | Ao depurar a checagem correspondente | 2-8 KB |
| `scripts/check_source_docs.py` | Checagem de commit, hooks, cópias ou origem | Ao depurar a checagem correspondente | 2-8 KB |
| `scripts/ci_gate_verify_sdd.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 8-32 KB |
| `scripts/framework_check.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 2-8 KB |
| `scripts/framework_lib.py` | Biblioteca compartilhada dos scripts | Ao criar ou alterar um script do kit | 8-32 KB |
| `scripts/generate_registry_md.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 2-8 KB |
| `scripts/guard_bash.sh` | Hook que barra comando Bash proibido | Ao depurar bloqueio de comando | <2 KB |
| `scripts/hook_post_edit.py` | Hook de sessão ou pós-edição do Claude Code | Ao depurar um hook | 2-8 KB |
| `scripts/hook_session_start.py` | Hook de sessão ou pós-edição do Claude Code | Ao depurar um hook | 2-8 KB |
| `scripts/lessons_check.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 2-8 KB |
| `scripts/parallel_plan.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 2-8 KB |
| `scripts/registry_tools.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 8-32 KB |
| `scripts/render_indexes.py` | Gerador de índices, mapa e sumários | Ao regenerar INDEX.md, mapa e sumários | 8-32 KB |
| `scripts/render_prompts.py` | Gerador dos adaptadores a partir do YAML | Ao regenerar AGENTS.md, prompts e cópias | >32 KB |
| `scripts/selftest.py` | Script utilitário ou gerador do kit | Ao rodar ou depurar o script | 2-8 KB |
| `scripts/tests/mutations.yaml` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_check_commit.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_check_hooks.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_check_source_docs.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_discover.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_generate_registry_md.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | <2 KB |
| `scripts/tests/test_guard_bash.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | <2 KB |
| `scripts/tests/test_hook_post_edit.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_hook_session_start.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_lessons_check.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_operational_artifacts.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | <2 KB |
| `scripts/tests/test_render_prompts_mechanization.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_render_prompts_sync.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_selftest.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 2-8 KB |
| `scripts/tests/test_validate_state.py` | Teste ou fixture dos scripts do kit | Ao alterar o script correspondente | 8-32 KB |
| `scripts/validate_doc.py` | Validador de documento ou de estado | Ao depurar reprovação de validação | 8-32 KB |
| `scripts/validate_state.py` | Validador de documento ou de estado | Ao depurar reprovação de validação | 8-32 KB |
| `skills/doc-traceability-framework/SKILL.md` | Definição de skill do Claude Code | Ao ajustar comportamento ou gatilho da skill | 2-8 KB |
| `skills/doc-traceability-framework/prompts/framework-audit.md` | Cópia de prompts/ dentro da skill | Nunca à mão; espelha prompts/ | 2-8 KB |
| `skills/doc-traceability-framework/prompts/onboarding-bootstrap.md` | Cópia de prompts/ dentro da skill | Nunca à mão; espelha prompts/ | 2-8 KB |
| `skills/doc-traceability-framework/references/audit.md` | Cópia do workflow-rules.yaml na skill (gerada) | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/references/incidents.md` | Cópia do workflow-rules.yaml na skill (gerada) | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/references/onboarding.md` | Cópia do workflow-rules.yaml na skill (gerada) | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/references/workflow-rules.yaml` | Cópia do workflow-rules.yaml na skill (gerada) | Nunca à mão; regenere com render_prompts.py | >32 KB |
| `skills/doc-traceability-framework/scripts/check_commit.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/check_hooks.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/check_renderings.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/check_source_docs.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/framework_check.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/framework_lib.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/generate_registry_md.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/hook_post_edit.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/hook_session_start.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/lessons_check.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/parallel_plan.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/registry_tools.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/render_indexes.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/render_prompts.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | >32 KB |
| `skills/doc-traceability-framework/scripts/selftest.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/validate_doc.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/validate_state.py` | Cópia byte a byte de scripts/ (gerada) | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/templates/adr.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | <2 KB |
| `skills/doc-traceability-framework/templates/base.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | <2 KB |
| `skills/doc-traceability-framework/templates/inc.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | <2 KB |
| `skills/doc-traceability-framework/templates/pm.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | <2 KB |
| `skills/doc-traceability-framework/templates/prd.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | 2-8 KB |
| `skills/doc-traceability-framework/templates/rfc.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | <2 KB |
| `skills/doc-traceability-framework/templates/sdd.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | 2-8 KB |
| `skills/doc-traceability-framework/templates/spec.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | 2-8 KB |
| `skills/doc-traceability-framework/templates/strategy.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | <2 KB |
| `skills/doc-traceability-framework/templates/tech-spec.template.md` | Cópia de templates/ dentro da skill | Nunca à mão; espelha templates/ | 2-8 KB |
| `skills/handover/SKILL.md` | Definição de skill do Claude Code | Ao ajustar comportamento ou gatilho da skill | <2 KB |
| `skills/pickup/SKILL.md` | Definição de skill do Claude Code | Ao ajustar comportamento ou gatilho da skill | <2 KB |
| `skills/verify-sdd/SKILL.md` | Definição de skill do Claude Code | Ao ajustar comportamento ou gatilho da skill | <2 KB |
| `templates/adr.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | <2 KB |
| `templates/base.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | <2 KB |
| `templates/ci/verify-sdd-gate.yml.example` | Exemplo de workflow de CI | Ao adotar o gate de verificação de SDD no CI | 2-8 KB |
| `templates/inc.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | <2 KB |
| `templates/pm.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | <2 KB |
| `templates/prd.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | 2-8 KB |
| `templates/rfc.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | <2 KB |
| `templates/sdd.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | 2-8 KB |
| `templates/spec.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | 2-8 KB |
| `templates/strategy.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | <2 KB |
| `templates/tech-spec.template.md` | Template de um tipo de documento | Ao criar um documento desse tipo | 2-8 KB |
| `tests/fixtures/sdd_fixture_a.md` | Fixture de teste do kit | Ao alterar o teste que a usa | <2 KB |
| `tests/fixtures/sdd_fixture_b.md` | Fixture de teste do kit | Ao alterar o teste que a usa | <2 KB |
| `tests/fixtures/verify_sdd_pre_reorder.md` | Fixture de teste do kit | Ao alterar o teste que a usa | 8-32 KB |
| `tests/test_ci_gate_verify_sdd.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 8-32 KB |
| `tests/test_gate_texto.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | <2 KB |
| `tests/test_gitattributes_generated.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 2-8 KB |
| `tests/test_kit_parity.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | <2 KB |
| `tests/test_parallel_plan.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 2-8 KB |
| `tests/test_procedures_structure.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 2-8 KB |
| `tests/test_render_indexes.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 8-32 KB |
| `tests/test_repo_hygiene.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | <2 KB |
| `tests/test_skill_md_consistency.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 8-32 KB |
| `tests/test_template_parity.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 2-8 KB |
| `tests/test_validate_doc.py` | Teste do kit (paridade, gates, render) | Ao mudar o comportamento testado | 8-32 KB |
