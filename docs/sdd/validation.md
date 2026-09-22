# Verificação — SDD-DTF-0039

- **Veredito:** PASS (rodada 2)
- **Diff verificado:** 75d0879941fd51a96f085c491dadf658baffb46b..1af0f8d (merge-base capturado com `git merge-base HEAD origin/main`, branch `sdd/SDD-DTF-0039`)
- **Verificador independente:** sim (sessão separada, sem leitura do histórico da sessão que implementou)

## Passo 0 — Fidelidade à origem

### Rodada 1 — FAIL (bloqueante)

| Item | Comando/verificação | Resultado |
|---|---|---|
| 1. Existência/status/url de `source_docs` (mecanizado) | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0039.md /home/michel/doc-traceability-central/docs/DTF` | `❌ 1 problema(s) encontrado(s): SDD-DTF-0039: source_docs 'STRAT-DTF-0003' está com status 'draft' — esperado approved ou implemented.` |
| 2. Todo RF-ID da origem tem requisito correspondente na SDD | leitura manual | STRAT-DTF-0003 não é SPEC (não tem RF-ID formal); o item 10 da tabela de prioridade e a linha E8 da seção "Comparação com o tlc-spec-lean" são cobertos por RF01-RF05 da SDD sem lacuna aparente |
| 3. Nenhum critério relaxado na consolidação | leitura manual | Sem relaxamento identificado — as 7 categorias, a exigência Destino/n/a+motivo e a não-retroatividade por `created` batem com a descrição da STRAT |
| 4. Contrato técnico da Parte 2 igual na SDD | leitura manual | Não aplicável no sentido estrito — STRAT é doc de direção, sem "Parte 2" formal (compatível com sizing `small`, que pula a SPEC); a SDD é quem define o contrato técnico pela primeira vez, o que é o esperado nesse caminho |

**Achado bloqueante (rodada 1):** `STRAT-DTF-0003` (a única entrada de `source_docs` desta SDD) seguia com `status: draft` no registry central, embora a própria STRAT já marcasse os itens 1-9 da sua tabela de prioridade como "Concluído" e o item 10 (origem desta SDD) como "Pendente" — nunca tinha chegado a `approved`. Por regra do passo 0 do `verify-sdd`, exit≠0 ali era bloqueante e impedia considerar a verificação completa, independente do restante.

### Rodada 2 — PASS

Reaberto a pedido do coordenador depois que STRAT-DTF-0003 virou `approved` (front-matter e `registry.yaml` do repositório central, PR michelpessoa/doc-traceability-central#121 — ainda não mergeado, mas o conteúdo em disco no worktree local, que é o que o script lê, já reflete `approved`).

| Item | Comando/verificação | Resultado |
|---|---|---|
| 1. Existência/status/url de `source_docs` (mecanizado) | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0039.md /home/michel/doc-traceability-central/docs/DTF` | `✅ source_docs de SDD-DTF-0039.md conferem com o registry central.` Exit 0. Confirmado em disco: `docs/DTF/registry.yaml:28` (`status: approved`) e front-matter de `docs/DTF/00-strategy/STRAT-DTF-0003.md:4` (`status: approved`), ambos em `/home/michel/doc-traceability-central`. |
| 2-4. | leitura manual | Sem mudança de conteúdo da STRAT além do campo `status` — as conclusões da rodada 1 (itens 2-4) continuam válidas |

**Sem achado bloqueante nesta rodada.** Passo 0 completo e aprovado.

## Passo 1-3 — Conformidade de código e evidência fresca

Rodados nesta sessão (rodada 1, antes de saber do bloqueio do passo 0 — mantidos porque nada no código/testes mudou entre as rodadas):

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| RF01 — seção nova no template | `grep -n "Requisitos transversais (sweep)" _framework/templates/spec.template.md` | `75:## Requisitos transversais (sweep)` | Mutação real do heading → hook `hook_post_edit.py` acusou seção ausente; restaurado, `git diff` vazio | Sim |
| RF02/RF03 — gate mecanizado | `python3 -m pytest _framework/tests/test_validate_doc.py -k sweep -v` | `6 passed` | Mutação de código isolada (cópia fora do repo, `check_sweep_section` forçado a `return []`) → 4/6 testes falharam; restaurado → 4/6 voltaram a passar (as outras 2 dependem de path relativo não reproduzível fora do repo, mas passam na execução real in-repo) | Sim |
| RF04 — `gate_content_quality` cita a seção | `grep -n "Requisitos transversais (sweep)" _framework/rules/workflow-rules.yaml` | linhas 24 e 1181 (2 ocorrências) | Mutação real de uma das linhas → contagem caiu para 1; restaurado → voltou a 2 | Sim |
| RF05 — render_prompts sem divergência | `python3 _framework/scripts/render_prompts.py --check` | Todos os itens `✅`, exit 0 | Mutação real (linha extra só na cópia bundlada de `validate_doc.py`) → `❌ divergente`, exit 1; restaurado → exit 0 | Sim |
| RF05 — cópias do template idênticas | `diff _framework/templates/spec.template.md _framework/skills/doc-traceability-framework/templates/spec.template.md` | sem saída, exit 0 | Mutação real (sufixo só na cópia bundlada) → diff detectou, exit 1; restaurado → exit 0 | Sim |
| Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | `180 passed in 26.44s` | Coberto pelos sensores acima | Sim |

Todos os critérios de código (RF01-RF05 + suíte) passam com evidência fresca e sensor de discriminação real desta sessão. Com a rodada 2 do passo 0 também PASS, a verificação está completa e sem achado bloqueante.

## Descompassos encontrados

- Nenhum ao final da rodada 2. Na rodada 1, `source_docs: STRAT-DTF-0003` estava `draft` no registry central — descompasso de processo (SDD compilada a partir de STRAT ainda não aprovada), resolvido fora desta sessão pela promoção de STRAT-DTF-0003 a `approved` (PR central #121).
- Nenhum arquivo fora de escopo: todos os arquivos do diff (`AGENTS.md`, `CHANGELOG.md`, `QUICKSTART.md`, prompts, `workflow-rules.yaml`, `validate_doc.py` (canônico e bundlado), `spec.template.md` (canônico e bundlado), `test_validate_doc.py`, `docs/especificacao.md`, `docs/sdd/registry.md`/`registry.yaml`) batem com a lista de "Especificação técnica consolidada" da SDD ou são housekeeping esperado de registry. Exceção informativa: `HANDOFF.md` (81 linhas, novo) não está na lista de arquivos tocados da SDD — mas é artefato descartável da skill `handover`, não produto, e o próprio `HANDOFF.md` já registrava a pendência do status da STRAT, então não é scope creep silencioso.

## Lições

- Sizing `small` que pula a SPEC e cita a STRAT diretamente em `source_docs` expôs uma lacuna: nada garantia que a STRAT de origem estivesse `approved` antes de uma SDD ser compilada dela — `check_source_docs.py` pegou isso mecanicamente na rodada 1 (funcionou como desenhado), mas o processo de redação da SDD não tinha esse gate antes de chegar a `approved`. Candidato a red flag em `verify-sdd.md`/checklist de quem redige a SDD: antes de declarar `source_docs` apontando para uma STRAT, confirmar que ela está `approved` (ou promovê-la nesse momento), não só que o item específico está documentado nela.
- STRAT-DTF-0003 tinha 9 de 10 itens da própria tabela marcados "Concluído" mas o documento continuava `draft` até ser promovida fora desta sessão — sugere que o ciclo de vida de STRAT (opcional, mas com `status` formal) não tinha um passo definido de "quando todos os itens fecham, o que acontece com o status da STRAT". Resolvido neste caso pontual; fica como pergunta mais ampla para o humano decidir se vira regra (ex.: `framework_check.py` avisar quando todos os itens de uma STRAT `draft` estiverem "Concluído").
- A rodada 2 confirma que o passo 0 do `verify-sdd` é sensível a mudança de estado fora do próprio repositório sendo verificado (repositório central) — reforça por que o script lê o registry central ao vivo em vez de confiar em cache/memória da sessão anterior.
