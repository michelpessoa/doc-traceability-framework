---
name: handover
description: >
  Gera HANDOFF.md para transferir contexto entre sessões ou agentes, referenciando ids em vez de reescrever documentos. Use when o planejamento terminou e outra sessão vai implementar, o contexto passa de ~45% com trabalho pela frente, ou pedirem "faz o handover". Do NOT use for retomar handoff existente (`pickup`), documentação permanente, nem para dispensar gate: a SDD segue precisando de `approved`.
---

# Handover

Checklist mínimo, antes de abrir o procedimento inteiro:

- Todas as seções fixas presentes: Goal, Status, Ids relacionados, Files
  touched, Key decisions, Open threads/blockers, Next step, Don't do.
- Referencie ids do framework em vez de reescrever o conteúdo deles.
- Não substitui gate algum — SDD `approved` e branch dedicada continuam
  obrigatórios do lado de quem retomar.

Procedimento normativo: `_framework/procedures/handover.md` na raiz do repositório. De qualquer diretório dentro dele: `cat "$(git rev-parse --show-toplevel)/_framework/procedures/handover.md"`. Leia-o inteiro antes de agir. Se o comando falhar ou o arquivo não existir, pergunte ao usuário onde está o repositório do kit ou do central; não improvise o procedimento.
