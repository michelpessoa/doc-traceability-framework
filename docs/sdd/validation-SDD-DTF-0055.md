# Verificação — SDD-DTF-0055

- **Veredito:** PASS
- **Diff verificado:** `012ff47..96969e6` no kit (branch `sdd/SDD-DTF-0055-review-approval`); espelho no central em `0f4f842` (branch `sdd/SDD-DTF-0055-espelho`, sobre `main` `5c5cee5`)
- **Rodada:** 1
- **Verificador independente:** sim (sessão diferente da que implementou; histórico dela não lido)

## Rodada 1

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0055.md <central>/docs/DTF`; leitura da SPEC-DTF-0030 (approved) do `main` do central | `exit=0`; RF01 a RF07 com texto e EARS idênticos aos da SPEC; os 12 casos de borda do kit iguais (o de `approvers` ausente sem a parte da fábrica); requisitos não funcionais iguais; contratos da Parte 2 (`approvers`, `decide`, `approvers_for`, CLI, JSON, esquema, mensagem do `check_approval`, `executor_contract`) descritos da mesma forma, só detalhados; RF08 a RF13 declaradamente fora | sem teste automatizado (leitura) | Sim |
| A01 (RF03-RF05) | `pytest test_review_approval.py -q -k "not approvers"`, ANTES em cópia de `012ff47` com os testes novos | ANTES `ImportError: cannot import name 'check_approvers'`, 1 error na coleta; DEPOIS `33 passed, 10 deselected` | ver A04 a A06 | Sim |
| A02 (RF01) | `pytest test_review_approval.py -q -k approvers`, ANTES na mesma cópia | ANTES o mesmo `ImportError`; DEPOIS `10 passed, 33 deselected` | `check_approvers` sempre `[]` (`if True:`): `8 failed, 2 passed`; restaurado `10 passed` | Sim |
| A03 (RF02) | `pytest test_approval.py -q`, ANTES na mesma cópia | ANTES `1 failed, 34 passed` (`test_actor_fora_da_lista_reprova_com_a_mensagem`); DEPOIS `35 passed` | ver A07 | Sim |
| A04 (RF04) | passo 5 de `decide` removido; pytest de A01 | `2 failed, 31 passed`; restaurado `33 passed` | derrubada | Sim |
| A05 (RF04) | `== "Aprovado"` trocado por `.lower().startswith("aprovado")`; pytest de A01 | `3 failed, 30 passed`; restaurado `33 passed` | derrubada | Sim |
| A06 (RF04) | `CHANGES_REQUESTED` tirado do filtro de `decide`; pytest de A01 | `1 failed, 32 passed`; restaurado `33 passed` | derrubada | Sim |
| A07 (RF02) | bloco do `actor` tirado de `check_approval`; pytest de A03 | `1 failed, 34 passed`; restaurado `35 passed` | derrubada | Sim |
| A08 (RF06) | `pytest _framework/tests/test_executor_contract.py -q`, ANTES na mesma cópia | ANTES `3 failed, 10 passed` (`KeyError`); DEPOIS `13 passed` | segunda linha nova de `writes` removida do YAML: `1 failed, 12 passed`; restaurado `13 passed` | Sim |
| A09 (não funcional) | `pytest test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` e contra `012ff47` | `26 passed`; os dois diffs vazios (`origin/main` = `012ff47` nesta sessão) | fixture do 2.3.2 compara stdout e exit | Sim |
| A10 (RF07) | `grep -n 'version: "2.6.0"'`; no central `framework_check.py --auto; echo exit=$?`; `git status --porcelain docs/` | linhas 17 e 20; `134 documento(s) ok` nas duas verificações, `exit=0`; porcelain vazio | sem teste automatizado (medição) | Sim |
| A11 | `render_prompts.py --check; echo exit=$?` | tudo `em dia`/`sincronizado`, incluindo `review_approval.py` da skill; `exit=0` | sem teste automatizado (medição) | Sim |
| A12 | `pytest -q`; `ruff format --check` e `ruff check` nos 9 `.py` do diff; `selftest.py` | `433 passed`; `9 files already formatted`; `All checks passed!`; `7 mutação(ões): todos os mutantes morreram` | suíte inteira | Sim |
| A13 | no central `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | `diff exit=0` | sem teste automatizado (medição) | Sim |

Todos os sensores mutaram o arquivo da worktree com cópia guardada no
scratchpad e foram restaurados por ela; `git status --porcelain` vazio
depois de cada um. Os "antes" rodaram em cópia descartável de `012ff47`
extraída com `git archive`, com `test_review_approval.py`, `test_approval.py`
e `test_executor_contract.py` copiados por cima, sem tocar no repositório.

## Descompassos encontrados

Nenhum.

Escopo nas duas direções: os 26 arquivos de `git diff --stat 012ff47..HEAD`
aparecem na decomposição em tasks, são gerados por `render_prompts.py`
(cópias da skill, `references/workflow-rules.yaml`, `AGENTS.md`,
`CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, prompts, mapa,
índices) ou são a própria SDD e o registry de SDD. RF01 (`approvers_field`
no YAML, `check_approvers` em `cmd_validate` só no modo central, logo depois
de `check_repository_state`), RF02 (`check_approval`, entre a política e o
hash), RF03 a RF05 (`review_approval.py` e o esquema), RF06 (as duas
entradas do `executor_contract`), RF07 (2.6.0 e changelog) têm código e
teste. `executor_contract` mantém exatamente `contract_version` (1),
`description`, `reads`, `machine_outputs` e `writes`; `approvers_field` tem
exatamente `field`, `level`, `description` e `since`. Nenhum `approvers`
declarado em registry do kit nem do central; nenhum executor citado no kit;
nenhuma mensagem existente dos validadores mudou.

Observações que não violam critério:

- A SPEC diz que `approvers_for` lê o `registry.yaml` de `docs/{PROJECT_CODE}/`;
  a SDD e o código sobem a árvore até o primeiro `registry.yaml`, como
  `project_version`. Para documento do central dá o mesmo arquivo. Aceito
  como detalhamento.
- O texto das saídas 2 que a SDD não fixa sai assim: `Não encontrado: <path>`,
  `<path>: documento sem front-matter`, `arquivo de reviews ilegível: <erro>`,
  `arquivo de reviews não é lista JSON` e `review <i> não é objeto` (item da
  lista que não é objeto). A SDD pede "saída 2 com o motivo" para esses casos
  sem fixar a frase; o último é a forma de "item sem campo" quando o item nem
  é objeto. Não são chaves nem campos novos. Só o caso "item sem campo" tem
  texto conferido por teste (`test_review_approval.py:224`).
- O espelho do central também regenera `docs/DTF/registry.md` (cabeçalho
  `Framework v2.6.0`). É vista gerada, não documento; `framework_check.py
  --auto` não mexe em `docs/` (porcelain vazio).
- O comando de A09 usa `origin/main`, ref móvel. Nesta sessão
  `origin/main` = `012ff47`, e o diff contra a base fixa também é vazio.
  Depois do merge, use `012ff47`.
- O espelho no central ainda precisa da própria PR.

## Lições

- Red flag: critério com sensor que só tira um passo da função pode passar
  por um único teste. Aqui A06 derrubou só
  `test_aprovacao_seguida_de_changes_requested_e_invalida`; está certo, mas
  um sensor com `1 failed` é o limite: se esse teste sumir, nada mais cobre.
- Red flag: SDD que declara "nomeando o campo" sem fixar a frase de todos os
  casos de saída 2 deixa a implementação escolher o texto. Quando a frase
  importa para quem consome a saída, fixe-a na SDD.
