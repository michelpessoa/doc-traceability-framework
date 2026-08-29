# Framework de Documentação & Rastreabilidade para IA

Registra e rastreia as decisões de um projeto — do problema à linha de
código — em documentos versionados, com gates que uma ferramenta de IA não
consegue pular em silêncio.

Não depende de fornecedor de IA. As regras vivem em um YAML canônico; cada
ferramenta recebe uma renderização gerada dele.

## Comece por aqui

| Se você quer | Vá para |
|---|---|
| **usar** o framework num projeto | [`QUICKSTART.md`](QUICKSTART.md) — uma página |
| **entender a regra** completa | [`docs/especificacao.md`](docs/especificacao.md) — gerada do YAML |
| **operar como IA** (Codex, Cursor, Gemini CLI, Copilot, Aider) | [`AGENTS.md`](AGENTS.md) — lido nativamente |
| **aprender pelo exemplo** | [`docs/guias/`](docs/guias/) e [`examples/`](examples/) |
| **saber o que mudou** | [`CHANGELOG.md`](CHANGELOG.md) — gerado do YAML |

## A ideia em três frases

Decisão vira documento antes de virar código. Documento sem critério
verificável não avança de status. Código nasce em branch própria e chega à
main por PR, com o id do documento que o originou.

O tamanho da mudança decide **quais** documentos existem — uma correção de
três arquivos escreve só uma SDD. Nunca decide se a ordem vale.

## O que é canônico e o que é gerado

`_framework/rules/workflow-rules.yaml` é a única fonte de verdade.
`AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md` e os
prompts em `_framework/prompts/` são **gerados** a partir dele:

```
python3 _framework/scripts/render_prompts.py           # regenera
python3 _framework/scripts/render_prompts.py --check   # o CI roda isto
```

Editar arquivo gerado à mão reprova no CI. Para mudar comportamento, edite
o YAML e regenere.

Escritos à mão: os guias em `docs/guias/` (narrativa e exemplos) e os
templates em `_framework/templates/`.

## Validar

```
python3 _framework/scripts/framework_check.py --auto
```

Verde significa registry e documentos consistentes, sem placeholder e sem
escopo pendente. É o mesmo comando do CI e do hook de pre-commit.

## Dois repositórios

O **central** guarda `_framework/` e `docs/{PROJECT_CODE}/` — todas as
decisões de todos os projetos. O **repositório de código** guarda
`docs/sdd/`, porque a SDD é o único documento pensado para ser lido por
uma IA no momento de implementar.

Projeto cujo repositório de código ainda não existe roda o fluxo inteiro no
central — veja o modo greenfield no `QUICKSTART.md`.

## Licença

MIT — veja [`LICENSE`](LICENSE).
