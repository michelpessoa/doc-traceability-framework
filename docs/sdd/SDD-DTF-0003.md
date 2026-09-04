---
id: SDD-DTF-0003
type: SDD
title: "Datação das exigências do gate 16 em validate_state.py"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-09-04"
relates_to: [SPEC-DTF-0003]
source_docs:
  - id: "SPEC-DTF-0003"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0003.md"
consumption_instructions: "Copie o mecanismo já existente em validate_doc.py — RULE_SINCE, project_version, rule_applies — em vez de inventar outro. Não altere nenhum documento de projeto para fazer a validação passar."
supersedes: null
superseded_by: null
tags: [nao-retroatividade, validadores]
---

# Datação das exigências do gate 16 em validate_state.py

## Resumo executivo

`lessons_policy.non_retroactive` é declarada desde a v1.5.0: regra nova
não reprova projeto antigo. `validate_doc.py` implementa isso com
`RULE_SINCE` + `rule_applies`. `validate_state.py` não implementa nada
disso — aplica as exigências da seção 16 (nascidas na v1.7.0) a qualquer
projeto. Consequência medida: as 9 SDDs do EVM, que opera em 1.6.0,
produzem 5 problemas e 4 warnings. Esta SDD leva o mesmo mecanismo para o
segundo validador.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — o sizing `medium` de `SPEC-DTF-0003` dispensou RFC e ADR: o
padrão a seguir já existe no repositório e está em uso, então não há
alternativa técnica em disputa.

## Requisitos consolidados

- **RF01** — `RULE_SINCE` em `validate_state.py`, versão do projeto
  resolvida pelo mesmo `project_version` de `validate_doc.py`.
- **RF02** — exigência posterior à versão do projeto não emite problema
  **nem warning**.
- **RF03** — projeto na versão da regra ou posterior mantém o
  comportamento atual, sem afrouxar nada.
- **RF04** — versão indeterminada é tratada como atual (semântica de
  `rule_applies`).
- **RF05** — `docs/sdd` do EVM valida limpo sem que nenhum documento dele
  seja editado.

Casos de borda: SDD fora de diretório com `registry.yaml` (versão
indeterminada → tudo vale); projeto 1.6.0 com evidência malformada
(silêncio — aplicar a regra pela metade é pior que não aplicar); projeto
exatamente em 1.7.0 (a regra vale, comparação é "igual ou posterior").

## Especificação técnica consolidada

Arquivo único: `_framework/scripts/validate_state.py`.

- `RULE_SINCE = {"evidence_required": "1.7.0", "scope_checklist": "1.7.0"}` —
  as duas exigências nasceram com a seção 16.
- `check_sdd(path: Path, version: str | None = None)` — quando `version`
  é omitida, resolve com `project_version(path)`. Guarda local
  `applies(rule)` idêntica à de `validate_doc.check_document`.
- Bloco pré-`implemented`: os dois warnings passam a depender de
  `applies("evidence_required")` e `applies("scope_checklist")`.
- Bloco `implemented`: todas as checagens de evidência sob
  `applies("evidence_required")`; a checklist de escopo sob
  `applies("scope_checklist")`.
- Importar `project_version` e `rule_applies` de `framework_lib`.

O bloco `implemented` é dividido em duas funções, `check_evidence` e
`check_scope`, para que cada exigência tenha sua própria guarda de versão.
**Desvio registrado:** o código antigo tinha um `return` logo após
"evidência ausente", que impedia a checagem de escopo de rodar no mesmo
documento; com as funções separadas, as duas rodam sempre. Efeito: uma SDD
`implemented` sem nenhuma das duas seções passa a produzir 2 problemas em
vez de 1. Nenhum documento muda de "passa" para "reprova" — só o relatório
fica completo. A alternativa (preservar o `return`) manteria o escopo
dependente da evidência, acoplamento que não está em regra alguma.

**NÃO alterar:** `registry_tools.py` (fora de escopo declarado),
o YAML, os templates, e nenhum documento de EVM ou ABSTRACTCLINIC.

**Rollout:** branch `sdd/SDD-DTF-0003-nao-retroatividade`, PR com CI
verde, replicado no central. Rollback é `git revert` de um arquivo.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF05 — EVM valida limpo | `validate_state.py /home/michel/projetos/viverMelhor/docs/sdd` | Sai 0, sem problema e sem warning |
| 2 | RF03 (sensor) — elevar a versão faz reprovar de novo | Copiar o `docs/sdd` do EVM, trocar `framework_version` para `1.7.0`, revalidar | Sai 1, com as mesmas 5 SDDs reprovadas |
| 3 | RF02 — nenhum documento do EVM foi tocado | `git -C /home/michel/projetos/viverMelhor status --porcelain docs/sdd` | Sem saída |
| 4 | RF04 — versão indeterminada aplica tudo | Copiar uma SDD do EVM sozinha, sem `registry.yaml`, e validar | Sai 1 — exigências valem |
| 5 | RF03 (regressão) — kit continua reprovando o que deve | Copiar `SDD-DTF-0001`, marcar `implemented`, apagar a tabela de evidência, validar | Sai 1 |
| 6 | RF01 — mecanismo idêntico ao de validate_doc | `grep -c "RULE_SINCE\|rule_applies\|project_version" validate_state.py` | ≥ 3 |
| 7 | Regressão geral | `framework_check.py --auto` no repositório central | Sai 0 |
| 8 | Paridade entre repositórios | `diff -r --exclude=__pycache__` entre os dois `_framework/` | Sem saída |

## Instruções específicas para a IA implementadora

- Reaproveite `project_version` e `rule_applies`; não escreva comparação
  de versão nova.
- Use os mesmos nomes de `validate_doc.py` (`RULE_SINCE`, `applies`) — a
  simetria entre os dois arquivos é o que evita a divergência voltar.
- O gate não pode afrouxar para projeto atual: se o sensor do critério 2
  não reprovar, a correção está errada.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0003`.

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado acima tem código correspondente.
- [x] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [x] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que implementou (tabela
abaixo, rodada durante a implementação). A verificação independente
exigida antes de `implemented` foi feita à parte, em subagente separado,
e está registrada em `docs/sdd/validation.md` — veredito
PASS, com um descompasso não bloqueante (paridade de formatação entre
repositórios, causada por commit de tooling posterior e não relacionado
a esta SDD).

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `validate_state.py /home/michel/projetos/viverMelhor/docs/sdd` | `✅ 9 documento(s) verificados`; `exit=0`, sem warning | ver #2 | sim |
| 2 | mesma árvore copiada, `framework_version` trocada para `1.7.0` | `exit=1`; reprova SDD-EVM-0001/0002/0003/0004/0009 | **é o sensor**: se a correção tivesse desligado o gate, isto passaria | sim |
| 3 | `git -C /home/michel/projetos/viverMelhor status --porcelain docs/sdd` | sem saída — nenhum documento do EVM tocado | saída vazia é o sinal | sim |
| 4 | `validate_state.py` numa SDD do EVM copiada sozinha, sem `registry.yaml` | `exit=1` — versão indeterminada aplica tudo | par com #1: mesma SDD, resultado oposto conforme a versão seja conhecida ou não | sim |
| 5 | `SDD-DTF-0001` copiada, marcada `implemented`, seção de evidência removida, validada sob 2.0.0 | `exit=1` | quebra introduzida de propósito em cópia descartável | sim |
| 6 | `grep -c "RULE_SINCE\|rule_applies\|project_version" validate_state.py` | `6` (mínimo 3) | medição direta | sim |
| 7 | `framework_check.py --auto` no central | `✅ Todas as verificações do framework passaram` — 42 docs | validador é o teste | sim |
| 8 | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída | diff vazio é o sinal | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0003 |
| Branch | `sdd/SDD-DTF-0003-nao-retroatividade` |
