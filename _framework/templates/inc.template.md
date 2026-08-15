---
id: INC-{PROJECT_CODE}-{SEQ}
type: INC
title: "{Título curto do incidente}"
status: open
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável pela resposta}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
severity: "{SEV1|SEV2|SEV3|SEV4}"
detected_at: "{YYYY-MM-DDTHH:MM}"
impact_summary: "{1-2 frases do impacto real}"
root_cause_key: "{identificador curto e estável da causa raiz, para detectar recorrência}"
tags: []
---

# {Título}

> INC não usa o ciclo de vida padrão do framework. Estados possíveis:
> `open → mitigated → resolved → closed`. Não é um documento para
> "aprovar" — é um evento operacional para acompanhar.

## Severidade
`{SEV1 | SEV2 | SEV3 | SEV4}` — critério objetivo, ver
`_framework/rules/workflow-rules.yaml` (`severity_scale`).

## Linha do tempo
| Horário | Evento |
|---|---|
| | Detecção |
| | Mitigação |
| | Resolução |

## Impacto
Quem/o quê foi afetado, por quanto tempo, severidade percebida pelo
usuário/cliente.

## Causa raiz (preliminar)
Hipótese inicial — o detalhamento definitivo vai para o Postmortem.

## Ações imediatas tomadas
O que foi feito para mitigar/resolver, na hora.

## Postmortem
Obrigatório? Ver `postmortem_policy` em `workflow-rules.yaml` (depende da
severidade e da regra de recorrência). Se sim, referenciar o PM criado em
`relates_to` assim que existir.
