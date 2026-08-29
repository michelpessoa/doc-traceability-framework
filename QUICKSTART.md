# Quickstart (framework v2.1.0)

Arquivo GERADO por `_framework/scripts/render_prompts.py`. Não edite à
mão.

## Em 30 segundos

Este framework registra decisões de projeto em documentos versionados e
obriga que código só nasça depois de especificação, em branch dedicada.
Quem executa é uma ferramenta de IA qualquer — as regras não dependem de
nenhuma delas.

Tipos ativos: STRAT, RFC, ADR, SPEC, SDD, BASE, INC, PM.

## Não cole prompt

Abra o repositório na sua ferramenta de IA. `AGENTS.md`, na raiz, é lido
nativamente por Codex, Cursor, Gemini CLI, Copilot e Aider; o Claude Code
lê `CLAUDE.md`. Não há prompt para colar a cada conversa.

## Primeiro trabalho

1. Descreva a mudança e peça o **sizing**. Mudança de até ~3 arquivos,
   sem impacto arquitetural e sem mudar comportamento externo, é `small`.
2. `small` → só a SDD, em `docs/sdd/` do repositório de código.
   `medium` → SPEC no repositório central, depois a SDD.
3. Aprove a SDD. Só então o código começa, em branch própria.
4. Antes de marcar `implemented`, rode os critérios de aceite e registre
   comando e saída reais na própria SDD.

## Validar a qualquer momento

```
python3 _framework/scripts/framework_check.py --auto
```

Verde significa registry e documentos consistentes, sem placeholder e
sem escopo pendente. É o mesmo comando que roda no CI.

## Onde está o resto

- `AGENTS.md` — o núcleo canônico e o caminho comum.
- `_framework/rules/workflow-rules.yaml` — fonte de verdade. Manda sobre
  qualquer arquivo gerado.
- `_framework/templates/` — um template por tipo de documento.
