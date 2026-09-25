---
id: SDD-DTF-0048
type: SDD
title: "Fechar a defasagem PRD/Tech Spec do YAML do kit: fluxo, gates 14, 15 e 17, capabilities e teste de regressão"
status: in_review
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-25"
updated: "2026-09-25"
relates_to: [SDD-DTF-0042]
source_docs:
  - id: "SPEC-DTF-0021"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0021.md"
  - id: "RFC-DTF-0008"
    url: "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md"
consumption_instructions: "Compilada da SPEC-DTF-0021 (approved), continuação da SDD-DTF-0042 (frente B da RFC-DTF-0008). Esta SDD carrega a tabela linha a linha das 75 linhas T/L/H, o texto-alvo e os 15 critérios A01 a A15 com comandos e saídas esperadas idênticos aos da SPEC; leia a SPEC-DTF-0021 inteira antes de implementar, e em qualquer divergência a SPEC manda. Implementar em sessão separada, no repositório do kit, em branch sdd/SDD-DTF-0048-*, com worktree próprio criado à mão; editar só o YAML (nunca os gerados à mão), criar o teste novo, regenerar com render_prompts.py e depois espelhar no central, também em worktree próprio. Rodar cada critério de fato e registrar comando e saída reais; verificação por sdd-verifier em sessão separada antes de implemented."
supersedes: null
superseded_by: null
tags: [otimizacao-llm, defasagem, prd-ts, gate_content_quality]
---

# Fechar a defasagem PRD/Tech Spec do YAML do kit: fluxo, gates 14, 15 e 17, capabilities e teste de regressão

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. Vive no repositório de código deste projeto (o kit
> `doc-traceability-framework`) porque é o único documento pensado para
> ser lido pela IA no momento de implementar. Fonte normativa:
> SPEC-DTF-0021 (Partes 1 e 2). Em qualquer divergência, a SPEC manda.

## Resumo executivo

O YAML do kit (`_framework/rules/workflow-rules.yaml`, framework 2.3.1)
ainda apresenta PRD e Tech Spec como passo do fluxo novo em 36 linhas
(68 ocorrências), enquanto o `iron_law`, o `AGENTS.md` e o `SKILL.md` já
dizem SPEC. O item mais grave é `gate_content_quality` (seção 15,
aplicado antes de todo `in_review`), cujo banner, `applies_to` e `rule`
mandam revisar "PRD/TS/SDD". Esta SDD troca essas 36 linhas por SPEC (seções
1, 2, 3, 3c, 4, 11, 12, 14, 15 e 17), mantém as 39 linhas de legado e
histórico byte a byte, acrescenta uma única cláusula de legado sob 1.x na
seção 15, sobe o framework para 2.3.2 (patch, texto puro, não-retroativo,
sem entrada em `RULE_SINCE`), cria o teste de regressão
`_framework/tests/test_prd_ts_texto.py` (4 testes e sensor de mutação),
regenera os gerados com `render_prompts.py` e espelha tudo na cópia
`_framework/` do repositório central. Continuação da SDD-DTF-0042, que
tratou só `gate_implementation_before_code`. Métrica de sucesso herdada da
RFC-DTF-0008: a contagem do critério A01 sai de `(36, 68)` para `(0, 0)`.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — a SPEC-DTF-0021 é sizing `medium` (`parent_adr: null`): nenhum
critério de `decision_gates.rfc_to_adr` se aplica, pois é só texto de regra
já decidida na v2.0.0. A RFC-DTF-0008 é contexto (`relates_to` da SPEC), não
origem, e dispensou ADR via gate. Decisões registradas na SPEC-DTF-0021
(2026-09-25, sujeitas à revisão do humano na aprovação), aplicáveis aqui:

1. **Escopo ampliado.** Além das seções 3, 13, 14, 15 e 17, inclui a seção
   12 (capabilities) e nove linhas das seções 1, 2, 3c, 4 e 11 (as 9 linhas
   de RF06), pelo mesmo critério de classificação (passo ou exemplo do
   fluxo novo). Das 36 linhas T: 10 na seção 15, 7 na 12, 4 na 17, 3 na 3,
   3 na 14 e 9 fora delas. Se o humano preferir o escopo estrito, RF06 sai e
   as 9 linhas passam a âncoras de legado no teste.
2. **Seção 13 não recebe edição.** Só restam nela as linhas 991
   (narrativa do incidente EVM) e 1039 (cláusula de legado da SPEC-DTF-0017).
3. **Narrativas do incidente EVM (linhas 991 e 1076) ficam.** Registram o
   que aconteceu sob 1.x. A troca de "PRD/TS/SDD já no lugar" vale para a
   red flag (1091), o `applies_to` (1100) e a `rule` (1115), não para a
   origem histórica.
4. **Versão 2.3.2, sem entrada nova em `RULE_SINCE`.** Nenhum validador lê
   o texto de `rule`, `applies_to` ou `description` do YAML; `version_date`
   consulta só as versões 1.7.0, 2.0.0, 2.2.0 e 2.3.0 do changelog, então uma
   entrada 2.3.2 no topo não move nenhuma data de corte. Entrada só é
   necessária quando o bump adiciona checagem mecanizada (caso do `sweep`
   em 2.3.0).
5. **Prefixos de texto de `render_prompts.py` ficam para SPEC própria.** O
   residual conhecido (`doc-framework.mdc` linhas 43, 44 e 84; prefixo
   "(v1.7.0)" do universal) vem de código Python; o critério A10 registra
   que permanece.
6. **`framework_version` do `docs/DTF/registry.yaml` sobe depois**, em PR
   de documento separado, como na PR #146 para a 2.3.1.
7. **Teste novo em arquivo novo** (`test_prd_ts_texto.py`), sem estender
   `test_gate_texto.py`, que fica byte a byte como a SDD-DTF-0042 o deixou.
8. **Escopo do teste por seções não isentas**, não por lista de seções
   escaneadas. Isentas: 0, 3b, 6, 8, 9 e 19.

## Requisitos consolidados

Caminhos relativos à raiz do repositório do kit
(`doc-traceability-framework`); os mesmos valem no central (RF12). "Linha" é
a linha do YAML 2.3.1 antes da mudança.

| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |
|---|---|---|---|
| RF01 | Seção 3 (fluxo textual): as linhas 375, 376 e 381 passam a "ADR -> SPEC -> SDD", "SPEC -> SDD" e "antes da SPEC". | Quando o YAML alterado for lido, o sistema deve apresentar zero ocorrências de PRD, Tech Spec ou TS entre o banner `# 3.` e o banner `# 3b.`. | `_framework/rules/workflow-rules.yaml` |
| RF02 | Seção 14 (`gate_branch_before_commit`): a red flag da linha 1091, o `applies_to` da linha 1100 e o item 4 de `rule` (linha 1115) trocam PRD/TS por SPEC. A narrativa do incidente EVM na linha 1076 fica (decisão 3). | O sistema deve manter, nos campos `red_flags.patterns[2].flag`, `applies_to` e `rule` de `gate_branch_before_commit`, zero ocorrências de PRD, Tech Spec ou TS. | `_framework/rules/workflow-rules.yaml` |
| RF03 | Seção 15 (`gate_content_quality`): o banner passa a "QUALIDADE DE CONTEÚDO DA SPEC E DA SDD"; comentário de motivação (linhas 1136-1137), `applies_to` (1164-1165) e `rule` (1167, 1179, 1183, 1196, 1198) trocam PRD/TS/Tech Spec por SPEC. O `applies_to` ganha uma única cláusula final "Em projeto legado (sob 1.x), PRD e Tech Spec ocupam o lugar da SPEC." O aviso da linha 1178 ("Em PRD legado (projeto sob 1.x) isto é aviso, não erro") fica. | O sistema deve conter, na seção 15, exatamente uma ocorrência da âncora `Em projeto legado (sob 1.x), PRD e Tech Spec ocupam o lugar da SPEC` e nenhuma outra ocorrência de PRD, Tech Spec ou TS fora da linha 1178. | `_framework/rules/workflow-rules.yaml` |
| RF04 | Seção 17 (`handover_protocol`): comentários das linhas 1324 e 1328, `artifact.location` (1349) e `content_rule` (1355) trocam PRD/TS por SPEC ("compila SPEC/SDD", "SPEC pendente", "SDD-X, SPEC-X"). | O sistema deve manter, entre o banner `# 17.` e o banner `# 18.`, zero ocorrências de PRD, Tech Spec ou TS. | `_framework/rules/workflow-rules.yaml` |
| RF05 | Seção 12 (`capabilities`): as descrições das linhas 892, 896, 908, 916, 918, 934 e o `trigger` da linha 970 trocam PRD/TS/Tech Spec por SPEC. Sem alterar `id`, `mechanization`, `enforcement_patterns` nem `procedure`. | O sistema deve manter, entre o banner `# 12.` e o banner `# 13.`, zero ocorrências de PRD, Tech Spec ou TS, com os mesmos `id` de capability e a mesma lista de chaves por capability. | `_framework/rules/workflow-rules.yaml` |
| RF06 | Demais passos ou exemplos do fluxo novo fora dos gates: o exemplo `cross_repo_reference.format` (236) vira `SPEC-CHECKOUT-0002` em `03-spec`; `SDD.purpose` (320), `PM.purpose` (363), `rfc_to_adr.description` (457), `onboarding.what_not_to_do` (552, 554), os dois passos de `phase_2_cutover` (561, 563) e o non_goal de auditoria (882) trocam por SPEC. | O sistema deve manter, fora das seções isentas (0, 3b, 6, 8, 9, 19), zero ocorrências de PRD, Tech Spec ou TS que não estejam numa âncora de legado ou de histórico da tabela de classificação. | `_framework/rules/workflow-rules.yaml` |
| RF07 | Nada além de texto muda: as 39 linhas de legado e histórico (tabela de classificação, classes L e H) ficam byte a byte; a seção 13 não recebe nenhuma edição; nenhuma chave, lista ou valor não textual do YAML muda, exceto o bloco `framework` (RF08). | Quando o YAML da branch for comparado com o da `main`, o sistema deve apresentar a mesma estrutura de chaves e listas, valores não textuais idênticos e diferença apenas nas 22 folhas de texto listadas em "Contratos técnicos" mais o bloco `framework`. | `_framework/rules/workflow-rules.yaml` |
| RF08 | Como o YAML muda, `framework.version` sobe de `2.3.1` para `2.3.2` (patch, texto puro, mesmo raciocínio da SPEC-DTF-0017), `framework.last_updated` recebe a data da implementação e `framework.changelog` ganha a entrada `2.3.2` no topo, citando SPEC-DTF-0021, dizendo que é correção de texto sem mudança de comportamento e não-retroativa. | Quando a SDD desta SPEC for implementada, o sistema deve apresentar `framework.version == "2.3.2"`, `framework.changelog[0].version == "2.3.2"`, `framework.changelog[1].version == "2.3.1"` e `framework.last_updated == framework.changelog[0].date`. | `_framework/rules/workflow-rules.yaml` |
| RF09 | Todos os artefatos gerados do YAML são regenerados com `render_prompts.py`, sem edição à mão: `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, `_framework/prompts/*`, a cópia do YAML no bundle da skill, `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md` e `docs/guias/guia-tecnico.md`. | Quando `python3 _framework/scripts/render_prompts.py --check` rodar após a regeneração, o sistema deve sair com código 0, e `docs/especificacao.md` deve conter no máximo uma linha com as expressões de passo antigo do critério A10 (a de `onboarding.applies_when`, âncora de legado). | `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, `docs/guias/guia-tecnico.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`, `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md` |
| RF10 | A mudança não é retroativa: nenhum registry, front-matter ou documento de projeto mapeado é alterado, nenhum script de validação é alterado, nenhuma entrada nova é criada em `RULE_SINCE` (decisão 4) e a validação dos projetos mapeados sob 1.x (ABSTRACTCLINIC, 1.4.0) e sob 2.x tem o mesmo resultado antes e depois. | O sistema deve produzir, para `framework_check.py --auto` e para `validate_doc.py` sobre cada documento de `docs/ABSTRACTCLINIC`, os mesmos códigos de saída e a mesma saída antes e depois, e `git diff` não deve listar `docs/**/registry.yaml`, `docs/**/registry.md`, `examples/` nem `_framework/scripts/*.py`. | (decisão pura) |
| RF11 | Um teste de regressão de texto reprova PRD/Tech Spec/TS como passo em qualquer seção não isenta do YAML (o que cobre 3, 12, 13, 14, 15 e 17), lendo o texto bruto para pegar também comentários, com âncoras explícitas de legado e de histórico, e com sensor de mutação. | Se o YAML reintroduzir PRD, Tech Spec ou TS numa seção não isenta fora das âncoras, então o sistema deve falhar `test_yaml_sem_prd_ts_como_passo`; se o detector deixar de detectar uma ocorrência injetada, então o sistema deve falhar `test_ocorrencias_proibidas_detecta_mutacao`. | `_framework/tests/test_prd_ts_texto.py` |
| RF12 | Toda alteração de RF01 a RF11 é aplicada também na cópia `_framework/` do repositório central (`doc-traceability-central`), com os gerados regenerados lá, e o `--check` do central passa. | Quando `cmp` comparar cada arquivo tocado no kit com o mesmo caminho no central, o sistema deve reportar arquivos idênticos, e `python3 _framework/scripts/render_prompts.py --check` no central deve sair com código 0. | `_framework/rules/workflow-rules.yaml`, `_framework/tests/test_prd_ts_texto.py`, `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`, `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, `docs/guias/guia-tecnico.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc` |
| RF13 | Ordem com a SDD-DTF-0049 (frente paralela que altera `render_indexes.py` e `kit-index.yaml` e não toca o YAML): as duas mudanças regeneram `_framework/rules/workflow-rules.map.md` e `_framework/INDEX.md`; quem mergear depois rebaseia sobre `main` e regenera com `render_prompts.py`, sem resolver conflito de arquivo gerado à mão. | Quando a segunda das duas mudanças for rebaseada sobre a `main` que já contém a primeira, o sistema deve sair com código 0 em `python3 _framework/scripts/render_prompts.py --check` sem que nenhum arquivo gerado tenha sido editado à mão. | `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md` |

### Casos de borda / condições de erro

| Caso | RF relacionado | Comportamento esperado |
|---|---|---|
| Comentário histórico do incidente EVM que cita PRD/TS (linha 991 na seção 13 e linha 1076 na seção 14) | RF02, RF07, RF11 | Fica intacto e está no conjunto de âncoras do teste (`com PRD/TS/SDD já no lugar`, `PRD, Tech Spec e SDD só foram escritos DEPOIS`); trocá-lo falsificaria a narrativa de um incidente que ocorreu sob 1.x |
| Texto dentro de blocos legados (`legacy_document_types`, seção 3b; esquema de front-matter, seção 8; escopo do registry, seção 9; ciclo de vida, seção 6) | RF07, RF11 | Seções inteiras isentas no teste; ficam byte a byte |
| Legado citado em seção não isenta (`replaces`, `parent_types`, `spec_to_sdd`, cláusula de legado do gate 13, aviso do item 1 da seção 15) | RF07, RF11 | Cada linha está numa âncora explícita (`ALLOWED_FRAGMENTS`); o teste exige que cada âncora ainda exista no YAML, para a lista não apodrecer |
| Projeto sob 1.x (ABSTRACTCLINIC, 1.4.0) e projeto que subir de versão depois | RF10 | Nenhum validador lê texto de regra do YAML; `RULE_SINCE` só mapeia checagens mecanizadas; documento antigo não é reprovado (decisão 4, critério A12) |
| Ocorrência em comentário YAML, que `yaml.safe_load` descarta | RF11 | O teste lê o texto bruto linha a linha; o teste `test_gate_texto.py` da SDD-DTF-0042 continua cobrindo só os campos parseados do gate 13 |
| Banner de seção renomeado ou removido, e o detector passa a tratar linhas de uma seção como "seção 0" | RF11 | `test_secoes_isentas_e_escaneadas` falha se algum id isento ou obrigatório (3, 12, 13, 14, 15, 17) deixar de existir como banner |
| A cláusula de legado da seção 15 duplicada ou ausente | RF03, RF11 | `test_ancoras_de_legado_existem` exige exatamente uma ocorrência da âncora da seção 15 |
| Variante de escrita ("tech spec" em minúsculas, "TECH SPEC" em caixa alta) | RF11 | O padrão é o mesmo do `test_gate_texto.py` (`PRD`, `Tech Spec`, `TS` inteiro). As variantes existentes (linhas 398, 406, 407, 422, 423) estão só nas seções 0 e 3b, isentas, verificado em 2026-09-25 |
| `--check` falha por gerado desatualizado | RF09 | Rodar `render_prompts.py` sem `--check` e commitar o resultado; nunca editar gerado à mão |
| Bump de versão colide com outra SDD que subiu para 2.3.2 antes | RF08 | Rebasear e usar o próximo patch livre; o critério A08 lê o número real da `main` (ver Riscos) |
| `framework_check.py --auto` já falha antes da mudança | RF10 | O critério compara resultado antes e depois; falha preexistente não é atribuída a esta SDD, mas é registrada nela |
| Texto novo mais longo que o atual | RF01 a RF06 | Não pode crescer mais que 20 linhas no total (uma cláusula de legado mais o changelog), porque o YAML é lido inteiro por LLM |

### Requisitos não funcionais

- Nenhuma dependência nova: o teste usa stdlib, `pytest` e `PyYAML` (já
  usados por `test_gate_texto.py`).
- Determinismo: o teste não depende de rede, de git nem de ordem de
  execução; lê só o YAML do repositório.
- Custo de leitura: a troca de PRD/Tech Spec por SPEC não pode aumentar o
  YAML em mais de 20 linhas (a RFC-DTF-0008 é sobre reduzir custo de
  leitura), e o teto de `render_indexes.py` (mapa mais maior seção abaixo
  de 15% do YAML) continua respeitado, verificado pelo `--check`.

### Requisitos transversais (sweep, herdados da SPEC)

Autorização, observabilidade, falha de dependência externa e limite de
volume/rate: n/a (só edita texto de YAML e cria um teste local; sem
runtime, sem rede, tamanho fixo de um YAML de cerca de 1500 linhas e 13
âncoras). Concorrência: RF13 (disputa por `workflow-rules.map.md` e
`INDEX.md` com a SDD-DTF-0049) e RF12 (kit e central). Idempotência: RF09
(`render_prompts.py` rodado duas vezes seguidas produz zero diff; o
critério A09 roda `--check` logo após a regeneração). Validação de entrada:
RF11 (o teste valida o texto do YAML contra as âncoras e falha se banner
isento ou obrigatório sumir; o sensor prova que o detector discrimina).

### Fora de escopo

- Alterar qualquer gate, critério, `sizing`, ciclo de status ou
  front-matter (só texto e comentários).
- Trocar as 23 linhas de legado e as 16 linhas de histórico (changelog,
  incidente EVM, custo observado na seção 19): ficam, com âncora no teste.
- Prefixos de texto escritos à mão dentro de `render_prompts.py`
  (`build_universal` e `build_cursor_mdc`): o `doc-framework.mdc` ainda diz
  "ADR -> PRD+TS -> SDD" (linhas 43-44) e "(SDD-X, TS-X)" (linha 84), e o
  prefixo do universal carrega "(v1.7.0)". Vêm de código Python, não do
  YAML; vira SPEC própria (decisão 5). Esta SDD não edita
  `render_prompts.py`, só o executa. Portanto `doc-framework.mdc` não é
  editado à mão em nenhuma hipótese.
- O comentário das linhas 99-102 de `validate_doc.py`, que cita o texto
  antigo `applies_to: "PRD, Tech Spec e SDD"`: comentário em código, sem
  efeito; `CONTENT_GATE_TYPES` já inclui SPEC, PRD, TS e SDD e não muda.
- `_framework/procedures/*.md`, `SKILL.md` e templates: já dizem SPEC; a
  SPEC-DTF-0018 os reorganiza.
- Subir `framework_version` no `docs/DTF/registry.yaml` para 2.3.2: passo
  separado e posterior, em PR de documento próprio no central (decisão 6).
- Migrar o changelog do YAML para o `CHANGELOG.md` (RFC-DTF-0009).

## Especificação técnica consolidada

Duas edições de conteúdo, um teste novo e regeneração, sem tocar código de
produção do kit; depois replicar no central. O CI do kit já roda
`python3 -m pytest _framework/tests/` (SPEC-DTF-0019), então o teste novo
entra no CI sem mudar workflow.

Fonte da tabela de classificação: a SPEC-DTF-0021, seção "Classificação
linha a linha (YAML 2.3.1)", copiada integralmente abaixo (75 linhas, 136
ocorrências), de modo que cada linha de troca T seja rastreável sem
depender de outra leitura. Classes: **T** = passo ou exemplo do fluxo novo,
troca por SPEC; **L** = legado legítimo, fica; **H** = histórico, fica.
"Seção" é o banner do YAML (0 = preâmbulo com o bloco `framework`). A
implementadora ainda assim lê a SPEC inteira (ver "Instruções").

### Classificação linha a linha (YAML 2.3.1)

| Linha | Seção | Trecho | Classe | Ação ou motivo |
|---|---|---|---|---|
| 25 | 0 | changelog 2.3.1 cita "PRD" ao descrever a SPEC-DTF-0017 | H | fica: entrada de changelog |
| 26 | 0 | idem, "Tech Spec" | H | fica |
| 70 | 0 | changelog 2.0.0: "PRD e TS saem de" | H | fica |
| 80 | 0 | changelog 2.0.0: "PRD e Tech Spec fundem-se no tipo SPEC" | H | fica |
| 84 | 0 | changelog 2.0.0: "PRD e TS seguem" | H | fica |
| 100 | 0 | changelog: incidente, "que PRD/TS/SDD existissem" | H | fica |
| 105 | 0 | changelog: "Templates de PRD/Tech Spec/SDD ganham" | H | fica |
| 118 | 0 | changelog: handover, "(PRD/TS/SDD)" | H | fica |
| 124 | 0 | changelog: "mesmo com PRD/TS/SDD" | H | fica |
| 138 | 0 | changelog: EVM "sem PRD/Tech Spec/SDD" | H | fica |
| 142 | 0 | changelog: "antes de PRD/TS (central)" | H | fica |
| 172 | 0 | changelog 1.0.0: "ADR->PRD/TS->SDD" | H | fica |
| 202 | 1 | comentário da topologia: "mais PRD e TS em projeto legado sob 1.x" | L | fica: já diz legado |
| 221 | 1 | `central_repo.contains`: "PRD e TS em projeto legado" | L | fica: já diz legado |
| 236 | 1 | exemplo `format`: id `PRD-CHECKOUT-0002`, pasta `03-prd` | T | `SPEC-CHECKOUT-0002`, pasta `03-spec` (RF06) |
| 306 | 2 | `SPEC.purpose`: "substitui o par PRD + Tech Spec" | L | fica: define a SPEC pelo que ela substitui |
| 315 | 2 | `SPEC.replaces` com PRD e TS | L | fica: dado estrutural |
| 320 | 2 | `SDD.purpose`: "compilado a partir de PRD + Tech Spec" | T | "compilado a partir da SPEC" (RF06) |
| 328 | 2 | `SDD.parent_types` com PRD e TS | L | fica: dado estrutural, legado precisa ser aceito |
| 363 | 2 | `PM.purpose`: "novas RFCs ou PRDs/Tech Specs" | T | "novas RFCs ou SPECs" (RF06) |
| 375 | 3 | fluxo: "ADR -> PRD + Tech Spec -> SDD" | T | "ADR -> SPEC -> SDD" (RF01) |
| 376 | 3 | fluxo: "PRD + Tech Spec -> SDD" | T | "SPEC -> SDD" (RF01) |
| 381 | 3 | "antes de PRD/Tech Spec" | T | "antes da SPEC" (RF01) |
| 387 | 3b | banner de tipos legados: "PRD e TS saíram de document_types" | L | fica: seção 3b isenta |
| 391 | 3b | "ids PRD-* e TS-* já emitidos" | L | fica |
| 397 | 3b | chave `PRD:` | L | fica |
| 402 | 3b | `deprecation_note` do PRD | L | fica |
| 411 | 3b | chave `TS:` | L | fica |
| 412 | 3b | `name: "Tech Spec (legado)"` | L | fica |
| 415 | 3b | `deprecation_note` do TS | L | fica |
| 457 | 3c | `rfc_to_adr.description`: "seguir para PRD/Tech Spec" | T | "seguir para a SPEC" (RF06) |
| 488 | 3c | `spec_to_sdd`: "sob 1.x, o par PRD + Tech Spec ocupa o lugar da SPEC" | L | fica: já diz legado |
| 489 | 3c | `spec_to_sdd.trigger`: "em projeto legado, PRD.status ..." | L | fica: já diz legado |
| 513 | 4 | `onboarding.applies_when`: "histórico de STRAT/RFC/ADR/PRD/TS" | L | fica: lista os tipos que um projeto sob 1.x pode ter |
| 552 | 4 | `what_not_to_do`: "Não reconstruir PRD ou Tech Spec" | T | "Não reconstruir SPEC" (RF06) |
| 554 | 4 | `what_not_to_do`: "no como (PRD/TS)" | T | "no como (SPEC)" (RF06) |
| 561 | 4 | `phase_2_cutover` 1: "numeração ... para RFC, PRD, TS e SDD" | T | "para RFC, SPEC e SDD" (RF06) |
| 563 | 4 | `phase_2_cutover` 2: "gate de decisão, PRD/Tech Spec, e a primeira SDD" | T | "gate de decisão, SPEC, e a primeira SDD" (RF06) |
| 633 | 6 | banner do ciclo de vida: lista de tipos com PRD, TS | L | fica: seção 6 isenta, o ciclo vale para os tipos legados |
| 675 | 8 | `type: enum[... PRD, TS ...]` | L | fica: seção 8 isenta, enum precisa aceitar legado |
| 697 | 8 | chave `PRD:` de `type_specific_fields` | L | fica |
| 700 | 8 | chave `TS:` de `type_specific_fields` | L | fica |
| 710 | 8 | `SDD.source_docs`: "PRD(s)/TS(s) em projeto ainda mapeado sob 1.x" | L | fica: já diz sob 1.x |
| 735 | 9 | `central_registry.scope` com PRD, TS | L | fica: seção 9 isenta |
| 882 | 11 | `audit.non_goals`: "Não reconstruir PRD/Tech Spec de commits passados" | T | "Não reconstruir SPEC de commits passados" (RF06) |
| 892 | 12 | `evaluate_rfc_gate`: "direto PRD/TS" | T | "direto SPEC" (RF05) |
| 896 | 12 | `compile_sdd`: "a partir de PRD + Tech Spec" | T | "a partir da SPEC" (RF05) |
| 908 | 12 | `triage_postmortem_action_items`: "vira PRD/TS direto" | T | "vira SPEC direto" (RF05) |
| 916 | 12 | `enforce_implementation_gate`: "PRD/TS/SDD aplicáveis" | T | "SPEC/SDD aplicáveis" (RF05) |
| 918 | 12 | `enforce_branch_before_commit`: "SDD/PRD/TS/ADR" | T | "SDD/SPEC/ADR" (RF05) |
| 934 | 12 | `enforce_content_quality_gate`: "mover PRD, Tech Spec ou SDD" | T | "mover SPEC ou SDD" (RF05) |
| 970 | 12 | `write_handover.trigger`: "(PRD/TS/SDD compilados)" | T | "(SPEC e SDD compilados)" (RF05) |
| 991 | 13 | comentário do incidente EVM: "PRD, Tech Spec e SDD só foram escritos DEPOIS" | H | fica: narrativa de fato ocorrido sob 1.x |
| 1039 | 13 | cláusula "Em projeto legado (sob 1.x), o par PRD + Tech Spec" | L | fica: âncora da SPEC-DTF-0017 |
| 1076 | 14 | comentário do incidente EVM: "com PRD/TS/SDD já no lugar" | H | fica: narrativa (decisão 3) |
| 1091 | 14 | red flag: "Já tenho PRD/TS/SDD prontos" | T | "Já tenho SPEC/SDD prontos" (RF02) |
| 1100 | 14 | `applies_to`: "SDD/PRD/TS/ADR já compilada" | T | "SDD/SPEC/ADR já compilada" (RF02) |
| 1115 | 14 | `rule` item 4: "(RFC/ADR/PRD/TS/SDD)" | T | "(RFC/ADR/SPEC/SDD)" (RF02) |
| 1133 | 15 | banner: "QUALIDADE DE CONTEÚDO DO PRD/TECH SPEC/SDD" | T | "QUALIDADE DE CONTEÚDO DA SPEC E DA SDD" (RF03) |
| 1136 | 15 | comentário: "Um PRD" | T | "Uma SPEC" (RF03) |
| 1137 | 15 | comentário: "ou Tech Spec podem existir" | T | reescrito no singular: "... pode existir, estar approved e ser vaga o bastante" (RF03) |
| 1164 | 15 | `applies_to`: "PRD, Tech Spec e SDD, nesta ordem" | T | "SPEC e SDD, nesta ordem" (RF03) |
| 1165 | 15 | `applies_to`: "qualidade do PRD/TS de onde foi compilada" | T | "qualidade da SPEC de onde foi compilada" mais a cláusula de legado (RF03) |
| 1167 | 15 | `rule`: "mover PRD/TS/SDD de draft" | T | "mover SPEC/SDD de draft" (RF03) |
| 1178 | 15 | item 1: "Em PRD legado (projeto sob 1.x) isto é aviso, não erro" | L | fica: já diz legado |
| 1179 | 15 | item 2: "contrato técnico (Tech Spec)" | T | "(SPEC, Parte 2)" (RF03) |
| 1183 | 15 | item 3: "(PRD: ...; Tech Spec: ...)" | T | "(SPEC: "Casos de borda / condições de erro")", igual ao heading do template (RF03) |
| 1196 | 15 | item 6: "em nenhum PRD/TS de source_docs" | T | "em nenhuma SPEC de source_docs" (RF03) |
| 1198 | 15 | item 6: "empobrecer o que o PRD/TS já continha" | T | "o que a SPEC já continha" (RF03) |
| 1324 | 17 | comentário: "(compila PRD/TS/SDD)" | T | "(compila SPEC/SDD)" (RF04) |
| 1328 | 17 | comentário: "(PRD/TS/SDD inteiros" | T | "(SPEC/SDD inteiros" (RF04) |
| 1349 | 17 | `artifact.location`: "PRD/TS pendentes" | T | "SPEC pendente" (RF04) |
| 1355 | 17 | `content_rule`: "(SDD-X, TS-X, PRD-X)" | T | "(SDD-X, SPEC-X)" (RF04) |
| 1440 | 19 | comentário: "STRAT, RFC, ADR, PRD, TS e SDD" (funil até a v1.7.0) | H | fica: seção 19 isenta, custo observado sob 1.x |
| 1441 | 19 | comentário: "RFC 293 + PRD 137 + TS 190" | H | fica |

Contagem (verificada por script sobre o YAML 2.3.1, com o padrão
`PRD|Tech Spec|\bTS\b`):

| Classe | Linhas | Ocorrências |
|---|---|---|
| T (troca por SPEC) | 36 | 68 |
| L (legado legítimo) | 23 | 38 |
| H (histórico) | 16 | 30 |
| Total | 75 | 136 |

Distribuição das 36 linhas T por seção: seção 1 (1), seção 2 (2), seção 3
(3), seção 3c (1), seção 4 (4), seção 11 (1), seção 12 (7), seção 14 (3),
seção 15 (10), seção 17 (4).

### Texto-alvo (norma; copiar daqui)

Seção 3, comentário do fluxo:

```
#   Strategy Doc -> RFC -> [GATE: exige ADR?]
#       -> sim: ADR -> SPEC -> SDD (no repo do projeto)
#       -> não: SPEC -> SDD (no repo do projeto)
```

e a linha 381 passa a "# antes da SPEC. Agora existe um gate explícito."

Seção 15, banner e `applies_to`:

```
# 15. GATE OBRIGATÓRIO: QUALIDADE DE CONTEÚDO DA SPEC E DA SDD
  applies_to: >
    SPEC e SDD, nesta ordem — a qualidade de uma SDD depende
    diretamente da qualidade da SPEC de onde foi compilada.
    Em projeto legado (sob 1.x), PRD e Tech Spec ocupam o lugar da SPEC.
```

A âncora da cláusula de legado cabe numa só linha do arquivo (`Em projeto
legado (sob 1.x), PRD e Tech Spec ocupam o lugar da SPEC.`), porque o teste
compara por linha. Seção 15, `rule`, item 3: `(SPEC: "Casos de borda /
condições de erro")`.

Seção 14, red flag: `- flag: "Já tenho SPEC/SDD prontos, o gate está
cumprido."`. Seção 17, `content_rule`: `(SDD-X, SPEC-X)`.

Entrada de changelog (o `summary` não pode conter as expressões do critério
A02, para o grep de A02 seguir exato):

```
    - version: "2.3.2"
      date: "<data da implementação, igual a framework.last_updated>"
      summary: >
        SPEC-DTF-0021: correção de texto, sem mudança de comportamento,
        não-retroativa. Seção 3 (fluxo), seção 12 (capabilities), seções
        14, 15 e 17 e mais oito trechos deixam de apresentar PRD e
        Tech Spec como passo do fluxo novo e passam a SPEC; cláusula de
        legado sob 1.x preservada. Nenhum gate, critério, sizing, ciclo
        de status ou front-matter muda. Teste de regressão
        test_prd_ts_texto.py.
```

Na entrada acima, `<data da implementação, igual a framework.last_updated>`
é a instrução de qual valor gravar (a data real do dia da implementação, no
formato `YYYY-MM-DD`), não um valor a manter literal.

### Contratos técnicos (APIs, eventos, schemas)

**Consumes** (nomes exatos, já existentes):

- YAML `_framework/rules/workflow-rules.yaml`: bloco `framework` com
  `version`, `last_updated`, `changelog[]` (cada item com `version`,
  `date`, `summary`); banners no formato `# <id>. <título>` entre linhas
  de `#` repetido (mesmo formato lido por `render_indexes.py`, constante
  `BANNER_RE`); âncora de legado da SPEC-DTF-0017, `Em projeto legado
  (sob 1.x)`, no campo `rule` de `gate_implementation_before_code`.
- `framework_lib.rule_applies_since_date` e `version_date`
  (`_framework/scripts/framework_lib.py`, linhas 231 e 242): consultam só as
  entradas de changelog das versões de `RULE_SINCE`, nunca a mais recente.
- `validate_doc.RULE_SINCE` (`_framework/scripts/validate_doc.py`) e
  `validate_state.RULE_SINCE` (`_framework/scripts/validate_state.py`): não
  editados.
- `render_prompts.py` (CLI): `python3 _framework/scripts/render_prompts.py`
  regenera `FULL_TARGETS`, `sync_copies` e `generate_all` (mapa de seções,
  `INDEX.md`, sumários); `... --check` sai com código diferente de 0 se
  algum alvo divergir.

**Produces:**

- Folhas de texto do YAML alteradas (22, caminho no formato do critério
  A07), além do bloco `framework` e de 8 linhas de comentário (375, 376,
  381, 1133, 1136, 1137, 1324, 1328):
  `repository_topology.cross_repo_reference.format`,
  `document_types.SDD.purpose`, `document_types.PM.purpose`,
  `decision_gates.rfc_to_adr.description`,
  `onboarding.phase_1_baseline.what_not_to_do`,
  `onboarding.phase_2_cutover.steps[0].action`,
  `onboarding.phase_2_cutover.steps[1].action`, `audit.non_goals[2]`,
  `capabilities[1].description`, `capabilities[3].description`,
  `capabilities[9].description`, `capabilities[11].description`,
  `capabilities[12].description`, `capabilities[13].description`,
  `capabilities[17].trigger`,
  `gate_branch_before_commit.red_flags.patterns[2].flag`,
  `gate_branch_before_commit.applies_to`, `gate_branch_before_commit.rule`,
  `gate_content_quality.applies_to`, `gate_content_quality.rule`,
  `handover_protocol.artifact.location`, `handover_protocol.content_rule`.
- `_framework/tests/test_prd_ts_texto.py`:

  ```python
  RULES_PATH: Path = REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
  PATTERN: re.Pattern = re.compile(r"PRD|Tech Spec|\bTS\b")     # igual ao LEGACY_PATTERN de test_gate_texto.py
  BANNER: re.Pattern = re.compile(r"^# (\d+[a-z]?)\. ")
  EXEMPT_SECTIONS: frozenset[str] = frozenset({"0", "3b", "6", "8", "9", "19"})
  REQUIRED_SECTIONS: frozenset[str] = frozenset({"3", "12", "13", "14", "15", "17"})
  ALLOWED_FRAGMENTS: tuple[str, ...]   # 13 âncoras de legado e histórico, uma por linha L/H de seção não isenta

  def ocorrencias_proibidas(text: str) -> list[tuple[int, str, str]]: ...
      # (linha, seção, conteúdo) de cada linha fora de EXEMPT_SECTIONS que casa PATTERN
      # e não contém nenhum ALLOWED_FRAGMENTS; seção = último banner visto, "0" antes do primeiro
  def resumo(text: str) -> tuple[int, int]: ...
      # (nº de linhas, nº de ocorrências de PATTERN nessas linhas) de ocorrencias_proibidas(text)

  def test_yaml_sem_prd_ts_como_passo() -> None: ...            # RF01-RF06, RF11: ocorrencias_proibidas(YAML) == []
  def test_ancoras_de_legado_existem() -> None: ...             # RF03, RF11: toda âncora aparece >= 1x; a da seção 15 exatamente 1x
  def test_secoes_isentas_e_escaneadas() -> None: ...           # RF11: ids de EXEMPT_SECTIONS e REQUIRED_SECTIONS existem como banner
  def test_ocorrencias_proibidas_detecta_mutacao() -> None: ... # RF11: sensor com fixtures em memória e mutação do YAML real
  ```

  As 13 âncoras de `ALLOWED_FRAGMENTS`: `em projeto legado sob 1.x`,
  `PRD e TS em projeto legado`, `Documento único que substitui o par PRD
  + Tech Spec`, `replaces: ["PRD", "TS"]`, `parent_types: ["SPEC", "PRD",
  "TS", "ADR"]`, `sob 1.x, o par PRD + Tech Spec ocupa o lugar da SPEC`,
  `em projeto legado, PRD.status == approved AND TS.status == approved`,
  `STRAT/RFC/ADR/PRD/TS neste framework`, `PRD, Tech Spec e SDD só foram
  escritos DEPOIS`, `Em projeto legado (sob 1.x), o par PRD + Tech Spec`,
  `com PRD/TS/SDD já no lugar`, `Em PRD legado (projeto sob 1.x)` e
  `Em projeto legado (sob 1.x), PRD e Tech Spec ocupam o lugar da SPEC`.

  `test_ocorrencias_proibidas_detecta_mutacao` afirma: um texto `# 14. T`
  seguido da linha `x PRD y` retorna uma ocorrência na seção `14`; o mesmo
  conteúdo sob `# 3b. T` retorna `[]`; a mesma linha antes de qualquer
  banner retorna `[]`; uma linha que contém uma âncora retorna `[]`; e o
  YAML real com `Já tenho SPEC/SDD prontos` trocado por `Já tenho
  PRD/TS/SDD prontos` retorna `resumo == (1, 2)` (a troca só é feita depois
  de `assert` de que o trecho existe).

- Alterações de dados: bloco `framework` (`version: "2.3.2"`,
  `last_updated`, novo `changelog[0]`); nenhuma entrada em `RULE_SINCE`.

### Tratamento de erro por contrato

| Caso | RF relacionado | Comportamento esperado | Onde é tratado |
|---|---|---|---|
| YAML ilegível ou inexistente | RF11 | Exceção propagada: o teste falha, nunca passa em silêncio | `test_yaml_sem_prd_ts_como_passo` em `_framework/tests/test_prd_ts_texto.py` |
| Ocorrência nova fora das âncoras | RF11 | `assert` lista linha, seção e conteúdo de cada ocorrência | `test_yaml_sem_prd_ts_como_passo` |
| Âncora de legado ausente ou, na seção 15, duplicada | RF03, RF11 | `assert` com o texto da âncora | `test_ancoras_de_legado_existem` |
| Banner renomeado, seção isenta ou obrigatória some | RF11 | `assert` lista os ids ausentes | `test_secoes_isentas_e_escaneadas` |
| Detector deixa de detectar | RF11 | `assert` falha na fixture ou na mutação do YAML real | `test_ocorrencias_proibidas_detecta_mutacao` |
| Estrutura do YAML muda além do texto | RF07 | O critério A07 sai com código 1 e imprime o caminho divergente | critério A07 |
| Artefato gerado desatualizado | RF09, RF12, RF13 | `render_prompts.py --check` sai com código diferente de 0 e "divergente"; corrige regenerando | `_framework/scripts/render_prompts.py` (existente) |
| Cópias kit e central divergem | RF12 | `cmp` sai com código diferente de 0 no critério A13; corrigir espelhando | critério A13 |
| Resultado de validação de projeto mapeado muda | RF10 | O `diff` do critério A12 não é vazio; a mudança é revertida e investigada | critério A12 |

### Estratégia de teste

| RF-ID / contrato | Tipo de teste | Mock? | Arquivo de teste |
|---|---|---|---|
| RF01 a RF06 | Unitário de texto bruto do YAML (`test_yaml_sem_prd_ts_como_passo`) e comandos A01, A02, A03 | Não | `_framework/tests/test_prd_ts_texto.py` |
| RF03 (âncora) | Unitário: âncora da seção 15 exatamente uma vez | Não | `_framework/tests/test_prd_ts_texto.py` (`test_ancoras_de_legado_existem`) |
| RF07 | Comparação estrutural do YAML contra a `main` (comando A07) | Não | (comando de aceite; sem arquivo de teste, dado de configuração) |
| RF08 | Comando A08 (leitura do YAML) | Não | (comando de aceite) |
| RF09 | Comandos A09 e A10 (`render_prompts.py --check` e grep) | Não | `_framework/scripts/render_prompts.py` (verificador existente) |
| RF10 | Comando A12 (`framework_check.py --auto`, `validate_doc.py` sobre ABSTRACTCLINIC, `git diff`) | Não | `_framework/scripts/framework_check.py` e `_framework/scripts/validate_doc.py` (existentes) |
| RF11 | Mutação: reintroduzir PRD/TS numa linha de campo e noutra de comentário (comando A05) e fixtures em memória | Não | `_framework/tests/test_prd_ts_texto.py` (`test_ocorrencias_proibidas_detecta_mutacao`, `test_secoes_isentas_e_escaneadas`) |
| RF12 | Comando A13 (`cmp` e `--check` no central) | Não | (comando de aceite) |
| RF13 | Comando A14 (`--check` após rebase sobre a SDD-DTF-0049) | Não | `_framework/scripts/render_prompts.py` (existente) |

### Plano de implementação

Ordem obrigatória para a parte de geração.

1. Branch `sdd/SDD-DTF-0048-<slug>` no repositório do kit, a partir de
   `main`, em worktree próprio; nunca commit em `main`.
2. Na `main`, antes de qualquer edição, rodar e guardar a saída real
   ("antes"): a parte ANTES de A02, A03, A10 e o `framework_check.py` e o
   laço `validate_doc.py` de A12 (no central).
3. Criar `_framework/tests/test_prd_ts_texto.py` conforme o contrato e rodar
   o `SCAN` de A01 sobre o YAML da `main` (ANTES: `(36, 68)`); o teste
   `test_yaml_sem_prd_ts_como_passo` deve falhar nesse ponto.
4. `_framework/rules/workflow-rules.yaml`: aplicar a tabela de classificação
   (36 linhas T) e o "Texto-alvo": seção 3 (RF01), seção 14 (RF02), seção 15
   com a cláusula de legado (RF03), seção 17 (RF04), seção 12 (RF05) e as 9
   linhas de RF06; não tocar em nenhuma linha L ou H; atualizar o bloco
   `framework` (`version: "2.3.2"`, `last_updated`, `changelog[0]` com
   `date` igual a `last_updated`).
5. `python3 _framework/scripts/render_prompts.py` (regenera gerados, cópia do
   YAML no bundle, mapa, `INDEX.md`, `guia-tecnico.md`), depois `--check`.
6. Rodar A01 a A11 e A15 e registrar comando e saída reais; incluir a saída
   do sensor A05 (falha com a mutação, verde depois de reverter).
7. Replicar no central (RF12), em worktree próprio: copiar o YAML, o teste
   novo e os gerados listados em A13, rodar `render_prompts.py` e `--check`
   lá, rodar A12 e A13.
8. Coordenar com a SDD-DTF-0049 (RF13): a segunda a mergear rebaseia,
   regenera e roda A14.
9. PR por repositório; verificação independente (`sdd-verifier`) em sessão
   separada antes de `implemented`.

### Riscos operacionais e rollout

- **Disputa de arquivos gerados com a SDD-DTF-0049** (`workflow-rules.map.md`
  e `INDEX.md`; ela altera `render_indexes.py` e `kit-index.yaml`, não o
  YAML). Mitigação: RF13 e o critério A14; conflito em arquivo gerado nunca
  é resolvido à mão, sempre regenerando.
- **SPEC-DTF-0018 (skills enxutas) copiar para `references/onboarding.md` e
  `references/audit.md` o texto antigo das seções 4 e 11.** Mitigação: se
  ela for implementada antes, esta SDD faz `grep` das linhas de RF06 nesses
  arquivos e alinha na mesma PR; se depois, a SDD dela copia do YAML já
  corrigido.
- **Bump de versão colidir com outra SDD que suba para 2.3.2 antes.**
  Mitigação: rebasear e usar o próximo patch livre; o critério A08 lê o
  número real da `main`.
- **Lista de âncoras apodrecer ou virar salvo-conduto.** Mitigação:
  `test_ancoras_de_legado_existem` exige que cada âncora ainda exista, e
  cada âncora é uma frase que se declara legado ou histórico.
- **Cláusula de legado da seção 15 ser lida como passo novo.** Mitigação:
  começa por "Em projeto legado (sob 1.x)", a mesma abertura de
  `decision_gates.spec_to_sdd` e do gate 13.
- **Trocar texto de onboarding e auditoria (seções 4 e 11) gerar surpresa.**
  Mitigação: só as 9 linhas de RF06, listadas uma a uma, com o texto novo; a
  decisão 1 registra o motivo.
- Rollout por PR no kit e PR no central, mesma mudança. Rollback: reverter o
  PR (o YAML volta à 2.3.1 e os gerados voltam junto); não toca projeto
  mapeado. Sem feature flag. Sem observabilidade nova: o sinal é a saída de
  `test_prd_ts_texto.py` e de `render_prompts.py --check`. Projetos
  mapeados (EVM em 2.1.0, ABSTRACTCLINIC em 1.4.0, CIMOCLINIC em 2.3.0) não
  mudam.

## Decomposição em tasks

Formato lido por `parallel_plan.py` (`python3 _framework/scripts/parallel_plan.py docs/sdd/SDD-DTF-0048.md`): colunas `#`, Task, RF(s), Arquivos tocados (separados por vírgula) e Depende de. Arquivos do repositório central levam o prefixo `central:` para não colidirem com os do kit.

Ordem entre SDDs: esta SDD é independente da SDD-DTF-0049 (que não toca o
YAML). As duas regeneram `_framework/rules/workflow-rules.map.md` e
`_framework/INDEX.md`: quem mergear depois rebaseia sobre `main` e roda
`render_prompts.py`, sem editar gerado à mão (RF13, task 8).

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Capturar "antes" na `main` (A02, A03, A10 e o laço de A12) e criar a branch e o worktree de implementação | RF07, RF09, RF10 | (decisão pura) | |
| 2 | Criar o teste de regressão de texto e rodar o SCAN de A01 sobre a `main` (esperado `(36, 68)`, teste vermelho) | RF11 | `_framework/tests/test_prd_ts_texto.py` | 1 |
| 3 | Editar o YAML: 36 linhas T (RF01 a RF06), cláusula de legado da seção 15 e bloco `framework` 2.3.2 | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08 | `_framework/rules/workflow-rules.yaml` | 2 |
| 4 | Regenerar gerados com `render_prompts.py` e rodar `--check` | RF09 | `AGENTS.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/especificacao.md`, `docs/guias/guia-tecnico.md`, `_framework/prompts/universal.md`, `_framework/prompts/cursor/doc-framework.mdc`, `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`, `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md` | 3 |
| 5 | Rodar A01 a A11 e A15 no kit e registrar saída real (inclui sensor A05) | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF11 | (decisão pura) | 2, 3, 4 |
| 6 | Espelhar no central (em worktree próprio): copiar YAML e teste, regenerar gerados lá e rodar `--check` | RF12 | `central:_framework/rules/workflow-rules.yaml`, `central:_framework/tests/test_prd_ts_texto.py`, `central:_framework/rules/workflow-rules.map.md`, `central:_framework/INDEX.md`, `central:_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`, `central:AGENTS.md`, `central:QUICKSTART.md`, `central:CHANGELOG.md`, `central:docs/especificacao.md`, `central:docs/guias/guia-tecnico.md`, `central:_framework/prompts/universal.md`, `central:_framework/prompts/cursor/doc-framework.mdc` | 5 |
| 7 | Rodar A12 (não-retroatividade) e A13 (espelho) no central e registrar saída real | RF10, RF12 | (decisão pura) | 6 |
| 8 | Ordem com a SDD-DTF-0049: depois de a primeira das duas entrar em `main`, rebasear a segunda, regenerar mapa e `INDEX.md` com `render_prompts.py` e rodar A14 | RF13 | `_framework/rules/workflow-rules.map.md`, `_framework/INDEX.md` | 4, 7 |

Nota sobre a task 4: se `render_prompts.py` regenerar também
`docs/sdd/INDEX.md` (índice das SDDs), esse arquivo entra na conta do
critério A15, junto da própria `docs/sdd/SDD-DTF-0048.md`; ele nunca é
editado à mão.

## Critérios de aceite / definição de pronto

Executar na raiz do kit (`cd /home/michel/doc-traceability-framework`),
salvo A12 e A13. "Antes" = na `main`, antes de qualquer edição; "Depois" =
na branch de implementação, após RF01 a RF13. Cada comando roda de fato e a
saída real vai para a Evidência. Para os comandos que comparam com a `main`,
`TMPD` é o diretório temporário da sessão. Critérios A01 a A15 da
SPEC-DTF-0021, sem relaxamento: comandos e saídas esperadas idênticos.

Coluna "Perfil esperado": `automatizado`, `manual` ou `n/a`, conforme o
template. O perfil declarado aqui é comparado com o "Perfil usado" da
Evidência (SDD-DTF-0036).

Script `SCAN` usado em A01 (importa o módulo criado por RF11 e aplica ao
YAML da `main`, para provar a contradição ANTES):

```
git show main:_framework/rules/workflow-rules.yaml > "$TMPD/main.yaml"
python3 -c "import sys; sys.path.insert(0, '_framework/tests'); import test_prd_ts_texto as t; print(t.resumo(open('$TMPD/main.yaml', encoding='utf-8').read()))"
```

Script `ESTRUTURA` usado em A07 (comando único, `python3 - <<'EOF'`; o
conjunto `PERMITIDOS` tem os 22 caminhos de "Produces"):

```python
import subprocess, sys, yaml
main = yaml.safe_load(subprocess.check_output(["git", "show", "main:_framework/rules/workflow-rules.yaml"]))
novo = yaml.safe_load(open("_framework/rules/workflow-rules.yaml", encoding="utf-8"))
main.pop("framework"); novo.pop("framework")
difs = []
def walk(a, b, p):
    if type(a) is not type(b):
        sys.exit(f"tipo diverge em {p}")
    if isinstance(a, dict):
        if list(a) != list(b):
            sys.exit(f"chaves divergem em {p}")
        for k in a:
            walk(a[k], b[k], f"{p}.{k}" if p else k)
    elif isinstance(a, list):
        if len(a) != len(b):
            sys.exit(f"tamanho diverge em {p}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{p}[{i}]")
    elif a != b:
        difs.append(p)
walk(main, novo, "")
PERMITIDOS = {
    "repository_topology.cross_repo_reference.format", "document_types.SDD.purpose",
    "document_types.PM.purpose", "decision_gates.rfc_to_adr.description",
    "onboarding.phase_1_baseline.what_not_to_do", "onboarding.phase_2_cutover.steps[0].action",
    "onboarding.phase_2_cutover.steps[1].action", "audit.non_goals[2]",
    "capabilities[1].description", "capabilities[3].description", "capabilities[9].description",
    "capabilities[11].description", "capabilities[12].description", "capabilities[13].description",
    "capabilities[17].trigger", "gate_branch_before_commit.red_flags.patterns[2].flag",
    "gate_branch_before_commit.applies_to", "gate_branch_before_commit.rule",
    "gate_content_quality.applies_to", "gate_content_quality.rule",
    "handover_protocol.artifact.location", "handover_protocol.content_rule",
}
print(len(difs), set(difs) == PERMITIDOS)
sys.exit(0 if set(difs) == PERMITIDOS else 1)
```

Argumentos `ANTIGA` usados em A02 e A10 (array bash, um `-e` por expressão de
passo antigo; equivale à alternância `PRD/TS/SDD`, `PRD/Tech Spec`,
`SDD/PRD/TS/ADR`, `TS-X, PRD-X`, `PRD, Tech Spec e SDD`, `RFC/ADR/PRD/TS`,
`PRDs/Tech Specs` da SPEC; escrito sem o caractere de barra vertical porque
o parser de tabela do `validate_state.py` divide células nele):

```
ANTIGA=(-e 'PRD/TS/SDD' -e 'PRD/Tech Spec' -e 'SDD/PRD/TS/ADR' -e 'TS-X, PRD-X' -e 'PRD, Tech Spec e SDD' -e 'RFC/ADR/PRD/TS' -e 'PRDs/Tech Specs')
```

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| A01 | Prova a contradição ANTES e a ausência DEPOIS, com contagem real (RF01 a RF06, RF11) | Comando `SCAN` acima (ANTES, sobre o YAML da `main`); depois, na branch: `python3 -c "import sys; sys.path.insert(0, '_framework/tests'); import test_prd_ts_texto as t; print(t.resumo(open('_framework/rules/workflow-rules.yaml', encoding='utf-8').read()))"` | ANTES: `(36, 68)`; DEPOIS: `(0, 0)` | automatizado |
| A02 | Prova por grep, fora do preâmbulo, as expressões de passo antigo (RF01 a RF06) | Definir `ANTIGA` (bloco acima); `sed -n '/^# 1\. TOPOLOGIA/,$p' _framework/rules/workflow-rules.yaml > "$TMPD/a02.txt"; grep -cE "${ANTIGA[@]}" "$TMPD/a02.txt"`, na `main` e na branch | ANTES: `19` (linhas 363, 381, 457, 513, 563, 882, 916, 918, 970, 991, 1076, 1091, 1100, 1115, 1164, 1167, 1324, 1328, 1355); DEPOIS: `3` (as linhas 513, 991 e 1076, todas âncoras de legado ou histórico) | automatizado |
| A03 | O banner da seção 15 está em SPEC (RF03) | `grep -n "^# 15\." _framework/rules/workflow-rules.yaml` | ANTES: termina em `DO PRD/TECH SPEC/SDD`; DEPOIS: `QUALIDADE DE CONTEÚDO DA SPEC E DA SDD` | automatizado |
| A04 | Testes de regressão do texto (RF03, RF11) | `python3 -m pytest _framework/tests/test_prd_ts_texto.py -v` | 4 passed; 0 failed | automatizado |
| A05 | Sensor do RF11: o teste discrimina campo e comentário | (a) `sed -i 's/Já tenho SPEC\/SDD prontos/Já tenho PRD\/TS\/SDD prontos/' _framework/rules/workflow-rules.yaml`; `python3 -m pytest _framework/tests/test_prd_ts_texto.py -q`; `git checkout -- _framework/rules/workflow-rules.yaml`. (b) `sed -i 's/(compila SPEC\/SDD)/(compila PRD\/TS\/SDD)/' _framework/rules/workflow-rules.yaml`; mesmo pytest; `git checkout -- ...`. (c) pytest de novo | (a) e (b): `test_yaml_sem_prd_ts_como_passo` FAILED, com a linha e a seção na mensagem; (c): 4 passed. A mutação (b) atinge um comentário, que o `test_gate_texto.py` não vê (esse continua com 2 passed) | automatizado |
| A06 | A SDD-DTF-0042 não regride (RF03, RF07) | `python3 -m pytest _framework/tests/test_gate_texto.py -v` | 2 passed; 0 failed | automatizado |
| A07 | Só texto mudou, e só nas 22 folhas previstas (RF05, RF07) | Script `ESTRUTURA` acima | Imprime `22 True`, código de saída 0; a seção 13 não aparece entre as diferenças | automatizado |
| A08 | Versão e changelog (RF08) | `python3 -c "import yaml; f=yaml.safe_load(open('_framework/rules/workflow-rules.yaml'))['framework']; print(f['version'], f['changelog'][0]['version'], f['changelog'][1]['version'], f['last_updated']==f['changelog'][0]['date'])"` | `2.3.2 2.3.2 2.3.1 True` | automatizado |
| A09 | Gerados em dia e idempotência (RF09) | `python3 _framework/scripts/render_prompts.py && python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | Última linha `exit=0`; nenhuma linha com "divergente" | automatizado |
| A10 | Ausência da instrução velha nos gerados e o residual conhecido (RF09) | Definir `ANTIGA`; `grep -cE "${ANTIGA[@]}" docs/especificacao.md`; `grep -c "PRD + Tech Spec" _framework/rules/workflow-rules.map.md`; `grep -c "PRD+TS" _framework/prompts/cursor/doc-framework.mdc` | ANTES: `6`, `1`, `2`; DEPOIS: `1` (só a linha de `onboarding.applies_when`, âncora de legado), `0`, `2` (o `doc-framework.mdc` vem de texto em `render_prompts.py`, fora de escopo, decisão 5) | automatizado |
| A11 | Nenhuma regressão da suíte existente (todos os RF) | `python3 -m pytest _framework/scripts/tests/ _framework/tests/ -q` | 0 failed | automatizado |
| A12 | Não-retroatividade (RF10) | Em `/home/michel/doc-traceability-central`, na `main` e depois na branch espelhada: `python3 _framework/scripts/framework_check.py --auto > "$TMPD/fc-N.txt" 2>&1; echo "exit=$?"` e `for f in docs/ABSTRACTCLINIC/0*/*.md; do python3 _framework/scripts/validate_doc.py "$f"; echo "$f exit=$?"; done > "$TMPD/abs-N.txt" 2>&1` (N = antes ou depois); `diff` dos pares; `git diff --stat main -- 'docs/**/registry.yaml' 'docs/**/registry.md' examples/ '_framework/scripts/*.py'` | `exit` igual antes e depois (verificado em 2026-09-25 antes: `exit=0` no `framework_check.py --auto`, 17 documentos ABSTRACTCLINIC, todos `exit=0`); os dois `diff` vazios; `git diff --stat` sem nenhuma linha | automatizado |
| A13 | Espelho no central (RF12) | Em `/home/michel/doc-traceability-central`: `for f in rules/workflow-rules.yaml tests/test_prd_ts_texto.py rules/workflow-rules.map.md INDEX.md skills/doc-traceability-framework/references/workflow-rules.yaml prompts/universal.md prompts/cursor/doc-framework.mdc; do cmp /home/michel/doc-traceability-framework/_framework/$f _framework/$f && echo "igual $f"; done; for f in AGENTS.md QUICKSTART.md CHANGELOG.md docs/especificacao.md docs/guias/guia-tecnico.md; do cmp /home/michel/doc-traceability-framework/$f $f && echo "igual $f"; done; python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"` | 12 linhas `igual ...` e `exit=0` | automatizado |
| A14 | Ordem com a SDD-DTF-0049 (RF13) | Com a SDD-DTF-0049 mergeada em `main` (ou esta mudança mergeada antes dela), rebasear a branch que vem depois, rodar `python3 _framework/scripts/render_prompts.py` e depois `python3 _framework/scripts/render_prompts.py --check; echo "exit=$?"`; `git diff --name-only main` | `exit=0`; `workflow-rules.map.md` e `INDEX.md` aparecem no diff só como saída do script (nenhuma edição à mão registrada na SDD) | manual (motivo: depende de a outra frente existir em `main`; a SDD registra qual entrou primeiro e a saída real) |
| A15 | Só os arquivos previstos mudaram (todos os RF) | `git diff --name-only main` no kit | Cada arquivo listado está entre: o YAML, o teste novo, os 10 arquivos gerados listados em RF09, a cópia do YAML no bundle entre eles (a SDD desta SPEC e `docs/sdd/INDEX.md` incluídos); nenhum `_framework/scripts/*.py`, nenhum `registry.yaml`, nenhum `examples/` | automatizado |

## Instruções específicas para a IA implementadora

- **Leitura obrigatória:** ler a SPEC-DTF-0021 inteira (URL em
  `source_docs`) antes de editar. A tabela de 75 linhas desta SDD é cópia
  dela, para rastreio de cada linha T; em qualquer divergência a SPEC manda
  e a divergência é registrada na Evidência.
- **Sessão, branch e worktree:** implementar em sessão separada, aberta no
  repositório do kit (`doc-traceability-framework`), nunca na sessão do
  central. Branch nomeada pelo id que originou o trabalho,
  `sdd/SDD-DTF-0048-<slug>` (ex.: `sdd/SDD-DTF-0048-prd-ts-yaml`), criada a
  partir de `main`, em worktree próprio criado à mão (`git worktree add`),
  levada a `main` por PR. Nunca commit de implementação direto em `main`.
  O espelho no central também roda em worktree próprio, em branch própria e
  PR próprio (o central bloqueia push direto em `main`).
- **Commit:** cada commit/PR carrega `Refs: SDD-DTF-0048` (e
  `SPEC-DTF-0021`) no corpo; é o vínculo com o código.
- **Ordem entre SDDs:** independente da SDD-DTF-0049, que não toca o YAML.
  As duas regeneram `_framework/rules/workflow-rules.map.md` e
  `_framework/INDEX.md`: quem mergear depois rebaseia sobre `main` e roda
  `python3 _framework/scripts/render_prompts.py`; conflito nesses arquivos
  nunca é resolvido à mão. Se outra SDD subir a versão para 2.3.2 antes,
  usar o próximo patch livre e ajustar o critério A08 ao número real.
- **Arquivos esperados:** só os das tasks 2, 3 e 4 no kit e da task 6 no
  central. `_framework/tests/test_prd_ts_texto.py` segue o contrato literal
  da seção "Contratos técnicos" (nomes de constante, função e teste), no
  estilo de `_framework/tests/test_gate_texto.py`.
- **Aplicação das trocas:** só as 36 linhas T da tabela, com o texto-alvo
  indicado; nenhuma linha L ou H é tocada; a seção 13 não recebe nenhuma
  edição; nenhuma chave, lista ou valor não textual muda; o YAML não pode
  crescer mais que 20 linhas.
- **Não editar à mão** os gerados (`AGENTS.md`, `QUICKSTART.md`,
  `CHANGELOG.md`, `docs/especificacao.md`, `docs/guias/guia-tecnico.md`,
  `_framework/prompts/*`, `workflow-rules.map.md`, `INDEX.md`) nem a cópia
  `references/workflow-rules.yaml` do bundle: só via `render_prompts.py`.
- **Não alterar:** `render_prompts.py` (só executar), qualquer
  `_framework/scripts/*.py` (inclusive o comentário das linhas 99-102 de
  `validate_doc.py` e `RULE_SINCE`), o `doc-framework.mdc` à mão (o resíduo
  vem de código Python, decisão 5), `_framework/procedures/*.md`, `SKILL.md`,
  templates, qualquer `registry.yaml`/`registry.md`, `examples/`, documentos
  de projeto mapeado e o `framework_version` de `docs/DTF/registry.yaml`
  (PR de documento separado depois, decisão 6). Nenhuma entrada nova em
  `RULE_SINCE`. Não adicionar dependência nova.
- **Testes obrigatórios:** os 4 de `test_prd_ts_texto.py`
  (`test_yaml_sem_prd_ts_como_passo`, `test_ancoras_de_legado_existem`,
  `test_secoes_isentas_e_escaneadas`,
  `test_ocorrencias_proibidas_detecta_mutacao`), cada um falhando por
  `assert` explícito, nunca passando por "nada a comparar"; e o sensor de
  mutação A05 rodado de fato, com comentário e com campo.
- **Verificação:** o implementador não marca `implemented`. A verificação
  roda com o agente `sdd-verifier` em sessão separada da que implementou,
  registrando na Evidência o comando e a saída reais de cada critério, o
  sensor de discriminação e a asserção `file:line`.
- **Falha preexistente:** se `framework_check.py --auto` já falhar antes da
  mudança, registrar na Evidência (A12) como preexistente.

## Verificação de escopo (nada a mais, nada a menos)

Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima (RF01 a RF13) tem código
      correspondente (nada da SPEC ficou de fora).
- [ ] Todo arquivo tocado pela implementação aparece em "Especificação
      técnica consolidada", na "Decomposição em tasks" ou nas "Instruções
      específicas" — arquivo não listado é escopo a registrar aqui ou scope
      creep a remover antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não foi
      pedido por nenhum requisito consolidado ("já que estava ali").

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou —
quem escreveu o código tem o resultado como conclusão desejada. Para cada
critério da tabela acima: comando rodado de fato nesta sessão e saída real,
nunca "deve passar" nem resultado de memória. Nenhuma linha abaixo foi
executada ainda: a SDD está em `draft` e a implementação não começou.

**Verificador independente:** não — nenhuma verificação rodou ainda (o `sdd-verifier` em sessão separada preenche esta seção depois da implementação)

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável (`git checkout --` / `rm`,
nunca `git stash`), teste tem que FALHAR, e volta ao normal depois. Teste
que passa com a implementação quebrada é ruído verde. Critério sem teste
automatizado: escreva "sem teste", nunca marque como verificado por leitura
de código.

Coluna "Assertion (file:line)": caminho e linha exatos da asserção (não do
comando) que resolve o critério, ou `n/a` para `manual`. Coluna "Perfil
usado": repete o "Perfil esperado" ou declara divergência com justificativa
entre parênteses.

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|---|
| 0 | Fidelidade à origem | `python3 _framework/scripts/check_source_docs.py docs/sdd/SDD-DTF-0048.md /home/michel/doc-traceability-central/docs/DTF` | não executado pelo verificador (rodado apenas na compilação desta SDD, ver relatório do compilador) | n/a | pendente | n/a | automatizado |
| 0 | A01 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A02 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A03 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A04 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A05 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A06 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A07 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A08 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A09 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A10 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A11 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A12 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A13 | não executado (implementação pendente) | não executado | não executado | pendente | não registrada | automatizado |
| 0 | A14 | não executado (depende da SDD-DTF-0049 em main) | não executado | n/a | pendente | n/a | manual (motivo: depende de a outra frente existir em `main`; a SDD registra qual entrou primeiro e a saída real) |
| 0 | A15 | não executado (implementação pendente) | não executado | n/a | pendente | n/a | automatizado |

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | SPEC-DTF-0021 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-spec/SPEC-DTF-0021.md), RFC-DTF-0008 (https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/01-rfc/RFC-DTF-0008.md) |
| RF-IDs cobertos | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13 |
| Versão alvo do framework | 2.3.2 |
| Relação com outras SDDs | continuação da SDD-DTF-0042 (`relates_to`); independente da SDD-DTF-0049, com disputa só de arquivo gerado (RF13) |
