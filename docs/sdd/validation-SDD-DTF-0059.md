# Verificação — SDD-DTF-0059

- **Veredito:** PASS
- **Diff verificado:** `6233635..94bcec1` no kit (`6233635` é `git merge-base HEAD origin/main`; `94bcec1` é o commit de implementação, e `3b373c3` e `3ec3342` só trazem a SDD e o status); espelho no central em `espelho/SDD-DTF-0059-0060` `e824ebb`, só leitura
- **Rodadas:** 1
- **Verificador independente:** sim (sessão diferente da que implementou; o histórico dela não foi lido)

## Rodada 1

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
| Fidelidade à origem | `check_source_docs.py docs/sdd/SDD-DTF-0059.md <central>/docs/DTF` | `exit=0`; `source_docs: []`, `sizing: small`, sem SPEC/ADR de origem; itens 2 a 4 do passo 0 não se aplicam | sem teste automatizado (leitura) | Sim |
| A01 | laço `grep -q` de cada `*.py`/`*.sh` de `_framework/scripts/`; `grep -c "docs/sdd/arquivo/"` | nenhum `falta`; `2` (21 scripts, não 22) | mutação: `falta review_approval.py` e `0`; guia da base: 7 `falta` | Sim |
| A02 | `grep -c '"1.7.0"'`; `grep -cE "repository_status\|none_yet\|approvers"` | `0`; `9` | mutação: `1` e `0`. Fraco: sem `approvers` e `none_yet` ainda `4` | Sim |
| A03 | `grep -c "optional_sections"` | `1` | mutação: `0` | Sim |
| A04 | `grep -cE "enxuta\|molde\|coluna \`Projeto\`"` | `6` | mutação dos três: `1`. Fraco: sem `molde` e sem a coluna ainda `3` | Sim |
| A05 | título `## 7.1` e laço dos seis termos | `313:`; nenhum `falta` | mutação: sem título e `falta transitions` | Sim |
| A06 | título `## 7.2` e laço dos quatro termos | `380:`; nenhum `falta` | mutação: sem título e `falta contract_version` | Sim |
| A07 | `grep -cE "render_indexes.py\|check_hooks.py"`; `grep -c "content_sha256"` | `6`; `3` | mutação: `0` e `0`. Fraco: sem `check_hooks.py` ainda `3` | Sim |
| A08 | `grep -cE` dos dois títulos; `grep -c "greenfield"` no guia não técnico | `2`; `1` | mutação: `1` e `0`; guia da base: `0` e `0` | Sim |
| A09 | leitura do diff dos guias contra as chaves de `workflow-rules.yaml` e contra `review_approval.py`, `approval_hash.py`, `render_indexes.py`, `check_hooks.py`, `validate_state.py`, `validate_doc.py` | nenhuma contradição, nenhuma afirmação sem fonte; quatro imprecisões não bloqueantes (abaixo) | sem teste automatizado (leitura) | Sim |
| A10 | `render_prompts.py --check`; `check_renderings.py` | `exit=0` e `exit=0` | sumário da 7.1 com `999 bytes`: `❌ ... divergente do gerado`, `exit=1`; restaurado, `exit=0` | Sim |
| A11 | `pytest _framework/scripts/tests/ _framework/tests/ -q`; `framework_check.py --auto`; `git diff --name-only origin/main` | `526 passed`; `exit=0`; dois guias, SDD e os três gerados de `docs/sdd/` | filtro de escopo: nenhum fora; `_framework/` e outros guias: 0 arquivos | Sim |
| A12 | no central: `cmp` dos dois guias e de `_framework/INDEX.md`; `framework_check.py --auto` | guias idênticos; INDEX difere na linha 71 (`SKILL.md` `2-8 KB` → `8-32 KB`, da SDD-DTF-0060); `exit=0` | cópia mutada do guia do central: `cmp` acusa a linha 180 | Sim (ver descompasso 4) |

Checagens extras desta rodada:

- Cada termo dos critérios grep conferido na sua seção (laço `awk` por seção 2, 3, 4.1, 6, 9 e 15): nenhuma falta. A mesma checagem sobre o guia de `6233635` acusa a falta de `enxuta`, `molde` e da coluna `Projeto` na seção 6, o que mostra que ela discrimina.
- A ordem 7, 7.1, 7.2, 8 do guia técnico está certa (linhas 249, 313, 380, 415).
- Simulação do passo 5 numa cópia de `docs/sdd/` em `/tmp`, com `status: implemented` na SDD e no registry: `validate_state.py` dá `exit=0` (projeto sob 2.3.1, `approved_by` não é cobrado). Nada foi commitado com `implemented`.

## Descompassos encontrados

1. **"22 scripts" na SDD; o diretório tem 21.** `_framework/scripts/` tem 21 arquivos `*.py`/`*.sh` na base `6233635` e no head (`git ls-tree origin/main _framework/scripts/`). O "sete faltando" está certo: no guia da base faltavam `approval_hash.py`, `check_hooks.py`, `guard_bash.sh`, `hook_post_edit.py`, `hook_session_start.py`, `render_indexes.py` e `review_approval.py`. O A01 percorre os arquivos reais, então a contagem errada não afeta o critério, e o guia não repete o número. **Não bloqueia.** Erro de contagem no texto da SDD (Resumo e RF01), que pode ser corrigido na própria SDD.
2. **"Todos aceitam `--report-only`" virou "Os validadores aceitam".** Confirmado no código: `approval_hash.py` e `review_approval.py` não têm a opção (`grep "report.only"` sem resultado nos dois; `approval_hash.py` recusa qualquer argumento além do documento e de `--json`). A frase da base já era falsa antes desta SDD (`lessons_check.py`, `parallel_plan.py`, `render_prompts.py`, `selftest.py` e `ci_gate_verify_sdd.py` também não têm a opção), e o RF07 a deixaria ainda mais falsa. A troca é uma correção sem RF próprio, mas é necessária para o RF07 não deixar uma afirmação falsa na seção 9. Fica uma imprecisão: "validadores" não está definido, e `lessons_check.py` e `ci_gate_verify_sdd.py`, que validam, não aceitam a opção. **Não bloqueia.** Pode entrar na SDD como escopo registrado, e a frase pode listar os scripts pelo nome numa mudança futura.
3. **"O executor não faz merge na versão principal" (guia não técnico).** A fonte é o RF10 desta SDD ("não faz merge em `main`"), que o owner aprovou. No YAML não existe uma chave que proíba o merge por extenso. O que existe é a lista fechada de `executor_contract.writes`: o merge não está nela, e o item "Na mesma PR, antes do merge" pressupõe que outra pessoa faz o merge. A frase segue do RF e não contradiz o YAML. **Não bloqueia.** Se a regra precisar valer para máquina, o lugar dela é `executor_contract`, numa SDD própria.
4. **A12: `_framework/INDEX.md` do central difere do kit.** A diferença é uma linha (`skills/doc-traceability-framework/SKILL.md`, `2-8 KB` → `8-32 KB`) e vem da SDD-DTF-0060, porque o espelho no central junta as duas SDDs. O INDEX do central é byte a byte igual ao da branch `sdd/SDD-DTF-0060-skill-e-prompts`, e esta SDD não muda `_framework/INDEX.md` no kit. Os dois guias são idênticos. **Não bloqueia esta SDD.** O A12 foi escrito para um espelho só da 0059: depois que as duas branches do kit forem mergeadas, o `cmp` do INDEX volta a ficar limpo. O humano deve saber que o espelho cobre as duas SDDs.
5. **A09: quatro imprecisões, nenhuma contradição.** (a) A 7.2 resume `executor_contract.writes` e perde dois qualificadores: "(SPEC, RFC) no central" no item da PR de documento novo, e "Na mesma PR, antes do merge: status approved" no item de `kind: human`. A escrita com `kind: policy` num único commit aparece só na 7.1. (b) Na seção 2, `schemas/` é descrito como "esquema JSON de cada saída --json", mas a pasta também guarda `resultado-verificacao.schema.json`, que é do M4 e não de um `--json`. (c) "Os validadores", como no item 2. (d) A frase do merge, como no item 3. O desenho da SDD manda apontar a chave e não reescrevê-la, e a 7.2 aponta `executor_contract.writes`. **Não bloqueia.**
6. **Critérios A02, A04 e A07 discriminam pouco.** Eles contam ocorrências de vários termos ligados por OR e cobram um mínimo, então tirar um termo não derruba o critério: sem `molde` e sem a coluna `Projeto`, o A04 ainda dá `3`. Todos os critérios grep contam no arquivo inteiro, não na seção que o RF nomeia. A implementação está certa: cada termo foi conferido na sua seção por uma checagem extra, que discrimina contra a base. **Não bloqueia.** A fraqueza é do critério, não do código.

Arquivos tocados ↔ SDD: o diff `6233635..94bcec1` toca só os dois guias. Os commits anteriores tocam a SDD, `registry.yaml`, `registry.md` e `docs/sdd/INDEX.md`, os gerados que o A11 admite. Não há mudança em `_framework/`, nos outros guias, em `AGENTS.md`, `QUICKSTART.md` nem em `docs/especificacao.md`. Requisito ↔ texto: RF01 a RF11 têm trecho na seção que nomeiam.

## Lições

- **Número escrito à mão num documento sai do lugar.** "22 scripts" foi contado de memória ou com `__pycache__`/`tests` no meio. Red flag: contagem literal numa SDD sem o comando que a produz. Escreva o comando (`ls *.py *.sh | wc -l`) ou cite a lista.
- **grep com OR e limite mínimo parece critério e não discrimina.** `grep -cE "a|b|c"` ≥ 3 passa com um termo só repetido. Red flag: critério de presença de N termos sem um laço por termo. Use `for t in ...; do grep -q || echo falta; done`, como o A05 e o A06, e recorte pela seção quando o RF nomeia a seção.
- **Um espelho que junta duas SDDs quebra o `cmp` de cada uma.** Red flag: critério de espelho "idêntico" numa branch de central que leva mais de uma SDD. O critério deve comparar contra o estado consolidado do kit ou listar só os arquivos daquela SDD.
- **Corrigir uma frase falsa vizinha é escopo.** Mesmo quando é necessária, a troca de "Todos" por "Os validadores" não tinha RF. Red flag: frase alterada fora do texto que o RF pede. Registre na SDD antes do commit.
