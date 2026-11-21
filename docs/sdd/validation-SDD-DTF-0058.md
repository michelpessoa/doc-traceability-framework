# Verificação — SDD-DTF-0058

- **Veredito:** PASS
- **Diff verificado:** `233fc2a..1d9b16c` no kit (`233fc2a` é o primeiro pai do merge da PR #150, o `main` anterior à mudança; `1d9b16c` é o merge em `main`); espelho no central em `main` `6e76c95` (PR #213)
- **Rodadas:** 1
- **Verificador independente:** sim (sessão diferente da que implementou; o histórico dela não foi lido)

## Rodada 1

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0058.md <central>/docs/DTF`; leitura de RF01 a RF03, casos de borda, não funcionais e Parte 2 da SPEC-DTF-0032 | `exit=0`; RF01 a RF03 idênticos; RF04 a RF10 fora (FAB); contratos do kit iguais | sem teste automatizado (leitura) | Sim |
| A01 | `pytest _framework/tests/test_validate_doc.py -q -k projeto`, ANTES numa worktree de `233fc2a` com os testes novos | ANTES `5 failed, 4 passed`; DEPOIS `9 passed` | ver A03 | Sim |
| A02 | `pytest _framework/scripts/tests/test_check_source_docs.py -q -k projeto`, ANTES na mesma cópia | ANTES `1 error` na coleta; DEPOIS `9 passed` | ver A04 e A05 | Sim |
| A03 (RF01) | `PROJECT_CODE = re.compile(r".+")`; pytest de A01 | `1 failed, 8 passed`; restaurado `9 passed` | derrubada | Sim |
| A04 (RF02) | `projects = None` em `check_rf_fidelity`; pytest de A02 | `6 failed, 3 passed`; restaurado `9 passed` | derrubada | Sim |
| A05 (RF02) | mensagem `é do projeto` trocada por `pass`; pytest de A02 | `1 failed, 8 passed`; restaurado `9 passed` | derrubada | Sim |
| A06 | `pytest test_sdd_lean.py test_check_source_docs.py test_validate_doc.py -q` | `83 passed` | ver A04 | Sim |
| A07 | no central `validate_doc.py docs/DTF/03-spec/SPEC-DTF-0032.md; echo exit=$?` | `exit=0` | sem teste automatizado (medição) | Sim |
| A08 | `pytest test_report_json.py -q`; `git diff --stat 233fc2a..HEAD -- _framework/scripts/tests/fixtures/` | `26 passed`; diff vazio | fixture do 2.3.2 | Sim |
| A09 | greps da versão e do procedimento; no central `framework_check.py --auto`; `git status --porcelain docs/ \| grep -v registry.md` | linhas 17 e 20; linha 64 (só casa com a crase); `134 documento(s) ok`, `exit=0`; porcelain vazio | sem teste automatizado (medição) | Sim |
| A10 | `render_prompts.py --check`; `generate_registry_md.py docs/sdd --check`; `check_renderings.py` | `exit=0` nos três | sem teste automatizado (medição) | Sim |
| A11 | `pytest -q`; `ruff format --check` e `ruff check` nos 8 `.py` do diff; `selftest.py` | `526 passed`; formatados; `All checks passed!`; `10 mutação(ões): todos os mutantes morreram` | suíte inteira | Sim |
| A12 | no central `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | `exit=0` | sem teste automatizado (medição) | Sim |

Sensores rodaram com cópia guardada no scratchpad e restauração por ela; os
"antes" rodaram numa worktree descartável removida no fim. Nenhum stash,
nenhum commit de mutação; `git status --porcelain` vazio no kit e no
central ao final.

## Descompassos encontrados

Nenhum requisito sem código, nenhum arquivo fora da SDD e nenhum código sem
requisito. Os 27 arquivos do diff estão nas tasks 1 a 6 ou são gerados
(`render_prompts.py --check` e `check_renderings.py` confirmam AGENTS.md,
CHANGELOG.md, QUICKSTART.md, `docs/especificacao.md`, os prompts, o mapa, os
índices e as cópias da skill). Observações que não reprovam:

1. **Comando de A09 não casa o texto exigido.** `grep -n 'coluna Projeto'`
   sai `exit=1`, porque o procedimento escreve `` coluna `Projeto` `` (com
   crase), exatamente como a SDD manda. O conteúdo está na linha 64; o
   defeito é do comando do critério, não da implementação.
2. **A08 usa `origin/main`.** Depois do merge, `origin/main` já contém a
   mudança e o diff fica vazio por definição. Rodei contra a base fixa
   `233fc2a`; também vazio.
3. **Mensagem de célula vazia diverge dentro da SPEC-DTF-0032.** Casos de
   borda: `RF07 sem projeto na coluna Projeto`; Parte 2:
   `RF07: coluna Projeto vazia`. A SDD e o código seguem a Parte 2.
4. **O registry do kit declara `framework_version: "2.3.1"`.** Por isso o
   `check_source_docs.py` não roda a fidelidade de RFs nesta SDD (não é
   enxuta); os itens 2 a 4 do passo 0 foram feitos por leitura.
5. **Task 7, parte `fabrica-central-teste` em 2.8.0,** não foi conferida:
   o repositório não está nesta sessão e nenhum critério de aceite a cobre.

## Lições

- Critério com `grep` literal de texto em markdown: confira se o texto tem
  crase ou outra marcação antes de fixar o padrão no critério.
- Critério com `git diff origin/main` deixa de discriminar depois do merge;
  escreva o critério com a base fixa (`<merge-base>`), como o procedimento
  já exige.
