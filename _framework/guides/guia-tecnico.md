# Guia de Uso — Framework de Documentação & Rastreabilidade (Técnico)

Este guia é para quem vai efetivamente criar documentos, revisar ADRs,
rodar os scripts e configurar o framework em um repositório novo. Se
você só precisa entender o que cada documento significa e quando pedir
um, veja `guia-nao-tecnico.md` — é mais curto e sem jargão.

A fonte de verdade de tudo que está aqui é
`_framework/rules/workflow-rules.yaml`. Este guia é um resumo prático;
em caso de dúvida ou divergência, o YAML manda.

## 1. Os dois repositórios

Você sempre vai estar operando em um destes dois lugares — confirme qual
antes de criar qualquer documento:

- **Repositório central** (`framework-central`, ou o nome que vocês
  derem): guarda `_framework/` (cópia única do kit) e
  `docs/{PROJECT_CODE}/` de **todos** os projetos, mas só os tipos
  STRAT, RFC, ADR, SPEC, BASE, INC, PM.
- **Repositório de cada projeto** (o repositório de código): guarda só
  `docs/sdd/` — as SDDs desse projeto específico.

A SDD é a única exceção porque é o único documento pensado para ser lido
por uma IA (Claude Code, Cursor, Copilot) no momento de implementar — ela
precisa estar perto do código, os outros tipos não.

## 2. Estrutura de pastas

**No repositório central:**
```
_framework/
  rules/workflow-rules.yaml       (fonte canônica)
  templates/*.template.md
  prompts/ (universal.md, onboarding-bootstrap.md, framework-audit.md,
            cursor/, copilot/)
  skills/doc-traceability-framework/   (skill principal)
  skills/handover/  skills/pickup/     (passagem de contexto entre sessões)
  skills/verify-sdd/                   (verificação independente)
  scripts/ (framework_check.py, registry_tools.py, validate_doc.py,
            validate_state.py, check_commit.py, check_renderings.py,
            render_prompts.py, generate_registry_md.py, framework_lib.py)
  guides/ (guia-tecnico.md, guia-nao-tecnico.md, paralelizacao-trilhas.md)
docs/
  {PROJECT_CODE}/
    00-strategy/
    01-rfc/
    02-adr/
    03-spec/
    # 03-prd/ e 04-tech-spec/ só existem em projeto mapeado sob 1.x —
    # foram fundidos em 03-spec/ na v2.0.0 e não são migrados
    # 05 é reservado para SDD, que não fica aqui — vive no repositório
    # do projeto, em docs/sdd/ (ver seção 1)
    06-baseline/
    07-incidents/
    08-postmortems/
    registry.yaml
    registry.md   (gerado)
```

**No repositório de cada projeto:**
```
docs/
  sdd/
    SDD-{PROJECT_CODE}-0001.md
    registry.yaml
    registry.md   (gerado)
```

## 3. Criando um projeto novo

1. No repositório central, crie `docs/{PROJECT_CODE}/` com as subpastas
   acima e um `registry.yaml` vazio (`project`, `framework_version`,
   `repository`, `documents: []`) — pergunte a URL do repositório de
   código do projeto se ainda não souber, nunca adivinhe:
   ```yaml
   project: "{PROJECT_CODE}"
   framework_version: "1.7.0"   # use o framework.version do workflow-rules.yaml
   repository: "https://github.com/{ORG}/{PROJECT_CODE}"
   documents: []
   ```
2. No repositório de código do projeto, crie `docs/sdd/` com seu próprio
   `registry.yaml` vazio.
3. Escolha o `PROJECT_CODE` (curto, maiúsculo, sem espaços) — ele é usado
   em todos os IDs desse projeto dali para frente e não muda depois.
4. Copie (ou aponte para) `prompts/universal.md` e use-o com a IA de sua
   preferência a partir daqui.

## 4. Criando um documento — passo a passo

1. Abra o template do tipo em `_framework/templates/{tipo}.template.md`.
2. Descubra o próximo ID: olhe `docs/{PROJECT_CODE}/registry.yaml` (ou
   `docs/sdd/registry.yaml` para SDD), conte quantos documentos daquele
   tipo já existem, o próximo é `{TYPE}-{PROJECT_CODE}-{N+1, 4 dígitos}`.
3. Preencha o front-matter (bloco YAML no topo) e o conteúdo.
4. Adicione a entrada correspondente no `registry.yaml` certo — **na
   mesma tarefa**, não depois.
5. Rode `python3 _framework/scripts/generate_registry_md.py docs/{PROJECT_CODE}`
   (ou `docs/sdd` no repo de projeto) para regenerar a tabela legível.

## 4.1 Antes de tudo: qual o tamanho da mudança

O funil não é fixo desde a v2.0.0. Antes de criar qualquer documento,
decida o nível e declare-o no campo `sizing` do front-matter:

| Nível | Critério | Documentos |
|---|---|---|
| `small` | ~3 arquivos, nenhum critério do gate RFC→ADR, comportamento externo inalterado | SDD |
| `medium` | Feature num domínio só, nenhum critério do gate | SPEC + SDD |
| `large` | Pelo menos 1 critério do gate se aplica | RFC + ADR + SPEC + SDD |
| `complex` | Vários critérios, cross-team, ou direção estratégica inexistente | STRAT + RFC + ADR + SPEC + SDD |

Não crie documento para registrar que outro documento não era necessário
— a ausência do arquivo é o registro. Descer de nível exige justificativa
escrita no documento; subir, não.

Tamanho decide **quais** documentos existem, nunca se os gates valem.
`small` tem menos documento, não menos gate.

## 5. O gate RFC → ADR na prática

Depois que uma RFC é aprovada, responda objetivamente:

```
[ ] Introduz ou altera um padrão arquitetural?
[ ] Decisão de alto custo ou difícil reversão?
[ ] Trade-off técnico relevante entre alternativas viáveis?
[ ] Impacto cross-team (mais de um time/domínio afetado)?
[ ] Troca ou introdução de tecnologia/vendor/dependência externa relevante?
```

Qualquer `[x]` → crie um ADR antes da SPEC. Nenhum marcado → pule direto
para a SPEC. Registre o resultado em
`requires_adr` e `decision_gate_criteria_met` no front-matter da RFC —
isso é o que torna a decisão auditável depois.

## 6. Compilando a SDD

A SDD nasce no repositório do projeto, não no central. Regras práticas:

- Só compile quando a SPEC (e o ADR, se existir) estiver
  `approved`.
- Não escreva conteúdo novo — consolide o que já está na SPEC
  Spec/ADR. A regra vale nas duas direções: a SDD também não pode
  empobrecer o que a SPEC já detalhava.
- `source_docs` é uma lista de `{id, url}`: a `url` é a URL completa do
  arquivo no repositório central (ex.:
  `https://github.com/org/framework-central/blob/main/docs/CHECKOUT/03-spec/SPEC-CHECKOUT-0002.md`).
  Sem essa URL, quem olhar a SDD depois não consegue chegar à origem.

A qualidade da SDD é herdada: SDD genérica quase sempre é sintoma de SPEC
vaga, não de erro na compilação. Por isso a Parte 1 da SPEC precisa
entregar o **o quê** (cada RF com id próprio e critério de aceite
em EARS) e a Parte 2 o **como** e o **onde** (assinatura/schema
exato de cada contrato, arquivo/módulo onde vive, casos de erro
explícitos) — ver seção 7.

## 7. Os gates obrigatórios

Quatro gates, todos não-opcionais, todos verificados pela IA (ou pessoa)
que opera o framework — nenhum é imposto por CI:

**Gate de implementação** (`gate_implementation_before_code`, seção 13
do YAML). Nenhuma linha de código de implementação antes da SPEC
(central) e SDD (projeto) existirem. Um ADR aprovado, mesmo com
"Consequências" detalhada, não é especificação suficiente. É gate de
ORDEM, não de tempo — tudo pode acontecer na mesma sessão.

**Gate de branch** (`gate_branch_before_commit`, seção 14). Nenhum commit
de implementação direto em main: branch dedicada com nome rastreável ao
id de origem (`feat/ADR-EVM-0011-controle-estoque`, `sdd/SDD-EVM-0009`),
e chegada a main por PR referenciando os ids relacionados. Independente
do gate anterior — dá para cumprir um e violar o outro.

**Gate de qualidade de conteúdo** (`gate_content_quality`, seção 15).
Antes de mover SPEC/SDD de `draft` para `in_review`, rode a
autorrevisão que está no rodapé de cada template:

```
[ ] Todo RF da SPEC tem RF-ID e critério de aceite em EARS
[ ] Todo contrato da SPEC tem assinatura/schema exato + arquivo/módulo
[ ] Casos de borda e erro listados explicitamente (não "tratar erros")
[ ] Nenhum placeholder: "TBD", "definir depois", "ajustar conforme
    necessário", "seguir o padrão do projeto" sem nomear o arquivo
[ ] Ambiguidade real marcada como NEEDS CLARIFICATION, não suposta
[ ] Nomes consistentes entre seções (criarPedido != criarNovoPedido)
```

Documento não vai para `approved` com `NEEDS CLARIFICATION` pendente —
até `in_review` sim, sinalizado ao revisor humano.

**Gate de verificação de escopo** (`gate_scope_verification`, seção 16).
Antes de mover uma SDD de `approved` para `implemented`:

```
[ ] Todo requisito consolidado da SDD tem código correspondente
    (faltou algum? a SDD está parcial — mantenha approved)
[ ] Todo arquivo tocado pela implementação está listado na SDD
    (fora da lista = escopo não registrado -> atualize a SDD,
     ou scope creep -> remova antes do commit; nunca em silêncio)
[ ] Nenhuma abstração/dependência/flag extra sem requisito na SDD
[ ] Tabela "Evidência de verificação" preenchida com o comando rodado
    NESTA sessão e a saída real de cada critério de aceite
```

O último item é o que separa `implemented` de "acho que terminei":
checklist marcado de memória não é evidência. Se não lembra de quando
rodou o comando pela última vez, rode de novo.

Descompasso encontrado (requisito sem código, ou código sem requisito)
não avança status em silêncio: relate ao responsável e proponha atualizar
a SDD ou remover o código fora de escopo — a decisão é dele.

## 8. Passagem de contexto entre sessões (handover/pickup)

O fluxo separa com frequência quem planeja (compila SPEC/SDD) de quem
implementa — inclusive quando é a mesma pessoa, em sessões de IA
diferentes para não estourar o orçamento de contexto de uma sessão só.
Para isso existem duas skills:

- `_framework/skills/handover/` — gera um `HANDOFF.md` de seções fixas
  (Goal, Status, Ids relacionados, Files touched, Key decisions, Open
  threads/blockers, Next step, Don't do). Use ao terminar o planejamento
  antes de outra sessão implementar, ou quando o uso de contexto da
  sessão atual se aproximar do limite que você adotar (~45% é um bom
  padrão) com trabalho ainda pela frente.
- `_framework/skills/pickup/` — a sessão seguinte lê o HANDOFF, confirma
  o status real dos ids citados (não confia no que o HANDOFF anotou),
  relê do disco os arquivos que vai alterar, e executa o "Next step".

Regra central: o HANDOFF **referencia ids** (SDD-X, SPEC-X, ADR-X), não
copia o conteúdo desses documentos — quem retoma lê o original quando
precisar de detalhe. Local: raiz do repositório de projeto para handover
de implementação; `docs/{PROJECT_CODE}/` no central para handover entre
etapas de documentação. Sobrescreve no lugar — o histórico real são os
documentos versionados e os PRs, não uma pilha de HANDOFFs antigos.

Handover não pula nenhum gate da seção 7: SDD ainda precisa estar
`approved` antes de implementar, branch dedicada continua obrigatória, e
a verificação de escopo roda antes de `implemented`, independente de
quantas sessões passaram no meio.

## 9. Scripts disponíveis

```bash
# Tudo de uma vez — é o que o hook de pre-commit e o CI chamam
python3 _framework/scripts/framework_check.py --auto

# Registry x front-matter: ids órfãos, referências quebradas, status
# inválido, `path` que não resolve, url de source_docs, framework_version
python3 _framework/scripts/registry_tools.py validate docs/{PROJECT_CODE}

# Gate de qualidade de conteúdo (seção 15): placeholder, ambiguidade
# pendente, seções obrigatórias, RF-ID, EARS, "onde" dos contratos
python3 _framework/scripts/validate_doc.py docs/{PROJECT_CODE}

# Gate de verificação de escopo (seção 16): SDD `implemented` precisa de
# tabela de evidência preenchida, uma linha por critério, sem "deve passar"
python3 _framework/scripts/validate_state.py docs/sdd

# Conventional Commits + referência a id do framework
python3 _framework/scripts/check_commit.py --range main..HEAD

# Prompts e skill ainda concordam com o YAML canônico
python3 _framework/scripts/check_renderings.py
python3 _framework/scripts/render_prompts.py --check

# Rastrear a cadeia completa de um documento
python3 _framework/scripts/registry_tools.py trace docs/{PROJECT_CODE} RFC-CHECKOUT-0001

# Regenerar a tabela legível (registry.md)
python3 _framework/scripts/generate_registry_md.py docs/{PROJECT_CODE}
```

Todos aceitam `--report-only` para listar sem falhar.

**Ligue isso no seu repositório central**, não deixe como comando manual:

```bash
git config core.hooksPath .githooks
```

O hook de pre-commit valida os documentos tocados pelo commit; o de
commit-msg checa a mensagem; e o workflow em `.github/workflows/` roda
tudo em PR e push. A recusa do framework a usar CI (seção 11 do YAML) é
sobre commits de terceiros nos repositórios de código — no seu próprio
repositório de documentação não há custo nenhum em bloquear.

**Regra nova não reprova documento antigo.** Cada exigência declara em que
versão entrou (`validate_doc.RULE_SINCE`) e só vale para projeto cujo
`registry.yaml` declara `framework_version` igual ou posterior. É a
não-retroatividade deixando de ser texto e virando comportamento.

## 9.1 Verificação independente antes de `implemented`

Não marque uma SDD como `implemented` na mesma sessão que a implementou.
Rode a skill `verify-sdd` em sessão ou subagente separado — quem escreveu
o código tem o resultado como conclusão desejada.

Ela faz três coisas que o validator sozinho não faz:

1. Confere requisito↔código nas **duas** direções: requisito sem código é
   SDD parcial (mantenha `approved`); arquivo tocado fora da SDD é escopo
   não registrado ou scope creep.
2. Roda cada critério de aceite **nesta sessão** e registra a saída real.
3. Aplica o **sensor de discriminação**: quebra o comportamento em espaço
   descartável (stash, cópia, worktree — nunca commit), confirma que o
   teste falha, e desfaz. Teste que passa com a implementação quebrada não
   verifica o critério.

O resultado vai para um `validation.md` ao lado da SDD, com veredito
PASS/FAIL, evidência por critério e resultado do sensor. `FAIL` não avança
status.

## 9.2 Quando um gate for violado

Registre no `LESSONS.md` do projeto — data, o que falhou com o id ou sha
concreto, a red flag que teria pegado antes, e a correção. **Não** proponha
mudar `workflow-rules.yaml` por causa de uma violação isolada: uma lição só
vira regra global se aparecer em dois projetos diferentes, tiver checagem
mecânica possível, e couber como red flag ou item de validator existente.

Entre a v1.4.0 e a v1.7.0 cada falha de agente virou seção obrigatória
nova; o arquivo de regras dobrou e a taxa de falha não caiu. É o padrão que
esta regra existe para quebrar.

## 10. Onboarding de um projeto já existente

Use `_framework/prompts/onboarding-bootstrap.md` — não improvise um
processo alternativo. Resumo do que acontece (detalhes completos no
próprio prompt):

1. Uma IA lê o repositório de código do projeto.
2. Gera um único `BASE-{PROJECT_CODE}-0001` (retrato do estado atual).
3. Propõe ADRs reconstruídos (`provenance: reconstructed`, sempre
   começando em `status: in_review`).
4. Alguém do time revisa e confirma/corrige cada ADR proposto antes de
   qualquer um virar `approved`.
5. A partir daí, o projeto segue o fluxo normal — a próxima RFC real é
   `RFC-{PROJECT_CODE}-0001`.

Não reconstrua SPEC do que já foi construído — não vale o
esforço, o código já é a especificação do que existe.

## 11. Auditoria de aderência (commits/PRs x registry)

A adesão de todo o time a referenciar documentos em commits/PRs nunca
pode ser garantida — sempre vai ter commit avulso, hotfix de incidente
feito sob pressão, ou simplesmente alguém que esqueceu. Por isso este
framework não tenta impor isso com CI ou bloqueio de merge: em vez de um
gate, existe uma auditoria periódica e sob demanda, que assume que vai
haver desvio e o transforma em achado revisável — reaproveitando o mesmo
mecanismo de reconstrução do onboarding (seção 10), só que contínuo em vez
de único.

Use `_framework/prompts/framework-audit.md` quando quiser rodar:

1. Gere o log de commits desde a última auditoria:
   ```bash
   git log --since="<data>" --pretty=format:'%H%n%s%n%b%n===END===' > gitlog.txt
   ```
2. Cruze com o(s) registry(ies) conhecidos:
   ```bash
   python3 _framework/scripts/registry_tools.py audit gitlog.txt docs/{PROJECT_CODE} docs/sdd
   ```
3. O relatório separa commits em cobertos, referência quebrada (id citado
   não existe) e não documentados. Para os não documentados, aplique os 5
   critérios do gate RFC→ADR (seção 5): se algum se aplica, proponha um
   ADR reconstruído (`provenance: reconstructed`, `status: in_review`,
   `tags: [audit]`); se nenhum se aplica, não crie documento nenhum.
4. Nenhum ADR reconstruído por auditoria é aprovado sem revisão humana —
   mesma regra do onboarding.

Não é CI, não bloqueia PR, não exige disciplina perfeita de commit — só
torna visível o que já é verdade sobre o repositório.

## 12. Incidentes e postmortem

INC tem ciclo de vida próprio: `open → mitigated → resolved → closed`
(não é `draft/review/approved`, é operacional).

Severidade e obrigatoriedade de postmortem:

| Severidade | Critério | Postmortem |
|---|---|---|
| SEV1 | Indisponibilidade total/crítica, perda de dados, incidente de segurança | Obrigatório, completo |
| SEV2 | Degradação relevante, sem workaround | Obrigatório, completo |
| SEV3 | Impacto limitado, workaround existe | Obrigatório, leve |
| SEV4 | Impacto mínimo/cosmético | Opcional |

Regra de recorrência: 2ª ocorrência da mesma `root_cause_key` em ≤ 90
dias torna o postmortem obrigatório mesmo em SEV4.

Cada action item do postmortem é triado: ajuste pontual → SPEC
direto; mudança estrutural (bateria em algum critério do gate) → nova
RFC, com `relates_to` apontando para o PM de origem.

## 13. Configurando as ferramentas de IA

- **Qualquer chat de IA (ChatGPT, Gemini, Claude):** cole
  `_framework/prompts/universal.md` no início da conversa.
- **Cursor/Windsurf:** copie
  `_framework/prompts/cursor/doc-framework.mdc` para
  `.cursor/rules/doc-framework.mdc` **no repositório do projeto** (não
  no central).
- **GitHub Copilot:** copie
  `_framework/prompts/copilot/copilot-instructions.md` para
  `.github/copilot-instructions.md` **no repositório do projeto**.
- **Claude / Cowork:** instale a skill `doc-traceability-framework.skill`
  — ela já embute templates, regra canônica e scripts. Para o ciclo
  planejamento → implementação em sessões separadas, instale também
  `_framework/skills/handover/` e `_framework/skills/pickup/` (seção 8).

## 14. Paralelização por trilhas de negócio (opcional)

Para projetos com módulos de negócio razoavelmente independentes, existe
um padrão opcional de organização — uma skill por trilha, uma sessão de
IA (ou pessoa) por trilha, grafo de dependências entre trilhas — em
`paralelizacao-trilhas.md`. Não é obrigatório e não altera o fluxo
principal de documentos; é um padrão de execução de código, não de
decisão. Combina bem com handover/pickup (seção 8): cada troca de sessão
dentro de uma trilha passa o bastão por um `HANDOFF.md` em vez de
carregar a sessão inteira adiante.

## 15. Erros comuns a evitar

- Criar STRAT/RFC/ADR/SPEC dentro do repositório de projeto (esses
  tipos são sempre do repositório central).
- Aprovar um ADR reconstruído sem revisão humana.
- Editar um ADR `approved` no lugar em vez de criar um novo e marcar o
  antigo como `superseded`.
- Esquecer de atualizar o `registry.yaml` junto com o documento.
- Reconstruir SPEC retroativa durante onboarding ou auditoria.
- Transformar a auditoria de aderência em gate de CI ou bloqueio de PR —
  ela é diagnóstico sob demanda, não um portão obrigatório.
- Aprovar SPEC com placeholder ("TBD", "tratar erros
  apropriadamente") ou com `NEEDS CLARIFICATION` pendente — a SDD
  compilada a partir disso vai sair genérica, e o custo aparece só na
  implementação (seção 7).
- Marcar uma SDD como `implemented` sem preencher a tabela de evidência
  com comando e saída reais — checklist marcado de memória não prova
  nada (seção 7).
- Deixar a implementação tocar arquivos que não estão na SDD sem
  resolver: ou a SDD está incompleta, ou é escopo a mais. Nunca as duas
  coisas em silêncio.
- Reescrever no `HANDOFF.md` o conteúdo que já está na SPEC/SDD em vez
  de referenciar os ids — handover é mapa, não cópia (seção 8).
