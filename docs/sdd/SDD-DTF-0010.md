---
id: SDD-DTF-0010
type: SDD
title: "Fecha lacuna do harness score: skills expostas + teste real prometido em SDD-DTF-0009"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-04"
updated: "2026-09-04"
relates_to: [SDD-DTF-0009]
source_docs: []
consumption_instructions: "Sizing small — sem SPEC upstream. Mudança operacional: expõe o que já existe (skills) e completa teste já prometido em SDD-DTF-0009, sem decisão de arquitetura nova."
supersedes: null
superseded_by: null
tags: [neutralidade, adocao, testes]
---

# Fecha lacuna do harness score: skills expostas + teste real prometido em SDD-DTF-0009

> Sizing `small`: toca poucos arquivos, nenhum critério do gate RFC→ADR
> se aplica, comportamento externo não muda (só passa a existir onde já
> deveria). Vai direto para SDD — a ausência de SPEC é o registro de que
> a fase foi dispensada, não uma lacuna.

## Resumo executivo

Uma avaliação de harness score rodada isoladamente no kit público
encontrou duas lacunas reais: (1) `.claude/skills/` não existe no kit —
as 4 skills (`_framework/skills/*/SKILL.md`, com front-matter correto)
não aparecem onde uma ferramenta Claude Code as procura, mesmo padrão que
o central já resolve via symlink; (2) `SDD-DTF-0009` prometeu na
"Estratégia de teste" um arquivo de teste real para os builders de
`mechanization` em `render_prompts.py` — nunca foi escrito, e o desvio
não foi registrado. Esta SDD fecha as duas, sem decisão nova: a primeira
é replicar um padrão já aprovado no central; a segunda é completar escopo
já aprovado em `SDD-DTF-0009`.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR novo — `ADR-DTF-0001` (camada 3, adaptador por fornecedor) já
cobre os symlinks de skill (mesmo mecanismo usado pelo central); o teste
está dentro do escopo técnico já `approved`/`implemented` de
`SDD-DTF-0009`.

## Requisitos consolidados

- **Symlinks de skill**: `.claude/skills/<nome>/SKILL.md` →
  `../../../_framework/skills/<nome>/SKILL.md`, um por skill existente
  (`doc-traceability-framework`, `handover`, `pickup`, `verify-sdd`) —
  mesmo alvo relativo que o central usa hoje, confirmado por
  `readlink`.
- **Teste real de `render_prompts.py` mechanization**: arquivo
  `_framework/scripts/tests/test_render_prompts_mechanization.py`
  cobrindo os pontos já descritos na tabela "Estratégia de teste" de
  `SDD-DTF-0009` — agrupamento de hooks por evento, geração de
  agent/command, geração de `guard_bash.sh` idêntica ao arquivo real em
  disco (via YAML real do repo, não fixture), capacidade sem
  `mechanization` não gera hook, e os dois `SystemExit`/`ValueError` de
  validação (`artifact_type` desconhecido, colisão de
  `mechanization_filename`).
- **CI**: `.github/workflows/framework-check.yml` roda
  `pytest _framework/scripts/tests/` antes dos validators; gatilho do
  workflow ganha `.claude/**` nos `paths` do `pull_request` (hoje só
  cobria `_framework/**`, deixando mudança em `.claude/*` sem rodar CI).

Fora de escopo: linter (é decisão de ferramenta nova — SPEC separada,
sizing `medium`); qualquer teste fora do módulo `mechanization` de
`render_prompts.py`.

## Especificação técnica consolidada

- `.claude/skills/{doc-traceability-framework,handover,pickup,verify-sdd}/SKILL.md`
  — 4 symlinks novos, criados com `ln -s`, sem conteúdo próprio.
- `_framework/scripts/tests/test_render_prompts_mechanization.py` —
  7 testes `pytest`, importando `render_prompts.py` via
  `sys.path.insert` (mesmo padrão que os scripts do framework já usam
  entre si). O teste de `guard_bash.sh` carrega o YAML real do repo
  (`framework_lib.find_rules_file`/`load_rules`) e compara byte a byte
  com o arquivo em disco — não usa fixture sintética, porque o requisito
  não funcional de `SDD-DTF-0009` é justamente "gerado bate com o real".
- `.github/workflows/framework-check.yml` — novo step "Testes de
  mechanization" (`pip install pytest` + `pytest _framework/scripts/tests/ -v`),
  antes do step de validação de registries; `.claude/**` adicionado aos
  `paths` do gatilho `pull_request`.

## Critérios de aceite / definição de pronto

| # | Critério | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | 4 symlinks resolvem para o `SKILL.md` real | `for n in doc-traceability-framework handover pickup verify-sdd; do readlink -f .claude/skills/$n/SKILL.md; done` | 4 caminhos absolutos existentes, cada um em `_framework/skills/<n>/SKILL.md` |
| 2 | Suite de teste passa | `python3 -m pytest _framework/scripts/tests/ -v` | `7 passed` |
| 3 | Sensor: teste de `guard_bash.sh` discrimina | Trocar `deny "{entry["message"]}" ;;` por `echo ...` em `build_guard_bash`, rodar o teste, reverter | falha com a mudança, passa depois de reverter |
| 4 | CI dispara para mudança em `.claude/**` | `grep -A5 "pull_request:" .github/workflows/framework-check.yml` | `.claude/**` presente em `paths` |
| 5 | Regressão | `python3 _framework/scripts/framework_check.py --auto` e `python3 _framework/scripts/render_prompts.py --check` | `exit 0` nos dois |

## Instruções específicas para a IA implementadora

- Symlinks são triviais — não vira script/gerador; são 4 `ln -s`
  manuais, mesmo espírito do central (não há necessidade de generalizar
  isso em `render_prompts.py` agora, é cópia de estrutura, não conteúdo
  variável por YAML).
- O teste de `guard_bash.sh` **precisa** usar o YAML real do repositório,
  não uma fixture sintética — é o único jeito de pegar divergência real
  entre o script gerado e o script em disco.
- Não adicionar `pyproject.toml`/config de linter aqui — fora de escopo
  desta SDD (ver "Fora de escopo" acima).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [x] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não ainda — mesma sessão que implementou
rodou os comandos abaixo como autorrevisão, com saída real e sensor de
discriminação no critério 3. Status fica em `approved`, não
`implemented`, até um agente `sdd-verifier` separado confirmar em sessão
própria — mesmo gate da seção 16, sem exceção para sizing `small`
("nunca dispensa... a verificação de escopo com evidência antes de
`implemented`"). Nota de processo: o código abaixo foi escrito antes
desta SDD existir, violando a ordem documento→código (seção 13) — a SDD
deveria ter sido escrita primeiro, mesmo em sizing `small`. Registrado
aqui em vez de encobrir; sem `LESSONS.md` porque não houve estado ruim
persistido (nada foi commitado fora de branch, nenhum status avançou
incorretamente) — é o tipo de desvio que a autorrevisão já pega antes do
commit, diferente da falha maior de `SDD-DTF-0009`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `readlink` nos 4 symlinks | 4 caminhos para `_framework/skills/<n>/SKILL.md`, todos existentes | — | Sim |
| 2 | `python3 -m pytest _framework/scripts/tests/ -v` | `7 passed in 0.12s` | — | Sim |
| 3 | troquei `deny` por `echo` em `build_guard_bash`, rodei o teste do guard_bash, revertei, rodei de novo | `1 failed` → `1 passed` | negativo→positivo | Sim |
| 4 | `grep -A5 "pull_request:" .github/workflows/framework-check.yml` | `.claude/**` presente | — | Sim |
| 5 | `framework_check.py --auto` e `render_prompts.py --check` | ambos `exit 0` (`✅ Todas as verificações do framework passaram.`) | — | Sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0009 |
| Branch | `sdd/SDD-DTF-0010-fecha-lacuna-harness` |
