---
id: SDD-DTF-0044
type: SDD
title: "Skills enxutas: SKILL.md roteador, references sob demanda, descriptions curtas e procedimentos por caminho estável"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0018"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0018.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Compilada da SPEC-DTF-0018 (frente C da RFC-DTF-0008), sizing medium. Implementar só em sessão separada aberta no kit, em worktree próprio, na ordem de 'Decomposição em tasks'. Não editar workflow-rules.yaml, render_prompts.py nem arquivos gerados. Cada critério de aceite tem comando e resultado esperado copiados da SPEC; nenhum pode ser relaxado. Verificar com sdd-verifier em sessão separada antes de implemented."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, skills, contexto, frente-c]
---

# Skills enxutas: SKILL.md roteador, references sob demanda, descriptions curtas e procedimentos por caminho estável

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar.

## Resumo executivo

Reduzir o custo de contexto de cada disparo das skills do kit sem perder
nenhum gate de vista. O `SKILL.md` principal cai de 21172 para no máximo
9216 bytes e vira roteador; incidentes, onboarding e auditoria passam
para `references/`. Toda `description` fica em até 450 caracteres.
`handover`, `pickup` e `verify-sdd` passam a citar o procedimento por
caminho que resolve de qualquer diretório (`git rev-parse
--show-toplevel`). `verify-sdd.md` é reordenado para que a seção 5 venha
antes dos títulos dos modelos de registro. A cópia `.claude/skills/` da
skill principal passa a ser symlink de pasta. Nenhuma regra de
comportamento muda: só a forma como a skill entrega o texto ao modelo.
Esta SDD é independente das demais da frente de otimização (não toca
`workflow-rules.yaml` nem `render_prompts.py`) e pode rodar em paralelo.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — RFC-DTF-0008 `approved` avaliou o gate `rfc_to_adr` como falso
(`requires_adr: false`); SPEC-DTF-0018 tem `parent_adr: null`, sizing
`medium`.

Decisões registradas na SPEC (humano, 2026-09-24):

- **Repositório sem `_framework/`:** mantém-se o fallback "pergunte ao
  usuário onde está o repositório" do RF05 para qualquer repositório sem
  `_framework/`; nenhum caminho alternativo para o central é embutido nas
  skills.
- **Symlink de pasta:** o carregamento da skill principal por symlink de
  pasta é verificado empiricamente como critério de aceite (`/skills`,
  critério 14). Se não carregar, vale a alternativa: manter o symlink de
  arquivo e citar `references/` no `SKILL.md` por caminho a partir da
  raiz do repositório.

## Requisitos consolidados

| RF-ID | Requisito | Arquivos |
|---|---|---|
| RF01 | O `SKILL.md` principal vira roteador com no máximo 9216 bytes (medido em bytes), mantendo: modelo de dois repositórios e modo greenfield, tabela de tipos (os 8 tipos ativos; PRD/TS só como legado), sizing com os quatro níveis, fluxo `small`/`medium`/`large`/`complex`, ciclo de vida com a frase "Transições válidas: ...", uma linha por gate e a tabela "O que fazer em cada pedido comum". Deve conter os oito tipos ativos, os quatro níveis, a frase "Transições válidas:" e a seção "O que fazer em cada pedido comum". | `_framework/skills/doc-traceability-framework/SKILL.md`, `_framework/tests/test_skill_md_consistency.py` |
| RF02 | Cada iron law do YAML (`gate_implementation_before_code`, `gate_branch_before_commit`, `gate_content_quality`, `gate_scope_verification`, `lessons_policy`, `sizing`) continua no `SKILL.md`, inteira, e cada gate ocupa uma linha ou parágrafo curto com o ponteiro literal `` `workflow-rules.yaml:<chave>` ``. Tabelas "Racionalização × Realidade", blocos "Origem" e passos detalhados saem do `SKILL.md` e ficam só no YAML (`red_flags`). O `SKILL.md` não cita "seção N". O teste acha cada `iron_law` inteira e o ponteiro da chave que a declara, nenhuma tabela com cabeçalho "Racionalização" e nenhuma ocorrência de "seção" seguida de número. | `_framework/skills/doc-traceability-framework/SKILL.md`, `_framework/tests/test_skill_md_consistency.py` |
| RF03 | Incidentes e postmortem, onboarding de projeto existente e auditoria de aderência saem do `SKILL.md` para `references/incidents.md`, `references/onboarding.md` e `references/audit.md` na pasta da skill. O texto movido preserva o conteúdo normativo (severidade, recorrência de 90 dias, triagem de action items, uso de `prompts/onboarding-bootstrap.md` e `prompts/framework-audit.md`) e troca "seção 5 de `references/workflow-rules.yaml`" por `workflow-rules.yaml:<chave>`. O `SKILL.md` ganha a tabela "Leia sob demanda" e não contém `SEV1` nem `root_cause_key`. | `_framework/skills/doc-traceability-framework/SKILL.md`, `_framework/skills/doc-traceability-framework/references/incidents.md`, `_framework/skills/doc-traceability-framework/references/onboarding.md`, `_framework/skills/doc-traceability-framework/references/audit.md`, `_framework/tests/test_skill_md_consistency.py` |
| RF04 | A `description` de cada uma das quatro skills (`doc-traceability-framework`, `handover`, `pickup`, `verify-sdd`) tem no máximo 450 caracteres (contagem do valor YAML, sem a quebra final do bloco `>`; limite inclusivo) e mantém "Use when" e "Do NOT use for". Texto exato em "Especificação técnica consolidada". | `_framework/skills/doc-traceability-framework/SKILL.md`, `_framework/skills/handover/SKILL.md`, `_framework/skills/pickup/SKILL.md`, `_framework/skills/verify-sdd/SKILL.md`, `_framework/tests/test_skill_md_consistency.py` |
| RF05 | Os `SKILL.md` de `handover`, `pickup` e `verify-sdd` citam o procedimento por caminho que resolve de qualquer diretório do repositório: `_framework/procedures/<skill>.md` com a instrução literal `cat "$(git rev-parse --show-toplevel)/_framework/procedures/<skill>.md"`, no lugar de "(a partir da raiz do repositório)". Executado de um subdiretório, o comando resolve para arquivo existente e cada `SKILL.md` contém o comando e o nome do procedimento. | `_framework/skills/handover/SKILL.md`, `_framework/skills/pickup/SKILL.md`, `_framework/skills/verify-sdd/SKILL.md`, `_framework/tests/test_skill_md_consistency.py` |
| RF06 | `_framework/procedures/verify-sdd.md` passa a ter a ordem estrutural 0, 1, 2, 3, 4, 5, "Modelos de registro", "Red flags": os três blocos de modelo hoje dentro do passo 4 (tabela "Evidência de verificação", seção "Escalonado ao humano", `validation.md`) vão para a nova subseção `### Modelos de registro`, depois do passo 5. Cada frase do passo 4 que introduzia um bloco passa a apontar para o modelo (M1, M2, M3). Nenhuma outra linha muda: o conjunto de linhas não vazias difere de `_framework/tests/fixtures/verify_sdd_pre_reorder.md` apenas pelas linhas de apontamento e pelo título da nova subseção. Lidos em ordem, incluindo os de blocos de código, "5. Checagem mecânica antes de mudar status" vem antes de "Escalonado ao humano", "Descompassos encontrados" e "Lições". | `_framework/procedures/verify-sdd.md`, `_framework/tests/test_procedures_structure.py`, `_framework/tests/fixtures/verify_sdd_pre_reorder.md` |
| RF07 | `.claude/skills/doc-traceability-framework` deixa de ser pasta com o symlink `SKILL.md` e passa a ser symlink para `../../_framework/skills/doc-traceability-framework`, de modo que `references/`, `prompts/`, `scripts/` e `templates/` resolvam a partir dela. Symlinks de `handover`, `pickup` e `verify-sdd` não mudam. Vale nos dois repositórios (kit e central), com `_framework/` idêntico (`diff -rq` sem diferença fora de `__pycache__`). | `.claude/skills/doc-traceability-framework`, `_framework/tests/test_skill_md_consistency.py` |

Casos de borda (todos da SPEC, com o comportamento esperado):

| Caso | RF | Comportamento esperado |
|---|---|---|
| `SKILL.md` cita gate cuja chave foi removida ou renomeada no YAML | RF02 | Teste reprova e nomeia arquivo e chave; vale também para `references/*.md` e os três `SKILL.md` de procedimento |
| Iron law do YAML reescrita e `SKILL.md` mantém a antiga | RF02 | Compara a lei inteira normalizada (minúsculas, sem crases, sem ponto, espaços colapsados), mesma normalização de `check_renderings.py` |
| Nova iron law entra no YAML numa chave nova | RF02 | Teste descobre as leis varrendo o YAML (toda chave de topo com `iron_law`), não lista fixa; lei nova sem linha no `SKILL.md` reprova |
| `SKILL.md` volta a crescer acima de 9216 bytes | RF01 | Teste reprova com o tamanho medido; a saída é mover conteúdo para `references/`, não subir o teto |
| `references/incidents.md` citado e ausente, ou presente e nunca citado | RF03 | Reprova nos dois sentidos (exceto `workflow-rules.yaml`, cópia sincronizada) |
| Texto movido perde regra (ex.: recorrência de 90 dias) | RF03 | `incidents.md` contém `root_cause_key`, `SEV1` e `90 dias`; `audit.md` contém `prompts/framework-audit.md`; `onboarding.md` contém `prompts/onboarding-bootstrap.md` |
| `description` com aspas ou `:` que quebra o YAML | RF04 | `read_frontmatter` devolve `{}` ou levanta erro; o teste reprova com mensagem de front-matter inválido, nunca passa em silêncio com string vazia |
| `description` com 450 caracteres exatos | RF04 | Passa (inclusivo); 451 reprova |
| Comando `cat "$(git rev-parse --show-toplevel)/..."` fora de repositório git | RF05 | Falha com erro do git; o `SKILL.md` instrui "se o comando falhar ou o arquivo não existir, pergunte ao usuário onde está o repositório do kit ou do central; não improvise o procedimento" |
| Sessão em worktree | RF05 | `git rev-parse --show-toplevel` devolve a raiz da worktree, que contém `_framework/` versionado; o teste roda o comando a partir de `_framework/tests/` |
| Repositório de projeto sem `_framework/` | RF05 | Vale a mesma instrução de perguntar (decisão do humano registrada acima) |
| Título de dentro de bloco de código (`## Evidência de verificação`, `## Escalonado ao humano`, `# Verificação —`, `## Descompassos encontrados`, `## Lições`) antes da seção 5 | RF06 | Teste exige que todos apareçam depois da linha `### 5.` |
| Passo 4 com frase "fica assim:" sem bloco em seguida | RF06 | Teste reprova frase de introdução terminada em `:` seguida de linha em branco e título; a frase termina em ponto e cita M1, M2 ou M3 |
| Checkout sem symlink (`core.symlinks=false`) | RF07 | `.claude/skills/...` vira arquivo de texto; o teste de layout reprova com mensagem que cita o requisito de symlink |
| Skill principal descoberta apenas por symlink de pasta | RF07 | Decisão do humano registrada acima: verificação empírica em `/skills` (critério 14), com alternativa do symlink de arquivo |

Requisitos não funcionais: nenhuma dependência nova (testes usam
`pytest`, `re`, `subprocess`, `pathlib`, `framework_lib.read_frontmatter`
e `framework_lib.load_rules`); não retroativo (nenhum documento de projeto
mapeado muda); texto movido para `references/` não é reescrito além da
troca de "seção N" por `workflow-rules.yaml:<chave>`.

Requisitos transversais (sweep da SPEC): falha de dependência externa
(binário `git` e repositório) tratada no RF05; validação de entrada
(ponteiro para chave inexistente, front-matter inválido) tratada nos
RF02 e RF04; limite de volume é o orçamento de 9216 bytes do RF01;
autorização, concorrência, idempotência e observabilidade são n/a (só
markdown, symlink e testes locais).

Fora de escopo: `.claude/agents/sdd-verifier.md` e o campo `procedure`
de `verify_sdd_independently` (gerado por `render_prompts.py`);
`workflow-rules.yaml`, `render_prompts.py`, `AGENTS.md`,
`docs/especificacao.md`, `universal.md`, prompts de Cursor e Copilot;
conteúdo de `_framework/procedures/handover.md` e `pickup.md`;
`prompts/onboarding-bootstrap.md` e `prompts/framework-audit.md` (bundle
e `_framework/prompts/`, idênticos entre si; `references/onboarding.md` e
`references/audit.md` apontam para eles); remoção da duplicação do bundle
(RFC-DTF-0009); índices gerados e mapa de seções do YAML (frente A);
mecanismo de instalação da skill fora do repositório.

## Especificação técnica consolidada

**Achados que condicionam a implementação.** Nenhum `SKILL.md` é gerado:
`render_prompts.py` só sincroniza `scripts/*.py` e
`rules/workflow-rules.yaml` para dentro do bundle
(`_framework/skills/doc-traceability-framework/`); `SKILL.md`,
`references/*.md` novos e `prompts/*.md` do bundle são mantidos à mão.
`.claude/skills/<skill>/SKILL.md` é symlink versionado de arquivo para
`../../../_framework/skills/<skill>/SKILL.md`; hoje, em
`.claude/skills/doc-traceability-framework/` só existe `SKILL.md`, então
`references/`, `prompts/`, `scripts/` e `templates/` não resolvem nessa
cópia (RF07). `.claude/agents/sdd-verifier.md` é gerado e fica fora.
`check_renderings.py` trata `SKILL.md` como renderização (oito tipos
ativos, cada iron law inteira, aviso de sizing ausente, link markdown
relativo quebrado); o roteador precisa continuar passando nele.

**Onde cada skill vive.**

| Lugar | Caminho | O que muda | Regenerado ou espelhado |
|---|---|---|---|
| Fonte das skills | `_framework/skills/{doc-traceability-framework,handover,pickup,verify-sdd}/SKILL.md` | Os quatro `SKILL.md` | Editado à mão; não gerado |
| Bundle da skill principal | `_framework/skills/doc-traceability-framework/references/{incidents,onboarding,audit}.md` (novos); `prompts/`, `templates/`, `scripts/` e `references/workflow-rules.yaml` intactos | Só os três arquivos novos | Mantidos à mão; `sync_copies` não os toca |
| Cópia Claude Code | `.claude/skills/doc-traceability-framework` (vira symlink de pasta); `.claude/skills/{handover,pickup,verify-sdd}/SKILL.md` sem mudança | Só o da skill principal | Espelhado por symlink versionado |
| Procedimento | `_framework/procedures/verify-sdd.md` | Reordenação | Editado à mão |
| Repositório central | `_framework/**` e `.claude/skills/**` do central | Mesmos arquivos acima | Espelho manual do kit, byte a byte; conferido por `diff -rq` |

**Estrutura-alvo do `SKILL.md` (orçamento por seção, soma 8560 bytes,
folga 656 até 9216).**

| Seção | Conteúdo | Orçamento (bytes) |
|---|---|---|
| Front-matter | `name`, `description` (RF04) | 560 |
| Dois repositórios e greenfield | Texto atual, sem alteração de regra | 700 |
| Tipos | Tabela atual reduzida à coluna "Quando usar" curta; nota de legado PRD/TS | 1100 |
| Fluxo e sizing | Diagrama de uma linha por nível, `sizing` com `workflow-rules.yaml:sizing`, frase de que a ausência de documento é o registro | 1100 |
| Gates | Uma linha por gate: iron law inteira + ponteiro `workflow-rules.yaml:<chave>` + uma frase do que fazer ("avise e peça confirmação explícita", branch nomeada pelo id, verifique com `verify-sdd`) | 1500 |
| Ciclo de vida | Cadeia de status, frase "Transições válidas: ...", INC | 650 |
| IDs e registry | Esquema de id, comandos de `registry_tools.py` | 650 |
| Pedidos comuns | Tabela "O que fazer em cada pedido comum" | 1500 |
| Leia sob demanda | Tabela do RF03 | 500 |
| Handover e novo projeto | Duas frases com ponteiro | 300 |

**Consome** (existente, nomes exatos): `framework_lib.read_frontmatter(path:
Path) -> tuple[dict, str]` e `framework_lib.load_rules() -> dict` em
`_framework/scripts/framework_lib.py` (chaves de topo com `iron_law` são
as leis); `framework_lib.allowed_transitions()` (usado por
`test_status_lifecycle_matches_yaml`, que continua valendo);
`check_renderings.py`. Não há função nova de produção: os contratos são
os textos e os testes.

**Contrato 1 — `description` (RF04).** Texto exato, no bloco `>` do
front-matter; comprimento em caracteres entre parênteses.

`doc-traceability-framework` (443):
```
Gerencia documentos de decisão (STRAT, RFC, ADR, SPEC, SDD) com ids, front-matter e registry: criar, avaliar, avançar status, rastrear, validar; também incidentes, onboarding de legado e auditoria. Use when pedirem "cria uma RFC", "precisa de ADR?", "monta a spec", "abre um incidente", e SEMPRE antes de implementar decisão aprovada. Do NOT use for verificar SDD (`verify-sdd`), passar contexto (`handover`/`pickup`), nem README ou changelog.
```

`handover` (403):
```
Gera HANDOFF.md para transferir contexto entre sessões ou agentes, referenciando ids em vez de reescrever documentos. Use when o planejamento terminou e outra sessão vai implementar, o contexto passa de ~45% com trabalho pela frente, ou pedirem "faz o handover". Do NOT use for retomar handoff existente (`pickup`), documentação permanente, nem para dispensar gate: a SDD segue precisando de `approved`.
```

`pickup` (420):
```
Retoma trabalho a partir de um HANDOFF.md da skill `handover`, confirmando o status real dos ids e relendo do disco os arquivos a alterar, sem confiar no que o handoff anotou. Use when pedirem "retomar", "continuar de onde parei", "ler o handoff", ou a sessão começar com um HANDOFF.md no repositório. Do NOT use for criar handoff (`handover`), verificar SDD (`verify-sdd`), nem retomar sem HANDOFF.md (leia o registry).
```

`verify-sdd` (426; "Use quando" vira "Use when" para casar com o gatilho exigido):
```
Verifica de forma independente se uma SDD foi implementada antes de virar `implemented`: confere requisito e código nas duas direções, roda cada critério de aceite registrando comando e saída reais e testa se os testes discriminam. Use when pedirem "verifica a SDD", "pode marcar implemented?" ou a implementação terminar. Do NOT use for escrever ou corrigir a implementação, code review geral, nem documento que não seja SDD.
```

**Contrato 2 — ponteiro de gate (RF02),** forma literal:
`` `workflow-rules.yaml:<chave>` ``, em que `<chave>` é chave de topo do
YAML. Exemplo de linha de gate:
`> **NENHUMA LINHA DE CÓDIGO ANTES DA SPEC E DA SDD EXISTIREM.** Se o pedido for implementar decisão aprovada, confirme SPEC e SDD antes de tocar código; se pedirem para pular, avise e peça confirmação explícita. Detalhes e red flags: `workflow-rules.yaml:gate_implementation_before_code`.`
Chaves obrigatórias no `SKILL.md`: `gate_implementation_before_code`,
`gate_branch_before_commit`, `gate_content_quality`,
`gate_scope_verification`, `lessons_policy`, `sizing`; e, onde couber,
`decision_gates`, `status_lifecycle`, `handover_protocol`.

**Contrato 3 — tabela "Leia sob demanda" (RF03),** no `SKILL.md`:

| Pedido envolve | Leia |
|---|---|
| incidente, severidade, postmortem, action items | `references/incidents.md` |
| projeto com código já em produção, baseline | `references/onboarding.md` |
| auditar commits/PRs contra o registry | `references/audit.md` |
| detalhe exato de campo, transição, critério | `references/workflow-rules.yaml`, na chave citada |

Os caminhos são relativos à pasta da skill, convenção que o `SKILL.md` já
usa para `references/workflow-rules.yaml`; por isso o RF07.

**Contrato 4 — linha final dos `SKILL.md` de procedimento (RF05),** forma
exata (troque `<skill>` por `handover`, `pickup` ou `verify-sdd`):

```
Procedimento normativo: `_framework/procedures/<skill>.md` na raiz do repositório. De qualquer diretório dentro dele: `cat "$(git rev-parse --show-toplevel)/_framework/procedures/<skill>.md"`. Leia-o inteiro antes de agir. Se o comando falhar ou o arquivo não existir, pergunte ao usuário onde está o repositório do kit ou do central; não improvise o procedimento.
```

**Contrato 5 — `_framework/procedures/verify-sdd.md` (RF06),** ordem
final dos títulos fora de bloco de código: `# Verificação independente
de SDD`; `## Entrada`; `## Procedimento`; `### 0.` a `### 4. Veredito`;
`### 5. Checagem mecânica antes de mudar status`; `### Modelos de
registro` (com rótulos em negrito `**M1. Tabela de evidência na SDD**`,
`**M2. Escalonado ao humano**`, `**M3. validation.md**`, cada um seguido
do bloco de código que hoje está no passo 4, sem alteração); `## Red
flags`. As três frases do passo 4 que terminam em ":" e introduzem um
bloco (`fica assim:`, `a seção abaixo em vez de despachar uma 4ª
tentativa:`, `Escreva validation.md ao lado da SDD:`) passam a terminar
em ponto e citar "modelo M1", "M2" ou "M3, em 'Modelos de registro'". O
restante do passo 4, o 5 e a tabela de red flags não mudam. Motivo:
hoje `### 5.` (linha 206) vem depois de `### 4. Veredito` (linha 146),
mas os modelos em blocos de código do passo 4 (linhas 151 a 195)
contêm títulos, e `grep '^#'` enxerga a seção 5 depois de "Lições".

**Contrato 6 — layout `.claude/skills/` (RF07):**
`.claude/skills/doc-traceability-framework` ->
`../../_framework/skills/doc-traceability-framework` (symlink de pasta;
remove o symlink de arquivo `SKILL.md` e a pasta que o continha).

**Contrato 7 — testes (nomes de função exatos).** Em
`_framework/tests/test_skill_md_consistency.py`, mantidos os testes
atuais e acrescentados:
- `test_skill_md_within_size_budget`
- `test_skill_md_has_every_iron_law_with_pointer`
- `test_skill_md_has_no_rationalization_tables_or_section_numbers`
- `test_yaml_pointers_resolve_to_top_level_keys`
- `test_references_exist_and_are_cited`
- `test_moved_sections_keep_normative_content`
- `test_skill_descriptions_within_limit_and_triggers`
- `test_procedure_skills_use_repo_root_path`
- `test_claude_skills_layout_exposes_skill_dir`

Em novo `_framework/tests/test_procedures_structure.py`:
- `test_verify_sdd_step5_before_fenced_templates_headings`
- `test_verify_sdd_reorder_preserves_lines`

Constantes nos testes: `SKILL_BUDGET_BYTES = 9216`,
`DESCRIPTION_MAX_CHARS = 450`,
`POINTER = re.compile(r"workflow-rules\.yaml:([a-z_]+)")`. Arquivos
varridos para `POINTER` e para "seção N": o `SKILL.md` principal,
`references/{incidents,onboarding,audit}.md` e os `SKILL.md` de
`handover`, `pickup`, `verify-sdd`.

**Tratamento de erro por contrato.**

| Caso | RF | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| Chave em ponteiro inexistente no YAML | RF02 | `AssertionError` que nomeia arquivo e chave | `test_yaml_pointers_resolve_to_top_level_keys` |
| Iron law ausente ou divergente | RF02 | `AssertionError` que nomeia a chave e a lei esperada | `test_skill_md_has_every_iron_law_with_pointer` |
| Tabela "Racionalização" ou "seção N" no roteador | RF02 | `AssertionError` com a linha ofensora | `test_skill_md_has_no_rationalization_tables_or_section_numbers` |
| Acima do orçamento | RF01 | `AssertionError` com bytes medidos e teto | `test_skill_md_within_size_budget` |
| `references/*.md` ausente, órfão ou sem conteúdo mínimo | RF03 | `AssertionError` que nomeia o arquivo | `test_references_exist_and_are_cited`, `test_moved_sections_keep_normative_content` |
| Front-matter não parseável, sem gatilho ou acima de 450 caracteres | RF04 | `AssertionError` que nomeia a skill e o valor medido | `test_skill_descriptions_within_limit_and_triggers` |
| Comando de raiz ausente do `SKILL.md`, ou não resolve de `_framework/tests/` | RF05 | `AssertionError` com saída do `subprocess` | `test_procedure_skills_use_repo_root_path` |
| Ordem de títulos incorreta ou linha normativa perdida | RF06 | `AssertionError` com as linhas que diferem | `test_procedures_structure.py` |
| `.claude/skills/doc-traceability-framework` não é symlink de pasta ou aponta para fora | RF07 | `AssertionError` com `os.readlink` | `test_claude_skills_layout_exposes_skill_dir` |
| `git` ausente no ambiente de teste | RF05 | `pytest.skip` com motivo explícito, nunca "passou" | `test_procedure_skills_use_repo_root_path` |

**Estratégia de teste.**

| RF-ID / contrato | Tipo de teste | Mock? | Arquivo de teste |
|---|---|---|---|
| RF01 | Estático: `Path.stat().st_size` e presença dos tipos, níveis e frases | Não | `_framework/tests/test_skill_md_consistency.py` |
| RF02 | Estático contra o YAML real (`load_rules`) | Não | `_framework/tests/test_skill_md_consistency.py` |
| RF03 | Estático: existência, citação cruzada e conteúdo mínimo | Não | `_framework/tests/test_skill_md_consistency.py` |
| RF04 | Estático parametrizado sobre `skills/*/SKILL.md` | Não | `_framework/tests/test_skill_md_consistency.py` |
| RF05 | Execução real de `git rev-parse --show-toplevel` com `cwd=_framework/tests` | Não | `_framework/tests/test_skill_md_consistency.py` |
| RF06 | Estático: ordem de títulos incluindo os de blocos de código; comparação do conjunto de linhas não vazias contra a fixture `_framework/tests/fixtures/verify_sdd_pre_reorder.md`, com lista fixa das linhas de apontamento esperadas como única diferença | Não | `_framework/tests/test_procedures_structure.py` |
| RF07 | Estático: `os.path.islink`, `os.readlink`, resolução dos caminhos citados a partir de `.claude/skills/doc-traceability-framework/` | Não | `_framework/tests/test_skill_md_consistency.py` |

**Sensor de discriminação** (cada teste deve falhar quando se introduz a
falha correspondente numa cópia descartável): acrescentar 900 bytes ao
roteador (RF01), apagar uma iron law (RF02), renomear
`references/incidents.md` (RF03), alongar uma description para 451
(RF04), trocar `git rev-parse` por um caminho relativo (RF05), voltar
`### 5.` para o fim do arquivo (RF06), recriar o symlink de arquivo
(RF07).

**Plano de implementação da SPEC (ordem de referência; a decomposição
abaixo o reparte em tasks).** (1) criar `references/incidents.md`,
`onboarding.md`, `audit.md` com o texto atual das seções "Incidentes e
postmortem", "Onboarding de projeto já existente" e "Auditoria de
aderência", trocando "seção N de `references/workflow-rules.yaml`" por
`workflow-rules.yaml:<chave>` (`severity_scale`, `postmortem_policy`,
`action_item_triage`, `onboarding`, `audit`); (2) reescrever o
`SKILL.md` principal conforme a estrutura-alvo, medir com `wc -c`; (3)
nova `description` e nova linha final em `handover`, `pickup`,
`verify-sdd` (o resto, checklist mínimo, não muda); (4) copiar o
`verify-sdd.md` atual para `_framework/tests/fixtures/verify_sdd_pre_reorder.md`
ANTES de editar, depois mover os três blocos e reescrever as três
frases; (5) `git rm` do symlink de arquivo e criar o symlink de pasta;
(6) acrescentar os nove testes e criar `test_procedures_structure.py`;
(7) espelhar no central e conferir com `diff -rq`; (8) rodar a suíte e
os gates e registrar comando e saída.

**Rollout / rollback.** Rollout direto, sem feature flag: uma SDD, um PR
no kit e um PR de espelho no central. Rollback: reverter o commit; nada é
gerado, não há artefato a regenerar. Projetos mapeados não são afetados.

**Observabilidade.** `SKILL.md` principal em bytes (hoje 21172, alvo até
9216) e tamanho de cada `description` em caracteres (hoje 947, 688, 577,
734; alvo até 450), medidos por comando. Sem log nem alerta novos.

**Riscos.** Perder gate de vista ao enxugar (RF02 mecaniza); roteador
enxuto demais (tabela de pedidos comuns e uma frase de ação por gate
ficam no `SKILL.md`); symlink de pasta não ser carregado (critério 14 e
alternativa); divergência kit/central (`diff -rq`); colisão de edição com
a frente A em `SKILL.md` e `verify-sdd.md` (trechos disjuntos, quem fizer
merge depois rebasa; a frente A não precisa converter o `SKILL.md`
principal, que já usa chave de YAML).

## Decomposição em tasks

Arquivos do central usam o prefixo `central:` para que `parallel_plan.py`
não os confunda com os do kit. As tasks 1, 3 e 4 não têm interseção de
arquivo nem dependência entre si e podem rodar em paralelo; a 8 fecha a
sequência.

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Criar `references/incidents.md`, `onboarding.md` e `audit.md` com o texto movido | RF03 | `_framework/skills/doc-traceability-framework/references/incidents.md`, `_framework/skills/doc-traceability-framework/references/onboarding.md`, `_framework/skills/doc-traceability-framework/references/audit.md` | |
| 2 | Reescrever `SKILL.md` principal como roteador (com `description` nova e tabela "Leia sob demanda") | RF01, RF02, RF03, RF04 | `_framework/skills/doc-traceability-framework/SKILL.md` | 1 |
| 3 | Nova `description` e nova linha final nos `SKILL.md` de `handover`, `pickup` e `verify-sdd` | RF04, RF05 | `_framework/skills/handover/SKILL.md`, `_framework/skills/pickup/SKILL.md`, `_framework/skills/verify-sdd/SKILL.md` | |
| 4 | Guardar a fixture original e reordenar `verify-sdd.md` (modelos M1 a M3) | RF06 | `_framework/tests/fixtures/verify_sdd_pre_reorder.md`, `_framework/procedures/verify-sdd.md` | |
| 5 | Trocar o symlink de arquivo por symlink de pasta em `.claude/skills/` | RF07 | `.claude/skills/doc-traceability-framework` | 1, 2 |
| 6 | Acrescentar os nove testes em `test_skill_md_consistency.py` | RF01, RF02, RF03, RF04, RF05, RF07 | `_framework/tests/test_skill_md_consistency.py` | 1, 2, 3, 5 |
| 7 | Criar `test_procedures_structure.py` | RF06 | `_framework/tests/test_procedures_structure.py` | 4 |
| 8 | Espelhar no central (`_framework/` idêntico e symlink) e rodar os gates | RF07 | `central:_framework/*`, `central:.claude/skills/doc-traceability-framework` | 1, 2, 3, 4, 5, 6, 7 |

## Critérios de aceite / definição de pronto

Copiados da SPEC-DTF-0018, sem relaxamento. Comandos rodados a partir da
raiz do repositório (kit ou central). Todo item é verificável por
comando; o 14 é o único de perfil `manual`, por decisão registrada da
SPEC.

Coluna "Perfil esperado": `automatizado`, `manual` ou `n/a`, conforme o
template; a Evidência compara contra o "Perfil usado" (SDD-DTF-0036,
STRAT-DTF-0003 item 7/E5).

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 | `test $(wc -c < _framework/skills/doc-traceability-framework/SKILL.md) -le 9216 && echo OK` | imprime `OK` | automatizado |
| 2 | RF01, RF02 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k "size_budget or iron_law or rationalization or pointers" -q` | todos passam | automatizado |
| 3 | RF02 | `python3 _framework/scripts/check_renderings.py` | exit 0, sem "Iron Law ... diverge ou ausente" | automatizado |
| 4 | RF03 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k "references or moved_sections" -q` | todos passam | automatizado |
| 5 | RF03 | `ls _framework/skills/doc-traceability-framework/references/` | lista `audit.md`, `incidents.md`, `onboarding.md`, `workflow-rules.yaml` | automatizado |
| 6 | RF04 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k descriptions -q` | passa nas quatro skills | automatizado |
| 7 | RF05 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k repo_root_path -q` | passa (ou `skip` explícito só sem `git`) | automatizado |
| 8 | RF05 | `cd _framework/tests && cat "$(git rev-parse --show-toplevel)/_framework/procedures/verify-sdd.md" \| head -1` | imprime `# Verificação independente de SDD` | automatizado |
| 9 | RF06 | `python3 -m pytest _framework/tests/test_procedures_structure.py -q` | passa nos dois testes | automatizado |
| 10 | RF06 | `grep -n '^### 5\.\|^## Escalonado\|^## Descompassos\|^## Lições' _framework/procedures/verify-sdd.md` | a linha de `### 5.` tem número menor que as demais | automatizado |
| 11 | RF07 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k layout -q` | passa | automatizado |
| 12 | RF07 | `test -f .claude/skills/doc-traceability-framework/references/incidents.md && echo OK` | imprime `OK` | automatizado |
| 13 | RF07 | `diff -rq /home/michel/doc-traceability-framework/_framework /home/michel/doc-traceability-central/_framework \| grep -v __pycache__` | sem saída | automatizado |
| 14 | RF07 | Manual (perfil `manual`): abrir sessão do Claude Code na raiz do kit e executar `/skills` | lista `doc-traceability-framework`; se não listar, aplicar a alternativa do RF07 (manter o symlink de arquivo `.claude/skills/doc-traceability-framework/SKILL.md` e citar `references/` no `SKILL.md` por caminho a partir da raiz do repositório) e registrar o resultado na evidência | manual |
| 15 | Todos | `python3 _framework/scripts/render_prompts.py --check` | exit 0 (nenhum alvo gerado mudou) | automatizado |
| 16 | Todos | `python3 -m pytest _framework/tests -q` | suíte verde | automatizado |

## Instruções específicas para a IA implementadora

- **Sessão e branch.** Implementar somente em sessão separada, aberta no
  repositório do kit (`doc-traceability-framework`), em worktree próprio
  (`git worktree add` explícito; não confiar em `isolation: worktree`).
  Branch nomeada pelo id, por exemplo `sdd/SDD-DTF-0044-skills-enxutas`,
  levada a main por PR. Nunca commitar implementação em main. Cada commit
  cita `Refs: SDD-DTF-0044` (e `SPEC-DTF-0018`). O espelho do central é um
  PR separado, também por branch, e a implementação nunca acontece na
  sessão do central.
- **Ordem e paralelismo.** Seguir "Decomposição em tasks". Conferir com
  `python3 _framework/scripts/parallel_plan.py docs/sdd/SDD-DTF-0044.md`.
  Esta SDD não toca `workflow-rules.yaml` nem `render_prompts.py`; pode
  rodar em paralelo com as demais da frente de otimização.
- **Texto movido:** copiar as seções "Incidentes e postmortem",
  "Onboarding de projeto já existente" e "Auditoria de aderência" do
  `SKILL.md` atual sem reescrever, salvo a troca de "seção N de
  `references/workflow-rules.yaml`" por `workflow-rules.yaml:<chave>`.
  Leia o `SKILL.md` atual inteiro antes de reescrevê-lo.
- **Roteador:** medir com `wc -c` a cada edição; se passar de 9216, mover
  conteúdo para `references/`, nunca subir o teto. Manter os oito tipos
  ativos, os quatro níveis, "Transições válidas:" e "O que fazer em cada
  pedido comum". Nenhuma tabela "Racionalização", nenhum bloco "Origem",
  nenhuma citação "seção N". Rodar `check_renderings.py` depois.
- **Descriptions e linha final:** usar o texto exato de "Especificação
  técnica consolidada", contratos 1 e 4; conferir o comprimento medido.
- **`verify-sdd.md`:** copiar o arquivo atual para a fixture ANTES de
  editar. Só mover os três blocos e reescrever as três frases; qualquer
  outra linha alterada reprova `test_verify_sdd_reorder_preserves_lines`.
- **Symlink:** `git rm` do symlink de arquivo, criar o de pasta com alvo
  relativo `../../_framework/skills/doc-traceability-framework`. Não mexer
  nos symlinks de `handover`, `pickup`, `verify-sdd`. Rodar o critério 14
  (`/skills`); se a skill não listar, aplicar a alternativa da SPEC e
  registrar.
- **Testes:** nomes de função e constantes exatos do contrato 7; sem
  dependência nova; `pytest.skip` só quando faltar `git`, com motivo.
- **NÃO alterar:** `_framework/rules/workflow-rules.yaml`,
  `_framework/scripts/render_prompts.py`, `.claude/agents/sdd-verifier.md`,
  `AGENTS.md`, `docs/especificacao.md`, `universal.md`, prompts de Cursor
  e Copilot, `_framework/procedures/handover.md` e `pickup.md`,
  `prompts/onboarding-bootstrap.md`, `prompts/framework-audit.md`,
  qualquer arquivo gerado, nem `registry.yaml`/`registry.md`. Não criar
  abstração, config ou refactor além dos RF.
- **Espelho no central:** copiar byte a byte os mesmos arquivos de
  `_framework/` e recriar o symlink; conferir com o `diff -rq` do
  critério 13.
- **Verificação:** feita pela skill `verify-sdd` (agente `sdd-verifier`)
  em sessão separada da que implementou; quem implementou não preenche a
  Evidência como verificada.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções:
- [ ] RF01 a RF07 têm arquivo correspondente na implementação (nada da
      SPEC ficou de fora).
- [ ] Todo arquivo tocado aparece em "Decomposição em tasks" ou em
      "Especificação técnica consolidada"; arquivo não listado é escopo a
      registrar na SDD ou scope creep a remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra não
      pedido por RF.
- [ ] `workflow-rules.yaml`, `render_prompts.py`, `sdd-verifier.md` e
      arquivos gerados sem diff.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
Esta SDD ainda não foi implementada: nenhuma linha abaixo tem comando
rodado nem saída real. A verificação substitui cada "(pendente ...)" pela
saída real; nunca "deve passar" nem resultado de memória.

**Verificador independente:** {sim | não — mesma sessão que implementou}

Coluna "Sensor": falha de comportamento introduzida em espaço
descartável (lista em "Sensor de discriminação"); o teste tem que FALHAR
e voltar ao normal depois. Critério sem teste automatizado: "sem teste".
Coluna "Assertion (file:line)": caminho e linha da asserção que resolve o
critério, ou `n/a` para `manual`. Coluna "Perfil usado": repete o "Perfil
esperado" ou declara divergência com justificativa entre parênteses.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
| 1 | `test $(wc -c < _framework/skills/doc-traceability-framework/SKILL.md) -le 9216 && echo OK` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 2 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k "size_budget or iron_law or rationalization or pointers" -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 3 | `python3 _framework/scripts/check_renderings.py` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 4 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k "references or moved_sections" -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 5 | `ls _framework/skills/doc-traceability-framework/references/` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 6 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k descriptions -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 7 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k repo_root_path -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 8 | `cd _framework/tests && cat "$(git rev-parse --show-toplevel)/_framework/procedures/verify-sdd.md" \| head -1` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 9 | `python3 -m pytest _framework/tests/test_procedures_structure.py -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 10 | `grep -n '^### 5\.\|^## Escalonado\|^## Descompassos\|^## Lições' _framework/procedures/verify-sdd.md` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 11 | `python3 -m pytest _framework/tests/test_skill_md_consistency.py -k layout -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 12 | `test -f .claude/skills/doc-traceability-framework/references/incidents.md && echo OK` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 13 | `diff -rq /home/michel/doc-traceability-framework/_framework /home/michel/doc-traceability-central/_framework \| grep -v __pycache__` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 14 | Manual (perfil `manual`): abrir sessão do Claude Code na raiz do kit e executar `/skills` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | manual |
| 15 | `python3 _framework/scripts/render_prompts.py --check` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |
| 16 | `python3 -m pytest _framework/tests -q` | (pendente: SDD ainda não implementada; sem comando rodado) | sem teste rodado | Não | n/a | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0018 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0018.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
