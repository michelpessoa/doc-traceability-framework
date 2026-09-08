# Verificação — SDD-DTF-0017

- **Veredito:** PASS
- **Diff verificado:** `dec1b9f` (docs(dtf): QUICKSTART e guia não-técnico cobrem os 4 níveis de sizing), mergeado em `c0db014` (PR #49); mais `a0b9f11` (correção de status `draft` → `approved`, sem mudança de conteúdo), mergeado em `23ab566` (PR #50) — ambos já em `main`.
- **Verificador independente:** sim — sessão separada, sem ter lido o histórico da sessão implementadora; entrada foi só a SDD (`docs/sdd/SDD-DTF-0017.md`) e o diff dos 2 commits acima, localizados via `git log --all --grep="SDD-DTF-0017"`.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1. RF1 — QUICKSTART.md menciona large/complex | `grep -A3 "small.*só a SDD" QUICKSTART.md` | Linhas citam `large`/`complex`, RFC/ADR e apontam pra `docs/guias/guia-tecnico.md` | Ver nota abaixo — grep isolado não discrimina (o padrão de match é a linha de introdução, não o conteúdo novo); sensor real aplicado sobre a cadeia de geração: revertida a edição em `build_quickstart()` (`_framework/scripts/render_prompts.py`), rodado `python3 _framework/scripts/render_prompts.py` (sem `--check`) pra regenerar — o `QUICKSTART.md` resultante voltou a **não** citar `large`/`complex`/RFC/ADR (confirmado por leitura do mesmo `grep -A3`). Desfeito (`git checkout`) o `render_prompts.py` do kit **e** a cópia sincronizada em `_framework/skills/doc-traceability-framework/scripts/render_prompts.py` (o regen tinha sincronizado a cópia com o texto quebrado) — `render_prompts.py --check` voltou a `✅ QUICKSTART.md: em dia.` em todas as 17 checagens, `git status --porcelain` limpo | Sim |
| 2. RF1 — arquivo gerado bate com a função | `python3 _framework/scripts/render_prompts.py --check` | `exit 0`, 17 linhas `✅ .../em dia`/`sincronizado` | trivial (idempotência do sync); não discrimina conteúdo, só consistência gerador↔gerado — coberto pelo sensor do critério 1 | Sim |
| 3. RF2 — guia não-técnico separa large/complex | `grep -c "Muito grande" docs/guias/guia-nao-tecnico.md` | `1` | Sim — removido temporariamente (edição descartável, não commitada) o bullet novo "Muito grande" de `docs/guias/guia-nao-tecnico.md`; `grep -c` caiu para `0` (exit 1). `git checkout -- docs/guias/guia-nao-tecnico.md` desfez a edição; `grep -c` voltou a `1`, `git status --porcelain` limpo | Sim |
| 4. Regressão geral | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` (4 diretórios: `docs/sdd` deste repo — 17 docs ok —, `examples/central/EXEMPLO`, `examples/central/LEGADO`, `examples/project-repo-checkout/docs/sdd`) | sem sensor dedicado — regressão geral, não lógica nova desta SDD | Sim |

Checagem mecânica complementar: `python3 _framework/scripts/validate_state.py docs/sdd` → `✅ 17 documento(s) verificados: nenhuma SDD 'implemented' sem evidência.`

## Conformidade requisito → código (e inverso)

RF1 (`QUICKSTART.md` menciona `large`/`complex` → RFC/ADR, com referência a `guia-tecnico.md`) e RF2 (`guia-nao-tecnico.md` separa "Grande" de "Muito grande" com o mesmo critério de `guia-tecnico.md`) têm conteúdo correspondente confirmado por leitura de diff (`git show dec1b9f`): a edição em `build_quickstart()` (item 2 da lista "Primeiro trabalho") bate literalmente com o texto pedido na "Especificação técnica consolidada" da SDD, assim como o bullet "Muito grande" adicionado em `guia-nao-tecnico.md`.

Direção inversa (arquivo no diff sem requisito): os arquivos tocados pelo commit `dec1b9f` são `QUICKSTART.md` (gerado, RF1), `_framework/scripts/render_prompts.py` (RF1) e sua cópia sincronizada em `_framework/skills/doc-traceability-framework/scripts/render_prompts.py` (mecanismo de sync já existente, não código novo), `docs/guias/guia-nao-tecnico.md` (RF2), mais `docs/sdd/SDD-DTF-0017.md`, `docs/sdd/registry.md` e `docs/sdd/registry.yaml` (bookkeeping da própria SDD). Nenhum arquivo fora dessa lista. `README.md`, `guia-tecnico.md` e `docs/especificacao.md` — declarados fora de escopo na SDD — não aparecem no diff. Nenhuma abstração, dependência, feature flag ou refactor sem requisito correspondente.

O passo 5 do plano de implementação (sync `_framework/` e `docs/guias/` para a cópia em `doc-traceability-central`, em PR separado) está fora do escopo verificável neste repositório — pertence ao repositório central, não a este. Não verificado aqui; ver nota em "Descompassos encontrados".

## Descompassos encontrados

Nenhum descompasso de requisito↔código, arquivo fora de escopo ou abstração extra neste repositório (kit).

Ressalva de processo: a SDD (`Riscos operacionais`, `Plano de rollout`, `Instruções específicas para a IA implementadora`) condiciona `implemented` à conclusão do passo 5 — sync para `doc-traceability-central` — mas esse passo acontece em outro repositório e não foi verificado nesta sessão (esta verificação rodou só em `/home/michel/doc-traceability-framework`). Não é um descompasso de código; é uma dependência externa ao escopo desta verificação, que o humano precisa confirmar separadamente antes ou depois de marcar `implemented` aqui.

## Lições

Nenhuma lição nova — nenhum red flag reaproveitável surgiu desta verificação. O critério 1 expôs que o `grep -A3` declarado como "Comando de verificação" na tabela de critérios de aceite da SDD não é, por si só, um sensor de discriminação (ele sempre casa a linha de introdução, independente do conteúdo novo estar presente); a discriminação real só apareceu ao reverter a cadeia de geração (`build_quickstart()` → regen → `QUICKSTART.md`) e comparar visualmente. Isso já está coberto pela orientação existente do procedimento normativo ("Se não houver teste automatizado para um critério, diga isso explicitamente em vez de marcar o critério como verificado por leitura de código") — não é gap novo, só aplicação de uma regra já existente.

## Recomendação de status

**PASS.** Todos os 4 critérios de aceite rodados nesta sessão com saída real; critérios 1 e 3 têm sensor de discriminação confirmado (falha injetada faz a checagem cair; revertida, volta a passar); critério 2 é estrutural (idempotência) e critério 4 é regressão geral, sem sensor dedicado, ambos consistentes com o procedimento. Nenhum requisito órfão, nenhum arquivo fora de escopo, nenhuma abstração extra. Autoriza avançar `SDD-DTF-0017` para `implemented` neste repositório (kit), com a ressalva registrada acima sobre o passo 5 (sync central) não coberto por esta verificação.
