# HANDOFF — STRAT-DTF-0003 item 10: sweep de requisitos transversais no template da SPEC (2026-09-22 22:00)

_Escopo: repo do projeto: doc-traceability-framework_

## Goal

Item 10 (último) da STRAT-DTF-0003 (central, `draft`): `spec.template.md`
ganha uma seção "sweep" — lista fixa de requisitos transversais que
ninguém escreve por padrão (autorização, concorrência, idempotência,
observabilidade, falha de dependência externa, validação de entrada,
limite de volume/rate), cada um com `destino` (RF-ID que cobre) ou `n/a`
+ motivo. Origem: E8 do `tlc-spec-lean`, já detalhado na tabela de
comparação de STRAT-DTF-0003 (seção "Comparação com o tlc-spec-lean").

## Status

Nada implementado. Sizing `small` já declarado na STRAT (itens 3-6 desta
mesma STRAT tiveram o mesmo sizing e foram direto a SDD, sem SPEC — ver
SDD-DTF-0034/0035 como precedente de forma). Este item segue o mesmo
caminho: **sem SPEC, sem RFC/ADR** — só SDD aqui, vínculo por `Refs:` no
commit.

## Ids relacionados

- STRAT-DTF-0003 — `draft` (repo central), item 10 é o último pendente
  da tabela; ao fechar, também avaliar se a STRAT inteira vira
  `implemented`/`approved` (perguntar ao humano, não decidir sozinho).

## Files touched

(nenhum ainda)

## Key decisions

- Sizing `small`, não `medium`: toca essencialmente 1 arquivo
  (`_framework/templates/spec.template.md`) + mecanização leve em
  `validate_doc.py` (~1 função nova), comportamento externo do produto
  não muda (é convenção de preenchimento de documento, não runtime).
- Mecanizar como checagem não-retroativa (mesma técnica de
  `SDD-DTF-0016`/`check_evidence_profile`, seção nova detectável por
  ausência estrutural, nunca por data de framework_version): SPECs
  criadas antes da seção existir no template não são reprovadas
  retroativamente por não terem a seção.
- Lista de categorias do sweep (mínimo, expansível depois):
  autorização/permissão, concorrência, idempotência, observabilidade,
  falha de dependência externa, validação de entrada, limite de
  volume/rate — cada linha da tabela nova exige `destino` (RF-ID) ou
  `n/a` + motivo, nunca célula vazia.

## Open threads / blockers

- Nenhum bloqueio técnico.
- Em aberto: se `validate_doc.py` deve reprovar SPEC `in_review` sem a
  seção preenchida (mecanizar de verdade, coerente com
  `gate_content_quality`) ou só o template ganhar a seção e a checagem
  ficar manual por ora. Recomendação: mecanizar — é o padrão que este
  STRAT inteiro vem seguindo (ver E1-E8 na tabela de comparação:
  "checagem mecânica" é sempre preferida a instrução solta).

## Next step

Compilar `SDD-DTF-0039` (próximo id livre) diretamente — sizing `small`,
sem `source_docs`. Conteúdo: (1) nova seção no
`_framework/templates/spec.template.md` entre "Requisitos não
funcionais" e "Fora de escopo"; (2) nova checagem em
`_framework/scripts/validate_doc.py` (não-retroativa); (3) atualizar
`_framework/rules/workflow-rules.yaml` (`gate_content_quality`, seção 15)
citando a seção nova; (4) replicar via `render_prompts.py`; (5) testes +
verificação independente antes de `implemented`. Depois, no repo
central: marcar item 10 **Concluído** na tabela de STRAT-DTF-0003
(mesmo padrão dos itens 1-9) e perguntar ao humano se a STRAT inteira
fecha.

## Don't do

- Não criar SPEC/RFC/ADR para este item — sizing `small` já declarado,
  criar documento a mais contradiz `TAMANHO DECIDE QUAIS DOCUMENTOS`.
- Não commitar direto em main — branch nomeada pelo id (`sdd/SDD-DTF-0039`),
  PR, merge humano.
- Não fechar a STRAT-DTF-0003 inteira sem perguntar — só o item 10 é
  escopo desta linha de trabalho.
