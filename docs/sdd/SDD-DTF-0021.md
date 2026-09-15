---
id: SDD-DTF-0021
type: SDD
title: "Guardrails sem falso positivo: guard_bash por subcomando e check_commit ignorando merge real"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-14"
updated: "2026-09-14"
relates_to: [SDD-DTF-0009, SDD-DTF-0020]
source_docs:
  - id: "SPEC-DTF-0009"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0009.md"
consumption_instructions: "Compilada de SPEC-DTF-0009, RF07–RF08 (RF01–RF06 estão em SDD-DTF-0020). Independente da SDD-DTF-0020 em comportamento, mas implementar depois dela mergeada: as duas mexem em render_prompts.py e workflow-rules.yaml. Branch sdd/SDD-DTF-0021-* a partir de main, PR, commits com Refs: SDD-DTF-0021. guard_bash.sh e cópias da skill só via render_prompts.py."
supersedes: null
superseded_by: null
tags: [tooling, harness, guardrails, claude-code]
---

# Guardrails sem falso positivo: guard_bash por subcomando e check_commit ignorando merge real

## Resumo executivo

Dois sensores do kit geraram falso positivo observado em 2026-09-14:

- **`_framework/scripts/guard_bash.sh`** casa os padrões de
  `enforcement_patterns` contra o comando Bash inteiro. Um comando que
  enviava a branch `docs/x` e, no mesmo comando, abria PR com
  `gh pr create --base main` casou `*"push"*" main"*` e foi bloqueado como
  "push direto em main". O mesmo acontece com texto de descrição de PR ou
  mensagem de commit que cite as duas palavras.
- **`_framework/scripts/check_commit.py`** só pula merge pelo assunto
  (`Merge `/`Revert `). No `viverMelhor`, o merge local
  `merge verify/SDD-EVM-0014 into develop` (minúsculo) reprova como fora
  de Conventional Commits.

Falso positivo recorrente ensina a contornar o guardrail (quebrar
comando, reescrever texto) e tira a confiança nele. Esta SDD faz o
`guard_bash.sh` avaliar cada subcomando isolado, com padrões ancorados no
início do segmento, e faz o `check_commit.py` reconhecer merge pelo
número de pais (ou por `MERGE_HEAD`), não pelo assunto.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — SPEC-DTF-0009 é `sizing: medium` e nenhum critério do gate
`rfc_to_adr` se aplica: correção de casamento textual em dois sensores
existentes, reversível por revert.

## Requisitos consolidados

| RF-ID | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF07 | guard_bash avalia cada subcomando | Quando o comando Bash tiver mais de um segmento (separados por E lógico, OU lógico, ponto e vírgula, pipe ou quebra de linha), o sistema deve avaliar os padrões de `enforcement_patterns` contra cada segmento isolado, com `git -C <caminho>` normalizado para `git`, e os padrões de push devem exigir que o segmento comece por `git push`. |
| RF08 | check_commit ignora merge real | Quando `check_commit.py` avaliar um commit com mais de um pai (modo `--range` ou `--last`) ou rodar como `commit-msg` com `MERGE_HEAD` presente, o sistema deve pular a checagem de formato desse commit, independente do assunto. |

Casos de borda:

| Caso | RF | Comportamento esperado |
|---|---|---|
| `gh pr create --body "...push direto em main..."` | RF07 | Segmento não começa com `git`: não bloqueia |
| `git -C /repo push origin main` | RF07 | Bloqueia: normalizado para `git push origin main` |
| `git commit -m "evita push em main agora"` | RF07 | Não bloqueia: segmento começa por `git commit` |
| Linha de heredoc que comece por `git push`/`rm -rf` | RF07 | Ainda bloqueia — limite aceito do casamento textual; escrever o arquivo pela ferramenta de edição e só executá-lo |
| Separador dentro de string entre aspas (ex.: `-m "a; git push origin main"`) | RF07 | O trecho depois do `;` vira segmento e bloqueia — limite aceito (divisão textual, sem parser de shell); falha para o lado seguro |
| `git push` sem argumentos estando em `main` | RF07 | Fora do alcance do padrão textual — coberto pelo `.githooks/pre-push` existente |
| stdin não é JSON ou sem `tool_input.command` | RF07 | Exit 0 sem saída (falha aberta, comportamento atual) |
| Merge com assunto `Merge pull request #N` | RF08 | Continua pulado pela regra de assunto existente |
| `commit-msg` fora de repositório git (`git rev-parse` falha) | RF08 | Segue checando a mensagem normalmente |
| Commit comum (um pai) fora do formato | RF08 | Continua reprovando |

Fora de escopo:
- Hooks que alcançam o modelo, `check_hooks.py`, `hook_command` com
  `${CLAUDE_PROJECT_DIR}` (RF01–RF06) — `SDD-DTF-0020`.
- Parser de shell (aspas, subshell, `$(...)`): a divisão é textual por
  decisão da SPEC.
- Novos padrões de bloqueio ou mudança das mensagens de `deny`.
- `.githooks/pre-push` e `.githooks/commit-msg`: não mudam.
- Sincronizar central e projetos; bump de `framework.version`.

## Especificação técnica consolidada

### `_framework/rules/workflow-rules.yaml` — `enforce_branch_before_commit.enforcement_patterns`

Só este campo muda (`hook_command` é da SDD-DTF-0020; `message` intacta):

```yaml
enforcement_patterns:
  - pattern: '"git push"*--force*|"git push"*" -f"|"git push"*" -f "*'
    message: "force-push detectado. Use PR normal."
  - pattern: '"git push"*" main"|"git push"*" main "*|"git push"*":main"*|"git push"*" main:"*'
    message: "push direto em main. Abra PR."
  - pattern: '"git reset --hard"*'
    message: "reset --hard é destrutivo. Confirme com o usuário antes."
  - pattern: '"rm -rf ."*|"rm -rf /"*|"rm -rf ~"*'
    message: "rm -rf de escopo amplo. Confirme com o usuário antes."
```

Os padrões não têm `*` inicial: aplicam-se a segmentos já normalizados.
Validados em 2026-09-14 numa simulação em bash contra os 17 casos da
tabela de testes (17/17); reconferidos na redação desta SDD com o
cabeçalho por segmento e o laço `done <<<"$segments"` gerados a partir
do `build_guard_bash` atual: 17/17, stdin inválido exit 0, bloco C4
`exit=0` / `exit=2`.

### `_framework/scripts/render_prompts.py` — `build_guard_bash(rules)`

O trecho Python do cabeçalho, depois de extrair `command`, divide em
segmentos e imprime um por linha:

```python
import re
for s in re.split(r"&&|\|\||;|\||\n", command):
    s = re.sub(r"^git\s+-C\s+\S+\s+", "git ", s.strip())
    if s:
        print(s)
```

A variável do shell passa a se chamar `segments`; o
`[ -z "$segments" ] && exit 0` substitui o teste atual. O `case` é
aplicado a cada segmento num laço **sem subshell**, para o `exit 2` de
`deny` encerrar o script:

```bash
while IFS= read -r segment; do
  case "$segment" in
    <padrão>)
      deny "<mensagem>" ;;
  esac
done <<<"$segments"
```

(não usar `printf ... | while`: o `exit` dentro do pipe só sai do
subshell e o comando passaria.) Demais linhas do cabeçalho (comentário,
`set -euo pipefail`, `deny`) ficam como estão; o comentário ganha uma
linha citando a avaliação por segmento e `SDD-DTF-0021`.

`_framework/scripts/guard_bash.sh` é regenerado por
`python3 _framework/scripts/render_prompts.py` — nunca editado à mão.
`test_build_guard_bash_padroes_identicos_ao_atual` continua valendo
(gerado == disco).

### `_framework/scripts/check_commit.py`

- `messages_from_range(rev_range)`: formato
  `%H%x00%P%x00%B%x00---END---`; commit cujo `%P` tem mais de um hash
  (separados por espaço) não entra no resultado. Assinatura e retorno
  (`list[tuple[str, str]]`) inalterados; `--last` herda o comportamento.
- `main()`, modo arquivo (`commit-msg`): antes de ler a mensagem, roda
  `git rev-parse --git-path MERGE_HEAD`; se o comando der certo e o
  caminho devolvido existir como arquivo, retorna 0 sem checar. Falha do
  `git` (fora de repositório) segue para a checagem normal.
- `check_message` e a regra de assunto `Merge `/`Revert ` não mudam.

### Testes

| RF | Arquivo | Casos (exit esperado) |
|---|---|---|
| RF07 | `_framework/scripts/tests/test_guard_bash.py` (novo; subprocess `bash _framework/scripts/guard_bash.sh` com payload `{"tool_input":{"command": ...}}` no stdin, parametrizado) | `git push -u origin feat/x && gh pr create --base main` (0); `git push origin main` (2); `git -C /repo push origin main` (2); `git push --force origin feat/x` (2); `gh pr create --body "bloqueia push direto em main"` (0); `cd /x && git reset --hard origin/main` (2); `echo ok; rm -rf /` (2); `git status` (0); `git push origin HEAD:main` (2); `git push -f` (2); `git push origin feature/maintenance` (0); `git push -u origin docs/sdd-dtf-0018-validate-state-data` (0); `git commit -m "fix: evita push em main"` (0); `git commit -m "evita push em main agora"` (0); `git -C /repo commit -m "x push main y"` (0); `git -C /repo reset --hard HEAD` (2); `git -C /repo push -f origin feat/x` (2); e stdin inválido (0) |
| RF08 | `_framework/scripts/tests/test_check_commit.py` (novo; repo git temporário em `tmp_path`) | `--range` com merge local `merge verify/x into develop` feito com `git merge --no-ff -m` (sem problema, exit 0); `--range` com commit comum fora do formato (problema, exit 1); modo arquivo com `MERGE_HEAD` presente e mensagem fora do formato (exit 0); modo arquivo sem `MERGE_HEAD` e mensagem fora do formato (exit 1) |

### Plano de implementação

1. `enforcement_patterns` em `workflow-rules.yaml` e `build_guard_bash`
   em `render_prompts.py`.
2. `python3 _framework/scripts/render_prompts.py` (regenera
   `guard_bash.sh` e cópias da skill).
3. `test_guard_bash.py`.
4. `check_commit.py` e `test_check_commit.py`.

Rollout: PR no kit, depois da SDD-DTF-0020 mergeada; sync para o central
em PR separado. Rollback: revert do PR restaura padrões, gerador e
`guard_bash.sh`; nenhum dado migra.

Riscos:
- **Padrão ancorado deixa passar forma não prevista** (ex.:
  `command git push origin main`, `sudo git push`). Mitigação: o
  `.githooks/pre-push` continua recusando push em `main` no nível do git;
  o guard é camada extra, não a única.
- **Divisão textual corta string com separador** — falha para o lado
  seguro (bloqueia a mais), registrado nos casos de borda.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF07 | `python3 -m pytest _framework/scripts/tests/test_guard_bash.py -v` | 18 casos ou mais, todos passam |
| 2 | RF08 | `python3 -m pytest _framework/scripts/tests/test_check_commit.py -v` | 4 casos ou mais, todos passam |
| 3 | RF07 — gerado bate com o YAML e sem laço em pipe | `python3 _framework/scripts/render_prompts.py --check && grep -cF 'done <<<"$segments"' _framework/scripts/guard_bash.sh` | exit 0; contagem `1` |
| 4 | RF07 discrimina o incidente real | bloco C4 abaixo | primeira linha `exit=0`, segunda `exit=2` |
| 5 | RF08 no histórico real do kit | `python3 _framework/scripts/check_commit.py --last 30` | exit 0 |
| 6 | Regressão e renderizações | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts && python3 -m pytest && python3 _framework/scripts/check_renderings.py && python3 _framework/scripts/framework_check.py --auto` | exit 0 em todos |

Bloco C4 (monta o payload por Python para não colocar o comando de
incidente literal na linha do Bash) — o comando que foi bloqueado em
2026-09-14 tem que passar; o push direto tem que continuar bloqueado:

```bash
python3 -c 'import json; print(json.dumps({"tool_input": {"command": "git " + "push -u origin docs/x && gh pr create --base " + "main"}}))' | bash _framework/scripts/guard_bash.sh; echo "exit=$?"
python3 -c 'import json; print(json.dumps({"tool_input": {"command": "git -C /repo " + "push origin " + "main"}}))' | bash _framework/scripts/guard_bash.sh; echo "exit=$?"
```

## Instruções específicas para a IA implementadora

- Implementar só depois de `SDD-DTF-0020` mergeada em `main` (conflito em
  `render_prompts.py` e `workflow-rules.yaml`); se não estiver, parar e
  avisar.
- Editar em `workflow-rules.yaml` só `enforcement_patterns` de
  `enforce_branch_before_commit`.
- Não editar à mão `guard_bash.sh` nem as cópias em
  `_framework/skills/doc-traceability-framework/`; rodar
  `python3 _framework/scripts/render_prompts.py` e commitar o gerado no
  mesmo PR.
- `test_guard_bash.py` contém textos que casam o guard atual: escrever o
  arquivo pela ferramenta de edição, nunca por heredoc no Bash.
- Enquanto o guard novo não estiver gerado, não colocar o envio da branch
  e `--base main` no mesmo comando Bash.
- Branch `sdd/SDD-DTF-0021-guardrails` a partir de `main`, PR — nunca
  commit direto (gate seção 14). Conventional Commits com
  `Refs: SDD-DTF-0021`.
- Verificação (`verify-sdd`) em sessão ou sub-agent separado; a tabela de
  evidência vai **nesta SDD**.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] RF07 e RF08 têm código e teste correspondentes.
- [ ] Arquivos tocados só entre: `_framework/rules/workflow-rules.yaml`,
      `_framework/scripts/render_prompts.py`,
      `_framework/scripts/guard_bash.sh` (gerado),
      `_framework/scripts/check_commit.py`,
      `_framework/scripts/tests/test_guard_bash.py`,
      `_framework/scripts/tests/test_check_commit.py`, cópias geradas em
      `_framework/skills/doc-traceability-framework/`, e esta SDD e o
      registry (status/evidência).
- [ ] Nenhuma mudança em hooks do `.claude/settings.json`, nos
      `.githooks/`, nas mensagens de `deny` ou em regra/gate além do
      descrito.

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
| source_docs | SPEC-DTF-0009 (RF07–RF08) |
| relates_to | SDD-DTF-0009 (origem de `guard_bash.sh` gerado), SDD-DTF-0020 (mesmos arquivos; ordem de implementação) |
