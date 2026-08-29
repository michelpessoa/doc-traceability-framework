---
id: SDD-DTF-0004
type: SDD
title: "Exclusão de artefatos operacionais na varredura de documentos"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-08-29"
updated: "2026-08-29"
relates_to: [SPEC-DTF-0005]
source_docs:
  - id: "SPEC-DTF-0005"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0005.md"
consumption_instructions: "Excluir por nome exato, lido do YAML. Não desligar a varredura de docs/{PROJECT_CODE}/ — o sensor do critério 3 existe para pegar exatamente isso."
supersedes: null
superseded_by: null
tags: [validadores, artefatos]
---

# Exclusão de artefatos operacionais na varredura de documentos

## Resumo executivo

`lessons_policy` manda escrever `LESSONS.md` em `docs/{PROJECT_CODE}/` e
`handover_protocol` manda escrever `HANDOFF.md` no mesmo lugar. Nenhum dos
dois tem front-matter — não são documentos do fluxo, são artefatos
operacionais. Mas `iter_documents` varre todo `.md` sob o diretório,
excluindo apenas `registry.md` e `templates/`, então o validador reprova
os arquivos que o próprio framework exige. Descoberto ao registrar a
primeira lição do projeto DTF.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `medium` de `SPEC-DTF-0005` dispensou RFC e ADR: nenhum
critério de `decision_gates.rfc_to_adr` se aplica.

## Requisitos consolidados

- **RF01** — `LESSONS.md` e `HANDOFF.md` não são varridos como documento,
  em qualquer diretório.
- **RF02** — a lista sai do YAML (`operational_artifacts`), com fallback
  no código quando a chave não existir.
- **RF03** — arquivo fora da lista e sem front-matter continua reprovando.
- **RF04** — o aviso de "existe em disco mas não está no registry" também
  respeita a lista.
- **RF05** — `docs/DTF/LESSONS.md` valida limpo.

Casos de borda: `LESSONS.md` junto de `docs/sdd/` também é excluído;
`lessons.md` minúsculo **não** é (nome exato); `LESSONS.md` com
front-matter por engano é ignorado do mesmo jeito, porque a exclusão é por
nome.

## Especificação técnica consolidada

- `_framework/rules/workflow-rules.yaml` — chave de topo
  `operational_artifacts`, mapa `nome -> {purpose, declared_in}`, com
  `LESSONS.md` e `HANDOFF.md`.
- `_framework/scripts/framework_lib.py` —
  `_FALLBACK_OPERATIONAL_ARTIFACTS = ("LESSONS.md", "HANDOFF.md")`;
  `OPERATIONAL_ARTIFACTS` derivada em `_derive_constants`;
  `iter_documents` pulando `path.name` que esteja nela.
- `_framework/scripts/registry_tools.py` — **nenhuma alteração
  necessária**: a varredura de disco já chama `iter_documents`, então
  herda a exclusão. Registrado aqui porque a SDD previa tocar o arquivo e
  a implementação não tocou — escopo menor que o planejado é desvio tanto
  quanto escopo maior.
- Cópia do YAML em `skills/doc-traceability-framework/references/`
  sincronizada.

**NÃO alterar:** templates, prompts, `AGENTS.md`/`QUICKSTART.md` e nada
da reorganização de documentação (`SPEC-DTF-0004`), que é a etapa
seguinte.

**Rollout:** branch `sdd/SDD-DTF-0004-artefatos-operacionais`, PR com CI
verde nos dois repositórios.

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF05, RF01 — LESSONS.md valida limpo | `framework_check.py --auto` no central, com `docs/DTF/LESSONS.md` presente | exit 0 |
| 2 | RF04 — sem aviso de não registrado | mesma saída do critério 1 | não contém "LESSONS.md existe em disco" |
| 3 | RF03 (sensor) — arquivo fora da lista reprova | Criar `docs/DTF/NAO-E-ARTEFATO.md` sem front-matter, validar, remover | exit 1 na presença do arquivo |
| 4 | RF01 — HANDOFF.md também excluído | Criar `docs/DTF/HANDOFF.md` sem front-matter, validar, remover | exit 0 |
| 5 | RF02 — lista derivada do YAML | `python3 -c "from framework_lib import OPERATIONAL_ARTIFACTS; print(OPERATIONAL_ARTIFACTS)"` | contém os dois nomes |
| 6 | RF02 (fallback) — chave ausente não quebra | `python3 -c` chamando `_derive_constants` com dicionário sem a chave | devolve o fallback |
| 7 | Regressão | `framework_check.py --auto` nos dois repositórios | exit 0 |
| 8 | Paridade | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída |

## Instruções específicas para a IA implementadora

- Exclusão por **nome exato**, nunca por sufixo ou regex ampla.
- `OPERATIONAL_ARTIFACTS` segue o padrão de `DOC_TYPES`: derivada do YAML
  em `_derive_constants`, com constante de fallback.
- Não mexer em `validate_doc.py` nem em `validate_state.py` — a exclusão é
  na varredura, não na checagem.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0004`.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem código correspondente.
- [ ] Todo arquivo tocado aparece em "Especificação técnica consolidada".
- [ ] Nenhuma abstração, config, feature flag ou refactor extra.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** não — mesma sessão que implementou. Não
substitui a verificação independente exigida antes de `implemented`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `framework_check.py --auto` no central, com `docs/DTF/LESSONS.md` presente | `✅ Todas as verificações do framework passaram` | ver #3 | sim |
| 2 | mesma saída, `grep -c "LESSONS.md"` | `0` — nem erro de front-matter, nem aviso de não registrado | contagem zero é o sinal | sim |
| 3 | `docs/DTF/NAO-E-ARTEFATO.md` criado sem front-matter, validado, removido | `exit=1` | **é o sensor**: arquivo fora da lista continua reprovando; se passasse, a varredura estaria desligada | sim |
| 4 | `docs/DTF/HANDOFF.md` criado sem front-matter, validado, removido | `exit=0` | par com #3: mesmo tipo de arquivo, resultado oposto conforme esteja na lista | sim |
| 5 | `from framework_lib import OPERATIONAL_ARTIFACTS` | `('LESSONS.md', 'HANDOFF.md')` — derivada do YAML | leitura direta | sim |
| 6 | `_derive_constants` com dicionário sem a chave | devolve `('LESSONS.md', 'HANDOFF.md')` pelo fallback | ausência da chave exercitada de propósito | sim |
| 7 | `framework_check.py --auto` nos dois repositórios | exit 0 | validador é o teste | sim |
| 8 | `diff -r --exclude=__pycache__` entre os dois `_framework/` | sem saída | diff vazio é o sinal | sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0005 |
| Branch | `sdd/SDD-DTF-0004-artefatos-operacionais` |
