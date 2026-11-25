---
id: SDD-DTF-0060
type: SDD
title: "Skill do framework e prompts de onboarding e auditoria cobrem a aprovação como dado, o executor, a SDD enxuta e o greenfield"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0040, SDD-DTF-0053, SDD-DTF-0054, SDD-DTF-0055, SDD-DTF-0057, SDD-DTF-0058]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção de documentação pedida pelo owner em 2026-11-25, sem mudança de regra, script ou template; ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0040). Três arquivos de produto, todos escritos à mão. A fonte de cada afirmação nova é a chave de workflow-rules.yaml citada no RF, nunca memória. A skill é roteador: aponta a chave do YAML, não copia a regra. check_renderings.py lê o SKILL.md e tem de continuar passando. O _framework/INDEX.md é gerado por render_prompts.py. A SDD-DTF-0059 cobre os guias, em branch própria. O central espelha os três arquivos em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [skill, prompts, onboarding, audit, documentacao, drift, aprovacao, executor, greenfield]
---

# Skill do framework e prompts de onboarding e auditoria cobrem a aprovação como dado, o executor, a SDD enxuta e o greenfield

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`_framework/skills/doc-traceability-framework/SKILL.md` é o roteador que os
agentes seguem, e não muda desde setembro: não cita `approval_policy`,
`approved_by`, `approval_hash.py`, `review_approval.py`, `approvers`,
`executor_contract` nem a SDD enxuta (2.4.0 a 2.8.0). Um agente que segue a
skill não sabe que a SPEC `medium` aprovada precisa de `approved_by` humano
com evidência da review, nem que a SDD compilada pode ser aprovada por
política. `_framework/prompts/onboarding-bootstrap.md` e
`_framework/prompts/framework-audit.md` ainda se apresentam como v1.3.0,
não tratam `repository_status` e mandam "registrar o que for aprovado" sem
dizer como a aprovação é registrada desde a 2.5.0. Esta SDD fecha essas
lacunas sem mudar regra nenhuma.

## Emendas

- **2026-11-25, RF10.** A verificação independente da rodada 1
  (`docs/sdd/validation-SDD-DTF-0060.md`, veredito FAIL, causa
  `especificacao`) achou escopo não registrado: as cópias dos dois prompts
  dentro da skill eram idênticas às canônicas antes desta SDD e ficaram
  para trás com ela, e a skill instalada as lê. O owner escolheu, na
  conversa de 2026-11-25, emendar esta SDD para copiar os dois prompts
  (RF10, task 4, A09), deixando a mudança no gerador para uma SDD própria.
  A emenda não muda os RF01 a RF09. O status segue `approved`, porque
  `status_lifecycle` não tem `approved → in_review`; a aprovação da emenda
  é uma review "Aprovado" do owner no commit dela, na PR #154.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: três arquivos de texto, reversão trivial, sem alternativa técnica a
registrar. `workflow-rules.yaml`, scripts, templates e `framework.version`
não mudam (`lessons_policy`).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | SKILL.md: seção nova "Aprovação", depois de "Ciclo de vida de status", que aponta `approval_policy` (seção 21: quem aprova cada tipo e sizing, humano ou política), `approved_by` (`frontmatter_schema`), `approval_hash.py`, `review_approval.py` e `approvers`, e diz que mudar o corpo depois da aprovação invalida o `content_sha256` | Quando o SKILL.md for lido, deve existir o título `## Aprovação` e ele deve citar `approval_policy`, `approved_by`, `approval_hash.py`, `review_approval.py` e `approvers` |
| RF02 | SKILL.md: o item "Monta a SDD" e o parágrafo de fluxo dizem que a SDD com `source_docs` em projeto sob 2.7.0 é enxuta (requisitos por referência à SPEC, `sizing` obrigatório, `check_source_docs.py` nas duas direções) e que a coluna `Projeto` (2.8.0) limita os RFs ao `project` da SDD | Quando o SKILL.md for lido, ele deve conter `enxuta` e `Projeto` |
| RF03 | SKILL.md: item novo em "O que fazer em cada pedido comum" para executor (ferramenta que roda o fluxo), apontando `executor_contract` (seção 20) e a regra de escrever só por PR; item novo para "Registra a aprovação", apontando RF01 | Quando o SKILL.md for lido, ele deve conter `executor_contract` |
| RF04 | SKILL.md: a tabela "Leia sob demanda" ganha a linha "aprovação, review, hash, executor" apontando `references/workflow-rules.yaml` nas chaves `approval_policy` e `executor_contract` | Quando o SKILL.md for lido, a tabela "Leia sob demanda" deve ter uma linha com `executor_contract` |
| RF05 | onboarding-bootstrap.md: o Passo 1.1 grava `repository_status: active` junto com `repository` (`registry.central_registry.repository_field`); se o código ainda não existe, o prompt não se aplica e o projeto segue em greenfield (`repository_status: none_yet`) | Quando o prompt for lido, ele deve conter `repository_status` e `none_yet` |
| RF06 | onboarding-bootstrap.md: o Passo 5 e o checklist de saída dizem que, em projeto sob 2.5.0 ou maior, o BASE e cada ADR confirmados entram em `approved` com `approved_by` `kind: human` e `evidence` (URL da review), e que pela PR isso sai de `review_approval.py` | Quando o prompt for lido, ele deve conter `approved_by` e `review_approval.py` |
| RF07 | framework-audit.md: o Passo 0 trata `repository_status: none_yet` — sem repositório de código não há commit a auditar, e o prompt para e reporta isso | Quando o prompt for lido, ele deve conter `none_yet` |
| RF08 | framework-audit.md: o Passo 5 diz como a aprovação de ADR reconstruído é registrada desde a 2.5.0, igual ao RF06 | Quando o prompt for lido, ele deve conter `approved_by` |
| RF09 | Os títulos dos dois prompts deixam de se apresentar como v1.3.0: passam a `(v1.3.0, revisado na 2.8.0)` | Quando os prompts forem lidos, a primeira linha de cada um deve conter `revisado na 2.8.0` |
| RF10 | Emenda de 2026-11-25 (ver "Emendas"): as cópias dos dois prompts dentro da skill, `_framework/skills/doc-traceability-framework/prompts/onboarding-bootstrap.md` e `framework-audit.md`, ficam idênticas às canônicas de `_framework/prompts/`, porque `references/onboarding.md` e `references/audit.md` mandam o agente da skill instalada ler essas cópias | Quando a SDD for verificada, `cmp` de cada cópia da skill contra o prompt canônico não deve imprimir nada |

Fora de escopo: `workflow-rules.yaml`, scripts, templates, as cópias
geradas dentro da skill (`references/`, `scripts/`, `templates/`; as de
`prompts/` entram pelo RF10, copiadas sem script), a mudança em
`render_prompts.py` para gerar e conferir as cópias de `prompts/` (SDD
própria), as
skills `handover`, `pickup` e `verify-sdd`, `prompts/universal.md` (gerado)
e os guias (SDD-DTF-0059). Os prompts de Cursor e Copilot também ficam de
fora: são gerados por `render_prompts.py` a partir de prefixos fixos no
próprio script, que ainda se apresentam como v1.7.0; atualizá-los é
mudança de script, para uma SDD própria.

## Especificação técnica consolidada

- **Onde.** `_framework/skills/doc-traceability-framework/SKILL.md`
  (RF01 a RF04), `_framework/prompts/onboarding-bootstrap.md` (RF05,
  RF06, RF09) e `_framework/prompts/framework-audit.md` (RF07 a RF09);
  as cópias dos dois prompts em
  `_framework/skills/doc-traceability-framework/prompts/` (RF10).
- **SKILL.md continua roteador.** As adições apontam a chave do YAML
  (`workflow-rules.yaml:approval_policy`, no formato das linhas
  existentes) e não copiam a regra. O front-matter (`name`,
  `description`) não muda.
- **`check_renderings.py`** confere o SKILL.md contra o YAML (tipos, Iron
  Laws, sizing, nenhum tipo ou status inexistente) e tem de continuar
  passando.
- **Gerado.** `_framework/INDEX.md` é refeito por `render_prompts.py`,
  nunca à mão.
- **Espelho no central.** Os três arquivos e `_framework/INDEX.md`,
  copiados sem divergência para `doc-traceability-central`, em branch e
  PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Seções e itens novos da skill | RF01 a RF04 | `_framework/skills/doc-traceability-framework/SKILL.md` | |
| 2 | Prompt de onboarding | RF05, RF06, RF09 | `_framework/prompts/onboarding-bootstrap.md` | |
| 3 | Prompt de auditoria | RF07 a RF09 | `_framework/prompts/framework-audit.md` | |
| 4 | Copiar os dois prompts para a pasta da skill | RF10 | `_framework/skills/doc-traceability-framework/prompts/onboarding-bootstrap.md`, `_framework/skills/doc-traceability-framework/prompts/framework-audit.md` | 2, 3 |
| 4b | Regenerar o índice | RF01 a RF10 | `_framework/INDEX.md` | 1, 2, 3, 4 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF10 | `central:_framework/skills/doc-traceability-framework/SKILL.md`, `central:_framework/prompts/onboarding-bootstrap.md`, `central:_framework/prompts/framework-audit.md`, `central:_framework/skills/doc-traceability-framework/prompts/onboarding-bootstrap.md`, `central:_framework/skills/doc-traceability-framework/prompts/framework-audit.md`, `central:_framework/INDEX.md` | 4b |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A08. O A09 entrou pela emenda de 2026-11-25.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01: seção Aprovação na skill | `f=_framework/skills/doc-traceability-framework/SKILL.md; grep -n "^## Aprovação" $f; for t in approval_policy approved_by approval_hash.py review_approval.py approvers; do grep -q "$t" $f \|\| echo "falta $t"; done` | Uma linha de título e nenhum `falta` | automatizado |
| A02 | RF02 a RF04: enxuta, Projeto e executor na skill | `f=_framework/skills/doc-traceability-framework/SKILL.md; for t in enxuta Projeto executor_contract; do grep -q "$t" $f \|\| echo "falta $t"; done` | Nenhum `falta` | automatizado |
| A03 | RF05 e RF06: prompt de onboarding | `f=_framework/prompts/onboarding-bootstrap.md; for t in repository_status none_yet approved_by review_approval.py; do grep -q "$t" $f \|\| echo "falta $t"; done` | Nenhum `falta` | automatizado |
| A04 | RF07 e RF08: prompt de auditoria | `f=_framework/prompts/framework-audit.md; for t in none_yet approved_by; do grep -q "$t" $f \|\| echo "falta $t"; done` | Nenhum `falta` | automatizado |
| A05 | RF09: títulos dos prompts | `head -1 _framework/prompts/onboarding-bootstrap.md _framework/prompts/framework-audit.md \| grep -c "revisado na 2.8.0"` | `2` | automatizado |
| A06 | RF01 a RF09: cada afirmação nova bate com a chave do YAML que ela cita (`approval_policy`, `frontmatter_schema.approved_by`, `executor_contract`, `registry.central_registry`) | Leitura lado a lado do diff dos três arquivos e das chaves citadas de `_framework/rules/workflow-rules.yaml` | Nenhuma afirmação sem chave correspondente ou que a contradiga | manual |
| A07 | Renderizações, gerados, suíte, validação e escopo | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0` três vezes; 0 failed; só os três arquivos, as duas cópias do RF10, `_framework/INDEX.md`, esta SDD, `docs/sdd/validation-SDD-DTF-0060.md` e os gerados de `docs/sdd/` (`registry.yaml`, `registry.md`, `INDEX.md`) | automatizado |
| A08 | Central: espelho idêntico | No central: `cmp` dos três arquivos, das duas cópias do RF10 e de `_framework/INDEX.md` contra o kit; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` | automatizado |
| A09 | RF10: cópias da skill idênticas às canônicas | `for p in onboarding-bootstrap framework-audit; do cmp _framework/prompts/$p.md _framework/skills/doc-traceability-framework/prompts/$p.md; done; echo "exit=$?"` | Sem saída de `cmp` e `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0060-skill-e-prompts`, a partir de
  `origin/main`. Commits com `Refs: SDD-DTF-0060`. Nunca em `main`.
- **Fonte:** cada afirmação nova vem da chave do YAML citada no RF, aberta
  na hora de escrever.
- **Não mudar** `workflow-rules.yaml`, scripts, templates, as cópias
  geradas dentro da skill (`references/`, `scripts/`, `templates/`), as
  outras skills, os prompts gerados nem os guias.
- **RF10:** copie os dois prompts canônicos, já com o texto final, sobre
  as cópias de `_framework/skills/doc-traceability-framework/prompts/`
  (`cp`), sem editar a cópia à mão e sem mudar `render_prompts.py`.
  Aproveite a rodada para os dois descompassos não bloqueantes do A06 da
  rodada 1: o item Executor do SKILL.md não pode dizer que toda escrita é
  por PR (`executor_contract.writes` também lista `entrega` e
  `approved_by` com `kind: policy`), e "em projeto sob 2.7.0" passa a
  "sob 2.7.0 ou maior".
- **Gerados só por script:** `render_prompts.py` para `_framework/INDEX.md`;
  `generate_registry_md.py` para `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF10) tem trecho
      correspondente nos arquivos. (Rodada 2, em `d9ea3a4`: RF01
      SKILL.md:79-90, depois de "Ciclo de vida de status" em :69; RF02
      :49-53 e :105; RF03 :106-107; RF04 :120; RF05 onboarding:10-12 e
      :33-42; RF06 :87-93 e :109-111; RF07 audit:31-34; RF08 :107-113; RF09
      linha 1 dos dois prompts; RF10 as duas cópias em
      `skills/doc-traceability-framework/prompts/`, idênticas às canônicas.)
- [x] Todo arquivo tocado aparece nas tasks ou nas instruções. (Rodada 2:
      os 11 arquivos de `git diff --name-only 7d9e858..d9ea3a4`, que são
      os três de produto (tasks 1-3), as duas cópias do RF10 (task 4),
      `_framework/INDEX.md` (task 4b), esta SDD,
      `docs/sdd/validation-SDD-DTF-0060.md` e os três gerados de
      `docs/sdd/`, exatamente a lista do A07.)
- [x] Nenhuma mudança em regra, script, template, gerado, outra skill ou
      guia. (Rodada 2: fora as cópias de `prompts/` que o RF10 trouxe para
      o escopo, nada mudou em `rules/`, `scripts/`, `templates/`,
      `references/`, outras skills ou guias. A ressalva da rodada 1, a
      cópia bundlada divergente, está resolvida pelo RF10: `cmp` sem saída
      no kit e no central.)

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Rodada 1: todas as linhas abaixo foram rodadas nesta sessão, no kit em
`0618b27` com base fixa `6233635` (`git merge-base HEAD origin/main`), e no
central na branch `espelho/SDD-DTF-0059-0060` (`e824ebb`), só leitura. Os
sensores mutaram cópias descartáveis em `/tmp` (`git archive`, `git clone`
e cópias dos arquivos do central), sem stash e sem commit.
Rodada 2: linhas com Rodada = 2, rodadas por outro subagente independente
(não fez a implementação nem a rodada 1), no kit em `d9ea3a4` com base fixa
`7d9e858` (`git merge-base HEAD origin/main`, depois do merge de main em
`aa9dba2`; os commits desta SDD no intervalo são `0618b27`, `d0b842c`,
`8ab9bc2` e `d9ea3a4`), e no central na branch `espelho/SDD-DTF-0059-0060`
(`065e53a`), só leitura. Sensores em `/tmp/sensor-0060-r2*` (`git archive`,
`git clone`, cópias dos arquivos do central e cópia inteira do central),
sem stash e sem commit.

Verificação independente completa em `docs/sdd/validation-SDD-DTF-0060.md`. Veredito: rodada 1 **FAIL**; rodada 2 **PASS**.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0060.md /home/user/doc-traceability-central/docs/DTF; echo "exit=$?"`; leitura do front-matter (comando rodado na verificação da rodada 2, em `8a5f22e`, não na rodada 1; na rodada 1 o passo 0 foi só leitura) | `✅ source_docs de SDD-DTF-0060.md conferem com o registry central.` `exit=0`; `source_docs: []` e `sizing: small`, sem SPEC nem ADR de origem (precedente SDD-DTF-0040): os itens 2 a 4 do passo 0 não se aplicam; a fonte de cada afirmação é a chave do YAML citada no RF (conferida no A06 da rodada 1) | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 1 | A01 | `f=_framework/skills/doc-traceability-framework/SKILL.md; grep -n "^## Aprovação" $f; for t in approval_policy approved_by approval_hash.py review_approval.py approvers; do grep -q "$t" $f \|\| echo "falta $t"; done` | `79:## Aprovação`; nenhum `falta` | seção 79-90 removida: sem título, `falta approval_hash.py`, `falta approvers`; cada termo apagado: `falta <termo>`; SKILL.md de `6233635`: 5 `falta`; restaurado: normal. Fraco: termos não restritos à seção | Sim | `docs/sdd/SDD-DTF-0060.md:102` (resolve em `SKILL.md:79-89`) | automatizado |
| 1 | A02 | `f=_framework/skills/doc-traceability-framework/SKILL.md; for t in enxuta Projeto executor_contract; do grep -q "$t" $f \|\| echo "falta $t"; done` | nenhum `falta` | cada termo apagado em todas as linhas: `falta <termo>`. Não discrimina: menção nova a `Projeto` (`SKILL.md:52`) trocada passa (pré-existente em `:15`); linha de RF04 (`:120`) removida passa (item de RF03 em `:107`). RF02 e RF04 confirmados por leitura | Sim | `docs/sdd/SDD-DTF-0060.md:103` (resolve em `SKILL.md:49-53`, `:107`, `:120`) | automatizado |
| 1 | A03 | `f=_framework/prompts/onboarding-bootstrap.md; for t in repository_status none_yet approved_by review_approval.py; do grep -q "$t" $f \|\| echo "falta $t"; done` | nenhum `falta` | cada termo apagado: `falta <termo>`; prompt de `6233635`: 4 `falta`; restaurado: nenhum | Sim | `docs/sdd/SDD-DTF-0060.md:104` (resolve em `onboarding-bootstrap.md:36-42`, `:87-93`, `:109-111`) | automatizado |
| 1 | A04 | `f=_framework/prompts/framework-audit.md; for t in none_yet approved_by; do grep -q "$t" $f \|\| echo "falta $t"; done` | nenhum `falta` | cada termo apagado: `falta <termo>`; prompt de `6233635`: 2 `falta`; restaurado: nenhum | Sim | `docs/sdd/SDD-DTF-0060.md:105` (resolve em `framework-audit.md:31-34`, `:107-113`) | automatizado |
| 1 | A05 | `head -1 _framework/prompts/onboarding-bootstrap.md _framework/prompts/framework-audit.md \| grep -c "revisado na 2.8.0"` | `2` | título de cada prompt revertido: `1`; texto movido para a linha 2: `1`; restaurado: `2` | Sim | `docs/sdd/SDD-DTF-0060.md:106` (resolve na linha 1 dos dois prompts) | automatizado |
| 1 | A06 | leitura lado a lado de `git diff 6233635..0618b27` dos três arquivos com `workflow-rules.yaml` em `approval_policy`, `frontmatter_schema.common_fields.approved_by`, `executor_contract`, `registry.central_registry` (`repository_field`, `approvers_field`), `audit.precondition`, `multi_project`, `document_types.SPEC.rf_optional_columns` e changelog 2.6.0/2.7.0; docstring de `review_approval.py` | nenhuma afirmação contradiz a chave citada; imprecisões não bloqueantes: item Executor resume `writes` como "o que escreve no central, sempre por PR" (`writes` inclui registry de projeto e `approved_by` policy); "sob 2.7.0" lido como "só 2.7.0" | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 1 | A07 | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0`; `exit=0`; `526 passed`; `exit=0`; 8 arquivos: `_framework/INDEX.md`, os dois prompts, `SKILL.md`, `docs/sdd/INDEX.md`, `SDD-DTF-0060.md`, `registry.md`, `registry.yaml` (`origin/main` = `6233635`) | INDEX.md com `2-8 KB`: `❌ divergente`, `exit=1`; Iron Law alterada no SKILL.md: `exit=1`; status do registry divergente: `exit=1`; arquivo extra aparece no `git diff --name-only 6233635`; restaurados: `exit=0`. Status inexistente no SKILL.md não derruba `check_renderings` (pré-existente) | Sim | `docs/sdd/SDD-DTF-0060.md:108` | automatizado |
| 1 | A08 | no central: `for p in <SKILL.md> <onboarding-bootstrap.md> <framework-audit.md> _framework/INDEX.md; do cmp $KIT/$p $p; done; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída nos quatro; `✅ Todas as verificações do framework passaram.` `exit=0` | título revertido na cópia: `differ: char 44, line 1`; SKILL.md de `dfa82db` (central): `differ: char 2726, line 49`; restaurado: sem saída | Sim | `docs/sdd/SDD-DTF-0060.md:109` | automatizado |
| 1 | Descompasso (bloqueante) | `git show 6233635:<canônico> \| cmp - <(git show 6233635:<cópia na skill>)`; `diff -q` dos mesmos em `0618b27` | em `6233635` idênticos; em `0618b27` divergem: `skills/doc-traceability-framework/prompts/{onboarding-bootstrap,framework-audit}.md` seguem v1.3.0 sem RF05 a RF09; `references/onboarding.md:4-5` e `references/audit.md:6` mandam o agente para essa cópia; `render_prompts.py --check` não a confere (`sync_copies`, `render_prompts.py:734`) | n/a | Não | `n/a` | manual |
| 2 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0060.md /home/user/doc-traceability-central/docs/DTF; echo "exit=$?"`; leitura do front-matter; emenda RF10 conferida contra a review do owner (`gh api repos/michelpessoa/doc-traceability-framework/pulls/154/reviews`) | `✅ source_docs de SDD-DTF-0060.md conferem com o registry central.` `exit=0`; `source_docs: []` e `sizing: small`, sem SPEC nem ADR de origem (precedente SDD-DTF-0040): os itens 2 a 4 do passo 0 não se aplicam; review `6057468337`: `michelpessoa COMMENTED aa9dba2 Aprovado`; a fonte de cada afirmação é a chave do YAML citada no RF (conferida no A06) | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 2 | A01 | `f=_framework/skills/doc-traceability-framework/SKILL.md; grep -n "^## Aprovação" $f; for t in approval_policy approved_by approval_hash.py review_approval.py approvers; do grep -q "$t" $f \|\| echo "falta $t"; done` | `79:## Aprovação`; nenhum `falta` | SKILL.md de `7d9e858`: 5 `falta`, sem título; cada termo trocado: `falta <termo>`; título trocado: saída vazia; restaurado: normal. Fraco (como na rodada 1): termos não restritos à seção; `awk` da seção acha os 5 termos e `content_sha256` | Sim | `docs/sdd/SDD-DTF-0060.md:122` (resolve em `SKILL.md:79-90`) | automatizado |
| 2 | A02 | `f=_framework/skills/doc-traceability-framework/SKILL.md; for t in enxuta Projeto executor_contract; do grep -q "$t" $f \|\| echo "falta $t"; done` | nenhum `falta` | SKILL.md de `7d9e858`: `falta enxuta`, `falta executor_contract` (`Projeto` pré-existente, não discrimina RF02 nessa parte); cada termo trocado: `falta <termo>`; restaurado: nenhum. RF02 e RF04 confirmados por leitura (`:49-53`, `:120`) | Sim | `docs/sdd/SDD-DTF-0060.md:123` (resolve em `SKILL.md:49-53`, `:107`, `:120`) | automatizado |
| 2 | A03 | `f=_framework/prompts/onboarding-bootstrap.md; for t in repository_status none_yet approved_by review_approval.py; do grep -q "$t" $f \|\| echo "falta $t"; done` | nenhum `falta` | prompt de `7d9e858`: 4 `falta`; cada termo trocado: `falta <termo>`; restaurado: nenhum | Sim | `docs/sdd/SDD-DTF-0060.md:124` (resolve em `onboarding-bootstrap.md:10-12`, `:33-42`, `:87-93`, `:109-111`) | automatizado |
| 2 | A04 | `f=_framework/prompts/framework-audit.md; for t in none_yet approved_by; do grep -q "$t" $f \|\| echo "falta $t"; done` | nenhum `falta` | prompt de `7d9e858`: 2 `falta`; cada termo trocado: `falta <termo>`; restaurado: nenhum | Sim | `docs/sdd/SDD-DTF-0060.md:125` (resolve em `framework-audit.md:31-34`, `:107-113`) | automatizado |
| 2 | A05 | `head -1 _framework/prompts/onboarding-bootstrap.md _framework/prompts/framework-audit.md \| grep -c "revisado na 2.8.0"` | `2` | título de cada prompt revertido: `1`; prompts de `7d9e858`: `0`; restaurado: `2` | Sim | `docs/sdd/SDD-DTF-0060.md:126` (resolve na linha 1 dos dois prompts) | automatizado |
| 2 | A06 | leitura lado a lado de `git diff 7d9e858..d9ea3a4` dos três arquivos (e `git diff aa9dba2..d9ea3a4` do SKILL.md) com `workflow-rules.yaml` em `approval_policy`, `frontmatter_schema.common_fields.approved_by`, `executor_contract.writes`, `registry.central_registry` (`repository_field`, `approvers_field`), `audit.precondition`, `document_types.SPEC.rf_optional_columns`, changelog 2.7.0; `review_approval.py:9,143-145`; `validate_doc.py:459` | nenhuma afirmação sem chave ou que a contradiga. Ajustes da rodada 1 resolvidos: item Executor (`SKILL.md:107`) agora cobre os itens de `writes` (central por PR; `entrega` e `path` no registry de projeto; `approved_by` `kind: policy` só onde `approval_policy` permite); "sob 2.7.0 ou maior" em `:49` e `:105`, igual a `validate_doc.py:459` | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 2 | A07 | `python3 _framework/scripts/check_renderings.py; echo "exit=$?"; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0`; `exit=0`; `526 passed`; `✅ Todas as verificações do framework passaram.` `exit=0`; 11 arquivos, os previstos (`origin/main` = merge-base `7d9e858`; igual com `git diff --name-only 7d9e858`) | INDEX.md com `2-8 KB`: `❌ _framework/INDEX.md: divergente`, `exit=1`; Iron Law `gate_branch_before_commit` alterada no SKILL.md: `exit=1`; status da SDD-0060 no registry trocado: `exit=1`; arquivo extra aparece no `git diff --name-only 7d9e858`; restaurados: `exit=0`. Cópia de prompt da skill mutada não derruba `render_prompts.py --check` (por isso o A09) | Sim | `docs/sdd/SDD-DTF-0060.md:128` | automatizado |
| 2 | A08 | no central (`065e53a`): `for p in <SKILL.md> <2 prompts> <2 cópias da skill> _framework/INDEX.md; do cmp $KIT/$p $p; done; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e exit 0 nos seis; `✅ 134 documento(s) ok.` `✅ Todas as verificações do framework passaram.` `exit=0`; `diff -rq` de `_framework/` inteiro kit x central: sem saída; `git status` do central vazio | cópia de `framework-audit.md` da skill mutada: `differ: char 1465, line 31`; SKILL.md e cópia de onboarding de `e824ebb` (central na rodada 1): `differ: char 2746, line 49` e `differ: char 70, line 1`; status trocado num registry de cópia inteira do central: `framework_check` `exit=1`; restaurado: sem saída | Sim | `docs/sdd/SDD-DTF-0060.md:129` | automatizado |
| 2 | A09 | `for p in onboarding-bootstrap framework-audit; do cmp _framework/prompts/$p.md _framework/skills/doc-traceability-framework/prompts/$p.md; done; echo "exit=$?"` | sem saída de `cmp`; `exit=0` (cada `cmp` isolado: exit 0) | cópia de onboarding mutada: `differ: char 659, line 11`, mas `exit=0` (o `$?` é só do último `cmp`; a saída discrimina); cópia de audit com linha a mais: `EOF on ... after byte 5254`, `exit=1`; cópias de `7d9e858`: `differ` nas duas, `exit=1`; restaurado: sem saída, `exit=0` | Sim | `docs/sdd/SDD-DTF-0060.md:130` | automatizado |
