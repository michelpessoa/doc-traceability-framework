---
id: SDD-DTF-0043
type: SDD
title: "Índices gerados do kit: INDEX.md, mapa de seções do YAML, INDEX de SDDs e sumários navegáveis"
status: implemented
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0042]
source_docs:
  - id: "SPEC-DTF-0016"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0016.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Compilada da SPEC-DTF-0016 (approved, sizing medium, frente A da RFC-DTF-0008). Só implementar DEPOIS de SDD-DTF-0042 estar implemented e mergeada em main (ambas tocam workflow-rules.yaml e render_prompts.py; rebasear sobre a versão 2.3.1) e ANTES da SDD de SPEC-DTF-0020. Implementar em branch sdd/SDD-DTF-0043-indices-gerados, sessão separada no repositório do kit, seguindo a seção Decomposição em tasks; rodar cada critério de aceite de fato; verificação por sdd-verifier em sessão separada."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, indice, render_prompts, gerado, contexto]
---

# Índices gerados do kit: INDEX.md, mapa de seções do YAML, INDEX de SDDs e sumários navegáveis

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar. Deve ser autocontido, mas
> sempre rastreável a SPEC-DTF-0016 e RFC-DTF-0008 via `source_docs`
> (id + url, já que os documentos de origem estão no repositório central).

## Resumo executivo

Dar a uma LLM (e a um humano) um caminho barato até qualquer arquivo do
kit, qualquer seção do `workflow-rules.yaml` e qualquer SDD de um
repositório de projeto, por meio de quatro índices gerados por script e
reprovados no CI quando defasados: `_framework/INDEX.md`, o mapa de
seções do YAML, `docs/sdd/INDEX.md` (mais o cabeçalho de versão do
`registry.md`) e o sumário de `universal.md` e `guia-tecnico.md`. Um
módulo novo, `_framework/scripts/render_indexes.py`, concentra a lógica;
`render_prompts.py` só ganha fiação (≤ 20 linhas adicionadas). Nenhuma
regra de comportamento do framework muda: `workflow-rules.yaml` não é
editado por esta SDD. É a frente A da RFC-DTF-0008.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — a RFC-DTF-0008 (`approved`) avaliou o gate `rfc_to_adr` como
false (`requires_adr: false`); sizing `medium`: feature contida no tooling
do kit, nenhum critério de `decision_gates.rfc_to_adr` se aplica.

Decisões humanas de 2026-09-24, registradas na SPEC e vinculantes aqui:

1. O §0 (bloco `framework:`, ~10,6 KB, quase todo changelog) NÃO conta
   como "maior seção" na métrica de teto do mapa. Constante
   `LARGEST_SECTION_EXCLUDES = {"0"}`. Com §0 incluído, mapa + §0 estouram
   13,5 KB e a métrica não fecha com nenhum mapa realista; a RFC-DTF-0009
   prevê tirar o changelog do YAML. A RFC-DTF-0008 diz "30 seções de
   topo"; a medição dá 25 chaves de topo mais o preâmbulo — vale a
   medição.
2. O cabeçalho do `registry.md` mostra a versão corrente do framework só
   quando `find_rules_file()` acha o YAML no repositório onde o comando
   roda (na prática, o kit); nos demais repositórios mostra
   `framework_version` do `registry.yaml` (versão de mapeamento), coerente
   com "mudanças não retroativas". Os registries centrais existentes não
   mudam.

## Requisitos consolidados

Numeração dos ids `§`: o YAML já tem seções numeradas nos comentários de
banner (`# 13. GATE OBRIGATÓRIO: ...`, com sufixos `3b`, `3c`), que são as
citações "seção 3", "seção 13" de SKILL.md e procedimentos. O mapa reusa
exatamente essa numeração (não renumera). O trecho anterior ao primeiro
banner (bloco `framework:`, com o changelog) recebe o id `§0`. A medição
no YAML atual dá 25 chaves de topo em 19 banners (+ `3b`, `3c` = 21
seções numeradas, mais `§0` = 22 linhas no mapa).

| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |
|---|---|---|---|
| RF01 | `_framework/INDEX.md` deve ter exatamente uma linha de tabela por arquivo do kit (toda a árvore `_framework/`, exceto caches e o próprio `INDEX.md`), com colunas caminho, o que é, quando ler e faixa de tamanho. | Quando `render_indexes.py` rodar, o sistema deve gerar `_framework/INDEX.md` com uma linha por arquivo existente em `_framework/`, na ordem alfabética do caminho, sem timestamp, e a faixa de tamanho deve ser uma de `<2 KB`, `2-8 KB`, `8-32 KB`, `>32 KB`. | `_framework/scripts/render_indexes.py`, `_framework/INDEX.md` |
| RF02 | O texto "o que é" e "quando ler" vem de um manifesto escrito à mão, `_framework/rules/kit-index.yaml`, cuja cobertura é verificada: arquivo sem entrada e entrada sem arquivo reprovam. | Se algum arquivo do kit não casar com nenhuma entrada de `kit-index.yaml`, ou alguma entrada não casar com nenhum arquivo, então o sistema deve sair com código 1 em `--check` (e código 2 fora dele), listando cada caminho ou padrão órfão. | `_framework/scripts/render_indexes.py`, `_framework/rules/kit-index.yaml` |
| RF03 | O mapa de seções do YAML deve listar, por seção, id estável `§N`, título do banner, chaves de topo contidas, linha inicial, bytes e resumo de uma linha, sem alterar o YAML. | Quando `render_indexes.py` rodar, o sistema deve gerar `_framework/rules/workflow-rules.map.md` com uma linha por seção (`§0` mais cada banner numerado), cujos ids e linha inicial coincidam com os banners de `workflow-rules.yaml`, e não deve modificar o YAML. | `_framework/scripts/render_indexes.py`, `_framework/rules/workflow-rules.map.md` |
| RF04 | O resumo de uma linha é a primeira frase do primeiro parágrafo de comentário após o banner; sem parágrafo, é o título do banner; nunca passa de 100 caracteres. | Onde a seção tiver parágrafo de comentário após o banner, o sistema deve usar sua primeira frase truncada em 100 caracteres como resumo; se a seção não tiver, então o sistema deve usar o título do banner. | `_framework/scripts/render_indexes.py` |
| RF05 | Todo id `§N` citado em prosa do kit deve existir no mapa. | Se algum arquivo `.md` sob `_framework/` (exceto o mapa e o `INDEX.md`) citar `§<id>` que não existe no mapa, então o sistema deve sair com código 1 em `--check`, apontando arquivo, linha e id. | `_framework/scripts/render_indexes.py` |
| RF06 | `docs/sdd/INDEX.md` deve ter uma linha por SDD do repositório de projeto: id, resumo de uma linha, arquivos de código declarados, `substitui`/`substituída por` e status. | Quando `render_indexes.py sdd <dir>` rodar, o sistema deve gerar `<dir>/INDEX.md` com uma linha por arquivo `SDD-*-NNNN.md` de `<dir>`, ordenada por id, lendo `status`, `supersedes` e `superseded_by` do front-matter. | `_framework/scripts/render_indexes.py`, `docs/sdd/INDEX.md` |
| RF07 | Os arquivos de código vêm da seção de arquivos da SDD; SDD sem essa seção não quebra o índice, mas é sinalizada. | Se uma SDD não tiver bloco de arquivos tocados reconhecível, então o sistema deve escrever `(sem seção de arquivos)` na célula e imprimir aviso com o id, sem falhar o `--check`. | `_framework/scripts/render_indexes.py` |
| RF08 | `registry.md` deve sair determinístico (sem hora de geração) e com a versão corrente do framework no cabeçalho, com modo `--check`. | Quando `generate_registry_md.py` rodar, o sistema deve emitir o cabeçalho `Framework v<versão>` com a versão de `framework.version` do `workflow-rules.yaml` encontrado, sem timestamp; e onde `--check` for passado, o sistema deve sair com código 1 se o `registry.md` em disco divergir do gerado. | `_framework/scripts/generate_registry_md.py`, `docs/sdd/registry.md` |
| RF09 | `universal.md` e `guia-tecnico.md` devem ganhar sumário navegável gerado (títulos `##`, âncora e bytes da seção). | Quando `render_indexes.py` rodar, o sistema deve gerar o sumário de `universal.md` dentro de `build_universal` e o de `docs/guias/guia-tecnico.md` entre os marcadores `<!-- BEGIN GENERATED: sumário -->` e `<!-- END GENERATED -->`, com uma linha por título `##`. | `_framework/scripts/render_indexes.py`, `_framework/prompts/universal.md`, `docs/guias/guia-tecnico.md` |
| RF10 | Cada índice tem teto de tamanho verificável no `--check`. | Se algum índice exceder seu teto (tabela abaixo), então o sistema deve sair com código 1 informando índice, tamanho medido e teto. | `_framework/scripts/render_indexes.py` |
| RF11 | Todos os modos têm `--check` no CI; a lógica vive em módulo novo importado por `render_prompts.py`, que não cresce além de fiação. | Quando `render_prompts.py --check` rodar, o sistema deve executar também os `--check` dos índices e falhar se algum divergir; e o diff de `render_prompts.py` desta SDD deve ter no máximo 20 linhas adicionadas, todas de import, chamada ou linha de `build_agents`. | `_framework/scripts/render_prompts.py`, `.github/workflows/framework-check.yml` |
| RF12 | O `AGENTS.md` gerado deve apontar para `_framework/INDEX.md` e para o mapa. | Quando `render_prompts.py` rodar, o sistema deve gerar `AGENTS.md` contendo uma linha que cita `_framework/INDEX.md` e `_framework/rules/workflow-rules.map.md`. | `_framework/scripts/render_prompts.py`, `AGENTS.md` |
| RF13 | A geração deve ser idempotente e a cópia da skill deve permanecer em paridade. | Quando `render_indexes.py` rodar duas vezes seguidas, o sistema deve produzir diff vazio na segunda; e o novo módulo deve ter cópia byte a byte em `_framework/skills/doc-traceability-framework/scripts/` (via `sync_copies`). | `_framework/scripts/render_indexes.py`, `_framework/tests/test_kit_parity.py` |

### Tetos de tamanho (RF10)

| Índice | Teto verificável |
|---|---|
| Mapa de seções do YAML | `bytes(mapa) + bytes(maior seção, exceto §0) <= floor(0.15 * bytes(workflow-rules.yaml))`, calculado no momento da checagem. Na medição da SPEC: 0,15 x 90 KB = 13,5 KB; maior seção (§12) = 8,7 KB; sobra ~4,8 KB para o mapa (após a SDD-DTF-0042 o YAML muda de tamanho; o teto é recalculado na hora). Cada linha ≤ 180 bytes; cabeçalho ≤ 400 bytes. |
| `_framework/INDEX.md` | ≤ 200 bytes por linha de arquivo e ≤ 24 KB no total. |
| `docs/sdd/INDEX.md` | ≤ 400 bytes por linha de SDD e ≤ `1 KB + 400 bytes x nº de SDDs`. |
| Sumário de `universal.md` e de `guia-tecnico.md` | ≤ 3 KB cada. |

### Casos de borda / condições de erro

| Caso | RF relacionado | Comportamento esperado |
|---|---|---|
| YAML sem nenhum banner numerado `# N. TÍTULO` | RF03 | Sai com código 2 e mensagem `workflow-rules.yaml sem seção numerada`; nunca escreve mapa vazio nem inventa ids |
| Dois banners com o mesmo id, ou ids fora de ordem crescente | RF03 | Sai com código 2 apontando as duas linhas; ids estáveis exigem unicidade e ordem |
| Seção com banner e nenhuma chave de topo (só comentário) | RF03 | Linha no mapa com `chaves` = `(nenhuma)`; não é erro |
| Banner de título em várias linhas (§3c, §12) | RF03, RF04 | Título = primeira linha do banner; as demais linhas são ignoradas |
| Arquivo novo no kit sem entrada em `kit-index.yaml` | RF02 | `--check` sai com 1 listando o caminho; sem `--check` sai com 2 sem escrever (nada de linha genérica silenciosa) |
| Entrada de `kit-index.yaml` que casa mais de um padrão para o mesmo arquivo | RF02 | Vale a primeira entrada na ordem do arquivo; sobreposição é aceita, mas a entrada que não casa nenhum arquivo continua sendo erro |
| `__pycache__`, `.ruff_cache`, `.pytest_cache`, `.mypy_cache` e `*.pyc` sob `_framework/` | RF01 | Excluídos do índice; não exigem entrada |
| SDD sem seção de arquivos tocados | RF07 | Célula `(sem seção de arquivos)` e aviso; `--check` não falha por isso |
| SDD com arquivos apenas na tabela de tasks (coluna "Arquivos tocados") | RF06, RF07 | Extraídos da coluna; união com o bloco em prosa, sem duplicata |
| SDD sem front-matter válido ou sem `id` | RF06 | Sai com código 2 citando o arquivo; não é ignorada em silêncio |
| `docs/sdd/LESSONS.md`, `registry.md`, `registry.yaml`, `INDEX.md` no mesmo diretório | RF06 | Ignorados: só entram arquivos que casam `SDD-<CÓDIGO>-<NNNN>.md` |
| `docs/sdd/` sem nenhuma SDD | RF06 | Gera `INDEX.md` só com cabeçalho e `Total: 0` |
| Repositório de projeto sem `workflow-rules.yaml` acessível | RF08 | Cabeçalho usa `framework_version` do `registry.yaml`; nunca `N/D` se o campo existe |
| Arquivo `guia-tecnico.md` sem marcadores de sumário | RF09 | `--check` sai com 1 (`marcador ausente`); sem `--check`, insere o bloco logo após o primeiro `#` do arquivo |
| Título `##` dentro de bloco de código cercado | RF09 | Ignorado (não vira entrada de sumário) |
| `§` citado dentro do próprio mapa ou do `INDEX.md` | RF05 | Esses dois arquivos não são varridos |
| Índice acima do teto | RF10 | Código 1 com nome do índice, medido e teto |

### Requisitos não funcionais

- Saída determinística: sem timestamp, sem ordem dependente de sistema de
  arquivos (sempre ordenada), fim de linha LF, UTF-8.
- Sem dependência nova: stdlib e PyYAML, que o kit já usa.
- `render_prompts.py` não cresce além da fiação (RF11); toda a lógica
  nova fica em `render_indexes.py`.
- Faixa de tamanho em `INDEX.md` em intervalos, não em bytes exatos, para
  editar um arquivo do kit não mudar o índice a cada commit.

### Requisitos transversais (sweep, herdado da SPEC)

Idempotência: RF13. Observabilidade: RF11 (saída `✅`/`❌` por arquivo e
código de saída 0/1/2, no padrão de `write_full`). Validação de entrada:
RF02, RF03, RF07. Limite de volume: RF10. Autorização, concorrência e
falha de dependência externa: n/a (scripts locais, execução sequencial,
só sistema de arquivos local e PyYAML, que o kit já usa).

### Fora de escopo

- Trocar as citações soltas "seção N" em `SKILL.md`, procedimentos e
  prompts pelos ids `§N` (frente C; aqui só se garante, por RF05, que
  qualquer `§` citado resolve).
- Renumerar, dividir ou reduzir o `workflow-rules.yaml` (RFC-DTF-0009).
- Corrigir `gate_implementation_before_code` e o teste de paridade de
  templates (frente B, SDD-DTF-0042).
- `SKILL.md` enxuto, `description` curta e `.gitignore`/`.claudeignore`
  (frentes C e E).
- Habilitar `docs/sdd/INDEX.md` no CI dos repositórios de projeto já
  mapeados (EVM, ABSTRACTCLINIC, CIMOCLINIC): mudança não retroativa; o
  comando fica disponível e cada projeto o adota quando quiser.
- Tratar `docs/sdd/INDEX.md` como documento do registry (é saída gerada,
  como o `registry.md`).
- Editar `_framework/rules/workflow-rules.yaml` (esta SDD só o lê).

## Especificação técnica consolidada

Visão geral: um módulo novo, `_framework/scripts/render_indexes.py`,
concentra os quatro geradores e as checagens. `render_prompts.py` importa
dele `generate_all` (RF11), invoca-o de `main()` com o mesmo `check`, e
`build_universal` chama `build_toc` para injetar o sumário. O módulo tem
CLI própria (`render_indexes.py [--check]` para os índices do kit;
`render_indexes.py sdd <dir> [--check]` para o `INDEX.md` de SDDs de um
repositório de projeto). `generate_registry_md.py` ganha `--check` e perde
o timestamp. `sync_copies` já copia todo `scripts/*.py` para a cópia da
skill, então o módulo novo é replicado sem código extra.

Arquivos gerados:

- `_framework/INDEX.md` (RF01)
- `_framework/rules/workflow-rules.map.md` (RF03)
- `docs/sdd/INDEX.md` e `docs/sdd/registry.md` (RF06, RF08) — no kit e em
  cada repositório de projeto que adotar
- sumário em `_framework/prompts/universal.md` e
  `docs/guias/guia-tecnico.md` (RF09)

Arquivo escrito à mão (insumo): `_framework/rules/kit-index.yaml`.

**Consumes** (já existe):

- `framework_lib.find_rules_file() -> Path | None` e
  `framework_lib.load_rules() -> dict` (usados por `render_prompts.py`).
- `framework_lib.read_frontmatter(path) -> (dict, str)`.
- `render_prompts.sync_copies(root: Path, check: bool) -> bool` (copia o
  módulo novo para a skill).
- `generate_registry_md.load_registry(docs_dir: Path) -> dict`,
  `render_table(docs: list) -> str`.
- `framework.version` de `workflow-rules.yaml` (`"2.3.1"` depois da
  SDD-DTF-0042).

**Produces**, todos em `_framework/scripts/render_indexes.py`:

```python
BANNER_RE = r"^# (\d+[a-z]?)\. (.+)$"      # linha de título; fence = ^#{20,}$
LARGEST_SECTION_EXCLUDES = {"0"}
SUMMARY_MAX = 100                          # caracteres (RF04)
SIZE_BUCKETS = [(2048, "<2 KB"), (8192, "2-8 KB"), (32768, "8-32 KB"), (None, ">32 KB")]
CEILINGS = {"kit_index_row": 200, "kit_index_total": 24576,
            "map_row": 180, "map_header": 400, "sdd_row": 400,
            "sdd_base": 1024, "toc_total": 3072}

@dataclass(frozen=True)
class Section:
    sid: str            # "0", "3b", "13"  (exibido como "§13")
    title: str          # primeira linha do banner; "preâmbulo" para §0
    keys: tuple[str, ...]   # chaves de topo YAML na faixa
    start: int          # linha (1-based) da linha `# N. TÍTULO`; 1 para §0
    end: int            # última linha da seção
    nbytes: int
    summary: str        # RF04, <= SUMMARY_MAX

def parse_yaml_sections(text: str) -> list[Section]: ...        # RF03, RF04
def build_section_map(yaml_path: Path) -> str: ...              # RF03
def check_map_ceiling(sections: list[Section], map_text: str, yaml_bytes: int) -> list[str]: ...  # RF10

def load_kit_manifest(path: Path) -> list[dict]: ...            # RF02
def list_kit_files(root: Path) -> list[Path]: ...               # RF01
def build_kit_index(root: Path, manifest: list[dict]) -> str: ...  # RF01, RF02

def extract_sdd_files(body: str) -> list[str]: ...              # RF07
def build_sdd_index(sdd_dir: Path) -> str: ...                  # RF06, RF07

def build_toc(markdown: str) -> str: ...                        # RF09
def inject_toc(text: str, toc: str) -> str: ...                 # RF09 (marcadores)
def check_section_refs(root: Path, sections: list[Section]) -> list[str]: ...  # RF05

def generate_all(root: Path, rules: dict, check: bool) -> bool: ...  # RF11
def main(argv: list[str] | None = None) -> int: ...             # 0 ok, 1 divergência, 2 erro estrutural
```

Em `_framework/scripts/generate_registry_md.py`:

```python
def render_header(project: str, fw_version: str) -> str: ...     # sem timestamp (RF08)
def main(argv: list[str] | None = None) -> int: ...              # aceita --check
```

**Schema de `_framework/rules/kit-index.yaml`** (escrito à mão, verificado
por RF02):

```yaml
entries:                       # ordem importa: a primeira entrada que casa vence
  - path: "scripts/*.py"       # glob relativo a _framework/, estilo pathlib
    what: "Script de validação ou geração do kit"    # 1 linha, <= 60 caracteres
    when: "Ao rodar ou depurar o gate correspondente" # 1 linha, <= 60 caracteres
```

Toda entrada tem exatamente as chaves `path`, `what` e `when` (string não
vazia). Chave extra ou vazia é erro código 2.

**Schema das linhas geradas:**

`_framework/INDEX.md` — cabeçalho fixo (`# Índice do kit`, nota "Gerado por
`render_indexes.py` — não edite à mão", `Total: N arquivos`) e tabela:

| Caminho (relativo a `_framework/`) | O que é | Quando ler | Tamanho |
|---|---|---|---|

`_framework/rules/workflow-rules.map.md` — mesmo cabeçalho, mais
`YAML: <bytes> bytes; mapa + maior seção: <bytes> (<pct>% de 15%)`, e a
tabela:

| § | Seção | Chaves | Linhas | Bytes | Resumo |
|---|---|---|---|---|---|
| §13 | GATE OBRIGATÓRIO: NENHUMA IMPLEMENTAÇÃO PULA ... | `gate_implementation_before_code` | 973-1059 | 5720 | ... |

`docs/sdd/INDEX.md` — cabeçalho e `Total: N SDDs`, tabela:

| ID | Resumo | Arquivos de código | Substitui | Substituída por | Status |
|---|---|---|---|---|---|

Resumo da SDD: primeira frase da seção `## Resumo executivo`, truncada em
140 caracteres. Arquivos: união de (a) caminhos entre crases nas linhas do
bloco que começa em linha iniciada por `Arquivos tocados` ou
`**Arquivos a alterar` dentro de `## Especificação técnica consolidada`,
até o próximo parágrafo que não seja item de lista, e (b) caminhos entre
crases na coluna `Arquivos tocados` da tabela de `## Decomposição em
tasks`; só tokens com `/` ou extensão; ordenados; no máximo 6 por linha,
depois `+N`.

Sumário (RF09): uma linha `- [<título>](#<âncora>) — <bytes> bytes` por
título `##`; âncora no estilo GitHub (minúsculas, espaços em `-`, sem
pontuação); bytes = tamanho da seção até o próximo `##`.

**Fiação em `render_prompts.py`** (única mudança, ≤ 20 linhas adicionadas):
`from render_indexes import generate_all, build_toc`; em `main()`,
`ok &= generate_all(root, load_rules(), check)`; em `build_universal`, a
chamada a `build_toc`; em `build_agents`, a linha de RF12.

**Fiação em `generate_registry_md.py`:** `--check`; cabeçalho
`_Gerado automaticamente a partir de registry.yaml. Não editar
manualmente. Framework v<versão>._`, onde `<versão>` é `framework.version`
se `find_rules_file()` achar o YAML, senão `framework_version` do
`registry.yaml`.

**Job de CI** em `.github/workflows/framework-check.yml`: o passo
existente `python3 _framework/scripts/render_prompts.py --check` passa a
cobrir os índices por RF11; passo novo `python3
_framework/scripts/render_indexes.py sdd docs/sdd --check` e `python3
_framework/scripts/generate_registry_md.py docs/sdd --check`.

### Tratamento de erro por contrato

| Caso | RF relacionado | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| YAML sem banner numerado | RF03 | `SystemExit(2)` com mensagem | `parse_yaml_sections` |
| Banner duplicado / fora de ordem | RF03 | `SystemExit(2)` com as duas linhas | `parse_yaml_sections` |
| Arquivo sem entrada no manifesto | RF02 | `--check`: `False` e lista; escrita: `SystemExit(2)` | `build_kit_index` |
| Entrada do manifesto sem arquivo | RF02 | Idem | `build_kit_index` |
| Manifesto com chave extra ou vazia | RF02 | `SystemExit(2)` | `load_kit_manifest` |
| `§id` inexistente na prosa | RF05 | `False` com arquivo:linha:id | `check_section_refs` |
| SDD sem seção de arquivos | RF07 | Célula `(sem seção de arquivos)` + aviso | `extract_sdd_files`, `build_sdd_index` |
| SDD sem front-matter/id | RF06 | `SystemExit(2)` citando o arquivo | `build_sdd_index` |
| `registry.md` divergente | RF08 | `--check` sai 1 | `generate_registry_md.main` |
| Marcador de sumário ausente | RF09 | `--check` sai 1; escrita insere o bloco | `inject_toc` |
| Teto excedido | RF10 | Código 1 com nome, medido e teto | `check_map_ceiling`, `generate_all` |
| Segunda execução gera diff | RF13 | Teste falha | `test_render_indexes.py` |

### Estratégia de teste (da SPEC)

| RF-ID / contrato | Tipo de teste | Mock? | Arquivo de teste |
|---|---|---|---|
| RF01 | Unitário sobre árvore fixture em `tmp_path` | Não | `_framework/tests/test_render_indexes.py` |
| RF02 | Unitário, mutação (arquivo novo sem entrada; entrada sem arquivo) | Não | `_framework/tests/test_render_indexes.py` |
| RF03 | Unitário com YAML fixture e teste sobre o YAML real | Não | `_framework/tests/test_render_indexes.py` |
| RF04 | Unitário (com e sem parágrafo; > 100 caracteres) | Não | `_framework/tests/test_render_indexes.py` |
| RF05 | Unitário, mutação (`§99` num `.md` fixture) | Não | `_framework/tests/test_render_indexes.py` |
| RF06 | Unitário com 3 SDDs fixture (uma com `superseded_by`) | Não | `_framework/tests/test_render_indexes.py` |
| RF07 | Unitário (bloco em prosa, só tabela, nenhum) | Não | `_framework/tests/test_render_indexes.py` |
| RF08 | Unitário: cabeçalho com versão, ausência de hora, `--check` | Não | `_framework/scripts/tests/test_generate_registry_md.py` (novo) |
| RF09 | Unitário (`##` em bloco cercado ignorado; marcador ausente) | Não | `_framework/tests/test_render_indexes.py` |
| RF10 | Unitário, mutação (índice inflado passa a falhar) e medição real | Não | `_framework/tests/test_render_indexes.py` |
| RF11 | Comando real | Não | `.github/workflows/framework-check.yml` |
| RF12 | Comando real | Não | `_framework/tests/test_render_indexes.py` (`-k agents_aponta_indice`) |
| RF13 | Paridade byte a byte + rodar duas vezes | Não | `_framework/tests/test_kit_parity.py`, `_framework/tests/test_render_indexes.py` |

### Plano de implementação

Ordem: só começa depois da SDD-DTF-0042 estar `implemented` e mergeada em
main (rebase sobre o YAML na versão 2.3.1 e sobre o `render_prompts.py`
dela). O mapa registra linhas do YAML, então só faz sentido depois que a
frente B terminou de mexer nele. Esta SDD termina ANTES da SDD de
SPEC-DTF-0020. Os passos estão detalhados em "Decomposição em tasks".

### Riscos operacionais e mitigação

- **Mapa não cabe no teto depois da SDD-DTF-0042**, porque ela muda o
  tamanho do YAML e, com ele, os 15%. Mitigação: o teto é calculado na
  hora; se estourar, reduz-se `SUMMARY_MAX` e `map_row` antes de tocar a
  métrica da RFC.
- **`kit-index.yaml` envelhece.** Mitigação: RF02 reprova arquivo sem
  entrada e entrada sem arquivo, então a falha aparece no CI no mesmo PR
  que cria o arquivo.
- **Heurística de `extract_sdd_files` não reconhecer formato de SDD
  futuro.** Mitigação: RF07 sinaliza em vez de falhar; o aviso lista os ids.
- **`render_prompts.py` crescer por engano.** Mitigação: checagem de
  ≤ 20 linhas adicionadas de RF11 no critério de aceite.
- **Ids `§` divergirem se alguém reescrever um banner.** Mitigação: RF03 e
  RF05 reprovam duplicata, ordem quebrada e citação inexistente.

### Plano de rollout / rollback

Rollout direto, sem feature flag: índices gerados entram no mesmo PR que o
gerador, e o CI passa a exigir que estejam em dia. Repositórios de projeto
já mapeados não são tocados (não retroativo); o comando
`render_indexes.py sdd docs/sdd` fica disponível para adoção voluntária.
Rollback: reverter o commit; apagar os arquivos gerados e o módulo não
afeta nenhum gate, pois nenhum outro script os lê.

### Observabilidade

Saída `✅ <arquivo>: em dia.` / `❌ <arquivo>: <motivo> — rode
render_indexes.py.` por índice, código de saída 0/1/2, e uma linha de
métrica por execução: `mapa+maior seção = <bytes> (<pct>% do YAML)`, que
é a métrica de sucesso da RFC-DTF-0008. Sem logs persistentes.

## Decomposição em tasks

Espelhamento no central (task 9) é o passo 9 do plano da SPEC: o
`_framework/` do central fica idêntico ao do kit; `docs/sdd/` só existe no
kit. Os caminhos da task 9 são relativos a
`/home/michel/doc-traceability-central/`, prefixados por `central:` para
não colidirem com os do kit.

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Manifesto `kit-index.yaml` cobrindo toda a árvore atual de `_framework/` (globs por pasta; entradas individuais para arquivos únicos), inclusive os arquivos novos desta SDD | RF01, RF02 | `_framework/rules/kit-index.yaml` | |
| 2 | Módulo `render_indexes.py` com todos os contratos (mapa, índice do kit, índice de SDDs, sumário, tetos, `generate_all`, CLI) | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF09, RF10, RF13 | `_framework/scripts/render_indexes.py` | 1 |
| 3 | `generate_registry_md.py`: `render_header`, sem timestamp, `--check`, e seus testes | RF08 | `_framework/scripts/generate_registry_md.py`, `_framework/scripts/tests/test_generate_registry_md.py` | |
| 4 | Marcadores de sumário em `guia-tecnico.md` (logo após o primeiro `#`) | RF09 | `docs/guias/guia-tecnico.md` | |
| 5 | Fiação em `render_prompts.py` (import, `generate_all` em `main()`, `build_toc` em `build_universal`, linha de RF12 em `build_agents`), ≤ 20 linhas adicionadas; e `iter_documents` de `framework_lib.py` passa a ignorar o `INDEX.md` gerado, como já ignora `registry.md` (escopo registrado na implementação: sem isso `validate_doc.py docs/sdd` reprova o `INDEX.md`) | RF11, RF12 | `_framework/scripts/render_prompts.py`, `_framework/scripts/framework_lib.py` | 2 |
| 6 | Testes de `render_indexes` e extensão do teste de paridade | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF09, RF10, RF12, RF13 | `_framework/tests/test_render_indexes.py`, `_framework/tests/test_kit_parity.py` | 2, 5 |
| 7 | Passos novos no CI | RF11 | `.github/workflows/framework-check.yml` | 2, 3 |
| 8 | Gerar os índices e sincronizar cópias da skill (`render_prompts.py` e `render_indexes.py`) | RF01, RF03, RF06, RF08, RF09, RF12, RF13 | `_framework/INDEX.md`, `_framework/rules/workflow-rules.map.md`, `docs/sdd/INDEX.md`, `docs/sdd/registry.md`, `_framework/prompts/universal.md`, `AGENTS.md`, `docs/guias/guia-tecnico.md`, `_framework/skills/doc-traceability-framework/scripts/render_indexes.py`, `_framework/skills/doc-traceability-framework/scripts/generate_registry_md.py`, `_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `_framework/skills/doc-traceability-framework/scripts/framework_lib.py` | 1, 2, 3, 4, 5 |
| 9 | Espelhar `_framework/` e `docs/guias/guia-tecnico.md` no central | RF01, RF03, RF09, RF13 | `central:_framework/INDEX.md`, `central:_framework/rules/kit-index.yaml`, `central:_framework/rules/workflow-rules.map.md`, `central:_framework/scripts/render_indexes.py`, `central:_framework/scripts/generate_registry_md.py`, `central:_framework/scripts/render_prompts.py`, `central:_framework/scripts/tests/test_generate_registry_md.py`, `central:_framework/tests/test_render_indexes.py`, `central:_framework/tests/test_kit_parity.py`, `central:_framework/prompts/universal.md`, `central:_framework/skills/doc-traceability-framework/scripts/render_indexes.py`, `central:_framework/skills/doc-traceability-framework/scripts/generate_registry_md.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_prompts.py`, `central:_framework/scripts/framework_lib.py`, `central:_framework/skills/doc-traceability-framework/scripts/framework_lib.py`, `central:docs/guias/guia-tecnico.md`, `central:AGENTS.md` | 8 |

Ordem sugerida: tasks 1, 3 e 4 são independentes entre si (grupo
paralelizável); 2 depois de 1; 5 depois de 2; 6 e 7 depois de 5/3; 8
depois de todas as anteriores; 9 por último. Confirmar com
`python3 _framework/scripts/parallel_plan.py docs/sdd/SDD-DTF-0043.md`.

## Critérios de aceite / definição de pronto

Cada item vem do RF da SPEC-DTF-0016 (critérios EARS copiados, sem
relaxar) e do contrato/caso de erro da Parte 2. `pytest` roda de
`/home/michel/doc-traceability-framework`; `-k` sem caminho refere-se a
`_framework/tests/test_render_indexes.py`.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF01 — `INDEX.md` com uma linha por arquivo do kit, ordem alfabética, sem timestamp, faixa de tamanho em `<2 KB`, `2-8 KB`, `8-32 KB` ou `>32 KB` | `python3 -m pytest _framework/tests/test_render_indexes.py -k kit_index_uma_linha_por_arquivo -v` | Todos os testes selecionados passam | automatizado |
| 2 | RF02 — arquivo sem entrada e entrada sem arquivo reprovam (1 em `--check`, 2 fora dele, listando cada órfão); chave extra ou vazia no manifesto sai 2 | `python3 -m pytest _framework/tests/test_render_indexes.py -k manifesto_orfao -v` | Todos os testes selecionados passam | automatizado |
| 3 | RF03 — mapa com uma linha por seção (`§0` mais cada banner), ids e linha inicial coincidem com os banners do YAML real; YAML não modificado; banner duplicado, fora de ordem ou ausente sai 2 | `python3 -m pytest _framework/tests/test_render_indexes.py -k mapa_ids_batem_com_banners -v` | Todos os testes selecionados passam | automatizado |
| 4 | RF04 — resumo é a primeira frase do primeiro parágrafo de comentário, truncada em 100 caracteres; sem parágrafo, o título do banner | `python3 -m pytest _framework/tests/test_render_indexes.py -k resumo_primeira_frase -v` | Todos os testes selecionados passam | automatizado |
| 5 | RF05 — `§<id>` citado em `.md` sob `_framework/` que não existe no mapa sai 1 com arquivo, linha e id; mapa e `INDEX.md` não são varridos | `python3 -m pytest _framework/tests/test_render_indexes.py -k secao_citada_inexistente -v` | Todos os testes selecionados passam | automatizado |
| 6 | RF06 — `INDEX.md` de SDDs com uma linha por `SDD-*-NNNN.md`, ordenada por id, com `status`, `supersedes`, `superseded_by`; diretório sem SDD gera `Total: 0`; SDD sem front-matter/id sai 2 | `python3 -m pytest _framework/tests/test_render_indexes.py -k sdd_index_campos -v` | Todos os testes selecionados passam | automatizado |
| 7 | RF07 — SDD sem bloco de arquivos: célula `(sem seção de arquivos)`, aviso com o id, `--check` não falha; união de bloco em prosa e coluna da tabela de tasks | `python3 -m pytest _framework/tests/test_render_indexes.py -k sdd_sem_secao_arquivos -v` | Todos os testes selecionados passam | automatizado |
| 8 | RF08 — cabeçalho `Framework v<versão>` sem timestamp, `--check` sai 1 se divergir, fallback para `framework_version` do `registry.yaml` | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -v` | Todos os testes passam | automatizado |
| 9 | RF09 — sumário de `universal.md` (dentro de `build_universal`) e de `guia-tecnico.md` (entre marcadores); `##` em bloco cercado ignorado; marcador ausente sai 1 em `--check` e é inserido sem ele | `python3 -m pytest _framework/tests/test_render_indexes.py -k sumario_universal_e_guia -v` | Todos os testes selecionados passam | automatizado |
| 10 | RF10 — tetos de tamanho por índice (mutação com índice inflado passa a falhar, código 1 com índice, medido e teto) | `python3 -m pytest _framework/tests/test_render_indexes.py -k tetos -v` | Todos os testes selecionados passam | automatizado |
| 11 | RF10 — medição real dos índices do kit contra os tetos, incluindo `bytes(mapa) + bytes(maior seção, exceto §0) <= floor(0.15 * bytes(workflow-rules.yaml))` | `python3 _framework/scripts/render_indexes.py --check` | Saída `✅` por índice, linha `mapa+maior seção = <bytes> (<pct>% do YAML)` com pct ≤ 15, exit 0 | automatizado |
| 12 | RF11 — `render_prompts.py --check` executa também os `--check` dos índices e falha se algum divergir | `python3 _framework/scripts/render_prompts.py --check` | Todos os itens `✅`, exit 0 | automatizado |
| 13 | RF11 — `render_prompts.py` com no máximo 20 linhas adicionadas (todas de import, chamada ou linha de `build_agents`), medido contra origin/main já contendo a SDD-DTF-0042 | `git diff --numstat origin/main -- _framework/scripts/render_prompts.py` | Primeira coluna (adições) ≤ 20 | automatizado |
| 14 | RF11 — CI cobre os índices de SDD e o `registry.md` | `grep -n -e "render_indexes.py sdd docs/sdd --check" -e "generate_registry_md.py docs/sdd --check" .github/workflows/framework-check.yml` | Ao menos 2 ocorrências | automatizado |
| 15 | RF11 — modos de projeto do kit em dia | `python3 _framework/scripts/render_indexes.py sdd docs/sdd --check && python3 _framework/scripts/generate_registry_md.py docs/sdd --check` | Ambos exit 0 | automatizado |
| 16 | RF12 — `AGENTS.md` cita `_framework/INDEX.md` e `_framework/rules/workflow-rules.map.md` | `grep -c "_framework/INDEX.md" AGENTS.md` e `python3 -m pytest _framework/tests/test_render_indexes.py -k agents_aponta_indice -v` | `grep -c` retorna ≥ 1; teste passa; `render_prompts.py --check` sai 0 (critério 12) | automatizado |
| 17 | RF13 — geração idempotente (segunda execução seguida com diff vazio) | `python3 -m pytest _framework/tests/test_render_indexes.py -k idempotente -v` | Todos os testes selecionados passam | automatizado |
| 18 | RF13 — cópia da skill de `render_indexes.py` byte a byte | `python3 -m pytest _framework/tests/test_kit_parity.py -k render_indexes -v` | Todos os testes selecionados passam | automatizado |
| 19 | Contratos (Parte 2) — `LARGEST_SECTION_EXCLUDES == {"0"}` e `SUMMARY_MAX == 100` no módulo | `grep -n -e 'LARGEST_SECTION_EXCLUDES = {"0"}' -e "SUMMARY_MAX = 100" _framework/scripts/render_indexes.py` | 2 ocorrências | automatizado |
| 20 | Escopo — `workflow-rules.yaml` não foi editado por esta SDD | `git diff --stat origin/main -- _framework/rules/workflow-rules.yaml` | Sem saída (baseline: main com a SDD-DTF-0042 já mergeada) | automatizado |
| 21 | Sem regressão nos validadores contra os documentos reais | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | Ambos ✅, 0 problemas | automatizado |
| 22 | Fidelidade à origem (SPEC e RFC existem, status utilizável, url correta) | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0043.md /home/michel/doc-traceability-central/docs/DTF` | `✅ source_docs de SDD-DTF-0043.md conferem com o registry central.` | automatizado |
| 23 | Espelhamento no central: `_framework/` idêntico | `diff -r -x __pycache__ -x .pytest_cache -x .ruff_cache /home/michel/doc-traceability-framework/_framework /home/michel/doc-traceability-central/_framework` | Sem saída (exit 0) | automatizado |
| 24 | Suíte completa sem regressão | `python3 -m pytest _framework/ -q` | Todos os testes passam | automatizado |

## Instruções específicas para a IA implementadora

- **Branch e commit:** implementar em branch nomeada pelo id que originou
  a mudança, `sdd/SDD-DTF-0043-indices-gerados`, criada a partir de main
  DEPOIS de a SDD-DTF-0042 estar mergeada (a branch de documentos
  `docs/sdd-dtf-0042-0045-otimizacao-llm` não é a de implementação).
  Rebasear sobre o YAML na versão 2.3.1 antes de gerar o mapa: linhas e
  bytes do mapa são os do YAML pós-SDD-DTF-0042. Cada commit de
  implementação leva `Refs: SDD-DTF-0043` no corpo. Nunca commit
  direto em main; levar a main por PR.
- **Sessão separada:** implementar na sessão aberta no repositório do kit
  (`doc-traceability-framework`), nunca na sessão do repositório
  central. O espelhamento da task 9 é escrita no central em branch e PR
  próprios do central (push direto em main é bloqueado lá).
- **Verificação:** o status só vai a `implemented` depois de o
  `sdd-verifier` rodar em sessão separada da que implementou, registrando
  comando e saída reais de cada critério na Evidência. Quem escreveu o
  código não verifica.
- **Ordem entre SDDs:** implementada DEPOIS de SDD-DTF-0042 (ambas tocam
  `workflow-rules.yaml` e `render_prompts.py`) e ANTES da SDD de
  SPEC-DTF-0020. O critério 13 (≤ 20 linhas) só faz sentido com a
  SDD-DTF-0042 já em origin/main.
- **Lógica só em `render_indexes.py`.** `render_prompts.py` recebe apenas
  import, chamada de `generate_all` em `main()`, chamada de `build_toc` em
  `build_universal` e a linha de RF12 em `build_agents`; qualquer outra
  linha adicionada ali reprova o critério 13.
- **Assinaturas idênticas às da Parte 2** (nomes, constantes e tipos da
  seção "Produces"): `parse_yaml_sections`, `build_section_map`,
  `check_map_ceiling`, `load_kit_manifest`, `list_kit_files`,
  `build_kit_index`, `extract_sdd_files`, `build_sdd_index`, `build_toc`,
  `inject_toc`, `check_section_refs`, `generate_all`, `main`;
  `render_header` e `main` em `generate_registry_md.py`. Não renomear.
- **Não editar à mão** os arquivos gerados (`_framework/INDEX.md`,
  `workflow-rules.map.md`, `docs/sdd/INDEX.md`, `docs/sdd/registry.md`,
  `universal.md`, `AGENTS.md`, o bloco entre marcadores de
  `guia-tecnico.md`, cópias da skill): rodar os geradores.
- **Não alterar** `workflow-rules.yaml`, `SKILL.md`, procedimentos nem
  prompts (frentes B, C e E). O `kit-index.yaml` é escrito à mão e deve
  ter entrada para cada arquivo novo criado por esta SDD (testes, cópias
  da skill, `INDEX.md`, mapa).
- Sem dependência nova: stdlib e PyYAML. Saída determinística: LF,
  UTF-8, sem timestamp, sempre ordenada.
- Testes obrigatórios: um por critério, com sensor de discriminação
  (mutar o gerador, confirmar que o teste cai, reverter) para RF02, RF03,
  RF05, RF07, RF09 e RF10.
- Não habilitar `docs/sdd/INDEX.md` no CI de EVM, ABSTRACTCLINIC ou
  CIMOCLINIC (não retroativo).

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [x] Todo requisito consolidado acima (RF01 a RF13) tem código
      correspondente (nada da SPEC ficou de fora).
- [x] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", na "Decomposição em tasks" ou em "Instruções
      específicas" — se a implementação tocou um arquivo não listado
      aqui, ou é escopo que faltou registrar na SDD (atualize-a) ou é
      scope creep a remover antes do merge.
- [x] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado ("já que estava ali").
- [x] `workflow-rules.yaml` intocado e `render_prompts.py` com ≤ 20 linhas
      adicionadas contra origin/main.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou —
quem escreveu o código tem o resultado como conclusão desejada. Para cada
critério da tabela acima: comando rodado de fato nesta sessão e saída real,
nunca "deve passar" nem resultado de memória. Verificação independente rodada em 2026-09-25 (rodada 1), veredito **PASS**.

**Verificador independente:** sim

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Teste que passa com a implementação quebrada é
ruído verde. Critério sem teste automatizado: escreva "sem teste", nunca
marque como verificado por leitura de código. Coluna "Assertion
(file:line)": caminho e linha exatos da asserção que resolve o critério;
critério `manual` ou `n/a` usa `n/a`. Coluna "Perfil usado": repete o
"Perfil esperado" do critério ou declara divergência com justificativa
entre parênteses.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
| 1 | `python3 -m pytest _framework/tests/test_render_indexes.py -k kit_index_uma_linha_por_arquivo -v` | 1 passed, 25 deselected | n/a (RF01 sem sensor exigido) | sim | _framework/tests/test_render_indexes.py:test_kit_index_uma_linha_por_arquivo | automatizado |
| 2 | `python3 -m pytest _framework/tests/test_render_indexes.py -k manifesto_orfao -v` | 6 passed, 20 deselected | sim: raise CoverageError desativado, 3 testes falharam, revertido | sim | _framework/tests/test_render_indexes.py:test_manifesto_orfao_* | automatizado |
| 3 | `python3 -m pytest _framework/tests/test_render_indexes.py -k mapa_ids_batem_com_banners -v` | 5 passed, 21 deselected | sim: checagem de banner duplicado desativada, 1 falhou, revertido | sim | _framework/tests/test_render_indexes.py:test_mapa_ids_batem_com_banners* | automatizado |
| 4 | `python3 -m pytest _framework/tests/test_render_indexes.py -k resumo_primeira_frase -v` | 1 passed, 25 deselected | n/a | sim | _framework/tests/test_render_indexes.py:test_resumo_primeira_frase | automatizado |
| 5 | `python3 -m pytest _framework/tests/test_render_indexes.py -k secao_citada_inexistente -v` | 2 passed, 24 deselected | sim: comparacao de id desativada, 1 falhou, revertido | sim | _framework/tests/test_render_indexes.py:test_secao_citada_inexistente | automatizado |
| 6 | `python3 -m pytest _framework/tests/test_render_indexes.py -k sdd_index_campos -v` | 2 passed, 24 deselected | n/a | sim | _framework/tests/test_render_indexes.py:test_sdd_index_campos* | automatizado |
| 7 | `python3 -m pytest _framework/tests/test_render_indexes.py -k sdd_sem_secao_arquivos -v` | 2 passed, 24 deselected | sim: leitura da coluna da tabela de tasks desativada, 2 falharam, revertido | sim | _framework/tests/test_render_indexes.py:test_sdd_sem_secao_arquivos* | automatizado |
| 8 | `python3 -m pytest _framework/scripts/tests/test_generate_registry_md.py -v` | 4 passed (header sem timestamp, versao corrente, fallback registry.yaml, --check) | n/a | sim | _framework/scripts/tests/test_generate_registry_md.py:test_check_sai_1_se_divergir_e_0_se_em_dia | automatizado |
| 9 | `python3 -m pytest _framework/tests/test_render_indexes.py -k sumario_universal_e_guia -v` | 2 passed, 24 deselected | sim: filtro de bloco cercado desativado, 1 falhou, revertido | sim | _framework/tests/test_render_indexes.py:test_sumario_universal_e_guia* | automatizado |
| 10 | `python3 -m pytest _framework/tests/test_render_indexes.py -k tetos -v` | 2 passed, 24 deselected | sim: teto do mapa e teto total do INDEX desativados um de cada vez, teste falhou nas duas, revertido | sim | _framework/tests/test_render_indexes.py:test_tetos | automatizado |
| 11 | `python3 _framework/scripts/render_indexes.py --check` | ✅ por indice (guia, mapa, INDEX do kit, docs/sdd/INDEX); linha `mapa+maior seção = 12520 (13.7% do YAML)`; exit 0 | n/a | sim | _framework/tests/test_render_indexes.py:test_tetos_medicao_real | automatizado |
| 12 | `python3 _framework/scripts/render_prompts.py --check` | 34 itens ✅, 0 ❌, exit 0 | n/a | sim | n/a | automatizado |
| 13 | `git diff --numstat origin/main -- _framework/scripts/render_prompts.py` | `6	1	_framework/scripts/render_prompts.py` (6 adições) | n/a | sim | n/a | automatizado |
| 14 | `grep -n -e "render_indexes.py sdd docs/sdd --check" -e "generate_registry_md.py docs/sdd --check" .github/workflows/framework-check.yml` | linhas 75 e 76 (2 ocorrências) | n/a | sim | n/a | automatizado |
| 15 | `python3 _framework/scripts/render_indexes.py sdd docs/sdd --check && python3 _framework/scripts/generate_registry_md.py docs/sdd --check` | ✅ docs/sdd/registry.md: em dia; exit 0 nos dois | n/a | sim | n/a | automatizado |
| 16 | `grep -c "_framework/INDEX.md" AGENTS.md` e `python3 -m pytest _framework/tests/test_render_indexes.py -k agents_aponta_indice -v` | grep -c retornou 1; 1 passed, 25 deselected; render_prompts.py --check exit 0 (criterio 12) | n/a | sim | _framework/tests/test_render_indexes.py:test_agents_aponta_indice | automatizado |
| 17 | `python3 -m pytest _framework/tests/test_render_indexes.py -k idempotente -v` | 1 passed, 25 deselected | n/a | sim | _framework/tests/test_render_indexes.py:test_idempotente | automatizado |
| 18 | `python3 -m pytest _framework/tests/test_kit_parity.py -k render_indexes -v` | 1 passed, 2 deselected | n/a | sim | _framework/tests/test_kit_parity.py:test_render_indexes_paridade | automatizado |
| 19 | `grep -n -e 'LARGEST_SECTION_EXCLUDES = {"0"}' -e "SUMMARY_MAX = 100" _framework/scripts/render_indexes.py` | linhas 35 e 36 (2 ocorrências) | n/a | sim | n/a | automatizado |
| 20 | `git diff --stat origin/main -- _framework/rules/workflow-rules.yaml` | sem saída | n/a | sim | n/a | automatizado |
| 21 | `python3 _framework/scripts/validate_doc.py docs/sdd && python3 _framework/scripts/validate_state.py docs/sdd` | ✅ 44 documentos no gate de qualidade; ✅ 44 verificados, 0 problemas (exigiu framework_lib.iter_documents ignorar INDEX.md, escopo registrado na task 5) | n/a | sim | n/a | automatizado |
| 22 | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0043.md /home/michel/doc-traceability-central/docs/DTF` | ✅ source_docs de SDD-DTF-0043.md conferem com o registry central. | n/a | sim | n/a | automatizado |
| 23 | `diff -r -x __pycache__ -x .pytest_cache -x .ruff_cache -x .mypy_cache /home/michel/dtf-wt-0043/_framework /home/michel/dtf-central-wt-0043/_framework` | sem saída, exit 0 (reexecutado pelo verificador; o checkout /home/michel/doc-traceability-central está em branch antiga docs/spec-dtf-0020-bundle-gerado-v2 e ainda em v2.3.0, então o alvo válido é o worktree do central com o espelho, PR #141 aberto e não mergeado) | n/a | sim (contra o worktree, não contra o checkout principal do central) | n/a | automatizado (divergência: alvo do diff é o worktree do central) |
| 24 | `python3 -m pytest _framework/ -q` | 217 passed | n/a | sim | n/a | automatizado |
| 25 | Fidelidade à origem: `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0043.md /home/michel/dtf-central-wt-0043/docs/DTF`; RF01 a RF13 da SPEC-DTF-0016 conferidos contra a SDD | ✅ source_docs de SDD-DTF-0043.md conferem com o registry central, exit 0; RF01 a RF13 presentes na SDD sem relaxamento de EARS | n/a | sim | n/a | automatizado |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0016 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0016.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
