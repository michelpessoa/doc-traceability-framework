# Verificação — SDD-DTF-0007

- **Veredito:** PASS
- **Diff verificado:** `ae22aa1~1..ae22aa1` (doc-traceability-framework) / `3e53074~1..3e53074` (doc-traceability-central, mesmo diff — `c118293` é o merge do PR #20)
- **Verificador independente:** sim (sessão separada da que implementou; não leu o histórico da sessão de implementação, só a SDD e o diff)

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `grep -c "build_universal\|build_cursor_mdc\|build_copilot_instructions" _framework/scripts/render_prompts.py` | `6` nos dois repositórios | — | sim |
| 2 | `git diff ae22aa1~1 ae22aa1 -- prompts/universal.md prompts/cursor/doc-framework.mdc prompts/copilot/copilot-instructions.md` (e equivalente em `3e53074`) | Nos 3 arquivos, única linha alterada é o título: `v1.7.0` → `v2.1.0`. Nenhuma outra diferença de conteúdo. | — | sim |
| 3 | Acrescentar linha manual a `prompts/universal.md`; `render_prompts.py --check`; depois `render_prompts.py` (sem `--check`) para regenerar; `--check` de novo | Com edição manual: `❌ universal.md: divergente do gerado` / `exit=1`. Após regenerar (via script, não `git checkout`): `✅ universal.md: em dia.` / `exit=0`; `git status` limpo | Falhou com a condição introduzida, voltou a passar depois — discrimina de verdade | sim |
| 4 | `mv prompts/cursor/doc-framework.mdc prompts/cursor/doc-framework.mdc.bak`; `render_prompts.py --check`; `mv` de volta; `--check` de novo | Ausente: `❌ doc-framework.mdc: ausente — rode render_prompts.py.` / `exit=1`. Restaurado: `✅ doc-framework.mdc: em dia.` / `exit=0` | Falhou com a condição introduzida, voltou a passar depois — discrimina de verdade | sim |
| 5 | `grep -c "^TARGETS = \|^def apply(" _framework/scripts/render_prompts.py` | `0` nos dois repositórios | — | sim |
| 6 | `framework_check.py --auto` e `check_renderings.py`, nos dois repositórios | `framework_check.py --auto`: exit 0 nos dois (únicos avisos são pré-existentes — versão do framework por projeto, e tipos legados PRD/TS no `.mdc`, nada relacionado a este diff). `check_renderings.py`: exit 0 nos dois, "4 renderização(ões) concordam" | — | sim |
| 7 | `diff -r --exclude=__pycache__ doc-traceability-framework/_framework doc-traceability-central/_framework` | sem saída, `exit=0` | — | sim |

Evidência complementar (não é um critério numerado da tabela, mas confirma o 2 de outro ângulo): `render_prompts.py --check` já no estado final do repositório (antes de qualquer sensor) retornou `exit=0` para os 7 alvos de `FULL_TARGETS`, incluindo os 3 novos — confirma que o conteúdo em disco já bate byte a byte com o gerado, sem precisar reescrever nada na verificação.

## Descompassos encontrados

Nenhum. As duas direções de conformidade foram checadas:

- Todo requisito de "Requisitos consolidados" (RF07 e os 3 casos de borda) tem código correspondente identificável em `render_prompts.py` (`FULL_TARGETS` com as 3 novas entradas, `build_universal`/`build_cursor_mdc`/`build_copilot_instructions`, `TARGETS`/`apply()` removidos).
- Todo arquivo do diff (`ae22aa1`: `_framework/scripts/render_prompts.py`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/prompts/copilot/copilot-instructions.md`) aparece listado na seção "Especificação técnica consolidada" / "Arquivos gerados" da SDD. Nenhum arquivo fora da lista.
- `check_renderings.py` não foi tocado (confirmado por `git diff --stat` vazio para esse arquivo), conforme a instrução explícita da SDD de deixá-lo para RF09/etapa 3.
- `build_block(rules)` continua existindo e é chamada pelos 3 novos builders — não foi removida, coerente com a ressalva da SDD ("continua existindo só como chamada interna... se ainda for usada").
- Paridade entre repositórios (RF11) confirmada por diff vazio de `_framework/` inteiro.

## Lições

Nenhum descompasso, mas dois pontos a registrar como reforço do procedimento:

- O sensor dos critérios 3 e 4 desfez a condição introduzida com o próprio mecanismo do sistema (`render_prompts.py` sem `--check` para regenerar; `mv` de volta para restaurar o nome) em vez de `git checkout <arquivo>` — evita o erro documentado de checkout desfazer o HEAD errado nesse fluxo de trabalho, e além disso é o teste mais realista: exercita o caminho de "correção" que o critério 3 já pede (`--check` falha, depois regenerar, depois `--check` passa), não um atalho por fora do sistema.
- O diff dos 3 arquivos entre commits é uma verificação mais forte do critério 2 do que rodar `render_prompts.py --check` no estado final sozinho: o `--check` final só prova que disco e gerado batem *agora*, não que a *migração* não mudou texto visível. Quando o critério de aceite for sobre "não mudar algo na transição", o comando certo é diff entre commits, não apenas o estado atual — vale generalizar para futuras SDDs de migração de geração.
