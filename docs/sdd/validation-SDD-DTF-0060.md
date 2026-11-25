# Verificação — SDD-DTF-0060

Duas rodadas. A rodada 2 vem primeiro; a rodada 1 segue abaixo sem alteração de conteúdo (só os títulos desceram um nível).

## Rodada 2

- **Veredito:** PASS
- **Diff verificado:** `7d9e858..d9ea3a4` no kit (`7d9e858` = `git merge-base HEAD origin/main`, SHA fixo; é o merge da PR #153 trazido à branch pelo merge `aa9dba2`, então o intervalo só contém commits desta SDD: `6e00a08`/`462ef1e` (SDD e status), `0618b27` (rodada 1), `f46557d` (validação da rodada 1), `d0b842c` (emenda RF10), `8ab9bc2` (gerado), `d9ea3a4` (rodada 2)); espelho no central em `065e53a` (branch `espelho/SDD-DTF-0059-0060`)
- **Rodada:** 2 (teto 3)
- **Verificador independente:** sim (subagente separado; não implementou, não fez a rodada 1 e não leu o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão. Sensores em cópias descartáveis (`/tmp/sensor-0060-r2` via `git archive HEAD`, `/tmp/sensor-0060-r2-base` via `git archive 7d9e858`, `/tmp/sensor-0060-r2-git` via `git clone`, `/tmp/sensor-0060-r2-central` com cópias dos seis arquivos do central, `/tmp/sensor-0060-r2-central-full` com cópia inteira do central), sem `git stash` e sem commit. O checkout do central não foi alterado (`git status --short` vazio antes e depois; HEAD `065e53a`).

A emenda RF10 foi conferida: a review `6057468337` da PR #154 é de `michelpessoa`, `COMMENTED`, corpo `Aprovado`, `commit_id` `aa9dba2c33d968c85afc5e16b8b550ce936c9d78`.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing `small`, `source_docs: []`, sem SPEC) | SDD lida inteira, com "Emendas"; RF01 a RF10 escritos na própria SDD | n/a | Sim |
| A01 | comando literal da SDD (linha 122) | `79:## Aprovação`; nenhum `falta` | SKILL.md de `7d9e858`: 5 `falta`, sem título. Cada termo trocado: `falta <termo>`. Só o título trocado: saída vazia. Restaurado: normal | Sim |
| A02 | comando literal da SDD (linha 123) | nenhum `falta` | SKILL.md de `7d9e858`: `falta enxuta`, `falta executor_contract` (sem `falta Projeto`: termo pré-existente). Cada termo trocado: `falta <termo>`. Restaurado: nenhum | Sim |
| A03 | comando literal da SDD (linha 124) | nenhum `falta` | Prompt de `7d9e858`: 4 `falta`. Cada termo trocado: `falta <termo>`. Restaurado: nenhum | Sim |
| A04 | comando literal da SDD (linha 125) | nenhum `falta` | Prompt de `7d9e858`: 2 `falta`. Cada termo trocado: `falta <termo>`. Restaurado: nenhum | Sim |
| A05 | comando literal da SDD (linha 126) | `2` | Título de cada prompt revertido: `1`. Prompts de `7d9e858`: `0`. Restaurado: `2` | Sim |
| A06 | leitura lado a lado de `git diff 7d9e858..d9ea3a4` dos três arquivos e de `git diff aa9dba2..d9ea3a4` do SKILL.md, com `approval_policy`, `frontmatter_schema.common_fields.approved_by`, `executor_contract` (`reads`, `machine_outputs`, `writes`), `registry.central_registry` (`repository_field` e seus `states`, `approvers_field`), `audit.precondition`, `document_types.SPEC.rf_optional_columns`, changelog 2.7.0; `review_approval.py:9,143-145`; `validate_doc.py:459` | Nenhuma afirmação sem chave ou que a contradiga. Os dois ajustes de texto da rodada 1 estão resolvidos (ver abaixo) | sem teste automatizado (leitura) | Sim |
| A07 | comando literal da SDD (linha 128) | `check_renderings` `exit=0` (`5 renderização(ões) concordam`); `render_prompts --check` `exit=0`; `526 passed`; `framework_check --auto` `exit=0`; `git diff --name-only origin/main`: 11 arquivos, exatamente os previstos; `origin/main` = `7d9e858`, mesmo resultado com o SHA fixo | INDEX.md com `2-8 KB` na linha do SKILL.md: `❌ _framework/INDEX.md: divergente do gerado`, `exit=1`. Iron Law `gate_branch_before_commit` alterada no SKILL.md: `exit=1`. Registry com status da SDD-0060 trocado para `draft`: `status diverge`, `exit=1`. Arquivo extra (`_framework/templates/extra.md`) aparece no `git diff --name-only 7d9e858`. Restaurados: `exit=0`. Cópia de prompt da skill mutada: `render_prompts --check` segue `exit=0` (não cobre RF10; o A09 cobre) | Sim |
| A08 | no central: `cmp` dos seis arquivos (SKILL.md, os dois prompts, as duas cópias da skill, `_framework/INDEX.md`) contra o kit; `framework_check.py --auto` | `cmp` sem saída e exit 0 nos seis; `✅ 134 documento(s) ok.` `✅ Todas as verificações do framework passaram.` `exit=0`. Extra: `diff -rq` de `_framework/` inteiro, kit x central: sem saída | Cópia `framework-audit.md` da skill mutada: `differ: char 1465, line 31`. SKILL.md e cópia `onboarding-bootstrap.md` de `e824ebb` (espelho da rodada 1): `differ: char 2746, line 49` e `differ: char 70, line 1`. Cópia inteira do central com um status trocado em `docs/ABSTRACTCLINIC/registry.yaml`: `framework_check` `exit=1`; restaurado `exit=0`. Restaurado: `cmp` sem saída | Sim |
| A09 | comando literal da SDD (linha 130) | sem saída de `cmp`, `exit=0`; cada `cmp` isolado também exit 0 | Cópia `onboarding-bootstrap.md` mutada: `differ: char 659, line 11`, porém `exit=0` (ver descompasso 2). Cópia `framework-audit.md` com uma linha a mais: `EOF on _framework/prompts/framework-audit.md after byte 5254`, `exit=1`. Cópias de `7d9e858` (v1.3.0): `differ` nas duas, `exit=1`. Restaurado: sem saída, `exit=0` | Sim |

### A06, os dois ajustes da rodada 1

- **Item Executor x `executor_contract.writes`.** `SKILL.md:107` agora diz "o que escreve: no central por PR, nunca em main; no registry de projeto, `entrega` e `path` da SDD entregue; `approved_by` com `kind: policy` só onde `approval_policy` permite". Os sete itens de `writes` (`workflow-rules.yaml:1682-1688`) cabem nessas três partes: rascunhos, LESSONS.md, PR de documento novo e `approved_by` humano na PR são escritas no central por PR; "Campo entrega e path de SDD entregue no registry de projeto" e "Campo approved_by com kind: policy só onde approval_policy permite" estão citados quase literalmente. O item não diz mais que toda escrita é no central. Resolvido.
- **"sob 2.7.0 ou maior".** `SKILL.md:49` e `:105` dizem "sob 2.7.0 ou maior". Bate com `validate_doc.py:459` ("projeto sob 2.7.0 ou maior") e com a regra `sdd_lean` (`validate_doc.py:63`). Resolvido.

Demais afirmações conferidas: seção "Aprovação" (`SKILL.md:79-90`) bate com `approval_policy` (`default_approver: human`, regras na ordem, SPEC `medium`/`large`/`complex` humano, SDD `policy` com `checks`, `hash_excluded_sections`), com `frontmatter_schema.common_fields.approved_by` (campos, `evidence` obrigatório com `human`, cobrança desde a 2.5.0 não-retroativa, `transitions` só com `policy`) e com `approvers_field`. "Só contam logins de `approvers`" é a regra de `review_approval.py:9`, que sai com erro sem a lista (`:143-145`). Prompts: `repository_status: active`/`none_yet` batem com `repository_field.states`; a parada da auditoria em `none_yet` bate com `audit.precondition`; o bloco de `approved_by` repete os campos do schema e a regra de `review_approval.py` sobre o head.

### Descompassos encontrados

Requisito ↔ texto: RF01 `SKILL.md:79-90` (depois de "Ciclo de vida de status", `:69`); RF02 `:49-53` e `:105`; RF03 `:106-107`; RF04 `:120`; RF05 `onboarding-bootstrap.md:10-12` e `:33-42`; RF06 `:87-93` e `:109-111`; RF07 `framework-audit.md:31-34`; RF08 `:107-113`; RF09 linha 1 dos dois prompts; RF10 as duas cópias de `skills/doc-traceability-framework/prompts/`, byte a byte iguais às canônicas, no kit e no central. Nenhum requisito sem texto.

Arquivo tocado ↔ SDD: os 11 arquivos de `git diff --name-only 7d9e858..d9ea3a4` estão todos previstos (tasks 1, 2, 3, 4 e 4b, a SDD, a validação e os três gerados de `docs/sdd/`, lista do A07). Nada mudou em `rules/`, `scripts/`, `templates/`, `references/`, outras skills, prompts gerados ou guias. Não há código sem requisito.

1. **Resolvido (era o bloqueante da rodada 1).** As cópias dos prompts na skill estão idênticas às canônicas (RF10, A09) e espelhadas no central (A08).
2. **Não bloqueante (critério fraco, A09).** O `echo "exit=$?"` depois do laço só reflete o último `cmp`: com só a cópia de `onboarding-bootstrap.md` divergente, o comando imprime `differ` e `exit=0`. O critério discrimina pela outra metade do resultado esperado ("sem saída de `cmp`"), então não há falso verde, mas o `exit=0` sozinho não prova as duas cópias. Uma SDD futura pode usar `cmp a b && cmp c d; echo "exit=$?"` ou acumular o status.
3. **Não bloqueante (critério fraco, A01/A02, já registrado na rodada 1).** Os greps olham o arquivo inteiro: `Projeto` existia antes, e os termos do A01 não estão presos à seção. Conferido por leitura e por `awk` restrito à seção `## Aprovação` (os cinco termos e `content_sha256` estão dentro).
4. **Pré-existente, fora desta SDD (já registrado na rodada 1).** `render_prompts.py --check` não sincroniza nem confere `skills/doc-traceability-framework/prompts/*.md`, embora `_framework/INDEX.md` diga "regenere com render_prompts.py": cópia mutada passa com `exit=0`. A SDD deixa a mudança no gerador para uma SDD própria ("Fora de escopo"); até lá, o A09 é a única guarda.
5. **Observação.** A seção "Especificação técnica consolidada", item "Espelho no central", ainda fala em "os três arquivos e `_framework/INDEX.md`", sem as duas cópias do RF10; a task 5 e o A08 as incluem, e o espelho está completo. Sem efeito no veredito.

### Lições

- **Red flag: `echo "exit=$?"` depois de um laço.** O `$?` é só do último comando. Para conferir várias cópias, encadeie com `&&` ou acumule o status; senão a evidência "exit=0" vale por uma cópia só.
- **Red flag: emenda que amplia critérios sem revisar todas as seções que listam o escopo.** A emenda atualizou tasks, A07 e A08, mas não o item "Espelho no central" da especificação. Ao emendar, procure na SDD toda menção à lista antiga (`rg "três arquivos"`).

## Rodada 1

- **Veredito:** FAIL
- **Diff verificado:** `6233635..0618b27` no kit (`6233635` = `git merge-base HEAD origin/main`, igual a `origin/main` no momento da verificação; implementação em `0618b27`, os commits `6e00a08`/`462ef1e` anteriores são só a SDD e o status); espelho no central em `e824ebb` (branch `espelho/SDD-DTF-0059-0060`)
- **Rodada:** 1
- **Verificador independente:** sim (subagente separado; não leu o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão. Sensores em cópias descartáveis (`/tmp/sensor-0060` via `git archive HEAD`, `/tmp/sensor-0060-git` via `git clone`, `/tmp/sensor-0060-central` com cópias dos quatro arquivos do central), sem `git stash` e sem commit. O checkout do central não foi alterado (`git status --short` vazio antes e depois).

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing `small`, `source_docs: []`, sem SPEC) | SDD lida inteira; RF01 a RF09 escritos na própria SDD | n/a | Sim |
| A01 | comando literal da SDD (linha 102) | `79:## Aprovação`; nenhum `falta` | Seção 79-90 removida: sem linha de título, `falta approval_hash.py`, `falta approvers`. Só o título removido: saída vazia (sem a linha de título). Cada termo apagado: `falta <termo>`. SKILL.md de `6233635`: 5 `falta`. Restaurado: volta ao normal | Sim |
| A02 | comando literal da SDD (linha 103) | nenhum `falta` | Apagar linhas com `enxuta`, `Projeto` ou `executor_contract`: `falta <termo>`. **Não discrimina**: com a menção nova da coluna `Projeto` (SKILL.md:52) trocada, passa (pré-existente `**Projeto**` em SKILL.md:15); com a linha de RF04 (SKILL.md:120) removida, passa (item de RF03 em SKILL.md:107). RF02 e RF04 confirmados por leitura | Sim |
| A03 | comando literal da SDD (linha 104) | nenhum `falta` | Cada termo apagado: `falta <termo>`; prompt de `6233635`: 4 `falta`; restaurado: nenhum | Sim |
| A04 | comando literal da SDD (linha 105) | nenhum `falta` | Cada termo apagado: `falta <termo>`; prompt de `6233635`: 2 `falta`; restaurado: nenhum | Sim |
| A05 | comando literal da SDD (linha 106) | `2` | Título de cada prompt revertido: `1`; texto movido para a linha 2: `1`; restaurado: `2` | Sim |
| A06 | leitura lado a lado do diff dos três arquivos e de `approval_policy`, `frontmatter_schema.approved_by`, `executor_contract`, `registry.central_registry` (`repository_field`, `approvers_field`), `audit.precondition`, `multi_project`, `document_types.SPEC.rf_optional_columns`, changelog 2.6.0/2.7.0, docstring de `review_approval.py` | Nenhuma afirmação contradiz a chave citada; duas imprecisões não bloqueantes (descompassos 3 e 4) | sem teste automatizado (leitura) | Sim |
| A07 | comando literal da SDD (linha 108) | `check_renderings` `exit=0`; `render_prompts --check` `exit=0`; `526 passed`; `framework_check --auto` `exit=0`; `git diff --name-only origin/main`: os 8 arquivos previstos | INDEX.md com `2-8 KB`: `❌ _framework/INDEX.md: divergente`, `exit=1`. Iron Law alterada no SKILL.md: `exit=1`. Registry da SDD-0060 com status divergente: `exit=1`. Arquivo extra (`sdd.template.md`) aparece no `git diff --name-only`. Restaurados: `exit=0`. Status inexistente (`obsolete`) no SKILL.md **não** derruba `check_renderings` (descompasso 5, pré-existente) | Sim |
| A08 | no central: `cmp` dos quatro arquivos contra o kit; `framework_check.py --auto` | `cmp` sem saída (exit 0 nos quatro); `✅ Todas as verificações do framework passaram.` `exit=0` | Título revertido na cópia: `differ: char 44, line 1`; SKILL.md do `dfa82db` do central: `differ: char 2726, line 49`; restaurado: sem saída | Sim |

### Descompassos encontrados

1. **Bloqueante (causa: especificação). Cópias bundladas dos prompts dentro da skill ficaram para trás.** `_framework/skills/doc-traceability-framework/prompts/onboarding-bootstrap.md` e `.../prompts/framework-audit.md` eram idênticas ao canônico em `6233635` (`cmp` sem saída; última mudança das quatro em `419ff7b`, SDD-DTF-0033). Depois de `0618b27` divergem: seguem `(v1.3.0)`, sem `repository_status`, `none_yet`, `approved_by` nem `review_approval.py`. A divergência nasce deste diff. Três fatos fazem dela parte do problema desta SDD, e não só uma lacuna antiga:
   - a própria skill manda o agente para a cópia: `references/onboarding.md:4-5` ("use `prompts/onboarding-bootstrap.md`, que está bundlado nesta skill") e `references/audit.md:6`. Um agente que segue a skill instalada lê os prompts antigos, que é a lacuna que o Resumo executivo diz fechar (RF05 a RF09);
   - `_framework/rules/kit-index.yaml:203-205` e `_framework/INDEX.md` declaram essas cópias como "Cópia gerada de prompts/{name} dentro da skill; regenere com render_prompts.py";
   - `render_prompts.py --check` passa porque `sync_copies` (`render_prompts.py:734-757`) só cobre scripts, o YAML e os templates.

   A SDD pôs fora de escopo "as cópias geradas dentro da skill (`references/`, `scripts/`, `templates/`)": a lista não inclui `prompts/`, e as instruções mandam "não mudar as cópias geradas". A implementação seguiu a letra, e a SDD não previu a cópia de `prompts/`, que não tem gerador. O espelho do central (`e824ebb`) tem a mesma divergência.
   **Parte pré-existente, para outra SDD:** `render_prompts.py` não sincroniza nem confere `skills/.../prompts/*.md`, embora o kit-index diga que sim. Esse gerador ausente existe desde SDD-DTF-0033 e é mudança de script.
   **Caminhos para o humano decidir:** (a) emendar a SDD para incluir a cópia dos dois prompts em `skills/doc-traceability-framework/prompts/` no kit e no central, com um critério `cmp` canônico x cópia, e abrir outra SDD para levar essa cópia ao `sync_copies`; ou (b) manter o escopo, declarar em "Fora de escopo" que a cópia bundlada fica desatualizada até a SDD do gerador e registrar essa SDD. A escolha é do humano.

2. **Não bloqueante (critério fraco).** O A02 não discrimina duas das três partes. `Projeto` já existia em SKILL.md:15, e `executor_contract` aparece também no item de RF03, então a linha de RF04 em "Leia sob demanda" pode sumir sem que o critério falhe. O A01 confere os termos no arquivo inteiro, não dentro da seção: `approval_policy`, `approved_by` e `review_approval.py` passam sem ela. Com o título ausente, o A01 imprime nada em vez de uma mensagem. Os requisitos foram confirmados por leitura e por checagem restrita à seção (`awk '/^## Aprovação$/…'`: todos os termos dentro, mais `content_sha256`).

3. **Não bloqueante (A06, imprecisão).** O item Executor (SKILL.md:107) resume `executor_contract.writes` como "o que escreve no central, sempre por PR, nunca em main". O contrato também inclui escrita no registry de projeto (`entrega`, `path`) e `approved_by` com `kind: policy`, sem menção a PR. Para o central a afirmação vale, mas o resumo sugere que toda escrita é no central.

4. **Não bloqueante (A06, redação).** "Em projeto sob 2.7.0" (SKILL.md:49) segue a redação do changelog 2.7.0, mas pode ser lido como "só na 2.7.0". Os prompts usam "2.5.0 ou maior". Projeto sob 2.8.0 também usa a SDD enxuta.

5. **Pré-existente, fora desta SDD.** `check_renderings.py` promete na docstring (item 4) reprovar "tipo ou status que não existe no YAML", mas o código não confere status: `obsolete` inserido no SKILL.md passou com `exit=0`. A "Especificação técnica consolidada" desta SDD repete essa promessa. O A07 continua discriminando por Iron Law, tipo e INDEX.

6. **Observação.** O A07 usa `git diff --name-only origin/main`, uma ref móvel. Aqui `origin/main` = merge-base `6233635`, então o resultado equivale ao da base fixa, conferido também num clone descartável com `git diff --name-only 6233635`.

Arquivo do diff ↔ SDD: os oito arquivos estão previstos (três de produto nas tasks 1-3, `_framework/INDEX.md` na task 4, a SDD e os gerados de `docs/sdd/` no A07). Requisito ↔ texto: RF01 SKILL.md:79-89 (depois de "Ciclo de vida de status", linha 69); RF02 SKILL.md:49-53 e 105; RF03 SKILL.md:106-107; RF04 SKILL.md:120; RF05 onboarding:10-12 e 36-42; RF06 onboarding:87-93 e 109-111; RF07 audit:31-34; RF08 audit:107-113; RF09 linha 1 de cada prompt. Nada mudou em regra, script, template, cópia gerada, outra skill ou guia. Não há código sem requisito.

### Lições

- **Red flag: "não mexa nas cópias geradas" sem conferir se cada cópia tem gerador.** Quando a SDD muda um arquivo canônico, liste as cópias dele (`kit-index.yaml`, `rg -l` pelo nome) e confirme qual script as regenera e qual `--check` as confere. Cópia "gerada" sem gerador fica para trás sem nenhum aviso.
- **Red flag: grep de presença sobre termo que já existia ou que aparece em outro trecho.** Antes de aprovar um critério `grep -q`, rode-o contra a base (`git show <base>:arquivo`) e contra o arquivo sem o trecho novo. Se passar, ancore o padrão no trecho (`coluna \`Projeto\``, a linha da tabela, a seção via `awk`).
- **Red flag: docstring de checker tomada como cobertura.** "check_renderings confere status inexistente" estava escrito, mas o código não fazia isso. Um sensor de um comando desmentiu.
