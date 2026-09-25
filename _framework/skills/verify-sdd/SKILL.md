---
name: verify-sdd
description: >
  Verifica de forma independente se uma SDD foi implementada antes de virar `implemented`: confere requisito e código nas duas direções, roda cada critério de aceite registrando comando e saída reais e testa se os testes discriminam. Use when pedirem "verifica a SDD", "pode marcar implemented?" ou a implementação terminar. Do NOT use for escrever ou corrigir a implementação, code review geral, nem documento que não seja SDD.
---

# Verificação independente de SDD

> QUEM IMPLEMENTOU NÃO VERIFICA.

Checklist mínimo, antes de abrir o procedimento inteiro:

- Diff fixo (`<merge-base>..HEAD`), nunca `origin/main` direto.
- Requisito↔código nas duas direções — faltou algo, mantenha `approved`.
- Cada critério de aceite rodado nesta sessão, saída real na tabela da SDD.
- Sensor de discriminação por critério com teste automatizado (quebrar,
  confirmar que falha, restaurar) — coluna `Sensor` da tabela nunca vazia,
  mecanizado por `validate_state.py`.
- Teto de 3 rodadas de correção-e-reverificação; na 3ª sem `PASS`,
  escalone ao humano em vez de tentar de novo.

Procedimento normativo: `_framework/procedures/verify-sdd.md` na raiz do repositório. De qualquer diretório dentro dele: `cat "$(git rev-parse --show-toplevel)/_framework/procedures/verify-sdd.md"`. Leia-o inteiro antes de agir. Se o comando falhar ou o arquivo não existir, pergunte ao usuário onde está o repositório do kit ou do central; não improvise o procedimento.
