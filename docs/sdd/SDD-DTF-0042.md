---
id: SDD-DTF-0042
type: SDD
title: "Corrigir defasagens do kit: gate_implementation_before_code em SPEC, espelho do sdd.template.md e teste de paridade de templates"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: []
source_docs:
  - id: "SPEC-DTF-0017"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0017.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Compilada da SPEC-DTF-0017 (frente B da RFC-DTF-0008). Implementar em sessão separada, no repositório do kit, em branch sdd/SDD-DTF-0042-*, nesta ordem: esta SDD (0042) primeiro, depois SDD-DTF-0043, depois a SDD de SPEC-DTF-0020. Editar só o YAML (nunca os gerados à mão), copiar o template do original para o bundle, criar os dois testes e regenerar com render_prompts.py; depois espelhar no central. Rodar cada critério de aceite de fato e registrar comando e saída reais; verificação por sdd-verifier em sessão separada antes de implemented."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, defasagem, gate_implementation_before_code, paridade-templates]
---

# Corrigir defasagens do kit: gate_implementation_before_code em SPEC, espelho do sdd.template.md e teste de paridade de templates

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar. Fonte normativa:
> SPEC-DTF-0017 (Partes 1 e 2). Em qualquer divergência, a SPEC manda.

## Resumo executivo

Três defasagens do kit (framework 2.3.0) são corrigidas sem mudar nenhuma
regra de comportamento: (1) `gate_implementation_before_code` em
`_framework/rules/workflow-rules.yaml` ainda manda verificar "PRD e/ou Tech
Spec" e cita a chave inexistente `decision_gates.prd_ts_to_sdd`, enquanto o
`iron_law`, o `AGENTS.md` e o `SKILL.md` já dizem SPEC; (2) o
`sdd.template.md` do bundle da skill perdeu os trechos das colunas
"Perfil esperado", "Assertion (file:line)" e "Perfil usado"; (3) nenhum
teste compara os templates do bundle com os originais. A mudança sobe o
framework para 2.3.1 (patch, texto sem mudança de comportamento,
não-retroativa), regenera os artefatos gerados, cria
`test_gate_texto.py` e `test_template_parity.py` e é espelhada na cópia
`_framework/` do repositório central. Frente B da RFC-DTF-0008. Ordem de
implementação: esta SDD vem PRIMEIRA (0042 → 0043 → SDD de SPEC-DTF-0020),
porque a SPEC-DTF-0016 e as seguintes rebaseiam sobre a 2.3.1.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — RFC-DTF-0008 dispensou decisão arquitetural via gate
(`decision_gates.rfc_to_adr = false`, `requires_adr: false`). Decisões
registradas na SPEC-DTF-0017 (2026-09-24), aplicáveis aqui:

1. Referências a PRD/Tech Spec fora de `gate_implementation_before_code`
   (capabilities, seção 14, seção 15) ficam para SPEC/SDD própria.
2. SPEC-DTF-0017 é implementada e mergeada em `main` do kit antes da
   SPEC-DTF-0016, que rebaseia sobre a 2.3.1.
3. O passo de CI que roda `python3 -m pytest _framework/tests/` entra pela
   SPEC-DTF-0019 (RF04), não por esta.
4. A versão é `2.3.1` (patch).

## Requisitos consolidados

Caminhos relativos à raiz do kit; os mesmos valem no central (RF10).

| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |
|---|---|---|---|
| RF01 | Os passos 1 a 3 do campo `rule` de `gate_implementation_before_code` mandam verificar/criar a **SPEC** (não "PRD e/ou Tech Spec"), verificar a SDD via `decision_gates.spec_to_sdd` (chave existente) e liberar código só depois de "SPEC e SDD" existirem. | O sistema deve conter, no campo `rule` de `gate_implementation_before_code`, a expressão `decision_gates.spec_to_sdd`, a palavra "SPEC" nos passos 1 e 3, e nenhuma ocorrência de `decision_gates.prd_ts_to_sdd`. | `_framework/rules/workflow-rules.yaml` |
| RF02 | Os campos `not_sufficient_alone`, `if_user_asks_to_skip` e `relationship_with_audit` da mesma regra e os dois comentários-banner normativos (título da seção 13 e o parágrafo que declara "PRD/TS/SDD exista ANTES") trocam PRD/Tech Spec por SPEC. Os comentários que narram o incidente EVM (linhas 979 e 1062) são histórico e ficam como estão. | O sistema deve manter, nos campos `rule` (antes da cláusula de legado do RF03), `not_sufficient_alone`, `if_user_asks_to_skip` e `relationship_with_audit` de `gate_implementation_before_code`, zero ocorrências de `PRD`, `Tech Spec` ou `TS` como palavra inteira. | `_framework/rules/workflow-rules.yaml` |
| RF03 | O campo `rule` ganha uma única cláusula final iniciada por "Em projeto legado (sob 1.x)" dizendo que o par PRD + Tech Spec ocupa o lugar da SPEC nos passos 1 e 3, alinhada a `decision_gates.spec_to_sdd` (YAML, linhas 471-477, que já diz isso). Nenhuma outra seção do YAML, exceto o bloco `framework:` (RF05), é alterada; em particular as menções legítimas de legado listadas em "Fora de escopo" ficam intactas. | Quando o YAML alterado for comparado com o da `main`, o sistema deve apresentar valores idênticos em todas as chaves de topo exceto `framework` e `gate_implementation_before_code`. | `_framework/rules/workflow-rules.yaml` |
| RF04 | Um teste de regressão de texto impede a volta da defasagem: falha se `rule` (antes da cláusula de legado) ou os outros três campos citarem PRD/Tech Spec/TS, ou se toda referência `decision_gates.<chave>` dentro da regra apontar para chave inexistente em `decision_gates`. | Se `gate_implementation_before_code` reintroduzir PRD/Tech Spec/TS fora da cláusula de legado, ou citar `decision_gates.<chave>` inexistente, então o sistema deve falhar o teste `test_gate_regra_sem_prd_ts_como_passo` ou `test_gate_referencias_decision_gates_existem`. | `_framework/tests/test_gate_texto.py` |
| RF05 | Como o YAML muda, `framework.version` sobe de `2.3.0` para `2.3.1`, `framework.last_updated` recebe a data da implementação e `framework.changelog` ganha a entrada `2.3.1` no topo, citando SPEC-DTF-0017/RFC-DTF-0008, dizendo que é correção de texto sem mudança de comportamento e não-retroativa. | Quando esta SDD for implementada, o sistema deve apresentar `framework.version == "2.3.1"`, `framework.changelog[0].version == "2.3.1"` e `framework.last_updated == framework.changelog[0].date`. | `_framework/rules/workflow-rules.yaml` |
| RF06 | Todos os artefatos gerados do YAML são regenerados com `render_prompts.py` (sem editar à mão), inclusive a cópia do YAML em `skills/doc-traceability-framework/references/workflow-rules.yaml`, e o `--check` passa. | Quando `python3 _framework/scripts/render_prompts.py --check` rodar após a regeneração, o sistema deve sair com código 0 e `docs/especificacao.md` deve conter zero ocorrências de "PRD e/ou Tech Spec". | `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/prompts/copilot/copilot-instructions.md`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml` |
| RF07 | A mudança não é retroativa: nenhum registry, front-matter ou documento de projeto mapeado é alterado, e a validação de todos os registries descobertos continua com o mesmo resultado. | O sistema deve produzir, em `python3 _framework/scripts/framework_check.py --auto`, o mesmo código de saída antes e depois da mudança, e `git diff --stat` não deve listar nenhum arquivo em `docs/**/registry.yaml`, `docs/**/registry.md` nem em `examples/`. | (decisão pura) |
| RF08 | O `sdd.template.md` do bundle passa a ser byte-idêntico ao de `_framework/templates/` (espelho do original para o bundle, nunca o inverso). | O sistema deve manter `_framework/skills/doc-traceability-framework/templates/sdd.template.md` byte-idêntico a `_framework/templates/sdd.template.md`. | `_framework/skills/doc-traceability-framework/templates/sdd.template.md` |
| RF09 | Um teste de paridade compara, byte a byte, todo `*.md` de `_framework/templates/` (não recursivo) com o gêmeo no bundle, e reprova arquivo `*.md` do bundle sem original. | Se algum `*.md` de `_framework/templates/` diferir do gêmeo em `_framework/skills/doc-traceability-framework/templates/`, ou faltar nele, ou o bundle tiver `*.md` sem original, então o sistema deve falhar o teste `test_templates_md_paridade` ou `test_bundle_sem_template_orfao`. | `_framework/tests/test_template_parity.py` |
| RF10 | Toda alteração dos RF01-RF09 é aplicada também na cópia `_framework/` do repositório central (`doc-traceability-central`), com os artefatos gerados da raiz do central regenerados lá, e o `--check` do central passa. | Quando `cmp` comparar cada arquivo tocado no kit com o mesmo caminho no central, o sistema deve reportar arquivos idênticos, e `python3 _framework/scripts/render_prompts.py --check` no central deve sair com código 0. | `_framework/rules/workflow-rules.yaml`, `_framework/templates/sdd.template.md`, `_framework/skills/doc-traceability-framework/templates/sdd.template.md`, `_framework/tests/test_gate_texto.py`, `_framework/tests/test_template_parity.py` |

### Casos de borda / condições de erro

| Caso | RF relacionado | Comportamento esperado |
|---|---|---|
| A cláusula de legado é escrita com outra abertura ("Em projetos legados…") e o teste divide o texto na âncora errada | RF03, RF04 | A âncora é a constante exata `Em projeto legado (sob 1.x)`; se ela faltar em `rule`, `test_gate_regra_sem_prd_ts_como_passo` falha com mensagem dizendo que a cláusula de legado sumiu (o teste não trata ausência como "nenhuma ocorrência") |
| A cláusula de legado aparece mais de uma vez em `rule` | RF03, RF04 | O teste falha: exige exatamente uma ocorrência da âncora |
| PRD/TS citados em outras seções do YAML (projeto legado) | RF03 | Não são tocados nem verificados pelo teste; RF03 prova só que essas seções não mudaram |
| `decision_gates.<chave>` citada na regra que existe com outro nome (caso real de `prd_ts_to_sdd`) | RF01, RF04 | `test_gate_referencias_decision_gates_existem` falha listando a chave inexistente |
| `templates/ci/` existe em `_framework/templates/` mas não no bundle | RF09 | Fora da comparação: o teste usa `glob("*.md")` não recursivo; `ci/verify-sdd-gate.yml.example` não é template `.md` |
| Bundle sem a pasta `templates/` ou sem algum gêmeo | RF09 | Teste falha por `assert` explícito de existência, nunca passa por "nada a comparar" |
| Original e bundle divergem só em fim de linha ou espaço final | RF08, RF09 | Compara `read_bytes()`: qualquer diferença de byte reprova (mesma técnica de `test_kit_parity.py`) |
| Bundle tem um `*.md` novo sem original (alguém editou só o bundle) | RF09 | `test_bundle_sem_template_orfao` falha listando o arquivo |
| `render_prompts.py --check` falha por arquivo gerado desatualizado | RF06 | Rodar `render_prompts.py` (sem `--check`) e commitar o resultado; nunca editar gerado à mão |
| `SPEC-DTF-0016` implementada antes desta SPEC | RF05, RF06 | Violação da ordem declarada: a implementação de 0017 deve parar e ser rebaseada sobre 0016 só com decisão humana registrada (decisão 2) |
| `framework_check.py --auto` já falha antes da mudança | RF07 | O critério compara resultado antes×depois; falha preexistente não é atribuída a esta SDD, mas precisa ser registrada nela |

### Requisitos não funcionais

- Nenhuma dependência nova: os testes usam stdlib, `pytest` e `PyYAML`.
- O texto novo dos passos 1-3 não pode ser mais longo que o atual em mais
  de uma linha.
- Determinismo: os testes não dependem de rede, de git nem de ordem de
  execução; leem só arquivos do repositório.

### Requisitos transversais (sweep, herdados da SPEC)

Autorização, observabilidade, falha de dependência externa e limite de
volume/rate: n/a (só edita texto de YAML, um template e testes locais; sem
runtime, sem rede, volume fixo de 10 templates e 1 regra). Concorrência e
idempotência: RF10 e RF06 (kit e central idênticos por `cmp`;
`render_prompts.py` rodado duas vezes seguidas produz zero diff). Validação
de entrada: RF04 e RF09.

### Fora de escopo

- Trocar PRD/Tech Spec em outras seções do YAML (capabilities nas linhas
  880, 884, 896, 904, 906, 922; red flag da seção 14 na linha 1077; corpo
  da seção 14 na linha 1101; seção 15 `gate_content_quality`, linhas
  1119-1184).
- Menções legítimas de legado, que ficam como estão: linhas 58-72, 209,
  224, 294-316, 375-411, 476-477, 501, 540-551, 685-698, 723, 870.
- Editar `render_prompts.py` (esta SDD só o executa; `sync_copies` não passa
  a sincronizar templates).
- Migrar o changelog do YAML para o `CHANGELOG.md` (RFC-DTF-0009) e
  remover a duplicação física do bundle (RFC-DTF-0009).
- Paridade de scripts e do YAML entre bundle e original (já existe).
- Passo de CI que rode `_framework/tests/` (SPEC-DTF-0019, RF04).

## Especificação técnica consolidada

Três edições de conteúdo e dois testes novos, sem tocar código de produção
do kit; depois replicar no central.

### Texto-alvo dos passos 1-3 (norma; copiar daqui)

```
      1. Verificar se a SPEC aplicável (conforme
         decision_gates.rfc_to_adr já decidiu) existe no repositório
         central. Se não existir, CRIÁ-LA PRIMEIRO — antes de qualquer
         linha de código — seguindo o fluxo normal (seção 3).
      2. Verificar se a SDD correspondente já foi compilada no
         repositório do projeto (decision_gates.spec_to_sdd). Se não
         existir, COMPILÁ-LA PRIMEIRO — antes de qualquer linha de
         código.
      3. Só depois de SPEC e SDD existirem (podem ser criadas na mesma
         sessão, não precisam de dias de intervalo — o gate é de ORDEM,
         não de tempo de espera) a IA pode começar a escrever código.
      Em projeto legado (sob 1.x), o par PRD + Tech Spec ocupa o lugar
      da SPEC nos passos 1 e 3, como já declara decision_gates.spec_to_sdd.
```

`not_sufficient_alone`: "ADR registra a decisão (o "porquê"); a SPEC
registra o requisito (o "o quê") e o desenho executável (o "como"); SDD
compila SPEC (+ ADR) para consumo direto de IA de implementação. Pular
SPEC/SDD e implementar a partir só do ADR é a violação…".
`if_user_asks_to_skip`: "…sem SPEC/SDD. Confirmado o pedido, a IA registra
na SPEC (quando for criada depois, se for) que nasceu retroativa…".
`relationship_with_audit`: "…pular a ordem SPEC/SDD → código…".

Banner: título "13. GATE OBRIGATÓRIO: NENHUMA IMPLEMENTAÇÃO PULA SPEC/SDD" e
"(SPEC/SDD) exista ANTES da implementação".

Bloco `framework`: `version: "2.3.1"`, `last_updated` = data da
implementação, `changelog[0]` com `version: "2.3.1"`, `date` igual a
`last_updated` e `summary` citando SPEC-DTF-0017 e RFC-DTF-0008, "correção
de texto, sem mudança de comportamento, não-retroativa".

### Contratos técnicos

**Consumes** (nomes exatos, já existentes):
- YAML `_framework/rules/workflow-rules.yaml`: chave de topo
  `gate_implementation_before_code` com os campos `iron_law`, `red_flags`,
  `applies_to`, `rule`, `not_sufficient_alone`, `if_user_asks_to_skip`,
  `relationship_with_audit`, `exception`; chave de topo `decision_gates`
  com as subchaves `rfc_to_adr`, `spec_to_sdd`; bloco `framework` com
  `name`, `version`, `last_updated`, `changelog[]` (cada item com
  `version`, `date`, `summary`).
- `render_prompts.py` (CLI): `python3 _framework/scripts/render_prompts.py`
  (regenera `FULL_TARGETS` e `sync_copies`) e `... --check` (sai com código
  != 0 se algum alvo divergir).
- `framework_lib.load_rules`, `framework_lib.find_rules_file` (não usadas
  pelos testes novos; os testes carregam o YAML direto com
  `yaml.safe_load` para não depender de `sys.path`).

**Produces:**
- `_framework/tests/test_gate_texto.py`:
  ```python
  RULES_PATH: Path  # REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
  LEGACY_ANCHOR: str = "Em projeto legado (sob 1.x)"
  LEGACY_PATTERN: re.Pattern = re.compile(r"PRD|Tech Spec|\bTS\b")

  def _gate() -> dict: ...                                    # yaml.safe_load(...)["gate_implementation_before_code"]
  def test_gate_regra_sem_prd_ts_como_passo() -> None: ...    # RF01, RF02, RF03(âncora), RF04
  def test_gate_referencias_decision_gates_existem() -> None: ...  # RF01, RF04
  ```
  `test_gate_regra_sem_prd_ts_como_passo`: `rule.count(LEGACY_ANCHOR) == 1`;
  `LEGACY_PATTERN.search(rule.split(LEGACY_ANCHOR)[0]) is None`; idem
  (texto inteiro) para `not_sufficient_alone`, `if_user_asks_to_skip`,
  `relationship_with_audit`; e `"SPEC" in` cada um dos passos 1 e 3
  (checa `"SPEC"` em `rule`).
  `test_gate_referencias_decision_gates_existem`:
  `re.findall(r"decision_gates\.(\w+)", rule)` não vazio e todo item ∈
  `yaml.safe_load(...)["decision_gates"].keys()`.
- `_framework/tests/test_template_parity.py`:
  ```python
  TEMPLATES_DIR: Path = REPO_ROOT / "_framework" / "templates"
  BUNDLE_TEMPLATES_DIR: Path = REPO_ROOT / "_framework" / "skills" / "doc-traceability-framework" / "templates"

  def _templates_md(directory: Path) -> list[str]: ...        # sorted(p.name for p in directory.glob("*.md"))
  def _divergentes(original_dir: Path, bundle_dir: Path) -> list[str]: ...
      # nomes de *.md de original_dir ausentes ou com bytes diferentes em bundle_dir
  def test_sdd_template_paridade() -> None: ...               # RF08: mesmo molde de test_ci_gate_verify_sdd_paridade
  def test_templates_md_paridade() -> None: ...               # RF09: assert _divergentes(TEMPLATES_DIR, BUNDLE_TEMPLATES_DIR) == []
  def test_bundle_sem_template_orfao() -> None: ...           # RF09: set(_templates_md(bundle)) <= set(_templates_md(original))
  def test_divergentes_detecta_diferenca(tmp_path) -> None: ...  # sensor: fixtures em tmp_path (igual, diferente, ausente) => lista exata
  ```
  Estilo dos dois arquivos: o de `_framework/tests/test_kit_parity.py`
  (`REPO_ROOT = Path(__file__).resolve().parents[2]`, funções `test_*`
  planas, leitura por `read_bytes()`/`yaml.safe_load`).
- Alterações de dados: bloco `framework` (`version: "2.3.1"`,
  `last_updated`, novo item `changelog[0]`), campos de texto do gate.

### Tratamento de erro por contrato

| Caso | RF relacionado | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| YAML ilegível ou chave `gate_implementation_before_code` ausente | RF04 | `KeyError`/`yaml.YAMLError` propagado: o teste falha, nunca passa em silêncio | `_gate()` em `test_gate_texto.py` |
| Âncora de legado ausente ou duplicada | RF03, RF04 | `assert rule.count(LEGACY_ANCHOR) == 1` com mensagem explícita | `test_gate_regra_sem_prd_ts_como_passo` |
| Chave `decision_gates.<x>` inexistente | RF01, RF04 | `assert` lista as chaves inexistentes | `test_gate_referencias_decision_gates_existem` |
| Regra sem nenhuma referência `decision_gates.` | RF04 | `assert` falha (lista vazia não é "tudo existe") | `test_gate_referencias_decision_gates_existem` |
| Template sem gêmeo, bundle sem pasta, ou bytes diferentes | RF08, RF09 | `assert` com o nome dos arquivos divergentes | `_divergentes` + `test_templates_md_paridade` |
| Template órfão no bundle | RF09 | `assert` com o nome do órfão | `test_bundle_sem_template_orfao` |
| Artefato gerado desatualizado | RF06, RF10 | `render_prompts.py --check` sai != 0 com "divergente"; corrige regenerando | `render_prompts.py` (existente) |
| Cópias kit×central divergem | RF10 | `cmp` sai != 0 no critério 12; corrigir espelhando | critério de aceite 12 |

### Estratégia de teste

| RF-ID / contrato | Tipo de teste | Mock? | Arquivo de teste |
|---|---|---|---|
| RF01 | Unitário de texto do YAML + comandos dos critérios 1/2 | Não | `_framework/tests/test_gate_texto.py` (`test_gate_regra_sem_prd_ts_como_passo`, `test_gate_referencias_decision_gates_existem`) |
| RF02 | Unitário de texto do YAML + comando do critério 3 | Não | `_framework/tests/test_gate_texto.py` (`test_gate_regra_sem_prd_ts_como_passo`) |
| RF03 | Comparação de YAML contra a `main` (critério 4) + âncora no teste | Não | `_framework/tests/test_gate_texto.py` (âncora); critério 4 (`git show main:`) |
| RF04 | Mutação: reintroduzir "PRD e/ou Tech Spec" no YAML e ver o teste falhar (critério 5) | Não | `_framework/tests/test_gate_texto.py` |
| RF05 | Critério 6 (leitura do YAML) | Não | (comando de aceite; dado de configuração, não lógica) |
| RF06 | Critérios 7/8 (`render_prompts.py --check` e grep) | Não | `_framework/scripts/render_prompts.py` (verificador existente) |
| RF07 | Critério 9 (`framework_check.py --auto` antes/depois, `git diff --stat`) | Não | `_framework/scripts/framework_check.py` (existente) |
| RF08 | Unitário de bytes + critério 10 | Não | `_framework/tests/test_template_parity.py` (`test_sdd_template_paridade`) |
| RF09 | Unitário com fixtures `tmp_path` + mutação no bundle (critério 11) | Não | `_framework/tests/test_template_parity.py` (`test_templates_md_paridade`, `test_bundle_sem_template_orfao`, `test_divergentes_detecta_diferenca`) |
| RF10 | Critério 12 (`cmp` + `--check` no central) | Não | (comando de aceite) |

### Plano de implementação

Ordem obrigatória (dependência com a SPEC-DTF-0016: esta primeiro).

1. Branch `sdd/SDD-DTF-0042-<slug>` no repositório do kit, a partir de
   `main`; nunca commit em `main`.
2. Rodar os critérios 1, 10 e o `grep` do critério 8 na `main` e guardar a
   saída real ("antes") na Evidência.
3. `_framework/rules/workflow-rules.yaml`: aplicar o "Texto-alvo" nos
   campos `rule`, `not_sufficient_alone`, `if_user_asks_to_skip`,
   `relationship_with_audit` e nos dois comentários-banner normativos
   (título da seção 13 e o parágrafo "para que a especificação … exista
   ANTES"); atualizar o bloco `framework`.
4. `cp _framework/templates/sdd.template.md
   _framework/skills/doc-traceability-framework/templates/sdd.template.md`.
5. Criar `_framework/tests/test_gate_texto.py` e
   `_framework/tests/test_template_parity.py` conforme os contratos.
6. `python3 _framework/scripts/render_prompts.py` (regenera `AGENTS.md`,
   `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, prompts e a
   cópia do YAML no bundle), depois `--check`.
7. Rodar critérios 2-9, 11, 13 e 14 e registrar comando e saída reais.
8. Replicar no central (RF10): copiar os 5 arquivos editados/criados,
   rodar `render_prompts.py` e `--check` lá, rodar o critério 12.
9. PR por repositório; verificação independente (`sdd-verifier`) em sessão
   separada antes de `implemented`.

### Riscos operacionais e rollout

- Disputa de arquivo com SPEC-DTF-0016 (`workflow-rules.yaml`, gerados):
  0042 implementada e mergeada antes; 0016 rebaseia sobre a 2.3.1.
- Cláusula de legado lida como passo novo: âncora
  `Em projeto legado (sob 1.x)` e teste exigindo uma única ocorrência.
- Teste novo em `_framework/tests/` fora do CI (o workflow
  `framework-check.yml` só roda `_framework/scripts/tests/`): critério 13
  roda os dois diretórios localmente; o passo de CI é da SPEC-DTF-0019.
- Bump de patch inédito: decisão 4 fixa `2.3.1`; critério 6 usa esse número.
- Rollout por PR no kit e PR no central, mesma mudança. Rollback: reverter
  o PR (YAML volta à 2.3.0 e os gerados voltam junto); não toca projeto
  mapeado. Sem feature flag. Sem observabilidade nova: o sinal é a saída
  dos testes e de `render_prompts.py --check`.

## Decomposição em tasks

Formato lido por `parallel_plan.py` (`python3 _framework/scripts/parallel_plan.py docs/sdd/SDD-DTF-0042.md`): colunas `#`, Task, RF(s), Arquivos tocados (separados por vírgula) e Depende de. Caminhos do repositório central levam o prefixo `doc-traceability-central/` para não colidirem com os do kit.

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Capturar "antes" na `main` (critérios 1, 8 e 10) e criar a branch de implementação | RF07, RF08 | (decisão pura) | |
| 2 | Editar `gate_implementation_before_code`, banners da seção 13 e bloco `framework` (2.3.1) | RF01, RF02, RF03, RF05 | `_framework/rules/workflow-rules.yaml` | 1 |
| 3 | Espelhar `sdd.template.md` original no bundle da skill | RF08 | `_framework/skills/doc-traceability-framework/templates/sdd.template.md` | 1 |
| 4 | Criar teste de regressão de texto do gate | RF04 | `_framework/tests/test_gate_texto.py` | 2 |
| 5 | Criar teste de paridade de templates | RF08, RF09 | `_framework/tests/test_template_parity.py` | 3 |
| 6 | Regenerar gerados com `render_prompts.py` e rodar `--check` | RF06 | `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/prompts/copilot/copilot-instructions.md`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml` | 2 |
| 7 | Rodar critérios 2-9, 11, 13 e 14 no kit e registrar saída real | RF01-RF09 | (decisão pura) | 4, 5, 6 |
| 8 | Espelhar no central: copiar os 5 arquivos, regenerar gerados da raiz do central, `--check` e critério 12 | RF10 | `doc-traceability-central/_framework/rules/workflow-rules.yaml`, `doc-traceability-central/_framework/templates/sdd.template.md`, `doc-traceability-central/_framework/skills/doc-traceability-framework/templates/sdd.template.md`, `doc-traceability-central/_framework/tests/test_gate_texto.py`, `doc-traceability-central/_framework/tests/test_template_parity.py`, `doc-traceability-central/AGENTS.md`, `doc-traceability-central/QUICKSTART.md`, `doc-traceability-central/CHANGELOG.md`, `doc-traceability-central/docs/especificacao.md`, `doc-traceability-central/_framework/prompts/universal.md`, `doc-traceability-central/_framework/prompts/cursor/doc-framework.mdc`, `doc-traceability-central/_framework/prompts/copilot/copilot-instructions.md`, `doc-traceability-central/_framework/skills/doc-traceability-framework/references/workflow-rules.yaml` | 7 |

Nota sobre o item 8: os gerados da raiz do central ficam listados porque o
`render_prompts.py` do central os reescreve; se `--check` no central já sair
0 sem diff nesses arquivos, eles não entram no commit. Verificado em 2026-09-25 no central: `AGENTS.md`, `QUICKSTART.md`,
`CHANGELOG.md` e `docs/especificacao.md` existem na raiz do central e
`render_prompts.py --check` roda lá com os mesmos alvos (`FULL_TARGETS`,
caminhos relativos a `_framework/`); a lista acima está correta.

## Critérios de aceite / definição de pronto

Executar na raiz do kit (`cd /home/michel/doc-traceability-framework`),
salvo o critério 12. "Antes" = na `main`, antes de qualquer edição;
"Depois" = na branch de implementação, após RF01-RF10. Cada comando roda de
fato e a saída real vai para a Evidência.

Coluna "Perfil esperado": `automatizado`, `manual` ou `n/a`, conforme o
template. O perfil declarado aqui é comparado com o "Perfil usado" da
Evidência (SDD-DTF-0036).

Script `GATE` usado nos critérios 1-3 (comando único, `python3 - <<'EOF'`):

```python
import re, sys, yaml
y = yaml.safe_load(open("_framework/rules/workflow-rules.yaml"))
g = y["gate_implementation_before_code"]
pat = re.compile(r"PRD|Tech Spec|\bTS\b")
bad = [k for k in ("rule", "not_sufficient_alone", "if_user_asks_to_skip", "relationship_with_audit")
       if pat.search(g[k].split("Em projeto legado (sob 1.x)")[0])]
print("campos com PRD/TS:", bad)
print("cita prd_ts_to_sdd:", "decision_gates.prd_ts_to_sdd" in g["rule"])
print("prd_ts_to_sdd existe:", "prd_ts_to_sdd" in y["decision_gates"])
print("cita spec_to_sdd:", "decision_gates.spec_to_sdd" in g["rule"])
sys.exit(1 if bad else 0)
```

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | Prova a contradição ANTES (RF01, RF02) | `GATE` na `main` | Saída: `campos com PRD/TS: ['rule', 'not_sufficient_alone', 'if_user_asks_to_skip', 'relationship_with_audit']`, `cita prd_ts_to_sdd: True`, `prd_ts_to_sdd existe: False`, `cita spec_to_sdd: False`; código de saída 1 | automatizado |
| 2 | Prova a ausência DEPOIS (RF01, RF02) | `GATE` na branch | `campos com PRD/TS: []`, `cita prd_ts_to_sdd: False`, `cita spec_to_sdd: True`; código de saída 0 | automatizado |
| 3 | Testes de regressão do texto (RF01-RF04) | `python3 -m pytest _framework/tests/test_gate_texto.py -v` | 2 passed; 0 failed | automatizado |
| 4 | Nada mais mudou no YAML (RF03) | `git show main:_framework/rules/workflow-rules.yaml > "$TMPDIR/main.yaml" && python3 -c "import yaml,sys; a=yaml.safe_load(open('$TMPDIR/main.yaml')); b=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); [d.pop(k) for d in (a,b) for k in ('framework','gate_implementation_before_code')]; print(a==b); sys.exit(0 if a==b else 1)"` (sem `TMPDIR`, usar o diretório temporário da sessão) | Imprime `True`, código de saída 0 | automatizado |
| 5 | Sensor do RF04: o teste discrimina | Com a mudança commitada na branch: `sed -i 's/Verificar se a SPEC aplicável/Verificar se PRD e\/ou Tech Spec aplicáveis/' _framework/rules/workflow-rules.yaml`; `python3 -m pytest _framework/tests/test_gate_texto.py -q`; reverter com `git checkout -- _framework/rules/workflow-rules.yaml`; rodar o pytest de novo | Com a mutação: `test_gate_regra_sem_prd_ts_como_passo` FAILED; após reverter: 2 passed | automatizado |
| 6 | Versão e changelog (RF05) | `python3 -c "import yaml; f=yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))['framework']; print(f['version'], f['changelog'][0]['version'], f['last_updated']==f['changelog'][0]['date'])"` | `2.3.1 2.3.1 True` | automatizado |
| 7 | Gerados em dia (RF06, idempotência) | `python3 _framework/scripts/render_prompts.py && python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | Última linha `exit=0`; nenhuma linha com "divergente" | automatizado |
| 8 | Ausência da instrução velha nos gerados (RF06) | `grep -c "PRD e/ou Tech Spec" docs/especificacao.md _framework/prompts/universal.md _framework/skills/doc-traceability-framework/references/workflow-rules.yaml`; ANTES na `main`: `docs/especificacao.md:1` (verificado em 2026-09-24) | Depois: `:0` nos três arquivos | automatizado |
| 9 | Não-retroatividade (RF07) | `python3 _framework/scripts/framework_check.py --auto; echo "exit=$?"` antes e depois; `git diff --stat main -- 'docs/**/registry.yaml' 'docs/**/registry.md' examples/` | Mesmo `exit` antes e depois; `git diff --stat` sem nenhuma linha | automatizado |
| 10 | Prova a divergência ANTES e a paridade DEPOIS (RF08) | `cmp _framework/templates/sdd.template.md _framework/skills/doc-traceability-framework/templates/sdd.template.md; echo "exit=$?"` | ANTES: `... differ: byte ...` e `exit=1` (o `diff` mostra os hunks `69,78c69,70` e `103,104c111,122`); DEPOIS: sem saída do `cmp` e `exit=0` | automatizado |
| 11 | Paridade de templates verde e sensor (RF09) | (a) `python3 -m pytest _framework/tests/test_template_parity.py -v`; (b) sensor: `echo x >> _framework/skills/doc-traceability-framework/templates/adr.template.md`, rodar (a) de novo, depois desfazer a linha (`sed -i '$ d' ...` no mesmo arquivo) e rodar (a) uma terceira vez | (a) 4 passed; (b) `test_templates_md_paridade` FAILED com `adr.template.md` na mensagem; terceira execução 4 passed | automatizado |
| 12 | Espelho no central (RF10) | Em `/home/michel/doc-traceability-central`: `for f in rules/workflow-rules.yaml templates/sdd.template.md skills/doc-traceability-framework/templates/sdd.template.md tests/test_gate_texto.py tests/test_template_parity.py; do cmp /home/michel/doc-traceability-framework/_framework/$f _framework/$f && echo "igual $f"; done; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | 5 linhas `igual ...` e `exit=0` | automatizado |
| 13 | Nenhuma regressão da suíte existente (todos os RF) | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | 0 failed | automatizado |
| 14 | Cache fora da árvore rastreada (higiene) | `git status --porcelain \| grep -E "__pycache__\|\.pytest_cache" ; echo "exit=$?"` | Nenhuma linha listada (`exit=1` do `grep`); se listar, é da frente E da RFC-DTF-0008 e vira nota na SDD, não falha desta | manual (motivo: depende do `.gitignore` da frente E, fora desta SDD) |

## Instruções específicas para a IA implementadora

- **Sessão e branch:** implementar em sessão separada, aberta no repositório
  do kit (`doc-traceability-framework`), nunca na sessão do central. Branch
  nomeada pelo id que originou o trabalho, `sdd/SDD-DTF-0042-<slug>`
  (ex.: `sdd/SDD-DTF-0042-defasagens-gate-spec`), criada a partir de `main`,
  levada a `main` por PR. Nunca commit de implementação direto em `main`.
- **Commit:** cada commit/PR carrega `Refs: SDD-DTF-0042` (e
  `SPEC-DTF-0017`) no corpo; é o vínculo com o código.
- **Ordem entre SDDs:** esta SDD vem primeiro (0042 → 0043 → SDD de
  SPEC-DTF-0020). Se SPEC-DTF-0016 já estiver implementada, parar e pedir
  decisão humana (caso de borda registrado acima).
- **Arquivos esperados:** só os das tasks 2-6 no kit e da task 8 no central.
  `_framework/tests/test_gate_texto.py` e
  `_framework/tests/test_template_parity.py` seguem os contratos literais da
  seção "Contratos técnicos" (nomes de constante, função e teste).
- **Não editar à mão** os gerados (`AGENTS.md`, `QUICKSTART.md`,
  `CHANGELOG.md`, `docs/especificacao.md`, `_framework/prompts/*`) nem a
  cópia `references/workflow-rules.yaml` do bundle: só via
  `render_prompts.py`. O `sdd.template.md` do bundle é copiado do original
  (`cp`), nunca o inverso.
- **Não alterar:** `render_prompts.py` (só executar), qualquer outra seção
  do YAML além de `framework` e `gate_implementation_before_code`, os
  comentários que narram o incidente EVM (linhas 979 e 1062), qualquer
  `registry.yaml`/`registry.md`, `examples/`, documentos de projeto mapeado.
  Não adicionar dependência nova.
- **Testes obrigatórios:** os 2 do `test_gate_texto.py` e os 4 do
  `test_template_parity.py`; cada teste falha por `assert` explícito, nunca
  passa por "nada a comparar".
- **Legado:** as menções legítimas de PRD/TS em outras seções do YAML ficam
  intactas (Fora de escopo); o critério 4 as protege.
- **Verificação:** o implementador não marca `implemented`. A verificação
  roda com o agente `sdd-verifier` em sessão separada da que implementou,
  registrando na Evidência o comando e a saída reais de cada critério, o
  sensor de discriminação e a asserção `file:line`.
- **Falha preexistente:** se `framework_check.py --auto` já falhar antes da
  mudança, registrar na Evidência (critério 9) como preexistente.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções:
- [ ] Todo requisito consolidado acima (RF01-RF10) tem código
      correspondente (nada da SPEC ficou de fora).
- [ ] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", na "Decomposição em tasks" ou nas "Instruções
      específicas" — arquivo não listado é escopo a registrar aqui ou scope
      creep a remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado.

## Evidência de verificação (preencher antes de status `implemented`)

Implementação rodada em 2026-09-25 (branch `sdd/SDD-DTF-0042-defasagens`). Evidência abaixo registrada pelo implementador; a verificação independente e a marcação `implemented` cabem ao `sdd-verifier` em sessão separada.

**Verificador independente:** o `sdd-verifier` registra aqui `sim` ou `não — mesma sessão que implementou` ao rodar a verificação

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Critério sem teste automatizado: escreva "sem
teste", nunca marque como verificado por leitura de código.

Coluna "Assertion (file:line)": caminho e linha exatos da asserção (não do
comando) que resolve o critério. Critério `manual` ou `n/a`: `n/a`. Coluna
"Perfil usado": repita o "Perfil esperado" do critério correspondente, ou
declare divergência com justificativa entre parênteses.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|
| 1 | `python3 /tmp/gate.py` (GATE) na `main` | ANTES: `campos com PRD/TS: ['rule', 'not_sufficient_alone', 'if_user_asks_to_skip', 'relationship_with_audit']`, `cita prd_ts_to_sdd: True`, `prd_ts_to_sdd existe: False`, `cita spec_to_sdd: False`; exit=1 | n/a | sim | n/a | automatizado |
| 2 | `python3 /tmp/gate.py` (GATE) na branch | `campos com PRD/TS: []`, `cita prd_ts_to_sdd: False`, `prd_ts_to_sdd existe: False`, `cita spec_to_sdd: True`; exit=0 | n/a | sim | `_framework/tests/test_gate_texto.py:34` | automatizado |
| 3 | `python3 -m pytest _framework/tests/test_gate_texto.py -v` | 2 passed in 0.15s | ver 5 | sim | `_framework/tests/test_gate_texto.py:34`, `:43` | automatizado |
| 4 | comparação YAML `git show main:...` vs branch sem `framework`/`gate_implementation_before_code` | `True`, exit=0 | sem teste | sim | n/a | automatizado |
| 5 | sed da mutação; pytest; `git checkout --`; pytest | mutado: `FAILED test_gate_regra_sem_prd_ts_como_passo`, `1 failed, 1 passed`; revertido: `2 passed` | falhou com a mutação | sim | `_framework/tests/test_gate_texto.py:34` | automatizado |
| 6 | `python3 -c "..."` (framework.version etc.) | `2.3.1 2.3.1 True` | sem teste | sim | n/a | automatizado |
| 7 | `render_prompts.py && render_prompts.py --check` | 0 linhas "divergente"; exit=0; `git status` sem diff extra | sem teste | sim | n/a | automatizado |
| 8 | `grep -c "PRD e/ou Tech Spec" ...` | ANTES (main): `docs/especificacao.md:1`, `references/workflow-rules.yaml:1`, `universal.md:0`; DEPOIS: `:0` nos três | sem teste | sim | n/a | automatizado |
| 9 | `framework_check.py --auto` antes/depois; `git diff --stat origin/main -- 'docs/**/registry.yaml' 'docs/**/registry.md' examples/` | exit=0 antes e depois; diff vazio contra `origin/main` (contra a `main` local, desatualizada, aparecia diff de registry alheio a esta SDD) | sem teste | sim | n/a | automatizado |
| 10 | `cmp` original vs bundle do `sdd.template.md` | ANTES: `differ: byte 2863, line 69`, exit=1; DEPOIS: sem saída, exit=0 | ver 11 | sim | `_framework/tests/test_template_parity.py:29` | automatizado |
| 11 | `pytest _framework/tests/test_template_parity.py -v`; sensor `echo x >> adr.template.md` no bundle | (a) 4 passed; sensor: `FAILED test_templates_md_paridade` com `['adr.template.md']`, `1 failed, 3 passed`; após desfazer: 4 passed | falhou com a mutação | sim | `_framework/tests/test_template_parity.py:37` | automatizado |
| 12 | `cmp` x5 + `render_prompts.py --check` em `/home/michel/dtf-central-wt-0042` (worktree do central, PR central #138) | 5 linhas `igual ...`; exit=0 | sem teste | sim | n/a | automatizado |
| 13 | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | 186 passed in 29.05s | sem teste | sim | n/a | automatizado |
| 14 | `git status --porcelain \| grep -E "__pycache__\|\.pytest_cache"` | nenhuma linha; exit=1 do grep | n/a | sim | n/a | manual (motivo: depende do `.gitignore` da frente E) |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0017 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0017.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
| RF-IDs cobertos | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10 |
| Versão alvo do framework | 2.3.1 |
| Ordem entre SDDs | SDD-DTF-0042 → SDD-DTF-0043 → SDD de SPEC-DTF-0020 |
