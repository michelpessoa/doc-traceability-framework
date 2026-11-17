# Verificação — SDD-DTF-0056

- **Veredito:** FAIL
- **Causa:** implementacao (gerado desatualizado; correção mecânica, sem mudança de código)
- **Diff verificado:** `012ff47..a620b1c` no kit (branch `sdd/SDD-DTF-0056-registry-md-todos-os-tipos`, PR #146); espelho no central em `e41dc71` (branch `claude/laughing-galileo-d9nymc`, PR #204)
- **Rodada:** 1
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | n/a (sizing small, `source_docs: []`) | SDD lida inteira; RF01 a RF06 têm código e teste correspondentes | n/a | Sim |
| A01 (RF01 a RF06) | `pytest _framework/scripts/tests/test_generate_registry_md.py -q`, ANTES em worktree de `012ff47` com o teste novo copiado, DEPOIS em `a620b1c` | ANTES 8 failed, 4 passed; DEPOIS 12 passed | A02, A03 e quatro mutações extras | Sim |
| A02 (RF03) | Linha `order += sorted(t for t in by_type if t not in order)` removida, em worktree descartável | 2 failed (tipo não declarado, soma das linhas); restaurado 12 passed | Derrubada | Sim |
| A03 (RF01) | `type_order` trocada por `return [t for t in TYPE_ORDER if t != "SPEC"]` | 3 failed (ordem do YAML, ordem embutida, rótulos); restaurado 12 passed | Derrubada | Sim |
| A04 | `render_prompts.py --check; echo exit=$?; cmp` script x cópia da skill | `❌ docs/sdd/INDEX.md: divergente do gerado`; `exit=1`; `cmp` sem saída | n/a (medição) | **Não** |
| A05 | pytest das duas suítes; `ruff check`; `ruff format --check`; `mypy _framework/scripts` | 392 passed; All checks passed; 38 files already formatted; Success: no issues found in 38 source files | sem sensor próprio (suíte inteira) | Sim |
| A06 | `git diff --name-status origin/main` (= `012ff47`) | 8 arquivos, todos previstos; `workflow-rules.yaml` intocado, `framework.version` 2.5.0 | n/a (medição) | Sim |
| A07 | No central: `cmp` dos 3 arquivos; `generate_registry_md.py docs/DTF --check`; `grep -c` de SPEC; `framework_check.py --auto` | 3 `igual ...`; `em dia`; 29 = 29 SPECs no registry.yaml; `exit=0` | n/a (medição; teste espelhado coberto por A02/A03) | Sim |

## Descompassos encontrados

1. **A04 reprova (bloqueante).** `docs/sdd/INDEX.md` ficou desatualizado. A
   coluna "Arquivos de código" é extraída da "Decomposição em tasks"
   (`render_indexes.py`, `extract_sdd_files`). A edição pós-aprovação da task
   3 (commit `a620b1c`) acrescentou `_framework/INDEX.md` a essa coluna, mas
   `docs/sdd/INDEX.md` não foi regenerado depois, e continua com a lista do
   commit `fa87aa5`. Regenerado num worktree descartável, a linha da
   SDD-DTF-0056 passa a começar por `_framework/INDEX.md` (segue `+4`). O
   código, os testes e o espelho estão corretos; falta só o gerado.
2. **Edição da SDD depois da aprovação (task 3 ganhou `_framework/INDEX.md`).**
   Avaliação: o escopo acrescentado é legítimo. A faixa de tamanho do teste
   passou de `<2 KB` para `2-8 KB` (1957 para 5171 bytes), e `render_prompts.py
   --check` cobra `_framework/INDEX.md` em dia; sem regenerá-lo, o A04
   reprovaria pelo outro índice. É um arquivo gerado, sem comportamento, e o
   texto da task diz o motivo. Sem a edição, o A06 ("só os arquivos das tasks 1
   a 3") reprovaria. Mas é uma mudança na seção "Decomposição em tasks", que
   entra no hash de `approval_policy` (não está em `hash_excluded_sections`).
   Hoje não reprova em nada mecânico: a SDD não tem `approved_by`, e
   `validate_state.py` não o cobra porque `docs/sdd/registry.yaml` declara
   `framework_version: "2.3.1"` (RF08 da SDD-DTF-0054, não-retroativo;
   `validate_state.py docs/sdd/SDD-DTF-0056.md` sai 0). Esse é o caminho
   "atualize a SDD" do passo 1. Cabe ao owner registrar que aceita a edição
   como parte do texto aprovado. Foi ela que causou o descompasso 1.
3. **Central: `_framework/INDEX.md` fora da task 4 (não bloqueante).** O diff do
   central (`origin/main...e41dc71`) tem 5 arquivos: os 4 da task 4 e mais
   `_framework/INDEX.md`. Esse arquivo é idêntico ao do kit (`cmp` sem saída) e
   é a mesma mudança de faixa. `render_prompts.py --check` no central sai 0.
   O A07 não o cobre e ele não está listado em "Arquivos tocados" da task 4.
   Sugestão: acrescentar `central:_framework/INDEX.md` à task 4, junto com a
   correção do descompasso 1.

Observações que não violam critério:

4. Mutações extras que **sobrevivem**: `type_order` devolvendo sempre
   `list(TYPE_ORDER)` (ignora o YAML) e `rules = {}` fixo em `render_registry`
   dão 12 passed. Isso acontece porque hoje a ordem do YAML é igual à ordem
   embutida, e o RF06 garante que os dois conjuntos sejam iguais. Os mutantes
   são equivalentes no estado atual. Mas nenhum teste prova que, com o YAML
   acessível, a ordem vem dele e não da constante. O RF06 compara com
   `sorted(...)`, então reordenar as chaves do YAML derruba só o teste do
   RF01, porque a lista `ALL_TYPES` está fixa nele. Um teste com regras
   sintéticas em outra ordem (ex.: `type_order({"document_types": {"B": {},
   "A": {}}})`) fecharia isso. Não é exigido por A01 a A03.
5. Outras mutações extras **derrubadas**: fallback sem `or list(TYPE_ORDER)`
   dá 1 failed (`test_type_order_sem_yaml_usa_ordem_embutida`). `type_label`
   sem o `name` do YAML dá 1 failed (`test_rotulo_cai_no_name_do_yaml_sem_rotulo_curto`).
6. A função auxiliar `_declared_types(rules)` não é nomeada na SDD. Ela faz a
   união das duas chaves descrita em `type_order` e `type_label`, sem
   comportamento extra.
7. `render_prompts.py --check` emite o aviso pré-existente de 30 SDDs sem seção
   de arquivos, que não é desta mudança.

## Caminhos (escolha do owner)

- **Regenerar o gerado (recomendado).** Rodar `python3
  _framework/scripts/render_prompts.py` (ou `render_indexes.py`) no kit, que
  reescreve só `docs/sdd/INDEX.md`, e commitar. Depois, rodada 2 do A04 (e do
  A06, que não muda de lista). Opcionalmente, acrescentar
  `central:_framework/INDEX.md` à task 4.
- **Desfazer a edição da task 3.** Não serve: `_framework/INDEX.md` continuaria
  exigido por `render_prompts.py --check`, e o A04 e o A06 reprovariam do
  mesmo jeito.

## Lições

- Red flag: editar a "Decomposição em tasks" de uma SDD já gerada no índice
  sem rodar `render_prompts.py --check` de novo. A coluna "Arquivos de código"
  do `docs/sdd/INDEX.md` vem dessa tabela, então mudar o escopo da SDD é
  mudar um gerado.
- Red flag: um teste que compara a ordem embutida com o YAML por `sorted(...)`
  não discrimina "ordem derivada do YAML" de "ordem fixa no código" enquanto
  as duas coincidirem. Para provar a origem da ordem, use regras sintéticas
  numa ordem que a constante não tem.
