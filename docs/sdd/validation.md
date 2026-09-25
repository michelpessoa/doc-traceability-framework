# Verificação — SDD-DTF-0042

- **Veredito:** PASS
- **Diff verificado:** `41570c9f47210c348ecae2d24b535ce5e86fb443..HEAD` (merge-base com `origin/main`; HEAD `15f38c6`)
- **Verificador independente:** sim (subagente sdd-verifier, sem histórico da sessão implementadora)

## Passo 0 — Fidelidade à origem

`check_source_docs.py` contra o central (`dtf-central-wt-0042/docs/DTF`): exit 0, SPEC-DTF-0017 e RFC-DTF-0008 conferem. RF01-RF10 da SPEC têm representação na SDD com critérios EARS e contratos da Parte 2 equivalentes; nenhum critério relaxado.

## Critérios de aceite (rodada 1)

Todos os 14 critérios rodados de novo nesta sessão; comandos e saídas na tabela "Evidência de verificação" de `docs/sdd/SDD-DTF-0042.md`. Resumo: 1-13 PASS (automatizados; sensores falharam com mutação nos critérios 3, 5, 10/11), 14 manual PASS. Suíte completa: 186 passed. `render_prompts.py --check` exit 0 no kit e no central; `cmp` x5 igual.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| 1-14 | ver SDD | ver SDD | ver SDD | Sim |

## Descompassos encontrados

Nenhum bloqueante. Notas: (d) o critério 14 usava `\|` em célula de tabela, que o parser do `validate_state.py` quebra; reescrito sem pipe (`git status --porcelain -- ...`), mesma semântica; (a) o diff do kit toca exatamente os arquivos previstos nas tasks 2-6 mais a própria SDD; (b) a Evidência do implementador citava `test_gate_texto.py:43` como asserção; a asserção real do segundo teste é `:45` (corrigido na tabela); (c) o critério 9 do implementador comparou contra `origin/main`; aqui foi usado o SHA fixo `41570c9`, mesmo resultado.

## Lições

Nenhuma nova. Registrar apenas: citar em "Assertion" a linha do `assert`, não a de pré-condição.
