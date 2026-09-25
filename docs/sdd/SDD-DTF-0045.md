---
id: SDD-DTF-0045
type: SDD
title: "Higiene de busca e CI: caches fora da árvore de busca e etapa de CI para índices e paridade"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0043]
source_docs:
  - id: "SPEC-DTF-0019"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0019.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Leia SPEC-DTF-0019 inteira antes de tocar em qualquer arquivo: esta SDD consolida Parte 1 e Parte 2, mas o texto completo de cada caso de borda vive só na SPEC. Nome do arquivo de exclusão de busca é `.ignore` (não `.claudeignore`) e NÃO entra `permissions.deny`. As tasks de higiene (1 a 4) não dependem de nenhuma outra SDD; a task 5 (passo de CI dos `--check` de índice, RF05) só pode ser implementada depois de SDD-DTF-0043 (SPEC-DTF-0016) estar `implemented`, e não usa guarda de existência nem `|| true`. O central tem workflow próprio: tasks 6 e 7 aplicam o mesmo no repositório central. Implementar em sessão separada, com worktree próprio no kit; verificação por sdd-verifier em outra sessão."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, higiene, ci, gitignore, cache]
---

# Higiene de busca e CI: caches fora da árvore de busca e etapa de CI para índices e paridade

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar.

## Resumo executivo

Os diretórios `.ruff_cache`, `.pytest_cache` e `.mypy_cache` não são
declarados pelo `.gitignore` da raiz (hoje só ficam fora do `git status`
porque cada ferramenta grava um `.gitignore` interno com `*`), e nenhum
arquivo de exclusão de busca existe para LLMs. Além disso, o CI
(`framework-check.yml`) nunca roda `_framework/tests/` e não roda os
`--check` dos índices gerados. Esta SDD (Frente E da RFC-DTF-0008)
declara os quatro caches no `.gitignore` e num `.ignore`, cria um teste
de higiene, acrescenta ao workflow o passo de `_framework/tests/`, o passo
de higiene de cache e (depois de SDD-DTF-0043 implementada) os `--check`
de índice, e aplica tudo também no repositório central. Nenhuma regra de
comportamento do framework muda.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — RFC-DTF-0008 dispensou decisão arquitetural via gate
(`rfc_to_adr` = false; `parent_adr: null` na SPEC-DTF-0019, sizing
`medium`). Decisões registradas na SPEC, decididas pelo humano em
2026-09-24:

- `.claudeignore` não é lido pelo Claude Code (0 ocorrências no binário
  2.1.278), então prometer exclusão de busca com esse nome seria falso.
  Adota-se `.ignore` (respeitado por ripgrep, que sustenta os Grep/Glob da
  ferramenta), redundante com o `.gitignore`, no lugar de `.claudeignore`
  da redação da RFC-DTF-0008 E.1 (`.rgignore` valeria só para ripgrep).
- **NÃO** entra `permissions.deny` em `.claude/settings.json`: é enforcement
  de leitura, altera configuração de sessão versionada de todos os usuários
  do kit e vai além de higiene de busca.
- Entrada por último, sem guarda: o passo de RF05 só é adicionado depois de
  SPEC-DTF-0016 `implemented`; `if [ -f ... ]` e `|| true` foram descartados
  porque fariam a remoção acidental de um índice passar como sucesso.
- RF06 dispensa passo próprio e guarda: pytest coleta o que existe em
  `_framework/tests/`, e o teste da SPEC-DTF-0017 entra sozinho no passo de
  RF04 quando existir.

## Requisitos consolidados

| RF-ID | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | O `.gitignore` da raiz declara os três diretórios de cache que faltam, mantendo `__pycache__/` e `*.pyc` já existentes. | O sistema deve ignorar, por regra do `.gitignore` da raiz, os diretórios `.ruff_cache`, `.pytest_cache`, `.mypy_cache` e `__pycache__`. |
| RF02 | Nenhum arquivo dentro de diretório de cache pode estar versionado. | Se algum caminho rastreado casar com `.ruff_cache/`, `.pytest_cache/`, `.mypy_cache/` ou `__pycache__/`, então o sistema deve reprovar a checagem listando o caminho. |
| RF03 | Um arquivo de exclusão de busca (`.ignore`) lista os mesmos quatro diretórios, para ferramentas que respeitam `.ignore` mas não leem o `.gitignore` interno de cada cache. | O sistema deve excluir de glob e grep de ferramentas baseadas em ripgrep os diretórios `.ruff_cache`, `.pytest_cache`, `.mypy_cache` e `__pycache__`. |
| RF04 | O CI roda o diretório `_framework/tests/`, hoje ausente do workflow. | Quando o workflow `framework-check` executar, o sistema deve rodar `python3 -m pytest _framework/tests/ -v` e reprovar o job se algum teste falhar. |
| RF05 | O CI roda cada `--check` de índice declarado em SPEC-DTF-0016 (`render_prompts.py --check`, `render_indexes.py sdd docs/sdd --check`, `generate_registry_md.py docs/sdd --check`), como último passo de conteúdo, sem guarda de existência. | Quando o workflow executar, o sistema deve rodar cada comando `--check` de índice declarado em SPEC-DTF-0016 e reprovar o job se algum sair com código diferente de 0. |
| RF06 | A paridade de templates (SPEC-DTF-0017) é executada pelo CI sem passo dedicado. | Quando SPEC-DTF-0017 estiver implementada, o sistema deve executar seu teste de paridade dentro do passo de RF04. |
| RF07 | Após a suíte, o CI verifica que os caches estão ignorados pela raiz e que nada de cache foi rastreado. | Quando a suíte terminar no CI, o sistema deve executar a checagem de higiene e reprovar o job se algum cache não estiver ignorado pelo `.gitignore` da raiz ou aparecer em `git ls-files` ou em `git status --porcelain --untracked-files=all`. |
| RF08 | Um teste de higiene de repositório mantém RF01 a RF03 sob teste local. | O sistema deve falhar `python3 -m pytest _framework/tests/test_repo_hygiene.py` se `.gitignore` deixar de conter qualquer dos quatro padrões ou se `.ignore` deixar de listá-los. |

Casos de borda (todos herdados da SPEC-DTF-0019, sem relaxamento):

| Caso | RF | Comportamento esperado |
|---|---|---|
| Cache já rastreado (`git ls-files` retorna caminho de cache) | RF01, RF02 | `.gitignore` não desrastreia arquivo já versionado. Executar `git rm -r --cached <dir>` no mesmo commit que altera `.gitignore`; RF02 reprova enquanto restar caminho rastreado. Hoje nenhum está rastreado (verificado em 2026-09-24), então o passo é condicional e o critério RF02 valida a ausência. |
| Diretório de cache ainda não existe na máquina (clone novo) | RF01, RF07 | `git check-ignore` de diretório inexistente com padrão terminado em `/` não casa. A checagem de RF07 roda só depois de ruff, mypy e pytest; para `__pycache__` usa `_framework/scripts/__pycache__`, nunca `__pycache__` na raiz. |
| Windows (desenvolvedor local) | RF01, RF03, RF08 | Padrões usam `/`; CI roda só em `ubuntu-latest`. Com CRLF por `autocrlf`, o padrão pode deixar de casar; RF08 lê linhas com `splitlines()` e `strip()`, e o critério `git check-ignore` de RF01 detecta a falha na prática. |
| CI sem Python (`setup-python` falha) | RF04, RF05, RF07 | Nenhum passo tem `continue-on-error` nem `if:` que o pule; job reprovado, nunca "passou sem checar". |
| `REPORT_ONLY` preenchido no workflow | RF04, RF05, RF07 | Os passos novos não usam `$REPORT_ONLY`: o gate é sempre bloqueante. |
| `.ignore` exclui caminho que outra ferramenta precisa ler | RF03 | `.ignore` lista só os quatro diretórios de cache. Nada em `docs/`, `_framework/` ou `examples/` é excluído. |
| Cache de outra ferramenta aparece depois (`.tox`, `.coverage`) | RF01 | Fora de escopo; lista fechada nos quatro diretórios. Acrescentar exige emenda da SPEC. |
| Repositório central sem workflow equivalente | RF04, RF05, RF07 | O central tem `.github/workflows/framework-check.yml` próprio (não espelhado por `_framework/`). Aplicar RF01-RF07 em cada repositório separadamente e validar cada um por comando. |

Requisitos não funcionais: sem dependência nova (RF08 usa `pytest` e
`subprocess` da stdlib; `requirements.txt` já lista `pytest==9.1.1`);
RF07 e RF08 não escrevem no repositório, só leem `.gitignore`, `.ignore` e
estado do git.

Requisitos transversais (sweep) resolvidos na SPEC: idempotência e
observabilidade em RF07 (a checagem só lê estado do git e imprime o
diretório ou caminho ofensor antes de sair com 1); falha de dependência
externa em RF04 (falha de `setup-python`, `pip install` ou
`actions/checkout` reprova o job); autorização, concorrência, validação de
entrada e limite de volume/rate são `n/a` com motivo registrado na SPEC.

Fora de escopo: reduzir ou dividir `workflow-rules.yaml`, criar índices ou
testes de paridade (SPEC-DTF-0016 e SPEC-DTF-0017); alterar `pyproject.toml`
(`cache_dir`); editar `workflow-rules.yaml`, `render_prompts.py` ou skill;
promover o workflow a check obrigatório de branch protection; hooks locais
(`.pre-commit-config.yaml`, `.githooks/`); limpeza retroativa de histórico
git ou de projetos mapeados.

## Especificação técnica consolidada

Três arquivos de configuração e um teste, por repositório (kit e central):

1. `.gitignore`: acrescenta `.ruff_cache/`, `.pytest_cache/` e `.mypy_cache/`
   abaixo de `__pycache__/`; mantém as linhas atuais.
2. `.ignore` (novo): os mesmos quatro padrões, um por linha, com um
   comentário de uma linha dizendo por que existe.
3. `.github/workflows/framework-check.yml`: passos acrescentados depois do
   último passo de conteúdo ("Renderizações concordam com o núcleo
   canônico") e antes de "Validar mensagens de commit do PR":
   - "Testes de paridade e consistência (_framework/tests)" (RF04, RF06);
   - passos de índice `--check` de SPEC-DTF-0016 (RF05), antes do passo de
     higiene;
   - "Higiene de cache (ignorados e não rastreados)" (RF07).
4. `_framework/tests/test_repo_hygiene.py` (novo; `_framework/tests/` não é
   copiado para o bundle da skill, então não há réplica no bundle; a cópia
   espelho é o mesmo arquivo em `_framework/tests/` do central): lê
   `.gitignore` e `.ignore` (RF08) e roda `git ls-files` para RF02.

Não é criado: `.claudeignore`; não se altera `.claude/settings.json`.

Edição concreta de RF04 e RF07 (comandos a copiar sem alteração):

```yaml
      - name: Testes de paridade e consistência (_framework/tests)
        run: python3 -m pytest _framework/tests/ -v

      - name: Higiene de cache (ignorados e não rastreados)
        run: |
          for d in .ruff_cache .pytest_cache .mypy_cache _framework/scripts/__pycache__; do
            git check-ignore -q "$d" || { echo "cache não ignorado pelo .gitignore da raiz: $d"; exit 1; }
          done
          if git ls-files | grep -E '(^|/)(\.ruff_cache|\.pytest_cache|\.mypy_cache|__pycache__)/'; then
            echo "cache rastreado acima"; exit 1
          fi
          if git status --porcelain --untracked-files=all | grep -E '(_cache|__pycache__|\.pyc)'; then
            echo "cache aparece no git status acima"; exit 1
          fi
```

**Consumes** (já existe):

- `pyproject.toml`, `[tool.pytest.ini_options] testpaths = ["_framework/scripts/tests", "_framework/tests"]`.
- `.github/workflows/framework-check.yml`, job `validate`, passos atuais
  (nomes exatos): "Instalar dependências", "Lint (ruff)", "Typecheck (mypy)",
  "Formatter (ruff format --check)", "Testes de mechanization (render_prompts.py)",
  "Validar registries e documentos", "Renderizações concordam com o núcleo
  canônico", "Validar mensagens de commit do PR".
- `python3 _framework/scripts/render_prompts.py --check` (já no CI).
- Comandos `--check` de índice definidos por SPEC-DTF-0016 (nesta SDD:
  `python3 _framework/scripts/render_indexes.py sdd docs/sdd --check` e
  `python3 _framework/scripts/generate_registry_md.py docs/sdd --check`; o
  `render_prompts.py --check` existente passa a cobrir os índices do kit) e
  teste de paridade de SPEC-DTF-0017 (`_framework/tests/test_template_parity.py`).

**Produces:**

- `.gitignore`: linhas exatas `.ruff_cache/`, `.pytest_cache/`, `.mypy_cache/`
  (novas), mais as existentes `__pycache__/`, `*.pyc`, `.env`, `.env.*`.
- `.ignore` (raiz): linhas exatas `.ruff_cache/`, `.pytest_cache/`,
  `.mypy_cache/`, `__pycache__/`.
- `_framework/tests/test_repo_hygiene.py`, funções
  `test_gitignore_cobre_caches() -> None`,
  `test_ignore_cobre_caches() -> None`,
  `test_nenhum_cache_rastreado() -> None`; constante
  `CACHE_DIRS: tuple[str, ...] = (".ruff_cache", ".pytest_cache", ".mypy_cache", "__pycache__")`;
  `REPO_ROOT = Path(__file__).resolve().parents[2]` (mesmo idioma de
  `_framework/tests/test_kit_parity.py`).
- Passos do workflow: "Testes de paridade e consistência (_framework/tests)",
  os passos de índice (nomes definidos por esta SDD conforme SPEC-DTF-0016)
  e "Higiene de cache (ignorados e não rastreados)".

Tratamento de erro por contrato:

| Caso | RF | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| Padrão de cache ausente do `.gitignore` | RF01, RF08 | Asserção falha nomeando o padrão faltante | `test_gitignore_cobre_caches` |
| Padrão ausente do `.ignore` ou arquivo inexistente | RF03, RF08 | Asserção falha com o nome do arquivo e do padrão | `test_ignore_cobre_caches` |
| Caminho de cache em `git ls-files` | RF02, RF07 | Teste falha listando o caminho; passo do CI sai com 1 | `test_nenhum_cache_rastreado` e passo "Higiene de cache" |
| `git` indisponível ou fora de repositório | RF02, RF08 | O teste falha com o stderr do git (não `skip`), nunca conta como "sem cache rastreado" | `test_nenhum_cache_rastreado` (`subprocess.run(..., check=True)`) |
| Falha do pytest em `_framework/tests/` | RF04 | Passo sai com código diferente de 0 e o job reprova | passo do workflow |
| `--check` de índice sai com 1 | RF05 | Passo sai com 1 e o job reprova; nenhum `\|\| true` | passo do workflow |
| Cache não ignorado pela raiz | RF07 | Mensagem com o diretório e saída 1 | passo "Higiene de cache" |

Estratégia de teste:

| RF-ID / contrato | Tipo | Mock? | Arquivo de teste |
|---|---|---|---|
| RF01, RF08 | Unitário estático (lê linhas do `.gitignore`) | Não | `_framework/tests/test_repo_hygiene.py::test_gitignore_cobre_caches` |
| RF03, RF08 | Unitário estático (lê linhas do `.ignore`) | Não | `_framework/tests/test_repo_hygiene.py::test_ignore_cobre_caches` |
| RF02 | Unitário com `git ls-files` real | Não | `_framework/tests/test_repo_hygiene.py::test_nenhum_cache_rastreado` |
| RF04, RF05, RF06, RF07 | Execução do workflow no CI e, localmente, dos mesmos comandos do passo | Não | passos de `.github/workflows/framework-check.yml` |
| Sensor de discriminação (RF01) | Mutação: remover `.mypy_cache/` do `.gitignore` em cópia temporária e ver `test_gitignore_cobre_caches` falhar | Não | `_framework/tests/test_repo_hygiene.py` (parametrizado sobre texto em `tmp_path`) |

Plano de implementação (ordem por dependência; 1 a 4 independentes de
SPEC-DTF-0016/0017; 5 só depois de SPEC-DTF-0016 `implemented`):

1. `.gitignore` (kit e central): acrescentar `.ruff_cache/`,
   `.pytest_cache/`, `.mypy_cache/`. Se `git ls-files` mostrar cache
   rastreado, `git rm -r --cached <dir>` no mesmo commit.
2. `.ignore` (kit e central): criar com os quatro padrões.
3. `_framework/tests/test_repo_hygiene.py`: criar as três funções de RF08.
4. `.github/workflows/framework-check.yml` (kit e central): acrescentar os
   passos de RF04 e RF07 depois de "Renderizações concordam com o núcleo
   canônico" e antes de "Validar mensagens de commit do PR".
5. `.github/workflows/framework-check.yml`: acrescentar, antes do passo de
   higiene, um passo por comando `--check` de índice de SPEC-DTF-0016, sem
   `continue-on-error` e sem guarda de existência.
6. Rodar a tabela de critérios em cada repositório e registrar comando e
   saída na SDD.
7. Espelhar `_framework/tests/test_repo_hygiene.py` entre kit e central
   (regra do `_framework/AGENTS.md`); `.gitignore`, `.ignore` e workflow
   não estão sob `_framework/` e são aplicados por repositório.

Riscos e mitigação: passo de RF07 falso-negativo em clone sem os diretórios
(roda só após os passos que criam os caches); testes de `_framework/tests/`
que nunca rodaram no CI falharem na primeira execução (rodar
`python3 -m pytest _framework/tests/ -v` localmente e registrar a saída
antes do PR; falha preexistente vira SDD própria, nunca é escondida por
`continue-on-error`); `.ignore` esconder diretório legítimo no futuro (só os
quatro caches); conflito de edição no workflow com SPEC-DTF-0016/0017 (elas
não tocam o workflow por escopo; se tocarem, declarar ordem e rebase nesta
SDD).

Rollout e rollback: rollout direto, sem feature flag, em PR do kit e PR do
central. Rollback: reverter o commit; `.gitignore`/`.ignore` são
declarativos e o teste e os passos de CI são somente leitura. O passo de
RF05 só entra depois de SPEC-DTF-0016 `implemented`, então reverter
SPEC-DTF-0016 exige reverter o passo junto. Observabilidade: nenhuma nova;
a saída do passo "Higiene de cache" nomeia o diretório ou caminho ofensor.
Nenhum time externo é impactado; nenhum projeto mapeado é alterado (mudança
não retroativa).

## Decomposição em tasks

Arquivos do repositório central usam o prefixo `central:` para não colidir
por nome com os do kit em `parallel_plan.py`. As tasks 1 a 4 não têm
dependência entre si além da declarada e podem rodar já. A task 5 exige
SDD-DTF-0043 (SPEC-DTF-0016) `implemented` antes de começar; essa
dependência é externa a esta SDD e por isso não aparece na coluna
"Depende de (#)" (que só aceita números de task).

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Kit: declarar os quatro caches no `.gitignore` (e `git rm -r --cached` só se houver cache rastreado) | RF01, RF02 | .gitignore | |
| 2 | Kit: criar `.ignore` com os quatro padrões | RF03 | .ignore | |
| 3 | Kit: criar `test_repo_hygiene.py` com as três funções e `CACHE_DIRS` | RF02, RF08 | _framework/tests/test_repo_hygiene.py | |
| 4 | Kit: passos "Testes de paridade e consistência (_framework/tests)" e "Higiene de cache (ignorados e não rastreados)" no workflow (RF06 é coberto pelo passo de RF04, sem edição própria) | RF04, RF06, RF07 | .github/workflows/framework-check.yml | 1 |
| 5 | Kit: passos `--check` de índice (SPEC-DTF-0016) no workflow, antes do passo de higiene; só depois de SDD-DTF-0043 `implemented` | RF05 | .github/workflows/framework-check.yml | 1, 2, 3, 4 |
| 6 | Central: espelhar `.gitignore`, `.ignore`, `test_repo_hygiene.py` e os passos de RF04/RF07 no workflow próprio do central | RF01, RF02, RF03, RF04, RF06, RF07, RF08 | central:.gitignore, central:.ignore, central:_framework/tests/test_repo_hygiene.py, central:.github/workflows/framework-check.yml | 1, 2, 3, 4 |
| 7 | Central: passos `--check` de índice no workflow do central; só depois de SDD-DTF-0043 `implemented` e espelhada | RF05 | central:.github/workflows/framework-check.yml | 1, 2, 3, 4, 5, 6 |

## Critérios de aceite / definição de pronto

Rodados na raiz de cada repositório (kit e central), com a saída registrada
na Evidência. Nenhum é verificado por leitura de código. Os critérios 7
(RF06) e 6 (RF05) só se aplicam depois de SPEC-DTF-0017 e SPEC-DTF-0016
`implemented`, respectivamente.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — caches ignorados por regra da raiz | `for d in .ruff_cache .pytest_cache .mypy_cache; do git check-ignore -v "$d"; done` (após `ruff check`, `mypy` e `pytest` criarem os diretórios) | três linhas, cada uma começando com `.gitignore:` (regra da raiz, não `.ruff_cache/.gitignore:`) | automatizado |
| 2 | RF02 — nenhum cache rastreado | `git ls-files \| grep -E '(^\|/)(\.ruff_cache\|\.pytest_cache\|\.mypy_cache\|__pycache__)/'; echo "rc=$?"` | nenhuma linha antes de `rc=1` | automatizado |
| 3 | RF03 — `.ignore` lista os quatro diretórios | `test -f .ignore && for d in .ruff_cache .pytest_cache .mypy_cache __pycache__; do grep -qxF "$d/" .ignore \|\| echo "falta $d"; done` | sem linha "falta" | automatizado |
| 4 | RF04 — CI roda `_framework/tests/` | `python3 -m pytest _framework/tests/ -v` | sai 0, lista `test_kit_parity.py`, `test_skill_md_consistency.py`, `test_validate_doc.py`, `test_ci_gate_verify_sdd.py`, `test_parallel_plan.py` e `test_repo_hygiene.py` | automatizado |
| 5 | RF04 (presença no CI) | `grep -n "pytest _framework/tests/" .github/workflows/framework-check.yml` | exatamente uma linha | automatizado |
| 6 | RF05 — cada `--check` de índice de SPEC-DTF-0016 | cada comando `--check` de índice declarado em SPEC-DTF-0016, rodado localmente (`python3 _framework/scripts/render_prompts.py --check`, `python3 _framework/scripts/render_indexes.py sdd docs/sdd --check`, `python3 _framework/scripts/generate_registry_md.py docs/sdd --check`) | sai 0 | automatizado |
| 7 | RF06 — paridade de templates coletada (após SPEC-DTF-0017) | `python3 -m pytest _framework/tests/ --collect-only -q \| grep -i templ` | ao menos um teste de paridade de template coletado | automatizado |
| 8 | RF07 — script do passo "Higiene de cache" | rodar localmente o script do passo "Higiene de cache (ignorados e não rastreados)" depois de `ruff check _framework/scripts && mypy _framework/scripts && python3 -m pytest _framework/ -q` | sai 0, sem mensagem | automatizado |
| 9 | RF07 (limpeza) | `git status --porcelain --untracked-files=all \| grep -E '(_cache\|__pycache__\|\.pyc)'; echo "rc=$?"` | nenhuma linha antes de `rc=1` | automatizado |
| 10 | RF08 — teste de higiene | `python3 -m pytest _framework/tests/test_repo_hygiene.py -v` | 3 testes passam; removendo `.mypy_cache/` do `.gitignore`, `test_gitignore_cobre_caches` falha | automatizado |
| 11 | Critério (3) da frente — `git status` limpo de caches após a suíte | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q && git status --porcelain --untracked-files=all \| grep -E '(_cache\|__pycache__\|\.pyc)'; echo "rc=$?"` | suíte verde e nenhuma linha de cache antes de `rc=1` | automatizado |

## Instruções específicas para a IA implementadora

- Branch nomeada pelo id que a originou, ex.: `sdd/SDD-DTF-0045-higiene-cache-ci`,
  levada a main por PR; nunca commit de implementação direto em main. Todo
  commit carrega `Refs: SDD-DTF-0045`.
- Implementar em sessão separada da que compilou esta SDD, aberta no kit,
  em worktree próprio (`git worktree add` explícito, porque isolamento
  automático não cobre repositório externo). O central é um segundo
  repositório com PR próprio (tasks 6 e 7).
- A verificação (status `implemented`) é feita pelo `sdd-verifier` em
  sessão separada da que implementou; quem implementou não preenche a
  Evidência de verificação.
- Nome do arquivo de exclusão de busca é `.ignore`. Não criar
  `.claudeignore` nem `.rgignore`. Não tocar `.claude/settings.json` e não
  adicionar `permissions.deny`.
- `.gitignore` e `.ignore` recebem só os quatro caches; nada em `docs/`,
  `_framework/` ou `examples/` entra no `.ignore`. Manter as linhas atuais
  do `.gitignore` (`__pycache__/`, `*.pyc`, `.env`, `.env.*`).
- Antes de alterar `.gitignore`, rodar `git ls-files | grep -E '(^|/)(\.ruff_cache|\.pytest_cache|\.mypy_cache|__pycache__)/'`;
  se listar algo, `git rm -r --cached <dir>` no mesmo commit.
- `test_repo_hygiene.py`: usar só `pytest`, `subprocess` e `pathlib`;
  `subprocess.run(..., check=True)` para `git ls-files` (nunca `skip`);
  ler `.gitignore` e `.ignore` com `splitlines()` e `strip()`; incluir o
  teste de mutação parametrizado sobre texto em `tmp_path` (sensor de
  discriminação de RF01). Não escreve no repositório.
- Workflow (kit e central): copiar exatamente os dois passos YAML de RF04 e
  RF07 da "Especificação técnica consolidada"; sem `continue-on-error`, sem
  `if:` que pule o passo, sem `$REPORT_ONLY`, sem `|| true`. Posição: depois
  de "Renderizações concordam com o núcleo canônico" e antes de "Validar
  mensagens de commit do PR".
- Task 5 (e 7): só iniciar com SDD-DTF-0043 `implemented`
  (`python3 _framework/scripts/framework_check.py --auto` e o registry
  confirmam o status). Sem guarda de existência dos índices. Se SDD-DTF-0043
  ainda não estiver `implemented`, parar e registrar em vez de improvisar
  guarda.
- Antes do PR, rodar `python3 -m pytest _framework/tests/ -v` localmente e
  registrar a saída; falha preexistente vira SDD própria.
- Não alterar `workflow-rules.yaml`, `render_prompts.py`, skills, templates,
  `pyproject.toml`, hooks locais, nem `registry.yaml`/`registry.md` fora do
  fluxo do framework. Arquivos gerados nunca são editados à mão.
- Espelhar `_framework/tests/test_repo_hygiene.py` byte a byte entre kit e
  central (regra do `_framework/AGENTS.md`).

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirmar as duas direções:

- [ ] Todo requisito consolidado (RF01 a RF08) tem código ou arquivo
      correspondente (nada da SPEC ficou de fora), no kit e no central.
- [ ] Todo arquivo tocado pela implementação aparece na "Decomposição em
      tasks" ou nas "Instruções específicas" — se a implementação tocou um
      arquivo não listado, ou é escopo que faltou registrar (atualizar a
      SDD) ou é scope creep a remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado; nenhum `.claudeignore`,
      nenhum `permissions.deny`, nenhum cache extra além dos quatro.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou —
quem escreveu o código tem o resultado como conclusão desejada. Para cada
critério da tabela acima: comando rodado de fato nesta sessão e saída real,
nunca "deve passar" nem resultado de memória. Cada critério é rodado no kit
e no central.

**Verificador independente:** não — SDD em `draft`, ainda não verificada

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Critério sem teste automatizado: escreva "sem
teste", nunca marque como verificado por leitura de código. "Assertion
(file:line)": caminho e linha exatos da asserção; critério `manual` ou
`n/a` usa `n/a`. "Perfil usado": repete o "Perfil esperado" ou declara
divergência com justificativa entre parênteses.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
| 1 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 2 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 3 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 4 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 5 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 6 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 7 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 8 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 9 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 10 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |
| 11 | não rodado | não rodado | não rodado | não rodado | não rodado | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0019 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0019.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
