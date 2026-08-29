# Framework de Documentação & Rastreabilidade para IA

Um framework para registrar e rastrear as decisões de um projeto —
Strategy Doc, RFC, ADR, SPEC e SDD — de forma consistente entre
projetos diferentes e entre ferramentas de IA diferentes (Claude, Cursor,
Copilot, ChatGPT, Gemini). Inclui um gate de decisão objetivo entre RFC e
ADR, um procedimento de onboarding para projetos que já existiam antes do
framework, um fluxo apartado (mas rastreável) para incidentes e
postmortem, e uma auditoria de aderência sob demanda para quando nem todo
commit/PR referencia um documento (e a adesão de todo o time nunca pode
ser garantida).

Desde a v2.0.0 os gates não são só texto: `_framework/scripts/` traz
validators que os checam mecanicamente, e a profundidade do fluxo é
função do tamanho da mudança — uma correção de três arquivos não
atravessa seis documentos.

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
[SIZING: qual o tamanho da mudança?]
  small   ->                                       SDD
  medium  ->                              SPEC ->  SDD
  large   ->        RFC -> [gate] -> ADR -> SPEC ->  SDD
  complex -> STRAT -> RFC -> [gate] -> ADR -> SPEC ->  SDD

SDD (repositório do projeto) -> input direto para a IA implementar
```

O nível é decidido pelos mesmos 5 critérios do gate RFC → ADR, não por
uma régua nova. `small` = toca ~3 arquivos, nenhum critério se aplica,
comportamento externo não muda. A **ausência** de um documento é o
registro de que aquela fase foi pulada — não se cria documento para
declarar que outro não era necessário.

Tamanho decide *quais* documentos existem, nunca se os gates valem: uma
mudança `small` tem menos documento, não menos gate.

Veja o diagrama completo em
[`_framework/guides/assets/flow_diagram.png`](_framework/guides/assets/flow_diagram.png).

A **fonte canônica** das regras é
[`_framework/rules/workflow-rules.yaml`](_framework/rules/workflow-rules.yaml)
— em caso de divergência com qualquer prompt, guia ou skill, o YAML manda.
A especificação narrada, que explica o desenho e o porquê de cada regra,
está em
[`Framework_Documentacao_Rastreabilidade.md`](Framework_Documentacao_Rastreabilidade.md)
e acompanha sempre a versão atual — não há cópias versionadas dela. O
histórico de o que mudou em cada versão está em
[`CHANGELOG.md`](CHANGELOG.md).

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
  skills/verify-sdd/                  — verificação independente antes de `implemented`
  scripts/
    framework_lib.py             — base comum; deriva as constantes do YAML
    framework_check.py           — entrada única (hook e CI chamam esta)
    registry_tools.py            — validate / trace / audit
    validate_doc.py              — gate de qualidade de conteúdo
    validate_state.py            — gate de verificação de escopo
    check_commit.py              — Conventional Commits + referência a id
    check_renderings.py          — prompts e skill concordam com o YAML
    render_prompts.py            — gera o núcleo canônico nos prompts
    generate_registry_md.py      — gera a tabela legível do registry
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
  Strategy Doc, RFC, ADR, SPEC, Baseline, Incidente e Postmortem.
- **Repositório de cada projeto** (seu repositório de código): guarda
  apenas `docs/sdd/` — as SDDs desse projeto, porque é o único documento
  pensado para ser lido por uma IA no momento de implementar.

Veja o diagrama em
[`_framework/guides/assets/topology_diagram.png`](_framework/guides/assets/topology_diagram.png).

## Os gates obrigatórios

Quatro portas, cada uma com uma lei de uma linha, uma tabela das
racionalizações que costumam contorná-la, e um validator que a checa:

| Gate | Lei | Mecanizado por |
|---|---|---|
| Implementação | **Nenhuma linha de código antes da SPEC e da SDD existirem** | — (ordem, verificada no momento) |
| Branch | **Nenhum commit de implementação direto em main** | branch protection do repositório |
| Qualidade de conteúdo | **Nenhum documento vai a `in_review` com placeholder ou ambiguidade pendente** | `validate_doc.py` |
| Verificação de escopo | **Nenhum `implemented` sem comando rodado nesta sessão e saída real** | `validate_state.py` + skill `verify-sdd` |

Rodar tudo de uma vez:

```
python3 _framework/scripts/framework_check.py --auto
```

Os validators respeitam a não-retroatividade: cada exigência declara em
que versão entrou, e só vale para projeto cujo `registry.yaml` declara
`framework_version` igual ou posterior. Evoluir o kit nunca reprova
documento de projeto já mapeado.

**Verificação é papel, não etapa.** Antes de uma SDD virar `implemented`,
a skill `verify-sdd` roda em sessão separada da que implementou — quem
escreveu o código tem o resultado como conclusão desejada. Ela confere
requisito↔código nas duas direções, roda cada critério registrando saída
real, e aplica o *sensor de discriminação*: quebrar o comportamento em
espaço descartável e confirmar que o teste falha. Teste que passa com a
implementação quebrada não verifica nada.

**Falha de execução vira lição local, não versão nova do framework.**
Violação de gate é registrada no `LESSONS.md` do projeto; só vira regra
global se aparecer em dois projetos, tiver checagem mecânica possível e
couber como red flag ou item de validator.

Quando o trabalho atravessa mais de uma sessão de IA — o caso comum entre
planejar e implementar — as skills `handover`/`pickup` passam o contexto
por um `HANDOFF.md` curto que referencia ids em vez de recarregar a sessão
inteira. Nenhum gate acima é pulado por causa disso.

## Os tipos de documento

| Tipo | Nome | Repositório |
|---|---|---|
| STRAT | Strategy Doc (opcional — normalmente é seção da RFC) | central |
| RFC | Request for Comments | central |
| ADR | Architectural Decision Record | central |
| SPEC | Requisito (o quê) + desenho (o como/onde) | central |
| SDD | Spec Driven Design | **do projeto** |
| BASE | Baseline (onboarding) | central |
| INC | Incidente | central |
| PM | Postmortem | central |

`PRD` e `TS` existiram até a v1.7.0 como documentos separados e foram
fundidos em `SPEC` na v2.0.0. Seguem reconhecidos pelos validators, para
que projetos mapeados sob 1.x continuem válidos sem migração.

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
   `_framework/skills/handover/` e `_framework/skills/pickup/`, e
   `_framework/skills/verify-sdd/` para a verificação independente.
3.1. Ligue os validators: copie `.githooks/` para o seu repositório
   central e rode `git config core.hooksPath .githooks`; e adicione um
   workflow que chame `framework_check.py --auto` em PR.
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
