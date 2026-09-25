---
name: pickup
description: >
  Retoma trabalho a partir de um HANDOFF.md da skill `handover`, confirmando o status real dos ids e relendo do disco os arquivos a alterar, sem confiar no que o handoff anotou. Use when pedirem "retomar", "continuar de onde parei", "ler o handoff", ou a sessão começar com um HANDOFF.md no repositório. Do NOT use for criar handoff (`handover`), verificar SDD (`verify-sdd`), nem retomar sem HANDOFF.md (leia o registry).
---

# Pickup

Checklist mínimo, antes de abrir o procedimento inteiro:

- Confirme o status real de cada id citado — não confie no status
  anotado no HANDOFF, ele pode estar desatualizado.
- Releia do disco todo arquivo de "Files touched" antes de alterar.
- Respeite "Don't do" — são caminhos já descartados.
- Se o "Next step" for implementar e a SDD não estiver `approved`, isso
  é bloqueio, mesmo que o HANDOFF sugira continuar.

Procedimento normativo: `_framework/procedures/pickup.md` na raiz do repositório. De qualquer diretório dentro dele: `cat "$(git rev-parse --show-toplevel)/_framework/procedures/pickup.md"`. Leia-o inteiro antes de agir. Se o comando falhar ou o arquivo não existir, pergunte ao usuário onde está o repositório do kit ou do central; não improvise o procedimento.
