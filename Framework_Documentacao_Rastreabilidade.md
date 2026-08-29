# Framework de Documentação & Rastreabilidade para IA

**Especificação — sempre na versão atual do framework**

Este documento acompanha `_framework/rules/workflow-rules.yaml` →
`framework.version`. Não existem cópias versionadas dele: quando o
framework evolui, este arquivo é atualizado no mesmo PR, e o histórico de
o que mudou em cada versão fica em [`CHANGELOG.md`](CHANGELOG.md).

Em caso de divergência entre este texto e
`_framework/rules/workflow-rules.yaml`, **o YAML manda** — ele é a fonte
canônica que prompts, skills e automações consomem. Este documento existe
para explicar o desenho e o porquê das regras; o YAML existe para
executá-las sem ambiguidade.

## 1. Objetivo

Criar, registrar e rastrear os documentos de decisão de um projeto de
forma reaplicável entre projetos, com skills e prompts que produzem o
mesmo resultado em qualquer ferramenta de IA (Claude, Cursor, Copilot,
ChatGPT, Gemini).

O problema que ele resolve: decisões técnicas e de produto ficam
espalhadas em conversas, docs soltos e memória de time, sem elo entre "por
que decidimos isso" e "o que foi construído". O framework define portas de
decisão explícitas e um registro central que permite, a qualquer momento,
perguntar "de onde veio X" ou "o que depende de Y" e obter uma resposta
confiável — inclusive para projetos que já existiam antes dele, e para o
que acontece quando algo quebra em produção.

## 2. Modelo de dois repositórios

O framework nunca assume um único repositório. Um **repositório central**
guarda a cópia única de `_framework/` (regras, templates, prompts, skills,
scripts, guias) e `docs/{PROJECT_CODE}/` de todos os projetos — mas
somente os tipos Strategy Doc, RFC, ADR, SPEC, Baseline, Incidente e
Postmortem. Cada projeto tem também seu próprio **repositório
de código**, e é ali — e somente ali — que a SDD nasce e vive, em
`docs/sdd/`, porque é o único documento pensado para ser lido por uma IA
no momento de implementar.

```mermaid
flowchart LR
    subgraph C["REPOSITÓRIO CENTRAL — histórico institucional de todos os projetos"]
        direction TB
        CT["STRAT · RFC · ADR · SPEC · BASE · INC · PM"]
        CL["<i>legado (1.x): PRD · TS</i>"]
        CF["_framework/ — cópia única: regras, templates, prompts, skills, scripts"]
        CR["docs/{PROJECT_CODE}/registry.yaml — um por projeto"]
    end
    subgraph P["REPOSITÓRIO DO PROJETO — onde o código vive"]
        direction TB
        PS["SDD — docs/sdd/"]
        PR["docs/sdd/registry.yaml — só SDD"]
    end
    CT -->|"source_docs: {id, url}"| PS
    PS --> IA["IA implementadora<br/>(Claude Code, Cursor, ...)"]

    classDef central fill:#eef2ff,stroke:#4338ca,color:#1e1b4b
    classDef projeto fill:#ecfdf5,stroke:#047857,color:#064e3b
    class CT,CL,CF,CR central
    class PS,PR,IA projeto
```

A SDD é o único tipo que vive no repositório de código, porque é o único
escrito para ser lido por uma IA no momento de implementar. Como ela
atravessa repositórios, cada `source_docs` carrega `id` **e** `url` — sem
a url a cadeia quebra na fronteira.

Como SPEC e ADR vivem no repositório central mas a SDD que os consolida
vive no repositório do projeto, toda referência de uma SDD aos
seus documentos de origem (`source_docs`) carrega não só o `id`, mas a URL
completa do arquivo no repositório central — sem isso a cadeia de
rastreabilidade quebraria ao atravessar repositórios.

A URL do repositório de código de cada projeto fica registrada no campo
`repository`, no topo de `docs/{PROJECT_CODE}/registry.yaml` — é a única
fonte que a auditoria (seção 6) consulta para saber qual repositório ler,
e nunca deve ser adivinhada.

## 3. Fluxo principal e gate de decisão

```mermaid
flowchart LR
    S{{"SIZING<br/>qual o blast radius?"}}
    S -->|small<br/>~3 arquivos| SDD
    S -->|medium| SPEC
    S -->|large / complex| RFC

    STRAT["STRAT<br/><i>opcional</i>"] -.->|complex| RFC
    RFC["RFC"] --> G{"Gate:<br/>exige ADR?"}
    G -->|sim| ADR["ADR"]
    G -->|não| SPEC
    G -->|rejeitada| ARC["rejected → archived<br/><i>nenhum downstream</i>"]
    ADR --> SPEC["SPEC<br/><i>Parte 1: requisito</i><br/><i>Parte 2: desenho</i>"]
    SPEC --> SDD["SDD<br/><i>repositório do projeto</i>"]
    SDD --> IA["IA implementa<br/>(Claude Code, Cursor, ...)"]
    ADR -.->|impacto estratégico| STRAT

    classDef central fill:#1f2937,color:#fff,stroke:#111827
    classDef projeto fill:#15803d,color:#fff,stroke:#14532d
    classDef gate fill:#2563eb,color:#fff,stroke:#1e40af
    classDef morto fill:#b91c1c,color:#fff,stroke:#7f1d1d
    class STRAT,RFC,ADR,SPEC central
    class SDD,IA projeto
    class S,G gate
    class ARC morto
```

O nível de sizing sai dos mesmos 5 critérios do gate RFC → ADR. A
**ausência** de um documento é o registro de que aquela fase foi pulada —
não se cria documento para declarar que outro não era necessário.

Leitura do fluxo: uma RFC (opcionalmente originada de um Strategy Doc) é
aprovada; o gate decide se um ADR é necessário; a SPEC segue, com ou sem
ADR; e a SDD, compilada a partir dela, é o artefato final consumido por
ferramentas de IA de implementação, criada no repositório do projeto.

Antes disso, porém, vem uma pergunta que até a v1.7.0 não existia: **de
que tamanho é esta mudança?** O funil não é fixo.

| Nível | Critério | Documentos |
|---|---|---|
| `small` | Toca ~3 arquivos, nenhum critério do gate se aplica, comportamento externo não muda | SDD |
| `medium` | Feature contida num domínio, nenhum critério do gate se aplica | SPEC, SDD |
| `large` | Pelo menos 1 critério do gate se aplica | RFC, ADR, SPEC, SDD |
| `complex` | Vários critérios, ou cross-team, ou precisa de direção estratégica ainda inexistente | STRAT, RFC, ADR, SPEC, SDD |

A régua não é nova: são os mesmos 5 critérios do gate RFC → ADR da tabela
abaixo, que já eram o teste de significância do framework. O que mudou é
que agora eles decidem também quantos documentos existem, não apenas se um
ADR é necessário.

A **ausência** de um artefato é o registro de que aquela fase foi pulada
deliberadamente — não se cria documento para declarar que outro documento
não era necessário. Quem quiser auditar lê o campo `sizing` no
front-matter da SPEC ou da SDD.

Isto nasceu de um custo medido, não de teoria: escrever RFC, PRD e Tech
Spec para configurar ESLint, Prettier, husky e um workflow de CI num
projeto de uma pessoa consumiu cerca de 620 linhas de documento. Documento
que ninguém lê não é rastreabilidade, é cerimônia — e cerimônia
desacredita o framework inteiro, inclusive nas partes em que ele paga.

Tamanho decide **quais** documentos existem, nunca se a ordem vale. Uma
mudança `small` tem menos documento, não menos gate.

| # | Critério do gate RFC → ADR | Exemplo |
|---|---|---|
| 1 | Introduz ou altera um padrão arquitetural | Novo serviço, mudança de topologia |
| 2 | Decisão de alto custo ou difícil reversão | Rollback caro, lento ou impossível |
| 3 | Trade-off técnico relevante entre alternativas | Mais de uma opção viável, prós/contras a registrar |
| 4 | Impacto cross-team | Mais de um time/domínio diretamente afetado |
| 5 | Troca ou introdução de tecnologia/vendor relevante | Novo banco de dados, provedor cloud, linguagem, lib crítica |

Nem toda RFC aprovada precisa gerar um ADR: se **qualquer** critério se
aplica, o ADR vem antes da SPEC; se **nenhum** se aplica, o trabalho segue
direto para a SPEC. O resultado fica registrado em
`requires_adr` e `decision_gate_criteria_met` no front-matter da RFC — é o
que torna a decisão auditável depois. RFC rejeitada vai para `archived`,
sem nenhum documento downstream.

## 4. Onboarding de projeto já existente

Quando um projeto com código já em produção, mas sem nenhum histórico
neste framework, precisa ser incorporado, ele passa por um procedimento de
duas fases, executado uma única vez.

### 4.1 Fase 1 — Levantamento de baseline

Uma IA lê o repositório de código existente (stack, estrutura,
integrações, dívidas técnicas visíveis) e produz um único documento
Baseline (BASE), que é um retrato do estado atual — não uma decisão. A
partir dele, a IA propõe um ADR para cada decisão de arquitetura que
consegue inferir do código, sempre com `provenance=reconstructed` e status
inicial `in_review` — nunca `approved` direto, porque é inferência sobre
código, não relato de uma decisão presenciada. Uma pessoa do time revisa e
confirma ou corrige cada ADR proposto antes de qualquer um ser aprovado.

Não se reconstrói SPEC do que já foi construído: o código já é a
especificação do que existe, e o valor de reconstruir está no "porquê"
(ADR), não no "como".

### 4.2 Fase 2 — Cutover

Concluída e revisada a Fase 1, o projeto passa a operar exatamente como um
projeto novo: a próxima demanda real vira `RFC-{PROJETO}-0001`, segue o
gate normalmente, e a primeira SDD nasce no repositório do projeto.

Este procedimento está implementado em
`_framework/prompts/onboarding-bootstrap.md`, usado uma única vez por
projeto no dia da adoção.

## 5. Incidentes e postmortem

Fluxo apartado do funil principal: não se abre uma RFC para tratar um
incidente em andamento. Um Incidente (INC) usa um ciclo de vida
operacional próprio — `open → mitigated → resolved → closed` — em vez do
ciclo padrão de aprovação, porque não é uma decisão a aprovar, é um evento
a acompanhar.

| Severidade | Critério | Postmortem |
|---|---|---|
| SEV1 — Crítico | Indisponibilidade total/crítica, perda de dados, incidente de segurança confirmado | Obrigatório, completo |
| SEV2 — Alto | Degradação relevante de função importante, sem workaround viável | Obrigatório, completo |
| SEV3 — Moderado | Impacto limitado, workaround razoável existe | Obrigatório, leve |
| SEV4 — Baixo | Impacto mínimo/cosmético, sem efeito perceptível ao usuário final | Opcional |

Regra de recorrência: independentemente da severidade individual, se a
mesma causa raiz se repetir dentro de uma janela de 90 dias, o postmortem
passa a ser obrigatório — um problema de baixo impacto que se repete
constantemente é, na prática, um problema estrutural.

O Postmortem (PM) segue o ciclo de vida padrão do framework (é um
documento analítico, não operacional) e cada action item é triado: um
ajuste pontual sem nenhum critério do gate aplicável entra pelo sizing
como `small` ou `medium`; uma mudança estrutural (que atenderia a algum critério do gate
RFC→ADR) vira uma nova RFC, referenciando o postmortem de origem, e segue
o fluxo normal a partir daí — reaproveitando a mesma régua de decisão em
vez de criar uma nova.

## 6. Auditoria de aderência (commits/PRs x registry)

O framework nunca assumiu que todo código nasce de um documento aprovado —
na prática sempre existem commits e PRs avulsos (hotfix fora de incidente,
ajuste de dependência, refactor pontual) e correções feitas durante um
incidente, onde o código muda antes de qualquer documento existir. Como a
adesão de todo o time à convenção de referenciar documentos em commits/PRs
**não pode ser garantida**, a resposta não é impor isso com CI ou bloqueio
de merge — é assumir que vai haver desvio e transformá-lo em achado
revisável, sem travar ninguém.

A auditoria é sob demanda (não é gate, não roda em CI): lê o histórico de
commits/PRs do repositório do projeto desde a última auditoria, cruza cada
mensagem com os ids conhecidos nos registries relevantes, e classifica em
três grupos — **coberto** (referencia um id existente), **referência
quebrada** (cita um id que não existe em nenhum registry, provável erro de
digitação) e **não documentado** (nenhum id na mensagem). Para os não
documentados, aplica os mesmos 5 critérios do gate RFC→ADR da seção 3: se
algum se aplica, propõe um ADR reconstruído — mesmas regras do onboarding,
`provenance: reconstructed`, `status: in_review`, nunca aprovado sem
revisão humana, com `tags: [audit]` no registry para distinguir de um
bootstrap inicial. Se nenhum critério se aplica, não gera documento algum.

O script
`_framework/scripts/registry_tools.py audit <git_log_file> <docs_dir...>`
automatiza o cruzamento entre um log de commits e um ou mais registries, e
o prompt `_framework/prompts/framework-audit.md` implementa o procedimento
completo para uso com qualquer ferramenta de IA.

## 7. Os quatro gates obrigatórios

A auditoria da seção 6 é a rede de segurança para quem **não** opera sob o
framework — tolera desvio e descobre depois. Os gates desta seção são o
oposto: valem para a IA (ou pessoa) que conhece a regra e está operando
sob ela. Para essa, pular a ordem não é desvio tolerável a ser descoberto
depois, é erro a evitar antes de acontecer. Nenhum deles é imposto por CI;
todos são verificados no momento em que o trabalho acontece.

Cada um nasceu de uma falha real de uso, não de teoria. E cada um tem
agora três camadas, porque só a primeira nunca bastou:

1. Uma **lei de uma linha**, em caixa alta, antes de qualquer explicação.
2. Uma **tabela de red flags** — as racionalizações literais que a IA usa
   para escapar do gate. O alvo não é ensinar a regra, que ela já
   entende; é impedir que ela se convença a não seguir.
3. Um **validator** que checa mecanicamente o que dá para checar de fora.

| Gate | Lei | Mecanizado por |
|---|---|---|
| Implementação | Nenhuma linha de código antes da SPEC e da SDD existirem | — (é ordem; verificada no momento) |
| Branch | Nenhum commit de implementação direto em main | branch protection do repositório |
| Qualidade de conteúdo | Nenhum documento vai a `in_review` com placeholder ou ambiguidade pendente | `validate_doc.py` |
| Verificação de escopo | Nenhum `implemented` sem comando rodado nesta sessão e saída real | `validate_state.py` + skill `verify-sdd` |

A terceira camada é o que faltava até a v1.7.0, e a ausência dela era
medível: os gates 15 e 16 existiam há uma versão inteira e, no momento em
que foram mecanizados, 11 de 11 PRDs de um projeto real estavam sem RF-ID
e 5 SDDs estavam `implemented` sem uma única linha de evidência. Um gate
que só a própria IA verifica é um gate que ela decide quando aplicar.

Os validators respeitam a não-retroatividade: cada exigência declara em
que versão entrou, e só vale para projeto cujo `registry.yaml` declara
`framework_version` igual ou posterior. Evoluir o kit nunca reprova
documento de projeto já mapeado.

### 7.1 Nenhuma implementação pula SPEC/SDD

Um ADR foi aprovado e a IA implementadora foi direto para o código,
tratando a seção "Consequências" do ADR como especificação suficiente —
SPEC e SDD só foram escritos depois, retroativamente, quando o
dono do projeto percebeu a lacuna.

Antes de criar ou editar qualquer arquivo de código de implementação
(schema, migration, service, endpoint, UI) para uma decisão já coberta por
RFC/ADR aprovado: a SPEC aplicável precisa existir no
repositório central (criá-los primeiro, se faltarem) e a SDD precisa estar
compilada no repositório do projeto (compilá-la primeiro, se faltar). Só
então o código.

É gate de **ordem**, não de tempo: tudo pode acontecer na mesma sessão. Um
ADR sozinho, mesmo com "Consequências" detalhada, nunca é especificação
suficiente — ADR registra o *porquê*, a SPEC registra o *o quê* (Parte 1)
e o *como/onde* (Parte 2), e a SDD compila os dois para consumo direto de
IA.

### 7.2 Implementação nasce em branch, nunca direto em main

Segundo gap do mesmo incidente: mesmo depois de SPEC/SDD existirem, o
código foi commitado direto na branch main do repositório de projeto, sem
branch dedicada nem PR. Sem isolamento não há checks de CI nem janela de
revisão antes de integrar, e um commit ruim já nasce em main.

Antes do primeiro commit de implementação: branch nova a partir de main,
nomeada de forma rastreável ao id de origem (`feat/ADR-EVM-0011-controle-estoque`,
`sdd/SDD-EVM-0009`), com chegada a main por PR referenciando os ids
relacionados — nunca merge local direto nem `push --force`. A IA pode
abrir o PR, mas não mergeá-lo sozinha sem sinal do humano responsável.

Ter especificação (7.1) não dispensa isolamento (7.2): são problemas
independentes, e dá para cumprir um e violar o outro.

### 7.3 Qualidade de conteúdo da SPEC/SDD

Os dois gates anteriores garantem **ordem**; nenhum garante **conteúdo**.
Uma SPEC pode existir, estar `approved`, e ainda assim ser
vagos o bastante para que a SDD compilada a partir deles saia genérica. A
qualidade observada nas SDDs de projetos reais veio de disciplina
espontânea da sessão que compilou, não de exigência do framework — ou
seja, não era reprodutível.

Antes de mover uma SPEC ou SDD de `draft` para `in_review`:

- Todo requisito funcional (SPEC, Parte 1) tem **RF-ID próprio e critério
  de aceite em notação EARS** — não um bucket de critérios desconectado
  dos requisitos. EARS dá a gramática que "verificável objetivamente" não
  dava sozinho: `O sistema deve X`; `Quando <gatilho>, o sistema deve X`;
  `Enquanto <estado>, o sistema deve X`; `Se <condição>, então o sistema
  deve X`; `Onde <capacidade>, o sistema deve X`.
- Todo contrato técnico (SPEC, Parte 2) tem **assinatura/schema exato e
  aponta o arquivo/módulo onde vive** — não prosa livre do tipo "no
  serviço de X". Contratos declaram o que consomem e o que produzem, com
  nomes e tipos exatos.
- Todo caminho de erro ou borda relevante está **listado
  explicitamente** — "tratar erros apropriadamente" é placeholder, não
  conteúdo.
- Nenhum placeholder: "TBD", "definir depois", "ajustar conforme
  necessário", "seguir o padrão do projeto" sem nomear o arquivo padrão.
- Ambiguidade real vira `NEEDS CLARIFICATION: <pergunta objetiva>` em vez
  de suposição silenciosa da IA. Um documento não pode ir para `approved`
  com essa marcação pendente.

A checagem é **autorrevisão**: quem redige o documento roda a checklist do
rodapé do próprio template como último passo antes de propor a mudança de
status — cobertura (todo requisito de origem tem contrapartida), scan de
placeholder (busca literal pelos termos banidos) e consistência de nome
(um contrato chamado `criarPedido` numa seção e `criarNovoPedido` noutra é
bug de documento, não estilo).

### 7.4 Verificação de escopo antes de SDD `implemented`

Nada garantia que o código entregue fosse exatamente o que a SDD pediu —
nem mais (scope creep silencioso: abstração, config ou refactor "já que
estava ali") nem menos (requisito que ficou de fora sem ninguém perceber).
E `implemented` não podia ser confiado sem evidência: um checklist marcado
`[x]` de memória não prova nada.

Antes de mover uma SDD de `approved` para `implemented`:

- Todo requisito consolidado tem código correspondente. Faltou algum? A
  SDD não está implementada, está parcial — mantém `approved`.
- Todo arquivo tocado pela implementação está listado na SDD. Arquivo fora
  da lista é uma de duas coisas, nunca silenciosa: escopo que faltou
  registrar (atualize a SDD) ou scope creep (remova antes do commit).
- Nenhuma abstração, dependência, feature flag ou refactor sem requisito
  correspondente.
- A tabela de **evidência de verificação** é preenchida com o comando de
  fato executado naquela sessão e a saída real. "Deve passar" ou resultado
  assumido de memória não satisfaz; na dúvida sobre quando rodou pela
  última vez, roda de novo.

Descompasso encontrado não avança o status em silêncio: relata-se ao
humano responsável e propõe-se atualizar a SDD ou remover o código fora de
escopo — a decisão de qual caminho é dele, não da IA.

Duas coisas que a v2.0.0 acrescentou aqui, ambas porque a versão anterior
pedia que a IA se auto-aprovasse:

**Quem implementou não verifica.** A checagem roda pela skill `verify-sdd`
numa sessão ou subagente separado, sem herdar o histórico da sessão de
implementação. Quem escreveu o código tem o resultado como conclusão
desejada, e o custo de rodar tudo de novo parece desnecessário justamente
quando mais importa. Quando for inevitável ser a mesma sessão, isso é
declarado na tabela de evidência — verificação não independente é dado
mais fraco, e o humano precisa saber disso.

**Sensor de discriminação.** Um teste que nunca falhou pode não estar
testando nada. Para cada critério com teste automatizado: introduzir uma
falha de comportamento real em espaço descartável (stash, cópia ou
worktree — nunca um commit), confirmar que o teste **falha**, e desfazer.
Teste que passa com a implementação quebrada é ruído verde, e a tabela de
evidência sem isso mede apenas "o comando rodou", não "o teste
discrimina".

## 8. Passagem de contexto entre sessões (handover/pickup)

O fluxo separa com frequência quem planeja (compila SPEC/SDD) de quem
implementa — inclusive quando é a mesma pessoa, em sessões de IA
diferentes para não estourar o orçamento de contexto de uma sessão só. Sem
um formato padrão de passagem, a sessão implementadora ou reconstrói
contexto lendo tudo de novo, ou herda uma sessão inchada.

A skill `handover` gera um `HANDOFF.md` de seções fixas — `Goal`,
`Status`, `Ids relacionados`, `Files touched`, `Key decisions`, `Open
threads / blockers`, `Next step`, `Don't do` — no repositório de projeto
(handover de implementação) ou no central (handover entre etapas de
documentação). Ele **referencia ids** do framework em vez de reescrever o
conteúdo dos documentos: quem retoma lê o original quando precisar de
detalhe. Sobrescreve no lugar, porque o histórico real são os documentos
versionados e os PRs, não uma pilha de handoffs antigos.

A skill `pickup` faz o caminho inverso: confirma o status real dos ids
citados (não confia no que o HANDOFF anotou), relê do disco os arquivos
que vai alterar — o arquivo pode ter mudado desde o handover — reconhece
em poucas linhas e executa o "Next step".

Handover não pula nenhum gate da seção 7: a SDD ainda precisa estar
`approved` antes de implementar, a branch dedicada continua obrigatória, e
a verificação de escopo roda antes de `implemented`, independente de
quantas sessões passaram no meio.

## 9. Lições locais e congelamento do núcleo

Entre a v1.4.0 e a v1.7.0 — duas semanas — cada falha de execução de um
agente virou uma seção nova e obrigatória das regras, válida para todos os
projetos, para sempre. Uma falha local produziu lei global quatro vezes
seguidas; o arquivo de regras dobrou de tamanho e a taxa de falha não
caiu. O problema não era a ausência da regra seguinte: era não existir
lugar para uma lição morar sem virar regra.

A partir da v2.0.0, violação de gate é registrada num `LESSONS.md` do
projeto — data, o que falhou com o id ou o sha concreto, a red flag que
teria pegado antes, e a correção adotada. Diferente do `HANDOFF.md`, que
sobrescreve, este acumula: o histórico é o valor. Entrada genérica do tipo
"ter mais atenção" não é lição; se não vira red flag ou checagem de
script, é lamento.

Uma lição só sobe para regra global quando as três condições valem juntas:
a mesma falha aparece no `LESSONS.md` de pelo menos **dois** projetos
(uma ocorrência é acidente, duas é padrão); existe uma **checagem
mecânica** possível (se a única forma de impor é pedir boa-fé em prosa, a
evidência é de que isso já não funcionou); e a regra cabe como red flag ou
item de validator existente, **sem criar seção nova**.

Com isso, o núcleo é tratado como estável. Versão nova passa a existir
para mudança de desenho — tipo novo, fluxo novo, mecanização nova —, não
para reagir a cada violação observada.

## 10. Exemplo ponta a ponta

O kit inclui três cenários de exemplo, todos validados com
`registry_tools.py validate` e `trace`. São **registries de
demonstração**: trazem as entradas que representam cada cenário, com o
campo `path` apontando para onde os documentos ficariam num repositório
real, sem incluir os arquivos `.md` de cada documento.

- `examples/central/EXEMPLO/` — projeto novo, demonstrando os dois
  caminhos do gate: `RFC-EXEMPLO-0001` (exige ADR) e `RFC-EXEMPLO-0002`
  (não exige, segue direto para a SPEC).
- `examples/project-repo-checkout/docs/sdd/` — repositório de projeto
  correspondente, com as duas SDDs e `source_docs` apontando via
  `id`+`url` para o repositório central.
- `examples/central/LEGADO/` — projeto já existente sendo incorporado:
  `BASE-LEGADO-0001` e um ADR reconstruído aprovado, um incidente SEV2
  (`INC-LEGADO-0001`), o postmortem correspondente (`PM-LEGADO-0001`) e o
  cutover: `RFC-LEGADO-0001` nascendo de um action item estrutural do
  postmortem.

O rastreio de `RFC-LEGADO-0001` confirma a cadeia completa:
`RFC-LEGADO-0001 → PM-LEGADO-0001 → INC-LEGADO-0001` — ou seja, dá para
responder "por que esta RFC existe" com uma resposta real, não uma
reconstrução de memória.
