# Framework de Documentação & Rastreabilidade para IA

Um framework para registrar e rastrear as decisões de um projeto —
Strategy Doc, RFC, ADR, PRD, Tech Spec e SDD — de forma consistente entre
projetos diferentes e entre ferramentas de IA diferentes (Claude, Cursor,
Copilot, ChatGPT, Gemini). Inclui um gate de decisão objetivo entre RFC e
ADR, um procedimento de onboarding para projetos que já existiam antes do
framework, um fluxo apartado (mas rastreável) para incidentes e
postmortem, e uma auditoria de aderência sob demanda para quando nem todo
commit/PR referencia um documento (e a adesão de todo o time nunca pode
ser garantida).

Este repositório é o **kit genérico**, feito para ser copiado/forkado por
qualquer pessoa ou time. Se você está montando o seu próprio repositório
central de uso real, veja a seção [Como adotar em um projeto](#como-adotar-em-um-projeto)
abaixo.

## Por que isso existe

Decisões técnicas e de produto costumam ficar espalhadas em conversas,
docs soltos e memória de time, sem elo entre "por que decidimos isso" e
"o que foi construído". Este framework define um fluxo com portas de
decisão explícitas e um registro central que permite, a qualquer
momento, perguntar "de onde veio X" ou "o que depende de Y" e obter uma
resposta confiável — mesmo para projetos que já existiam antes dele, e
mesmo depois que algo quebra em produção.

## O fluxo

```
Strategy Doc -> RFC -> [GATE: exige ADR?]
    -> SIM -> ADR -> PRD + Tech Spec -> SDD (repositório do projeto)
    -> NÃO ------------> PRD + Tech Spec -> SDD (repositório do projeto)
SDD -> input direto para a IA que vai implementar o código
```

Veja o diagrama completo em
[`_framework/guides/assets/flow_diagram.png`](_framework/guides/assets/flow_diagram.png).

A **fonte canônica e sempre atual** das regras é
[`_framework/rules/workflow-rules.yaml`](_framework/rules/workflow-rules.yaml)
— em caso de divergência com qualquer prompt, guia ou skill, o YAML manda.
Os arquivos `Framework_Documentacao_Rastreabilidade_v1.x.md` na raiz são
instantâneos históricos das especificações 1.1 e 1.2, mantidos por
registro, e não refletem mais o estado atual. O histórico de evolução está
em [`CHANGELOG.md`](CHANGELOG.md).

## Estrutura deste repositório

```
_framework/
  rules/workflow-rules.yaml     — fonte canônica de todas as regras
  templates/*.template.md       — um template por tipo de documento
  prompts/
    universal.md                 — cole em qualquer chat de IA
    onboarding-bootstrap.md      — uso único, projeto já existente
    framework-audit.md           — uso periódico, sob demanda
    cursor/doc-framework.mdc     — regra para Cursor/Windsurf
    copilot/copilot-instructions.md
  skills/doc-traceability-framework/  — Claude Skill completa
  skills/handover/                    — gera HANDOFF.md entre sessões/agentes
  skills/pickup/                      — retoma sessão a partir de um HANDOFF.md
  scripts/
    generate_registry_md.py      — gera a tabela legível do registry
    registry_tools.py            — validate / trace / audit
  guides/
    guia-tecnico.md
    guia-nao-tecnico.md
    paralelizacao-trilhas.md     — padrão opcional de execução paralela
examples/                        — dois cenários validados (ver abaixo)
```

## Modelo de dois repositórios

Este framework assume **dois tipos de repositório**, nunca um só:

- **Repositório central**: guarda `_framework/` (cópia única) e
  `docs/{PROJECT_CODE}/` de todos os seus projetos — mas só os tipos
  Strategy Doc, RFC, ADR, PRD, Tech Spec, Baseline, Incidente e
  Postmortem.
- **Repositório de cada projeto** (seu repositório de código): guarda
  apenas `docs/sdd/` — as SDDs desse projeto, porque é o único documento
  pensado para ser lido por uma IA no momento de implementar.

Veja o diagrama em
[`_framework/guides/assets/topology_diagram.png`](_framework/guides/assets/topology_diagram.png).

## Os gates obrigatórios

Quatro portas que a IA (ou pessoa) operando o framework precisa atravessar
— nenhuma delas é imposta por CI; todas são verificadas no momento em que
o trabalho acontece:

| Gate | Quando | O que exige |
|---|---|---|
| Implementação | Antes da 1ª linha de código | PRD/Tech Spec (central) e SDD (projeto) já existem. ADR sozinho não basta. |
| Branch | Antes do 1º commit | Branch dedicada com nome rastreável ao id; chegada a main por PR. |
| Qualidade de conteúdo | `draft` → `in_review` | Requisito com critério verificável próprio, contrato com assinatura e arquivo exatos, casos de erro explícitos, zero placeholder. |
| Verificação de escopo | `approved` → `implemented` | Todo requisito virou código, todo arquivo tocado está na SDD (nada a mais, nada a menos), e cada critério tem comando + saída reais registrados. |

Quando o trabalho atravessa mais de uma sessão de IA — o caso comum entre
planejar e implementar — as skills `handover`/`pickup` passam o contexto
por um `HANDOFF.md` curto que referencia ids em vez de recarregar a sessão
inteira. Nenhum gate acima é pulado por causa disso.

## Os 9 tipos de documento

| Tipo | Nome | Repositório |
|---|---|---|
| STRAT | Strategy Doc | central |
| RFC | Request for Comments | central |
| ADR | Architectural Decision Record | central |
| PRD | Product Requirements Document | central |
| TS | Tech Spec | central |
| SDD | Spec Driven Design | **do projeto** |
| BASE | Baseline (onboarding) | central |
| INC | Incidente | central |
| PM | Postmortem | central |

## Exemplos incluídos (`examples/`)

- `examples/central/EXEMPLO/` — projeto novo, demonstrando os dois
  caminhos do gate de decisão (com e sem ADR).
- `examples/project-repo-checkout/` — o repositório de projeto
  correspondente, com as SDDs.
- `examples/central/LEGADO/` — projeto já existente sendo incorporado:
  onboarding (Baseline + ADR reconstruído), um incidente com postmortem,
  e o cutover para o fluxo normal.

Os exemplos são **registries de demonstração**: trazem as entradas
(`registry.yaml` + `registry.md` gerado) que representam cada cenário, com
o campo `path` apontando para onde os documentos ficariam num repositório
real — os arquivos `.md` de cada documento não estão incluídos, para o kit
não carregar conteúdo fictício. Todos os três passam em
`registry_tools.py validate` e `trace`.

## Como adotar em um projeto

1. Crie (ou faça fork d)o seu próprio repositório central privado, com
   uma cópia de `_framework/` e uma pasta `docs/{PROJECT_CODE}/` por
   projeto (vazia, com as subpastas de cada tipo e um `registry.yaml`
   vazio).
2. Em cada repositório de código, crie `docs/sdd/` com seu próprio
   `registry.yaml` vazio.
3. Configure a IA de sua preferência: cole `_framework/prompts/universal.md`
   num chat, copie `_framework/prompts/cursor/doc-framework.mdc` para
   `.cursor/rules/` no repositório de projeto, `copilot-instructions.md`
   para `.github/`, ou instale a Claude Skill
   (`_framework/skills/doc-traceability-framework/`). Para o ciclo
   planejar → implementar em sessões separadas, instale também
   `_framework/skills/handover/` e `_framework/skills/pickup/`.
4. Se for um projeto que já existe, use
   `_framework/prompts/onboarding-bootstrap.md` uma única vez antes de
   seguir o fluxo normal.
5. Periodicamente (sob demanda, não é CI), rode
   `_framework/prompts/framework-audit.md` para ver se os commits/PRs do
   repositório de projeto têm documento por trás — a adesão de todo o
   time nunca é garantida, então isso funciona como rede de segurança,
   não como bloqueio.

Guias completos: [`guia-tecnico.md`](_framework/guides/guia-tecnico.md)
(para quem cria documentos e roda os scripts) e
[`guia-nao-tecnico.md`](_framework/guides/guia-nao-tecnico.md) (para quem
participa das decisões sem mexer em código).

## Licença

MIT — veja [`LICENSE`](LICENSE). Use, copie, modifique e redistribua
livremente, inclusive comercialmente.
