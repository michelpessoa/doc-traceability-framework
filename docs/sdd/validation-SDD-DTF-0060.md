# Verificação — SDD-DTF-0060

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

## Descompassos encontrados

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

## Lições

- **Red flag: "não mexa nas cópias geradas" sem conferir se cada cópia tem gerador.** Quando a SDD muda um arquivo canônico, liste as cópias dele (`kit-index.yaml`, `rg -l` pelo nome) e confirme qual script as regenera e qual `--check` as confere. Cópia "gerada" sem gerador fica para trás sem nenhum aviso.
- **Red flag: grep de presença sobre termo que já existia ou que aparece em outro trecho.** Antes de aprovar um critério `grep -q`, rode-o contra a base (`git show <base>:arquivo`) e contra o arquivo sem o trecho novo. Se passar, ancore o padrão no trecho (`coluna \`Projeto\``, a linha da tabela, a seção via `awk`).
- **Red flag: docstring de checker tomada como cobertura.** "check_renderings confere status inexistente" estava escrito, mas o código não fazia isso. Um sensor de um comando desmentiu.
