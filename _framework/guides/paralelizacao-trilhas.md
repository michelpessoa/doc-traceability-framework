# Guia — Paralelização por Trilhas de Negócio

Este guia é opcional e complementar ao `guia-tecnico.md`. Ele descreve
um padrão de organização para projetos cujo escopo se divide em módulos
de negócio relativamente independentes, permitindo que múltiplas
sessões de IA (ou pessoas) trabalhem em paralelo sem pisar uma na outra.
Não é um novo tipo de documento nem altera o fluxo principal
(seção 3 de `workflow-rules.yaml`) — é um padrão de **execução**, não de
**decisão**.

## Quando faz sentido

- O projeto tem módulos de negócio com fronteiras razoavelmente claras
  (ex.: Pacientes, Financeiro, Relatórios), cada um consumindo um núcleo
  comum (auth, RBAC, catálogos, etc.).
- Existe uma "Fundação" (Fase 0) que todos os módulos dependem, e que
  precisa ficar pronta (ao menos o schema/contratos) antes das demais
  trilhas começarem.
- Há intenção real de rodar mais de uma trilha ao mesmo tempo — seja com
  múltiplas sessões de IA, seja com mais de uma pessoa no time.

Quando não faz sentido: projeto pequeno, sem módulos separáveis, ou
equipe de uma pessoa só trabalhando sequencialmente de qualquer forma —
aí o overhead de organizar trilhas/skills não se paga.

## O que NÃO muda

O fluxo de documentação (Strategy → RFC → gate → ADR → SPEC → SDD),
os tipos de documento, o registry e os IDs continuam exatamente como
descritos em `workflow-rules.yaml`. Paralelização é sobre como o
**código** é implementado depois que a decisão já está documentada e
aprovada — não sobre paralelizar aprovação de documentos (a cadeia
RFC→ADR→SPEC é sequencial por natureza: cada etapa depende do
resultado da anterior).

O que pode ser paralelizado dentro do próprio fluxo de documentação,
quando fizer sentido:
- Documentos irmãos sem dependência entre si (ex.: vários ADRs
  originados da mesma RFC, cada um cobrindo uma decisão atômica
  diferente) — podem ser escritos em paralelo, desde que cada um
  aponte para o mesmo `parent_rfc` e não dependa do conteúdo dos
  outros.
- Etapas de leitura/pesquisa (ex.: levantar múltiplas partes de um
  código grande no onboarding, ou cruzar vários commits numa auditoria)
  — a coleta pode paralelizar, mas a síntese final (o BASE, o relatório
  de auditoria) deve ser um passo único, para não gerar documentos
  conflitantes.

## O padrão: uma trilha, uma skill, uma sessão

1. **Defina as trilhas** no Plano Técnico do projeto (arquivo livre,
   fora de `_framework/` — ex.: `PLANO_TECNICO.md` na raiz do
   repositório de código): liste os módulos, suas dependências entre si
   e o grafo de quem pode rodar em paralelo com quem. Um exemplo de
   formato:

   ```mermaid
   flowchart LR
     F[Fase 0: Fundação] --> A[Trilha A]
     F --> B[Trilha B]
     A --> C[Trilha C]
     B --> C
   ```

2. **Uma skill por trilha**, em `.claude/skills/<trilha>/SKILL.md`, no
   repositório de código do projeto (não no repositório central). Cada
   skill deve trazer, de forma autocontida:
   - Escopo da trilha (o que está dentro/fora).
   - Requisitos relevantes (RF/RNF, se existirem fora do framework).
   - Recorte do schema/modelo de dados que a trilha usa.
   - Contrato com as outras trilhas (o que ela consome, o que ela
     expõe).
   - O que a trilha **não** deve fazer (ex.: não hardcode o que deveria
     vir de um serviço da Fundação).

   Isso evita reexplicar o projeto inteiro toda vez que uma sessão nova
   começa a trabalhar numa trilha.

3. **Uma sessão de IA (ou pessoa) por trilha em execução**, isolada por
   branch ou worktree git, para não haver conflito de working directory
   entre trilhas rodando ao mesmo tempo. A sessão carrega a skill
   correspondente no início do trabalho.

4. **Respeite o grafo de dependências.** Uma trilha só começa quando o
   que ela depende (normalmente: schema estável de outra trilha, não
   necessariamente a implementação completa) está pronto. Combinar
   cedo a interface/schema de uma entidade compartilhada entre quem for
   trabalhar nas trilhas dependentes permite que todas comecem quase ao
   mesmo tempo, mesmo sem a trilha de origem estar 100% implementada.

5. **A trilha que consolida (se existir) fica por último.** Se uma
   trilha depende de todas as outras (ex.: um módulo de relatórios que
   lê dado de todo o resto), ela não paraleliza — só começa quando as
   demais tiverem schema/contrato prontos.

## Onde isso se conecta ao framework

- Cada trilha, ao iniciar implementação real, segue o fluxo normal:
  RFC (se a mudança justificar) → gate → SPEC → SDD no
  repositório do projeto. A skill da trilha não substitui a SDD — a
  skill é contexto de execução; a SDD é o documento rastreável que
  origina o código.
- Se a existência de trilhas paralelas em si for uma decisão
  arquitetural relevante para o projeto (normalmente é — bate o
  critério `impacto_cross_team` do gate), registre-a em um ADR próprio,
  com `parent_rfc` apontando para a RFC de fundação do projeto.

## Troca de sessão dentro de uma trilha

Uma trilha raramente cabe em uma sessão de IA só. Quando a sessão atual
se aproxima do limite de contexto que você adotar (~45% é um bom padrão),
ou quando o planejamento termina e a implementação vai rodar em outra
sessão, use as skills `handover`/`pickup` (`_framework/skills/handover/`,
`_framework/skills/pickup/`) em vez de carregar a sessão inteira adiante:
o `HANDOFF.md` referencia os ids da trilha (SDD-X, TS-X) e o próximo
passo literal, e a sessão seguinte retoma a partir dele. Isso é o
equivalente, dentro de uma trilha, ao que a skill da trilha faz entre
trilhas: contexto suficiente, não contexto inteiro.

## Exemplo real

Um projeto usando este padrão tem, tipicamente: Fase 0 (Fundação)
bloqueando o resto; duas trilhas de domínio iniciando em paralelo assim
que a Fundação expõe schema/contratos; trilhas seguintes dependendo só do
schema de uma entidade central e rodando paralelas entre si; e uma trilha
de consolidação (ex.: Relatórios) fechando o grafo por último. O registro
dessa organização vive na RFC de fundação do projeto
(`docs/{PROJECT_CODE}/01-rfc/RFC-{PROJECT_CODE}-0001.md`, no repositório
central) e no `PLANO_TECNICO.md` do repositório de código.
