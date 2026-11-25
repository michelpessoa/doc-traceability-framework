# Verificação — SDD-DTF-0063

- **Veredito:** PASS
- **Diff verificado:** `7c86bb9..25d1951` no kit (`7c86bb9` = `git merge-base HEAD origin/main`, SHA fixo, igual a `origin/main` no momento da verificação; o intervalo contém a SDD e o status, o merge `c9185de`, a implementação em `e104c82`, `0d452cf`, `629c3d1`, `82174c4` e `25d1951`, e a emenda da task 1b em `a116740`, aprovada pelo owner por review na PR #155)
- **Rodada:** 1
- **Verificador independente:** sim (subagente separado; não implementou e não leu o relatório nem o histórico da sessão que implementou)

Todos os comandos rodaram nesta sessão. Sensores em cópias descartáveis feitas com `git archive` em subpastas de um diretório próprio do scratchpad (`verify-0063/`: `before` de `e104c82`, `a02`, `a03`, `sensor` de `25d1951`, `mainbase` de `7c86bb9`), sem `git stash` e sem commit na worktree. O `selftest.py` foi rodado no kit (ele muta e restaura no lugar) e numa cópia de `7c86bb9`; `git status --porcelain` do kit ficou vazio. O central foi só lido.

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0063.md /home/user/doc-traceability-central/docs/DTF` | `✅ source_docs ... conferem`, `exit=0`; `source_docs: []`, sizing `small`, RFs escritos na própria SDD | sem teste automatizado (leitura) | Sim |
| A01 | comando literal da SDD, em `25d1951` e em cópia de `e104c82` | `16 passed`; em `e104c82` (antes da task 2): `15 failed, 1 passed` | uma mutação por regra (RF01, `{2,}`, lookbehind, RF02, RF03, dedupe): todas mortas; restaurado `16 passed` | Sim |
| A02 | `in_review` → `obsolete` na cadeia do `SKILL.md`, em cópia; `check_renderings.py` | `cita o status inexistente 'obsolete'`, `exit=1` | script de `7c86bb9` na mesma cópia: `exit=0` (antes da SDD não detectava); `` `status: obsolete` ``: `exit=1` | Sim |
| A03 | `XYZ-EVM-0001` no `SKILL.md`, em cópia; `check_renderings.py` | `cita o tipo inexistente 'XYZ'`, `exit=1` | RF03 desligado: `3 failed` no pytest | Sim |
| A04 | `check_renderings.py` no kit | `✅ 5 renderização(ões) concordam`, `exit=0`; 17 cadeias, 1 `status:` e 8 ids conferidos, nenhum desconhecido | `{2,}` → `{1,}`: `test_rf04_kit_real_passa` falha | Sim |
| A05 | `selftest.py` no kit e em cópia de `7c86bb9` | `11 mutação(ões): todos os mutantes morreram.` `exit=0`; base: `10` | mutação nova só com o `test_file`: `3 failed` em testes de comportamento; mutação equivalente: `16 passed` | Sim |
| A06 | comando literal da SDD | `--check` `exit=0`; `cmp` sem saída; `542 passed`; ruff, format e mypy sem erro; `framework_check --auto` `exit=0`; diff com os 10 arquivos previstos | cópia da skill alterada: `cmp` acusa e `--check` `exit=1`; entrada da 1b removida: `arquivo sem entrada em kit-index.yaml`, `exit=1` | Sim |
| A07 | `cmp` dos seis arquivos da task 5, central (`8798155`) contra o kit | os seis diferem ou faltam (o teste não existe no central) | sem teste automatizado nesta etapa (espelho pós-merge) | Pendente: etapa pós-merge no kit |

## Descompassos encontrados

Requisito ↔ código: RF01 `check_renderings.py:161` (`STATUS_CHAIN`, igual à regex da SDD) e `:172-173` (texto sem `` ` ``/`*` e com `\s*\n\s*` trocado por espaço); RF02 `:162` (`STATUS_DECLARED` sobre o texto bruto); RF03 `:163` (`ID_PREFIX`, igual à regex do requisito); conjuntos `:211-214` (`status_lifecycle` ∪ `incident_lifecycle`; `document_types` ∪ `legacy_document_types`); mensagens e "uma vez por renderização" `:166-188`; chamada no laço `:261`; docstring do item 4 `:17-22`; RF04 `test_check_renderings_unknown.py:125-134`; RF05 o arquivo novo, com os três negativos pedidos (`:69`, `:88`, `:73`) e um para o RF03 (`:114`); RF06 `mutations.yaml:68-72`. Nenhum requisito sem código.

Arquivo tocado ↔ SDD: `git diff --name-only 7c86bb9..25d1951` dá os seis arquivos das tasks 1, 1b, 2, 3 e 4 (teste, `kit-index.yaml`, script, `mutations.yaml`, cópia da skill, `_framework/INDEX.md`) e, de `docs/sdd/`, a SDD, `INDEX.md`, `registry.md` e `registry.yaml`. As outras checagens de `check_renderings.py`, `workflow-rules.yaml`, as renderizações e `render_prompts.py` não mudaram. Não há código sem requisito.

**Ponto da regex do RF03 (julgado).** A regex dada pela SDD termina em `\b`. Depois de `}` não há fronteira de palavra quando o próximo caractere não é de palavra, então as alternativas `\{SEQ4?\}` quase nunca casam: `FOO-{PROJECT_CODE}-{SEQ4}`, `FOO-{PROJECT_CODE}-{SEQ}.` e `FOO-DTF-{SEQ4}` dão lista vazia em `check_unknown_names`, enquanto `FOO-{PROJECT_CODE}-X` e `FOO-DTF-0001` reprovam. O código seguiu a SDD ao pé da letra. Não viola RF nem critério: o RF03 fixa a regex, e o seu critério EARS (`XYZ-EVM-0001`) passa, assim como o A03. É achado não bloqueante de especificação: o RF03 promete conferir "todo prefixo de id no formato `{TIPO}-{PROJETO}-{SEQ}`", e a regex prescrita não cobre o formato com `{SEQ4}`, que é justamente o dos templates (`SKILL.md:93` usa `{TYPE}-{PROJECT_CODE}-{SEQ4}`). Um tipo inventado escrito assim passa. Trocar o `\b` final por `(?!\w)` resolve e foi conferido sem falso positivo nas cinco renderizações (mesmos 8 ids, nenhum desconhecido). Fica para uma SDD de correção, porque a mudança altera a regex aprovada.

Achados não bloqueantes:

1. **Regex do RF03 (acima).** Consequência nos testes: em `test_rf03_tipos_ativos_e_legados_passam` (`:109-111`), os casos `SPEC-{PROJECT_CODE}-{SEQ4}` e `TS-EVM-{SEQ}` não casam a regex, então não testam a aceitação de tipo conhecido; o teste só prova algo para `SDD-DTF-0063`, `ADR-EVM-N` e `PRD-EVM-0001`.
2. **A chamada em `main` não tem teste automatizado.** Trocar `problems += check_unknown_names(...)` (`:261`) por `pass` deixa a suíte inteira verde (`542 passed`, cópia com `git init`). A SDD desenha os testes assim (função direto e subprocesso só para o RF04, que um no-op também passa); o fio até `main` é provado só pelo A02 e pelo A03, rodados aqui. Um teste de subprocesso sobre uma cópia com renderização mutada fecharia isso.
3. **A união com `legacy_document_types` em `main` não é discriminada.** `known_types = set(types)` (`:214`) passa em todos os testes: o teste monta os seus próprios conjuntos, e nenhuma renderização atual cita id legado no formato casado. O RF03 está cumprido no código, mas sem teste que o segure.
4. **Troca de quebra de linha redundante.** `chained = text` no lugar de `re.sub(r"\s*\n\s*", " ", text)` dá `16 passed`: o `\s*` em volta de `→` já atravessa quebras de linha. É mutante equivalente, não lacuna de teste; o código segue a SDD.
5. **Redação do A06.** `registry.yaml` não é gerado, mas é o registro da própria SDD (mesmo ponto da SDD-DTF-0061); o A01 pedia "pelo menos 3 failed" antes da task 2 e deu 15.
6. **A07 ainda não aplicável.** O central (`8798155`) tem o kit anterior e não há branch de espelho. O critério deve ser rodado por quem espelhar, depois do merge no kit.

## Lições

- **Red flag: `\b` depois de placeholder com chave.** Uma regex que termina em `\b` não casa nada que termine em `}` seguido de espaço ou pontuação. Ao especificar regex com alternativas não alfanuméricas no fim, use `(?!\w)` e inclua no teste um caso positivo com cada alternativa.
- **Red flag: teste de caso válido que não casa a regex.** "Passa sem acusar" é verdadeiro tanto para um id conhecido conferido quanto para um id que a regex nem viu. Confira, no sensor, que o caso válido é realmente extraído (por exemplo, tirando o tipo do conjunto e vendo o teste falhar).
- **Red flag: função testada, fio não.** Testar só a função nova e o "kit real passa" deixa passar a remoção da chamada em `main`. Mutar a chamada é um sensor barato; rode-o sempre que a SDD pedir uma função nova chamada de um laço existente.
