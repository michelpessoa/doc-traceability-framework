---
id: SDD-DTF-0009
type: SDD
title: "Mecanização de capacidades: hooks, agent e command gerados por fornecedor"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-03"
updated: "2026-09-03"
relates_to: [SDD-DTF-0007, SDD-DTF-0006]
source_docs:
  - id: "SPEC-DTF-0006"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0006.md"
  - id: "ADR-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0001.md"
consumption_instructions: "Leia SPEC-DTF-0006 inteira (Parte 1 e Parte 2) antes de tocar em arquivo — esta SDD consolida, não substitui, os contratos técnicos lá descritos. Mesmo padrão FULL_TARGETS de SDD-DTF-0007/SDD-DTF-0008: builders geram arquivo inteiro, sem marcador de bloco."
supersedes: null
superseded_by: null
tags: [neutralidade, adocao, geracao, automacao]
---

# Mecanização de capacidades: hooks, agent e command gerados por fornecedor

## Resumo executivo

O central (`doc-traceability-central`) criou `.claude/settings.json`
(hooks), `.claude/agents/sdd-verifier.md` e
`.claude/commands/framework-check.md` escritos à mão, só para Claude
Code — sem lugar na arquitetura atual do kit, que só gera prompt de texto
por fornecedor (`SDD-DTF-0007`). Esta SDD implementa `SPEC-DTF-0006`:
declara mecanização por `capability` na camada 1
(`workflow-rules.yaml`), e estende `render_prompts.py` para gerar os
quatro arquivos (`.claude/settings.json`, `.claude/agents/sdd-verifier.md`,
`.claude/commands/framework-check.md`, `_framework/scripts/guard_bash.sh`)
por inteiro, com `--check` cobrindo os quatro.

## Decisão(ões) de arquitetura aplicável(is)

`ADR-DTF-0001` — três camadas, fornecedor confinado a adaptadores
gerados. Esta SDD aplica a exceção que o próprio ADR previu: "um
fornecedor com capacidade exclusiva relevante não tem onde ser
acomodado sem virar exceção declarada na camada 1." Não há ADR novo —
`SPEC-DTF-0006` já registrou que este caso é aplicação, não mudança, da
decisão existente.

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0006`:

- **RF01** — `capability` em `workflow-rules.yaml` (seção 12) ganha campo
  opcional `mechanization: {vendor, artifact_type, matcher?, hook_command?, prompt?}`,
  `artifact_type` ∈ `{hook_pretooluse, hook_posttooluse, hook_sessionstart,
  hook_precompact, agent, command}`.
- **RF02** — `render_prompts.py` gera `.claude/settings.json` inteiro a
  partir de toda `capability` com `mechanization.artifact_type` começando
  em `hook_`, agrupada por evento.
- **RF03** — `render_prompts.py` gera `.claude/agents/<id>.md` e
  `.claude/commands/<id>.md` inteiros para `capability` com
  `artifact_type: agent`/`command`.
- **RF04** — `_framework/scripts/guard_bash.sh` gerado a partir de
  `enforcement_patterns` (padrão shell + mensagem) anexado à capacidade
  `enforce_branch_before_commit`.
- **RF05** — `--check` reprova divergência dos quatro arquivos.
- **RF06** — paridade kit ↔ central para os quatro arquivos.
- **RF07** — capacidade sem `mechanization` não gera arquivo `.claude/*`
  (comportamento atual preservado).

Casos de borda consolidados:

- Vendor sem hooks nativos (Cursor/Copilot hoje) → nenhum `.claude/*`
  gerado para ele; cobertura continua só via prosa dos adaptadores
  existentes.
- `.claude/settings.json` editado à mão fora do gerado → `--check` sai 1
  nomeando o arquivo.
- `artifact_type` desconhecido → `render_prompts.py` sai com erro citando
  `capability['id']` e o valor recebido, nenhum arquivo parcial escrito.
- `enforcement_patterns` vazio/ausente → `guard_bash.sh` gerado só com a
  leitura do payload e `exit 0`, mais um `WARN` no stdout de
  `render_prompts.py` — não falha a geração.
- Dois `capability['id']` mecanizados como `agent`/`command` colidindo no
  mesmo path → `render_prompts.py` sai com erro citando os dois ids,
  antes de escrever qualquer arquivo.

Requisito não funcional: geração idempotente (rodar duas vezes sem mudar
o YAML produz bytes idênticos); `guard_bash.sh` gerado precisa recusar
exatamente os mesmos padrões que a versão escrita à mão do central recusa
hoje — comparação linha a linha antes do commit da migração.

Fora de escopo (herdado de `SPEC-DTF-0006`): adaptador `.claude/*`
equivalente para Cursor/Copilot; alterar lógica de
`framework_check.py`/`procedures/verify-sdd.md`; `sync_copies`,
`RENDERINGS` ampliada além dos 4 arquivos, `ai_targets` fora do schema
(pendências já sinalizadas em `SDD-DTF-0007`); novas capacidades de
negócio.

## Especificação técnica consolidada

**`_framework/rules/workflow-rules.yaml`** (seção 12):

- `enforce_branch_before_commit` ganha:
  ```yaml
  mechanization:
    vendor: "claude-code"
    artifact_type: "hook_pretooluse"
    matcher: "Bash"
    hook_command: ["bash", "_framework/scripts/guard_bash.sh"]
  enforcement_patterns:
    - pattern: '*"push --force"*|*"push -f "*|*" -f "*"origin main"*'
      message: "force-push detectado. Use PR normal."
    - pattern: '*"push"*"origin main"*|*"push"*" main"*'
      message: "push direto em main. Abra PR."
    - pattern: '*"reset --hard"*'
      message: "reset --hard é destrutivo. Confirme com o usuário antes."
    - pattern: '*"rm -rf ."*|*"rm -rf /"*|*"rm -rf ~"*'
      message: "rm -rf de escopo amplo. Confirme com o usuário antes."
  ```
- `enforce_content_quality_gate` (junto com `validate_registry`, mesmo
  gatilho) ganha:
  ```yaml
  mechanization:
    vendor: "claude-code"
    artifact_type: "hook_posttooluse"
    matcher: "Edit|Write"
    hook_command: ["python3", "_framework/scripts/framework_check.py", "--auto", "--report-only"]
  ```
- `verify_sdd_independently` ganha `mechanization: {vendor: claude-code,
  artifact_type: agent}` — gera `.claude/agents/verify_sdd_independently.md`.
  **Ajuste de nome:** o arquivo hoje no central chama-se
  `sdd-verifier.md`; para não quebrar quem já usa esse nome, o builder
  usa `capability.get('mechanization_filename', capability['id'])` —
  `verify_sdd_independently` ganha `mechanization_filename: sdd-verifier`
  no YAML, preservando o nome atual sem acoplar o gerador ao id.
- `audit_repo_adherence` ganha `mechanization: {vendor: claude-code,
  artifact_type: command}` + `mechanization_filename: framework-check`
  (mesmo motivo — nome atual é `framework-check.md`, id da capacidade é
  `audit_repo_adherence`).
- `pickup_handoff` ganha `mechanization: {vendor: claude-code,
  artifact_type: hook_sessionstart, matcher: "*", prompt: "Se existir
  HANDOFF.md na raiz do repositório, use a skill pickup antes de qualquer
  outra coisa: confirme o status real dos ids citados e releia do disco
  os arquivos que vai alterar, em vez de confiar no que o handoff
  anotou."}`.
- `write_handover` ganha `mechanization: {vendor: claude-code,
  artifact_type: hook_precompact, matcher: "*", prompt: "O contexto desta
  sessão está prestes a ser compactado. Antes disso, use a skill handover
  para gerar/atualizar HANDOFF.md referenciando os ids dos documentos em
  vez de reescrever o conteúdo deles — não deixe o estado de
  rastreabilidade se perder na compactação."}`.

**`_framework/scripts/render_prompts.py`:**

- `find_capability(rules, capability_id) -> dict` — busca em
  `rules['capabilities']` por `id`; `raise ValueError` nomeando o id se
  ausente.
- `mechanized_filename(capability) -> str` — retorna
  `capability.get('mechanization_filename', capability['id'])`.
- `build_claude_settings(rules) -> str` — monta o dict Python (chaves
  `SessionStart`, `PreCompact`, `PreToolUse`, `PostToolUse`, só as
  presentes) a partir de toda `capability` com
  `mechanization.artifact_type` iniciando em `hook_`; serializa com
  `json.dumps(..., indent=2) + "\n"`. Erro se `artifact_type` de alguma
  capacidade não bater com o enum aceito, ou se dois `hook_pretooluse`/
  `hook_posttooluse` colidirem no mesmo `matcher` (mistura no mesmo array
  de hooks daquele matcher, não é erro — matchers iguais concatenam).
- `build_claude_agent(capability, rules) -> str` — front-matter
  `name: {mechanized_filename}` + `description: {capability['description']}`
  + corpo curto apontando para `capability['procedure']` (quando
  existir) ou `capability['description']` (quando não).
- `build_claude_command(capability, rules) -> str` — front-matter
  `description: {capability['description']}` + corpo com o comando
  literal a rodar, derivado de `capability['mechanization']['hook_command']`
  quando presente, senão `capability['description']`.
- `build_guard_bash(rules) -> str` — cabeçalho fixo (comentário
  explicando o hook) + bloco `case "$command" in` construído a partir de
  `enforcement_patterns` da capacidade `enforce_branch_before_commit`
  (uma linha `*"pattern"*) deny "message" ;;` por entrada) + rodapé fixo
  (`esac`, `exit 0`). Sem `enforcement_patterns`: só cabeçalho + `case`
  vazio + rodapé, e `print("WARN: ...")` no stdout de `render_prompts.py`.
- Validação no início de `main()`, antes de escrever qualquer
  `FULL_TARGETS`: para toda `capability` com `mechanization`, checar
  `artifact_type` no enum aceito; para as com `artifact_type` `agent`/
  `command`, checar que `mechanized_filename` não colide entre si —
  `sys.exit(1)` citando os ids envolvidos em qualquer violação.
- `FULL_TARGETS` ganha:
  - `(".claude/settings.json", "build_claude_settings")`
  - `(".claude/agents/sdd-verifier.md", lambda rules: build_claude_agent(find_capability(rules, "verify_sdd_independently"), rules))`
  - `(".claude/commands/framework-check.md", lambda rules: build_claude_command(find_capability(rules, "audit_repo_adherence"), rules))`
  - `("_framework/scripts/guard_bash.sh", "build_guard_bash")`

**`_framework/scripts/check_renderings.py`:** `RENDERINGS` ganha os
quatro caminhos acima — mesmo mecanismo de checagem tipo/status já
existente para os demais adaptadores.

**Migração sem mudança de comportamento:** antes do commit, `diff` entre
`guard_bash.sh` gerado e a versão hoje escrita à mão no central precisa
ser vazio (ou só whitespace); mesma checagem para os outros três
arquivos.

**Paridade entre repositórios (RF06):** os arquivos acima, mais
`workflow-rules.yaml` e `render_prompts.py`, alterados nos dois
repositórios na mesma branch, antes do PR.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — YAML aceita `mechanization` nas 6 capacidades listadas | `grep -c "^    mechanization:" _framework/rules/workflow-rules.yaml` | `6` |
| 2 | RF02 — `.claude/settings.json` gerado agrupa por evento | `python3 -c "import json; d=json.load(open('.claude/settings.json')); print(sorted(d['hooks'].keys()))"` | `['PostToolUse', 'PreCompact', 'PreToolUse', 'SessionStart']` |
| 3 | RF03 — agent e command gerados existem e citam a capacidade certa | `grep -l "verify_sdd_independently\|audit_repo_adherence" .claude/agents/sdd-verifier.md .claude/commands/framework-check.md` | os dois arquivos listados |
| 4 | RF04 — `guard_bash.sh` gerado recusa os 4 padrões atuais | `grep -c "deny " _framework/scripts/guard_bash.sh` | `4` |
| 5 | Migração sem mudança de comportamento (guard_bash) | `diff <(git show HEAD~1:_framework/scripts/guard_bash.sh 2>/dev/null \|\| cat _framework/scripts/guard_bash.sh) _framework/scripts/guard_bash.sh` | sem diferença de conteúdo normativo (só possível diferença: comentário de cabeçalho citando que é gerado) |
| 6 | RF05 — `--check` reprova edição manual | editar `.claude/settings.json`, rodar `--check`, regenerar, `--check` | `exit 1` com edição, `exit 0` depois de regenerar |
| 7 | RF05 — `--check` reprova ausência | renomear temporariamente `.claude/agents/sdd-verifier.md`, `--check`, restaurar | `exit 1` nomeando o arquivo, depois `exit 0` |
| 8 | RF07 — capacidade sem `mechanization` não gera arquivo | `find .claude -type f \| wc -l` (antes/depois da mudança, só os 4 novos a mais) | `+4` em relação à contagem anterior à SDD, nenhum arquivo extra |
| 9 | `artifact_type` inválido é rejeitado | inserir temporariamente `artifact_type: "bogus"` numa capacidade, rodar `render_prompts.py`, reverter | saída não-zero citando o id da capacidade e `"bogus"` |
| 10 | Regressão | `framework_check.py --auto` (central) e `check_renderings.py` (kit) | exit 0 nos dois |
| 11 | Paridade (RF06) | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída |

Sensor de discriminação: critérios 6, 7 e 9 têm caso negativo explícito
(edição manual, arquivo ausente, valor inválido) — falha antes da
correção, passa depois, nas duas pontas.

## Instruções específicas para a IA implementadora

- Comece pelo YAML (seção 12) — os builders dependem dos campos novos
  existirem antes de rodar.
- `build_guard_bash`, `build_claude_settings` etc. seguem o padrão
  `build_agents`/`build_universal` já existentes em `render_prompts.py`:
  recebem `rules`, devolvem `str`, sem I/O direto — quem escreve arquivo é
  o laço em `main()`.
- Não reescreva a prosa de `guard_bash.sh`/`settings.json`/agent/command
  "já que está mexendo" — é transcrição dos arquivos hoje existentes no
  central para dentro dos builders, com os campos variáveis vindos do
  YAML.
- Depois de gerar, rode o critério 5 (diff) antes de qualquer outro passo
  — se aparecer diferença de sentido no `guard_bash.sh`, é erro de
  transcrição.
- Replicar toda alteração (YAML, `render_prompts.py`,
  `check_renderings.py`, os 4 arquivos gerados) nos dois repositórios
  antes de abrir PR.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0009`.
- NÃO tocar em `framework_check.py`, `procedures/verify-sdd.md`,
  `sync_copies`, `ai_targets` — fora de escopo (ver "Fora de escopo"
  herdado de `SPEC-DTF-0006`).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [x] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** sim — sessão separada da que implementou,
sem ler o histórico da sessão implementadora. Os 11 critérios abaixo
foram re-executados nesta sessão em 2026-09-04, com os mesmos resultados
já registrados (implementação correta; a falha original era só de
processo — ver `LESSONS.md`, "SDD-DTF-0009 marcada implemented sem
verificador independente").

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `grep -c "^    mechanization:" _framework/rules/workflow-rules.yaml` | `6` | — | Sim |
| 2 | `python3 -c "import json; d=json.load(open('.claude/settings.json')); print(sorted(d['hooks'].keys()))"` | `['PostToolUse', 'PreCompact', 'PreToolUse', 'SessionStart']` | — | Sim |
| 3 | `grep -l "verify_sdd_independently\|audit_repo_adherence" .claude/agents/sdd-verifier.md .claude/commands/framework-check.md` | os dois arquivos listados | — | Sim |
| 4 | `grep -c "deny " _framework/scripts/guard_bash.sh` | `4` | — | Sim |
| 5 | `diff /tmp/guard_bash_original.sh _framework/scripts/guard_bash.sh` (original = guard_bash.sh hoje escrito à mão no central, `_framework/scripts/guard_bash.sh` sincronizado por `chore/sync-harness-guard-bash`, PR #30) | sem saída | — | Sim |
| 6 | Editei `.claude/settings.json` manualmente (`{"broken": true}`), rodei `render_prompts.py --check` (exit 1), regenerei com `render_prompts.py`, rodei `--check` de novo | exit 1 → exit 0 | negativo→positivo | Sim |
| 7 | Renomeei `.claude/agents/sdd-verifier.md` temporariamente, rodei `render_prompts.py --check` (`❌ sdd-verifier.md: ausente`), restaurei e regenerei, `--check` de novo | ausente citado → exit 0 | negativo→positivo | Sim |
| 8 | `find .claude -type f \| wc -l` (repositório não tinha `.claude/` antes desta SDD) | `3` (settings.json + agents/sdd-verifier.md + commands/framework-check.md; +4 contando `_framework/scripts/guard_bash.sh` fora de `.claude/`) | — | Sim |
| 9 | Troquei `artifact_type: "command"` de `audit_repo_adherence` para `"bogus"` no YAML, rodei `render_prompts.py`, reverti | `capacidade 'audit_repo_adherence': artifact_type 'bogus' desconhecido (...)`, exit 1, nenhum arquivo escrito antes do erro | negativo→positivo | Sim |
| 10 | `python3 _framework/scripts/framework_check.py --auto` (kit e central) e `python3 _framework/scripts/check_renderings.py` (kit e central) | `✅ Todas as verificações do framework passaram.` / `✅ 5 renderização(ões) concordam...` nos dois repositórios | — | Sim |
| 11 | `diff -r --exclude=__pycache__ _framework /home/michel/doc-traceability-central/_framework` e `diff .claude /home/michel/doc-traceability-central/.claude` | primeiro sem saída; segundo só acusa `settings.local.json` e `skills/` (pré-existentes no central, fora de escopo desta SDD) | — | Sim |
| — | Idempotência (não é critério numerado, mas é requisito não funcional da SDD): `render_prompts.py` rodado duas vezes seguidas, `md5sum` dos 4 arquivos comparado | hashes idênticos nas duas rodadas | — | Sim |

**Desvio da especificação técnica registrado nesta implementação:** a
`SPEC-DTF-0006`/SDD pedia adicionar os 4 caminhos novos ao `RENDERINGS` de
`check_renderings.py`, "mesmo mecanismo de checagem tipo/status já
existente". Fazer isso litealmente reprova sempre: `.claude/settings.json`
(JSON), o agent/command gerados e `guard_bash.sh` não citam nenhum tipo de
documento nem Iron Law — o mesmo motivo pelo qual `procedures/*.md`
(SDD-DTF-0006) já é explicitamente excluído do mesmo laço, no comentário
que precede `RENDERINGS` no próprio arquivo. Implementei uma checagem de
existência equivalente (`check_mechanized_artifacts`), consistente com o
padrão já usado para `capabilities.<id>.procedure`
(`check_capability_procedures`) — a checagem de conteúdo/divergência
continua coberta por `render_prompts.py --check` (RF05), que é a mais
forte das duas.

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0006, ADR-DTF-0001 |
| Branch | `sdd/SDD-DTF-0009-mecanizacao-capacidades` |
