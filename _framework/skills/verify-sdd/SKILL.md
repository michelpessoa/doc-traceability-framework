---
name: verify-sdd
description: >
  Verifica de forma independente se uma SDD foi de fato implementada antes
  de o status virar `implemented`: confere requisito↔código nas duas
  direções, roda cada critério de aceite e registra comando e saída reais,
  e testa se os testes realmente discriminam implementação certa de errada.
  Use quando o usuário disser "verifica a SDD", "pode marcar implemented?",
  "confere se ficou tudo", "roda a verificação de escopo", ou quando uma
  sessão de implementação terminar e o status precisar avançar de
  `approved` para `implemented`. Do NOT use for escrever ou corrigir a
  implementação (isso é da sessão que implementa), para revisar qualidade
  de código em geral (use uma skill de code review), nem para verificar
  documento que não seja SDD.
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

Procedimento normativo: `_framework/procedures/verify-sdd.md` (a partir
da raiz do repositório) — leia-o inteiro antes de verificar.
