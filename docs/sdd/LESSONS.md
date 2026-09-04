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

---

## 2026-09-04 — `validate_state.py` reprova SDD-DTF-0002 por falso positivo na checagem de "resultado assumido"

**O que falhou:** verificação independente da `SDD-DTF-0002` (agente
`sdd-verifier`) rodou todos os critérios com comando real e obteve PASS,
mas `python3 _framework/scripts/validate_state.py docs/sdd` reprova o
documento: "linha de evidência com resultado assumido ('assumido') —
evidence_standard exige comando rodado e saída real". A regra existe pra
pegar evidência preguiçosa ("assumo que passa"), mas o gate casa a
palavra "assumido" em qualquer lugar da linha da tabela — inclusive
dentro do texto citado de uma mensagem de warning real que o próprio
requisito (RF02) manda o sistema emitir ("o estado foi **assumido**, não
declarado"). A palavra descreve o comportamento correto do sistema sob
teste, não a qualidade da evidência do verificador.

**Correção aplicada:** nenhuma no validador — decisão do dono do projeto
(risco aceito conscientemente: alterar `validate_state.py` pra esse caso
não vale o custo/risco de mexer num gate compartilhado por causa de uma
linha). A linha #1 da evidência de `SDD-DTF-0002.md` foi reescrita para
descrever o resultado sem citar a string literal do warning
(`"...ASSUMIDO..."`), preservando o mesmo fato verificado. `status:
implemented` mantido — a evidência sempre foi real, só a redação
disparava o gate.

**Correção futura possível, não adotada:** a checagem de "resultado
assumido" em `validate_state.py` poderia ignorar texto entre aspas/crases
ao varrer a coluna de resultado — mesma classe de falso-negativo que RF06
de `SDD-DTF-0005` já expôs em `check_links` (regex de sintaxe, não de
intenção). Fica registrado caso o mesmo padrão se repita em outra SDD.

**Escopo desta lição:** um projeto, uma ocorrência. Mesma política de
`lessons_policy` acima — não vira SPEC até repetir.
