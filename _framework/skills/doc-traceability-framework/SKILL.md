---
name: doc-traceability-framework
description: >
  Gerencia o fluxo de documentos de decisão de um projeto — Strategy Doc,
  RFC, ADR, PRD, Tech Spec e SDD — com IDs, front-matter e um registry
  central para rastreabilidade completa, incluindo onboarding de projetos
  já existentes (Baseline + ADRs reconstruídos) e o fluxo separado de
  incidentes/postmortem. Use sempre que o usuário pedir para criar,
  avaliar, avançar status, rastrear ou validar qualquer um desses
  documentos, mesmo sem dizer o nome exato ("cria uma RFC pra isso",
  "essa proposta precisa de ADR?", "monta a spec pra IA implementar", "de
  onde veio essa decisão?", "esse projeto antigo precisa entrar no
  framework", "abre um incidente", "registra esse postmortem", "audita se
  os commits têm documento por trás"). Também use para gate RFC→ADR,
  legado, severidade/postmortem de incidentes, ou auditoria periódica de
  aderência entre commits/PRs e o registry. USE TAMBÉM antes de
  implementar qualquer código a partir de uma decisão já aprovada neste
  framework ("implementa o que já foi decidido", "desenvolve esse ADR",
  "bota pra rodar essa RFC") — há dois gates obrigatórios (PRD/TS/SDD
  antes de código, e branch dedicada + PR em vez de commit direto em
  main) que precisam ser checados primeiro. Aplicável a qualquer
  projeto.
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
  projetos, mas só os tipos STRAT, RFC, ADR, PRD, TS, BASE, INC, PM. É o
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
| STRAT (Strategy Doc) | Uma ideia/direção ainda pouco amadurecida | central | `docs/{PROJETO}/00-strategy/` |
| RFC | Antes de decisões relevantes: mudança transversal, custo alto, risco técnico, nova tecnologia, alteração de contrato | central | `docs/{PROJETO}/01-rfc/` |
| ADR | Registro atômico e imutável de UMA decisão de arquitetura | central | `docs/{PROJETO}/02-adr/` |
| PRD | Requisitos de produto a construir | central | `docs/{PROJETO}/03-prd/` |
| TS (Tech Spec) | Desenho executável: contratos técnicos, plano de rollout | central | `docs/{PROJETO}/04-tech-spec/` |
| SDD (Spec Driven Design) | Compilado de PRD+TS(+ADR), pronto para uma IA implementar código | **projeto** | `docs/sdd/` |
| BASE (Baseline) | Retrato do estado atual, só no onboarding de projeto já existente | central | `docs/{PROJETO}/06-baseline/` |
| INC (Incidente) | Evento em produção, do início ao fechamento | central | `docs/{PROJETO}/07-incidents/` |
| PM (Postmortem) | Análise pós-incidente e action items | central | `docs/{PROJETO}/08-postmortems/` |

Templates prontos (com front-matter) estão em `templates/*.template.md` —
sempre parta de um template, nunca escreva um documento do zero.

## O fluxo principal e o gate de decisão RFC → ADR

```
Strategy Doc -> RFC -> [GATE: exige ADR?]
    -> SIM -> ADR -> PRD + Tech Spec -> SDD (repositório do projeto)
    -> NÃO ------------> PRD + Tech Spec -> SDD (repositório do projeto)
SDD -> input direto para a IA que vai implementar o código
```

Nem toda RFC aprovada precisa gerar um ADR. Depois que uma RFC é
aprovada, avalie o gate perguntando se QUALQUER um destes critérios é
verdadeiro: (1) introduz ou altera um padrão arquitetural; (2) decisão de
alto custo ou difícil reversão; (3) trade-off técnico relevante entre
alternativas viáveis; (4) impacto cross-team; (5) troca ou introdução de
tecnologia/vendor/dependência externa relevante. Se algum for verdadeiro,
crie um ADR antes de PRD/Tech Spec; se nenhum for, pule direto para
PRD/Tech Spec. RFC rejeitada → `archived`, sem downstream. Registre
sempre `decision_gate_criteria_met` no front-matter da RFC.

Quando PRD e Tech Spec (e o ADR, se existir) estiverem `approved`,
compile a SDD **no repositório do projeto** a partir deles — nunca
escreva a SDD do zero. `source_docs` é uma lista de `{id, url}`, porque
os documentos de origem estão no repositório central, não no do projeto.

## Gate obrigatório: nunca implemente antes de PRD/TS/SDD existirem

Regra não-opcional, adicionada depois de um incidente real de uso deste
framework: um ADR foi aprovado e a implementação foi direto para o
código, tratando a seção "Consequências" do ADR como spec suficiente —
PRD, Tech Spec e SDD só foram escritos depois, retroativamente. Ver
`gate_implementation_before_code` em `references/workflow-rules.yaml`
(seção 13).

Se o pedido for "implementa/desenvolve o que já foi decidido" a partir
de um RFC/ADR `approved`, **pare antes de tocar em código**:
1. PRD e/ou Tech Spec aplicáveis existem no repositório central? Se não,
   crie-os primeiro.
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

Segundo gap do mesmo incidente: mesmo com PRD/TS/SDD prontos, o código
foi commitado direto na branch main do repositório de projeto, sem
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
archived` para STRAT, RFC, ADR, PRD, TS, SDD, BASE e PM. Um ADR
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
começando em `-0001`. Não reconstrua PRD ou Tech Spec do passado — o
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
   gate → PRD/Tech Spec direto, sem RFC; mudança estrutural (atenderia a
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

**"Cria uma RFC/ADR/PRD/Tech Spec/SDD/Strategy Doc"** — abra o template
do tipo no repositório certo, gere o próximo ID disponível (consultando
o registry), preencha front-matter e conteúdo, devolva a entrada nova
para o registry.

**"Essa RFC precisa de ADR?"** — aplique o gate, mostre quais critérios
se aplicaram e por quê, diga o próximo documento a criar.

**"Implementa/desenvolve o que já foi decidido"** (a partir de RFC/ADR
`approved`) — pare antes de código: confirme PRD/TS existem (crie se
faltarem), confirme SDD compilada no repositório do projeto (compile se
faltar), só então implemente. Ver "Gate obrigatório" acima.

**"Muda o status de X"** — valide contra o ciclo de vida certo (padrão
ou o de INC), atualize documento e registry juntos.

**"Monta a SDD de X"** — confirme PRD/Tech Spec (e ADR, se houver)
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

## Aplicando isto a um novo projeto

O framework não muda entre projetos — apenas o `PROJECT_CODE`, o
repositório de projeto e o conteúdo dos documentos. `_framework/` existe
em cópia única, no repositório central. Não invente critérios, status ou
campos novos "só para este projeto" — trate como proposta de evolução do
framework e sinalize que `references/workflow-rules.yaml` deveria ser
atualizado primeiro, para não divergir do prompt universal, Cursor e
Copilot, que seguem a mesma fonte.
