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

---

## 2026-09-14 — Descompassos das verificações independentes de SDD-DTF-0018 a 0023

Oito descompassos apontados pelos verificadores (`validation.md`,
seções de SDD-DTF-0018, 0019, 0020, 0021 e 0023). Nenhum reprovou
implementação. **Todos os 8 resolvidos em 2026-09-15** (PRs #69–#73);
ver "Resolvido" em cada item.

### 1. SDD-DTF-0018 — RF4 em prosa diverge do pseudocódigo

**O que falhou:** RF4 diz "sem coluna reconhecível como **comando** →
linha inteira"; o pseudocódigo (e o código, commit `16ae117`) só cai para
a linha inteira quando não há **nenhuma** coluna comando/saída/passou.
Com cabeçalho `# | Critério | Saída | Passou?`, "n/a" em Critério deixa de
ser apontado. O teste só cobria `a | b | c`, onde as duas leituras
coincidem.

**Red flag:** requisito em prosa e pseudocódigo descrevendo o mesmo
fallback com gatilhos diferentes, sem teste que separe as duas leituras.

**Correção proposta:** ajustar o texto do RF4 ao implementado (edição de
SDD `implemented`, sem mudança de código).

**Resolvido:** PR #69 — RF4 corrigido em `docs/sdd/SDD-DTF-0018.md`.

### 2. `table_rows` conta linha de bloco de código como linha de tabela

**O que falhou:** ao validar `SDD-DTF-0018`, `validate_state.py` acusou 6
critérios para 5 linhas de evidência: a continuação `  | grep -c ...` do
bloco C2, dentro de bloco cercado, virou critério. Contornado só
editorialmente (pipe no fim da linha anterior).

**Red flag:** parser markdown por "linha começa com `|`" sem saber de
blocos cercados.

**Correção proposta:** SDD small para `table_with_header` ignorar linhas
dentro de blocos cercados. Até lá, em SDD, pipe de shell no fim da linha.

**Resolvido:** PR #70, `SDD-DTF-0024` (`approved`) — `table_with_header`
ignora linhas dentro de blocos cercados.

### 3. SDD-DTF-0020 — `check_hooks` reprova comando válido em forma de shell

**O que falhou:** a regra 3 exige que a string inteira de `command`
comece por `${CLAUDE_PROJECT_DIR}/`. Reprova `"python3
${CLAUDE_PROJECT_DIR}/..."` e `"python3 \"$CLAUDE_PROJECT_DIR\"/..."` (forma
do exemplo da documentação oficial), e mascara a regra 4 (script
inexistente). O kit não é afetado (gerador usa `args`); projeto com
settings escrito à mão teria CI reprovado.

**Red flag:** especificação técnica ("sem começar por") mais estreita que
o RF06 ("sem `${CLAUDE_PROJECT_DIR}/`"), validada só contra o settings
gerado.

**Correção proposta:** decidir entre (a) RF06 exigir só a forma sem shell
ou (b) SDD small tokenizando com `shlex` e aceitando as variantes.

**Resolvido:** decisão (b), PR #73, `SDD-DTF-0027` (`approved`) —
`check_hooks.py` tokeniza `command` com `shlex.split()`.

### 4. SDD-DTF-0021 — justificativa do here-string está errada

**O que falhou:** a SDD (e o HANDOFF da sessão) afirmam que em `printf |
while` o `exit 2` "só sai do subshell". Executado: com `set -e` o status
do `while` (último do pipe) encerra o script com exit 2, com ou sem
`pipefail`. A mutação para pipe é equivalente e nenhum teste falha; só o
`grep` do critério 3 protege a escolha.

**Red flag:** afirmação sobre semântica de shell escrita sem rodar no
cabeçalho real do script; sensor que não consegue falhar indica mutação
equivalente.

**Correção proposta:** corrigir a frase na SDD para "sem `set -e` o exit
sairia só do subshell; o here-string não depende disso". Here-string
mantido.

**Resolvido:** PR #69 — justificativa corrigida em
`docs/sdd/SDD-DTF-0021.md`.

### 5. SDD-DTF-0021 — caso de borda com `;` dentro de aspas não bloqueia

**O que falhou:** a SDD afirma que `git commit -m "a; git push origin
main"` "vira segmento e bloqueia". Executado: exit 0 — o segmento termina
com aspas (`git push origin main"`) e nenhum padrão casa. Idem `bash -c
"cd x; git push origin main"`. O `.githooks/pre-push` continua barrando o
push real.

**Red flag:** caso de borda com resultado afirmado fora da tabela de
testes.

**Correção proposta (decisão do dono):** (a) corrigir o caso de borda na
SDD como limite aceito, coberto pelo pre-push; ou (b) SDD small apertando
os padrões com fronteira que aceite aspas, com teste dedicado.

**Resolvido:** decisão (a), PR #69 — tabela de casos de borda de
`docs/sdd/SDD-DTF-0021.md` corrigida (dizia "bloqueia", comportamento
real é "não bloqueia"), documentado como limite aceito coberto por
`.githooks/pre-push`. Sem mudança de código.

### 6. `verify-sdd.md` sugere `git stash` como espaço descartável

**O que falhou:** o passo 3 do procedimento sugere `git stash` para
mutações de sensor; o stash é compartilhado entre worktrees e sessões. Em
2026-09-14 havia até 3 verificadores em paralelo no mesmo repositório.

**Red flag:** instrução de procedimento que assume um único checkout.

**Correção proposta:** SDD small trocando por "restaurar por cópia ou
`git checkout -- <arquivo>` na própria worktree".

**Resolvido:** PR #72, `SDD-DTF-0026` (`approved`) —
`_framework/procedures/verify-sdd.md` não recomenda mais `git stash`.

### 7. SDD-DTF-0023 — blocos C3 e C5 usam `origin/main` como estado "antes"

**O que falhou:** depois do merge do PR #67, `origin/main` já contém a
implementação e os blocos deixam de discriminar. O verificador rodou com
a base `756c83b`.

**Red flag:** critério de aceite comparativo ancorado em ref móvel.

**Correção proposta:** em SDD nova, bloco "antes/depois" usa o SHA da
base registrado na redação (ou `git merge-base`), nunca `origin/main`.
Candidata a red flag no template de SDD se repetir.

**Resolvido:** PR #72, `SDD-DTF-0026` (`approved`) — mesma SDD do item 6
(mesmo arquivo, `verify-sdd.md`); instrução agora exige SHA fixo.

### 8. SDD-DTF-0023 — `test_discover.py` não pega duas mutações

**O que falhou:** podar `worktrees` em qualquer nível (em vez de só
`root/.claude/worktrees`) e tirar `.git` da poda passam no teste. O
código está correto (conferido à mão); a tabela de testes da SDD não
previu esses casos.

**Red flag:** requisito com duas restrições ("só relativo a `root`",
"não desce em `.git`") e fixture que só exercita uma delas.

**Correção proposta:** junto com a próxima SDD que tocar `discover`,
acrescentar `docs/worktrees/registry.yaml` (deve ser descoberto) e
`.git/x/registry.yaml` (não deve) à fixture.

**Resolvido:** PR #71, `SDD-DTF-0025` (`approved`) — fixture reforçada em
`test_discover.py`, discriminação das 2 mutações confirmada.

**Escopo:** um projeto (kit), uma ocorrência cada. Nenhum vira regra
global (`lessons_policy`).

**Nota sobre status das SDDs de correção (0024–0027):** código de todas
já mergeado em `main`. A `SDD-DTF-0027` passou por verificação
independente em 2026-09-15 e está `implemented` (ver seção abaixo e
`validation.md`); 0024–0026 seguem `approved`, aguardando verificação
independente em sessão separada (quem implementou não verifica).

---

## 2026-09-15 — SDD-DTF-0027: risco nomeado na SDD sem teste que o reprove

**O que falhou:** nada no comportamento. A verificação independente da
`SDD-DTF-0027` (PR #73, `f8ee505`) confirmou os 6 critérios de aceite com
comando e saída reais, e confirmou à mão que a regra 3 de `check_hooks.py`
não afrouxou (`python3 _framework/scripts/hook.py`,
`$CLAUDE_PROJECT_DIR_FALSO/_framework/...` e
`CLAUDE_PROJECT_DIR_framework/...` continuam reprovados). O que falhou foi
o sensor: a mutação que troca o `startswith` por uma checagem de substring
— exatamente o afrouxamento que a SDD proíbe em "Riscos" e em "Instruções
específicas para a IA implementadora" — **passa nos 11 testes**. O único
caso negativo da tabela de testes não contém a substring
`CLAUDE_PROJECT_DIR`, então não discrimina.

**Red flag que teria pegado antes:** risco descrito em prosa com uma
implementação errada concreta ("não use `"CLAUDE_PROJECT_DIR" in token`")
e nenhuma linha correspondente na tabela de testes da SDD. Enquanto o
risco só vive na prosa, quem for editar a regra depois não tem freio
automático. Mesma família do item 8 de 2026-09-14 (`test_discover.py`).

**Correção proposta:** na próxima SDD que tocar `check_hooks.py`,
acrescentar um caso com `command: "python3 $CLAUDE_PROJECT_DIR_FALSO/_framework/scripts/hook.py"`
esperando 1 problema. Não bloqueia o `implemented` da 0027: todo RF tem
código conforme e a tabela de testes aprovada foi cumprida à letra.

**Escopo:** um projeto (kit), uma ocorrência. Não vira regra global em
`workflow-rules.yaml` (`lessons_policy` exige dois projetos).
