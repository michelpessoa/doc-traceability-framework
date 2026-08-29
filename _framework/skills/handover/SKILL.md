---
name: handover
description: >
  Gera HANDOFF.md para transferir contexto entre sessões ou agentes do
  framework de rastreabilidade, referenciando ids dos documentos em vez de
  reescrever o conteúdo deles. Use when o planejamento terminou e outra
  sessão vai implementar, quando o uso de contexto da sessão atual passa de
  ~45% com trabalho ainda pela frente, ou quando o usuário pedir para
  "fazer o handover", "passar isso pro próximo", "documentar onde parei".
  Do NOT use for retomar um handoff já existente (use `pickup`), para
  gerar documentação permanente do projeto — HANDOFF.md é descartável e
  sobrescreve em lugar —, nem como substituto de qualquer gate: a SDD
  continua precisando estar approved antes de implementar.
---

# Handover

Produz um `HANDOFF.md` para que a próxima sessão/agente retome o trabalho
sem herdar esta sessão inteira nem reconstruir contexto lendo tudo de
novo — só o necessário para continuar.

## Quando usar

- Planejamento terminou (PRD/Tech Spec/SDD compilados e no status
  correto) e a implementação vai rodar em sessão ou agente separado.
- Uso de contexto da sessão atual está perto do limite que o usuário
  configurou (padrão sugerido: ~45%) e ainda há trabalho do fluxo pela
  frente — documentar ou implementar.
- Troca deliberada de agente no meio da implementação (ex.: subagente por
  tarefa).

Não use para o encerramento normal de uma tarefa completa e verificada —
handover é para trabalho que continua em outra sessão, não para relatar
conclusão.

## Onde o HANDOFF.md vai

Este framework opera em dois repositórios (ver `workflow-rules.yaml`,
seção 1) — o local do handover segue a mesma regra:

1. **Handover para implementação** (SDD já compilada, próximo passo é
   código): escreva em `<repo_do_projeto>/HANDOFF.md`, junto de
   `docs/sdd/`.
2. **Handover entre etapas de documentação** (ex.: RFC/ADR redigidos,
   PRD/Tech Spec ainda pendentes): escreva em
   `<repo_central>/docs/{PROJECT_CODE}/HANDOFF.md`.

Sempre sobrescreva no lugar — não acumule versões antigas de HANDOFF. O
histórico real de decisões já vive nos documentos versionados e no
registry; o HANDOFF é só o mapa de "onde parei agora".

## Template

Use exatamente estes cabeçalhos de seção — a skill `pickup` depende deles
para parsear:

```markdown
# HANDOFF — <rótulo curto da tarefa> (<YYYY-MM-DD HH:MM>)

_Escopo: <repo central | repo do projeto: nome>_

## Goal
<Uma frase: o que esta linha de trabalho está tentando entregar.>

## Status
<O que está pronto, em andamento, não iniciado. Específico — nunca
"progresso feito em X".>

## Ids relacionados
- SDD-{PROJECT_CODE}-{SEQ} — <status atual>
- TS-{PROJECT_CODE}-{SEQ} — <status atual>
- PRD-{PROJECT_CODE}-{SEQ} — <status atual>
(Referencie por id, não copie o conteúdo do documento — quem retomar lê
o original quando precisar de detalhe.)

## Files touched
- `path/to/file.ext` — <razão em uma linha>
(Caminhos relativos ao repositório onde este HANDOFF vive.)

## Key decisions
- Escolhi <X> em vez de <Y> porque <Z>.

## Open threads / blockers
- <Pergunta não resolvida, teste falhando, dependência externa, etc.>

## Next step
<A próxima ação literal. Uma frase específica e executável, não uma lista.>

## Don't do
- <Caminho já descartado ou correção do usuário — para a próxima sessão não repetir.>
```

## Regras

1. **Sem placeholder.** "Status" e "Next step" não aceitam "fazer os
   ajustes pendentes" ou equivalente — mesma proibição do
   `gate_content_quality` (seção 15 de `workflow-rules.yaml`): ação
   literal, específica, executável.
2. **Sem segredo.** Nunca inclua credencial, token, chave de API ou
   conteúdo de `.env`/`.ssh` no HANDOFF.md.
3. **Disco, não conversa.** O resumo vai para o arquivo, não para o chat.
4. **Referencia, não reexplica.** Se o conteúdo já está em `source_docs`,
   nos "Critérios de aceite" da SDD, ou em qualquer documento do
   framework, cite o id — não copie.
5. **Handover magro é válido.** Pouco aconteceu? Escreva mesmo assim — um
   esqueleto vale mais que nada.
6. **Não avança nenhum gate.** Escrever o HANDOFF não substitui o gate de
   verificação de escopo (seção 16) nem aprova nada — se a SDD ainda não
   está `approved`, o HANDOFF registra isso em "Status", não finge que
   está.

## Saída para o usuário

Depois de escrever o arquivo, imprima só isto:

```
HANDOFF escrito: <caminho absoluto>

Próximo: nova sessão/agente + skill pickup.
```

Sem "aqui está o que fizemos", sem resumo adicional em chat — o resumo já
está no arquivo.
