# Verificação — SDD-DTF-0061

- **Veredito:** PASS
- **Diff verificado:** `7c86bb9..665e66f` no kit (`7c86bb9` = `git merge-base HEAD origin/main`, SHA fixo, igual a `origin/main` no momento da verificação; o intervalo contém `bb2ed62`/`0b5eca0` (SDD e status), o merge `731c4c6` e a implementação em `2f4c2b9`, `bad91fa`, `e395dad` e `665e66f`)
- **Rodada:** 1
- **Verificador independente:** sim (subagente separado; não implementou e não leu o relatório nem o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão. Sensores em cópias descartáveis feitas com `git archive` em subpastas de um diretório próprio do scratchpad (`verify-0061/`: `2f4c2b9`, `base` de `731c4c6`, `mainbase` de `7c86bb9`, `head`, `a02`, `a03`, `a04`, `root-helper`), sem `git stash` e sem commit. O `selftest.py` foi rodado no kit (ele muta e restaura no lugar) e numa cópia; `git status --porcelain` do kit ficou vazio. O central foi só lido.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0061.md /home/user/doc-traceability-central/docs/DTF` | `✅ source_docs ... conferem`, `exit=0`; `source_docs: []`, sizing `small`, RFs escritos na própria SDD | sem teste automatizado (leitura) | Sim |
| A01 | comando literal da SDD, em `665e66f` e em cópia de `2f4c2b9` | `12 passed`; em `2f4c2b9` (antes da task 2): `4 failed, 8 passed` | ver A02 | Sim |
| A02 | laço de `BUNDLED_PROMPTS` removido em cópia; pytest do A01 | `4 failed`; restaurado `12 passed` | órfão sem `ok = False`: `2 failed`; órfão apagado: `2 failed`; `check` forçado a `False` nos prompts: `2 failed` | Sim |
| A03 | linha a mais na cópia `framework-audit.md` da skill; `render_prompts.py --check` | `divergente de`, `exit=1` | mesma mutação sobre `731c4c6`: `exit=0` (antes da SDD não detectava); órfão `extra.md`: `exit=1` nos dois modos e arquivo preservado; canônico alterado sem `--check`: cópia idêntica | Sim |
| A04 | `grep -c "BUNDLED_PROMPTS"`; leitura de `sync_copies.__doc__` | `6`; `True` | docstring sem o nome: `grep -c` dá `4` (não discrimina); leitura da docstring dá `False` | Sim |
| A05 | `selftest.py` no kit e em cópia de `7c86bb9` | `11 mutação(ões): todos os mutantes morreram.` `exit=0`; base: `10` | só a mutação nova: morre; mutação equivalente também morre (ver descompasso 2) | Sim |
| A06 | comando literal da SDD | `--check` `exit=0`; `cmp` sem saída; `531 passed`; ruff, format e mypy sem erro; `framework_check --auto` `exit=0`; diff com 8 arquivos previstos | INDEX com tamanho trocado: `divergente do gerado`, `exit=1`; cópia da skill alterada: `cmp` acusa e `--check` dá `exit=1` | Sim |
| A07 | `cmp` dos cinco arquivos da task 5, central (`8798155`) contra o kit e contra `7c86bb9` | contra o kit: quatro diferem, INDEX igual; contra `7c86bb9`: os cinco iguais | sem teste automatizado nesta etapa (espelho pós-merge) | Pendente: etapa pós-merge no kit |

## Descompassos encontrados

Requisito ↔ código: RF01 `render_prompts.py:61` (constante) e `:765-766` (sincronização por `_sync_file`, depois do laço dos templates); RF02 a mensagem de `_sync_file` (`divergente de`) e `main` devolvendo 1; RF03 `:767-772` (só `*.md` direto, não recursivo, nunca apaga); RF04 `:742-749`; RF05 `test_render_prompts_sync.py:101-149` (gera, atualiza, divergente e ausente em `--check`, órfão nos dois modos com o arquivo preservado, kit real); RF06 `mutations.yaml:68-72`. Nenhum requisito sem código.

Arquivo tocado ↔ SDD: `git diff --name-only 7c86bb9..665e66f` dá os quatro arquivos das tasks 1 a 4 e, de `docs/sdd/`, a SDD, `INDEX.md`, `registry.md` e `registry.yaml`. Não há código sem requisito.

Os três pontos levantados por quem despachou:

1. **`_framework/INDEX.md` sem mudança (task 4).** Correto, não é lacuna. O INDEX registra caminho, descrição (de `kit-index.yaml`, que não muda) e faixa de tamanho. Nenhum arquivo mudou de faixa: `render_prompts.py` e a cópia seguem `>32 KB` (65917 → 66709 bytes), o teste `2-8 KB` (3340 → 5780) e `mutations.yaml` `2-8 KB` (3623 → 3953). `render_prompts.py --check` diz `_framework/INDEX.md: em dia`, e um INDEX com a faixa trocada reprova, então o gerador confere o arquivo. A task 4 lista o INDEX porque ele é regenerado pelo script, e a regeneração resultou igual.
2. **`docs/sdd/registry.yaml` no diff.** Cabe no A06. O diff do arquivo é só a entrada da SDD-DTF-0061 (`bb2ed62`, `in_review`, e `0b5eca0`, `approved`), sem tocar outras entradas. A entrada é parte inseparável de "esta SDD": sem ela `framework_check.py` reprova a SDD. O texto do A06 diz "os gerados de `docs/sdd/`", e o `registry.yaml` não é gerado, mas é o registro da própria SDD. É uma imprecisão de redação, sem efeito no veredito.
3. **Helper `_root` dos testes.** É escopo legítimo do RF05. A Especificação manda seguir "o padrão dos testes de template existentes (`tmp_path` com a árvore mínima)". Como `sync_copies` passa a ler `prompts/{nome}`, a árvore mínima precisa da pasta. Sem ela, todos os testes de `sync_copies` caem com `FileNotFoundError` (conferido numa cópia com o helper antigo). O `universal.md` acrescentado serve ao teste que confirma que prompt fora de `BUNDLED_PROMPTS` não vai para a skill, o que o "Fora de escopo" pede.

Achados não bloqueantes:

1. **Critério fraco (A04).** O `grep -c ≥ 3` não discrimina a docstring: sem ela, a contagem é 4 (constante, laço, condição e mensagem do órfão). O RF04 foi confirmado lendo `sync_copies.__doc__`.
2. **Mutação do selftest não discrimina por comportamento sozinha (A05/RF06).** `test_sync_copies_kit_real_em_dia` compara o script com a sua cópia na skill. Qualquer mudança textual em `render_prompts.py`, até uma equivalente, mata a mutação. O RF06 pede só que ela morra, e no A02 a mesma mutação derruba também três testes de comportamento, então o requisito está cumprido. Mas o `selftest.py`, sozinho, não prova mais que esta suíte discrimina mutações de `render_prompts.py`.
3. **Canônico ausente.** Se `prompts/{nome}` não existir, `_sync_file` levanta `FileNotFoundError` em vez de reprovar com mensagem. É o mesmo comportamento já existente para scripts e templates. A SDD não pede nada aqui.
4. **A07 ainda não aplicável.** O central (`8798155`) tem os cinco arquivos iguais aos de `7c86bb9`, e não existe branch de espelho. O critério deve ser rodado por quem espelhar, depois do merge no kit.

## Lições

- **Red flag: teste do "kit real em dia" na mesma suíte usada pelo selftest.** Um teste que compara o arquivo mutado com a sua cópia gerada mata qualquer mutação daquele arquivo, inclusive uma equivalente. Ao declarar uma mutação em `mutations.yaml`, rode também uma mutação equivalente. Se ela morrer, prove a morte por comportamento rodando à parte os testes que não comparam com a cópia.
- **Red flag: `grep -c ≥ N` para provar uma menção específica.** Se o termo aparece em outros lugares, o número pode continuar acima do limite sem a menção pedida. Ancore a busca no trecho (`ast.get_docstring`, `awk` por seção).
- **Red flag: pyc velho no sensor.** Uma mutação do mesmo tamanho, restaurada no mesmo segundo, reaproveita o `__pycache__` da versão mutada e dá um falso vermelho depois da restauração. Rode os sensores com `PYTHONDONTWRITEBYTECODE=1` ou apague o `__pycache__`.
