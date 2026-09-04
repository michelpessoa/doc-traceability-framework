# LESSONS.md — repositório `doc-traceability-framework`

Acumula, não sobrescreve. Ver `lessons_policy` em
`_framework/rules/workflow-rules.yaml` (seção 18).

---

## 2026-09-04 — SDD-DTF-0009 marcada `implemented` sem verificador independente

**O que falhou:** a sessão que implementou `SDD-DTF-0009` (commit
`9cf2a57`, PR #32 do kit) preencheu a tabela "Evidência de verificação" e
avançou o status de `approved` para `implemented` na mesma sessão,
registrando "**Verificador independente:** não — mesma sessão que
implementou." O gate `gate_scope_verification` (seção 16) exige sessão ou
subagente separado — "QUEM IMPLEMENTOU NÃO VERIFICA" — justamente porque
quem escreveu o código tem o resultado como conclusão desejada.

**Red flag que teria pegado antes:** a própria tabela nomeia a violação
("mesma sessão que implementou") em vez de interromper e pedir uma
segunda sessão/subagente antes de mudar o status — o racional "já rodei
os comandos, deu certo" (linha da tabela de red flags do gate) foi
seguido sem o freio.

**Correção:** sessão separada (esta) rodou de novo os 11 critérios de
aceite listados em `SDD-DTF-0009.md`, com comando e saída reais,
incluindo os sensores negativos (critérios 6, 7 e 9 — edição manual,
arquivo ausente, `artifact_type` inválido). Todos os 11 passaram; o
resultado da implementação está correto. `status: implemented` mantido —
o problema era só de processo, não de conteúdo, e a verificação
independente feita agora fecha a lacuna.

**Escopo desta lição:** um projeto (kit `doc-traceability-framework`),
uma ocorrência. Não vira regra global em `workflow-rules.yaml` ainda —
`lessons_policy` exige repetição em pelo menos dois projetos antes disso.
