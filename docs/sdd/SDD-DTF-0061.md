---
id: SDD-DTF-0061
type: SDD
title: "render_prompts.py sincroniza e confere as cópias dos prompts dentro da skill"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-11-25"
updated: "2026-11-25"
relates_to: [SDD-DTF-0060]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small: correção de tooling achada na verificação da SDD-DTF-0060 (rodada 1, descompasso bloqueante, e rodada 2, item 4); ausência de SPEC e de source_docs é o registro de que a fase foi pulada (precedente SDD-DTF-0056). Leia esta SDD inteira; ela nomeia a constante, as mensagens e os testes. Teste primeiro, visto falhar; depois o código. A cópia do script na skill e o _framework/INDEX.md são gerados por render_prompts.py, nunca à mão. A SDD-DTF-0062 também muda render_prompts.py, em outra função: se ela entrar antes, faça merge de main e regenere. O central espelha em branch e PR próprios."
supersedes: null
superseded_by: null
tags: [render_prompts, skill, prompts, tooling, sync]
---

# render_prompts.py sincroniza e confere as cópias dos prompts dentro da skill

> Compilada em sizing `small`: os requisitos estão escritos aqui mesmo, sem
> SPEC de origem. Vive no repositório do projeto (kit) porque é o documento
> lido pela IA ao implementar.

## Resumo executivo

`_framework/rules/kit-index.yaml` declara
`skills/doc-traceability-framework/prompts/*` como "Cópia gerada de
prompts/{name} dentro da skill" e manda regenerar com `render_prompts.py`.
Só que `sync_copies` (`_framework/scripts/render_prompts.py`) copia scripts,
o YAML e os templates, e não copia os prompts. Por isso
`render_prompts.py --check` não vê quando
`skills/doc-traceability-framework/prompts/onboarding-bootstrap.md` ou
`framework-audit.md` ficam para trás do canônico. Isso aconteceu na
SDD-DTF-0060, rodada 1: a skill instalada lia os prompts antigos, porque
`references/onboarding.md` e `references/audit.md` mandam ler a cópia da
skill. A SDD-DTF-0060 resolveu à mão (RF10, `cp`). Esta SDD faz o gerador
cobrir as cópias, para que a divergência volte a reprovar o `--check`.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `small`, nenhum critério de `decision_gates.rfc_to_adr` se
aplica: uma função de um script e o seu teste, no mesmo padrão já usado
para templates. `workflow-rules.yaml`, `kit-index.yaml` e
`framework.version` não mudam (`lessons_policy`: é falha de execução, não
desenho).

## Requisitos consolidados

| RF | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | `render_prompts.py` ganha a constante `BUNDLED_PROMPTS = ("framework-audit.md", "onboarding-bootstrap.md")`, os prompts que a skill embute, e `sync_copies` sincroniza cada `prompts/{nome}` para `skills/doc-traceability-framework/prompts/{nome}` por `_sync_file` | Quando o canônico `prompts/onboarding-bootstrap.md` for diferente da cópia da skill e `render_prompts.py` rodar sem `--check`, a cópia deve ficar idêntica ao canônico |
| RF02 | Com `--check`, a cópia divergente ou ausente reprova com a mensagem que `_sync_file` já usa (`❌ {dest}: divergente de {src}.`) e o script sai com código 1 | Quando a cópia da skill divergir do canônico e `render_prompts.py --check` rodar, a saída deve conter `divergente de` e o código de saída deve ser 1 |
| RF03 | Arquivo `*.md` em `skills/doc-traceability-framework/prompts/` cujo nome não está em `BUNDLED_PROMPTS` reprova nos dois modos, com `❌ {arquivo}: órfão (fora de BUNDLED_PROMPTS) — remova à mão.`, e nunca é apagado pelo script | Quando existir `skills/doc-traceability-framework/prompts/extra.md`, `render_prompts.py` com e sem `--check` deve imprimir `órfão` e sair com 1, e o arquivo deve continuar existindo |
| RF04 | A docstring de `sync_copies` passa a citar os prompts embutidos ao lado de scripts, YAML e templates | Quando a docstring for lida, ela deve conter `BUNDLED_PROMPTS` |
| RF05 | Testes em `_framework/scripts/tests/test_render_prompts_sync.py` cobrem RF01 a RF03 em repositório temporário e conferem que o kit real está em dia | Quando o pytest do arquivo rodar, os testes novos devem passar, e com a sincronização dos prompts removida de `sync_copies` pelo menos um deve falhar |
| RF06 | `_framework/scripts/tests/mutations.yaml` ganha uma mutação que remove a sincronização dos prompts, morta por `test_render_prompts_sync.py`, para `selftest.py` cobrir o RF01 | Quando `python3 _framework/scripts/selftest.py` rodar, a mutação nova deve morrer, e a contagem de mutações deve subir em uma unidade |

Fora de escopo: copiar para a skill outros prompts (`universal.md`, Cursor,
Copilot); mudar `kit-index.yaml`, `references/onboarding.md` ou
`references/audit.md`; o núcleo canônico das renderizações (SDD-DTF-0062);
`check_renderings.py` (SDD-DTF-0063).

## Especificação técnica consolidada

- **Onde.** `_framework/scripts/render_prompts.py`, função `sync_copies`,
  e a constante nova `BUNDLED_PROMPTS` no topo do módulo.
- **Sincronização.** Depois do laço dos templates, para cada nome de
  `BUNDLED_PROMPTS`: `ok &= _sync_file(root / "prompts" / nome, skill /
  "prompts" / nome, check)`.
- **Órfãos.** Para cada `*.md` direto em `skill / "prompts"` (não
  recursivo) cujo `name` não está em `BUNDLED_PROMPTS`: imprimir a
  mensagem do RF03 e `ok = False`. Não apagar.
- **Testes.** Em `test_render_prompts_sync.py`, no padrão dos testes de
  template existentes (`tmp_path` com a árvore mínima): gera a cópia
  (RF01); `--check` com cópia divergente e com cópia ausente (RF02); órfão
  nos dois modos, com o arquivo preservado (RF03); o kit real com
  `sync_copies(root, check=True)` verdadeiro.
- **Gerados.** A cópia `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`
  e `_framework/INDEX.md` saem de `render_prompts.py`.
- **Espelho no central.** O script, a cópia da skill, o teste,
  `mutations.yaml` e `_framework/INDEX.md`, em branch e PR próprios.

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Testes novos, vistos falhar | RF01 a RF03, RF05 | `_framework/scripts/tests/test_render_prompts_sync.py` | |
| 2 | Constante, sincronização, órfãos e docstring | RF01 a RF04 | `_framework/scripts/render_prompts.py` | 1 |
| 3 | Mutação do selftest | RF06 | `_framework/scripts/tests/mutations.yaml` | 2 |
| 4 | Regenerar a cópia da skill e o índice | RF01 a RF04 | `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `_framework/INDEX.md` | 2 |
| 5 | Espelhar no central, em branch e PR próprios | RF01 a RF06 | `central:_framework/scripts/render_prompts.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `central:_framework/scripts/tests/test_render_prompts_sync.py`, `central:_framework/scripts/tests/mutations.yaml`, `central:_framework/INDEX.md` | 4 |

## Critérios de aceite / definição de pronto

Executar na raiz do kit, na branch de implementação, salvo o A07.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01 a RF03, RF05: testes novos | `python3 -m pytest _framework/scripts/tests/test_render_prompts_sync.py -q` | ANTES da task 2: pelo menos 3 failed; DEPOIS: todos passam | automatizado |
| A02 | RF01: sensor da sincronização | Em cópia descartável, remover de `sync_copies` o laço de `BUNDLED_PROMPTS`; rodar o pytest do A01; restaurar | Com a mutação: pelo menos 1 failed; restaurado: 0 failed | automatizado |
| A03 | RF02: o kit real reprova divergência | Em cópia descartável do kit, acrescentar uma linha a `_framework/skills/doc-traceability-framework/prompts/framework-audit.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `divergente de` na saída e `exit=1` | automatizado |
| A04 | RF04: docstring | `grep -c "BUNDLED_PROMPTS" _framework/scripts/render_prompts.py` | ≥ 3 (constante, uso e docstring) | automatizado |
| A05 | RF06: selftest | `python3 _framework/scripts/selftest.py; echo "exit=$?"` | `N mutação(ões): todos os mutantes morreram.`, com N uma unidade acima do de `origin/main` antes da branch, e `exit=0` | automatizado |
| A06 | Gerados, suíte, lint e escopo | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/render_prompts.py _framework/skills/doc-traceability-framework/scripts/render_prompts.py; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0`; `cmp` sem saída; 0 failed; ruff e mypy sem erro; `exit=0`; só os arquivos das tasks 1 a 4, esta SDD, o seu `validation-SDD-DTF-0061.md` e os gerados de `docs/sdd/` | automatizado |
| A07 | Central: espelho idêntico | No central: `cmp` dos arquivos da task 5 contra o kit; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` | `cmp` sem saída e `exit=0` nos dois | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** `sdd/SDD-DTF-0061-sync-prompts-da-skill`, já aberta
  com esta SDD. Comece por `git fetch origin main && git merge origin/main`
  e regenere os gerados se houver conflito em `docs/sdd/`. Commits com
  `Refs: SDD-DTF-0061`. Nunca em `main`.
- **Teste primeiro:** escrever os testes, ver falhar, guardar a saída.
- **Não mudar** `workflow-rules.yaml`, `kit-index.yaml`, os prompts, os
  `references/` da skill, `check_renderings.py` nem `core_facts`.
- **Gerados só por script:** `render_prompts.py` para a cópia da skill e os
  índices; `generate_registry_md.py` para `registry.md`.
- **Evidência de verificação** só por verificador independente, em sessão
  ou subagente separado.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF06) tem código ou teste
      correspondente.
- [ ] Todo arquivo tocado aparece nas tasks ou nas instruções.
- [ ] Nenhuma abstração, config ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 1 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0061.md /home/user/doc-traceability-central/docs/DTF; echo "exit=$?"`; leitura do front-matter | `✅ source_docs de SDD-DTF-0061.md conferem com o registry central.` `exit=0`; `source_docs: []` e `sizing: small`, sem SPEC nem ADR de origem (precedente SDD-DTF-0056): os itens 2 a 4 do passo 0 não se aplicam, e RF01 a RF06 estão escritos na própria SDD | sem teste automatizado (leitura) | Sim | `n/a` | manual |
| 1 | A01 | `python3 -m pytest _framework/scripts/tests/test_render_prompts_sync.py -q`, no kit em `665e66f` e numa cópia de `2f4c2b9` (testes antes da task 2) | `665e66f`: `12 passed`; `2f4c2b9`: `4 failed, 8 passed` (gera, atualiza, check divergente/ausente, órfão) | ver A02; `_root` sem a pasta `prompts/` (cópia): todos os testes de `sync_copies` caem com `FileNotFoundError`, então a mudança do helper é necessária | Sim | `_framework/scripts/tests/test_render_prompts_sync.py:105`, `:126`, `:144` | automatizado |
| 1 | A02 | em cópia descartável: laço de `BUNDLED_PROMPTS` removido de `sync_copies`; pytest do A01; restaurado por cópia guardada | mutação: `4 failed, 8 passed` (gera, atualiza, check, kit real); restaurado: `12 passed` | outras mutações na cópia: mensagem de órfão sem `ok = False`: `2 failed`; órfão apagado (`unlink`): `2 failed`; `check` trocado por `False` na chamada dos prompts: `2 failed`; restaurado: `12 passed` | Sim | `_framework/scripts/tests/test_render_prompts_sync.py:105` | automatizado |
| 1 | A03 | cópia descartável de `665e66f`, linha acrescentada a `_framework/skills/doc-traceability-framework/prompts/framework-audit.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `❌ .../skills/doc-traceability-framework/prompts/framework-audit.md: divergente de .../prompts/framework-audit.md.` `exit=1`; controle sem a mutação: `exit=0`, 0 `❌` | mesma mutação numa cópia de `731c4c6` (antes da SDD): 0 `❌`, `exit=0`, ou seja, o critério discrimina. Extras na cópia de `665e66f`: `extra.md` na pasta de prompts da skill dá `órfão (fora de BUNDLED_PROMPTS)` e `exit=1` com e sem `--check`, e o arquivo continua lá; canônico `onboarding-bootstrap.md` alterado e script sem `--check`: `exit=0` e cópia idêntica (`cmp`) | Sim | `_framework/scripts/render_prompts.py:766` (via `--check`) | automatizado |
| 1 | A04 | `grep -c "BUNDLED_PROMPTS" _framework/scripts/render_prompts.py`; `python3 -c "import render_prompts as r; print('BUNDLED_PROMPTS' in r.sync_copies.__doc__)"` | `6` (linhas 61, 743, 748, 765, 770, 771); `True` | cópia com `BUNDLED_PROMPTS` tirado da docstring: `grep -c` dá `4`, ainda ≥ 3, então o grep não discrimina a docstring (critério fraco); a leitura da docstring via `ast` dá `False`, derrubado | Sim | `_framework/scripts/render_prompts.py:743` | automatizado |
| 1 | A05 | `python3 _framework/scripts/selftest.py; echo "exit=$?"` no kit em `665e66f`, e o mesmo numa cópia de `7c86bb9` (`origin/main` = merge-base) | kit: `✅ 11 mutação(ões): todos os mutantes morreram.` `exit=0`; `7c86bb9`: `✅ 10 mutação(ões)`, `exit=0`; `git status --porcelain` vazio depois | só a mutação nova (YAML de uma entrada): `1 mutação(ões)... morreram`. Mutação equivalente (comentário no fim da linha) também morre, porque `test_sync_copies_kit_real_em_dia` reprova qualquer mudança no script, cuja cópia na skill passa a divergir; a morte por comportamento está provada no A02 | Sim | `_framework/scripts/tests/mutations.yaml:68` | automatizado |
| 1 | A06 | `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; cmp _framework/scripts/render_prompts.py _framework/skills/doc-traceability-framework/scripts/render_prompts.py; python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q; ruff check _framework/scripts; ruff format --check _framework/scripts; mypy _framework/scripts; python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"; git diff --name-only origin/main` | `exit=0`, 0 `❌` (`_framework/INDEX.md: em dia`); `cmp` sem saída; `531 passed in 68.82s`; `All checks passed!`; `42 files already formatted`; `Success: no issues found in 42 source files`; `✅ Todas as verificações do framework passaram.` `exit=0`; diff: os 4 arquivos das tasks 1 a 4, `SDD-DTF-0061.md`, `docs/sdd/INDEX.md`, `registry.md`, `registry.yaml` (`origin/main` = merge-base `7c86bb9`) | cópia com o tamanho de `test_render_prompts_sync.py` trocado no INDEX: `❌ _framework/INDEX.md: divergente do gerado`, `exit=1`; cópia da skill com uma linha a mais: `cmp` acusa EOF e `--check` dá `exit=1` | Sim | `n/a` (suíte inteira e lista do diff) | automatizado |
| 1 | A07 | no central `/home/user/doc-traceability-central` (`8798155`, sem a mudança): `cmp` de cada arquivo da task 5 contra o kit e contra `git show 7c86bb9:<arquivo>` | contra o kit: `render_prompts.py` e sua cópia `differ: char 2187, line 58`, teste `differ: char 84, line 1`, `mutations.yaml` `EOF ... after byte 3623`, `_framework/INDEX.md` igual; contra `7c86bb9`: os cinco iguais. O central ainda tem o kit anterior, sem branch de espelho da SDD | sem teste automatizado nesta etapa: o espelho vem depois do merge no kit (task 5), e o critério é rodado por quem espelhar | Pendente: etapa pós-merge no kit | `n/a` (`cmp`) | automatizado (estado pré-espelho) |
