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

Procedimento normativo: `_framework/procedures/handover.md` (a partir da
raiz do repositório) — leia-o inteiro antes de gerar o HANDOFF.md.
