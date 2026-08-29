---
name: doc-traceability-framework
description: >
  Gerencia os documentos de decisão de um projeto — Strategy Doc, RFC, ADR,
  SPEC (requisito + desenho) e SDD — com ids, front-matter e registry
  central para rastreabilidade completa, incluindo onboarding de projeto
  legado e o fluxo de incidentes/postmortem. Use when o usuário pedir para
  criar, avaliar, avançar status, rastrear ou validar esses documentos
  ("cria uma RFC pra isso", "precisa de ADR?", "monta a spec pra IA
  implementar", "de onde veio essa decisão?", "abre um incidente", "audita
  os commits"), e SEMPRE antes de implementar código a partir de decisão já
  aprovada ("implementa o que foi decidido", "desenvolve esse ADR") — há
  gates obrigatórios a checar primeiro, e o sizing decide quantos
  documentos a mudança exige. Do NOT use for verificar SDD implementada
  (use `verify-sdd`), passar contexto entre sessões (`handover`/`pickup`),
  nem para documentação de API, README ou changelog, que não são documentos
  de decisão deste framework.
---

# Framework de Documentação & Rastreabilidade para IA

Este framework resolve um problema comum: decisões técnicas e de produto
ficam espalhadas em conversas, docs soltos e memória de time, sem elo
entre "por que decidimos isso" e "o que foi construído". Ele define um
fluxo com portas de decisão explícitas e um registro central que permite,
a qualquer momento, perguntar "de onde veio X" ou "o que depende de Y" e
obter uma resposta confiável — inclusive para projetos que já existiam
antes deste framework, e para o que acontece quando algo quebra em
produção.

A fonte canônica e completa das regras está em
`references/workflow-rules.yaml` — leia esse arquivo quando precisar do
detalhe exato de algum campo, transição de status ou critério do gate.
Este SKILL.md resume o suficiente para operar no dia a dia.

## Modelo de dois repositórios — confirme onde você está antes de agir

- **Repositório central**: guarda `docs/{PROJECT_CODE}/` de todos os
  projetos, mas só os tipos STRAT, RFC, ADR, SPEC, BASE, INC, PM. É o
  histórico institucional completo, de todos os projetos, para sempre.
- **Repositório de cada projeto** (o repositório de código): guarda
  apenas `docs/sdd/` — as SDDs desse projeto nascem e vivem ali, porque é
  o único documento pensado para uma IA ler no momento de implementar.

Se não souber em qual repositório você está operando, pergunte antes de
criar qualquer documento — criar o tipo errado no repositório errado
quebra o modelo inteiro.

## Os 9 tipos de documento

| Tipo | Quando usar | Repositório | Pasta |
|---|---|---|---|
| STRAT (Strategy Doc) | **Opcional.** Direção que precisa existir sem RFC associada | central | `docs/{PROJETO}/00-strategy/` |
| RFC | Antes de decisões relevantes: mudança transversal, custo alto, risco técnico, nova tecnologia, alteração de contrato | central | `docs/{PROJETO}/01-rfc/` |
| ADR | Registro atômico e imutável de UMA decisão de arquitetura | central | `docs/{PROJETO}/02-adr/` |
| SPEC | Requisito (o QUÊ) + desenho executável (o COMO/ONDE) num arquivo só | central | `docs/{PROJETO}/03-spec/` |
| PRD, TS | **Legados** (fundidos em SPEC na v2.0.0). Só em projeto mapeado sob 1.x | central | `03-prd/`, `04-tech-spec/` |
| SDD (Spec Driven Design) | Compilado da SPEC (+ADR), pronto para uma IA implementar código | **projeto** | `docs/sdd/` |
| BASE (Baseline) | Retrato do estado atual, só no onboarding de projeto já existente | central | `docs/{PROJETO}/06-baseline/` |
| INC (Incidente) | Evento em produção, do início ao fechamento | central | `docs/{PROJETO}/07-incidents/` |
| PM (Postmortem) | Análise pós-incidente e action items | central | `docs/{PROJETO}/08-postmortems/` |

Templates prontos (com front-matter) estão em `templates/*.template.md` —
sempre parta de um template, nunca escreva um documento do zero.

## O fluxo principal e o gate de decisão RFC → ADR

```
[SIZING: qual o blast radius?]
  small   ->                                      SDD
  medium  ->                             SPEC ->  SDD
  large   ->        RFC -> [gate] -> ADR -> SPEC ->  SDD
  complex -> STRAT -> RFC -> [gate] -> ADR -> SPEC ->  SDD
SDD (repositório do projeto) -> input direto para a IA implementar
```

**Antes de qualquer coisa, declare o sizing.** `small` = toca ~3 arquivos,
nenhum critério do gate se aplica, comportamento externo não muda → vai
direto para SDD, e o `Refs:` no commit é o vínculo. Um nível acima em
qualquer critério sobe o nível inteiro. A ausência do documento **é** o
registro de que a fase foi pulada — não crie documento para dizer que
outro não era necessário. Declare o nível usado no campo `sizing` do
front-matter. Ver `sizing` em `references/workflow-rules.yaml` (seção 19).

> **TAMANHO DECIDE QUAIS DOCUMENTOS, NUNCA SE A ORDEM VALE.** Uma mudança
> `small` tem menos documento, não menos gate: ordem, branch, qualidade de
> conteúdo e verificação de escopo continuam valendo integralmente.

Nem toda RFC aprovada precisa gerar um ADR. Depois que uma RFC é
aprovada, avalie o gate perguntando se QUALQUER um destes critérios é
verdadeiro: (1) introduz ou altera um padrão arquitetural; (2) decisão de
alto custo ou difícil reversão; (3) trade-off técnico relevante entre
alternativas viáveis; (4) impacto cross-team; (5) troca ou introdução de
tecnologia/vendor/dependência externa relevante. Se algum for verdadeiro,
crie um ADR antes da SPEC; se nenhum for, pule direto para a SPEC.
RFC rejeitada → `archived`, sem downstream. Registre
sempre `decision_gate_criteria_met` no front-matter da RFC.

Quando a SPEC (e o ADR, se existir) estiver `approved`, compile a SDD
**no repositório do projeto** a partir dela — nunca
escreva a SDD do zero. `source_docs` é uma lista de `{id, url}`, porque
os documentos de origem estão no repositório central, não no do projeto.

## Gate obrigatório: nunca implemente antes de SPEC/SDD existirem

> **NENHUMA LINHA DE CÓDIGO ANTES DA SPEC E DA SDD EXISTIREM.**

Red flags — se você se ouvir pensando qualquer uma destas, o gate está
sendo violado agora:

| Racionalização | Realidade |
|---|---|
| "O ADR tem Consequências detalhada, é spec suficiente" | Foi exatamente a falha que originou este gate |
| "Escrevo o documento depois, o código sai igual" | Documento retroativo não guiou nada |
| "É pequeno, não compensa o overhead" | Tamanho decide *quais* documentos, nunca se a ordem vale |
| "O usuário pediu para ir direto" | Avise e peça confirmação explícita — nunca obedeça em silêncio |
| "Já entendi o que fazer, documentar é burocracia" | A próxima sessão não herda o seu entendimento |

Origem: um ADR foi aprovado e a implementação foi direto para o código,
tratando a seção "Consequências" do ADR como spec suficiente — a
especificação e a SDD só foram escritas depois, retroativamente. Ver
`gate_implementation_before_code` em `references/workflow-rules.yaml`
(seção 13).

Se o pedido for "implementa/desenvolve o que já foi decidido" a partir
de um RFC/ADR `approved`, **pare antes de tocar em código**:
1. A SPEC aplicável existe no repositório central (ou o par PRD+TS, em
   projeto legado)? Se não, crie-a primeiro — no nível que o sizing pedir.
2. A SDD correspondente já foi compilada no repositório do projeto? Se
   não, compile-a primeiro.
3. Só então escreva código.

Um ADR sozinho nunca é suficiente, mesmo detalhado. Isto não é um gate
de tempo — pode ser tudo feito na mesma sessão — é um gate de **ordem**.
Se o usuário pedir para pular direto pro código, não obedeça em
silêncio: avise que isso viola o gate e peça confirmação explícita
antes de implementar sem os documentos. Diferente da auditoria (abaixo),
que tolera desvio de terceiros e descobre depois sem bloquear nada, este
gate vale para você mesma — pular a ordem aqui é erro a evitar, não
desvio a tolerar. Única exceção: incidente ativo (`INC` em
`open`/`mitigated`).

## Gate obrigatório: implementação nasce em branch, nunca direto em main

> **NENHUM COMMIT DE IMPLEMENTAÇÃO DIRETO EM MAIN.**

| Racionalização | Realidade |
|---|---|
| "É um commit só, branch é cerimônia" | Sem branch não há CI nem janela de revisão |
| "Estou sozinho, não tem quem revisar" | O PR é onde os checks rodam e os ids ficam vinculados |
| "Já tenho SPEC e SDD, o gate está cumprido" | Gates 13 e 14 são independentes |
| "Faço o merge local e abro o PR depois" | Depois do merge não existe PR a abrir |
| "Abri o PR, então posso mergear" | Mergear precisa de sinal do humano responsável |

Origem: segundo gap do mesmo incidente — mesmo com a especificação e a SDD prontas, o
código foi commitado direto na branch main do repositório de projeto, sem
branch dedicada nem PR. Ver `gate_branch_before_commit` em
`references/workflow-rules.yaml` (seção 14).

Antes do primeiro commit de implementação de uma decisão coberta pelo
framework:
1. Se a branch atual for main/master, crie uma branch nova a partir
   dela, nomeada de forma rastreável ao id de origem (ex.:
   `feat/ADR-EVM-0011-controle-estoque`, `sdd/SDD-EVM-0009`).
2. Commite nessa branch, nunca em main.
3. Leve o resultado a main por PR, referenciando os ids relacionados no
   corpo — não faça merge sozinha sem sinal do humano responsável.

Independente do gate acima (documento antes de código): pode-se cumprir
um e violar o outro. Se o usuário pedir para commitar direto em main,
não obedeça em silêncio: avise que viola o gate e peça confirmação
explícita. Única exceção: incidente ativo, e mesmo aí prefira branch
dedicada (ex.: `hotfix/INC-EVM-0003`) a commit direto em main.

## Ciclo de vida de status

`draft → in_review → approved → implemented|rejected|superseded →
archived` para STRAT, RFC, ADR, SPEC, SDD, BASE e PM. Um ADR
`approved` é imutável — mudança de entendimento gera um **novo** ADR.

INC é a exceção: usa `open → mitigated → resolved → closed`, porque é um
evento operacional, não uma decisão para aprovar.

## Onboarding de projeto já existente

Se o pedido envolver um projeto com código já em produção que nunca usou
este framework, **não invente um processo — use `prompts/onboarding-bootstrap.md`**,
que está bundlado nesta skill. Resumo: uma IA lê o repositório de código,
gera um único `BASE` (retrato do estado atual) e propõe ADRs
reconstruídos (`provenance: reconstructed`, sempre começando em
`in_review`, nunca `approved` sem revisão humana). Só depois dessa
revisão o projeto passa a operar no fluxo normal, com a primeira RFC
começando em `-0001`. Não reconstrua SPEC do passado — o
código já é a especificação do que existe.

## Incidentes e postmortem

Fluxo separado do funil principal — nunca abra uma RFC para tratar um
incidente em andamento.

1. Crie um `INC` com severidade objetiva: SEV1 (indisponibilidade
   total/crítica, perda de dados, incidente de segurança) e SEV2
   (degradação relevante sem workaround) exigem postmortem completo;
   SEV3 (impacto limitado, workaround existe) exige postmortem leve;
   SEV4 (impacto mínimo) tem postmortem opcional.
2. Regra de recorrência: se a mesma causa raiz (`root_cause_key`) se
   repetir em até 90 dias, o postmortem passa a ser obrigatório mesmo em
   SEV4 — um problema pequeno que se repete é, na prática, estrutural.
3. Ao fechar o incidente, crie o `PM` (`source_incident` aponta para o
   INC) com os action items.
4. Triagem de cada action item: ajuste pontual sem nenhum critério do
   gate → SPEC direto, sem RFC; mudança estrutural (atenderia a
   algum critério do gate RFC→ADR) → nova RFC (`relates_to` aponta para
   o PM), seguindo o fluxo normal a partir daí.

## Auditoria de aderência (commits/PRs x registry)

A adesão de todo o time a documentar tudo NUNCA pode ser garantida —
sempre vai haver commit/PR avulso ou hotfix de incidente que muda código
antes de qualquer documento existir. Em vez de tentar impor isso com CI
ou bloqueio de merge, use `prompts/framework-audit.md` **periodicamente,
sob demanda** (não é um gate): ele cruza o histórico de commits do
repositório do projeto com os registries conhecidos, classifica cada
commit em coberto / referência quebrada / não documentado, e para os não
documentados aplica os mesmos 5 critérios do gate RFC→ADR — se algum se
aplica, propõe um ADR reconstruído (igual ao onboarding, nunca aprovado
sem revisão humana, com `tags: [audit]`); se nenhum se aplica, não gera
documento algum. `scripts/registry_tools.py audit` automatiza o
cruzamento a partir de um log de commits.

## IDs, front-matter e registry

- ID: `{TYPE}-{PROJECT_CODE}-{SEQ4}` (ex.: `RFC-CHECKOUT-0007`),
  sequencial por tipo dentro do projeto, nunca reutilizado.
- Front-matter comum: `id, type, title, status, project, owner, created,
  updated, relates_to, supersedes, superseded_by, tags`, mais campos
  específicos do tipo — ver seção 8 de `references/workflow-rules.yaml`.
- Repositório central: `docs/{PROJECT_CODE}/registry.yaml` (fonte da
  verdade) + `docs/{PROJECT_CODE}/registry.md` (gerado). Repositório de
  projeto: `docs/sdd/registry.yaml` + `docs/sdd/registry.md`. Regenere
  a visão legível com `python3 scripts/generate_registry_md.py <docs_dir>`.
- Três ferramentas prontas em `scripts/registry_tools.py`: `validate`
  (detecta ids órfãos, referências quebradas, status inválidos), `trace
  <ID>` (imprime a cadeia completa de rastreabilidade) e `audit
  <git_log_file> <docs_dir...>` (cruza commits com os registries).
- Regra inegociável: ao criar ou alterar qualquer documento, atualize o
  front-matter DO documento e a entrada correspondente no registry certo
  (central ou de projeto) na mesma resposta/tarefa.

## O que fazer em cada pedido comum

**"Cria uma RFC/ADR/SPEC/SDD/Strategy Doc"** — abra o template
do tipo no repositório certo, gere o próximo ID disponível (consultando
o registry), preencha front-matter e conteúdo, devolva a entrada nova
para o registry.

**"Essa RFC precisa de ADR?"** — aplique o gate, mostre quais critérios
se aplicaram e por quê, diga o próximo documento a criar.

**"Implementa/desenvolve o que já foi decidido"** (a partir de RFC/ADR
`approved`) — pare antes de código: confirme que a SPEC existe (crie se
faltarem), confirme SDD compilada no repositório do projeto (compile se
faltar), só então implemente. Ver "Gate obrigatório" acima.

**"Muda o status de X"** — valide contra o ciclo de vida certo (padrão
ou o de INC), atualize documento e registry juntos.

**"Monta a SDD de X"** — confirme a SPEC (e o ADR, se houver)
`approved`, compile no repositório do projeto, preencha `source_docs`
com id+url.

**"Esse projeto antigo precisa entrar no framework"** — use
`prompts/onboarding-bootstrap.md`, não invente um atalho.

**"Abre um incidente" / "registra esse postmortem"** — siga a seção de
incidentes acima.

**"De onde veio X" / "rastreia X"** — percorra `relates_to`,
`parent_*` e `source_docs` (seguindo a `url` quando a cadeia atravessar
repositórios), mostre a cadeia completa.

**"Valida o registry"** — rode `scripts/registry_tools.py validate` ou
aponte manualmente ids órfãos, referências quebradas, status inválido ou
divergência front-matter/registry.

**"Marca a SDD como implementada" / "terminei de implementar"** — rode o
gate de verificação de escopo antes de mudar o status (seção acima).

**"Faz o handover" / "passa isso pro próximo agente"** — use a skill
`handover` (seção acima).

## Gate obrigatório: qualidade de conteúdo da SPEC/SDD

> **NENHUM DOCUMENTO VAI A `in_review` COM PLACEHOLDER OU AMBIGUIDADE PENDENTE.**

| Racionalização | Realidade |
|---|---|
| "'Seguir o padrão do projeto' basta" | Só se você nomear o arquivo que é o padrão |
| "'Tratar erros apropriadamente' cobre as bordas" | É a definição de placeholder |
| "Deixo TBD e preencho quando souber" | Vira TBD esquecido em documento aprovado |
| "A ambiguidade é pequena, decido por conta" | É o que `NEEDS CLARIFICATION` existe para impedir |
| "Critérios juntos no fim dá no mesmo" | Bucket solto não permite verificar cobertura 1:1 |
| "Rodei a checklist mentalmente" | O scan é busca literal. Rode `validate_doc.py` |

Mecanizado por `_framework/scripts/validate_doc.py` — a autorrevisão
continua sua, mas deixou de ser a única checagem.

Os gates de ordem (acima) não garantem qualidade de conteúdo — uma SPEC
`approved` pode ser vago o bastante pra SDD sair genérica. Antes de mover
SPEC ou SDD de `draft` para `in_review`, rode autorrevisão:
todo requisito tem RF-ID + critério de aceite em EARS;
todo contrato técnico (TS) tem assinatura/schema exato + arquivo/módulo
onde vive; casos de borda/erro listados explicitamente, não "tratar
apropriadamente"; nenhum placeholder ("TBD", "definir depois", "seguir
padrão" sem nomear o arquivo); ambiguidade real vira `NEEDS
CLARIFICATION: <pergunta>` em vez de suposição silenciosa — documento não
vai a `approved` com isso pendente; a SDD compilada não adiciona nem
empobrece o que está em `source_docs`. Ver `gate_content_quality` em
`references/workflow-rules.yaml` (seção 15).

## Gate obrigatório: verificação de escopo antes de SDD "implemented"

> **NENHUM `implemented` SEM COMANDO RODADO NESTA SESSÃO E SAÍDA REAL.**

| Racionalização | Realidade |
|---|---|
| "Rodei há pouco, deve estar passando" | Sem saída desta sessão, você não tem evidência |
| "Passou de primeira, está tudo certo" | Teste que nunca falhou pode não testar nada |
| "Já que eu estava ali, refatorei" | Código sem requisito é scope creep. Remova |
| "Toquei o arquivo mas é detalhe" | Ou é escopo não registrado, ou é scope creep |
| "Faltou um requisito pequeno, completo depois" | Faltando = parcial. Mantenha `approved` |
| "O subagente relatou que passou" | Relato próprio não substitui verificação independente |

> **QUEM IMPLEMENTOU NÃO VERIFICA.**

Rode a skill `verify-sdd` numa sessão ou subagente separado da que
implementou: ela confere requisito↔código nas duas direções, roda cada
critério registrando comando e saída reais, e aplica o **sensor de
discriminação** — quebrar o comportamento em espaço descartável e
confirmar que o teste falha. Teste que passa com a implementação quebrada
é ruído verde. Complemento mecânico:
`_framework/scripts/validate_state.py`.

Antes de mover SDD de `approved` para `implemented`: todo requisito
consolidado tem código correspondente (senão mantenha `approved`); todo
arquivo tocado pela implementação está listado na SDD (senão é escopo não
registrado — atualize a SDD — ou scope creep — remova antes do commit);
nenhuma abstração/dependência/flag extra sem requisito na SDD; a tabela
"Evidência de verificação" preenchida com comando+saída reais desta
sessão para cada critério — nunca "deve passar" de memória. Descompasso
encontrado não avança status silenciosamente: relate ao humano e proponha
atualizar a SDD ou remover o código fora de escopo. Ver
`gate_scope_verification` em `references/workflow-rules.yaml` (seção 16).

## Handover/pickup: transferindo contexto entre sessões

Ao terminar planejamento (SDD compilada) antes de implementação rodar em
sessão/agente separado, ou perto de ~45% de uso de contexto com trabalho
pela frente, use a skill `handover` para gerar `HANDOFF.md` (seções
fixas: Goal, Status, Ids relacionados, Files touched, Key decisions, Open
threads/blockers, Next step, Don't do) — referenciando ids do framework
em vez de reescrever conteúdo. A sessão seguinte usa `pickup`: relê do
disco os arquivos de "Files touched" antes de alterar, reconhece em
poucas linhas, e segue direto pro "Next step". Não substitui nenhum gate
— SDD `approved`, branch dedicada e verificação de escopo continuam
obrigatórios. Ver `handover_protocol` em `references/workflow-rules.yaml`
(seção 17).

## Falha de execução vira lição local, não versão nova do framework

> **FALHA DE EXECUÇÃO VIRA LIÇÃO LOCAL, NÃO VERSÃO NOVA DO FRAMEWORK.**

Quando um gate for violado — por você ou por outra sessão — registre em
`LESSONS.md` (repositório do projeto para falha de implementação, central
para falha de documentação): data, o que falhou com o id/sha concreto, a
red flag que teria pegado antes, e a correção. Acumula, não sobrescreve.

Não proponha mudar `workflow-rules.yaml` por causa de uma violação. Uma
lição só vira regra global quando as três valerem juntas: aparece em pelo
menos dois projetos, existe checagem mecânica possível, e cabe como red
flag ou item de validator sem criar seção nova. Ver `lessons_policy` em
`references/workflow-rules.yaml` (seção 18).

## Aplicando isto a um novo projeto

O framework não muda entre projetos — apenas o `PROJECT_CODE`, o
repositório de projeto e o conteúdo dos documentos. `_framework/` existe
em cópia única, no repositório central. Não invente critérios, status ou
campos novos "só para este projeto" — trate como proposta de evolução do
framework e sinalize que `references/workflow-rules.yaml` deveria ser
atualizado primeiro, para não divergir do prompt universal, Cursor e
Copilot, que seguem a mesma fonte.
