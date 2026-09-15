---
id: SDD-DTF-0023
type: SDD
title: "Varredura dos validadores em repositório de projeto: validation-*.md como artefato operacional e --auto sem node_modules nem worktrees"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-14"
updated: "2026-09-14"
relates_to: [SDD-DTF-0019]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Implementar depois de SDD-DTF-0019 mergeada (as duas editam operational_artifacts em workflow-rules.yaml). Branch sdd/SDD-DTF-0023-* a partir de main, PR, commits com Refs: SDD-DTF-0023. Cópias da skill só via render_prompts.py."
supersedes: null
superseded_by: null
tags: [tooling, validadores, artefatos]
---

# Varredura dos validadores em repositório de projeto: validation-*.md como artefato operacional e --auto sem node_modules nem worktrees

## Resumo executivo

`iter_documents` (`_framework/scripts/framework_lib.py`) pula artefatos
operacionais comparando o **nome exato** do arquivo com as chaves de
`operational_artifacts` (`LESSONS.md`, `HANDOFF.md`, `validation.md`). O
procedimento `verify-sdd` manda escrever `validation.md` ao lado da SDD —
um nome só, sobrescrito a cada verificação.

Projeto com várias SDDs verificadas guarda um relatório por SDD. No EVM
(`viverMelhor`), `docs/sdd/validation-EVM-0011.md` a `-0015.md` são
tratados como documento: `framework_check.py docs/sdd` (kit em `main`,
2026-09-14) devolve 5 problemas "sem bloco de front-matter" e 5 avisos
"existe em disco mas não está em nenhuma entrada do registry". São os
únicos problemas de conteúdo do diretório. Com isso, o job bloqueante de
CI planejado em `SPEC-EVM-0008` falharia em todo PR.

Além disso, `_FALLBACK_OPERATIONAL_ARTIFACTS` (usado quando
`workflow-rules.yaml` não é achado, caso de projeto que copiou só os
scripts) não inclui `validation.md`.

Decisão do Michel em 2026-09-14: o kit aceita o padrão, em vez de o
projeto renomear os relatórios ou excluir arquivos no próprio CI.

Segundo achado na mesma varredura: `framework_check.discover` usa
`root.rglob("registry.yaml")` e só descarta depois `_framework/` e
`.git/`. Num repositório de projeto JavaScript, isso percorre
`node_modules/` inteiro: no `viverMelhor` (WSL), achar os `registry.yaml`
levou 93 s, e o `--auto` ainda descobre 6 cópias de `docs/sdd/` dentro de
`.claude/worktrees/`, validando worktree de sub-agent como se fosse o
projeto. Com o `discover` desta SDD, conferido na redação no mesmo
checkout: só `docs/sdd`, em menos de 0,1 s. O command `/framework-check` gerado pelo kit roda `--auto`, e o
hook de CI de `SPEC-EVM-0008` também.

`sizing: small` — 3 arquivos editados à mão e 2 testes novos, nenhum
critério do gate `rfc_to_adr` se aplica, sem mudança de comportamento
externo além de parar de reprovar arquivo que não é documento e de não
descer em diretório que nunca tem documento. Não é regra nova por
violação (`lessons_policy`): é o validador reconhecendo um artefato que o
próprio framework manda criar e a topologia de repositório de projeto.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção de varredura de validador, nenhum critério do gate
`rfc_to_adr` se aplica.

## Requisitos consolidados

- **RF1**: As chaves de `operational_artifacts` passam a aceitar padrão
  glob (`fnmatch`, sensível a maiúsculas). `iter_documents` pula todo
  `.md` cujo nome case com alguma chave.
- **RF2**: `operational_artifacts` ganha a chave `validation-*.md`,
  com `purpose` descrevendo o relatório por SDD e `declared_in:
  "capabilities.verify_sdd_independently"`.
- **RF3**: `_FALLBACK_OPERATIONAL_ARTIFACTS` passa a
  `("LESSONS.md", "HANDOFF.md", "validation.md", "validation-*.md")`.
- **RF4**: `framework_check.discover(root)` não desce em diretório
  chamado `.git`, `_framework` ou `node_modules`, nem em
  `.claude/worktrees` relativo a `root`; os demais diretórios com
  `registry.yaml` continuam descobertos, em ordem.

Casos de borda:
- `validation.md` (nome único do kit) continua pulado.
- `docs/sdd/validation-EVM-0013.md` pulado; `docs/sdd/SDD-EVM-0013.md`
  continua validado.
- Arquivo com front-matter e nome `validation-x.md` também é pulado —
  aceito: o nome é reservado ao relatório, e documento do framework tem
  nome `TIPO-PROJETO-SEQ.md`.
- `Validation-EVM-0013.md` (maiúscula) **não** é pulado: `fnmatchcase`,
  sem depender do sistema de arquivos.
- `registry_tools.cmd_validate` herda o comportamento (usa
  `iter_documents`): o aviso "existe em disco mas não está em nenhuma
  entrada" some para esses arquivos.
- `docs/node_modules_notes/registry.yaml`: descoberto (a poda é por nome
  exato de diretório).
- `.claude/` fora de `worktrees/` (ex.: `.claude/agents/`): percorrido
  normalmente; não tem `registry.yaml`.
- `framework_check.py <dir>` explícito (sem `--auto`) não usa `discover`:
  valida o diretório pedido, mesmo dentro de um worktree.

Fora de escopo:
- Mudar o nome que o procedimento `verify-sdd` manda criar (continua
  `validation.md`; o texto do procedimento é da `SDD-DTF-0019`).
- Validar o conteúdo do relatório.
- Sincronizar o `viverMelhor` (é `SDD-EVM-0016`, de `SPEC-EVM-0008`).
- Bump de `framework.version`.

## Especificação técnica consolidada

**`_framework/scripts/framework_lib.py`**

- `import fnmatch` no topo.
- `_FALLBACK_OPERATIONAL_ARTIFACTS = ("LESSONS.md", "HANDOFF.md", "validation.md", "validation-*.md")`.
- Nova função, logo antes de `iter_documents`:
  ```python
  def is_operational_artifact(name: str) -> bool:
      """Nome casa com alguma chave de operational_artifacts (glob, sensível a maiúsculas)."""
      return any(fnmatch.fnmatchcase(name, pattern) for pattern in OPERATIONAL_ARTIFACTS)
  ```
- `iter_documents`: `path.name in OPERATIONAL_ARTIFACTS` passa a
  `is_operational_artifact(path.name)`; docstring cita
  `validation*.md` junto de `LESSONS.md` e `HANDOFF.md`.

**`_framework/rules/workflow-rules.yaml`** — `operational_artifacts`,
nova chave depois de `validation.md` (as existentes não mudam aqui):

```yaml
  validation-*.md:
    purpose: "Relatório de verificação independente por SDD (ex.: validation-EVM-0013.md), para projeto que guarda um relatório por SDD em vez de sobrescrever validation.md. Mesmo formato e mesmo papel de validation.md."
    declared_in: "capabilities.verify_sdd_independently"
```

**`_framework/scripts/framework_check.py`** — `discover` passa a podar a
árvore em vez de filtrar depois de `rglob`:

```python
PRUNED_DIR_NAMES = {".git", "_framework", "node_modules"}


def discover(root: Path) -> list[Path]:
    """Todo diretório com registry.yaml, sem descer em .git, _framework,
    node_modules nem .claude/worktrees (cópias de sub-agent)."""
    found = []
    worktrees = root / ".claude" / "worktrees"
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames if d not in PRUNED_DIR_NAMES and current / d != worktrees
        )
        if "registry.yaml" in filenames:
            found.append(current)
    return sorted(found)
```

(`import os` no topo.)

**`_framework/scripts/tests/test_discover.py`** (novo) — `tmp_path` com
`registry.yaml` em `docs/sdd/`, `docs/EVM/`,
`node_modules/pkg/docs/`, `_framework/examples/`, `.claude/worktrees/a/docs/sdd/`
e `docs/node_modules_notes/`. Caso: `discover(tmp_path)` devolve
exatamente `docs/EVM`, `docs/node_modules_notes` e `docs/sdd`, nessa
ordem.

**`_framework/scripts/tests/test_operational_artifacts.py`** (novo) —
`tmp_path` com `registry.yaml` mínimo e os arquivos `SDD-X-0001.md`,
`LESSONS.md`, `HANDOFF.md`, `validation.md`, `validation-X-0001.md`,
`Validation-X-0002.md`, `registry.md` e `templates/t.md`. Casos:
1. `iter_documents` devolve exatamente `SDD-X-0001.md` e
   `Validation-X-0002.md`.
2. `is_operational_artifact` é `True` para `validation-X-0001.md` e
   `False` para `SDD-X-0001.md` e `Validation-X-0002.md`.
3. `_FALLBACK_OPERATIONAL_ARTIFACTS` contém `validation-*.md`.

**Gerados por `python3 _framework/scripts/render_prompts.py`** (nunca à
mão): `_framework/skills/doc-traceability-framework/scripts/framework_lib.py`
e `references/workflow-rules.yaml`.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1, RF3, casos de borda | `python3 -m pytest _framework/scripts/tests/test_operational_artifacts.py -v` | 3 casos ou mais, todos passam |
| 2 | RF2 | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); print('validation-*.md' in d['operational_artifacts'], 'validation.md' in d['operational_artifacts'])"` | `True True` |
| 3 | RF1 discrimina o caso real do EVM | bloco C3 abaixo | primeira execução com `exit=1` e `sem bloco de front-matter` citando `validation-EVM-0013.md`; segunda com `exit=0` |
| 4 | RF4 | `python3 -m pytest _framework/scripts/tests/test_discover.py -v` | 1 caso ou mais, todos passam |
| 5 | RF4 discrimina o caso real (node_modules e worktree) | bloco C5 abaixo | primeira execução lista 3 diretórios (inclui `node_modules` e `.claude/worktrees`); segunda lista só `docs/sdd` |
| 6 | Regressão e renderizações | `ruff check _framework/scripts && ruff format --check _framework/scripts && mypy _framework/scripts && python3 -m pytest && python3 _framework/scripts/render_prompts.py --check && python3 _framework/scripts/check_renderings.py && python3 _framework/scripts/framework_check.py --auto` | exit 0 em todos |

Bloco C3 (usa redirecionamento, fica fora da tabela) — reproduz o
diretório do EVM numa cópia descartável do kit: a primeira execução usa
o `framework_lib.py` de `origin/main` (antes desta SDD), a segunda o da
branch.

```bash
tmp=$(mktemp -d) && mkdir -p "$tmp/docs" && cp docs/sdd/registry.yaml docs/sdd/SDD-DTF-0017.md "$tmp/docs/" && \
printf '# Verificação — SDD-EVM-0013\n\n- **Veredito:** PASS\n' > "$tmp/docs/validation-EVM-0013.md" && \
git worktree add -q "$tmp/antes" origin/main && \
python3 - "$tmp/docs/registry.yaml" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p))
d["documents"] = [x for x in d["documents"] if x["id"] == "SDD-DTF-0017"]
d["documents"][0]["path"] = "SDD-DTF-0017.md"
yaml.safe_dump(d, open(p, "w"), allow_unicode=True, sort_keys=False)
PY
python3 "$tmp/antes/_framework/scripts/framework_check.py" "$tmp/docs"; echo "exit=$?"
python3 _framework/scripts/framework_check.py "$tmp/docs"; echo "exit=$?"
git worktree remove --force "$tmp/antes"
```

Bloco C5 — mesma técnica, para `discover`:

```bash
tmp=$(mktemp -d) && mkdir -p "$tmp/root/docs/sdd" "$tmp/root/node_modules/pkg/docs" "$tmp/root/.claude/worktrees/a/docs/sdd" && \
touch "$tmp/root/docs/sdd/registry.yaml" "$tmp/root/node_modules/pkg/docs/registry.yaml" "$tmp/root/.claude/worktrees/a/docs/sdd/registry.yaml" && \
git worktree add -q "$tmp/antes" origin/main && \
python3 -c "import sys; sys.path.insert(0, sys.argv[1]); from framework_check import discover; from pathlib import Path; r = Path(sys.argv[2]); print([str(p.relative_to(r)) for p in discover(r)])" "$tmp/antes/_framework/scripts" "$tmp/root"
python3 -c "import sys; sys.path.insert(0, sys.argv[1]); from framework_check import discover; from pathlib import Path; r = Path(sys.argv[2]); print([str(p.relative_to(r)) for p in discover(r)])" "_framework/scripts" "$tmp/root"
git worktree remove --force "$tmp/antes"
```

## Instruções específicas para a IA implementadora

- Implementar só depois de `SDD-DTF-0019` mergeada em `main`; se não
  estiver, parar e avisar.
- Em `workflow-rules.yaml`, só acrescentar a chave `validation-*.md`.
- Não mudar `read_frontmatter`, `validate_doc`, `validate_state` nem o
  texto de `verify-sdd.md`.
- Não editar à mão as cópias em
  `_framework/skills/doc-traceability-framework/`; rodar
  `python3 _framework/scripts/render_prompts.py` e commitar o gerado no
  mesmo PR.
- Branch `sdd/SDD-DTF-0023-validation-por-sdd` a partir de `main`, PR —
  nunca commit direto (gate seção 14). Conventional Commits com
  `Refs: SDD-DTF-0023`.
- Verificação (`verify-sdd`) em sessão ou sub-agent separado; a tabela de
  evidência vai **nesta SDD**.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] RF1–RF4 têm código e teste correspondentes.
- [ ] Arquivos tocados só entre: `_framework/scripts/framework_lib.py`,
      `_framework/scripts/framework_check.py`,
      `_framework/rules/workflow-rules.yaml`,
      `_framework/scripts/tests/test_operational_artifacts.py`,
      `_framework/scripts/tests/test_discover.py`, cópias
      geradas em `_framework/skills/doc-traceability-framework/`, e esta
      SDD e o registry (status/evidência).
- [ ] Nenhuma mudança de regra, gate ou script além do descrito.

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
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0019 (mesmo bloco `operational_artifacts`; ordem de implementação) |
