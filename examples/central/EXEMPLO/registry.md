# Registry — Projeto EXEMPLO

_Gerado automaticamente a partir de `registry.yaml` em 2026-08-15 17:37. Não editar manualmente. Framework v1.1.0._

Total de documentos: **8**


## Strategy Doc (1)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `STRAT-EXEMPLO-0001` | Reduzir tempo de checkout em 30% | approved | time-produto | 2026-08-01 | RFC-EXEMPLO-0001 |


## RFC (2)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `RFC-EXEMPLO-0001` | Migrar processamento de pagamento para novo provedor | approved | time-checkout | 2026-08-05 | STRAT-EXEMPLO-0001, ADR-EXEMPLO-0001 |
| `RFC-EXEMPLO-0002` | Adicionar campo opcional de apelido no formulário de endereço | approved | time-checkout | 2026-08-11 | PRD-EXEMPLO-0002, TS-EXEMPLO-0002 |


## ADR (1)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `ADR-EXEMPLO-0001` | Adotar Provedor X para processamento de pagamento | approved | arquitetura | 2026-08-06 | RFC-EXEMPLO-0001, PRD-EXEMPLO-0001, TS-EXEMPLO-0001 |


## PRD (2)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `PRD-EXEMPLO-0001` | Novo fluxo de checkout com Provedor X | approved | time-produto | 2026-08-07 | RFC-EXEMPLO-0001, ADR-EXEMPLO-0001, SDD-EXEMPLO-0001 |
| `PRD-EXEMPLO-0002` | Campo opcional de apelido no endereço de entrega | approved | time-produto | 2026-08-11 | RFC-EXEMPLO-0002, SDD-EXEMPLO-0002 |


## Tech Spec (2)

| ID | Título | Status | Owner | Atualizado | Relacionados |
|---|---|---|---|---|---|
| `TS-EXEMPLO-0001` | Especificação técnica — integração com Provedor X | approved | time-checkout | 2026-08-07 | RFC-EXEMPLO-0001, ADR-EXEMPLO-0001, SDD-EXEMPLO-0001 |
| `TS-EXEMPLO-0002` | Especificação técnica — campo apelido de endereço | approved | time-checkout | 2026-08-11 | RFC-EXEMPLO-0002, SDD-EXEMPLO-0002 |
