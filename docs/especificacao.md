# Especificação do framework (v2.1.0)

Arquivo GERADO por `_framework/scripts/render_prompts.py` a partir de
`_framework/rules/workflow-rules.yaml`. Não edite à mão — o CI reprova.
Para narrativa e exemplos, veja `docs/guias/`. Para começar a usar,
`QUICKSTART.md`. Para operar como IA, `AGENTS.md`.

## Modelo de dois repositórios

**`central_repo`** — Fonte da verdade de todas as decisões, de todos os projetos, para sempre.

- _framework/
- docs/{PROJECT_CODE}/ (STRAT, RFC, ADR, SPEC, BASE, INC, PM; PRD e TS em projeto legado)
- registry: `docs/{PROJECT_CODE}/registry.yaml (um por projeto, não um arquivo único gigante)`

**`project_repo`** — Onde a IA de implementação lê a SDD e onde o rastreio de código (commits/PRs) acontece.

- docs/sdd/ (SDDs deste projeto)
- registry: `docs/sdd/registry.yaml (local, mesmo schema, escopo só SDD)`

**Referência entre repositórios** — Como o repositório de projeto não tem os arquivos do repositório central presentes localmente, toda referência de uma SDD a um documento de origem (SPEC, ADR) DEVE incluir não só o id mas também a URL completa do arquivo no repositório central — sem isso, a rastreabilidade quebra ao atravessar repositórios. Ver frontmatter_schema.type_specific_fields.SDD.source_docs.

## Núcleo canônico (framework 2.1.0)

Gerado de `_framework/rules/workflow-rules.yaml`. Em caso de
divergência com qualquer texto abaixo ou acima, o YAML manda.

### Leis inegociáveis

- **NENHUMA LINHA DE CÓDIGO ANTES DA SPEC E DA SDD EXISTIREM.** (`gate_implementation_before_code`)
- **NENHUM COMMIT DE IMPLEMENTAÇÃO DIRETO EM MAIN.** (`gate_branch_before_commit`)
- **NENHUM DOCUMENTO VAI A in_review COM PLACEHOLDER OU AMBIGUIDADE PENDENTE.** (`gate_content_quality`)
- **NENHUM implemented SEM COMANDO RODADO NESTA SESSÃO E SAÍDA REAL.** (`gate_scope_verification`)
- **FALHA DE EXECUÇÃO VIRA LIÇÃO LOCAL, NÃO VERSÃO NOVA DO FRAMEWORK.** (`lessons_policy`)
- **TAMANHO DECIDE QUAIS DOCUMENTOS, NUNCA SE A ORDEM VALE.** (`sizing`)

### Tipos de documento

| Tipo | Repositório | Pasta | Situação |
|---|---|---|---|
| STRAT | central | `docs/{PROJECT_CODE}/00-strategy` | opcional |
| RFC | central | `docs/{PROJECT_CODE}/01-rfc` | ativo |
| ADR | central | `docs/{PROJECT_CODE}/02-adr` | ativo |
| SPEC | central | `docs/{PROJECT_CODE}/03-spec` | ativo |
| SDD | project | `docs/sdd` | ativo |
| BASE | central | `docs/{PROJECT_CODE}/06-baseline` | ativo |
| INC | central | `docs/{PROJECT_CODE}/07-incidents` | ativo |
| PM | central | `docs/{PROJECT_CODE}/08-postmortems` | ativo |

### Sizing — quais documentos a mudança exige

| Nível | Critério | Documentos |
|---|---|---|
| small | Toca ~3 arquivos ou menos, nenhum critério de decision_gates.rfc_to_adr se aplica, e o comportamento externo do produto não muda (ajuste de config, correção pontual, tooling). | SDD |
| medium | Feature contida em um domínio, nenhum critério do gate rfc_to_adr se aplica. | SPEC, SDD |
| large | Pelo menos 1 critério de decision_gates.rfc_to_adr se aplica. | RFC, ADR, SPEC, SDD |
| complex | Vários critérios do gate se aplicam, ou a mudança é cross-team, ou precisa de direção estratégica que ainda não existe em nenhuma RFC. | STRAT (opcional), RFC, ADR, SPEC, SDD |

### Ciclo de vida de status

`draft` → `in_review` → `approved` → `rejected` → `implemented`

Transições válidas: draft → in_review, archived; in_review → approved, rejected, draft; approved → implemented, superseded, archived; rejected → archived; implemented → superseded, archived; superseded → archived.

INC usa o ciclo próprio: `open` → `mitigated` → `resolved` → `closed`.

### Critérios do gate RFC → ADR (qualquer um verdadeiro exige ADR)

- **novo_padrao_arquitetural** — Introduz ou altera um padrão arquitetural (novo componente estrutural, novo serviço, mudança de topologia).
- **alto_custo_reversao** — Decisão de alto custo ou difícil reversão (rollback caro, lento ou impossível).
- **trade_off_tecnico_relevante** — Existe mais de uma alternativa técnica viável cujos prós/contras precisam ficar registrados para não serem rediscutidos.
- **impacto_cross_team** — Mais de um time/domínio é diretamente afetado pela decisão.
- **troca_tecnologia_vendor** — Introduz ou troca tecnologia, vendor ou dependência externa relevante (banco de dados, provedor cloud, linguagem, lib crítica).

## As leis inegociáveis, uma a uma

### gate_implementation_before_code

**NENHUMA LINHA DE CÓDIGO ANTES DA SPEC E DA SDD EXISTIREM.**

OBRIGATÓRIO, não é sugestão. Antes de criar, editar ou gerar qualquer arquivo de código de implementação (schema, migration, service, endpoint, UI) para uma decisão que já tem RFC e/ou ADR aprovado neste framework, a IA DEVE, na mesma resposta/turno em que decide começar a implementar (nunca depois): 1. Verificar se PRD e/ou Tech Spec aplicáveis (conforme decision_gates.rfc_to_adr já decidiu) existem no repositório central. Se não existirem, CRIÁ-LOS PRIMEIRO — antes de qualquer linha de código — seguindo o fluxo normal (seção 3). 2. Verificar se a SDD correspondente já foi compilada no repositório do projeto (decision_gates.prd_ts_to_sdd). Se não existir, COMPILÁ-LA PRIMEIRO — antes de qualquer linha de código. 3. Só depois de PRD/TS/SDD existirem (podem ser criados na mesma sessão, não precisam de dias de intervalo — o gate é de ORDEM, não de tempo de espera) a IA pode começar a escrever código.

Racionalizações que denunciam a violação acontecendo agora:

| Se você pensar | A realidade |
|---|---|
| O ADR tem uma seção Consequências detalhada, é especificação suficiente. | Foi exatamente a falha que originou este gate (v1.5.0). ADR é o porquê, nunca o o quê nem o como. |
| Escrevo o documento depois, o código sai igual. | Documento retroativo não guiou nada. Ele registra o que já foi feito, e o gate existe para o oposto. |
| É uma mudança pequena, não compensa o overhead. | Tamanho decide QUAIS documentos (ver sizing), nunca se a ordem vale. |
| O usuário está com pressa / pediu para ir direto. | Ver if_user_asks_to_skip: avisar e pedir confirmação explícita, nunca obedecer em silêncio. |
| Já entendi o que precisa ser feito, o documento seria burocracia. | Entender não é registrar. A próxima sessão não herda o seu entendimento. |

### gate_branch_before_commit

**NENHUM COMMIT DE IMPLEMENTAÇÃO DIRETO EM MAIN.**

OBRIGATÓRIO, não é sugestão. Antes do primeiro commit de implementação de uma decisão coberta por este framework, a IA DEVE: 1. Confirmar que a branch de trabalho atual não é a branch padrão do repositório (main/master) — se for, criar uma branch nova a partir dela antes de qualquer commit. 2. Nomear a branch de forma rastreável ao id do documento que a originou (ex.: `feat/ADR-EVM-0011-controle-estoque`, `sdd/SDD-EVM-0009`) — mesmo espírito do id_scheme (seção 7): rastreio pelo nome, não só pela mensagem de commit. 3. Levar essa branch a main por PR (pull request / merge request), nunca por merge local direto nem push --force em main. A IA pode abrir o PR, mas não deve mergeá-lo sozinha sem sinal do humano responsável, salvo instrução explícita em contrário. 4. Referenciar no corpo do PR os ids relacionados (RFC/ADR/PRD/TS/ SDD), no mesmo padrão de referência usado na auditoria (seção 11), para que o PR funcione como o commit/PR "coberto" que essa auditoria espera encontrar.

Racionalizações que denunciam a violação acontecendo agora:

| Se você pensar | A realidade |
|---|---|
| É um commit só / mudança trivial, branch é cerimônia. | Sem branch não há check de CI nem janela de revisão. Um commit ruim já nasce integrado. |
| Estou sozinho no projeto, não tem quem revisar. | O PR não existe só para revisão humana — é onde os status checks rodam e onde os ids ficam vinculados. |
| Já tenho PRD/TS/SDD prontos, o gate está cumprido. | Gate 13 e gate 14 são independentes. Cumprir um não dispensa o outro. |
| Faço o merge local agora e abro o PR depois. | Depois do merge não existe mais PR a abrir. A ordem é o gate. |
| Abri o PR, então posso mergear. | A IA pode abrir o PR; mergear precisa de sinal do humano responsável. |

### gate_content_quality

**NENHUM DOCUMENTO VAI A in_review COM PLACEHOLDER OU AMBIGUIDADE PENDENTE.**

OBRIGATÓRIO antes de mover PRD/TS/SDD de `draft` para `in_review`: 1. Todo requisito funcional (SPEC, Parte 1) tem RF-ID próprio e critério de aceite em notação EARS — não um bucket solto de critérios desconectado dos requisitos. EARS dá a gramática que "verificável objetivamente" não dava sozinho, e é a mesma notação de AWS Kiro e tlc-spec-driven: ubíqua "O sistema deve <resposta>" dirigida a evento "Quando <gatilho>, o sistema deve <resposta>" dirigida a estado "Enquanto <estado>, o sistema deve <resposta>" indesejada "Se <condição>, então o sistema deve <resposta>" opcional "Onde <capacidade>, o sistema deve <resposta>" Em PRD legado (projeto sob 1.x) isto é aviso, não erro. 2. Todo contrato técnico (Tech Spec) tem assinatura/schema exato e aponta o arquivo/módulo onde vive ("onde") — não descrição em prosa livre do tipo "no serviço de X". 3. Todo caminho de erro/borda relevante está listado explicitamente (PRD: "Casos de borda"; Tech Spec: "Casos de borda / tratamento de erro") — "tratar erros apropriadamente" não é conteúdo, é placeholder. 4. Nenhum placeholder do tipo "TBD", "definir depois", "ajustar conforme necessário", "seguir padrão do projeto" sem nomear o arquivo padrão, ou qualquer frase que descreva o que fazer sem mostrar como. 5. Ambiguidade real (algo que genuinamente depende de decisão do humano) é marcada como `NEEDS CLARIFICATION: <pergunta objetiva>` em vez de resolvida por suposição da IA. Um documento não pode ir para `approved` com `NEEDS CLARIFICATION` pendente — só até `in_review`, e mesmo assim sinalizado ao humano revisor. 6. A SDD compilada não introduz critério, contrato ou instrução que não exista em nenhum PRD/TS de `source_docs` — compilar não é redigir do zero (regra já existente, seção 3), e este gate proíbe também a direção inversa: a SDD empobrecer o que o PRD/TS já continha.

Racionalizações que denunciam a violação acontecendo agora:

| Se você pensar | A realidade |
|---|---|
| 'Seguir o padrão do projeto' é específico o bastante. | Só se você nomear o arquivo que é o padrão. Sem o nome, é placeholder. |
| 'Tratar erros apropriadamente' cobre os casos de borda. | É a definição de placeholder: descreve o que fazer sem mostrar como. |
| Deixo TBD e preencho quando souber. | TBD em documento que avança de status vira TBD esquecido em documento aprovado. |
| A ambiguidade é pequena, decido por conta e sigo. | Suposição silenciosa da IA é o que NEEDS CLARIFICATION existe para impedir. |
| Os critérios de aceite estão listados juntos no fim, dá no mesmo. | Bucket de critérios desconectado dos requisitos não permite verificar cobertura 1:1. |
| Rodei a checklist mentalmente, está tudo certo. | O scan de placeholder é busca literal pelos termos banidos, não impressão. Rode validate_doc.py. |

### gate_scope_verification

**NENHUM implemented SEM COMANDO RODADO NESTA SESSÃO E SAÍDA REAL.**

OBRIGATÓRIO antes de mover uma SDD para `implemented`: 1. Todo item de "Requisitos consolidados" e "Especificação técnica consolidada" da SDD tem código correspondente identificável — se algo ficou de fora, a SDD não está implementada, está parcial (mantenha `approved`, não avance o status). 2. Todo arquivo efetivamente criado/alterado pela implementação está listado na SDD (seção técnica ou instruções à IA). Arquivo tocado que não está na SDD é um destes dois casos, nunca silencioso: (a) escopo que faltou registrar — volte e atualize a SDD antes de prosseguir; ou (b) scope creep — remova antes do commit final. 3. Nenhuma abstração, dependência nova, feature flag ou refactor que não foi pedido por nenhum requisito da SDD. "Já que eu estava ali" não é justificativa válida sob este framework (ver também `principio_minimalismo`, se definido em guias do projeto). 4. A tabela "Evidência de verificação" da SDD é preenchida com o comando de fato executado NESTA sessão e a saída real — cada critério de "Critérios de aceite" precisa de uma linha de evidência correspondente. "Deve passar" ou resultado assumido de memória não satisfaz este item; rode o comando de novo se não tiver certeza de quando rodou pela última vez. 5. A verificação é feita por quem NÃO implementou (skill `verify-sdd`, sessão ou subagente separado, sem herdar o histórico da sessão de implementação). Quem escreveu o código tem o resultado como conclusão desejada. Quando for inevitável ser a mesma sessão, isso é declarado na tabela — verificação não independente é dado mais fraco, e o humano precisa saber. 6. Todo critério com teste automatizado passa pelo sensor de discriminação: introduzir uma falha de comportamento real em espaço descartável (stash/cópia/worktree, nunca commit), confirmar que o teste FALHA, e desfazer. Teste que passa com a implementação quebrada não verifica nada — é ruído verde. Critério sem teste automatizado é declarado como tal, nunca marcado como verificado por leitura de código.

Racionalizações que denunciam a violação acontecendo agora:

| Se você pensar | A realidade |
|---|---|
| Rodei esse teste há pouco, deve estar passando. | Se você não tem a saída desta sessão, você não tem evidência. Rode de novo. |
| O teste passou de primeira, então está tudo certo. | Teste que nunca falhou pode não estar testando nada. Confirme que ele reprova a implementação errada. |
| Já que eu estava ali, aproveitei e refatorei/abstraí. | Código sem requisito correspondente é scope creep. Remova antes do commit. |
| Esse arquivo eu toquei mas é detalhe, não precisa entrar na SDD. | Arquivo fora da lista é escopo não registrado ou scope creep — nunca uma terceira coisa silenciosa. |
| Faltou um requisito pequeno, marco implemented e completo depois. | Requisito faltando significa parcial. Mantenha approved. |
| O subagente relatou que passou. | Relato de outro agente sobre o próprio trabalho não substitui verificação independente. |

### lessons_policy

**FALHA DE EXECUÇÃO VIRA LIÇÃO LOCAL, NÃO VERSÃO NOVA DO FRAMEWORK.**

### sizing

**TAMANHO DECIDE QUAIS DOCUMENTOS, NUNCA SE A ORDEM VALE.**

A ausência de um artefato É o registro de que a fase foi pulada deliberadamente — não se cria documento para declarar que outro documento não era necessário. Quem quiser auditar o porquê lê o campo `sizing` no front-matter da SPEC ou da SDD.

Racionalizações que denunciam a violação acontecendo agora:

| Se você pensar | A realidade |
|---|---|
| É simples, pulo a SDD também. | small já é o piso. Abaixo da SDD não existe nível — existe código sem especificação. |
| Classifico como small para ir mais rápido. | O critério é objetivo: ~3 arquivos, nenhum critério do gate, sem mudança de comportamento externo. Se falhar em um, não é small. |
| É large, mas a RFC eu escrevo depois. | Documento retroativo é a violação da seção 13 com outro nome. |

## Registry

- **entry_fields**: id, type, title, status, owner, created, updated, relates_to, path
- **update_rule**: Toda vez que um documento é criado ou tem status/relates_to alterado, o registry correspondente (central ou de projeto, conforme o tipo) DEVE ser atualizado no mesmo momento. O front-matter do documento e a entrada no registry nunca podem divergir.
- **traceability_query**: Dado um id, a cadeia completa (ancestrais e descendentes) é obtida percorrendo relates_to/parent_*/source_docs recursivamente. Quando a cadeia atravessa do repositório de projeto para o central (via SDD), a resolução usa a url gravada em source_docs em vez de leitura local.

## Auditoria de aderência

Detectar, depois do fato, quais commits/PRs do repositório de um projeto não têm nenhum documento do framework por trás — sem travar merge, sem exigir disciplina perfeita de commit.

Sob demanda, quando alguém decide rodar — não é um gate de CI nem bloqueia PR. Cadência sugerida (não obrigatória): a cada ciclo de RFC ou periodicamente (ex.: mensal).

- **precondition**: A auditoria lê o campo `repository` do registry central para saber qual repositório varrer. Se ele estiver ausente, a IA DECLARA que o projeto não tem repositório de código registrado e PARA, perguntando ao usuário — nunca infere, adivinha ou deduz a URL a partir do nome do projeto. Quando `repository_status: none_yet`, não há o que auditar: o projeto está em modo greenfield e ainda não produziu commit algum.
- **commit_reference_convention**: Convenção recomendada, não obrigatória: mencionar o id do documento relacionado na mensagem de commit ou descrição da PR (ex.: "Refs: SDD-{PROJECT}-0001" ou "Refs: INC-{PROJECT}-0002"). A auditoria funciona mesmo que ninguém siga a convenção — ela só facilita achar o vínculo quando alguém segue.
- **output**: Relatório de auditoria (texto ou arquivo) — não é um novo tipo de documento formal, não bloqueia nada, não precisa de aprovação para existir; só os ADRs reconstruídos que ele eventualmente propõe seguem o ciclo de aprovação normal.
- **non_goals**: Não bloquear commit, PR ou merge., Não exigir que todo commit tenha referência — a auditoria mede e reporta, não força adesão., Não reconstruir PRD/Tech Spec de commits passados, pela mesma razão do onboarding (o código já é a especificação do 'como').

## Passagem de contexto entre sessões

- **normative_source**: Esta seção é resumo estrutural. O procedimento normativo completo vive em _framework/procedures/handover.md (geração do HANDOFF.md) e _framework/procedures/pickup.md (retomada) — em caso de divergência, o procedimento manda.
- **when_to_trigger**: Planejamento terminou (SDD compilada e approved) e a implementação vai rodar em sessão/agente separado., Uso de contexto da sessão atual atinge ~45% (limite configurável pelo usuário) e ainda há trabalho do fluxo (documentar ou implementar) pela frente., Troca deliberada de sessão/agente no meio da implementação (ex.: subagente por tarefa, como em execução multi-agente).
- **content_rule**: HANDOFF referencia ids do framework (SDD-X, TS-X, PRD-X) em vez de reescrever o conteúdo desses documentos — a sessão seguinte lê os documentos originais quando precisar de detalhe, o HANDOFF é só o mapa de "onde parei e o que fazer a seguir". Nunca duplica o que já está em source_docs ou nos Critérios de aceite da SDD.
- **no_placeholder**: Mesma proibição do gate_content_quality (seção 15): "Status" e "Next step" não podem ser vagos ("fazer os ajustes pendentes") — precisam de ação literal e específica.
- **pickup_rule**: A sessão/agente que retoma lê o HANDOFF, relê (do disco, não da descrição do HANDOFF) qualquer arquivo listado em "Files touched" que for alterar, reconhece em poucas linhas (objetivo + o que está pronto + próximo passo) e prossegue direto para "Next step" sem pedir confirmação genérica de "posso continuar?" — a menos que "Next step" seja de fato ambíguo, caso em que faz UMA pergunta específica.
- **relationship_with_gates**: Handover não substitui nenhum gate anterior — SDD ainda precisa existir e estar `approved` antes de implementar (seção 13), branch dedicada ainda é obrigatória antes do commit (seção 14), e a verificação de escopo (seção 16) ainda roda antes de `implemented`, independente de quantas sessões/handoffs aconteceram no meio.

## Onboarding de projeto existente

- **applies_when**: Projeto com código em produção e nenhum histórico de STRAT/RFC/ADR/PRD/TS neste framework.
- **phase_1_baseline**: Levantamento único do estado atual, feito por uma IA lendo o repositório de código existente. Não inventa histórico que não existe — descreve o que encontra e infere decisões passadas a partir do código.
- **phase_2_cutover**: A partir daqui, o projeto segue o fluxo principal normalmente, como se fosse um projeto novo — não há mais diferença de tratamento.

## Ciclo de vida de incidente

- **states**: open, mitigated, resolved, closed

