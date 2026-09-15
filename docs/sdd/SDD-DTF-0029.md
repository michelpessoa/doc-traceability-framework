---
id: SDD-DTF-0029
type: SDD
title: "test_check_hooks: token com prefixo de variável falso (substring, não prefixo válido) continua reprovado"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: [SDD-DTF-0027]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Escopo mecânico: um teste novo em test_check_hooks.py, nenhuma mudança em check_hooks.py. Implementar em branch sdd/SDD-DTF-0029-* a partir de main, PR, commits com Refs: SDD-DTF-0029."
supersedes: null
superseded_by: null
tags: [tooling, testes, check_hooks, gate_scope_verification]
---

# test_check_hooks: token com prefixo de variável falso (substring, não prefixo válido) continua reprovado

## Resumo executivo

Gap de cobertura de teste, achado em verificação independente e
registrado em `docs/sdd/LESSONS.md`, seção "2026-09-15 — SDD-DTF-0027:
risco nomeado na SDD sem teste que o reprove": `SDD-DTF-0027` tokenizou
`command` (`_framework/scripts/check_hooks.py`) com `shlex.split()` e
passou a checar, token a token, se algum começa por um dos
`PROJECT_DIR_PREFIXES` (`${CLAUDE_PROJECT_DIR}/` ou
`$CLAUDE_PROJECT_DIR/`) usando `token.startswith(prefix)` — prefixo
exato, não substring. A própria SDD-DTF-0027 nomeia esse risco na seção
"Riscos": um `command` malicioso poderia tentar se disfarçar como
`"$CLAUDE_PROJECT_DIR_FALSO/x.py"`, mitigado porque `startswith` exige o
prefixo exato (barra incluída), "não apenas conter a substring". O código
está correto (confirmado por verificação independente, fora desta sessão)
e não é alterado aqui.

O que falta é cobertura: nenhum dos 11 testes atuais de
`test_check_hooks.py` usa um `command` que **contém** a substring
`CLAUDE_PROJECT_DIR` sem ser, de fato, um prefixo válido. Mutar a
condição de `token.startswith(p)` para `"CLAUDE_PROJECT_DIR" in token`
passa nos 11 testes atuais, porque nenhum caso testado tem esse tipo de
token — a mutação não é discriminada, apesar do risco estar nomeado e
mitigado na SDD de origem.

`sizing: small` — 1 teste novo em 1 arquivo, sem mudança de código de
produção, regra, gate ou fluxo: fecha a lacuna de cobertura para que a
suíte volte a discriminar essa classe de mutação.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — reforço de cobertura de teste, nenhum critério do gate
`rfc_to_adr` se aplica.

## Requisitos consolidados

- **RF1**: `_framework/scripts/tests/test_check_hooks.py` ganha um teste
  novo que chama `check_settings` com um `command` contendo o token
  `$CLAUDE_PROJECT_DIR_FALSO/_framework/scripts/hook.py` (variável de
  nome parecido, mas diferente — não é um prefixo válido de
  `PROJECT_DIR_PREFIXES`, só compartilha o texto `CLAUDE_PROJECT_DIR`
  como substring).
- **RF2**: o teste novo faz uma asserção exata sobre o retorno de
  `check_settings`: exatamente 1 problema, citando o evento (`PreToolUse`)
  e "sem o prefixo" — o mesmo formato de mensagem usado pelos testes
  já existentes de reprovação (`test_caminho_relativo`,
  `test_command_shell_sem_referencia_reprova`).
- **RF3**: o teste novo discrimina a mutação de `check_hooks.py` que
  trocar o critério de `token.startswith(p)` (prefixo exato, dentro de
  `next(...)` que calcula `prefix`) por checagem de substring solta
  (`"CLAUDE_PROJECT_DIR" in token`). Com a mutação aplicada, o teste novo
  falha; sem ela (código atual, já `approved` em `SDD-DTF-0027`), passa.
  Verificado nesta sessão em espaço descartável (`git checkout --` para
  restaurar, nunca stash).
- **RF4**: nenhuma mudança em `_framework/scripts/check_hooks.py` — o
  código já está correto; esta SDD é só teste.
- **RF5**: os 11 testes existentes de `test_check_hooks.py` continuam
  passando sem alteração.

Casos de borda:
- O teste novo reaproveita o padrão de fixture já usado pelos testes de
  `SDD-DTF-0027` (`_settings`, `tmp_path`, hook `PreToolUse`/`Bash`) para
  ficar consistente com o resto do arquivo — não inventa uma segunda
  convenção de fixture.
- O token de teste ainda contém `_framework/`, então a regra 3 (mensagem
  "sem o prefixo") é a que deve disparar — não a regra 4 (script
  inexistente), que só dispara quando `prefix is not None`. Isso é
  justamente o que a asserção de RF2 confirma.

Fora de escopo:
- Alterar `check_settings`, `_tokens`, `PROJECT_DIR_PREFIXES` ou qualquer
  outra função/constante de `check_hooks.py`.
- Alterar `validate_state.py`, `test_validate_state.py` ou qualquer outro
  script — reservado a `SDD-DTF-0028`, em andamento em paralelo por outro
  agente.
- Sincronizar a cópia de `_framework/skills/doc-traceability-framework/`
  — a cópia sincronizada cobre `check_hooks.py` (arquivo de origem), não
  `test_check_hooks.py` (não há cópia de testes na skill); nenhuma
  mudança em `check_hooks.py` significa nada a sincronizar aqui,
  confirmado por `render_prompts.py --check` já em dia antes e depois
  desta mudança.
- Bump de `framework.version`.

## Especificação técnica consolidada

**`_framework/scripts/tests/test_check_hooks.py`** — um teste novo,
próximo dos três testes de `SDD-DTF-0027`:

```python
def test_command_shell_prefixo_falso_reprova(tmp_path):
    """SDD-DTF-0029: token que CONTÉM a substring "CLAUDE_PROJECT_DIR" mas
    não é um prefixo válido (nome de variável diferente, só compartilha o
    texto) continua reprovado — discrimina mutação que trocasse
    `token.startswith(prefix)` por `"CLAUDE_PROJECT_DIR" in token`."""
    hooks = {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 $CLAUDE_PROJECT_DIR_FALSO/_framework/scripts/hook.py",
                    }
                ],
            }
        ]
    }
    problems = check_settings(_settings(tmp_path, hooks))
    assert len(problems) == 1
    assert "PreToolUse" in problems[0] and "sem o prefixo" in problems[0]
```

- Reaproveita `check_settings` e `_settings`, já importados/definidos no
  topo do arquivo — nenhum import ou fixture nova.
- Nenhuma outra função ou arquivo é tocado.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1–RF2, RF5 | `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | todos os testes `passed`, exit 0 (12 testes: 11 já existentes + 1 novo) |
| 2 | RF3 — sensor de discriminação | trocar `token.startswith(p)` por `"CLAUDE_PROJECT_DIR" in token` no cálculo de `prefix` em `check_hooks.py` (espaço descartável), rodar o comando do critério 1, restaurar com `git checkout --` | o teste novo falha (junto com `test_command_shell_com_prefixo_sem_chaves_entre_aspas`, que também depende do prefixo exato); restaurado, os dois voltam a passar |
| 3 | RF4 — sem mudança de produção | `git diff --stat main -- _framework/scripts/check_hooks.py` | saída vazia (nenhuma linha alterada) |
| 4 | Regressão geral (self-host) | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.` e suíte inteira `passed` |
| 5 | Paridade com o CI | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | exit 0 |
| 6 | Cópia da skill não afetada | `python3 _framework/scripts/render_prompts.py --check` | exit 0 — nenhuma mudança em `check_hooks.py`, nada a sincronizar |

## Instruções específicas para a IA implementadora

- Não alterar `check_settings`, `_tokens`, `PROJECT_DIR_PREFIXES` nem
  qualquer outra função/constante de `check_hooks.py` — o código já está
  correto (verificação independente fora desta SDD confirmou).
- Não tocar `validate_state.py` nem `test_validate_state.py` — reservado
  a `SDD-DTF-0028`, em andamento em paralelo por outro agente.
- Sensor de discriminação: trocar temporariamente
  `prefix = next((p for p in PROJECT_DIR_PREFIXES if token.startswith(p)), None)`
  por `prefix = next((p for p in PROJECT_DIR_PREFIXES if "CLAUDE_PROJECT_DIR" in token), None)`
  em `check_hooks.py` (espaço descartável, nunca commit), confirmar que o
  teste novo falha, restaurar com
  `git checkout -- _framework/scripts/check_hooks.py` (nunca `git
  stash`, que é compartilhado entre sessões/worktrees).
- Branch `sdd/SDD-DTF-0029-*` a partir de `main`, PR — nunca commit
  direto (gate seção 14). Commits em Conventional Commits com
  `Refs: SDD-DTF-0029`.
- `docs/sdd/registry.yaml` pode conflitar no merge do PR com
  `SDD-DTF-0028`, criada em paralelo por outro agente — é esperado,
  resolvido pelo humano no merge, não é bug desta SDD.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Arquivos tocados: `_framework/scripts/tests/test_check_hooks.py`
      e este documento (`docs/sdd/SDD-DTF-0029.md`) mais a entrada
      correspondente em `docs/sdd/registry.yaml` — qualquer outro arquivo
      é escopo não registrado ou scope creep.
- [x] Nenhuma abstração, config ou refactor extra sem requisito acima.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida nesta mesma sessão porque o sizing é `small` e a verificação
mecânica (sensor de mutação) já foi rodada como parte da implementação;
a verificação independente completa (skill `verify-sdd`, quem
implementou não verifica) fica para outra sessão antes de mover para
`implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | `12 passed in 1.24s`, exit 0 (12º teste: `test_command_shell_prefixo_falso_reprova`) | n/a (checagem estática) | sim |
| 2 | Editado o cálculo de `prefix` em `check_hooks.py`: `token.startswith(p)` → `"CLAUDE_PROJECT_DIR" in token` (espaço descartável, não commitado); rodado `python3 -m pytest _framework/scripts/tests/test_check_hooks.py -v` | `2 failed, 10 passed` — falharam `test_command_shell_com_prefixo_sem_chaves_entre_aspas` (mensagem `script referenciado inexistente` em vez de `[]`, porque `prefix` deixa de ser `None` e a regra 4 dispara sobre um slice errado) e `test_command_shell_prefixo_falso_reprova` (mesma causa: `AssertionError` — a mensagem virou `script referenciado inexistente: .../LSO/_framework/scripts/hook.py.`, não mais `sem o prefixo`, então `len(problems) == 1` ainda bate mas o texto esperado não); restaurado com `git checkout -- _framework/scripts/check_hooks.py`, `12 passed in 0.10s` de novo | Mutação aplicada de fato e revertida de fato, não simulada | sim |
| 3 | `git diff --stat main -- _framework/scripts/check_hooks.py` | saída vazia, exit 0 | Confirma nenhuma mudança de produção nesta SDD | sim |
| 4 | `python3 _framework/scripts/framework_check.py --auto && python3 -m pytest` | `✅ Todas as verificações do framework passaram.`; suíte `81 passed in 3.11s`, exit 0 | Regressão geral; lógica nova coberta pelo sensor do critério 2 | sim |
| 5 | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts` | `All checks passed!`; `21 files already formatted`; `Success: no issues found in 21 source files`, exit 0 | Checagem estática de paridade com o CI, sem sensor dedicado | sim |
| 6 | `python3 _framework/scripts/render_prompts.py --check` | exit 0; todas as cópias, inclusive `check_hooks.py`, `sincronizado` | Confirma que a ausência de mudança em `check_hooks.py` não deixou a cópia divergente | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0027 (fecha o gap de cobertura do risco nomeado — e não testado — na seção "Riscos" da mesma) |
