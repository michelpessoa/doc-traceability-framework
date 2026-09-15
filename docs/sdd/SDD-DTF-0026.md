---
id: SDD-DTF-0026
type: SDD
title: "verify-sdd: sensor de mutação sem git stash compartilhado e diff ancorado em SHA fixo, não em origin/main"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0019, SDD-DTF-0023]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — correção pontual de texto em _framework/procedures/verify-sdd.md, sem mudança de código nem de regra. Ausência de SPEC é o registro de que a fase foi pulada. Implementar em branch sdd/SDD-DTF-0026-* a partir de main, PR, commits com Refs: SDD-DTF-0026."
supersedes: null
superseded_by: null
tags: [procedimento, verify_sdd, gate_scope_verification]
---

# verify-sdd: sensor de mutação sem git stash compartilhado e diff ancorado em SHA fixo, não em origin/main

## Resumo executivo

`docs/sdd/LESSONS.md` (seção "2026-09-14 — Descompassos das verificações
independentes de SDD-DTF-0018 a 0023", itens 6 e 7) registra dois
problemas reais no procedimento `_framework/procedures/verify-sdd.md`.
Item 6: o passo 3 (sensor de discriminação) sugeria `git stash` como
espaço descartável para a mutação temporária — mas o stash é
compartilhado entre worktrees e sessões do mesmo repositório, e em
2026-09-14 havia até 3 verificadores em paralelo (worktrees diferentes)
no mesmo repo, risco real de colisão. Item 7: a verificação de
`SDD-DTF-0023` usou `origin/main` como estado "antes" em blocos
comparativos; depois do merge do PR #67, `origin/main` passou a conter a
própria implementação sendo verificada, e o bloco parou de discriminar
(o "antes" deixou de existir). `sizing: small` — edição de texto em um
único arquivo de procedimento, nenhuma mudança de regra, gate ou
código; ambos os itens já tinham a correção proposta na própria lição.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção pontual de procedimento, nenhum critério do gate
`rfc_to_adr` se aplica (não introduz padrão novo, não é decisão de alto
custo, não há trade-off entre alternativas, não é cross-team, não troca
tecnologia).

## Requisitos consolidados

- **RF1**: O passo 3 ("Sensor de discriminação") de
  `_framework/procedures/verify-sdd.md` não deve oferecer `git stash`
  como opção de espaço descartável para a mutação temporária. Deve
  instruir explicitamente restaurar por cópia do arquivo original (ex.:
  `cp arquivo.py /tmp/backup && ...` seguido de restauração) ou por
  `git checkout -- <arquivo>` rodado dentro da própria worktree, e
  declarar por que `git stash` fica de fora (compartilhado entre
  worktrees/sessões do mesmo repositório).
- **RF2**: O procedimento deve instruir que o `<base>` usado no diff da
  implementação (`git diff <base>..HEAD`) e em qualquer bloco
  comparativo "antes/depois" seja um SHA fixo — o `merge-base` capturado
  no momento da redação (`git merge-base HEAD origin/main`, rodado antes
  de qualquer merge da própria mudança) ou o SHA específico citado na
  SDD/PR — e nunca `origin/main` direto, explicando que é uma ref móvel
  que deixa de representar o "antes" assim que a própria mudança é
  mergeada.
- **RF3**: Nenhum outro texto do procedimento deve seguir sugerindo
  `git stash` como espaço descartável, e nenhum bloco deve continuar
  ancorado em `origin/main` como "antes" fixo.

Casos de borda:
- O `git stash` continua citado no texto apenas como exemplo do que
  **não** fazer (com a justificativa) — não é para sumir a palavra, é
  para sumir a recomendação de uso.

Fora de escopo:
- Reescrever as SDDs já `implemented` (0018–0023) que usaram `origin/main`
  ou `git stash` na verificação histórica — já feito e registrado, sem
  retroatividade.
- Qualquer mudança em `validate_state.py`, `test_discover.py` ou
  `check_hooks.py` (escopo de outras SDDs em paralelo: 0024, 0025, 0027).
- Mudar `workflow-rules.yaml` — não é regra global ainda
  (`lessons_policy` exige repetição em dois projetos).
- Sincronizar `_framework/skills/doc-traceability-framework/` —
  confirmado por `grep` que `_framework/procedures/verify-sdd.md` não
  tem cópia sincronizada por `render_prompts.py` (`sync_copies` só copia
  `*.py` de `scripts/` e `rules/workflow-rules.yaml`; a skill
  `verify-sdd` só aponta para o procedimento por referência de caminho,
  não embute o conteúdo).

## Especificação técnica consolidada

Arquivo único: `_framework/procedures/verify-sdd.md`.

**Seção "Entrada"** — troca o bullet do diff:

```diff
- - O diff da implementação (`git diff <base>..HEAD`).
+ - O diff da implementação (`git diff <base>..HEAD`), onde `<base>` é um
+   SHA fixo — o `merge-base` capturado no momento da redação (`git
+   merge-base HEAD origin/main`, rodado **antes** de qualquer merge da
+   própria mudança) ou o SHA específico citado na SDD/PR. **Nunca
+   `origin/main`** direto: é uma ref móvel, e assim que a mudança sendo
+   verificada é mergeada, `origin/main` passa a contê-la — o "antes" deixa
+   de existir e qualquer bloco comparativo para de discriminar.
```

**Seção "3. Sensor de discriminação"** — troca o passo 1 e o passo 3:

```diff
- 1. Num espaço descartável (`git stash`, cópia, ou worktree — **nunca** um
-    commit), introduza uma falha de comportamento real no código que
-    aquele critério cobre: inverta uma condição, retorne valor fixo, pule
-    uma validação.
+ 1. Num espaço descartável — cópia do arquivo original (ex.: `cp
+    arquivo.py /tmp/backup && ...` ou `git checkout -- <arquivo>` rodado
+    dentro da própria worktree) — **nunca `git stash`** (o stash é
+    compartilhado entre worktrees e sessões do mesmo repositório; com
+    verificadores em paralelo, um `git stash` de uma sessão colide com o
+    de outra) e **nunca** um commit, introduza uma falha de comportamento
+    real no código que aquele critério cobre: inverta uma condição,
+    retorne valor fixo, pule uma validação.
  2. Rode o teste. **Ele tem que falhar.**
- 3. Desfaça a alteração e confirme que o teste volta a passar.
+ 3. Restaure pela cópia guardada (ou `git checkout -- <arquivo>`) e
+    confirme que o teste volta a passar.
```

Nenhum outro arquivo é tocado — confirmado que não há cópia sincronizada
deste procedimento.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1/RF3 — `git stash` não é mais oferecido como opção de uso no passo 3 | `grep -n "stash\`, cópia\|stash, cópia" _framework/procedures/verify-sdd.md` | Sem match, exit 1 (grep não encontra a recomendação antiga) |
| 2 | RF1 — instrução de restauração por cópia/checkout presente | `grep -n "cp arquivo.py /tmp/backup\|git checkout -- <arquivo>" _framework/procedures/verify-sdd.md` | 2+ ocorrências |
| 3 | RF2/RF3 — instrução de SHA fixo (merge-base) presente e `origin/main` citado só como o que evitar | `grep -n "merge-base\|nunca .origin/main" _framework/procedures/verify-sdd.md` | 3+ ocorrências |
| 4 | RF3 — não há cópia sincronizada deste arquivo a atualizar | `python3 _framework/scripts/render_prompts.py --check` | exit 0, sem menção a `verify-sdd.md` como divergente |
| 5 | Regressão geral (self-host) | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` |
| 6 | Suíte de testes do kit intacta | `python3 -m pytest -q` | Todos os testes `passed`, exit 0 |

## Instruções específicas para a IA implementadora

- Editar só `_framework/procedures/verify-sdd.md` — nenhum script Python,
  nenhum arquivo em `_framework/skills/`.
- Não tocar em `validate_state.py`, `test_discover.py` nem
  `check_hooks.py` — escopo de SDDs irmãs (0024, 0025, 0027) em
  paralelo.
- Manter a palavra `git stash` no texto apenas como exemplo do que
  evitar, com a justificativa (compartilhado entre worktrees/sessões) —
  não apagar a menção, trocar a recomendação.
- Branch `sdd/SDD-DTF-0026-verify-sdd-stash-ref-movel` a partir de
  `main`, PR — nunca commit direto (gate seção 14). Commits em
  Conventional Commits com `Refs: SDD-DTF-0026`.
- Conflito esperado em `docs/sdd/registry.yaml` no PR (outras 3 SDDs em
  paralelo tocam o mesmo arquivo) — resolvido pelo humano depois do
  merge, mantendo todas as entradas novas.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima (RF1–RF3) tem texto correspondente
      no procedimento.
- [x] Arquivo tocado: só `_framework/procedures/verify-sdd.md` — qualquer
      outro arquivo além desta SDD e do registry é escopo não registrado
      ou scope creep.
- [x] Nenhuma abstração, config ou refactor extra sem requisito acima.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que redigiu e aplicou a
correção (mudança de texto, sizing small, sem código; risco aceito pelo
sizing — não há lógica a discriminar por sensor de mutação, só presença
de texto).

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `grep -n "stash\`, cópia\|stash, cópia" _framework/procedures/verify-sdd.md` | sem saída, exit 1 | n/a (checagem estática — ausência de string) | Sim |
| 2 | `grep -n "cp arquivo.py /tmp/backup\|git checkout -- <arquivo>" _framework/procedures/verify-sdd.md` | 2 linhas: `51:1. Num espaço descartável — cópia do arquivo original (ex.: \`cp` e `60:3. Restaure pela cópia guardada (ou \`git checkout -- <arquivo>\`) e` | n/a (checagem estática) | Sim |
| 3 | `grep -n "merge-base\|nunca .origin/main" _framework/procedures/verify-sdd.md` | 3 linhas: `21: SHA fixo — o \`merge-base\` capturado...`, `22: merge-base HEAD origin/main\`, rodado...`, `24: \`origin/main\`** direto: é uma ref móvel...` | n/a (checagem estática) | Sim |
| 4 | `python3 _framework/scripts/render_prompts.py --check` | exit 0; todas as cópias listadas como "em dia"/"sincronizado", nenhuma menção a `verify-sdd.md` (confirma que este arquivo não é copiado por `sync_copies`) | n/a (checagem estática) | Sim |
| 5 | `python3 _framework/scripts/framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` (docs/sdd 22 documentos ok; 3 exemplos ok) | Regressão geral, sem sensor dedicado (sem lógica nova) | Sim |
| 6 | `python3 -m pytest -q` | `72 passed in 2.99s`, exit 0 | Regressão geral, sem sensor dedicado (sem lógica nova) | Sim |

Sem sensor de mutação (item "Sensor" da tabela do gate 16): a mudança é
só texto de procedimento consumido por uma IA verificadora em sessão
futura, não há código executável para introduzir falha de comportamento
e observar teste falhando. Critérios 1–4 são checagem estática de
presença/ausência de string, declarada como tal em vez de marcada
"verificado por leitura de código".

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0019 (procedimento original), SDD-DTF-0023 (verificação onde o item 7 ocorreu), `docs/sdd/LESSONS.md` seção "2026-09-14" itens 6 e 7 |
