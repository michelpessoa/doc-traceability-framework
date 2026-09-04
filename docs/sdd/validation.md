# Verificação — SDD-DTF-0014

- **Veredito:** PASS
- **Diff verificado:** `main..sdd/SDD-DTF-0014-lockfile-formatter` (commit `1055ffc` "fix(tooling): lockfile de deps dev + config de formatter explicita", PR #43, ainda não mergeada em `main`).
- **Verificador independente:** sim — sessão separada da implementação, sem contexto herdado (leu só a SDD e o diff). A tabela de evidência preenchida pelo implementador dentro da SDD **não** foi usada como fonte de verdade — todos os comandos abaixo foram rodados de novo, nesta sessão.

| # | Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | `requirements.txt` instala as mesmas ferramentas pinadas | `python3 -m pip install --user --break-system-packages -r requirements.txt` | `Requirement already satisfied: pyyaml==6.0.1 / pytest==9.1.1 / ruff==0.16.6 / mypy==2.3.1`, sem erro | conteúdo do arquivo comparado com `diff` contra o texto exato da "Especificação técnica consolidada" da SDD — idêntico, byte a byte | Sim |
| 2 | CI usa o lockfile | `grep -n "pip install -r requirements.txt" .github/workflows/framework-check.yml` | `51:        run: pip install -r requirements.txt` (1 ocorrência) | revertida a linha para `pip install pyyaml pytest ruff mypy` → `grep` sai com exit 1 (não encontra); linha restaurada → volta a exit 0. Discrimina corretamente | Sim |
| 3 | `[format]` declarado sem mudar comportamento | `ruff format --check _framework/scripts` | `10 files already formatted`, exit 0 | (a) removida a seção `[format]` inteira do `ruff.toml` → mesma saída (`10 files already formatted`, exit 0) — comportamento idêntico com ou sem a seção, como a SDD alega; restaurado o arquivo original. (b) com `[format]` presente, introduzida violação real (`'aspas simples'` em vez de `"duplas"`) num script de `_framework/scripts` → `ruff format --check` falha (exit 1, "1 file would be reformatted", aponta a linha); desfeita a violação → volta a exit 0. Ambos os testes confirmam que o check discrimina de verdade | Sim |
| 4 | Regressão geral | `python3 _framework/scripts/framework_check.py --auto`; `python3 -m pytest` | `✅ Todas as verificações do framework passaram.` (exit 0); `7 passed in 0.13s` (exit 0) | coberto indiretamente pelos sensores 2 e 3 acima; sem defeito isolável próprio a injetar aqui sem duplicar os anteriores | Sim |

## Conformidade com a spec (as duas direções)

- Os 3 requisitos consolidados (`requirements.txt` novo, CI usando `-r
  requirements.txt`, `[format]` em `ruff.toml`) têm código correspondente
  identificável, um a um.
- Arquivos do diff `main..sdd/SDD-DTF-0014-lockfile-formatter`:
  `.github/workflows/framework-check.yml`, `requirements.txt`,
  `ruff.toml` — os 3 declarados na "Especificação técnica consolidada" —
  mais `docs/sdd/SDD-DTF-0014.md` e `docs/sdd/registry.yaml`, que são
  bookkeeping padrão do próprio fluxo de SDD (criação/registro do
  documento), não scope creep.
- Nenhuma abstração, dependência, feature flag ou refactor sem requisito
  correspondente. `git status --short` limpo ao final — nenhum resíduo
  dos experimentos de sensor.

## Descompassos encontrados

Nenhum.

## Lições

Nenhuma lição nova — os 3 arquivos batem exatamente com a spec, e os
sensores dos critérios 2 e 3 confirmam que os comandos de aceite
realmente discriminam implementação certa de errada (falham quando o
comportamento correspondente é quebrado de verdade, não são ruído verde).
