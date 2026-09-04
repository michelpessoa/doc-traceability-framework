# Verificação — lote SDD-DTF-0002/0003/0004/0005 (2026-09-04)

Quatro SDDs `approved` cujo código já estava mesclado em `main` (sem
diff isolado) foram verificadas de forma independente na mesma rodada,
por sessões/subagentes separados de quem implementou. Consolidado num
único `validation.md`, seção por SDD, seguindo a convenção do artefato
operacional único (ver `operational_artifacts.validation.md` em
`workflow-rules.yaml`).

---

# Verificação — SDD-DTF-0002

- **Veredito:** PASS (com ressalva no critério 12 — ver "Descompassos
  encontrados"; RF01–RF06 estão todos implementados e verificados com
  evidência fresca e sensor de discriminação. O critério 12 é sobre
  sincronia entre cópias do kit, não sobre a lógica desta SDD, e a
  divergência encontrada é cosmética/pós-implementação — não indica
  requisito sem código. Julgamento explícito: não bloqueio `implemented`
  por isso, mas o descompasso fica registrado para decisão humana sobre
  ressincronizar os dois repositórios.)
- **Diff verificado:** N/A — não há base/head isolados: a implementação
  (commit `5a24ead4299e2572f46edcc041abd2a481d88808`, "feat(framework):
  modo greenfield sem repositório de código") já está mesclada em `main`,
  junto de mudanças posteriores. Verificação feita comparando o estado
  atual do código (`/home/michel/doc-traceability-framework` @ `main`)
  com cada requisito da SPEC-DTF-0002 e cada critério de aceite da
  SDD-DTF-0002.
- **Verificador independente:** sim — sessão separada da que implementou,
  sem leitura do histórico da sessão de implementação; só a SDD, a SPEC
  de origem e o código atual.

## Conformidade com a spec (as duas direções)

- Todo item de "Requisitos consolidados" (RF01–RF06 + 5 casos de borda)
  tem código correspondente identificável — ver tabela de evidência
  abaixo.
- Arquivos do commit `5a24ead`: `AGENTS.md`, `QUICKSTART.md`,
  `_framework/rules/workflow-rules.yaml`, `_framework/scripts/registry_tools.py`,
  `_framework/scripts/render_prompts.py`, `docs/sdd/SDD-DTF-0002.md`,
  `docs/sdd/registry.yaml`. Os cinco primeiros aparecem em "Especificação
  técnica consolidada" da SDD; os dois últimos são a própria SDD e o
  registro dela — esperados, não scope creep.
- **Divergência SPEC → SDD, sem código faltando:** a SPEC (Contratos
  técnicos, item "Produces", e Plano de implementação passo 2) descreve
  `_framework/scripts/validate_doc.py` ganhando
  `RULE_SINCE["repository_status"] = "2.1.0"`. A SDD **não** lista
  `validate_doc.py` em "Especificação técnica consolidada", e de fato o
  arquivo não foi tocado (`grep repository_status validate_doc.py` não
  retorna nada). Investigado: `RULE_SINCE` só governa regras de
  documento (`validate_doc.py`, `validate_state.py`); `repository_status`
  é campo de **registry**, checado por `check_repository_state`, que já é
  estruturalmente seguro para projeto legado — se `repository` está
  preenchido (caso de ABSTRACTCLINIC/EVM), a função retorna sem problema
  nem warning independente de `framework_version`, e nenhum dos dois
  declara `repository_status`. O critério 10 (compatibilidade empírica,
  rodado abaixo) confirma isso na prática. Não é requisito sem código —
  é um mecanismo de compatibilidade diferente do que a SPEC esboçou,
  decisão de consolidação da SDD que cumpre o RNF sem o campo em
  `RULE_SINCE`. Registrado como observação, não como FAIL.
- Nenhuma abstração, dependência, feature flag ou refactor sem requisito
  correspondente encontrado.

## Evidência de verificação (comandos rodados nesta sessão)

| # | Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | RF01 — ausência de `repository` é warning, não erro | `registry_tools.py validate` em registry de teste sem `repository`/`repository_status` | `exit=0`, warning "modo greenfield ASSUMIDO, não declarado" | ver linha do sensor abaixo | sim |
| 2 | RF01 (sensor funcional) — preencher `repository`+`repository_status: active` silencia o warning | mesmo registry + `repository`/`repository_status: active`, revalidado | `exit=0`, **sem** warning de repositório | é o sensor funcional do RF01 | sim |
| 3 | RF02 — contradição `repository_status: none_yet` + `repository` preenchido | registry com os dois campos preenchidos | `exit=1` — "`repository_status: none_yet` contradiz o campo `repository`" | **sensor de discriminação rodado** (ver abaixo) | sim |
| 4 | RF02 — valor inválido de `repository_status` | registry com `repository_status: talvez` | `exit=1` — "valor inválido 'talvez' — aceitos: active, none_yet" | coberto pelo sensor amplo abaixo | sim |
| 5 | RF02 — estado declarado vs. assumido têm mensagens distintas | registry com `repository_status: none_yet` e sem `repository` | `exit=0`, warning "modo greenfield DECLARADO" (texto diferente do #1) | coberto pelo sensor amplo abaixo | sim |
| 6 | RF02 — `repository: ""` equivale a ausente | registry com `repository: ""` | `exit=0`, mesmo warning do #1 | coberto pelo sensor amplo abaixo | sim |
| 7 | RF03, RF04 — textos gerados trazem o modo greenfield | `render_prompts.py && render_prompts.py --check`, depois `grep -c -i greenfield AGENTS.md QUICKSTART.md` | `exit=0` nos dois comandos; 1 ocorrência em cada arquivo | `--check` reprova edição manual (mecanismo herdado de SDD-DTF-0001, não re-testado aqui) | sim |
| 8 | RF03 — instrução condicional no YAML | `python3 -c "...assert 'condicional' in multi_project['instructions']"` | `ok`, sem AssertionError | não rodado isoladamente — leitura de texto, não função | sim |
| 9 | RF05 — pré-condição da auditoria declarada | `python3 -c "...assert 'repository' in str(audit) and 'não' in str(audit)"` | `ok`, sem AssertionError | não rodado isoladamente — leitura de texto, não função | sim |
| 10 | Compatibilidade — projetos já mapeados não reprovam | `framework_check.py --auto` (repositório central, projetos ABSTRACTCLINIC 1.4.0, DTF 2.1.0, EVM 1.6.0) | `exit=0`; "✅ Todas as verificações do framework passaram." (17+11+44 documentos) | validador é o próprio teste | sim |
| 11 | RF04 (limite) — `AGENTS.md` dentro do teto | `wc -l < AGENTS.md` | `119` (limite 120) | medição direta | sim |
| 12 | Paridade entre repositórios | `diff -r --exclude=__pycache__` entre `_framework/` do kit e da cópia no worktree do central; `diff` dos dois `AGENTS.md` | **com saída** — ver "Descompassos" | N/A | **não** (ver abaixo) |

### Sensor de discriminação (rodado nesta sessão)

Alvo: `check_repository_state` em
`_framework/scripts/registry_tools.py`, que cobre os critérios 1, 3, 4,
5 e 6.

1. **Falha pontual** — removida a checagem de contradição
   (`if status == "none_yet": problems.append(...)` dentro do bloco
   `if url:`), mantendo o resto. Revalidado o registry do critério 3
   (`repository_status: none_yet` + `repository` preenchido): passou a
   sair `exit=0` sem problema — o teste **detectou a falha introduzida**.
2. **Falha ampla** — `check_repository_state` alterada para `return [], []`
   logo na primeira linha (checagem inteira desativada). Revalidados os
   registries dos critérios 1, 2, 3, 4, 5, 6: **todos** os que antes
   emitiam warning ou saíam 1 passaram a sair `exit=0` sem warning nem
   problema — confirma que os critérios 1, 3, 4 e 5 dependem
   genuinamente da função, não são ruído verde.
3. Arquivo restaurado via `cp` do backup feito antes da alteração;
   `diff` contra o backup: sem saída (restauração exata). Revalidados os
   registries 1 e 3 no arquivo restaurado: voltaram a sair `exit=0`
   com warning (#1) e `exit=1` com a mensagem de contradição (#3) —
   comportamento original recuperado.

Critérios 7, 8, 9, 10, 11 não têm sensor rodado nesta sessão: 7 já
carrega o mecanismo de detecção do `--check` (herdado e não
re-exercitado); 8 e 9 são leitura de texto YAML via `assert`, sem função
para quebrar; 10 é validação de compatibilidade sobre dados reais, não
uma função isolável; 11 é medição direta de linhas.

## Descompassos encontrados

**Critério 12 (paridade entre repositórios) FALHOU no estado atual.**
`diff -r --exclude=__pycache__` entre
`/home/michel/doc-traceability-framework/_framework` e o `_framework/`
copiado no worktree `agent-a8d1470e819877a74` do repositório central
produz saída em `registry_tools.py`, `render_prompts.py` e outros
arquivos. Inspeção do conteúdo: as diferenças são **só de formatação**
(quebra de linha em chamadas longas, aspas simples vs. duplas, docstring
em uma linha vs. várias) — a lógica de `check_repository_state` é
idêntica byte a byte na comparação semântica (mesmas condições, mesmas
mensagens). `workflow-rules.yaml` (o único arquivo YAML da SDD) está
**idêntico** nos dois repositórios — diff vazio.

Isso não é scope creep nem requisito sem código desta SDD: é drift de
formatação ocorrido **depois** de 2026-08-29 (quando a SDD registrou
"diff -r sem saída" como evidência), provavelmente por um formatador
(estilo `black`) rodado em um dos dois repositórios em commits
posteriores, não relacionados a SDD-DTF-0002. Não achei o commit exato
que introduziu o drift — fora do escopo desta verificação, que é sobre
SDD-DTF-0002, não sobre manutenção de paridade geral do kit.

Nenhum outro descompasso requisito↔código encontrado. `validate_doc.py`
não foi alterado, mas não precisava ser (ver seção "Conformidade com a
spec" acima).

## Lições

- **Paridade entre repositórios não é auto-mantida.** `diff -r` vazio é
  o critério de aceite 12 desta SDD, mas nada no CI ou nos hooks
  re-verifica isso continuamente — qualquer commit posterior em só um
  dos dois repositórios (ex.: rodar um formatter) quebra silenciosamente
  a paridade sem reprovar nada, porque o `diff -r` só roda quando alguém
  lembra de rodar manualmente. Red flag reaproveitável: **"paridade
  verificada uma vez na validation.md" não é "paridade garantida
  depois"** — se a paridade importa de verdade, precisa de um gate
  recorrente (CI ou pre-commit), não só de uma linha na tabela de
  evidência do dia em que a SDD foi escrita.
- **SPEC e SDD podem divergir no "como" sem quebrar o contrato — mas a
  divergência precisa ser investigada, não assumida.** A SPEC descreveu
  `RULE_SINCE["repository_status"]` como mecanismo de compatibilidade; a
  SDD implementou compatibilidade por desenho estrutural da função
  (`check_repository_state` não reprova quem já preenche `repository`).
  Os dois cumprem o RNF, mas só ficou claro depois de ler o código e
  testar `framework_check.py --auto` nos projetos legados — sem isso,
  teria parecido requisito faltando.

---

# Verificação — SDD-DTF-0003

- **Veredito:** PASS
- **Diff verificado:** sem `base..head` isolado (implementação já mesclada
  em `main`, commit `024e243` — `fix(scripts): validate_state respeita a
  não-retroatividade`, `Refs: SDD-DTF-0003, SPEC-DTF-0003`). Verificação
  feita por comparação entre o código atual (`_framework/scripts/validate_state.py`,
  `framework_lib.py`) e cada RF01–RF05 da SPEC-DTF-0003 / SDD-DTF-0003,
  com todos os comandos re-executados nesta sessão.
- **Verificador independente:** sim — subagente de verificação separado da
  sessão que implementou (esta sessão não escreveu o código de
  `validate_state.py`; a tabela de evidência da própria SDD já registra
  "Verificador independente: não" para a rodada original, o que este
  documento substitui).

| Critério (RF) | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 — RF05: EVM valida limpo | `python3 _framework/scripts/validate_state.py /home/michel/projetos/viverMelhor/docs/sdd` | `✅ 9 documento(s) verificados`; exit 0, sem warning | ver linha 2 | sim |
| 2 — RF03 (sensor): elevar versão volta a reprovar | Cópia real de `docs/sdd` do EVM em scratch, `framework_version` trocada de `1.6.0` para `1.7.0`, revalidada | exit 1; **18 problemas** nas 9 SDDs (2 por documento — evidência + escopo, ambas ausentes em todas as 9) | é o próprio sensor: elevar a versão reprova de novo | sim — mecanismo funciona; nota: a tabela original da SDD registrava só 5 SDDs reprovadas, hoje são 9 (ver "Descompassos") |
| 3 — RF02: nenhum documento do EVM tocado | `git -C /home/michel/projetos/viverMelhor status --porcelain docs/sdd` | sem saída | saída vazia é o sinal | sim |
| 4 — RF04: versão indeterminada aplica tudo | `SDD-EVM-0001.md` copiada sozinha (sem `registry.yaml`) para diretório isolado, validada | exit 1 — 2 problemas (evidência + escopo) | par com a linha 1: mesmo documento, resultado oposto conforme versão conhecida/desconhecida | sim |
| 5 — RF03 (regressão): kit continua reprovando o que deve | `SDD-DTF-0001.md` copiada para scratch com `registry.yaml` fixando `framework_version: 2.0.0`, `status` forçado para `implemented`, tabela de evidência esvaziada, validada | exit 1 — 2 problemas (evidência vazia + escopo não marcado) | quebra introduzida de propósito em cópia descartável, fora do repositório | sim |
| 6 — RF01: mecanismo idêntico ao de `validate_doc.py` | `grep -c "RULE_SINCE\|rule_applies\|project_version" _framework/scripts/validate_state.py` | `6` (mínimo 3) | medição direta | sim |
| 7 — Regressão geral | `python3 _framework/scripts/framework_check.py --auto` (repositório central, worktree desta sessão) | `✅ Todas as verificações do framework passaram` — ABSTRACTCLINIC (17 docs), DTF (11 docs), EVM (44 docs no espelho central) | validador é o teste | sim |
| 8 — Paridade entre repositórios | `diff -r --exclude=__pycache__` entre `_framework/` do kit e `_framework/` do worktree central | **saída não vazia** — diferenças em `validate_state.py`, `framework_lib.py` e outros arquivos, todas de formatação (quebra de linha, espaçamento), sem nenhuma diferença semântica | diff não deveria ter saída segundo o critério original | **não** — ver "Descompassos" |
| Sensor de discriminação adicional (procedimento verify-sdd, passo 3) | `applies()` em `check_sdd` forçado a `return True` incondicionalmente (quebra deliberada), revalidado contra o EVM real (1.6.0), depois revertido | Com a quebra: exit 1, mesmos 18 problemas de retroatividade indevida (reproduz o bug que a SDD corrige). Revertido (`git diff --stat` vazio): exit 0 de novo | é o sensor do procedimento — confirma que o mecanismo, e não coincidência, discrimina 1.6.0 de "regra sempre aplicada" | sim |

## Descompassos encontrados

1. **Critério 8 (paridade) não passa hoje.** `diff -r` entre os dois
   `_framework/` não está vazio — mas toda a diferença é de formatação
   (quebra de linha e espaçamento; provável `ruff format`/`black`
   aplicado no kit e não replicado no central). Não há divergência de
   comportamento: `validate_state.py` e `framework_lib.py` são
   semanticamente idênticos nos dois repositórios (mesma lógica, mesmas
   guardas `applies(...)`, mesmo `RULE_SINCE`). A causa provável é o
   commit posterior `13e206d` (`feat(tooling): test runner declarado,
   mypy, ruff format, pre-commit`), que reformatou o kit depois que
   `024e243` (implementação da SDD-DTF-0003) já tinha paridade — o
   commit de tooling não foi replicado no central. Isso é drift
   **posterior** ao escopo desta SDD, não um defeito da própria
   SDD-DTF-0003.
2. **A contagem de SDDs reprovadas no sensor RF03 mudou** (5 na tabela
   original da SDD, 9 nesta verificação). O EVM é um repositório vivo:
   commits posteriores (`bd53854`, `fc7661e`, ...) marcaram mais SDDs
   como `implemented` sem seção de evidência desde que a SDD-DTF-0003 foi
   implementada. Isso é drift do projeto consumidor, não do mecanismo —
   o comportamento (reprovar ao elevar a versão, passar limpo na versão
   real) é exatamente o especificado.

Nenhum requisito (RF01–RF05) ficou sem código correspondente, e nenhum
arquivo fora do declarado em "Especificação técnica consolidada"
(`_framework/scripts/validate_state.py`) foi tocado pelo commit de
implementação — confirmado por `git show --stat 024e243`, que só alterou
`validate_state.py`, `SDD-DTF-0003.md` e `registry.yaml`.

## Lições

- **Critério de aceite "diff vazio entre repositórios" é frágil a
  trabalho não relacionado.** Um commit de tooling (formatação) em um
  repositório, sem replicação imediata no outro, quebra silenciosamente
  um critério de paridade registrado numa SDD já `implemented`. Red flag
  reaproveitável: sempre que uma SDD futura declarar "paridade entre
  repositórios" como critério de aceite, tratar como um invariante
  contínuo (checar no framework_check ou CI), não como uma foto tirada
  uma vez na implementação — senão o critério "passa" no dia em que foi
  escrito e nunca mais é reconferido.
- **Contagens absolutas em evidência ("reprova as mesmas 5 SDDs") datam
  mal quando o alvo do teste é um repositório de projeto vivo.** Preferir
  registrar a propriedade ("volta a reprovar as SDDs sem seção de
  evidência/escopo") em vez do número exato, para que a evidência não
  pareça falsa simplesmente porque o projeto avançou.

---

# Verificação — SDD-DTF-0004

- **Veredito:** PASS
- **Diff verificado:** não há diff base..head isolado — implementação já mesclada em `main` do kit (`doc-traceability-framework`). Verificação feita contra o estado atual do código nesta sessão (HEAD em `main`, working tree limpo no início e no fim).
- **Verificador independente:** sim — esta sessão não implementou o código, não leu histórico da sessão implementadora, e chegou à SDD/SPEC apenas pelos arquivos.

Nota sobre origem: `source_docs` no front-matter de `SDD-DTF-0004.md` confirma `SPEC-DTF-0005` como spec de origem real (a tabela "Documentos originados" de `SPEC-DTF-0005.md` está correta também, ao contrário do aviso recebido — não achei o bug de id trocado citado na tarefa; de todo modo o `source_docs` foi tratado como fonte de verdade).

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 — RF05, RF01: LESSONS.md valida limpo | `cd /home/michel/doc-traceability-central && python3 /home/michel/doc-traceability-framework/_framework/scripts/framework_check.py --auto` | `EXIT: 0`; seção `docs/DTF`: `✅ registry.yaml e documentos consistentes (12 documentos...)`, `✅ 12 documento(s) ok.` (qualidade e escopo) | n/a (evidência direta) | sim |
| 2 — RF04: sem aviso de não registrado para LESSONS.md/HANDOFF.md | mesma saída do critério 1, `grep -n "LESSONS.md\|HANDOFF.md"` sobre a saída completa (todos os projetos, todas as worktrees) | 0 ocorrências de `LESSONS.md`/`HANDOFF.md` em qualquer lugar da saída (nem erro de front-matter, nem aviso de "existe em disco mas não está no registry") | n/a | sim |
| 3 — RF03 (sensor): arquivo fora da lista, sem front-matter, continua reprovando | Criado `examples/central/EXEMPLO/00-strategy/QUALQUER.md` sem front-matter; `python3 _framework/scripts/framework_check.py --auto examples/central/EXEMPLO`; removido em seguida | `EXIT=1`; `❌ 1 problema(s) encontrado(s): .../QUALQUER.md: sem bloco de front-matter.` | **é o sensor** — prova que a exclusão é específica por nome, não uma varredura desligada | sim |
| 4 — RF01: HANDOFF.md também excluído (par do sensor 3) | Criado `examples/central/EXEMPLO/00-strategy/HANDOFF.md` sem front-matter; mesmo comando; removido em seguida | `EXIT=0`; seção EXEMPLO: `✅ 0 documento(s) ok.` (arquivo nem entra na varredura) | par do sensor 3: mesmo tipo de arquivo, resultado oposto conforme esteja na lista — discrimina corretamente | sim |
| 4b — edge case RF01: `lessons.md` minúsculo NÃO é excluído | Criado `examples/central/EXEMPLO/00-strategy/lessons.md` (minúsculo) sem front-matter; mesmo comando; removido em seguida | `EXIT=1`; `.../lessons.md: sem bloco de front-matter.` | confirma exclusão por nome exato, não case-insensitive | sim |
| 5 — RF02: lista derivada do YAML | `cd _framework/scripts && python3 -c "from framework_lib import OPERATIONAL_ARTIFACTS; print(OPERATIONAL_ARTIFACTS)"` | `('LESSONS.md', 'HANDOFF.md', 'validation.md')` — contém os dois nomes da SDD; `validation.md` é uma terceira entrada adicionada por evolução posterior do kit (`capabilities.verify_sdd_independently`), fora do escopo desta SDD, não é regressão | leitura direta | sim |
| 6 — RF02 (fallback): chave ausente cai no fallback do código | `operational_artifacts:` removido temporariamente de `_framework/rules/workflow-rules.yaml` (backup em `/tmp`); `python3 -c "from framework_lib import _derive_constants; print(_derive_constants())"` | `artifacts == ('LESSONS.md', 'HANDOFF.md')` — bate exatamente com `_FALLBACK_OPERATIONAL_ARTIFACTS` | **é o sensor**: com a chave ausente, o sistema tem que continuar funcionando para LESSONS.md/HANDOFF.md via fallback | sim |
| 6b — fallback em uso real (não só import) | Com a chave ainda removida: `framework_check.py --auto examples/central/EXEMPLO` | `EXIT=1`, mas a única falha é `docs/sdd/validation.md: sem bloco de front-matter` — `validation.md` não está no fallback de 2 nomes (é esperado: fallback cobre só o escopo original desta SDD). Nenhuma falha relacionada a LESSONS.md/HANDOFF.md | confirma que o fallback funciona precisamente para o escopo desta SDD, e não "esconde" um terceiro artefato que uma SDD posterior adicionou | sim |
| 7 — Regressão: framework_check --auto nos dois repositórios | Comando do critério 1 (central) + `cd /home/michel/doc-traceability-framework && python3 _framework/scripts/framework_check.py --auto` | Ambos `EXIT=0`, "✅ Todas as verificações do framework passaram." | validador é o teste | sim |
| 8 — Paridade dos dois `_framework/` | `diff -rq --exclude=__pycache__ /home/michel/doc-traceability-framework/_framework/ /home/michel/doc-traceability-central/_framework/` | **Diverge em vários arquivos** (`framework_check.py`, `framework_lib.py`, `registry_tools.py`, `validate_doc.py`, etc. — só formatação/black e evolução de SDDs posteriores, `_framework/scripts/tests` só existe no kit). Isolado o trecho relevante desta SDD: `diff` de `workflow-rules.yaml` = vazio (idêntico); `diff` de `framework_lib.py` = só diferenças de formatação (linhas em branco, quebra de linha), a lógica de `OPERATIONAL_ARTIFACTS`/`_FALLBACK_OPERATIONAL_ARTIFACTS`/`_derive_constants`/`iter_documents` é idêntica nos dois repositórios; `registry_tools.py` idêntico no uso de `iter_documents` | ver "Descompassos" abaixo | parcial — ver nota |

## Descompassos encontrados

- **Critério 8 (paridade) não passa literalmente hoje**, mas não por causa de SDD-DTF-0004: o kit (`doc-traceability-framework`) avançou por várias SDDs posteriores (até SDD-DTF-0015) que ainda não foram sincronizadas para a cópia em `doc-traceability-central/_framework/`. Isso é drift geral entre os dois repositórios, não uma falha desta SDD especificamente — a fatia relevante a esta SDD (`workflow-rules.yaml` completo e a lógica de `operational_artifacts` em `framework_lib.py`/`registry_tools.py`) está em paridade exata (YAML idêntico byte a byte; `framework_lib.py` idêntico exceto formatação). Não bloqueia o veredito PASS desta SDD, mas fica registrado como pendência de sincronização geral dos dois repositórios (fora do escopo de SDD-DTF-0004).
- Nenhum requisito (RF01–RF05) sem código correspondente.
- Nenhum arquivo tocado pela implementação real que não conste em "Especificação técnica consolidada" da SDD (`workflow-rules.yaml`, `framework_lib.py`; `registry_tools.py` corretamente listado como "nenhuma alteração necessária").
- Nenhuma abstração, feature flag ou refactor sem requisito correspondente encontrada.
- `validation.md` como terceiro artefato operacional no YAML é evolução de uma SDD posterior (capacidade `verify_sdd_independently`), não desta SDD — mencionado aqui só para não confundir quem ler a evidência do critério 5/6b.

## Lições

- Rodar `framework_check.py --auto` com uma chave de config temporariamente removida pode disparar sincronização automática do YAML para a cópia em `skills/.../references/` (observado: a remoção de `operational_artifacts` em `_framework/rules/workflow-rules.yaml` propagou para `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml` depois de rodar o comando). Red flag reaproveitável: **ao testar fallback via edição temporária de YAML, sempre conferir `git status` no repositório inteiro antes de considerar a limpeza concluída** — restaurar só o arquivo editado diretamente não é suficiente se o comando de teste tem efeito colateral de sincronização.

---

# Verificação — SDD-DTF-0005

- **Veredito:** PASS
- **Diff verificado:** nenhum diff isolado disponível — implementação já mesclada em `main` (commit `018bd83 feat(docs): porta de entrada única e documentação gerada` no kit). Verificação feita comparando o estado atual do código com cada requisito/critério de aceite da própria SDD.
- **Verificador independente:** sim — sessão separada da que implementou e da que fez a rodada anterior (que gerou o FAIL), sem acesso ao histórico de raciocínio de nenhuma das duas, apenas à SDD, à SPEC-DTF-0004 e ao `validation-SDD-DTF-0005.md` anterior.
- **Repositórios:** kit em `/home/michel/doc-traceability-framework` (worktree `agent-a4f1a0b80436f6ce9`); central em `/home/michel/doc-traceability-central` (leitura direta, sem worktree isolado — nenhuma escrita feita lá nesta sessão).
- **Rodada anterior:** FAIL, por 2 motivos: (1) `docs/README.md` do central citava `../_framework/guides/guia-tecnico.md`, caminho morto; (2) paridade `diff -r` entre os `_framework/` quebrada só por formatação (`ruff format` rodado só no kit, commit `13e206d`, não-bloqueante). Esta rodada reexecuta os dois pontos com comando real e reaproveita, sem reexecutar, os critérios que já haviam passado.

| # | Critério (origem: RF-ID) | Comando rodado | Saída (resumo) | Sensor | Passou? | Reexecutado nesta sessão? |
|---|---|---|---|---|---|---|
| 1 | RF01 — teto do README | `wc -l < README.md` (kit) | `67` (≤ 90) | medição direta | sim | não — reaproveitado do PASS anterior, sem motivo de dúvida |
| 2 | RF01 — três caminhos | `grep -c` dos três alvos em README.md (kit) | `5` (≥ 3) | medição direta | sim | não — reaproveitado |
| 3 | RF02, RF04 — gerados e em dia | `render_prompts.py && render_prompts.py --check` (kit) | todos os alvos em dia/sincronizado; `--check` exit 0 | ver #4 | sim | não — reaproveitado |
| 4 | RF02 (sensor) — edição manual reprova | linha intrusa em `docs/especificacao.md`; `--check`; desfeito com `sed` | `--check` exit 1; após `sed`, exit 0 e arquivo idêntico ao original | **é o sensor**: edição manual do gerado reprova e a reversão restaura o estado exato | sim | não — reaproveitado |
| 5 | RF02 — conteúdo mínimo | `grep -c "Iron Law\|red flag\|sizing\|handover" docs/especificacao.md` | `5` (≥ 4) | medição direta | sim | não — reaproveitado |
| 6 | RF03 — removido nos dois repos | `test ! -f Framework_Documentacao_Rastreabilidade.md` + `find` nos dois repos | exit 0 nos dois; nenhuma ocorrência | ausência é o sinal | sim | não — reaproveitado |
| 7 | RF04 — versão corrente presente | `grep -c "2.1.0" CHANGELOG.md` (kit) | `2` (≥ 1) | medição direta | sim | não — reaproveitado |
| 8 | RF05 — guias com aviso | `ls docs/guias/` e `grep -l "regra canônica" docs/guias/*.md` (kit) | 3 arquivos, os 3 com o aviso | inspeção direta | sim | não — reaproveitado |
| 9 | RF06 — sem link quebrado | `python3 _framework/scripts/check_renderings.py` (kit, esta sessão); `python3 /home/michel/doc-traceability-central/_framework/scripts/check_renderings.py` (central, esta sessão); `grep -n "guia-tecnico\|guias/\|_framework/guides" docs/README.md` (central, esta sessão); `grep -rln "_framework/guides" --include="*.md" .` (central, esta sessão) | Kit: `0` linhas "quebrado" (só 2 avisos não relacionados PRD/TS legado). Central: `0` linhas "quebrado" (mesmos 2 avisos). `docs/README.md` do central agora lê `` `../docs/guias/guia-tecnico.md` `` — caminho existente, correção confirmada. O grep amplo por `_framework/guides` no central só encontra `docs/DTF/LESSONS.md` (linha narrando o histórico da própria migração) e `docs/DTF/03-spec/SPEC-DTF-0004.md` (texto da própria spec descrevendo o `git mv` planejado) — nenhum é referência de link ativa, ambos são prosa histórica sobre o caminho antigo, não uma citação de caminho vigente | **RE-EXECUTADO nesta sessão, sensor original do critério 10 permanece válido** (não refeito de novo — mesmo mecanismo já comprovado na rodada anterior) | **sim** (era o motivo do FAIL; corrigido e confirmado) | **sim — refeito nesta sessão** |
| 10 | RF06 (sensor) — link inexistente reprova | (rodada anterior) link para `docs/nao-existe-sensor.md` acrescentado a README.md; `check_renderings.py`; removido com `sed` | `❌ 1 problema(s)`, exit 1; após `sed`, exit 0, README idêntico ao original | **é o sensor** — confirma que `check_links` detecta o que está no seu escopo (links `[]()`) | sim | não — reaproveitado do PASS anterior; nenhum motivo novo de dúvida (a correção do item 9 foi de prosa em crase, fora do escopo desse sensor, que já era conhecido e registrado como ressalva de cobertura) |
| 11 | Regressão | `framework_check.py --auto` nos dois repositórios | `✅ Todas as verificações do framework passaram` nos dois | validador é o teste | sim | não — reaproveitado |
| 12 | Paridade | `diff -rq --exclude=__pycache__ _framework/ (kit) _framework/ (central)` (esta sessão) + comparação de AST (`ast.dump`) de cada `.py` divergente, dos dois diretórios (`scripts/` e da cópia em `skills/.../scripts/`), nesta sessão | `diff -rq` não vazio — mesmos arquivos já apontados na rodada anterior divergem em bytes (todos os `.py` de `_framework/scripts/` e da cópia na skill). AST idêntica (`ast.dump` igual) em 5 dos 8 arquivos comparados no diretório `scripts/` (`check_commit.py`, `framework_check.py`, `framework_lib.py`, `validate_state.py`, `registry_tools.py`); os 3 restantes (`render_prompts.py`, `generate_registry_md.py`, `validate_doc.py`) têm AST "differs", mas a inspeção manual do diff mostra apenas reflow de docstrings/strings multilinha e reformatação de expressões (`f-string` quebrada em mais/menos linhas, listas literais reindentadas) — nenhuma mudança de token de lógica, operador, nome ou ordem de execução localizada. Consistente com a causa raiz já identificada (`ruff format`, commit `13e206d`, só no kit) | comparação de árvore + AST; nenhuma diferença semântica confirmada, apenas formatação | **não bloqueante — confirmado cosmético** (mesmo tratamento já dado nas SDDs irmãs 0002/0003/0004) | **sim — refeito nesta sessão** |

## Descompassos encontrados

Nenhum bloqueante. O único descompasso da rodada anterior (item 9 — RF06,
referência morta em `docs/README.md` do central) foi corrigido em sessão
separada anterior a esta verificação e a correção foi confirmada nesta
sessão com comando real: `grep` já não encontra a referência morta, e as
duas ocorrências remanescentes de `_framework/guides` no central são
prosa histórica (LESSONS.md e a própria SPEC-DTF-0004 narrando a
migração), não citações de caminho vigente.

A paridade quebrada entre `_framework/` do kit e do central (item 12)
permanece não vazia em `diff -rq`, mas — como já registrado nas SDDs
irmãs 0002/0003/0004 — é drift de formatação (`ruff format`, commit
`13e206d`, posterior à implementação desta SDD, aplicado só no kit), não
uma falha desta SDD. Nesta sessão, além de reafirmar a causa raiz, a
diferença foi checada por igualdade de AST em todos os arquivos
divergentes: 5 de 8 arquivos batem exatamente em AST; os 3 restantes
diferem só por reflow de string/docstring e reindentação de expressão,
sem qualquer alteração de lógica localizada na inspeção manual do diff.
Tratado como não-bloqueante, do mesmo jeito que nas SDDs irmãs — fica
registrado para o humano decidir se e quando sincronizar os dois
repositórios.

## Lições

- **Correção de referência morta em prosa (crase) resolve o RF06, mas o
  checker automatizado continua sem cobrir esse caso.** `check_links`
  ainda só varre `[texto](alvo)`; a lição já estava registrada na rodada
  anterior — reafirmada aqui porque a correção manual (não o checker) é
  que fechou o item 9.
- **Paridade "ponto no tempo" precisa ser revalidada por conteúdo, não só
  por presença de diff.** Quando um critério de aceite tipo "diff vazio
  entre dois diretórios espelhados" é reverificado meses depois e falha,
  comparar AST (ou equivalente semântico) antes de escalar como
  bloqueante evita tratar reformatação de ferramenta (`ruff format`,
  `black`, etc.) como regressão real. Vale para qualquer SDD futura que
  reverifique paridade de árvore entre os dois repositórios.

## Recomendação ao humano

Nenhuma pendente. PASS. `SDD-DTF-0005.md` e `docs/sdd/registry.yaml`
avançados para `implemented` nesta sessão. O drift de formatação do item
12 segue não-bloqueante e não corrigido (é trabalho de sincronização, não
desta verificação) — mesmo tratamento dado às SDDs irmãs 0002/0003/0004.

