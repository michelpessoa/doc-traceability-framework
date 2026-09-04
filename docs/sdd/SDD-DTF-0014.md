---
id: SDD-DTF-0014
type: SDD
title: "Lockfile de dependências dev + config de formatter explícita"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-04"
updated: "2026-09-04"
relates_to: [SDD-DTF-0013]
source_docs: []
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada, não falha de processo. Escopo mecânico: requirements.txt novo + CI passa a instalar dele + seção [format] em ruff.toml."
supersedes: null
superseded_by: null
tags: [tooling, higiene, kit-publico]
---

# Lockfile de dependências dev + config de formatter explícita

## Resumo executivo

Quarta rodada de harness score isolada no kit público (99/108, 92%,
L4) apontou 2 achados, ambos confirmados por leitura direta antes desta
SDD:

- **HYG-07 (lockfile)**: CI instala `pip install pyyaml pytest ruff
  mypy` sem versão fixada — build não reproduzível, cada run pode pegar
  versão diferente das ferramentas.
- **SNS-04 (formatter)**: `ruff format --check` já roda no CI
  (`SDD-DTF-0013`), mas a config do formatter é implícita (herda
  `line-length`/`target-version` do `[lint]`/topo de `ruff.toml`,
  sem seção `[format]` própria) — o sensor não detecta config de
  formatter declarada.

Terceiro achado da rodada (HYG-08, interpolação de env em `.mcp.json`)
segue fora de escopo — kit não tem config MCP, mesmo veredito das
rodadas anteriores.

`sizing: small` — 3 arquivos (`requirements.txt` novo,
`framework-check.yml`, `ruff.toml`), nenhum critério do gate
`rfc_to_adr` se aplica, comportamento externo não muda (mesmas
ferramentas, mesmas versões já em uso, só declaradas).

## Decisão(ões) de arquitetura aplicável(is)

Nenhuma — mudança de higiene/tooling, sem ADR.

## Requisitos consolidados

- `requirements.txt` na raiz do kit fixa as versões das ferramentas
  de dev usadas pelo CI: `pyyaml==6.0.1`, `pytest==9.1.1`,
  `ruff==0.16.6`, `mypy==2.3.1` (versões confirmadas nesta sessão via
  `pip show`).
- `.github/workflows/framework-check.yml` troca `pip install pyyaml
  pytest ruff mypy` por `pip install -r requirements.txt`.
- `ruff.toml` ganha seção `[format]` explícita — sem mudar
  comportamento (os valores já são os defaults herdados hoje), só
  declara a config pra ficar detectável.

Casos de borda: nenhum — mudança puramente declarativa, sem lógica.

Fora de escopo: atualizar as ferramentas para versão mais nova; HYG-08
(sem config MCP no kit, sem ação); lockfile de dependências de
produção (o kit não tem `install_requires`/pacote publicado, só
scripts).

## Especificação técnica consolidada

**`/requirements.txt`** (raiz do kit, arquivo novo):
```
pyyaml==6.0.1
pytest==9.1.1
ruff==0.16.6
mypy==2.3.1
```

**`.github/workflows/framework-check.yml`**, step "Instalar
dependências":
```yaml
- name: Instalar dependências
  run: pip install -r requirements.txt
```

**`/ruff.toml`**:
```toml
target-version = "py312"
line-length = 120
exclude = ["examples/**"]

[lint]
select = ["E", "F", "I", "W"]

[format]
quote-style = "double"
indent-style = "space"
```
(`quote-style`/`indent-style` são os defaults do `ruff format` — a
seção só torna explícito o que já estava em vigor implicitamente;
`ruff format --check` sobre o repositório continua `exit 0` sem
nenhuma reformatação.)

## Critérios de aceite / definição de pronto

| # | Critério | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | `requirements.txt` instala as mesmas ferramentas | `pip install -r requirements.txt` (ambiente limpo) | instala `pyyaml==6.0.1`, `pytest==9.1.1`, `ruff==0.16.6`, `mypy==2.3.1`, sem erro |
| 2 | CI usa o lockfile | `grep -n "pip install -r requirements.txt" .github/workflows/framework-check.yml` | 1 ocorrência |
| 3 | `[format]` declarado sem mudar comportamento | `ruff format --check _framework/scripts` | `exit 0`, "10 files already formatted" (nenhuma reformatação nova) |
| 4 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto` e `pytest` | `exit 0` nos dois |

## Instruções específicas para a IA implementadora

- Não atualizar nenhuma ferramenta para versão mais nova — pinar
  exatamente a versão já em uso (confirmada via `pip show` nesta
  sessão).
- `[format]` em `ruff.toml` deve reproduzir o comportamento atual
  (`quote-style`/`indent-style` = defaults) — rodar `ruff format
  --check` antes e depois da mudança, confirmar saída idêntica.
- Commits em Conventional Commits, com `Refs: SDD-DTF-0014`.
- Branch dedicada a partir de `main`, PR — nunca commit direto em main
  (gate seção 14).

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito consolidado tem código correspondente.
- [x] Único 3 arquivos tocados, todos listados em "Especificação
      técnica consolidada".
- [x] Nenhuma abstração, config extra ou refactor além do declarado.

## Evidência de verificação (preencher antes de status `implemented`)

**Verificador independente:** sim — sessão separada da implementação,
sem contexto herdado (leu só a SDD e o diff). A tabela abaixo (do
implementador) não foi usada como fonte de verdade — todos os comandos
foram rodados de novo pela verificação independente. Detalhe completo,
incluindo os sensores de discriminação dos critérios 2 e 3, em
`docs/sdd/validation.md`.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1 | `pip install --user --break-system-packages -r requirements.txt` | instala/confirma `pyyaml==6.0.1`, `pytest==9.1.1`, `ruff==0.16.6`, `mypy==2.3.1` | — | Sim |
| 2 | `grep -n "pip install -r requirements.txt" .github/workflows/framework-check.yml` | 1 ocorrência (linha 51) | — | Sim |
| 3 | `ruff format --check _framework/scripts` | `10 files already formatted` | — | Sim |
| 4 | `framework_check.py --auto` e `pytest` | `✅ Todas as verificações do framework passaram.`, `7 passed` | — | Sim |

Verificação independente (sessão separada, subagente/sessão de
verificação `verify-sdd`): comandos 1-4 rerodados do zero, mais sensor
de discriminação nos critérios 2 e 3 (linha do CI revertida → grep
falha; violação de formatação real introduzida → `ruff format --check`
falha). Veredito PASS. Detalhe completo em `docs/sdd/validation.md`.

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| Branch | `sdd/SDD-DTF-0014-lockfile-formatter` |
