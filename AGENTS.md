# AGENTS.md — Framework de Documentação & Rastreabilidade (v2.1.0)

Arquivo GERADO por `_framework/scripts/render_prompts.py` a partir de
`_framework/rules/workflow-rules.yaml`. Não edite à mão: o CI reprova
(`render_prompts.py --check`). Para mudar comportamento, edite o YAML e
regenere. Em qualquer divergência entre este arquivo e o YAML, **o YAML
manda** — divergência é falha de build, não diferença tolerada.

## Como usar

Você ajuda a criar, avaliar e rastrear os documentos de decisão do
projeto. Não pule etapas do fluxo, não invente campo fora do schema, e
atualize o registry no mesmo momento em que criar ou alterar qualquer
documento — front-matter e registry nunca divergem.

Dois repositórios: o **central** guarda `_framework/` e
`docs/{PROJECT_CODE}/`; o **repositório de projeto** guarda `docs/sdd/`.
A SDD é a única exceção que vive no repositório de código, porque é o
único documento pensado para ser lido por uma IA na hora de implementar.
Antes de criar qualquer documento, confirme em qual dos dois você está.

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

## Caminho comum (small e medium)

1. **Classifique o sizing** aplicando os critérios acima e **declare** o
   nível no campo `sizing` do front-matter. Você propõe; o humano pode
   subir a qualquer momento, e descer exige justificativa registrada.
2. **small** → escreva só a SDD, em `docs/sdd/` do repositório de
   projeto. O vínculo com o código é o `Refs:` no commit/PR.
   **medium** → SPEC no central (`docs/{PROJECT_CODE}/03-spec`), depois
   a SDD compilada a partir dela.
3. **Compile, não escreva do zero.** A SDD nasce de `source_docs` — cada
   entrada com id **e** URL completa, já que os documentos de origem
   estão no outro repositório.
4. **Só então implemente**, em branch nomeada pelo id que a originou
   (ex.: `sdd/SDD-PROJETO-0007`), levada a main por PR.
5. **Verifique antes de `implemented`**: cada critério de aceite rodado
   de fato, com o comando e a saída real registrados na SDD. Nunca
   "deve passar", nunca resultado de memória.

## Ainda não tenho repositório de código

Modo greenfield: STRAT, RFC, ADR e SPEC rodam inteiros no repositório
central. Declare `repository_status: none_yet` no `registry.yaml` do
projeto — sem isso o estado é assumido, não registrado. SDD fica
bloqueada enquanto durar, porque SDD vive em `docs/sdd/` do repositório
de projeto; isso não dispensa gate algum, apenas não há código ainda.
Ao criar o repositório, num único ato: preencha `repository` com a URL
e `repository_status: active` no central, e crie `docs/sdd/registry.yaml`
vazio no repositório novo.

`large` e `complex` acrescentam RFC e ADR antes da SPEC — leia
`_framework/rules/workflow-rules.yaml` (seções `decision_gates` e
`sizing`) antes de conduzir um desses.

## Proibido

- Placeholder em documento (`TBD`, `a definir`, `ajustar conforme
  necessário`). Ambiguidade real vira `[NEEDS CLARIFICATION: pergunta]`.
- Marcar critério como verificado por leitura de código.
- Editar ADR já `approved` — gere um novo que o marque `superseded`.
- Editar qualquer arquivo gerado (este inclusive).

## Validação

```
python3 _framework/scripts/framework_check.py --auto
```
