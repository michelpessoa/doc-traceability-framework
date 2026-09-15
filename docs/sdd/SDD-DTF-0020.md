---
id: SDD-DTF-0020
type: SDD
title: "Hooks do harness que alcançam o modelo: SessionStart por stdout, PostToolUse por exit 2 e sensor de configuração"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-14"
updated: "2026-09-14"
relates_to: [SDD-DTF-0009, SDD-DTF-0018, SDD-DTF-0019]
source_docs:
  - id: "SPEC-DTF-0009"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0009.md"
consumption_instructions: "Compilada de SPEC-DTF-0009, RF01–RF06 (RF07–RF08 ficam em SDD-DTF-0021). Implementar só depois de SDD-DTF-0018 mergeada em main (RF03 depende do validate_state sem falso positivo). Branch sdd/SDD-DTF-0020-* a partir de main, PR, commits com Refs: SDD-DTF-0020. Arquivos gerados (.claude/settings.json, cópias da skill) só via render_prompts.py."
supersedes: null
superseded_by: null
tags: [tooling, harness, hooks, claude-code]
---

# Hooks do harness que alcançam o modelo: SessionStart por stdout, PostToolUse por exit 2 e sensor de configuração

## Resumo executivo

`SDD-DTF-0009` passou a gerar `.claude/settings.json` a partir de
`capabilities[].mechanization`. Checado em 2026-09-14 contra a
documentação oficial de hooks do Claude Code
(`https://code.claude.com/docs/en/hooks`), três dos quatro hooks gerados
não chegam ao modelo:

- `pickup_handoff` (SessionStart) e `write_handover` (PreCompact) são
  `type: "prompt"` — avaliador de turno único num modelo separado, que
  devolve decisão em JSON e não injeta texto na sessão.
  `test_render_prompts_mechanization.py:58` assegura `type == "prompt"`.
- `enforce_content_quality_gate` (PostToolUse) roda
  `framework_check.py --auto --report-only`: sempre exit 0, e o stdout de
  PostToolUse vai para o log de debug. Só exit 2 mostra stderr ao modelo.
- Todos usam caminho relativo `_framework/scripts/...`, que quebra depois
  de `cd` ou dentro de worktree.

Esta SDD troca os hooks para `type: "command"` com
`${CLAUDE_PROJECT_DIR}`, cria `hook_session_start.py` (instrução por
stdout) e `hook_post_edit.py` (feedback por stderr + exit 2, validando
só o arquivo editado), impede o gerador de voltar a produzir hook mudo e
cria `check_hooks.py` para reprovar `settings.json` escrito à mão com os
mesmos defeitos. Contexto: a camada de hooks dava sensação de cobertura
sem cobrir, e SDD-EVM-0013/0014/0015 chegaram a `implemented` com a
tabela de evidência vazia sem nenhum sinal durante a edição.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — SPEC-DTF-0009 é `sizing: medium` e nenhum critério do gate
`rfc_to_adr` se aplica: a mecanização por capacidade de `SDD-DTF-0009`
continua igual, é reversível por revert, não é cross-team, não troca
tecnologia. O tipo de hook é decidido pela documentação oficial, não por
trade-off.

## Requisitos consolidados

| RF-ID | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Pickup chega ao modelo no início da sessão | Quando uma sessão iniciar (qualquer origem) e existir `HANDOFF.md` na raiz do projeto ou em `docs/*/HANDOFF.md`, o sistema deve imprimir em stdout a instrução de usar a skill `pickup` citando o caminho de cada `HANDOFF.md` encontrado; se nenhum existir, o sistema não deve imprimir nada. |
| RF02 | Lembrete de handover depois de compactação | Quando uma sessão iniciar com origem `compact`, o sistema deve imprimir em stdout a instrução de atualizar `HANDOFF.md` com a skill `handover` se o trabalho do fluxo continuar em outra sessão. |
| RF03 | Violação de gate ao editar documento chega ao modelo | Quando uma ferramenta `Edit` ou `Write` alterar um arquivo `.md` cujo front-matter declara um `type` de documento do framework, o sistema deve rodar `validate_doc.check_document` nesse arquivo (e `validate_state.check_sdd` se `type` for `SDD`) e, havendo problema, escrever os problemas em stderr e sair com código 2; sem problema, deve sair com 0 sem saída. |
| RF04 | Gerador não produz hook mudo | Se alguma capacidade declarar `mechanization` de hook com a chave `prompt`, ou `hook_command` com caminho `_framework/` sem o prefixo `${CLAUDE_PROJECT_DIR}/`, então o sistema deve abortar `render_prompts.py` com mensagem citando a capacidade antes de escrever qualquer arquivo. |
| RF05 | Hooks independem do diretório corrente | O sistema deve referenciar todo script de hook gerado em `.claude/settings.json` como `${CLAUDE_PROJECT_DIR}/_framework/scripts/<script>`. |
| RF06 | Sensor de configuração de hooks | O sistema deve prover `check_hooks.py` que reprova um `settings.json` com hook `type: "prompt"` em SessionStart, PreCompact ou PostCompact, com hook PostToolUse cujo comando contém `--report-only`, com caminho `_framework/` sem `${CLAUDE_PROJECT_DIR}/`, ou com script referenciado inexistente; e `framework_check.py --auto` deve rodá-lo quando existir `.claude/settings.json` no diretório corrente. |

Casos de borda:

| Caso | RF | Comportamento esperado |
|---|---|---|
| `HANDOFF.md` na raiz e em `docs/EVM/` ao mesmo tempo | RF01 | Lista os dois caminhos, raiz primeiro |
| `CLAUDE_PROJECT_DIR` ausente do ambiente | RF01, RF02 | Usa o campo `cwd` do payload; sem ele, o diretório corrente do processo |
| Payload de stdin malformado ou vazio | RF01, RF02, RF03 | Exit 0 sem saída (falha aberta, mesmo princípio de `guard_bash.sh`) |
| Argumento de modo desconhecido | RF01, RF02 | Exit 0 sem saída; `check_hooks.py` pega a configuração errada |
| `file_path` ausente, arquivo inexistente ou não `.md` | RF03 | Exit 0 sem saída |
| `.md` sem front-matter (README) ou com `type` fora dos tipos do framework | RF03 | Exit 0 sem saída — `check_document` não é chamado |
| Documento `draft` com placeholder | RF03 | Aviso (não problema) em `validate_doc`; avisos não geram saída; exit 0 |
| SDD legada (criada antes da regra) em projeto com `framework_version` novo | RF03 | Sem problema após `SDD-DTF-0018` — por isso esta SDD depende dela |
| Exceção dentro de um validador | RF03 | stderr `hook_post_edit: erro interno — <exceção>`, exit 1 (não bloqueante, visível ao usuário e não ao modelo) |
| Sub-agent editando dentro de worktree | RF03, RF05 | `${CLAUDE_PROJECT_DIR}` continua no checkout principal: valida o arquivo do worktree com as regras do checkout principal (aceito) |
| `settings.json` com JSON quebrado | RF06 | Um problema `settings.json ilegível: <erro>`, exit 1 |
| Nenhum `registry.yaml` descoberto por `--auto` | RF06 | A checagem de hooks roda mesmo assim (antes da descoberta) |

Requisitos não funcionais:
- `hook_post_edit.py` termina em menos de 2 s por edição no kit e no
  central: valida um arquivo, nunca o repositório.
- Nenhum hook acessa rede.

Fora de escopo:
- `guard_bash.sh` por segmento e `check_commit.py` ignorando merge real
  (RF07, RF08) — `SDD-DTF-0021`.
- Hook `Stop` ou gatilho por percentual de contexto para handover: nenhum
  evento expõe uso de contexto; o gatilho de ~45% segue comportamental.
- Registry ↔ front-matter no hook de edição: o registry costuma ser
  atualizado num passo seguinte da mesma tarefa; continua no pre-commit e
  no CI.
- Sincronizar `.claude/` e `_framework/` no central e em projetos.
- Bump de `framework.version` (precedente SDD-DTF-0009 a 0019).
- `hook_command` de capacidade `artifact_type: command`
  (`audit_repo_adherence`): roda como comando Bash do modelo, não como
  hook; a checagem de RF04 vale só para `artifact_type` iniciando em
  `hook_`.

## Especificação técnica consolidada

### Contratos consumidos

- Payload JSON de hook no stdin: `cwd`, `hook_event_name`; em PostToolUse,
  `tool_name` e `tool_input.file_path`.
- Variável de ambiente `CLAUDE_PROJECT_DIR`.
- `framework_lib.load_rules`, `framework_lib.read_frontmatter`,
  `framework_lib.report`, `validate_doc.check_document(path) -> (problems,
  warnings)`, `validate_state.check_sdd(path) -> (problems, warnings)`.

### `_framework/scripts/hook_session_start.py` (novo)

```python
def project_root(payload: dict) -> Path: ...    # CLAUDE_PROJECT_DIR > payload["cwd"] > Path.cwd()
def find_handoffs(root: Path) -> list[Path]: ... # [root/HANDOFF.md] + sorted(root.glob("docs/*/HANDOFF.md")), só existentes
def main(argv: list[str]) -> int: ...            # argv[1] in {"pickup", "post-compact"}; sempre retorna 0
```

Saída de `pickup` (só se `find_handoffs` não vazio), numa linha:

```
HANDOFF.md encontrado em: <caminhos relativos à raiz, separados por vírgula>. Antes de qualquer outra coisa, use a skill pickup: confirme o status real dos ids citados e releia do disco os arquivos que vai alterar.
```

Saída de `post-compact`:

```
O contexto desta sessão foi compactado. Se o trabalho do fluxo vai continuar em outra sessão, use a skill handover para atualizar HANDOFF.md referenciando os ids dos documentos.
```

### `_framework/scripts/hook_post_edit.py` (novo)

```python
def framework_types() -> set[str]: ...  # document_types + legacy_document_types de load_rules()
def problems_for(path: Path) -> list[str]: ...
def main() -> int: ...  # 0 sem problema ou fora do escopo; 2 com problema; 1 em exceção
```

`problems_for`: lê o front-matter; se `type` não estiver em
`framework_types()`, retorna `[]`. Senão, soma os `problems` (nunca os
`warnings`) de `validate_doc.check_document(path)` e, se `type == "SDD"`,
de `validate_state.check_sdd(path)`.

stderr com exit 2:

```
framework: <caminho> viola gate(s) — corrija antes de seguir:
  - <problema 1>
  - <problema 2>
```

### `_framework/scripts/check_hooks.py` (novo)

```python
def check_settings(path: Path) -> list[str]: ...
def main() -> int: ...  # uso: check_hooks.py [settings.json] [--report-only]; default .claude/settings.json; retorna framework_lib.report(...)
```

Regras de `check_settings` (um problema por ocorrência, citando evento e
matcher):
1. `type: "prompt"` em `SessionStart`, `PreCompact` ou `PostCompact`.
2. Hook em `PostToolUse` cujo `command` ou algum item de `args` contém
   `--report-only`.
3. `command` ou item de `args` contendo `_framework/` sem começar por
   `${CLAUDE_PROJECT_DIR}/`.
4. Item iniciando por `${CLAUDE_PROJECT_DIR}/` cujo arquivo não existe,
   resolvendo `${CLAUDE_PROJECT_DIR}` como `path.resolve().parent.parent`.
5. JSON inválido: único problema `settings.json ilegível: <erro>`.

### `_framework/scripts/framework_check.py`

No ramo `--auto` (ou sem argumentos), **antes** de `discover`: se
`Path(".claude/settings.json")` existir, imprime `-- hooks do harness`,
roda `check_hooks.check_settings` e soma o resultado de
`framework_lib.report(..., report_only=report_only)` em `failures`. O
retorno antecipado "Nenhum registry.yaml encontrado" passa a respeitar
essas falhas.

### `_framework/scripts/render_prompts.py`

- `validate_mechanizations(rules)` (já existe — estender): para
  `artifact_type` iniciando em `hook_`, `SystemExit` citando o id da
  capacidade se `"prompt" in mech`; `SystemExit` se algum item de
  `hook_command` contiver `_framework/` sem começar por
  `${CLAUDE_PROJECT_DIR}/`. Continua rodando antes de escrever qualquer
  arquivo.
- `build_claude_settings(rules)`: remove o ramo `prompt`; agrupa por
  `(evento, matcher)` na ordem de aparição das capacidades dentro de cada
  evento; eventos em `HOOK_EVENT_ORDER` (inalterado); cada evento vira
  uma lista com um objeto por matcher.

### `_framework/rules/workflow-rules.yaml`, seção `capabilities`

Só os blocos `mechanization` abaixo mudam (demais campos intactos; a
chave `prompt` sai de `pickup_handoff` e `write_handover`; `write_handover`
troca `hook_precompact` por `hook_sessionstart` com matcher `compact`):

```yaml
- id: pickup_handoff
  mechanization:
    vendor: "claude-code"
    artifact_type: "hook_sessionstart"
    matcher: "*"
    hook_command: ["python3", "${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_session_start.py", "pickup"]
- id: write_handover
  mechanization:
    vendor: "claude-code"
    artifact_type: "hook_sessionstart"
    matcher: "compact"
    hook_command: ["python3", "${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_session_start.py", "post-compact"]
- id: enforce_content_quality_gate
  mechanization:
    vendor: "claude-code"
    artifact_type: "hook_posttooluse"
    matcher: "Edit|Write"
    hook_command: ["python3", "${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_post_edit.py"]
- id: enforce_branch_before_commit
  mechanization:
    hook_command: ["bash", "${CLAUDE_PROJECT_DIR}/_framework/scripts/guard_bash.sh"]
```

`enforcement_patterns` de `enforce_branch_before_commit` **não** muda
aqui (é da SDD-DTF-0021).

### Gerados por `python3 _framework/scripts/render_prompts.py` (nunca à mão)

- `.claude/settings.json`, conteúdo esperado (espaçamento segue o
  gerador):
  ```json
  {
    "hooks": {
      "SessionStart": [
        {"matcher": "*", "hooks": [{"type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_session_start.py", "pickup"]}]},
        {"matcher": "compact", "hooks": [{"type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_session_start.py", "post-compact"]}]}
      ],
      "PreToolUse": [
        {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash", "args": ["${CLAUDE_PROJECT_DIR}/_framework/scripts/guard_bash.sh"]}]}
      ],
      "PostToolUse": [
        {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/_framework/scripts/hook_post_edit.py"]}]}
      ]
    }
  }
  ```
- `_framework/skills/doc-traceability-framework/scripts/hook_session_start.py`,
  `hook_post_edit.py`, `check_hooks.py`, `framework_check.py`,
  `render_prompts.py` e `references/workflow-rules.yaml` (`sync_copies`).

### Testes

| RF | Arquivo | Casos mínimos |
|---|---|---|
| RF01, RF02 | `_framework/scripts/tests/test_hook_session_start.py` (novo; subprocess, repo em `tmp_path`, `CLAUDE_PROJECT_DIR` no env) | raiz com `HANDOFF.md`; só `docs/X/HANDOFF.md`; os dois (ordem raiz primeiro); nenhum (stdout vazio); `post-compact` (stdout não vazio); stdin inválido (exit 0) |
| RF03 | `_framework/scripts/tests/test_hook_post_edit.py` (novo; subprocess, documentos mínimos em `tmp_path` com `registry.yaml`) | arquivo `.py` (0); README sem front-matter (0); SPEC `draft` com placeholder (0, sem saída); SDD `implemented` criada depois de 2026-08-29 com evidência vazia (2, stderr cita o id); a mesma SDD com evidência preenchida (0); stdin inválido (0) |
| RF04, RF05 | `_framework/scripts/tests/test_render_prompts_mechanization.py` (alterar; a asserção da linha 58 passa a `type == "command"`) | SessionStart gera dois grupos (`*` e `compact`) com `type: "command"`; `prompt` em mechanization gera `SystemExit`; `hook_command` com `_framework/` relativo gera `SystemExit` |
| RF06 | `_framework/scripts/tests/test_check_hooks.py` (novo; `settings.json` em `tmp_path`) | um caso por regra (prompt em SessionStart, `--report-only` em PostToolUse, caminho relativo, script inexistente, JSON inválido), um válido, e o `.claude/settings.json` real do kit sem problema |

### Plano de implementação

1. `hook_session_start.py` e testes.
2. `hook_post_edit.py` e testes.
3. `render_prompts.py`: `validate_mechanizations` e
   `build_claude_settings`; atualizar o teste da linha 58.
4. `workflow-rules.yaml`: os quatro blocos acima.
5. `check_hooks.py`, testes, integração em `framework_check.py --auto`.
6. `python3 _framework/scripts/render_prompts.py` e conferir o
   `.claude/settings.json` gerado contra o esperado.
7. Sensor manual em sessão real (critério 9).

Rollout: PR no kit; sync para o central em PR separado depois do merge.
Rollback: reverter o PR restaura gerador e `settings.json` anteriores;
nenhum dado migra. Observabilidade: `claude --debug` mostra execução e
exit de cada hook; CI e pre-commit reprovam configuração inválida via
`framework_check.py --auto`.

Riscos:
- Feedback de exit 2 no meio de edição em várias etapas (ex.: `status`
  `implemented` antes da tabela) — é a ordem que `SDD-DTF-0019` passo 5
  proíbe; o feedback empurra para a ordem certa.
- Projeto copia `settings.json` sem os scripts — `check_hooks.py`
  reprova script inexistente.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01, RF02 | `python3 -m pytest _framework/scripts/tests/test_hook_session_start.py -v` | todos passam, 6 casos ou mais |
| 2 | RF03 | `python3 -m pytest _framework/scripts/tests/test_hook_post_edit.py -v` | todos passam, 6 casos ou mais |
| 3 | RF04, RF05 | `python3 -m pytest _framework/scripts/tests/test_render_prompts_mechanization.py -v` | todos passam |
| 4 | RF06 | `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | todos passam, 7 casos ou mais |
| 5 | RF05 — gerado sem prompt nem caminho relativo | `python3 -c "import json; s=json.load(open('.claude/settings.json'))['hooks']; hs=[h for ev in s.values() for g in ev for h in g['hooks']]; print(sorted(s), {h['type'] for h in hs}, all(a.startswith('\x24{CLAUDE_PROJECT_DIR}/') for h in hs for a in h['args'] if '_framework/' in a))"` | `['PostToolUse', 'PreToolUse', 'SessionStart'] {'command'} True` |
| 6 | RF06 — sensor no `--auto` com o kit real | `python3 _framework/scripts/check_hooks.py && python3 _framework/scripts/framework_check.py --auto` | exit 0; saída contém `-- hooks do harness` |
| 7 | RF03 discrimina o caso real | bloco C7 abaixo | primeira execução exit `2` com stderr citando `SDD-DTF-0017`; segunda exit `0` sem saída |
| 8 | Regressão e renderizações | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts && python3 -m pytest && python3 _framework/scripts/render_prompts.py --check && python3 _framework/scripts/check_renderings.py` | exit 0 em todos |
| 9 | RF01, RF03 em sessão real | manual: sessão nova de Claude Code no kit com `HANDOFF.md` na raiz; depois, pedir para esvaziar a tabela de evidência de uma cópia de SDD `implemented` | primeira resposta cita pickup; o modelo relata o stderr do hook; trecho de `claude --debug` registrado na evidência |

Bloco C7 (usa redirecionamento, fica fora da tabela) — simula a
SDD-EVM-0013 numa cópia descartável da SDD-DTF-0017 e chama o hook com o
payload que o Claude Code envia:

```bash
tmp=$(mktemp -d) && cp -r docs/sdd "$tmp/" && \
python3 - "$tmp/sdd/SDD-DTF-0017.md" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
s = re.sub(r"(\| # \|[^\n]*\| Sensor \| Passou\? \|\n\|[-| ]+\|\n)(?:\|[^\n]*\n)+", r"\1", s, count=1)
open(p, "w").write(s)
PY
printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$tmp/sdd/SDD-DTF-0017.md" | python3 _framework/scripts/hook_post_edit.py; echo "exit=$?"
printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$PWD/docs/sdd/SDD-DTF-0017.md" | python3 _framework/scripts/hook_post_edit.py; echo "exit=$?"
```

## Instruções específicas para a IA implementadora

- Implementar só depois de `SDD-DTF-0018` mergeada em `main`; se não
  estiver, parar e avisar.
- Hooks só `type: "command"`. Não reintroduzir `type: "prompt"` para
  instruir o modelo, e não declarar hook funcionando sem o critério 9.
- Não editar à mão `.claude/settings.json` nem as cópias em
  `_framework/skills/doc-traceability-framework/`; rodar
  `python3 _framework/scripts/render_prompts.py` e commitar o gerado no
  mesmo PR.
- Não mexer em `enforcement_patterns`, `build_guard_bash`,
  `guard_bash.sh` nem `check_commit.py` — são da `SDD-DTF-0021`.
- Não alterar `rule_applies` nem `rule_applies_since_date` em
  `framework_lib.py`.
- `hook_post_edit.py` nunca imprime warnings nem valida registry.
- Scripts novos seguem o padrão dos existentes: `sys.path` relativo ao
  próprio arquivo para importar `framework_lib`, docstring de módulo
  citando `SDD-DTF-0020`.
- Não escrever conteúdo com padrão do `guard_bash.sh` atual (ex.:
  `push --force`) por heredoc no Bash: escrever o arquivo pela ferramenta
  de edição e só executá-lo.
- Branch `sdd/SDD-DTF-0020-hooks-modelo` a partir de `main`, PR — nunca
  commit direto (gate seção 14). Conventional Commits com
  `Refs: SDD-DTF-0020`.
- Verificação (`verify-sdd`) em sessão ou sub-agent separado; a tabela de
  evidência vai **nesta SDD**.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] RF01–RF06 têm código e teste correspondentes.
- [ ] Arquivos tocados só entre: `_framework/scripts/hook_session_start.py`,
      `_framework/scripts/hook_post_edit.py`,
      `_framework/scripts/check_hooks.py`,
      `_framework/scripts/framework_check.py`,
      `_framework/scripts/render_prompts.py`,
      `_framework/rules/workflow-rules.yaml`,
      `_framework/scripts/tests/test_hook_session_start.py`,
      `_framework/scripts/tests/test_hook_post_edit.py`,
      `_framework/scripts/tests/test_check_hooks.py`,
      `_framework/scripts/tests/test_render_prompts_mechanization.py`,
      `.claude/settings.json` (gerado), cópias geradas em
      `_framework/skills/doc-traceability-framework/`, e esta SDD e o
      registry (status/evidência).
- [ ] Nenhuma mudança em `guard_bash.sh`, `check_commit.py`,
      `enforcement_patterns` ou regra/gate além do descrito.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
A tabela fica **nesta seção**; `docs/sdd/validation.md` é o relatório
complementar.

**Verificador independente:** —

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0009 (RF01–RF06) |
| relates_to | SDD-DTF-0009 (origem da mecanização), SDD-DTF-0018 (dependência: validador sem falso positivo), SDD-DTF-0019 (passo 5, mesma ordem que RF03 reforça) |
