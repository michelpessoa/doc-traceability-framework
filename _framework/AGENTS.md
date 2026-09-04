# AGENTS.md — `_framework/`

Escopo: tudo dentro desta subárvore (`rules/`, `templates/`, `prompts/`,
`skills/`, `scripts/`, `procedures/`).

## Não-negociáveis

- **Espelho do kit público.** Qualquer alteração aqui DEVE ser replicada
  em [doc-traceability-framework](https://github.com/michelpessoa/doc-traceability-framework),
  mesma estrutura de pastas, arquivo a arquivo. Antes de encerrar uma
  tarefa que tocou `_framework/`, confirme que o diff foi aplicado lá
  também.
- **YAML manda.** `rules/workflow-rules.yaml` é a fonte canônica das
  Iron Laws, sizing e ciclo de status. `AGENTS.md` da raiz e
  `docs/especificacao.md` são **gerados** de lá por
  `scripts/render_prompts.py` — não edite esses gerados à mão, o CI
  reprova (`render_prompts.py --check`). Mude o YAML, regenere.
- **Skills espelham `procedures/`.** Cada `skills/<nome>/SKILL.md` é o
  ponto de entrada; o procedimento normativo completo vive em
  `procedures/<nome>.md`. Mudar um sem o outro quebra a rastreabilidade
  entre os dois.

Ver raiz do repositório para as leis inegociáveis completas (`/AGENTS.md`).
