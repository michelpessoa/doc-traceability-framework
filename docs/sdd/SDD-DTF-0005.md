---
id: SDD-DTF-0005
type: SDD
title: "Porta de entrada única e documentação gerada"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-08-29"
relates_to: [SPEC-DTF-0004, ADR-DTF-0001]
source_docs:
  - id: "SPEC-DTF-0004"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0004.md"
  - id: "ADR-DTF-0001"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/02-adr/ADR-DTF-0001.md"
consumption_instructions: "Leia 'Especificação técnica consolidada' e 'Instruções específicas' inteiras antes de tocar em arquivo. Os README dos dois repositórios são DIFERENTES e não se copiam. Nada aqui depende de SPEC-DTF-0005, já implementada."
supersedes: null
superseded_by: null
tags: [adocao, documentacao]
---

# Porta de entrada única e documentação gerada

## Resumo executivo

O repositório do kit tem 1682 linhas de documentação escrita à mão em seis
arquivos, dos quais seis falam dos mesmos gates, e nenhum diz por onde
começar. `README.md` (280 linhas) e
`Framework_Documentacao_Rastreabilidade.md` (482) cobrem os mesmos cinco
assuntos, e o `CHANGELOG.md` já divergiu do YAML — para na 2.0.0 enquanto
`framework.version` é 2.1.0. Esta SDD aplica à documentação humana a mesma
regra que `ADR-DTF-0001` já estabeleceu para as renderizações de IA: fato
canônico é gerado, didática é escrita à mão.

> Segunda tentativa. A primeira foi revertida por violar
> `gate_implementation_before_code` — código antes desta SDD existir. Ver
> `docs/DTF/LESSONS.md` no repositório central. A `SPEC-DTF-0004` não
> mudou.

## Decisão(ões) de arquitetura aplicável(is)

`ADR-DTF-0001` — três camadas, fornecedor confinado a adaptadores
gerados. Consequência aplicada aqui: quando um arquivo gerado discordar do
YAML, o YAML manda, e a divergência é falha de build barrada por
`render_prompts.py --check`.

## Requisitos consolidados

Da Parte 1 de `SPEC-DTF-0004`:

- **RF01** — `README.md` de no máximo 90 linhas, com exatamente três
  caminhos nomeados (`QUICKSTART.md`, `docs/especificacao.md`,
  `AGENTS.md`), sem repetir as tabelas de gates, tipos ou sizing.
- **RF02** — `docs/especificacao.md` gerada do YAML, cobrindo tipos ativos
  e legados, as seis Iron Laws com red flags, sizing, ciclo de status,
  registry, auditoria e handover.
- **RF03** — `Framework_Documentacao_Rastreabilidade.md` removido dos dois
  repositórios, sem referência sobrando.
- **RF04** — `CHANGELOG.md` gerado de `framework.changelog`, em ordem
  decrescente, contendo a versão corrente.
- **RF05** — guias em `docs/guias/`, à mão, cada um abrindo com aviso de
  que a regra canônica vive no YAML.
- **RF06** — nenhum link relativo quebrado em arquivo versionado.

Casos de borda consolidados: entrada de changelog sem `summary` gera a
versão com aviso explícito, nunca omite; histórico anterior ao changelog
canônico (versões 1.0.0 a 1.3.0, ausentes do YAML) é preservado como bloco
final; o caminho do guia citado dentro do YAML é atualizado junto,
incluindo a cópia dentro da skill; link para arquivo que nunca existiu é
reportado igual a link para arquivo movido.

## Especificação técnica consolidada

**`_framework/scripts/render_prompts.py`:**

- `build_spec_doc(rules) -> str` — `docs/especificacao.md`. Ordem das
  seções: cabeçalho de arquivo gerado; modelo de dois repositórios
  (`repository_topology`, incluindo `cross_repo_reference`); `core_facts`
  (núcleo já compartilhado com `AGENTS.md`); cada lei inegociável com
  `rule`/`principle` e a tabela de red flags; e então `registry`, `audit`,
  `handover_protocol`, `onboarding` e `incident_lifecycle`.
- `build_changelog(rules) -> str` — `CHANGELOG.md`, iterando
  `framework.changelog` ordenado por versão numérica decrescente, com
  bloco final vindo da constante `LEGACY_CHANGELOG` do próprio script.
- Helper `_wrap(text)` — normaliza as quebras arbitrárias do YAML em
  parágrafo único.
- `FULL_TARGETS` recebe `("../docs/especificacao.md", "build_spec_doc")` e
  `("../CHANGELOG.md", "build_changelog")`.
- `write_full` passa a criar o diretório do alvo quando não estiver em
  `--check`.

**`_framework/scripts/check_renderings.py`:**

- `LINK = re.compile(r"\]\(([^)\s]+)\)")`.
- `check_links(root) -> list` — varre `root.parent` (a raiz do
  repositório) por `*.md`, ignorando `.git`, `node_modules`,
  `__pycache__` e `examples`; para cada link relativo que não seja `http`,
  `https`, âncora ou `mailto`, resolve o caminho e reporta o que não
  existir.
- `main` chama `check_links` antes do laço de renderizações.

**`_framework/rules/workflow-rules.yaml`** e a cópia em
`skills/doc-traceability-framework/references/`: caminho
`_framework/guides/paralelizacao-trilhas.md` → `docs/guias/…`.

**Movidos:** `_framework/guides/*.md` → `docs/guias/*.md` (`git mv`), com
a linha de aviso inserida logo após o título de cada um.

**Removidos:** `Framework_Documentacao_Rastreabilidade.md`, nos dois
repositórios.

**Reescritos à mão:** `README.md` do kit (porta de entrada) e, no central,
apenas os trechos que citam `_framework/guides/` e o documento removido —
os dois README são diferentes e não se copiam um sobre o outro.

**Rollout:** branch `sdd/SDD-DTF-0005-superficie-doc` nos dois
repositórios, PR com CI verde. Rollback é `git revert`: nenhum documento
de projeto é alterado, nenhum dado migrado.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF01 — teto do README | `wc -l < README.md` | ≤ 90 |
| 2 | RF01 — três caminhos | `grep -c "QUICKSTART.md\|docs/especificacao.md\|AGENTS.md" README.md` | ≥ 3 |
| 3 | RF02, RF04 — gerados e em dia | `render_prompts.py && render_prompts.py --check` | exit 0 |
| 4 | RF02 (sensor) — edição manual reprova | Acrescentar linha a `docs/especificacao.md`, rodar `--check`, regenerar | exit 1 |
| 5 | RF02 — conteúdo mínimo | `grep -c "Iron Law\|red flag\|sizing\|handover" docs/especificacao.md` | ≥ 4 |
| 6 | RF03 — removido nos dois repos | `test ! -f Framework_Documentacao_Rastreabilidade.md` | exit 0 |
| 7 | RF04 — versão corrente presente | `grep -c "2.1.0" CHANGELOG.md` | ≥ 1 |
| 8 | RF05 — guias com aviso | `ls docs/guias/` e `grep -l "regra canônica" docs/guias/*.md` | 3 arquivos, 3 com aviso |
| 9 | RF06 — sem link quebrado | `check_renderings.py` nos dois repos | sem linha "quebrado" |
| 10 | RF06 (sensor) — link inexistente reprova | Acrescentar link para arquivo inexistente, rodar, remover **com `sed`** | reporta "quebrado" |
| 11 | Regressão | `framework_check.py --auto` nos dois repos | exit 0 |
| 12 | Paridade | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída |

## Instruções específicas para a IA implementadora

- `docs/especificacao.md` e `CHANGELOG.md` são **saída gerada**: mude o
  builder, nunca o markdown.
- Geração determinística — sem timestamp, sem caminho absoluto, sem ordem
  de `dict` não fixada. O CI compara bytes.
- **Nunca use `git checkout <arquivo>` para desfazer um teste em arquivo
  que você acabou de reescrever** — restaura a versão do HEAD e apaga o
  trabalho. Para remover uma linha de teste, use `sed`. (Aconteceu na
  primeira tentativa: o README novo foi perdido assim.)
- Os `README.md` do kit e do central são **diferentes**. Não copie um
  sobre o outro; no central, edite só os trechos que citam caminhos
  alterados.
- `check_links` varre a raiz do repositório, não a de `_framework/` —
  atenção ao `root.parent`.
- **NÃO alterar:** `templates/`, `prompts/`, `AGENTS.md`, `QUICKSTART.md`,
  `framework_lib.py`, `validate_*.py`, `registry_tools.py`,
  `.github/workflows/`.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0005`.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem código correspondente.
- [ ] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que implementou. Não
substitui a verificação independente exigida antes de `implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `wc -l < README.md` | `67` (teto 90; antes eram 280) | medição direta | sim |
| 2 | `grep -c` dos três caminhos no README | `5` ocorrências dos três alvos | medição direta | sim |
| 3 | `render_prompts.py` e `render_prompts.py --check` | `especificacao.md: gerado` (195 linhas), `CHANGELOG.md: gerado` (52); `--check` exit 0 | ver #4 | sim |
| 4 | linha intrusa em `docs/especificacao.md`, `--check`, regenerar | `exit=1` | **é o sensor**: edição manual do gerado reprova | sim |
| 5 | `grep -c "Iron Law\|red flag\|sizing\|handover" docs/especificacao.md` | `4` (mínimo 4) | medição direta | sim |
| 6 | `test ! -f Framework_Documentacao_Rastreabilidade.md` | removido no kit e no central | ausência é o sinal | sim |
| 7 | `grep -c "2.1.0" CHANGELOG.md` | `2` — a cópia à mão parava na 2.0.0 | comparação com o estado anterior | sim |
| 8 | `ls docs/guias/` e `grep -l "regra canônica"` | 3 arquivos, os 3 com o aviso | inspeção direta | sim |
| 9 | `check_renderings.py` nos dois repositórios | `0` linhas "quebrado" | ver #10 | sim |
| 10 | link para `docs/nao-existe.md` acrescentado ao README; check; removido com `sed` | `1` quebrado, depois `0`; README segue com 67 linhas | **é o sensor**. `sed` em vez de `git checkout`, conforme a instrução — na primeira tentativa o `git checkout` apagou o README novo | sim |
| 11 | `framework_check.py --auto` nos dois repositórios | `✅ Todas as verificações do framework passaram` | validador é o teste | sim |
| 12 | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída | diff vazio é o sinal | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0004, ADR-DTF-0001 |
| Branch | `sdd/SDD-DTF-0005-superficie-doc` |
| Tentativa | 2 — a primeira foi revertida, ver `docs/DTF/LESSONS.md` |
