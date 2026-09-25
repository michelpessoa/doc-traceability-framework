---
id: SDD-DTF-0046
type: SDD
title: "Bundle da skill como artefato gerado: .gitattributes com linguist-generated e templates sincronizados por render_prompts.py"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0042, SDD-DTF-0043, SDD-DTF-0045]
source_docs:
  - id: "SPEC-DTF-0020"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0020.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Leia SPEC-DTF-0020 inteira antes de tocar em qualquer arquivo: esta SDD consolida Parte 1 e Parte 2, mas o texto completo de cada caso de borda e a evidência da decisão sobre `-diff` e `merge=` vivem só na SPEC. Escreva primeiro o teste de sync e veja RF04 a RF07 falharem (task 1); só então altere `render_prompts.py` (task 2). Não crie RFC-DTF-0009, não remova a duplicação do bundle, não mova o changelog do YAML. Não toque `.ignore`, `.gitignore`, `test_repo_hygiene.py`, o workflow de CI, `test_template_parity.py` nem `workflow-rules.yaml`. As tasks 1 a 5 são feitas no kit e no central em dois PRs; a ordem entre SPECs 0017, 0016 e 0020 já está satisfeita (SDD-DTF-0042 e SDD-DTF-0043 `implemented` em main). Implementar em sessão separada, em worktree próprio; verificação por sdd-verifier em outra sessão."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, bundle, gerado, sync, gitattributes]
---

# Bundle da skill como artefato gerado: .gitattributes com linguist-generated e templates sincronizados por render_prompts.py

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar.

## Resumo executivo

A pasta `_framework/skills/doc-traceability-framework/` (o bundle da
skill) contém cópias geradas de scripts, do YAML de regras e de templates,
mas nada diz ao Git que elas são geradas, e `sync_copies` em
`render_prompts.py` só cobre scripts e YAML, deixando os templates para
`cp` manual (a defasagem já aconteceu no `sdd.template.md`). Esta SDD
(Frente C da RFC-DTF-0008, SPEC-DTF-0020, sizing `medium`, sem RFC) cria
um `.gitattributes` com três padrões `linguist-generated=true` no kit e no
central, estende `sync_copies` para gerar `_framework/templates/*.md` no
bundle (com órfão reprovado sem apagar), passa `_sync_file` a comparar e
gravar por bytes e a rejeitar destino symlink, e adiciona dois arquivos de
teste. Nenhuma regra de comportamento do framework muda: o YAML, o
`CHANGELOG.md` e o conjunto de arquivos do bundle ficam iguais.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `medium`, nenhum critério de `decision_gates.rfc_to_adr`
se aplica (`parent_rfc: null`, `parent_adr: null` na SPEC-DTF-0020).
Decisões registradas na SPEC, com evidência (git 2.43.0):

- Não remover a duplicação do bundle: o `.skill` empacota a pasta e precisa
  ser autocontido; a duplicação já é gerada e checada por `sync_copies` e
  `--check`. A referência "RFC-DTF-0009" na RFC-DTF-0008 fica como histórico
  e não gera documento.
- Não migrar o changelog do YAML: `CHANGELOG.md` é gerado de
  `framework.changelog` e `rule_since` lê esse bloco.
- `-diff` rejeitado: `git diff --numstat` passaria a mostrar `- -` e
  esconderia a edição à mão que o `--check` quer expor.
- `merge=ours` e `merge=binary` rejeitados: sem driver em `.git/config`
  (não versionado) o Git ignora `merge=ours`; `merge=binary` deixa conflito
  sem solução legível. Conflito em cópia gerada se resolve regenerando.
- Templates legados (`prd.template.md`, `tech-spec.template.md`) entram no
  sync; `templates/ci/` fica fora (seleção `*.md` não recursiva).
- Órfão no bundle reprova nos dois modos e nunca é apagado pelo script.
- Sem bump de `framework.version`: o YAML não muda.
- O bundle não entra em `.ignore` (fronteira com a SPEC-DTF-0019).

## Requisitos consolidados

| RF-ID | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | `.gitattributes` na raiz do kit com exatamente três padrões `linguist-generated=true`, caminhos completos ancorados na raiz: `_framework/skills/doc-traceability-framework/scripts/*.py`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml` e `_framework/skills/doc-traceability-framework/templates/*.md`. Nenhum outro atributo. | O sistema deve resolver `linguist-generated: true` para todo arquivo gerado pelo `sync_copies` no bundle e `diff` e `merge` como `unspecified` para esses arquivos, segundo `git check-attr`. |
| RF02 | Arquivos escritos à mão no bundle (`SKILL.md`, `prompts/*.md`, `references/*.md` exceto o YAML) não são marcados. | O sistema não deve marcar como gerado nenhum arquivo do bundle que não seja saída do `sync_copies`: `git check-attr linguist-generated` retorna `unspecified` para `SKILL.md` e `prompts/framework-audit.md`. |
| RF03 | O central recebe o mesmo `.gitattributes`, byte a byte. | O sistema deve manter `.gitattributes` do central byte-idêntico ao do kit, segundo `cmp`. |
| RF04 | `sync_copies` sincroniza `_framework/templates/*.md` (não recursivo, incluindo `prd` e `tech-spec` legados) para `skills/doc-traceability-framework/templates/`; `--check` reprova template do bundle ausente ou divergente. | Quando `render_prompts.py` rodar sem `--check`, deixar cada `*.md` de `_framework/templates/` byte-idêntico ao gêmeo no bundle; com `--check`, sair com código 1 se algum gêmeo divergir ou faltar. |
| RF05 | `*.md` no bundle sem original (órfão) é reprovado nos dois modos e nunca apagado. | Se existir órfão em `<bundle>/templates/`, o sistema deve sair com código 1, com ou sem `--check`, nomear o órfão e manter o arquivo no disco. |
| RF06 | `_sync_file` compara e grava por bytes (hoje usa `read_text`/`write_text`, que normaliza fim de linha). | Se o bundle diferir do original só em CRLF, o sistema deve reprovar em `--check` (código 1); sem `--check`, gravar os bytes do original sem tradução de fim de linha. |
| RF07 | `_sync_file` reprova destino que seja symlink. | Se o destino de uma cópia for symlink, o sistema deve sair com código 1 com e sem `--check`, nomeando o caminho, sem seguir nem sobrescrever o link. |
| RF08 | `templates/ci/` fica fora do bundle. | O sistema não deve criar `templates/ci/` nem copiar `verify-sdd-gate.yml.example` para o bundle ao rodar `render_prompts.py`. |
| RF09 | `_framework/tests/test_template_parity.py` (SPEC-DTF-0017) permanece inalterado e independente: não importa `render_prompts.py`. | Quando um template do bundle for editado à mão, o sistema deve reprovar tanto `render_prompts.py --check` quanto `pytest _framework/tests/test_template_parity.py`, cada um por conta própria. |
| RF10 | Fronteira com a SPEC-DTF-0019: não criar nem editar `.ignore`, `.gitignore`, `test_repo_hygiene.py` nem o workflow de CI; o bundle não entra em `.ignore`. | O sistema não deve alterar esses quatro arquivos ao aplicar esta SDD. |
| RF11 | Testes de regressão sem rede: `test_gitattributes_generated.py` (RF01 a RF03) e `test_render_prompts_sync.py` (RF04 a RF08). | O sistema deve executar com sucesso os dois arquivos, com 3 e 7 testes respectivamente, e reprovar cada teste quando sua mutação correspondente for aplicada. |
| RF12 | A mudança não altera o YAML, o `CHANGELOG.md`, nenhum registry de conteúdo de framework nem o conjunto de arquivos do bundle. | O sistema deve manter `workflow-rules.yaml`, `CHANGELOG.md` e a lista de arquivos versionados do bundle iguais aos de `origin/main` no início da implementação, e `framework_check.py --auto` com o mesmo código de saída antes e depois. |
| RF13 | Toda alteração de RF01 a RF08 e RF11 é aplicada também na cópia `_framework/` do central (incluindo a cópia de `render_prompts.py` no bundle), e o `--check` do central passa. | Quando `cmp` comparar cada arquivo tocado no kit com o mesmo caminho no central, o sistema deve reportar arquivos idênticos, e `render_prompts.py --check` no central deve sair com 0. |

Casos de borda (herdados da SPEC-DTF-0020, sem relaxamento):

| Caso | RF | Comportamento esperado |
|---|---|---|
| Template só no bundle (órfão) | RF05 | Sai 1 nos dois modos, nomeia o órfão, não apaga; remoção é manual. `test_bundle_sem_template_orfao` da SPEC-DTF-0017 reprova em paralelo. |
| Template só no original | RF04 | Sem `--check` cria o gêmeo; com `--check` reprova com "divergente". |
| Template legado | RF04 | Entra na cópia como qualquer outro (projetos 1.x precisam deles). |
| `templates/ci/` no original | RF08 | Fora da seleção `*.md` não recursiva. |
| Bundle editado à mão (template, script ou YAML) | RF04, RF09 | `--check` sai 1 com "divergente de"; `git checkout -- <arquivo>` ou `render_prompts.py` restauram. |
| Cópia com CRLF em uma ponta só | RF06 | Bytes diferentes reprovam; com `autocrlf=true` as duas pontas mudam juntas e seguem iguais. |
| Checkout sem `.gitattributes` (tarball, `git archive`) | RF01, RF11 | Nada em runtime depende do atributo; o teste de `git check-attr` usa `pytest.skip` com motivo só fora de árvore de trabalho Git; os outros dois testes leem o arquivo como texto. |
| Destino é symlink | RF07 | Reprova nos dois modos, sem seguir o link (`Path.is_symlink()` antes de ler). |
| Original ausente ou ilegível | RF04 | O erro do Python propaga; nunca é tratado como "nada a copiar". |
| Diretório `<bundle>/templates/` inexistente | RF04 | Sem `--check`, `mkdir(parents=True)` o cria; com `--check`, reprova cada gêmeo ausente. |
| GitHub não colapsa o diff | RF01 | Limite conhecido, sem critério de aceite: só `git check-attr` é verificável localmente. |
| Bundle ganha arquivo à mão (SPEC-DTF-0018) | RF02 | Não é marcado: os padrões de RF01 nomeiam só `scripts/*.py`, o YAML e `templates/*.md`. |

Requisitos não funcionais: nenhuma dependência nova (stdlib, `pytest`,
`PyYAML`); determinismo (`sorted(...)`, sem mtime nem rede); idempotência
(`render_prompts.py` duas vezes seguidas deixa `git status --porcelain`
vazio na segunda); a mudança em `render_prompts.py` altera `_sync_file` e
`sync_copies` no lugar e acrescenta só `_bundle_orphans`.

Requisitos transversais (sweep) resolvidos na SPEC: autorização em RF07
(symlink para fora do bundle); concorrência em RF13 (disputa de
`render_prompts.py` com a SPEC-DTF-0016 e divergência kit e central);
idempotência em RF04; observabilidade em RF05 (saída `✅`/`❌` nomeando o
arquivo); validação de entrada em RF05 e RF07; falha de dependência
externa e limite de volume são `n/a` com motivo registrado na SPEC.

Fora de escopo: remover a duplicação do bundle e a antiga "RFC-DTF-0009";
migrar o changelog; `.ignore`, `.gitignore`, `test_repo_hygiene.py` e CI
(SPEC-DTF-0019); novos testes de paridade de template (SPEC-DTF-0017);
gerar `SKILL.md`, `prompts/*.md` ou `references/*.md` do bundle;
empacotar `templates/ci/` no `.skill`; colapsar diff de PRs já mergeados;
alterar `docs/guias/guia-tecnico.md`.

## Especificação técnica consolidada

**Consumes** (já existem em `_framework/scripts/render_prompts.py`):
`_sync_file(src: Path, dest: Path, check: bool) -> bool` (hoje com
`read_text`/`write_text`), `sync_copies(root: Path, check: bool) -> bool`
(hoje cobre `scripts/*.py` e o YAML), `main() -> int` que propaga o
retorno de `sync_copies`, e `git check-attr <attr>... -- <path>...`.

**Produces:**

- `_framework/scripts/render_prompts.py`:
  - `_sync_file(src, dest, check) -> bool` (assinatura inalterada): retorna
    `False` com `❌ {dest}: é symlink` se `dest.is_symlink()`; compara
    `src.read_bytes()` com `dest.read_bytes()`; grava com `write_bytes`.
    Mensagens `✅ ...: sincronizado.` e `❌ ...: divergente de ...`
    inalteradas.
  - `_bundle_orphans(src_dir: Path, dest_dir: Path) -> list[Path]`: `*.md`
    de `dest_dir` cujo `name` não existe em `src_dir`, ordenado; lista vazia
    se `dest_dir` não existir.
  - `sync_copies(root, check) -> bool`: depois do laço de scripts e do YAML,
    acrescenta `for src in sorted((root / "templates").glob("*.md"))` para
    `skills/doc-traceability-framework/templates/<nome>` e a checagem de
    órfãos, que imprime `❌ {path}: órfão (sem original em {root}/templates) — remova à mão.`
    e força `ok = False`. O docstring passa a citar templates.
- A cópia `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`
  é gerada por `python3 _framework/scripts/render_prompts.py`, nunca editada
  à mão.
- `.gitattributes` (raiz, kit e central), conteúdo exato:

  ```
  # Cópias do bundle da skill geradas por _framework/scripts/render_prompts.py
  _framework/skills/doc-traceability-framework/scripts/*.py linguist-generated=true
  _framework/skills/doc-traceability-framework/references/workflow-rules.yaml linguist-generated=true
  _framework/skills/doc-traceability-framework/templates/*.md linguist-generated=true
  ```

- `_framework/tests/test_gitattributes_generated.py`:
  `test_gitattributes_declara_copias_geradas() -> None` (as três linhas
  exatas, RF01), `test_gitattributes_sem_diff_nem_merge() -> None` (nenhum
  token `diff`, `-diff`, `merge` ou `merge=` em linha não comentada, RF01),
  `test_git_check_attr_gerados_e_manuais() -> None` (`git check-attr
  linguist-generated diff merge` em cada saída do `sync_copies` derivada de
  `_framework/scripts/*.py`, do YAML e de `_framework/templates/*.md`,
  esperando `true`, `unspecified`, `unspecified`; `unspecified` para
  `SKILL.md` e `prompts/*.md` do bundle; `pytest.skip` com motivo se não for
  árvore de trabalho Git; RF01, RF02).
- `_framework/scripts/tests/test_render_prompts_sync.py` (mesmo molde de
  `test_render_prompts_mechanization.py`: `sys.path` para `render_prompts`,
  `tmp_path` montando `root` com `scripts/`, `rules/`, `templates/` e
  `skills/doc-traceability-framework/`): `test_sync_copies_gera_templates_md`,
  `test_sync_copies_check_detecta_template_divergente_ou_ausente`,
  `test_sync_copies_ignora_subpasta_ci`,
  `test_sync_copies_reprova_template_orfao_nos_dois_modos`,
  `test_sync_file_compara_bytes_crlf`, `test_sync_file_rejeita_symlink`,
  `test_sync_copies_idempotente`.

Tratamento de erro por contrato:

| Caso | RF | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| Template do bundle divergente ou ausente | RF04, RF09 | `❌ <dest>: divergente de <src>.`, retorno `False`, `main` sai 1 | `_sync_file` |
| Órfão no bundle | RF05 | `❌ <path>: órfão ...`, retorno `False`, arquivo preservado, nos dois modos | `sync_copies` via `_bundle_orphans` |
| CRLF só numa ponta | RF06 | Bytes diferem; `--check` sai 1; sem `--check` regrava os bytes do original | `_sync_file` |
| Destino symlink | RF07 | `❌ <dest>: é symlink`, retorno `False`, sem ler nem gravar | `_sync_file` |
| `templates/ci/` no original | RF08 | Fora da seleção `*.md` não recursiva | `sync_copies` |
| `.gitattributes` sem uma das três linhas | RF01 | Teste falha nomeando a linha ausente | `test_gitattributes_declara_copias_geradas` |
| `-diff` ou `merge=` introduzido | RF01 | Teste falha nomeando o token | `test_gitattributes_sem_diff_nem_merge` |
| Arquivo manual do bundle marcado como gerado | RF02 | Teste falha nomeando o arquivo | `test_git_check_attr_gerados_e_manuais` |
| Fora de árvore Git | RF01 | `pytest.skip("não é árvore de trabalho Git")`; os outros dois testes seguem | `test_git_check_attr_gerados_e_manuais` |
| Kit e central divergem | RF13 | `cmp` sai diferente de 0 no critério 15; corrigir espelhando | critério 15 |

Estratégia de teste:

| RF-ID / contrato | Tipo | Mock? | Arquivo de teste |
|---|---|---|---|
| RF01, RF02 | Unitário de texto e `git check-attr` real, mais critérios 1 a 3 | Não | `_framework/tests/test_gitattributes_generated.py` |
| RF03, RF13 | Comando `cmp` entre repositórios (critérios 4 e 15) | Não | (comando de aceite) |
| RF04 a RF08 | Unitário com `tmp_path`, mais critérios 6 e 8 a 11 | Não | `_framework/scripts/tests/test_render_prompts_sync.py` |
| RF09 | Sensor de mutação sobre os dois mecanismos (critério 7) | Não | `_framework/tests/test_template_parity.py` (existente, inalterado) |
| RF10, RF12 | Comandos dos critérios 12 e 14 | Não | (comando de aceite) |
| RF11 | Critérios 5 e 13 | Não | os dois arquivos de teste novos |

Plano de implementação (da SPEC): (1) branch do kit nomeada pelo id da SDD;
teste de sync primeiro, ver RF04 a RF07 falharem; (2) editar
`render_prompts.py`; (3) rodar `render_prompts.py` para regenerar a cópia do
bundle e conferir que `git status` lista só `render_prompts.py` (duas
cópias) e os arquivos novos; (4) `.gitattributes` e seu teste; (5) rodar
critérios 1 a 14 no kit e registrar a saída; (6) espelhar no central e rodar
o critério 15; (7) PR para `main` e verificação independente.

Riscos: `_sync_file` em bytes reprovar checkout Windows com `autocrlf`
misto (mitigado: as duas pontas passam pela mesma conversão e o teste da
0017 já é por bytes); `git checkout --` dos sensores apagar edição não
commitada (rodar sensores só depois do commit da implementação);
generalizar o padrão e marcar `references/*.md` como gerado (RF02 e
`test_git_check_attr_gerados_e_manuais`); conflito textual em
`render_prompts.py` com a SPEC-DTF-0016 (já mergeada, SDD-DTF-0043
`implemented`, então basta partir de `origin/main` atual).

Rollout direto, sem feature flag, um PR no kit e um no central. Rollback:
reverter o commit; `.gitattributes` e testes são aditivos e `_sync_file`
volta a comparar texto. Observabilidade: nenhuma nova (saída `✅`/`❌` e
pytest). Nenhum time externo nem projeto mapeado é afetado.

Ordem entre SPECs: SPEC-DTF-0017 (SDD-DTF-0042, `implemented`) e
SPEC-DTF-0016 (SDD-DTF-0043, `implemented`) antes da SPEC-DTF-0020
(esta SDD); ambas estão em `main`, então a ordem 0042, 0043, 0046 está
satisfeita. SPEC-DTF-0018 e SPEC-DTF-0019 são independentes.

## Decomposição em tasks

Arquivos do repositório central usam o prefixo `central:` para não colidir
por nome com os do kit em `parallel_plan.py`. As tasks 1 e 3 não têm
dependência entre si e não compartilham arquivo: podem rodar em paralelo. A
task 4 e a task 6 registram evidência no próprio documento, então são
serializadas pela interseção no arquivo da SDD.

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Kit: escrever `test_render_prompts_sync.py` com os 7 testes e ver os de RF04 a RF07 falharem contra o `render_prompts.py` atual | RF04, RF05, RF06, RF07, RF08, RF11 | _framework/scripts/tests/test_render_prompts_sync.py | |
| 2 | Kit: `_sync_file` em bytes com rejeição de symlink, `_bundle_orphans`, laço de templates e checagem de órfãos em `sync_copies`, docstring; rodar `render_prompts.py` para regenerar a cópia do bundle | RF04, RF05, RF06, RF07, RF08 | _framework/scripts/render_prompts.py, _framework/skills/doc-traceability-framework/scripts/render_prompts.py | 1 |
| 3 | Kit: criar `.gitattributes` (três padrões) e `test_gitattributes_generated.py` com os 3 testes | RF01, RF02, RF11 | .gitattributes, _framework/tests/test_gitattributes_generated.py | |
| 4 | Kit: rodar os critérios 1 a 14 (com sensores, só depois do commit da implementação) e registrar comando e saída real na Evidência desta SDD; conferir RF09, RF10 e RF12 pelos critérios 7, 12 e 14 | RF01, RF02, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12 | docs/sdd/SDD-DTF-0046.md | 2, 3 |
| 5 | Central: espelhar `.gitattributes`, as duas cópias de `render_prompts.py` e os dois arquivos de teste, mesmos caminhos | RF03, RF13 | central:.gitattributes, central:_framework/scripts/render_prompts.py, central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py, central:_framework/tests/test_gitattributes_generated.py, central:_framework/scripts/tests/test_render_prompts_sync.py | 1, 2, 3 |
| 6 | Rodar o critério 15 (kit e central iguais, `--check` verde no central) e registrar a saída na Evidência | RF03, RF13 | docs/sdd/SDD-DTF-0046.md | 4, 5 |

Dependência transitiva conferida à mão: 5 depende de 1, 2 e 3; 2 depende
de 1; 4 depende de 2 e 3 (logo, transitivamente, de 1); 6 depende de 4 e
5 (logo de 1, 2 e 3). A task 5 lista 1, 2 e 3 explicitamente porque copia
os artefatos dessas três tasks.

## Critérios de aceite / definição de pronto

Rodados na raiz do kit, salvo o critério 15, que roda no central. Definir
antes: `BUNDLE=_framework/skills/doc-traceability-framework` e
`CENTRAL=/home/michel/doc-traceability-central` (ou o worktree do central
com a branch de implementação, que é onde o espelho da task 5 existe).
"Antes" = `origin/main` no início da implementação; "Depois" = branch de
implementação. Nas mutações, reverter com `git checkout -- <arquivo>` (o
arquivo está commitado na branch). Cada comando roda de fato e a saída real
vai para a Evidência. O número do critério corresponde ao A01 a A15 da SPEC.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | Marca de gerado resolvida (RF01) | `git check-attr linguist-generated diff merge -- $BUNDLE/scripts/render_prompts.py $BUNDLE/references/workflow-rules.yaml $BUNDLE/templates/spec.template.md` | Nove linhas: para cada arquivo `linguist-generated: true`, `diff: unspecified`, `merge: unspecified` | automatizado |
| 2 | Manuais e originais não marcados (RF02) | `git check-attr linguist-generated -- $BUNDLE/SKILL.md $BUNDLE/prompts/framework-audit.md _framework/scripts/render_prompts.py _framework/templates/spec.template.md` | Quatro linhas `linguist-generated: unspecified` | automatizado |
| 3 | Sem `-diff` nem `merge=` (RF01) | `grep -c -e '^[^#].* -diff' -e '^[^#].* diff$' -e '^[^#].* diff ' -e '^[^#].* merge=' .gitattributes; echo "exit=$?"` | Imprime `0` e `exit=1` (o `grep -c` sem casamento sai 1, que é o esperado) | automatizado |
| 4 | Central igual ao kit (RF03) | `cmp .gitattributes $CENTRAL/.gitattributes; echo "exit=$?"` | Sem saída do `cmp`; `exit=0` | automatizado |
| 5 | Testes de `.gitattributes` (RF01, RF02, RF11) | `python3 -m pytest _framework/tests/test_gitattributes_generated.py -v` | 3 passed; 0 failed | automatizado |
| 6 | Templates gerados e em dia (RF04) | `OUT=$(mktemp); python3 _framework/scripts/render_prompts.py --check > "$OUT"; echo "exit=$?"; grep -c "templates/.*template.md: sincronizado" "$OUT"` | `exit=0` e contagem `10` | automatizado |
| 7 | Sensor RF09 e RF04: template editado à mão reprova os dois mecanismos (RF04, RF09) | `echo "<!-- mão -->" >> $BUNDLE/templates/spec.template.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 -m pytest _framework/tests/test_template_parity.py -q`; `git checkout -- $BUNDLE/templates/spec.template.md`; repetir os dois comandos | Com a mutação: `--check` imprime `❌ ... spec.template.md: divergente de ...` e `exit=1`, e `test_templates_md_paridade` FAILED. Após reverter: `exit=0` e pytest passed | automatizado |
| 8 | Órfão reprovado sem apagar (RF05) | `cp $BUNDLE/templates/spec.template.md $BUNDLE/templates/orfao.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `python3 _framework/scripts/render_prompts.py; echo "exit=$?"`; `test -f $BUNDLE/templates/orfao.md && echo preservado`; `rm $BUNDLE/templates/orfao.md` | Os dois `exit=1`, linha com `órfão` nomeando `orfao.md`, e `preservado` | automatizado |
| 9 | Bytes, não texto (RF06) | `sed -i 's/$/\r/' $BUNDLE/templates/adr.template.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `git checkout -- $BUNDLE/templates/adr.template.md`. Antes (checkout de `origin/main`, mesma mutação): `exit=0`, provando a lacuna | Depois: `exit=1` com `divergente`; Antes: `exit=0` | automatizado |
| 10 | Sem `ci/` no bundle e idempotência (RF08, RF04) | `python3 _framework/scripts/render_prompts.py; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"; test ! -e $BUNDLE/templates/ci && echo sem-ci; git status --porcelain -- $BUNDLE` | `exit=0`, `sem-ci`, e `git status --porcelain` sem nenhuma linha (rodado com a implementação já commitada) | automatizado |
| 11 | Destino symlink reprovado (RF07) | `rm $BUNDLE/templates/inc.template.md && ln -s "$PWD/_framework/templates/inc.template.md" $BUNDLE/templates/inc.template.md`; `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `git checkout -- $BUNDLE/templates/inc.template.md` | Linha com `é symlink` nomeando `inc.template.md` e `exit=1` | automatizado |
| 12 | Fronteira com a SPEC-DTF-0019 (RF10) | `git diff --stat origin/main -- .ignore .gitignore _framework/tests/test_repo_hygiene.py .github/workflows/framework-check.yml; grep -c "doc-traceability-framework" .ignore; echo "exit=$?"` | `git diff --stat` sem nenhuma linha; `grep -c` imprime `0` e `exit=1` | automatizado |
| 13 | Testes do sync (RF04 a RF08, RF11) | `python3 -m pytest _framework/scripts/tests/test_render_prompts_sync.py -v` | 7 passed; 0 failed. Sensor: reverter `_framework/scripts/render_prompts.py` ao estado de `origin/main` faz `test_sync_copies_gera_templates_md`, `test_sync_copies_reprova_template_orfao_nos_dois_modos` e `test_sync_file_compara_bytes_crlf` FAILED | automatizado |
| 14 | Não-retroatividade e YAML intocado (RF12) | `git diff --stat origin/main -- _framework/rules/workflow-rules.yaml CHANGELOG.md $BUNDLE/references/workflow-rules.yaml`; `git diff --name-status --diff-filter=AD origin/main -- $BUNDLE`; `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` (este último também no checkout de `origin/main`) | Os dois `git diff` sem nenhuma linha (nenhum arquivo adicionado nem removido no bundle) e o mesmo `exit` antes e depois | automatizado |
| 15 | Kit e central iguais e `--check` verde no central (RF03, RF13) | `for f in .gitattributes _framework/scripts/render_prompts.py $BUNDLE/scripts/render_prompts.py _framework/tests/test_gitattributes_generated.py _framework/scripts/tests/test_render_prompts_sync.py; do cmp "$f" "$CENTRAL/$f"; echo "rc=$? $f"; done; cd $CENTRAL; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | Cinco linhas `rc=0`, sem saída do `cmp`; `exit=0` | automatizado |

## Instruções específicas para a IA implementadora

- Branch nomeada pelo id que a originou, por exemplo
  `sdd/SDD-DTF-0046-bundle-gerado`, levada a main por PR; nunca commit de
  implementação direto em main. Todo commit carrega `Refs: SDD-DTF-0046`.
- Implementar em sessão separada da que compilou esta SDD, aberta no kit,
  em worktree próprio (`git worktree add` explícito). O central é um segundo
  repositório com PR próprio (task 5). Nunca fazer merge dos PRs: o humano
  mescla.
- A verificação (status `implemented`) é feita pelo `sdd-verifier` em sessão
  separada; quem implementou não preenche a Evidência de verificação como
  verificador independente.
- Ordem: task 1 e task 3 primeiro (em paralelo, se houver duas sessões);
  ver os testes de RF04 a RF07 falharem antes de tocar `render_prompts.py`.
- `render_prompts.py`: alterar `_sync_file` e `sync_copies` no lugar,
  acrescentar apenas `_bundle_orphans`; sem módulo novo, sem dependência
  nova. Manter inalteradas as mensagens `✅ ...: sincronizado.` e
  `❌ ...: divergente de ...`. Regenerar a cópia do bundle rodando
  `python3 _framework/scripts/render_prompts.py`, nunca à mão.
- `.gitattributes`: exatamente o conteúdo da "Especificação técnica
  consolidada"; nenhum atributo `diff` nem `merge`; nenhum arquivo manual do
  bundle marcado.
- Não alterar: `.ignore`, `.gitignore`, `_framework/tests/test_repo_hygiene.py`,
  `.github/workflows/framework-check.yml`, `_framework/tests/test_template_parity.py`,
  `workflow-rules.yaml`, `CHANGELOG.md`, templates, `SKILL.md`,
  `prompts/*.md`, `docs/guias/guia-tecnico.md`, nenhum registry. Não subir
  `framework.version`.
- Nas tabelas do documento e da Evidência, nunca usar pipe escapado dentro
  de célula (quebra `validate_state.py`); reescrever o comando sem pipe.
- Espelhar no central os cinco arquivos da task 5 byte a byte (regra do
  `_framework/AGENTS.md`) e rodar o critério 15.
- Sensores dos critérios 7 a 9, 11 e 13 só depois do commit da
  implementação; sempre reverter com `git checkout -- <arquivo>`.
- Antes do PR, rodar `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q`
  e `python3 _framework/scripts/framework_check.py --auto` e registrar a
  saída.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirmar as duas direções:

- [ ] Todo requisito consolidado (RF01 a RF13) tem arquivo, teste ou
      critério correspondente, no kit e no central.
- [ ] Todo arquivo tocado pela implementação aparece na "Decomposição em
      tasks" ou nas "Instruções específicas"; arquivo não listado é escopo
      que faltou registrar (atualizar a SDD) ou scope creep a remover
      antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra além de
      `_bundle_orphans`; nenhum `-diff`, nenhum `merge=`, nenhum `templates/ci/`
      no bundle, nenhuma RFC-DTF-0009.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou —
quem escreveu o código tem o resultado como conclusão desejada. Para cada
critério da tabela acima: comando rodado de fato nesta sessão e saída real,
nunca "deve passar" nem resultado de memória. Critérios 1 a 14 rodam no kit
e o 15 no central.

**Verificador independente:** não — SDD em `in_review`, ainda não implementada nem verificada

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Critério sem teste automatizado: escreva "sem
teste", nunca marque como verificado por leitura de código. "Assertion
(file:line)": caminho e linha exatos da asserção; critério `manual` ou
`n/a` usa `n/a`. "Perfil usado": repete o "Perfil esperado" ou declara
divergência com justificativa entre parênteses.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0020 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0020.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
