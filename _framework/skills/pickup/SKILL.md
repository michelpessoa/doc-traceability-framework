---
name: pickup
description: >
  Retoma uma sessão do Framework de Documentação & Rastreabilidade a
  partir de um HANDOFF.md deixado pela skill `handover` — tipicamente uma
  sessão de implementação retomando o trabalho de uma sessão de
  planejamento (PRD/Tech Spec/SDD), ou um agente continuando o que outro
  começou. Use quando o usuário pedir para "retomar", "continuar de onde
  parei", "ler o handoff", ou no início de uma sessão nova que encontra
  um HANDOFF.md no repositório. Complementa a skill `handover`.
---

# Pickup

Lê o `HANDOFF.md` deixado por uma sessão anterior e retoma o trabalho sem
herdar a sessão inteira — só o necessário do arquivo, mais os documentos
do framework que ele referencia por id.

## Onde procurar

Segue o mesmo local de `handover_protocol` (`workflow-rules.yaml`, seção
17): raiz do repositório de projeto (junto de `docs/sdd/`) quando o
handover foi de planejamento para implementação, ou
`docs/{PROJECT_CODE}/HANDOFF.md` no repositório central quando foi entre
etapas de documentação. Se não souber qual, procure nos dois antes de
assumir que não existe.

Se não encontrar nenhum HANDOFF.md, diga isso explicitamente e pergunte
ao usuário o que ele quer retomar — não invente contexto.

## Ao carregar o HANDOFF

1. **Parseie as seções fixas**: `Goal`, `Status`, `Ids relacionados`,
   `Files touched`, `Key decisions`, `Open threads / blockers`,
   `Next step`, `Don't do`. Se o arquivo estiver malformado ou faltando
   seção obrigatória, diga o que falta e pare.
2. **Siga os ids antes de agir.** Para cada id em "Ids relacionados",
   confirme o status atual do documento (não confie no status anotado no
   HANDOFF — ele pode estar desatualizado). Se o HANDOFF aponta para uma
   SDD que ainda não está `approved` e o "Next step" é implementar, isso
   é bloqueio — não prossiga sem resolver, mesmo que o HANDOFF sugira
   continuar.
3. **Releia do disco.** Todo arquivo listado em "Files touched" que você
   for alterar precisa ser lido no estado atual antes de editar — o
   HANDOFF é um resumo do momento em que foi escrito, o arquivo pode ter
   mudado desde então. Disco vence resumo.
4. **Reconheça em poucas linhas.** No máximo: Goal (uma linha), o que já
   está pronto (uma linha), Next step (uma linha). Não reexplique
   decisões, arquivos ou bloqueios — eles já estão registrados.
5. **Respeite "Don't do".** São caminhos já descartados. Não tente de
   novo sem perguntar antes.
6. **Prossiga.** Execute o "Next step" diretamente — quem chamou `pickup`
   já decidiu continuar, não pergunte "posso continuar?". Só pare para
   perguntar se o "Next step" for genuinamente ambíguo, e aí faça uma
   pergunta específica, não genérica.

## Regras

1. **Disco vence resumo.** Se o estado dos arquivos divergiu do que o
   HANDOFF descreve, confie nos arquivos e mencione a divergência
   brevemente antes de prosseguir.
2. **Gates continuam valendo.** Retomar via `pickup` não pula nenhum gate
   do framework — se o "Next step" é implementar e a SDD não está
   `approved`, ou se o commit ainda não tem branch dedicada, aplique o
   gate correspondente (seções 13/14/16 de `workflow-rules.yaml`) antes
   de agir.
3. **Não apague o HANDOFF.** Quem decide quando o HANDOFF.md some é o
   usuário, não esta skill.
4. **Não encadeie handover automaticamente** ao final — se a nova sessão
   também precisar passar o bastão adiante, isso é uma invocação separada
   da skill `handover`.
