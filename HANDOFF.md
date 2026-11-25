# HANDOFF — implementação das SDD-DTF-0061, 0062 e 0063 (2026-11-25 16:55)

_Escopo: repo do projeto: doc-traceability-framework (kit, `docs/sdd/`), com espelho no central `doc-traceability-central`_

## Goal
Levar a `implemented` as três SDDs de tooling que a verificação da SDD-DTF-0060 revelou, cada uma com implementação e verificação independente, e espelhar o resultado no central.

## Status
- **Pronto:** as três SDDs estão `approved` por review do owner. Cada uma está na sua branch, numa PR em rascunho, ainda sem nenhuma linha de implementação:

  | SDD | Branch | PR | Head |
  |---|---|---|---|
  | SDD-DTF-0061 | `sdd/SDD-DTF-0061-sync-prompts-da-skill` | #156 | `0b5eca0` |
  | SDD-DTF-0062 | `sdd/SDD-DTF-0062-nucleo-aprovacao-executor` | #157 | `a340526` |
  | SDD-DTF-0063 | `sdd/SDD-DTF-0063-check-renderings-status-tipo` | #155 | `59c42e3` |

- **Base:** as três branches saíram de `origin/main` `ac99da1`, o merge da PR #154.
- **Em andamento:** nada.
- **Não começado:**
  - a implementação das três;
  - a verificação independente das três;
  - o `implemented` das três;
  - as três PRs de espelho no central.

## Ids relacionados
- SDD-DTF-0061 — approved (review https://github.com/michelpessoa/doc-traceability-framework/pull/156#pullrequestreview-6061537180)
- SDD-DTF-0062 — approved (review https://github.com/michelpessoa/doc-traceability-framework/pull/157#pullrequestreview-6061541572)
- SDD-DTF-0063 — approved (review https://github.com/michelpessoa/doc-traceability-framework/pull/155#pullrequestreview-6061532390)
- SDD-DTF-0060 — implemented: origem dos três achados (`docs/sdd/validation-SDD-DTF-0060.md`, rodada 1 item 5 e rodada 2 item 4)
- SDD-DTF-0056 — implemented: precedente de sizing `small` para script com teste

## Files touched
- `docs/sdd/SDD-DTF-0061.md`, `docs/sdd/SDD-DTF-0062.md` e `docs/sdd/SDD-DTF-0063.md`: as SDDs, cada uma só na sua branch.
- `docs/sdd/registry.yaml`, `docs/sdd/registry.md` e `docs/sdd/INDEX.md`: cada branch tem uma entrada nova e os gerados refeitos.
- `HANDOFF.md`: este arquivo, que entra em `main` por PR própria.
- Os arquivos que cada implementação pode tocar estão nas tasks de cada SDD; não estão listados aqui.

## Key decisions
- **Uma SDD por achado, cada uma em branch e PR próprias,** para que cada uma tenha a sua verificação. As três acrescentam uma entrada ao fim de `docs/sdd/registry.yaml`; na que entrar depois, o conflito é mecânico: refazer o registry com as entradas de `main` e regenerar com `generate_registry_md.py` e `render_prompts.py`.
- **Ordem sugerida: 0061, depois 0062, depois 0063.**
  - A 0061 (`sync_copies`) e a 0062 (`core_facts`) mudam funções diferentes de `render_prompts.py`.
  - A 0063 precisa continuar sem falso positivo sobre o `AGENTS.md` que a 0062 gera.
  - As três podem andar em paralelo, mas a que entrar depois faz merge de `main` e regenera.
- **O achado "prompts de Cursor e Copilot dizem v1.7.0" estava errado.** O `v1.7.0` só existe no `prefix` fixo do script e é trocado pela versão do YAML; os gerados mostram v2.8.0. A SDD-DTF-0062 trata o problema real: o núcleo canônico não fala de aprovação nem de executor, e a cadeia do ciclo de status sugere `rejected → implemented`.
- **As regras da SDD-DTF-0063 foram testadas** sobre as cinco renderizações de `ac99da1`, sem nenhum falso positivo. A versão mais solta acusava `repository_status: none_yet` e "Muda o status: valide", e foi descartada.
- **Forma de trabalho usada nas SDD-DTF-0059 e 0060, a pedido do owner:**
  - a implementação roda num subagente novo, de contexto limpo;
  - a verificação roda noutro subagente `sdd-verifier`;
  - quem despacha marca `implemented` só depois de PASS e de `validate_state.py docs/sdd` sem erro.
- **Na tabela de evidência, toda linha precisa de comando rodado de fato,** inclusive "Fidelidade à origem". A SDD-DTF-0060 levou recusa do `validate_state.py` por uma linha com "n/a". O modelo certo é a linha equivalente de `docs/sdd/SDD-DTF-0059.md`, que roda `check_source_docs.py ... /home/user/doc-traceability-central/docs/DTF`.

## Open threads / blockers
- **O sizing da SDD-DTF-0062 é `small`,** com a ressalva escrita na SDD: o owner pode subir na review. Ele aprovou sem mudar.
- **O espelho no central fica para depois do merge de cada SDD no kit,** em branch e PR próprias (task de espelho e critério A07 de cada SDD). Para a SDD-DTF-0062, o central roda `render_prompts.py` e regenera o próprio `AGENTS.md`.
- **Fora deste fluxo:** a pós-release 0.9.1 da fábrica (`fabrica-agentica`, PR #87 mergeada em `f4b5d35`) está com o owner.

## Next step
Numa sessão nova, rode `git fetch origin sdd/SDD-DTF-0061-sync-prompts-da-skill && git checkout sdd/SDD-DTF-0061-sync-prompts-da-skill && git merge origin/main` e despache um subagente de contexto limpo para implementar a SDD-DTF-0061 conforme as "Instruções específicas" dela, com o teste escrito primeiro.

## Don't do
- Não implementar nem verificar na mesma sessão ou subagente que implementou: quem implementa não verifica.
- Não editar gerado à mão (`AGENTS.md`, prompts gerados, cópias da skill, `INDEX.md`, `registry.md`): só `render_prompts.py` e `generate_registry_md.py`.
- Não mudar `workflow-rules.yaml` nem `framework.version` em nenhuma das três.
- Não marcar `implemented` com linha de evidência sem comando rodado ("n/a").
- Não rodar a suíte com um merge em andamento: `test_check_commit_json` falha enquanto existe `MERGE_HEAD`. Conclua o merge e rode de novo.
- Não extrair `git archive` direto em `/tmp`: use um diretório próprio, vazio, para os sensores.
- Não fazer merge em `main`, nem no kit nem no central: é do owner.
