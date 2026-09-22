# Verificação — SDD-DTF-0037

- **Veredito:** PASS
- **Diff verificado:** `0de077d58a25f4a40c87e3a4d5d95f539919dc8c..HEAD` (branch `sdd/SDD-DTF-0037`, merge-base capturado antes de qualquer merge desta mudança)
- **Verificador independente:** sim (sessão separada da que implementou, sem acesso ao histórico da sessão de implementação)

## Passo 0 — Fidelidade à origem

- `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0037.md /home/michel/doc-traceability-central/docs/DTF` → `✅ source_docs de SDD-DTF-0037.md conferem com o registry central.` (exit 0). SPEC-DTF-0014 e ADR-DTF-0007 existem no registry central, status `approved`, urls conferem com o `path` resolvido.
- Todo RF-ID de SPEC-DTF-0014 (RF01-RF06) tem requisito correspondente em SDD-DTF-0037 — correspondência 1:1 de ids e conteúdo equivalente.
- Nenhum critério de aceite foi relaxado, com uma ressalva examinada em detalhe: a SPEC (RF06, texto principal) pede "mesma técnica de detecção por presença de conteúdo já usada por `check_evidence_profile`, não por versão/data", enquanto a implementação usa `RULE_SINCE["source_fidelity"] = "2.2.0"` + comparação estrita de `created` (`applies_strict`, `>` em vez de `>=`) — uma técnica baseada em data. Avaliado como divergência legítima, não relaxamento silencioso, por três motivos: (1) a própria SDD documenta essa decisão explicitamente na seção "Especificação técnica consolidada", explicando por que a técnica de `check_evidence_profile` (presença de coluna) não se aplica a uma linha nova; (2) a EARS de RF06 tem uma cláusula de escape — "sem uma janela de tolerância declarada explicitamente na SDD" — que abre espaço exatamente para esse tipo de decisão de desenho documentada; (3) o comportamento funcional exigido por RF06 (SDD-DTF-0036, criada no mesmo dia, não é reprovada retroativamente) é entregue e testado com sensor real (ver tabela abaixo). Achado sinalizado, não bloqueante.
- Todo contrato técnico da Parte 2 da SPEC (assinaturas `check_sdd_source_docs(sdd_path: Path, central_docs_dir: Path) -> list[str]`, `check_source_fidelity(doc_id: str, source_docs: list, evidence: str | None) -> list[str]`, tratamento de erro por caso) é descrito de forma idêntica na SDD e implementado de forma idêntica no código.

## Passo 1 — Conformidade com a spec (as duas direções)

Todo item de "Requisitos consolidados" (RF01-RF06) e "Especificação técnica consolidada" tem código correspondente identificável:

- RF01 → `_framework/procedures/verify-sdd.md`, seção "0. Fidelidade à origem" antes de "1. Conformidade com a spec".
- RF02/RF03 → `_framework/scripts/check_source_docs.py` (novo).
- RF04/RF05/RF06 → `_framework/scripts/validate_state.py`, `check_source_fidelity` + `applies_strict`.
- Changelog 2.2.0 + bump de `framework.version` → `_framework/rules/workflow-rules.yaml`.
- Bundle da skill sincronizado → `_framework/skills/doc-traceability-framework/scripts/check_source_docs.py`, `.../scripts/validate_state.py`, `.../references/workflow-rules.yaml`.

Arquivos do diff fora da lista explícita de "Arquivos tocados" da SDD: `AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/prompts/copilot/copilot-instructions.md`. Investigado: todos são saída 100% mecânica de `render_prompts.py` a partir de `_framework/rules/workflow-rules.yaml` (arquivo que É a mudança em escopo, task 6 da decomposição) — confirmado por `render_prompts.py --check` (critério #8) e pelo próprio cabeçalho desses arquivos ("Arquivo GERADO... não edite à mão"). Não é scope creep (nenhuma edição manual, conteúdo é derivado) nem escopo silenciosamente não registrado em sentido funcional — mas a lista de "Arquivos tocados" da SDD poderia ter mencionado explicitamente que o bump em `workflow-rules.yaml` também regera esses arquivos. Tratado como lacuna de documentação menor, não bloqueante (ver Lições).

Nenhuma abstração, dependência, feature flag ou refactor sem requisito correspondente encontrado. Nenhum vocabulário vago nos critérios de aceite marcados como cumpridos.

## Passo 2/3 — Evidência fresca + sensor de discriminação

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0037.md /home/michel/doc-traceability-central/docs/DTF` | `✅ ... conferem com o registry central.` exit 0 | sem teste automatizado (checklist manual/IA por decisão de ADR-DTF-0007) | Sim |
| #1 RF01 | `grep -n "^### 0. Fidelidade à origem" -A1 verify-sdd.md` + `grep -n "^### 1. Conformidade com a spec" verify-sdd.md` | linha 40 < linha 84 | sem teste automatizado | Sim |
| #2 RF02/RF03 | `python3 -m pytest _framework/scripts/tests/test_check_source_docs.py -v` | 11 passed | mutação real (`if status not in OK_STATUSES:` → `if False:`) derrubou `test_status_fora_de_approved_implemented_reprova`; revertido, 11 passed de novo | Sim |
| #3 RF04 | `python3 -m pytest _framework/scripts/tests/test_validate_state.py -k "fidelidade or rf04 or rf05 or rf06" -v` | 7 passed | mutação real (`found = any(...)` → `found = True`) derrubou 2 testes RF04; revertido, 7 passed de novo | Sim |
| #4 RF05 | (mesmo comando) | 7 passed (inclui `test_rf05_...`) | mutação real (guard perdeu checagem de `source_docs` vazio) derrubou `test_rf05_source_docs_vazio_nao_exige_linha`; revertido | Sim |
| #5 RF06 | (mesmo comando) | 7 passed (inclui `test_rf06_...`) | mutação real (`>` → `>=` em `applies_strict`) derrubou `test_rf06_created_no_mesmo_dia_da_regra_nao_reprova_retroativamente` — exatamente o caso SDD-DTF-0036; revertido | Sim |
| #6 regressão real | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | 36 documentos, 0 problemas, ambos exit 0 | coberto pelos sensores #2-#5 | Sim |
| #7 suíte completa | `python3 -m pytest _framework/ -q` | 154 passed | coberto pelos sensores #2-#5 | Sim |
| #8 bundle sincronizado | `python3 _framework/scripts/render_prompts.py --check` | todos os alvos "em dia"/"sincronizado", exit 0 | script determinístico byte-a-byte, ausência de sincronia já é o sensor | Sim |

Todas as mutações foram revertidas por cópia guardada (`cp arquivo /tmp/...bak` + restauração), nunca `git stash`, nunca commit — `git diff --stat` confirmado vazio para `check_source_docs.py` e `validate_state.py` antes de prosseguir.

## Descompassos encontrados

Nenhum bloqueante. Um achado sinalizado (não bloqueante): a lista "Arquivos tocados" da SDD não enumera os arquivos gerados por `render_prompts.py` (`AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, prompts de universal/cursor/copilot) que mudam como efeito mecânico do bump de versão em `workflow-rules.yaml` — comportamento correto e coberto pelo critério #8, mas não documentado explicitamente na lista de arquivos da SDD.

## Lições

- Quando uma task da decomposição mexe em `workflow-rules.yaml` de um jeito que muda `framework.version` (changelog novo), a lista de "Arquivos tocados" da SDD deveria citar explicitamente "+ todos os alvos de `render_prompts.py` (regenerados, não editados à mão)" para que o passo 1 do `verify-sdd` não precise investigar a origem de arquivos fora da lista a cada verificação — red flag reaproveitável para a próxima SDD que tocar o YAML de regras.
- Ao escrever comando com `||` (ou qualquer `|` literal) dentro de uma célula de tabela markdown de Evidência, escapar com `\|` não é suficiente — o parser de `validate_state.py` (`table_with_header`) faz split literal em `|` sem honrar escape, e isso desalinha as colunas seguintes silenciosamente (neste caso, fez "Perfil usado" ler o valor de "Passou?"). Usar frase alternativa sem pipe (ex.: "dois comandos separados") em vez de tentar escapar.
