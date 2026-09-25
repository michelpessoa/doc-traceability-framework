# Verificação — SDD-DTF-0048

- **Veredito:** PASS (rodada 2)
- **Diff verificado:** `c74f45b..ad47261` no kit (main antes e depois do PR #126); central `b348b42..b54e9ba` (PR #149)
- **Verificador independente:** sim (subagente sdd-verifier, sem histórico da sessão implementadora)

## Passo 0 — Fidelidade à origem

`check_source_docs.py` contra o central: exit 0 (SPEC-DTF-0021, SPEC-DTF-0023 e RFC-DTF-0008 conferem). RF01 a RF13 da SPEC-DTF-0021 têm requisito idêntico na SDD; as quatro correções da SPEC-DTF-0023 (copilot-instructions.md em RF09, RF12, A13 e A15; A05 com `2 failed, 2 passed`; seção "0" isenta de banner; guia-tecnico.md pode ficar fora do diff) estão refletidas na SDD e no teste. Nenhum critério relaxado.

## Critérios de aceite (rodada 2)

Todos os 15 critérios rodados de novo nesta sessão; comandos e saídas na tabela "Evidência de verificação" de `docs/sdd/SDD-DTF-0048.md`.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| A01 | `SCAN` ANTES e DEPOIS | `(36, 68)` e `(0, 0)` | mutação A05 | Sim |
| A02 | grep das expressões antigas | 19 e 3 | mutação A05 | Sim |
| A03 | `grep -n "^# 15\."` | banner novo `DA SPEC E DA SDD` | mutação A05 | Sim |
| A04 | pytest `test_prd_ts_texto.py` | 4 passed | mutações a, b e banner `# 12.` falharam | Sim |
| A05 | mutações (a), (b), (c) | `2 failed, 2 passed` (a e b), 4 passed (c) | é o sensor | Sim |
| A06 | pytest `test_gate_texto.py` | 2 passed | `SPEC` trocado por `PRD` falhou (1 failed) | Sim |
| A07 | `ESTRUTURA` | `22 True`, exit 0 | sem teste | Sim |
| A08 | leitura do YAML | `2.3.2 2.3.2 2.3.1 True` | sem teste | Sim |
| A09 | `render_prompts.py` e `--check` | exit=0; árvore limpa após regenerar | sem teste próprio | Sim |
| A10 | grep nos gerados | ANTES 6,1,2; DEPOIS 1,0,2 | sem teste | Sim |
| A11 | pytest da suíte | 270 passed | ver A04 a A06 | Sim |
| A12 | central, `framework_check` e `validate_doc` antes/depois | exit=0 nos dois; 17 x exit=0; diff ABSTRACTCLINIC vazio; diff do `framework_check` só caminho, rótulo de versão e um aviso informativo | sem teste | Sim (em substância) |
| A13 | comando corrigido no central | 13 `igual`, exit=0 | sem teste | Sim |
| A14 | ancestralidade, `--check` e regeneração no head do PR #127 | 0048 entrou primeiro; exit=0; nada muda ao regenerar; CI do #127 SUCCESS; #127 ainda OPEN | n/a (manual) | Sim (parcial, manual) |
| A15 | `git diff --name-only c74f45b ad47261` | só arquivos previstos, mais `docs/sdd/registry.md` gerado | sem teste | Sim (com observação) |

## Descompassos encontrados

Nenhum bloqueante. Observações:

1. A12, literal: os `diff` de saída não são vazios (caminho do worktree, rótulo `2.3.1` para `2.3.2` e um aviso informativo novo, `projeto opera sob framework 2.3.1; kit atual é 2.3.2`, porque o `framework_version` do `docs/DTF/registry.yaml` ficou fora) e `git diff --stat` lista `docs/DTF/registry.md` (rótulo de versão). Em substância o critério vale: mesmos códigos de saída, mesma saída de `validate_doc.py` nos 17 documentos ABSTRACTCLINIC, nenhum `registry.yaml`, `examples/` ou script alterado, nenhum erro novo. O rótulo vem do kit, não de decisão sobre o projeto.
2. `docs/sdd/registry.md` do kit está no diff da implementação e não constava da lista de A15 nem da SDD. É gerado (rótulo de versão e status approved das SDDs 0048 e 0049); `registry.yaml` não mudou. Registrado na SDD como escopo gerado.
3. A14: a 0049 (PR #127) ainda está `OPEN`; o que é mecânico foi verificado no head do PR (`2d50c83`, contém `ad47261`), e a ausência de edição à mão nos gerados só se confirma por leitura do histórico do PR (manual).
4. A02: as linhas remanescentes no head são 523, 1001 e 1086 (a SDD cita 513, 991 e 1076, antes do changelog novo de 10 linhas); mesma contagem e mesmas âncoras.
5. Fora da SDD e a decidir: bump de `framework_version` do `docs/DTF/registry.yaml` (PR de documento separado).

## Lições

- Critério que compara "saída antes e depois" de um validador que imprime a versão do kit nunca dá diff vazio quando o kit sobe de versão; escrever o critério sobre códigos de saída e conteúdo de erro, não sobre texto integral.
- Arquivo gerado de registry (`registry.md`) muda com o bump de versão do kit: listar em A15 e RF10 como exceção gerada.
- Sensor de discriminação de teste de texto: mutar dentro do escopo exato que o teste lê (o `test_gate_texto.py` só olha `gate_implementation_before_code`).
