---
name: pickup
description: >
  Retoma o trabalho a partir de um HANDOFF.md deixado pela skill
  `handover`, confirmando o status real dos ids citados e relendo do disco
  os arquivos que vai alterar, em vez de confiar no que o handoff anotou.
  Use when o usuário pedir para "retomar", "continuar de onde parei", "ler
  o handoff", ou no início de uma sessão que encontra um HANDOFF.md no
  repositório. Do NOT use for criar um handoff (use `handover`), para
  verificar uma SDD antes de `implemented` (use `verify-sdd`), nem para
  retomar trabalho sem HANDOFF.md — nesse caso leia o registry e os
  documentos diretamente.
---

# Pickup

Procedimento normativo: `_framework/procedures/pickup.md` (a partir da
raiz do repositório) — leia-o inteiro antes de retomar o trabalho.
