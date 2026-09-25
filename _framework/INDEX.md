# Índice do kit

Gerado por `render_indexes.py` — não edite à mão. Fonte: `rules/kit-index.yaml`.
Total: 111 arquivos

| Caminho (relativo a `_framework/`) | O que é | Quando ler | Tamanho |
|---|---|---|---|
| `AGENTS.md` | Regras do agente dentro de _framework/: espelho com o kit público e YAML como fonte | Ao editar qualquer arquivo dentro de _framework/ | <2 KB |
| `procedures/handover.md` | Procedimento normativo do handover: como gerar o HANDOFF.md de uma sessão | Ao gerar um HANDOFF.md ou mudar a skill handover | 2-8 KB |
| `procedures/pickup.md` | Procedimento normativo do pickup: retomar trabalho a partir do HANDOFF.md | Ao retomar de um handoff ou mudar a skill pickup | 2-8 KB |
| `procedures/verify-sdd.md` | Procedimento da verificação independente de SDD antes de implemented | Ao verificar uma SDD ou mudar a skill verify-sdd | 8-32 KB |
| `prompts/copilot/copilot-instructions.md` | Renderização do núcleo do framework para o GitHub Copilot | Ao configurar o Copilot num repositório de projeto | 8-32 KB |
| `prompts/cursor/doc-framework.mdc` | Regra do Cursor com o núcleo do framework, sempre ativa | Ao configurar o Cursor num repositório de projeto | 8-32 KB |
| `prompts/framework-audit.md` | Prompt da auditoria periódica de commits e PRs contra o registry | Ao auditar a aderência de um projeto ao framework | 2-8 KB |
| `prompts/onboarding-bootstrap.md` | Prompt do bootstrap de projeto legado: BASE e ADRs reconstruídos | Ao onboardar um projeto com código sem documentos | 2-8 KB |
| `prompts/universal.md` | Prompt universal gerado do YAML, colável em qualquer IA, com sumário | Ao usar o framework numa IA sem AGENTS.md nem skill | 8-32 KB |
| `rules/kit-index.yaml` | Manifesto manual deste INDEX.md e dos resumos de seção do mapa | Ao criar, mover ou remover arquivo do kit | 8-32 KB |
| `rules/workflow-rules.map.md` | Mapa gerado das seções do YAML: id, título, chaves, linhas, bytes e resumo | Antes de ler o YAML, para achar a seção certa | 2-8 KB |
| `rules/workflow-rules.yaml` | Fonte canônica das regras: gates, sizing, tipos, ciclo de status e changelog | Ao mudar ou consultar uma regra; leia pelo mapa | >32 KB |
| `scripts/check_commit.py` | Checa mensagem de commit: Conventional Commits e referência a id do framework | Ao depurar hook commit-msg ou checagem de intervalo | 2-8 KB |
| `scripts/check_hooks.py` | Reprova .claude/settings.json com hook mudo ou mal configurado | Ao editar hooks do Claude Code | 2-8 KB |
| `scripts/check_renderings.py` | Compara os fatos entre YAML, SKILL.md, universal, Cursor e Copilot | Ao mudar uma renderização e ver divergência | 2-8 KB |
| `scripts/check_source_docs.py` | Confere que cada source_docs da SDD existe, usável e no arquivo certo | Ao depurar falha de fidelidade à origem da SDD | 2-8 KB |
| `scripts/ci_gate_verify_sdd.py` | Gate de CI que barra SDD implemented sem validação PASS real | Ao adotar ou depurar o gate de CI do verify-sdd | 8-32 KB |
| `scripts/framework_check.py` | Entrada única dos validadores: registry, conteúdo e estado das SDDs | Ao rodar a validação completa ou configurar o pre-commit | 2-8 KB |
| `scripts/framework_lib.py` | Base comum dos validadores: front-matter, constantes do YAML e caminhos | Ao criar ou alterar um script do kit | 8-32 KB |
| `scripts/generate_registry_md.py` | Gera registry.md a partir do registry.yaml, sem hora, com --check | Ao regenerar ou conferir o registry.md | 2-8 KB |
| `scripts/guard_bash.sh` | Hook PreToolUse que recusa comando Bash destrutivo antes de rodar | Ao depurar bloqueio de comando pelo agente | <2 KB |
| `scripts/hook_post_edit.py` | Hook PostToolUse que valida o documento recém-editado | Ao depurar aviso de gate após editar documento | 2-8 KB |
| `scripts/hook_session_start.py` | Hook SessionStart que injeta instrução de pickup no contexto | Ao depurar o que a sessão recebe ao começar | 2-8 KB |
| `scripts/lessons_check.py` | Conta a recorrência do critério de 2 projetos nas lições locais | Ao decidir se uma lição vira candidata a promoção | 2-8 KB |
| `scripts/parallel_plan.py` | Cruza arquivos tocados das tasks e diz quais rodam em paralelo | Ao planejar a ordem das tasks de uma SDD | 2-8 KB |
| `scripts/registry_tools.py` | CLI do registry: validate, trace por id e audit de commits | Ao validar o registry ou rastrear um documento | 8-32 KB |
| `scripts/render_indexes.py` | Gera INDEX.md do kit, mapa de seções do YAML, INDEX de SDDs e sumários | Ao mudar a forma ou o teto de um índice gerado | 8-32 KB |
| `scripts/render_prompts.py` | Gera AGENTS.md, prompts e cópias da skill a partir do YAML | Ao regenerar os arquivos derivados do YAML | >32 KB |
| `scripts/selftest.py` | Muta os validadores do kit e exige que os testes falhem | Ao checar se os testes dos validadores discriminam | 2-8 KB |
| `scripts/tests/mutations.yaml` | Lista de mutações dos validadores usada pelo selftest.py | Ao adicionar mutação ou depurar mutante sobrevivente | 2-8 KB |
| `scripts/tests/test_check_commit.py` | Testes do check_commit.py sobre repositório git temporário | Ao alterar a checagem de mensagem de commit | 2-8 KB |
| `scripts/tests/test_check_hooks.py` | Testes do check_hooks.py: um caso por regra de hook | Ao alterar a checagem de hooks | 2-8 KB |
| `scripts/tests/test_check_source_docs.py` | Testes do check_source_docs.py sobre origens da SDD | Ao alterar a checagem de source_docs | 2-8 KB |
| `scripts/tests/test_discover.py` | Testes da descoberta de diretórios em framework_check.discover | Ao alterar como o framework_check acha os documentos | 2-8 KB |
| `scripts/tests/test_generate_registry_md.py` | Testes do cabeçalho, da ausência de hora e do --check do registry.md | Ao alterar o generate_registry_md.py | <2 KB |
| `scripts/tests/test_guard_bash.py` | Testes do guard_bash.sh: exit 0 libera, exit 2 bloqueia | Ao alterar o hook de bloqueio de comandos | <2 KB |
| `scripts/tests/test_hook_post_edit.py` | Testes do hook_post_edit.py sobre documentos mínimos | Ao alterar o hook pós-edição | 2-8 KB |
| `scripts/tests/test_hook_session_start.py` | Testes do hook_session_start.py com repositório mínimo | Ao alterar o hook de início de sessão | 2-8 KB |
| `scripts/tests/test_lessons_check.py` | Testes do lessons_check.py: contagem de recorrência de lições | Ao alterar a contagem de lições | 2-8 KB |
| `scripts/tests/test_operational_artifacts.py` | Testes dos artefatos operacionais por glob, como validation-*.md | Ao alterar quais arquivos dispensam front-matter | <2 KB |
| `scripts/tests/test_render_prompts_mechanization.py` | Testes do bloco mechanization gerado pelo render_prompts.py | Ao alterar a mecanização dos gates nas renderizações | 2-8 KB |
| `scripts/tests/test_render_prompts_sync.py` | Testes do sync de templates e da cópia byte a byte da skill | Ao alterar sync_copies ou a paridade do bundle | 2-8 KB |
| `scripts/tests/test_selftest.py` | Testes do selftest.py: mutante morto, sobrevivente e não aplicável | Ao alterar a mutação dos validadores | 2-8 KB |
| `scripts/tests/test_table_cells.py` | Testes do split_table_row para células de tabela markdown | Ao alterar a leitura de células de tabela | <2 KB |
| `scripts/tests/test_validate_state.py` | Testes do validate_state.py sobre o YAML real | Ao alterar o gate de evidência da SDD | 8-32 KB |
| `scripts/validate_doc.py` | Validador do gate de qualidade de conteúdo: placeholders e seções | Ao depurar reprovação de conteúdo de documento | 8-32 KB |
| `scripts/validate_state.py` | Validador do gate de escopo: SDD implemented exige evidência real | Ao depurar reprovação de evidência de uma SDD | 8-32 KB |
| `skills/doc-traceability-framework/SKILL.md` | Skill principal: roteador do fluxo de documentos, sizing e gates | Ao ajustar gatilho ou roteamento da skill principal | 2-8 KB |
| `skills/doc-traceability-framework/prompts/framework-audit.md` | Cópia gerada de prompts/framework-audit.md dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/prompts/onboarding-bootstrap.md` | Cópia gerada de prompts/onboarding-bootstrap.md dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/references/audit.md` | Referência da skill sobre auditoria de commits e PRs contra o registry | Ao pedir auditoria e a skill carregar a referência | <2 KB |
| `skills/doc-traceability-framework/references/incidents.md` | Referência da skill sobre incidente, severidade e postmortem | Ao abrir incidente ou postmortem pela skill | <2 KB |
| `skills/doc-traceability-framework/references/onboarding.md` | Referência da skill sobre onboarding de projeto já existente | Ao onboardar projeto legado pela skill | <2 KB |
| `skills/doc-traceability-framework/references/workflow-rules.yaml` | Cópia gerada de rules/workflow-rules.yaml dentro da skill | Nunca à mão; regenere com render_prompts.py | >32 KB |
| `skills/doc-traceability-framework/scripts/check_commit.py` | Cópia gerada de scripts/check_commit.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/check_hooks.py` | Cópia gerada de scripts/check_hooks.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/check_renderings.py` | Cópia gerada de scripts/check_renderings.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/check_source_docs.py` | Cópia gerada de scripts/check_source_docs.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/ci_gate_verify_sdd.py` | Cópia gerada de scripts/ci_gate_verify_sdd.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/framework_check.py` | Cópia gerada de scripts/framework_check.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/framework_lib.py` | Cópia gerada de scripts/framework_lib.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/generate_registry_md.py` | Cópia gerada de scripts/generate_registry_md.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/hook_post_edit.py` | Cópia gerada de scripts/hook_post_edit.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/hook_session_start.py` | Cópia gerada de scripts/hook_session_start.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/lessons_check.py` | Cópia gerada de scripts/lessons_check.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/parallel_plan.py` | Cópia gerada de scripts/parallel_plan.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/registry_tools.py` | Cópia gerada de scripts/registry_tools.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/render_indexes.py` | Cópia gerada de scripts/render_indexes.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/render_prompts.py` | Cópia gerada de scripts/render_prompts.py dentro da skill | Nunca à mão; regenere com render_prompts.py | >32 KB |
| `skills/doc-traceability-framework/scripts/selftest.py` | Cópia gerada de scripts/selftest.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/scripts/validate_doc.py` | Cópia gerada de scripts/validate_doc.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/scripts/validate_state.py` | Cópia gerada de scripts/validate_state.py dentro da skill | Nunca à mão; regenere com render_prompts.py | 8-32 KB |
| `skills/doc-traceability-framework/templates/adr.template.md` | Cópia gerada de templates/adr.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/templates/base.template.md` | Cópia gerada de templates/base.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/templates/inc.template.md` | Cópia gerada de templates/inc.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/templates/pm.template.md` | Cópia gerada de templates/pm.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/templates/prd.template.md` | Cópia gerada de templates/prd.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/templates/rfc.template.md` | Cópia gerada de templates/rfc.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/templates/sdd.template.md` | Cópia gerada de templates/sdd.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/templates/spec.template.md` | Cópia gerada de templates/spec.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/doc-traceability-framework/templates/strategy.template.md` | Cópia gerada de templates/strategy.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | <2 KB |
| `skills/doc-traceability-framework/templates/tech-spec.template.md` | Cópia gerada de templates/tech-spec.template.md dentro da skill | Nunca à mão; regenere com render_prompts.py | 2-8 KB |
| `skills/handover/SKILL.md` | Skill handover: gatilho e ponte para procedures/handover.md | Ao ajustar quando a skill handover dispara | <2 KB |
| `skills/pickup/SKILL.md` | Skill pickup: gatilho e ponte para procedures/pickup.md | Ao ajustar quando a skill pickup dispara | <2 KB |
| `skills/verify-sdd/SKILL.md` | Skill verify-sdd: gatilho e ponte para procedures/verify-sdd.md | Ao ajustar quando a skill verify-sdd dispara | <2 KB |
| `templates/adr.template.md` | Template de ADR: decisão, alternativas e consequências | Ao criar um ADR | <2 KB |
| `templates/base.template.md` | Template de BASE: baseline do estado atual de projeto legado | Ao fazer o onboarding de projeto legado | <2 KB |
| `templates/ci/verify-sdd-gate.yml.example` | Exemplo de workflow do GitHub Actions para o gate verify-sdd | Ao adotar o gate de CI num repositório de projeto | 2-8 KB |
| `templates/inc.template.md` | Template de INC: incidente com severidade e causa raiz | Ao abrir um incidente | <2 KB |
| `templates/pm.template.md` | Template de PM: postmortem de um incidente com action items | Ao escrever um postmortem | <2 KB |
| `templates/prd.template.md` | Template legado de PRD, mantido para projetos sob 1.x | Ao ler PRD antigo; não usar em trabalho novo | 2-8 KB |
| `templates/rfc.template.md` | Template de RFC: proposta, gate para ADR e sizing | Ao criar uma RFC | <2 KB |
| `templates/sdd.template.md` | Template de SDD: compilada da SPEC, com tasks e critérios de aceite | Ao compilar uma SDD | 2-8 KB |
| `templates/spec.template.md` | Template de SPEC: requisitos em EARS, contratos e estratégia de teste | Ao criar uma SPEC | 2-8 KB |
| `templates/strategy.template.md` | Template de STRAT: direção estratégica opcional | Ao criar um Strategy Doc | <2 KB |
| `templates/tech-spec.template.md` | Template legado de Tech Spec, mantido para projetos sob 1.x | Ao ler TS antigo; não usar em trabalho novo | 2-8 KB |
| `tests/fixtures/sdd_fixture_a.md` | SDD fictícia A que os testes do parallel_plan.py leem | Ao alterar test_parallel_plan.py | <2 KB |
| `tests/fixtures/sdd_fixture_b.md` | SDD fictícia B que os testes do parallel_plan.py leem | Ao alterar test_parallel_plan.py | <2 KB |
| `tests/fixtures/verify_sdd_pre_reorder.md` | Cópia do verify-sdd antes da reordenação, base do teste de estrutura | Ao alterar test_procedures_structure.py | 8-32 KB |
| `tests/test_ci_gate_verify_sdd.py` | Testes do ci_gate_verify_sdd.py: bloqueio de merge sem validação PASS | Ao alterar o gate de CI do verify-sdd | 8-32 KB |
| `tests/test_gate_texto.py` | Regressão do texto do gate de implementação antes do código | Ao editar o texto de gate_implementation_before_code | <2 KB |
| `tests/test_gitattributes_generated.py` | Testes do .gitattributes que marca o bundle gerado | Ao alterar o .gitattributes dos arquivos gerados | 2-8 KB |
| `tests/test_kit_parity.py` | Paridade byte a byte entre scripts originais e cópias da skill | Ao alterar um script copiado para a skill | <2 KB |
| `tests/test_parallel_plan.py` | Testes do parallel_plan.py sobre SDDs fictícias | Ao alterar o cálculo de paralelismo das tasks | 2-8 KB |
| `tests/test_prd_ts_texto.py` | Regressão de PRD e TS como passo do fluxo no texto bruto do YAML | Ao editar o texto do workflow-rules.yaml | 2-8 KB |
| `tests/test_procedures_structure.py` | Testes da estrutura do procedimento verify-sdd.md | Ao reordenar ou editar o verify-sdd.md | 2-8 KB |
| `tests/test_render_indexes.py` | Testes do render_indexes.py: mapa, INDEX do kit, SDDs, tetos e idempotência | Ao alterar qualquer índice gerado | 8-32 KB |
| `tests/test_repo_hygiene.py` | Testes de higiene: caches fora da busca e do versionamento | Ao alterar .gitignore ou .claudeignore | <2 KB |
| `tests/test_skill_md_consistency.py` | Testes de consistência entre SKILL.md e workflow-rules.yaml | Ao alterar o SKILL.md ou a tabela de sizing | 8-32 KB |
| `tests/test_template_parity.py` | Paridade byte a byte dos templates entre original e bundle | Ao alterar um template | 2-8 KB |
| `tests/test_validate_doc.py` | Testes do validate_doc.py: placeholders, seções e front-matter | Ao alterar o gate de qualidade de conteúdo | 8-32 KB |
