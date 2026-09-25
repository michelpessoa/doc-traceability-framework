---
id: SDD-DTF-0049
type: SDD
title: "Título completo e resumo útil no mapa de seções e linhas específicas no INDEX do kit"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0043]
source_docs:
  - id: "SPEC-DTF-0024"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0024.md"
  - id: "SPEC-DTF-0022"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0022.md"
  - id: "SPEC-DTF-0016"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0016.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Compilada da SPEC-DTF-0022 (approved, sizing medium), que complementa a SPEC-DTF-0016 (approved): nos RFs que a 0022 marca como alterados (RF02, RF03 e RF04 da 0016) a SPEC-DTF-0022 prevalece; nos demais a 0016 vale sem mudança. Objetivo herdado da RFC-DTF-0008. Ler Requisitos consolidados, Especificação técnica consolidada, Decomposição em tasks e Critérios de aceite antes de tocar em render_indexes.py. Implementar só na sessão aberta no repositório do kit, em branch sdd/SDD-DTF-0049-mapa-index-especificos dentro de worktree próprio, nunca em main; cada commit com Refs: SDD-DTF-0049; verificação por sdd-verifier em sessão separada. Não alterar workflow-rules.yaml, render_prompts.py nem framework.version."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, indice, mapa, resumo, errata]
---

# Título completo e resumo útil no mapa de seções e linhas específicas no INDEX do kit

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar. Deve ser autocontido, mas
> sempre rastreável a SPEC-DTF-0022, SPEC-DTF-0016 e RFC-DTF-0008 via
> `source_docs` (id + url, já que os documentos de origem estão no
> repositório central).

## Resumo executivo

A SDD-DTF-0043 implementou os índices da SPEC-DTF-0016 e todos os tetos
passam, mas a avaliação de 2026-09-25 mostrou que os índices ajudam pouco a
escolher um alvo sem abri-lo. Medido na `main` do kit (commit `1fe4f68`): no
mapa `_framework/rules/workflow-rules.map.md`, 9 das 22 linhas repetem o
título da seção na coluna Resumo, 16 das 22 têm o título cortado com `…` e 5
resumos terminam no meio de uma palavra; no `_framework/INDEX.md`, 98 das 110
linhas dividem o mesmo texto de "O que é" com outra linha (27 textos
distintos). A SPEC-DTF-0022 (errata da 0016) corrige isso: esta SDD troca as
regras de título, de fonte do resumo e de corte em `render_indexes.py`, ganha
a chave opcional `map_summaries` e a expansão `{name}`/`{stem}` em
`rules/kit-index.yaml`, e reescreve o manifesto com uma descrição própria por
arquivo. Objetivo herdado da RFC-DTF-0008: qualquer LLM chega a qualquer
seção ou arquivo do kit lendo um índice pequeno, sem ler o alvo inteiro.
Todos os tetos da SPEC-DTF-0016 continuam valendo.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — sizing `medium` na SPEC-DTF-0022: nenhum critério de
`decision_gates.rfc_to_adr` se aplica (mudança de regra de renderização de
dois índices gerados, stdlib e PyYAML).

Relação entre as duas SPECs, decidida na SPEC-DTF-0022: a SPEC-DTF-0016
continua `approved` e a 0022 a complementa; nenhuma é `superseded`. Onde a
tabela abaixo diz "alterado", a SPEC-DTF-0022 prevalece; onde diz
"permanece", vale a 0016.

| RF da SPEC-DTF-0016 | Situação | O que muda ou permanece |
|---|---|---|
| RF01 (`INDEX.md`: colunas e faixas de tamanho) | permanece | Só o texto vindo do manifesto muda (RF05 desta SDD); faixas `<2 KB`, `2-8 KB`, `8-32 KB`, `>32 KB` e uma linha por arquivo não mudam |
| RF02 (`kit-index.yaml`) | alterado por RF04 e RF05 | Cobertura e schema de `entries` (exatamente `path`, `what`, `when`; primeira que casa vence) permanecem; ganha a chave de topo opcional `map_summaries`; `what` e `when` aceitam `{name}` e `{stem}`; a nota "<= 60 caracteres" deixa de valer e o limite passa a ser só o teto de 200 bytes por linha |
| RF03 (mapa) | alterado por RF01 e RF02 | Ids `§N`, chaves, linha inicial, bytes, `§0` permanecem; a coluna Seção passa a ser o título completo e limpo de RF01; o Resumo segue a cadeia de RF02 |
| RF04 (resumo) | alterado por RF02 e RF03 | `SUMMARY_MAX` (100) permanece; a fonte passa a ser a cadeia de seis fontes e o corte passa a ser em fronteira de palavra |
| RF05, RF06, RF07, RF08, RF09, RF12 | permanecem | Nenhuma mudança |
| RF10 (tetos) | permanece, reafirmado por RF06 | Nenhum valor de `CEILINGS` nem de `MAP_FRACTION` muda |
| RF11 (`--check`; `render_prompts.py` só fiação) | permanece | `render_prompts.py` não muda |
| RF13 (idempotência e paridade da cópia da skill) | permanece, reafirmado por RF07 | Cópia da skill idêntica byte a byte |

Caso de borda da 0016 alterado: "Banner de título em várias linhas (§3c,
§12): título = primeira linha do banner" passa a incluir as linhas de
continuação no título (RF01). Os demais casos de borda da 0016 permanecem.

Versão e changelog (decisão da SPEC-DTF-0022): `framework.version` fica em
`2.3.1` e nenhuma entrada de changelog é criada; esta SDD não edita
`_framework/rules/workflow-rules.yaml`.

## Requisitos consolidados

Consolidado da Parte 1 da SPEC-DTF-0022. Caminhos relativos à raiz do kit
`doc-traceability-framework`; os mesmos valem no central (RF07).
Comportamento de referência: `_first_sentence`, `_section_summary`,
`_section_row` e `build_kit_index` em `_framework/scripts/render_indexes.py`
(commit `1fe4f68`) e `_framework/rules/kit-index.yaml` (86 linhas, 27
entradas).

| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |
|---|---|---|---|
| RF01 | Altera RF03 da 0016 (título). O título da linha do mapa deve ser completo e limpo até o fim de uma expressão: o título do banner com as linhas de continuação juntas, sem cauda descritiva após o travessão e sem parêntese quando ele estourar 70 caracteres. | Quando `render_indexes.py` gerar o mapa, o sistema deve montar o título juntando a linha `# N. TÍTULO` com as linhas de comentário contíguas que a seguem antes da linha `#` vazia ou da fence, colapsar espaços, descartar tudo a partir do primeiro ` — ` (travessão cercado por espaços) e, se o resultado passar de `TITLE_MAX` (70) caracteres, remover os grupos entre parênteses; se ainda passar, o sistema deve cortar em fronteira de palavra e terminar com `…`. Os dois-pontos do título são mantidos. | `_framework/scripts/render_indexes.py` |
| RF02 | Altera RF03 e RF04 da 0016 (resumo). O Resumo deve ajudar a escolher a seção: é a primeira frase completa da melhor fonte disponível e só é o título quando nenhuma outra fonte existe. | Quando o sistema calcular o Resumo de uma seção com id diferente de `0`, o sistema deve usar a primeira fonte não vazia da cadeia: (1) parágrafo do corpo do banner (após a `#` vazia que segue o título); (2) primeiro parágrafo de comentário após a fence de fechamento; (3) primeiro valor textual não vazio, na ordem `description`, `purpose`, `instructions`, `approach`, `applies_when`, entre os filhos diretos da primeira chave de topo da seção; (4) texto de `map_summaries` (RF04) para o id; (5) cauda do título após ` — `; (6) o título limpo de RF01. De cada fonte o sistema deve extrair a primeira frase completa: tirar o rótulo inicial `Motivação` ou `Origem` (com ou sem parêntese) seguido de dois-pontos, terminar em `.`, `!` ou `?` seguido de espaço e maiúscula, aspas, crase ou parêntese (ou no fim do parágrafo), remover `:`, `;` e `,` finais e pôr a primeira letra em maiúscula. | `_framework/scripts/render_indexes.py` |
| RF03 | Altera RF04 da 0016 (corte). Todo corte de texto do mapa deve ocorrer em fronteira de palavra, sem conectivo pendurado e sem estourar o limite; `SUMMARY_MAX` (100) permanece. | Quando um Resumo tiver mais de `SUMMARY_MAX` (100) caracteres, o título mais de `TITLE_MAX` (70), ou uma linha do mapa passar de 180 bytes, o sistema deve cortar por `_cut_words(text, limit)`, que devolve no máximo `limit` caracteres contando o `…`, recua até o último espaço, descarta ao fim as palavras de `DANGLING` e as terminadas em `(`, `:`, `,` ou `;`, e acrescenta `…`. Para caber em 180 bytes o sistema deve encurtar, nesta ordem, as chaves (comportamento já existente), o Resumo até `SUMMARY_MIN` (30) caracteres e só então o título (mínimo 20 caracteres). | `_framework/scripts/render_indexes.py` |
| RF04 | Altera RF02 da 0016 (schema do manifesto). Seção sem nenhuma fonte automática de RF02 pode receber resumo escrito à mão em `kit-index.yaml`, sem editar `workflow-rules.yaml`. | Onde `_framework/rules/kit-index.yaml` tiver a chave de topo `map_summaries` (mapa de id de seção, como texto, para frase), o sistema deve usá-la na fonte (4) de RF02, depois de esgotadas as fontes (1) a (3), de modo que fonte automática vence texto à mão. Se um id de `map_summaries` não existir no mapa, ou o valor for vazio ou não textual, então o sistema deve sair com código 2 citando o id. `load_kit_manifest` continua devolvendo só a lista `entries`. | `_framework/scripts/render_indexes.py`, `_framework/rules/kit-index.yaml` |
| RF05 | Altera RF02 da 0016 (texto das entradas). Cada linha do INDEX do kit diz o que o arquivo faz: descrição própria por arquivo, com o nome dele, e famílias de cópia espelhada diferenciadas pelo nome. | Onde `what` ou `when` de uma entrada contiver `{name}` (nome do arquivo com extensão) ou `{stem}` (sem extensão), o sistema deve substituí-los pelo valor de cada arquivo casado ao montar a linha, sem outra interpretação de chaves. O manifesto deve ter entrada individual (caminho exato) para cada arquivo que não é cópia espelhada, com `what` de pelo menos 4 palavras tirado da leitura do arquivo (docstring, título ou descrição), e entrada com glob e `{name}` para cada família de cópia gerada. Quando `render_indexes.py` gerar o INDEX, o sistema não deve produzir duas linhas com o mesmo texto de "O que é". | `_framework/scripts/render_indexes.py`, `_framework/rules/kit-index.yaml` |
| RF06 | Reafirma RF10, RF11 e RF13 da 0016. Nada do contrato externo dos geradores piora: tetos, códigos de saída, determinismo e o conteúdo de `workflow-rules.yaml` e `render_prompts.py`. | Quando `render_indexes.py --check` ou `render_prompts.py --check` rodar, o sistema deve manter os valores de `CEILINGS` e `MAP_FRACTION` (mapa mais maior seção, exceto `§0`, ≤ 15% do bytes do YAML; linha do mapa ≤ 180 bytes; cabeçalho ≤ 400; INDEX ≤ 200 bytes por linha e ≤ 24576 no total), os códigos 0, 1 e 2, a saída sem timestamp e a segunda geração seguida com diff vazio; e o sistema não deve modificar `_framework/rules/workflow-rules.yaml`, `_framework/scripts/render_prompts.py` nem `framework.version`. | `_framework/scripts/render_indexes.py`, `_framework/tests/test_render_indexes.py` |
| RF07 | Reafirma RF13 da 0016 e a regra de espelho do kit. Os gerados, a cópia da skill e o espelho do central refletem as regras novas. | Quando a implementação estiver concluída, o sistema deve ter `_framework/INDEX.md`, `_framework/rules/workflow-rules.map.md` e `docs/sdd/INDEX.md` regenerados por `render_prompts.py`, a cópia de `render_indexes.py` na skill idêntica byte a byte, e a árvore `_framework/` do central idêntica à do kit. | `_framework/INDEX.md`, `_framework/rules/workflow-rules.map.md`, `docs/sdd/INDEX.md`, `_framework/skills/doc-traceability-framework/scripts/render_indexes.py` |

Tetos (permanecem; RF10 da SPEC-DTF-0016, reafirmados por RF06):

| Índice | Teto verificável | Medido na `main` (1fe4f68) |
|---|---|---|
| Mapa de seções | `bytes(mapa) + bytes(maior seção, exceto §0) <= floor(0.15 * bytes(YAML))` com `LARGEST_SECTION_EXCLUDES = {"0"}`; cada linha ≤ 180 bytes; cabeçalho ≤ 400 bytes | 3787 + 8733 (§12) = 12520 bytes, 13,7% de 91181; teto 13677; maior linha 180 bytes |
| `_framework/INDEX.md` | ≤ 200 bytes por linha e ≤ 24576 no total | 14934 bytes; maior linha 177 bytes |

Evidência de viabilidade (da SPEC-DTF-0022, protótipo descartável fora do
repositório, não reexecutado): com RF01 a RF04 aplicados ao YAML atual, mapa
mais maior seção = 12631 bytes (13,8% de 91181; sobra de 1046 bytes até o
teto de 13677), 22 linhas todas ≤ 180 bytes, títulos ≤ 70 caracteres exceto
o §12 (82 caracteres depois de tirar o parêntese; o segundo maior, §16, tem
66) e nenhum resumo cortado no meio de palavra. Por isso a meta de títulos
terminados em `…` é ≤ 1, e não 0. Limite conhecido: nas seções 13 a 19 o
Resumo fica com 35 a 60 caracteres, porque o teto de 180 bytes por linha,
fixado pela 0016, deixa essa folga depois do título completo e da coluna
Chaves; não é falha de RF03.

Casos de borda / condições de erro (SPEC-DTF-0022):

| Caso | RF relacionado | Comportamento esperado |
|---|---|---|
| Seção sem descrição em nenhuma fonte e sem `map_summaries` | RF02 | Resumo = cauda do título após ` — ` se houver, senão o título limpo; não é erro (o teste de fixture "SEÇÃO SEM PARÁGRAFO" segue válido) |
| Título com dois-pontos (gates, §17, §19) | RF01 | Dois-pontos mantido; o título sai inteiro se couber em 70 |
| Título com travessão (§3b, §3c, §8) | RF01, RF02 | Título só com a parte antes de ` — `; a cauda vira fonte (5) do Resumo quando não há fonte melhor |
| Banner com título em várias linhas (§3c, §12) | RF01 | Linhas de continuação até a `#` vazia ou a fence entram no título; o que vem depois da `#` vazia é o corpo do banner (fonte 1). Substitui o caso de borda equivalente da 0016 |
| Bloco de comentário vazio (só linhas `#`) | RF02 | Bloco ignorado como fonte; segue para a próxima fonte da cadeia |
| Parágrafo sem ponto final (termina em `:`, como §1) | RF02 | Vale o parágrafo inteiro, sem o `:` final |
| Primeira frase maior que 100 caracteres | RF03 | Corte em fronteira de palavra com `…`, sem conectivo pendurado |
| Texto de uma palavra só maior que o limite | RF03 | Corte duro em `limit - 1` caracteres com `…` (único caso sem fronteira) |
| Texto que cabe no limite | RF03 | Devolvido inteiro, sem `…`, mesmo terminando em conectivo (só o corte descarta conectivo) |
| Linha do mapa ainda acima de 180 bytes depois de encurtar chaves, Resumo (piso 30) e título (piso 20) | RF03, RF06 | Não corta abaixo dos pisos; `check_map_ceiling` reprova com código 1 (comportamento da 0016) |
| `map_summaries` com id inexistente, vazio ou não textual | RF04 | Código 2 citando o id; nada é escrito |
| Seção nova sem descrição e sem entrada em `map_summaries` | RF02, RF04 | Resumo cai para o título; o teste de qualidade do mapa real acusa a linha repetida, sem quebrar `--check` |
| Valor da primeira chave de topo que não é mapeamento (lista ou escalar) | RF02 | Fonte (3) ignorada; segue para a fonte (4) |
| Arquivo novo no kit sem entrada em `kit-index.yaml` | RF05 | Igual à 0016: `--check` sai 1 listando o caminho; sem `--check`, sai 2 e não escreve |
| Entrada com `{name}` fora de família espelhada | RF05 | Permitido; a linha sai com o nome do arquivo; o teste de textos distintos reprova duas linhas iguais |
| Chave desconhecida entre chaves (`{outro}`) em `what` ou `when` | RF05 | Mantida como texto literal; só `{name}` e `{stem}` são substituídos |
| Linha do INDEX acima de 200 bytes | RF06 | Igual à 0016: `check_kit_ceiling` reprova, código 1 |
| Outra SPEC altera o YAML antes ou depois desta (SPEC-DTF-0021) | RF06, RF07 | Ver "Coordenação com a SPEC-DTF-0021"; o teto do mapa é recalculado pelo `--check` sobre o YAML vigente |

Requisitos não funcionais: saída determinística (sem timestamp, ordem
estável, LF, UTF-8); sem dependência nova (stdlib e PyYAML); parâmetros novos
nas funções públicas existentes só com valor padrão, de modo que os testes
atuais que chamam `parse_yaml_sections(text)` continuam válidos; nenhuma
flag de CLI nova.

Requisitos transversais (sweep): autorização e falha de dependência externa
não se aplicam (scripts locais sobre arquivos do próprio repositório);
concorrência (dois repositórios e duas SPECs regeneram os mesmos gerados) é
coberta por RF07, pelo `diff -r` kit x central e pela regra de quem mergeia
depois regenerar; idempotência, observabilidade (`✅`/`❌` por índice, linha
`mapa+maior seção = <bytes> (<pct>% do YAML)`, códigos 0/1/2) e limites de
volume são cobertos por RF06; validação de entrada (id e valor de
`map_summaries`, chaves desconhecidas literais, cobertura do manifesto) por
RF04 e RF05.

Fora de escopo: editar ou marcar `superseded` a SPEC-DTF-0016; qualquer
edição de `_framework/rules/workflow-rules.yaml` (inclusive bloco
`framework:` e changelog, que é da SPEC-DTF-0021); alterar
`_framework/scripts/render_prompts.py`, `AGENTS.md`, `SKILL.md`,
procedimentos, prompts e templates; corrigir a faixa de tamanho do INDEX ou
a coluna Bytes do mapa; trocar citações soltas "seção N" pelos ids `§N`
(frente C da RFC-DTF-0008); versão do framework e changelog.

## Especificação técnica consolidada

Consolidado da Parte 2 da SPEC-DTF-0022. Três mudanças em
`_framework/scripts/render_indexes.py` e uma no manifesto:

1. Título e resumo do mapa: funções novas `_cut_words`, `_sentence`,
   `_clean_title` e `_banner_parts`; `_section_summary` passa a percorrer a
   cadeia de RF02; `parse_yaml_sections` lê o YAML uma vez com
   `yaml.safe_load` para alimentar a fonte (3) e aceita `overrides`;
   `_section_row` usa `_cut_words` na ordem de encurtamento de RF03.
2. `map_summaries`: `load_map_summaries` lê e valida a chave de topo opcional
   de `kit-index.yaml`; `generate_all` passa o resultado a
   `parse_yaml_sections` e `build_section_map`.
3. INDEX: `build_kit_index` expande `{name}` e `{stem}`; `kit-index.yaml` é
   reescrito com uma entrada individual por arquivo não espelhado e globs com
   `{name}` para as quatro famílias de cópia da skill.

Arquivos tocados (produto), todos no kit `doc-traceability-framework`:

- `_framework/scripts/render_indexes.py`: RF01 a RF05.
- `_framework/rules/kit-index.yaml`: RF04 (`map_summaries`) e RF05 (entradas).
- `_framework/tests/test_render_indexes.py`: testes de RF01 a RF06 e a
  correção do teste que fixa "título é a primeira linha" (linha 167).
- Gerados: `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md`,
  `docs/sdd/INDEX.md`, cópia bundlada
  `_framework/skills/doc-traceability-framework/scripts/render_indexes.py`.
- Espelho no central (task 6), caminhos relativos a
  `/home/michel/doc-traceability-central/`.

**Consumes** (já existe, não mudar): `framework_lib.find_rules_file`,
`framework_lib.read_frontmatter`, `framework_lib.split_table_row`;
`render_prompts.sync_copies` (copia o módulo para a skill);
`render_indexes.CoverageError`, `_glob_re`, `list_kit_files`, `_bucket`,
`check_map_ceiling`, `check_section_refs`, `check_kit_ceiling`,
`load_kit_manifest`; constantes `BANNER_RE`, `FENCE_RE`, `SUMMARY_MAX`,
`CEILINGS`, `MAP_FRACTION`, `LARGEST_SECTION_EXCLUDES`. O `Section`
(dataclass `frozen`, campos inalterados) passa a guardar em `title` o título
limpo de RF01.

**Produces**, todos em `_framework/scripts/render_indexes.py`:

```python
TITLE_MAX = 70          # caracteres do título da linha do mapa (RF01)
SUMMARY_MIN = 30        # piso do Resumo ao encurtar a linha (RF03)
LABEL_RE = re.compile(r"^(?:Motivação|Origem)(?:\s*\([^)]*\))?\s*:\s*")   # rótulo removido (RF02)
SCALAR_KEYS = ("description", "purpose", "instructions", "approach", "applies_when")   # fonte (3)
DANGLING = {"a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na",
            "nos", "nas", "por", "para", "com", "sem", "ao", "aos", "e", "ou", "que", "como", "se",
            "->", "+"}   # conectivos que não podem terminar um corte (RF03)

def _cut_words(text: str, limit: int) -> str: ...            # RF03
def _sentence(text: str, limit: int) -> str: ...             # RF02: primeira frase completa + _cut_words
def _clean_title(raw: str) -> str: ...                       # RF01
def _banner_parts(lines: list[str], title_idx: int, hi: int) -> tuple[str, str, int]: ...
    # (continuação do título, parágrafo do corpo do banner, índice logo após a fence de fechamento)
def _section_summary(lines: list[str], title_idx: int, hi: int, first_key_value=None,
                     override: str = "", tail: str = "") -> str: ...   # RF02, fontes 1 a 5; "" se nenhuma
def parse_yaml_sections(text: str, overrides: dict[str, str] | None = None) -> list[Section]: ...   # RF01, RF02; aplica a fonte 6
def load_map_summaries(path: Path) -> dict[str, str]: ...    # RF04; SystemExit (código 2) em erro
def build_section_map(yaml_path: Path, overrides: dict[str, str] | None = None) -> str: ...   # RF01 a RF04
def build_kit_index(root: Path, manifest: list[dict]) -> str: ...   # RF05: expande {name} e {stem}
```

`_section_summary` mantém os três primeiros parâmetros posicionais atuais;
os novos têm valor padrão. `generate_all` carrega `map_summaries` de
`rules/kit-index.yaml` e passa a `parse_yaml_sections` e `build_section_map`;
`check_map_ceiling` e `check_section_refs` seguem recebendo a lista de
seções sem `overrides` (só usam ids e bytes). `load_kit_manifest` mantém
assinatura e retorno (`list[dict]` de `entries`) e continua exigindo
exatamente `path`, `what` e `when` em cada entrada; a chave de topo
`map_summaries` não é entrada e não afeta essa validação.

Contratos por regra:

- **`_cut_words(text, limit)` (RF03).** Se `len(text) <= limit`, devolve
  `text` inalterado. Senão toma `text[:limit - 1]`; se o caractere seguinte
  não é espaço, recua até o último espaço; descarta ao fim palavras em
  `DANGLING` (comparação em minúsculas) ou terminadas em `(`, `:`, `,`, `;`;
  acrescenta `…`. Se não sobrar palavra (ou não houver espaço), corte duro em
  `limit - 1` caracteres mais `…`. O retorno tem no máximo `limit`
  caracteres. O laço de largura da linha chama `_cut_words` com limite
  decrescente de 6 em 6 caracteres sobre o texto já sem o `…` anterior, para
  nunca cortar duas vezes no mesmo lugar.
- **`_sentence(text, limit)` (RF02).** Colapsa espaços, remove `LABEL_RE`,
  termina a frase em `.`, `!` ou `?` seguidos de espaço e de maiúscula,
  aspas, crase ou parêntese (ou no fim do texto), tira `:`, `;` e `,` finais,
  põe a primeira letra em maiúscula e aplica `_cut_words(., limit)`.
- **`_clean_title(raw)` (RF01).** Colapsa espaços; corta em ` — `; se
  `len > TITLE_MAX`, remove grupos `\s*\([^)]*\)`; se ainda passar,
  `_cut_words(., TITLE_MAX)`.
- **Fonte por chave (RF02).** A "primeira chave de topo" é `Section.keys[0]`;
  o valor vem de `yaml.safe_load` do texto inteiro, lido uma vez em
  `parse_yaml_sections`. A fonte (3) só vale se o valor for mapeamento; para
  cada nome de `SCALAR_KEYS`, na ordem, vale o primeiro valor `str` não
  vazio.
- **Títulos esperados no YAML atual (RF01).** §3b `TIPOS LEGADOS`; §3c
  `ARTEFATOS OPERACIONAIS`; §6 `CICLO DE VIDA DE STATUS PADRÃO`; §8
  `METADADOS (FRONT-MATTER)`; §13 `GATE OBRIGATÓRIO: NENHUMA IMPLEMENTAÇÃO
  PULA SPEC/SDD`; §16 `GATE OBRIGATÓRIO: VERIFICAÇÃO DE ESCOPO ANTES DE SDD
  "IMPLEMENTED"`; §12 (o único que ainda estoura 70) `CAPACIDADES QUE
  QUALQUER FERRAMENTA DE IA DEVE OFERECER AO EXECUTAR…`.
- **`map_summaries` (RF04).** Chave de topo opcional de `kit-index.yaml`,
  mapa de id (string, ex.: `"12"`) para frase de 30 a 100 caracteres. Semente
  para as seções sem fonte automática no YAML atual: `"2"` (tipos de
  documento), `"6"` (ciclo de vida de status), `"7"` (esquema de id), `"9"`
  (registry) e `"12"` (capacidades); cada frase é escrita lendo a seção.
- **INDEX (RF05).** Famílias de cópia com `{name}`:
  `skills/doc-traceability-framework/scripts/*`,
  `skills/doc-traceability-framework/templates/*`,
  `skills/doc-traceability-framework/prompts/*`,
  `skills/doc-traceability-framework/references/*`; forma de exemplo:
  `what: "Cópia gerada de scripts/{name} para a skill"`, `when: "Nunca à
  mão; regenere com render_prompts.py"`. Entrada individual (caminho exato,
  antes das globs, já que a primeira que casa vence) para cada script de
  `scripts/`, cada teste de `scripts/tests/` e `tests/`, cada template, cada
  fixture, cada procedimento, cada prompt e cada `SKILL.md`. O `what` nomeia
  o que o arquivo faz (ex.: `scripts/lessons_check.py` conta a recorrência do
  critério de 2 projetos das lições; `scripts/selftest.py` muta os
  validadores do kit e exige que os testes falhem) e o `when` diz em que
  tarefa abri-lo. Meta por linha: ≤ 200 bytes incluindo caminho e faixa.

Schema de `kit-index.yaml` depois desta SDD:

```yaml
entries:                     # exatamente path, what, when; primeira entrada que casa vence
  - path: "scripts/lessons_check.py"
    what: "..."              # texto próprio; aceita {name} e {stem}
    when: "..."
map_summaries:               # opcional (RF04): id de seção -> frase de 30 a 100 caracteres
  "12": "..."
```

(as reticências acima só ilustram a forma; o arquivo real não tem texto
provisório.)

Tratamento de erro por contrato:

| Caso | RF relacionado | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| `map_summaries` com id inexistente, vazio ou não textual | RF04 | `SystemExit(2)` citando o id | `load_map_summaries`, `parse_yaml_sections` |
| `map_summaries` que não é mapeamento | RF04 | `SystemExit(2)` | `load_map_summaries` |
| Nenhuma fonte de RF02 disponível | RF02 | `_section_summary` devolve `""`; fonte (6) aplicada | `parse_yaml_sections` |
| Texto de uma palavra acima do limite | RF03 | Corte duro com `…` | `_cut_words` |
| Linha do mapa acima de 180 bytes nos pisos | RF03, RF06 | Código 1 com nome, medido e teto | `check_map_ceiling`, `generate_all` |
| Título acima de 70 mesmo sem parêntese | RF01 | `_cut_words(., TITLE_MAX)` | `_clean_title` |
| Arquivo sem entrada / entrada sem arquivo | RF05 | Código 1 em `--check`, 2 fora dele | `build_kit_index`, `generate_all` |
| Linha do INDEX acima de 200 bytes | RF05, RF06 | Código 1 | `check_kit_ceiling` |
| Chave `{outro}` em `what` ou `when` | RF05 | Texto literal | `build_kit_index` |
| Geração seguida com diff | RF06 | Teste de idempotência falha | `test_render_indexes.py` |
| Cópia da skill ou central divergente | RF07 | Teste de paridade e `diff -r` falham | `test_kit_parity.py`, critério A13 |

**Estratégia de teste** (`pytest` roda de `/home/michel/doc-traceability-framework`;
`-k` refere-se a `_framework/tests/test_render_indexes.py`; sem mock):

| RF-ID / contrato | Tipo de teste | Arquivo de teste |
|---|---|---|
| RF01, `-k titulo_completo` | Unitário sobre YAML fixture (multilinha, travessão, parêntese acima e abaixo de 70) | `_framework/tests/test_render_indexes.py` |
| RF02, `-k resumo_cadeia` | Unitário por fonte (1 a 6), rótulo `Motivação`, bloco de comentário vazio | `_framework/tests/test_render_indexes.py` |
| RF03, `-k corte_fronteira_palavra` | Unitário de `_cut_words` (limite, conectivo pendurado, palavra única) e ordem de encurtamento da linha | `_framework/tests/test_render_indexes.py` |
| RF04, `-k map_summaries` | Unitário (fonte automática vence; id inexistente, vazio, não textual saem com código 2) | `_framework/tests/test_render_indexes.py` |
| RF05, `-k kit_index_o_que_e_distinto` | Unitário com `{name}`, `{stem}`, chave desconhecida; e sobre o INDEX real | `_framework/tests/test_render_indexes.py` |
| RF01 a RF03 sobre o mapa real, `-k metricas_mapa_real` | Helper que lê o YAML e o mapa reais e mede repetição, título cortado, corte no meio de palavra e piso de 30 caracteres antes do `…` | `_framework/tests/test_render_indexes.py` |
| RF06, testes existentes e A10 a A12 | Cobertura, ids, tetos e idempotência já existentes; `--check` real | `_framework/tests/test_render_indexes.py` |
| RF07, `-k render_indexes` e `diff -r` | Paridade byte a byte e espelho | `_framework/tests/test_kit_parity.py` |

Teste existente que muda por esta SDD: em `test_mapa_ids_batem_com_banners`
(linha 167 do arquivo, comentário "multi-linha: título é a primeira linha"),
`assert sections[3].title == "BANNER EM VÁRIAS LINHAS QUE CONTINUA"` passa a
exigir o título juntado (`BANNER EM VÁRIAS LINHAS QUE CONTINUA AQUI NA
SEGUNDA LINHA`). Nenhum outro teste existente é alterado.

**Medição ANTES e metas DEPOIS** (ANTES medido na `main` em `1fe4f68`, em
2026-09-25; DEPOIS na branch de implementação, com
`python3 _framework/scripts/render_prompts.py` já rodado):

| Métrica | Como medir | Antes (main, 1fe4f68) | Meta depois |
|---|---|---|---|
| Linhas do mapa com Resumo repetindo o título; títulos terminados em `…` | A07 (`awk`), imprime dois números | `9 16` (repetição em §2, §3b, §3c, §6, §7, §8, §9, §10, §12) | `0` e ≤ 1 (só §12) |
| Resumos do mapa cortados no meio de palavra | A08 (script MEDE-CORTE) | 5 (§4, §11, §13, §17, §18) | 0 |
| Linhas do INDEX que dividem o "O que é"; textos distintos | A09 (`awk`) | `98 27` (15 grupos; 110 linhas) | `0` e igual ao `Total:` do cabeçalho |
| Mapa mais maior seção (exceto §0) | linha `YAML:` do cabeçalho e `--check` | 12520 bytes = 3787 + 8733, 13,7% de 91181 | ≤ `floor(0.15 * bytes(YAML))` (13677 com o YAML atual) |
| Maior linha do mapa | `awk` de tamanho sobre linhas `\| §` | 180 bytes | ≤ 180 |
| INDEX do kit: total e maior linha | `wc -c` e maior linha | 14934 bytes; 177 bytes | ≤ 24576 e ≤ 200 |

**Script MEDE-CORTE (A08).** Dado o YAML e o mapa, conta os Resumos que
terminam em `…` e cujo prefixo, procurado nos comentários e nos valores
textuais do YAML, só aparece seguido de caractere que não é espaço. Salvar
fora do repositório (ex.: no scratchpad) e rodar com os dois caminhos como
argumentos, ou colar por entrada padrão:

```python
# python3 - <yaml> <mapa> <<'EOF' ... EOF
import sys, yaml
ytxt = open(sys.argv[1], encoding="utf-8").read()
mtxt = open(sys.argv[2], encoding="utf-8").read()
norm = lambda s: " ".join(str(s).split()).lower()
hay = [norm(" ".join(l.lstrip("#") for l in ytxt.splitlines() if l.startswith("#")))]
def walk(o):
    if isinstance(o, str): hay.append(norm(o))
    elif isinstance(o, dict): [walk(v) for v in o.values()]
    elif isinstance(o, list): [walk(v) for v in o]
walk(yaml.safe_load(ytxt))
bad = []
for ln in mtxt.splitlines():
    if not ln.startswith("| §"): continue
    c = [x.strip() for x in ln.strip("|").split("|")]
    if c[0] == "§0" or not c[-1].endswith("…"): continue
    pre = norm(c[-1][:-1])
    hits = [(h, i) for h in hay for i in range(len(h)) if h.startswith(pre, i)]
    if hits and not any(i + len(pre) >= len(h) or h[i + len(pre)] == " " for h, i in hits):
        bad.append(c[0])
print(len(bad), bad)
```

Rodado na `main` (YAML e mapa de `git show main:...`), imprime
`5 ['§4', '§11', '§13', '§17', '§18']` (verificado pela SPEC-DTF-0022 em
2026-09-25).

**Coordenação com a SPEC-DTF-0021 e com a SDD-DTF-0048.** Esta SDD é
independente da SDD-DTF-0048 (que mexe só em `workflow-rules.yaml`), mas as
duas regeneram `_framework/rules/workflow-rules.map.md` e
`_framework/INDEX.md` (e `docs/sdd/INDEX.md`, que ganha as duas SDDs). Quem
for mergeada depois rebaseia sobre `main` e roda
`python3 _framework/scripts/render_prompts.py` de novo; conflito nesses
gerados nunca se resolve à mão. O teto do mapa é recalculado pelo `--check`
sobre o YAML vigente; se o YAML mudar antes da verificação, os números de
A07, A10 e A11 são refeitos contra o YAML novo.

Rollout e rollback: rollout direto, sem feature flag, por PR no kit e PR no
central com a mesma mudança; repositórios de projeto já mapeados não são
tocados. Rollback: reverter o commit; os gerados voltam junto e nenhum outro
script os lê.

Riscos operacionais e mitigação: (1) mapa passa do teto de 15% depois de
mudança no YAML: o teto é recalculado a cada `--check`; se estourar, reduz-se
`SUMMARY_MAX` e o piso `SUMMARY_MIN` antes de tocar a métrica da
RFC-DTF-0008 (folga medida no protótipo: 1046 bytes); (2) conflito de merge
nos gerados: quem mergeia depois rebaseia e regenera; (3) manifesto maior:
a cobertura reprova arquivo sem entrada no mesmo PR que o cria e as cópias
espelhadas usam glob com `{name}`; (4) linha de `kit-index.yaml` acima de 200
bytes: `check_kit_ceiling` reprova e o autor encurta o `what`; (5) fonte (3)
escolher valor que não descreve a seção: só vale para as cinco chaves de
`SCALAR_KEYS`, e o critério manual A17 e `map_summaries` corrigem caso a caso.

## Decomposição em tasks

Espelhamento no central (task 6): os caminhos prefixados por `central:` são
relativos a `/home/michel/doc-traceability-central/`; o `_framework/` do
central deve ficar idêntico ao do kit. A task 1 é só de medição (nenhum
arquivo do repositório é tocado).

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Rodar A07, A08 e A09 na `main` do kit e guardar as saídas reais (ANTES) para a Evidência | RF01, RF02, RF03, RF05 | (decisão pura) | |
| 2 | Código: `_cut_words`, `_sentence`, `_clean_title`, `_banner_parts`, nova `_section_summary`, `load_map_summaries`, `parse_yaml_sections` com `overrides`, expansão de `{name}` e `{stem}`, ajuste de `_section_row` (ordem de encurtamento) e da fiação em `generate_all` | RF01, RF02, RF03, RF04, RF05, RF06 | `_framework/scripts/render_indexes.py` | 1 |
| 3 | Manifesto: entrada individual por arquivo não espelhado, globs com `{name}` para as quatro famílias de cópia, `map_summaries` das seções 2, 6, 7, 9 e 12 | RF04, RF05 | `_framework/rules/kit-index.yaml` | 2 |
| 4 | Testes de A01 a A06, correção da linha 167 do teste do título multilinha e os cinco sensores de mutação | RF01, RF02, RF03, RF04, RF05, RF06 | `_framework/tests/test_render_indexes.py` | 2, 3 |
| 5 | Regenerar com `render_prompts.py` (mapa, INDEX do kit, `docs/sdd/INDEX.md`, cópia bundlada de `render_indexes.py`), rodar `--check` e A01 a A16 registrando comando e saída reais | RF06, RF07 | `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md`, `docs/sdd/INDEX.md`, `_framework/skills/doc-traceability-framework/scripts/render_indexes.py` | 2, 3, 4 |
| 6 | Espelhar no central, em worktree, branch e PR próprios do central | RF07 | `central:_framework/scripts/render_indexes.py`, `central:_framework/rules/kit-index.yaml`, `central:_framework/rules/workflow-rules.map.md`, `central:_framework/INDEX.md`, `central:_framework/tests/test_render_indexes.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_indexes.py` | 2, 3, 4, 5 |

Ordem: 1, 2, 3, 4, 5, 6 (cadeia linear: o manifesto usa a sintaxe nova do
código e a validação de `map_summaries`; os testes validam as duas contra os
arquivos reais). Não há grupo paralelizável. Confirmar com
`python3 _framework/scripts/parallel_plan.py docs/sdd/SDD-DTF-0049.md`.
A verificação independente (`sdd-verifier`, sessão separada) vem depois da
task 6 e antes de `implemented`.

## Critérios de aceite / definição de pronto

Consolidados da SPEC-DTF-0022 (A01 a A17, sem relaxar comando nem resultado).
Executar na raiz do kit (`cd /home/michel/doc-traceability-framework`), salvo
A13. "Antes" = `main` em `1fe4f68`; "depois" = na branch de implementação,
com o gerador já rodado (`python3 _framework/scripts/render_prompts.py`).

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | RF01: título completo, sem cauda após travessão, sem parêntese quando passa de 70, corte com `…` só quando ainda passa | `python3 -m pytest _framework/tests/test_render_indexes.py -k titulo_completo -v` | Todos os testes selecionados passam | automatizado |
| A02 | RF02: cadeia de fontes, rótulo removido, primeira frase completa, casos sem descrição e com comentário vazio | `python3 -m pytest _framework/tests/test_render_indexes.py -k resumo_cadeia -v` | Todos passam | automatizado |
| A03 | RF03: corte em fronteira de palavra, ≤ limite contando `…`, sem conectivo pendurado, ordem de encurtamento | `python3 -m pytest _framework/tests/test_render_indexes.py -k corte_fronteira_palavra -v` | Todos passam | automatizado |
| A04 | RF04: `map_summaries` só sem fonte automática; erro com código 2 | `python3 -m pytest _framework/tests/test_render_indexes.py -k map_summaries -v` | Todos passam | automatizado |
| A05 | RF05: `{name}` e `{stem}` expandidos, chave desconhecida literal, nenhum "O que é" repetido no INDEX real, cobertura da 0016 intacta | `python3 -m pytest _framework/tests/test_render_indexes.py -k kit_index_o_que_e_distinto -v` | Todos passam | automatizado |
| A06 | RF01 a RF03: métricas do mapa real no teste (0 repetidos, ≤ 1 título cortado, 0 cortes no meio de palavra, todo resumo com `…` tem ≥ 30 caracteres antes dele) | `python3 -m pytest _framework/tests/test_render_indexes.py -k metricas_mapa_real -v` | Todos passam | automatizado |
| A07 | RF01, RF02: medição DEPOIS do mapa; para o ANTES usar `git show main:_framework/rules/workflow-rules.map.md` como entrada padrão no lugar do arquivo | `awk -F'\174' 'NR>8 && $1=="" {t=$3; r=$7; gsub(/^ +/,"",t); gsub(/ +$/,"",t); gsub(/^ +/,"",r); gsub(/ +$/,"",r); sub(/…$/,"",t); sub(/…$/,"",r); if (index(r,substr(t,1,15))==1) rep++; else if (index(t,substr(r,1,15))==1) rep++; if ($3 ~ /…[ ]*$/) tt++} END {print rep+0, tt+0}' _framework/rules/workflow-rules.map.md` | Primeiro número `0`, segundo ≤ `1` (antes: `9 16`) | automatizado |
| A08 | RF03: nenhum resumo cortado no meio de palavra (script MEDE-CORTE sobre o YAML e o mapa gerados; ANTES com os dois de `git show main:`) | `python3 - _framework/rules/workflow-rules.yaml _framework/rules/workflow-rules.map.md <<'EOF'` com o script MEDE-CORTE acima | `0 []` (antes: `5 ['§4', '§11', '§13', '§17', '§18']`) | automatizado |
| A09 | RF05: medição DEPOIS do INDEX; ANTES com `git show main:_framework/INDEX.md` como entrada padrão | `awk -F'\174' 'NR>7 && $1=="" {c[$3]++} END {n=0; d=0; for (k in c) {d++; if (c[k]>1) n+=c[k]}; print n, d}' _framework/INDEX.md` | Primeiro número `0`, segundo igual ao `Total:` do cabeçalho (antes: `98 27`) | automatizado |
| A10 | RF06: tetos e códigos de saída dos índices e da renderização completa | `python3 _framework/scripts/render_indexes.py --check; echo "exit=$?"` e `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | `✅` por índice, linha `mapa+maior seção = <bytes> (<pct>% do YAML)` com pct ≤ 15,0 (mapa mais maior seção ≤ 13677 bytes com o YAML atual), INDEX ≤ 24576 bytes e cada linha ≤ 200 bytes, `exit=0` nos dois | automatizado |
| A11 | RF06: testes existentes de cobertura, ids do mapa, tetos e idempotência seguem passando (o teste do título multilinha foi atualizado) | `python3 -m pytest _framework/tests/test_render_indexes.py -k "manifesto_orfao or mapa_ids_batem or tetos or idempotente" -v` | Todos passam | automatizado |
| A12 | RF06: YAML e `render_prompts.py` não editados; versão intacta | `git diff --stat origin/main -- _framework/rules/workflow-rules.yaml _framework/scripts/render_prompts.py` e `python3 -c "import yaml; print(yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))['framework']['version'])"` | Primeiro comando sem saída (baseline: `origin/main` no momento da verificação, mesmo que a SPEC-DTF-0021 já esteja mergeada); segundo imprime a versão de `origin/main` (`2.3.1` na data da SPEC-DTF-0022) | automatizado |
| A13 | RF07: `_framework/` do central idêntico ao do kit | `diff -r -x __pycache__ -x .pytest_cache -x .ruff_cache -x .mypy_cache /home/michel/doc-traceability-framework/_framework /home/michel/doc-traceability-central/_framework; echo "exit=$?"` | Sem saída de diff, `exit=0` | automatizado |
| A14 | RF07: cópia da skill de `render_indexes.py` idêntica byte a byte | `python3 -m pytest _framework/tests/test_kit_parity.py -k render_indexes -v` | Todos passam | automatizado |
| A15 | RF07: `docs/sdd/INDEX.md` em dia | `python3 _framework/scripts/render_indexes.py sdd docs/sdd --check` | `✅ docs/sdd/INDEX.md: em dia.`, exit 0 | automatizado |
| A16 | Suíte completa sem regressão (antes: 27 testes em `test_render_indexes.py`, todos passando) | `python3 -m pytest _framework/ -q` | Todos passam | automatizado |
| A17 | Qualidade do texto para um leitor: cada linha distingue o alvo dos vizinhos, sem frase cortada que mude o sentido | Leitura humana de `_framework/rules/workflow-rules.map.md` inteiro e de 10 linhas sorteadas de `_framework/INDEX.md` | Aprovado pelo revisor | manual |

Justificativa do perfil manual em A17 (da SPEC-DTF-0022): "ajuda a escolher"
é juízo de leitor; as métricas A06 a A09 cobrem o que é mecânico.

## Instruções específicas para a IA implementadora

- **Branch, worktree e commit:** implementar em branch nomeada pelo id que
  originou a mudança, `sdd/SDD-DTF-0049-mapa-index-especificos`, criada em
  worktree próprio do kit a partir de `origin/main`:
  `git worktree add ../dtf-wt-0049 -b sdd/SDD-DTF-0049-mapa-index-especificos origin/main`.
  Cada commit de implementação leva `Refs: SDD-DTF-0049` no corpo. Nunca
  commit direto em `main`; levar a `main` por PR. A branch de documentos
  `docs/sdd-dtf-0048-0049-mapa-e-gates` não é a de implementação. O espelho
  da task 6 é feito em worktree próprio do central, com branch e PR próprios
  (push direto em `main` lá é bloqueado); no central, `git add` por arquivo,
  nunca `git add -A`.
- **Sessão separada:** implementar na sessão aberta no repositório do kit,
  nunca na do repositório central.
- **Verificação:** o status só vai a `implemented` depois de o
  `sdd-verifier` rodar em sessão separada da que implementou, registrando
  comando e saída reais de cada critério na Evidência. Quem escreveu o
  código não verifica.
- **Ordem entre mudanças:** esta SDD é independente da SDD-DTF-0048 (que só
  mexe em `workflow-rules.yaml`), mas as duas regeneram
  `workflow-rules.map.md` e `INDEX.md`. Quem for mergeada depois rebaseia
  sobre `main` e roda `python3 _framework/scripts/render_prompts.py`; nunca
  editar esses arquivos à mão para resolver conflito. Se o YAML mudar antes,
  refazer as medições de A07, A10 e A11 contra o YAML novo.
- **Contrato:** nos RFs que a SPEC-DTF-0022 marca como alterados prevalece a
  0022 sobre a SPEC-DTF-0016. Nada pode divergir da 0022 (nomes,
  assinaturas, constantes `TITLE_MAX = 70`, `SUMMARY_MAX = 100`,
  `SUMMARY_MIN = 30`, piso do título 20, teto de linha 180 bytes, cadeia de
  seis fontes, `DANGLING`). Não relaxar nenhum critério nem meta.
- **Não alterar** `_framework/rules/workflow-rules.yaml`,
  `_framework/scripts/render_prompts.py`, `framework.version`, `AGENTS.md`,
  `SKILL.md`, procedimentos, prompts nem templates. Não editar à mão nenhum
  arquivo gerado (`_framework/INDEX.md`, `workflow-rules.map.md`,
  `docs/sdd/INDEX.md`, cópias da skill): rodar os geradores. Não tocar em
  `registry.yaml` nem `registry.md`.
- **Assinaturas** como na seção "Produces". Não renomear as funções públicas
  existentes (`parse_yaml_sections`, `build_section_map`,
  `load_kit_manifest`, `build_kit_index`, `generate_all`, `main`); parâmetros
  novos só com valor padrão. Sem dependência nova, saída determinística (LF,
  UTF-8, sem timestamp, ordenada), nenhuma flag de CLI nova.
- **Escrita do `kit-index.yaml`:** abrir cada arquivo antes de escrever a
  linha dele (docstring, título ou primeira descrição); `what` diz o que o
  arquivo faz, com o nome do script, teste, skill ou template e uma frase
  real, ≥ 4 palavras e sem copiar o `what` de outro arquivo; `when` diz em
  que tarefa abri-lo. Nenhum texto provisório: cada linha já sai final.
  Rodar `render_indexes.py` e conferir o teto de 200 bytes por linha antes de
  seguir.
- **Não usar** colchete seguido de parêntese em tabela markdown dos índices
  gerados: `check_renderings.py` lê isso como link quebrado. Se o texto de
  `what`, `when` ou `map_summaries` precisar de colchetes, reescrever a
  frase.
- **Testes obrigatórios (task 4):** um teste por critério A01 a A06, cada um
  com sensor de discriminação em espaço descartável (mutar, ver o teste
  FALHAR, reverter): (a) `_cut_words` cortando por caractere sem recuar ao
  espaço derruba `corte_fronteira_palavra` e `metricas_mapa_real`; (b) tirar a
  fonte (3) de `_section_summary` derruba `resumo_cadeia`; (c) remover o
  descarte da cauda após ` — ` em `_clean_title` derruba `titulo_completo`;
  (d) desativar a validação de id em `load_map_summaries` derruba
  `map_summaries`; (e) remover a expansão de `{name}` derruba
  `kit_index_o_que_e_distinto`. As métricas de A06 são implementadas no teste
  (helper que lê o mapa real e o YAML real e usa as funções do módulo).
- **Teste que muda por decisão desta SDD:** em `test_mapa_ids_batem_com_banners`
  a linha 167 que exige título igual à primeira linha do banner multilinha
  passa a exigir o título juntado (`BANNER EM VÁRIAS LINHAS QUE CONTINUA AQUI
  NA SEGUNDA LINHA`). Nenhum outro teste existente é alterado.
- Não corrigir a faixa de tamanho do INDEX nem a coluna Bytes do mapa (fora
  de escopo).

## Errata da SPEC-DTF-0024 (segunda rodada de implementação)

A SPEC-DTF-0024 (`approved`) complementa a SPEC-DTF-0022 depois da
verificação independente desta SDD, que passou A01 a A16 e reprovou com
ressalvas o A17 no mapa. Onde esta seção diz "alterado", a SPEC-DTF-0024
prevalece sobre o RF03 da SPEC-DTF-0022; em tudo o mais a 0022 vale. As tasks
1 a 6 e os critérios A01 a A17 acima já foram implementados (PR #127) e não
mudam. Leia a SPEC-DTF-0024 inteira antes de implementar; em divergência com
esta seção, a SPEC manda.

| RF (SPEC-DTF-0024) | Requisito | Arquivos |
|---|---|---|
| RF01 | `_cut_words` descarta, depois do corte, palavra final que seja só um travessão (`—`, `–` ou `-`), além dos conectivos de `DANGLING` | `_framework/scripts/render_indexes.py`, cópia na skill |
| RF02 | `_cut_words` recua até antes de um `(` sem `)` correspondente no trecho retido e refaz o descarte | `_framework/scripts/render_indexes.py`, cópia na skill |
| RF03 | Mapa regenerado com 0 resumos terminando em travessão ou com parêntese aberto; tetos de tamanho inalterados | `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md` |
| RF04 | Testes das três lacunas: descarte de `DANGLING` exercido, precedência da fonte 3 sobre `map_summaries` e piso `SUMMARY_MIN` | `_framework/tests/test_render_indexes.py` |
| RF05 | Desvio de `references/` registrado (esta seção, abaixo) | `docs/sdd/SDD-DTF-0049.md` |

**Desvio registrado (RF05): `references/` da skill.** A SPEC-DTF-0022 mandava
tratar `references/` como família de cópia com glob. Só
`references/workflow-rules.yaml` é cópia gerada por `render_prompts.py`;
`audit.md`, `incidents.md` e `onboarding.md` são escritos à mão. O manifesto
`kit-index.yaml` usa entradas individuais para os três `.md` e um glob
`references/*` com `{name}` para o restante, porque uma descrição de "cópia
gerada" para os três descreveria errado. O verificador confirmou o desvio como
justificado e de baixo risco.

Contrato do laço final de `_cut_words` (assinatura
`_cut_words(text: str, limit: int) -> str` permanece; constante nova
`DASHES = {"—", "–", "-"}`), depois de montar `words` a partir do trecho retido:

```
while words:
    joined = " ".join(words)
    if joined.count("(") > joined.count(")"):
        idx = joined.rfind("(")
        words = joined[:idx].split()
        continue
    if words[-1].lower() in DANGLING or words[-1] in DASHES or words[-1][-1] in "(:,;":
        words.pop()
        continue
    break
```

Só palavra final composta apenas de travessão é descartada (`pré-condição`
não casa); sem palavras restantes vale o corte duro por caractere já
existente. Testes novos em `_framework/tests/test_render_indexes.py`:
`test_corte_descarta_travessao_e_parentese_aberto`,
`test_corte_descarta_conectivo_pendurado_exercido`,
`test_map_summaries_perde_para_fonte_3` e
`test_piso_summary_min_no_encurtamento_da_linha`.

### Tasks da errata

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 7 | Rodar A18 a A21 na `main` e guardar as saídas reais (ANTES) | RF01, RF02, RF03, RF04 | (decisão pura) | |
| 8 | Código: `DASHES` e o laço final de `_cut_words` | RF01, RF02 | `_framework/scripts/render_indexes.py` | 7 |
| 9 | Testes: os quatro novos e os três sensores de mutação | RF01, RF02, RF04 | `_framework/tests/test_render_indexes.py` | 8 |
| 10 | Regenerar com `render_prompts.py` (mapa, INDEX, cópia da skill, `docs/sdd/`), rodar `--check` e A18 a A27 registrando comando e saída reais | RF03 | `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md`, `_framework/skills/doc-traceability-framework/scripts/render_indexes.py`, `docs/sdd/INDEX.md`, `docs/sdd/registry.md` | 9 |
| 11 | Espelhar no central, em worktree, branch e PR próprios do central | RF03 | `central:_framework/scripts/render_indexes.py`, `central:_framework/skills/doc-traceability-framework/scripts/render_indexes.py`, `central:_framework/tests/test_render_indexes.py`, `central:_framework/rules/kit-index.yaml`, `central:_framework/rules/workflow-rules.map.md`, `central:_framework/INDEX.md` | 10 |

Ordem: 7, 8, 9, 10, 11 (cadeia linear). Branch de implementação nova:
`git worktree add ../dtf-wt-0049b -b sdd/SDD-DTF-0049-errata-0024 origin/main`
(a `sdd/SDD-DTF-0049-mapa-index-especificos` já foi mergeada). Commits com
`Refs: SDD-DTF-0049`; sem commit direto em `main`; sem force-push; gerados só
por `render_prompts.py` e `render_indexes.py`, nunca à mão. O `sdd-verifier`
roda depois da task 11, em sessão separada.

### Critérios de aceite da errata (SPEC-DTF-0024, A01 a A11)

Executar na raiz do kit. "Antes" = `main` antes da errata; "depois" = na
branch de implementação, com os gerados regenerados.

| # | Critério (origem) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A18 | RF01, RF02: travessão e parêntese aberto no corte (0024 A01) | `python3 -m pytest _framework/tests/test_render_indexes.py -k corte_descarta_travessao -v` | ANTES: 0 selecionados; DEPOIS: 1 passed | automatizado |
| A19 | RF04: três lacunas cobertas (0024 A02) | `python3 -m pytest _framework/tests/test_render_indexes.py -k "conectivo_pendurado_exercido or map_summaries_perde_para_fonte_3 or piso_summary_min" -v` | 3 passed | automatizado |
| A20 | RF03: mapa sem resumo em travessão nem parêntese aberto (0024 A03) | `python3 -c "rows=[l for l in open('_framework/rules/workflow-rules.map.md',encoding='utf-8') if l[2:3]=='§']; print(sum(1 for l in rows if '—…' in l or '–…' in l or ' -…' in l), sum(1 for l in rows if l.count('(')>l.count(')')))"` | ANTES: `3 2`; DEPOIS: `0 0` | automatizado |
| A21 | RF03: índices e gerados em dia (0024 A04) | `python3 _framework/scripts/render_indexes.py --check; echo "exit=$?"` e `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | Os dois com `exit=0`; `mapa+maior seção` abaixo de 15% do YAML | automatizado |
| A22 | RF04: cada mutação derruba um teste (0024 A05) | Em cópia descartável, mutar (a) o descarte de `DANGLING` no laço final de `_cut_words`, (b) a ordem entre `_scalar_source` e `map_summaries`, (c) `SUMMARY_MIN = 30` para `10`; rodar `python3 -m pytest _framework/tests/test_render_indexes.py -q`; restaurar | Cada mutação: pelo menos 1 failed; sem mutação: 0 failed | automatizado |
| A23 | Suíte inteira sem regressão (0024 A06) | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | 0 failed | automatizado |
| A24 | RF05: desvio de `references/` registrado (0024 A07) | `grep -c "references/\*" docs/sdd/SDD-DTF-0049.md; grep -c "SPEC-DTF-0024" docs/sdd/SDD-DTF-0049.md` | Ambos com contagem maior ou igual a 1 | automatizado |
| A25 | RF01, RF02: cópia da skill e formatação (0024 A08) | `cmp _framework/scripts/render_indexes.py _framework/skills/doc-traceability-framework/scripts/render_indexes.py; ruff format --check _framework/scripts; echo "exit=$?"` | `cmp` sem saída e `exit=0` | automatizado |
| A26 | Só os arquivos previstos mudaram (0024 A09) | `git diff --name-only main` | Só `render_indexes.py`, a cópia dele na skill, `test_render_indexes.py`, `workflow-rules.map.md`, `INDEX.md` e os gerados de `docs/sdd/` (`registry.md`, `INDEX.md`); nenhum `workflow-rules.yaml`, nenhum `render_prompts.py` | automatizado |
| A27 | Espelho no central (0024 A10) | Em `/home/michel/doc-traceability-central`: `for f in scripts/render_indexes.py skills/doc-traceability-framework/scripts/render_indexes.py tests/test_render_indexes.py rules/kit-index.yaml rules/workflow-rules.map.md INDEX.md; do cmp /home/michel/doc-traceability-framework/_framework/$f _framework/$f && echo "igual $f"; done; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | 6 linhas `igual ...` e `exit=0` | automatizado |
| A28 | RF03: leitura humana do mapa regenerado (0024 A11) | Ler as 22 linhas do mapa regenerado | Nenhum resumo termina em travessão ou parêntese aberto; resumos de §13, §16, §18 e §19 seguem como limite reconhecido | manual (motivo: julgar se o resumo é útil exige leitura; registrar julgamento e a saída de A20) |

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF07) tem código
      correspondente (nada da SPEC-DTF-0022 ficou de fora).
- [ ] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", na "Decomposição em tasks" ou em "Instruções
      específicas" — se a implementação tocou um arquivo não listado aqui, ou
      é escopo que faltou registrar na SDD (atualize-a) ou é scope creep a
      remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado ("já que estava ali").
- [ ] Errata da SPEC-DTF-0024: RF01 a RF05 têm código, teste ou nota
      correspondente e só os arquivos da task 7 a 11 mudaram.
- [ ] `workflow-rules.yaml` intocado, `render_prompts.py` sem diff,
      `framework.version` igual ao de `origin/main`, e os valores de
      `CEILINGS` e `MAP_FRACTION` iguais aos da 0016.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou —
quem escreveu o código tem o resultado como conclusão desejada. Para cada
critério da tabela acima: comando rodado de fato nesta sessão e saída real,
nunca "deve passar" nem resultado de memória. Nada foi rodado ainda: esta SDD
está em `draft` e as linhas abaixo esperam o verificador.

**Verificador independente:** pendente — sdd-verifier em sessão separada

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Teste que passa com a implementação quebrada é
ruído verde. Critério sem teste automatizado: escreva "sem teste", nunca
marque como verificado por leitura de código. Coluna "Assertion
(file:line)": caminho e linha exatos da asserção que resolve o critério;
critério `manual` ou `n/a` usa `n/a`. Coluna "Perfil usado": repete o
"Perfil esperado" do critério ou declara divergência com justificativa entre
parênteses.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
| A01 | pendente: `python3 -m pytest _framework/tests/test_render_indexes.py -k titulo_completo -v` | pendente | pendente: mutação (c) | pendente | pendente | pendente |
| A02 | pendente: `python3 -m pytest _framework/tests/test_render_indexes.py -k resumo_cadeia -v` | pendente | pendente: mutação (b) | pendente | pendente | pendente |
| A03 | pendente: `python3 -m pytest _framework/tests/test_render_indexes.py -k corte_fronteira_palavra -v` | pendente | pendente: mutação (a) | pendente | pendente | pendente |
| A04 | pendente: `python3 -m pytest _framework/tests/test_render_indexes.py -k map_summaries -v` | pendente | pendente: mutação (d) | pendente | pendente | pendente |
| A05 | pendente: `python3 -m pytest _framework/tests/test_render_indexes.py -k kit_index_o_que_e_distinto -v` | pendente | pendente: mutação (e) | pendente | pendente | pendente |
| A06 | pendente: `python3 -m pytest _framework/tests/test_render_indexes.py -k metricas_mapa_real -v` | pendente | pendente: mutação (a) | pendente | pendente | pendente |
| A07 | pendente: awk de A07 sobre o mapa gerado (ANTES e DEPOIS) | pendente | n/a | pendente | n/a | pendente |
| A08 | pendente: script MEDE-CORTE sobre o YAML e o mapa gerados (ANTES e DEPOIS) | pendente | n/a | pendente | n/a | pendente |
| A09 | pendente: awk de A09 sobre o INDEX gerado (ANTES e DEPOIS) | pendente | n/a | pendente | n/a | pendente |
| A10 | pendente: `render_indexes.py --check` e `render_prompts.py --check` | pendente | n/a | pendente | n/a | pendente |
| A11 | pendente: pytest de cobertura, ids, tetos e idempotência | pendente | n/a | pendente | pendente | pendente |
| A12 | pendente: `git diff --stat origin/main` do YAML e de `render_prompts.py`, e versão | pendente | n/a | pendente | n/a | pendente |
| A13 | pendente: `diff -r` kit x central | pendente | n/a | pendente | n/a | pendente |
| A14 | pendente: `pytest _framework/tests/test_kit_parity.py -k render_indexes -v` | pendente | n/a | pendente | pendente | pendente |
| A15 | pendente: `render_indexes.py sdd docs/sdd --check` | pendente | n/a | pendente | n/a | pendente |
| A16 | pendente: `python3 -m pytest _framework/ -q` | pendente | n/a | pendente | n/a | pendente |
| A17 | pendente: leitura humana do mapa e de 10 linhas do INDEX | pendente | n/a | pendente | n/a | pendente |
| A18 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | pendente | pendente |
| A19 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | pendente | pendente |
| A20 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |
| A21 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |
| A22 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | pendente: mutações (a) a (c) | pendente | pendente | pendente |
| A23 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | pendente | pendente |
| A24 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |
| A25 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |
| A26 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |
| A27 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |
| A28 | pendente: critério da errata SPEC-DTF-0024 (ver tabela acima) | pendente | n/a | pendente | n/a | pendente |

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0024 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0024.md), SPEC-DTF-0022 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0022.md), SPEC-DTF-0016 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0016.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
