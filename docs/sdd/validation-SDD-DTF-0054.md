# Verificação — SDD-DTF-0054

- **Veredito:** PASS
- **Diff verificado:** `d3749e2..d238b61` no kit (branch `sdd/SDD-DTF-0054-aprovacao-como-dado`); espelho no central em `abac56e` (branch `sdd/SDD-DTF-0054-espelho`)
- **Rodada:** 1
- **Verificador independente:** sim (sessão diferente da que implementou; histórico dela não lido)

## Rodada 1

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0054.md <central>/docs/DTF`; leitura da SPEC-DTF-0029 e da ADR-DTF-0008 (itens 3 e 4) | `exit=0`; RF01 a RF10, os 10 casos de borda e os requisitos não funcionais iguais aos da SPEC; EARS sem relaxamento; contratos da Parte 2 descritos da mesma forma | sem teste automatizado (leitura) | Sim |
| A01 (RF04) | `pytest _framework/scripts/tests/test_approval_hash.py -q`, ANTES em cópia de `d3749e2` com o teste | ANTES `ModuleNotFoundError: No module named 'approval_hash'`; DEPOIS `12 passed` | ver A05; leitura em bytes sem normalizar CRLF: `1 failed`; restaurado `12 passed` | Sim |
| A02 (RF01-RF03, RF05-RF08) | `pytest _framework/scripts/tests/test_approval.py -q`, ANTES em cópia de `d3749e2` com `approval_hash.py` e o teste | ANTES `ImportError: cannot import name 'check_approval'`; DEPOIS `31 passed` | ver A03 e A04; cobrança desligada `4 failed`; `evidence` não cobrada `1 failed`; restaurado `31 passed` | Sim |
| A03 (RF07) | comparação de `content_sha256` desligada (`if False and ...`) em `validate_state.py`; pytest de A02 | `2 failed, 29 passed`; restaurado `31 passed` | derrubada | Sim |
| A04 (RF06) | regra de SPEC com `approver: policy` no YAML; pytest de A02 | `3 failed, 28 passed`; restaurado `31 passed` | derrubada | Sim |
| A05 (RF04) | `hash_excluded_sections: []` no YAML; pytest de A01 | `2 failed, 10 passed`; restaurado `12 passed` | derrubada | Sim |
| A06 (RF09) | `pytest _framework/tests/test_executor_contract.py -q`, ANTES em cópia de `d3749e2` com o teste e o esquema | ANTES `3 failed, 8 passed` (`KeyError`); DEPOIS `11 passed` | `approval_policy` fora de `reads`: `1 failed`; restaurado `11 passed` | Sim |
| A07 (não funcional) | `pytest _framework/scripts/tests/test_report_json.py -q`; `git diff --stat origin/main -- _framework/scripts/tests/fixtures/` e contra `d3749e2` | `26 passed`; os dois diffs vazios | fixture do 2.3.2 compara stdout e exit | Sim |
| A08 (RF10) | `grep -n 'version: "2.5.0"'`; no central `framework_check.py --auto; echo exit=$?`; `git status --porcelain docs/` | linhas 17 e 20; `134 documento(s) ok` nas duas verificações, `exit=0`; porcelain vazio | sem teste automatizado (medição) | Sim |
| A09 | `render_prompts.py --check; echo exit=$?` | tudo em dia, `exit=0` | sem teste automatizado (medição) | Sim |
| A10 | `pytest -q`; `ruff format --check` e `ruff check` nos 10 `.py` do diff; `selftest.py` | `384 passed`; `10 files already formatted`; `All checks passed!`; `7 mutação(ões): todos os mutantes morreram` | suíte inteira | Sim |
| A11 | no central `diff -r -x __pycache__ -x .pytest_cache <kit>/_framework _framework` | `diff exit=0` | sem teste automatizado (medição) | Sim |

Todos os sensores rodaram na worktree com cópia guardada no scratchpad e
foram restaurados por ela; `git status --porcelain` vazio depois de cada um.
Os "antes" rodaram em cópia descartável de `d3749e2` extraída com `git
archive`, sem tocar no repositório.

Checagem do passo 5 em cópia descartável (SDD com `status: implemented` ao
lado do `registry.yaml` do kit): `validate_state.py` sai com 0. O status
real não foi mudado.

## Descompassos encontrados

Nenhum.

Escopo nas duas direções: os 26 arquivos de `git diff --stat d3749e2..HEAD`
aparecem na decomposição em tasks, são gerados por `render_prompts.py`
(cópias da skill, `references/workflow-rules.yaml`, `AGENTS.md`,
`CHANGELOG.md`, `QUICKSTART.md`, `docs/especificacao.md`, prompts, mapa,
índices) ou são a própria SDD e o registry de SDD. Todo RF01 a RF10 tem
código e teste. `executor_contract` mantém exatamente `contract_version`
(1), `description`, `reads`, `machine_outputs` e `writes`. Nenhuma mensagem
existente dos validadores mudou; o diff de `validate_state.py` e
`framework_check.py` só acrescenta.

Observações que não violam critério:

- A SDD acrescenta à SPEC que documento sem `created` não é cobrado. A
  justificativa está na própria SDD e vem do requisito não funcional da
  SPEC (fixture do 2.3.2); `created` já é obrigatório no `validate_doc.py`,
  então o caso só ocorre em documento que já reprova lá. Coberto por
  `test_approval.py:255`. Aceito como resolução de tensão interna da SPEC,
  não como relaxamento.
- O `.replace("\r\n", "\n")` de `approval_hash.split_document` é redundante:
  `Path.read_text` já abre em modo de quebra de linha universal. Tirar o
  `replace` é mutante equivalente e sobrevive; ler em bytes sem normalizar
  derruba `test_hash_estavel_com_crlf`, então o teste discrimina.
- O comando de A07 usa `origin/main`, ref móvel. Nesta sessão
  `origin/main` = `d3749e2`, e o mesmo diff contra a base fixa também é
  vazio. Depois do merge, use `d3749e2`.
- Linha `## ` dentro de bloco de código conta como título de seção para o
  hash. A SPEC não trata o caso; não afeta nenhum critério.
- No `--json` de `approval_hash.py`, documento sem `id` no front-matter sai
  com o nome do arquivo em `documento`. A SPEC só diz `<id>`; o esquema
  continua válido.
- A própria SDD-DTF-0054 está `approved` sem `approved_by`: o kit declara
  `framework_version: "2.3.1"`, então pelo RF08 não é cobrada.
- O espelho no central ainda precisa da própria PR.

## Lições

- Red flag: mutação que sobrevive pode ser mutante equivalente, não teste
  fraco. Antes de registrar "sensor sobreviveu", confira se o código
  mutado era redundante (aqui, `read_text` já normaliza CRLF) e quebre o
  comportamento de outro jeito.
- Red flag: critério de aceite com `git diff origin/main`. Vale enquanto a
  branch não foi mergeada; registre a base fixa ao lado.
