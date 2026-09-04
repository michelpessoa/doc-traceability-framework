---
id: SDD-DTF-0012
type: SDD
title: "Adiciona .env ao .gitignore do kit público"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-03"
updated: "2026-09-03"
relates_to: []
source_docs: []
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada, não falha de processo. Escopo mecânico: 1 linha em .gitignore."
supersedes: null
superseded_by: null
tags: [tooling, higiene, kit-publico]
---

# Adiciona .env ao .gitignore do kit público

## Resumo executivo

Terceira rodada de harness score isolada no kit público apontou HYG-02:
`.gitignore` não cobre `.env`, hoje só tem `__pycache__/` e `*.pyc`. Sem
`.env` real no repositório hoje (confirmado antes desta SDD), mas
ausência da regra é risco — qualquer contribuidor futuro que criar um
`.env` local (credenciais de teste, etc.) commitaria por acidente.

`sizing: small` — toca 1 arquivo, nenhum critério do gate `rfc_to_adr`
se aplica, comportamento externo não muda. `source_docs: []` por
decisão, não omissão.

## Decisão(ões) de arquitetura aplicável(is)

Nenhuma — mudança de higiene, sem ADR.

## Requisitos consolidados

- `.gitignore` do kit público ganha as linhas `.env` e `.env.*` (cobre
  variantes como `.env.local`), sem remover as entradas existentes
  (`__pycache__/`, `*.pyc`).

Casos de borda: nenhum `.env` versionado hoje — `git status` confirmado
limpo antes desta SDD, mudança é puramente preventiva.

Fora de escopo: `.env.example`/template de variáveis de ambiente — não
existe hoje, criar um é decisão separada sem requisito aqui.

## Especificação técnica consolidada

**`/.gitignore`** (raiz do kit):
```
__pycache__/
*.pyc
.env
.env.*
```

## Critérios de aceite / definição de pronto

| # | Critério | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | `.env` ignorado | `touch .env && git check-ignore .env && rm .env` | `git check-ignore` imprime `.env`, exit 0 |
| 2 | `.env.local` ignorado | `touch .env.local && git check-ignore .env.local && rm .env.local` | `git check-ignore` imprime `.env.local`, exit 0 |
| 3 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` | `exit 0` |

## Instruções específicas para a IA implementadora

- Só editar `.gitignore` — nenhum outro arquivo.
- Commit em Conventional Commits, com `Refs: SDD-DTF-0012`.
- Branch dedicada a partir de `main`, PR — nunca commit direto em main
  (gate seção 14).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Requisito consolidado tem código correspondente (2 linhas).
- [x] Único arquivo tocado é `.gitignore`, listado acima.
- [x] Nenhuma abstração, config extra ou refactor.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** sim — subagent `sdd-verifier`, sessão
separada da implementação, sem contexto herdado, worktree isolado a
partir de `origin/main`. Detalhe completo em `docs/sdd/validation.md`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `touch .env && git check-ignore .env` | imprime `.env`, exit 0 | Linhas removidas do `.gitignore` → exit 1; restauradas → exit 0 | Sim |
| 2 | `touch .env.local && git check-ignore .env.local` | imprime `.env.local`, exit 0 | Mesma quebra acima → exit 1; restaurado → exit 0 | Sim |
| 3 | `framework_check.py --auto` | `✅ Todas as verificações do framework passaram.` | — | Sim |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| Branch | `sdd/SDD-DTF-0012-gitignore-env` |
