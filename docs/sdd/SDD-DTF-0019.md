---
id: SDD-DTF-0019
type: SDD
title: "verify-sdd: a tabela de evidência vive na SDD e a checagem mecânica na SDD verificada vira passo obrigatório"
status: approved
project: "DTF"
owner: "Michel Pessoa"
created: "2026-09-14"
updated: "2026-09-14"
relates_to: [SDD-DTF-0018]
source_docs: []
sizing: "small"
consumption_instructions: "Sizing small — ausência de SPEC é o registro de que a fase foi pulada. Texto de procedimento (verify-sdd.md) e duas descrições em workflow-rules.yaml; nenhum script muda. Depende de SDD-DTF-0018 mergeada antes (o passo novo manda rodar validate_state.py e precisa dele sem falso positivo). Branch sdd/SDD-DTF-0019-* a partir de main, PR, commits com Refs: SDD-DTF-0019."
supersedes: null
superseded_by: null
tags: [procedimento, gate_scope_verification, verify_sdd]
---

# verify-sdd: a tabela de evidência vive na SDD e a checagem mecânica na SDD verificada vira passo obrigatório

## Resumo executivo

`gate_scope_verification` item 4 (`_framework/rules/workflow-rules.yaml`,
seção 16) exige a tabela "Evidência de verificação" preenchida **na
SDD**, e `validate_state.py` lê exatamente essa tabela. O procedimento
`_framework/procedures/verify-sdd.md` diz isso no passo 2, mas o passo 4
("Veredito") manda escrever `validation.md` com uma cópia da mesma
tabela e não repete que a da SDD continua obrigatória. A descrição da
capacidade `verify_sdd_independently` (`produces`) e a de
`operational_artifacts.validation.md` também só citam o `validation.md`.

Achado real em 2026-09-14 no projeto EVM (`viverMelhor`): SDD-EVM-0013,
0014 e 0015 foram verificadas por sessões independentes, com veredito
PASS registrado em `validation-EVM-00XX.md`, e movidas para
`implemented` com a tabela da SDD vazia e o corpo ainda dizendo "Ainda
não implementado". Uma sessão nova que abre a SDD — o artefato pensado
para ser a verdade autocontida — lê duas afirmações contraditórias. As
sessões do kit fizeram as duas coisas (`SDD-DTF-0017`: tabela na SDD +
ponteiro para `validation.md`), por hábito, não por instrução.

A "Checagem mecânica complementar" do procedimento hoje é opcional,
roda no diretório inteiro (`validate_state.py docs/sdd`) e vem depois de
"`PASS` autoriza mover a SDD para `implemented`". No viverMelhor esse
comando devolvia 27 problemas, 21 falsos positivos (corrigidos em
`SDD-DTF-0018`) — ruído suficiente para ser ignorado.

`sizing: small` — 2 arquivos editados à mão, sem regra nova: alinha a
renderização (procedimento e descrições) ao item 4 do gate, que já está
em vigor. Não é proposta de regra por causa de uma violação
(`lessons_policy`): é inconsistência entre renderizações do mesmo gate,
o tipo de divergência que `check_renderings.py` existe para impedir.

## Decisão(ões) de arquitetura aplicável(is)

Sem ADR — correção de texto normativo, nenhum critério do gate
`rfc_to_adr` se aplica.

## Requisitos consolidados

- **RF1**: O procedimento `verify-sdd.md`, passo 2, deve dizer que a
  tabela "Evidência de verificação" a preencher é a **da própria SDD**, e
  que é essa a lida pelo gate 16 e por `validate_state.py`.
- **RF2**: O passo 4 ("Veredito") deve instruir, antes do modelo de
  `validation.md`, que a seção "Evidência de verificação" da SDD recebe:
  a tabela com uma linha por critério, a linha `**Verificador
  independente:**` e uma linha apontando para o `validation.md` com o
  veredito — e deve dizer explicitamente que `validation.md` complementa
  e não substitui a tabela da SDD.
- **RF3**: O procedimento deve ter um passo 5 obrigatório, "Checagem
  mecânica antes de mudar status", que: (a) muda `status` para
  `implemented` no front-matter e no registry; (b) roda
  `python3 _framework/scripts/validate_state.py <caminho da SDD
  verificada>` só no arquivo verificado; (c) se o exit for diferente de
  0, volta `status` para `approved` antes de qualquer commit e corrige
  a tabela ou a checklist de escopo; (d) só commita com exit 0. A seção
  "Checagem mecânica complementar" atual é absorvida por este passo
  (sem duplicar), mantendo a ressalva "necessário e não suficiente".
- **RF4**: `capabilities.verify_sdd_independently.produces` em
  `workflow-rules.yaml` deve citar a tabela de evidência preenchida na
  própria SDD, o `validation.md` como relatório complementar e o
  `validate_state.py` com exit 0 na SDD verificada.
- **RF5**: `operational_artifacts.validation.md.purpose` deve dizer que
  o arquivo complementa, nunca substitui, a tabela de evidência da SDD.

Casos de borda:
- `FAIL`: passo 5 não roda (status não muda); texto atual "`FAIL` não
  avança status" permanece.
- Verificação não independente (mesma sessão): passo 5 roda igual; a
  linha `**Verificador independente:** não` já é exigida pelo texto
  atual.
- SDD de projeto que ainda não sincronizou `SDD-DTF-0018`: o passo 5 roda
  num arquivo só, então falso positivo de SDD legada de outro arquivo não
  aparece; falso positivo de "n/a" na coluna Sensor ainda pode aparecer —
  o procedimento manda corrigir a tabela ("sem sensor — checagem
  estática") em vez de ignorar o exit.

Fora de escopo:
- Nome do relatório por SDD (`validation.md` único sobrescrito no kit vs.
  `validation-EVM-00XX.md` no viverMelhor) — convenção não muda aqui.
- Corrigir SDD-EVM-0013/0014/0015 (fase separada, repositório do
  projeto).
- Mecanizar o passo 5 por hook — escopo de `SPEC-DTF-0009` (PostToolUse
  que roda `validate_state` a cada edição de SDD).
- Sincronizar central e projetos.

## Especificação técnica consolidada

**`_framework/procedures/verify-sdd.md`**

- Passo 2, primeiro parágrafo passa a:
  > Para cada linha de "Critérios de aceite", rode o comando **nesta
  > sessão** e registre a saída real na tabela "Evidência de verificação"
  > **da própria SDD** — é essa tabela que o gate 16 e `validate_state.py`
  > leem.
- Passo 4, antes do bloco do `validation.md`, novo trecho com o modelo
  da seção da SDD:
  ````markdown
  Na SDD, a seção "Evidência de verificação" fica assim:

  ```markdown
  ## Evidência de verificação (preencher antes de status `implemented`)

  Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

  **Verificador independente:** sim

  | # | Comando rodado | Saída (resumo) | Sensor | Passou? |
  |---|---|---|---|---|
  | 1 | `<comando>` | `<saída real>` | <resultado do sensor ou "sem teste automatizado"> | Sim |
  ```

  `validation.md` complementa essa tabela com veredito, descompassos e
  lições — **não a substitui**. SDD `implemented` com a tabela vazia é
  gate 16 violado, mesmo com `validation.md` PASS ao lado.
  ````
- Última frase do passo 4 ("`PASS` autoriza mover a SDD para
  `implemented` e atualizar o registry.") passa a: "`PASS` autoriza o
  passo 5."
- Novo `### 5. Checagem mecânica antes de mudar status`, substituindo a
  seção `## Checagem mecânica complementar`:
  ```markdown
  ### 5. Checagem mecânica antes de mudar status

  1. Mude `status` para `implemented` no front-matter da SDD e no
     `docs/sdd/registry.yaml`.
  2. Rode só no arquivo verificado:

     ```
     python3 _framework/scripts/validate_state.py docs/sdd/SDD-{PROJETO}-{SEQ}.md
     ```

  3. Exit diferente de 0: volte `status` para `approved` (SDD e registry)
     antes de qualquer commit, corrija a tabela ou a checklist de escopo
     e rode de novo. Não commite `implemented` com exit diferente de 0.

  Passar é necessário e não suficiente — o script não sabe se o comando
  foi mesmo rodado nesta sessão e não roda o sensor. Rodar no diretório
  inteiro mistura problemas de outras SDDs com os desta.
  ```
- Tabela de red flags ganha uma linha:
  `| "O PASS está no validation.md, a tabela da SDD é repetição" | A SDD é o que a próxima sessão lê. Tabela vazia com status implemented é contradição no artefato autoritativo |`

**`_framework/rules/workflow-rules.yaml`**

- `capabilities` → `verify_sdd_independently.produces`:
  `"Tabela 'Evidência de verificação' preenchida na própria SDD (lida pelo gate 16), validation.md ao lado com veredito PASS/FAIL, descompassos e lições, e validate_state.py com exit 0 na SDD verificada antes de implemented."`
- `operational_artifacts.validation.md.purpose`:
  `"Veredito da verificação independente de uma SDD, ao lado dela. Complementa, nunca substitui, a tabela 'Evidência de verificação' dentro da SDD. Sem front-matter, mesmo formato de artefato descartável que HANDOFF.md e LESSONS.md."`

**`_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`**
— gerado por `python3 _framework/scripts/render_prompts.py`
(`sync_copies`), nunca editado à mão.

## Critérios de aceite / definição de pronto

| # | Critério (origem) | Comando de verificação | Resultado esperado |
|---|---|---|---|
| 1 | RF1, RF2 | `grep -n "da própria SDD" _framework/procedures/verify-sdd.md; grep -n "não a substitui" _framework/procedures/verify-sdd.md` | uma ocorrência no passo 2 e uma no passo 4 |
| 2 | RF3 | `grep -n "### 5. Checagem mecânica antes de mudar status" _framework/procedures/verify-sdd.md; grep -c "Checagem mecânica complementar" _framework/procedures/verify-sdd.md` | cabeçalho encontrado; contagem `0` |
| 3 | RF3 — comando por arquivo, nunca por diretório | `grep -c "validate_state.py docs/sdd$" _framework/procedures/verify-sdd.md` | `0` |
| 4 | RF4, RF5 | `python3 -c "import yaml; d=yaml.safe_load(open('_framework/rules/workflow-rules.yaml')); c=[x for x in d['capabilities'] if x['id']=='verify_sdd_independently'][0]; print('própria SDD' in c['produces'], 'nunca substitui' in d['operational_artifacts']['validation.md']['purpose'])"` | `True True` |
| 5 | RF3 discrimina o caso real | bloco C5 abaixo | primeira execução exit `1`, segunda exit `0` |
| 6 | Renderizações e regressão | `python3 _framework/scripts/render_prompts.py --check && python3 _framework/scripts/check_renderings.py && python3 _framework/scripts/framework_check.py --auto` | exit 0 e `✅ Todas as verificações do framework passaram.` |

Bloco C5 (usa redirecionamento, fica fora da tabela) — simula a
SDD-EVM-0013 numa cópia descartável da SDD-DTF-0017, rodando o comando
exato do passo 5:

```bash
tmp=$(mktemp -d) && cp -r docs/sdd "$tmp/" && \
python3 - "$tmp/sdd/SDD-DTF-0017.md" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
s = re.sub(r"(\| # \|[^\n]*\| Sensor \| Passou\? \|\n\|[-| ]+\|\n)(?:\|[^\n]*\n)+", r"\1", s, count=1)
open(p, "w").write(s)
PY
python3 _framework/scripts/validate_state.py "$tmp/sdd/SDD-DTF-0017.md"; echo "exit=$?"
python3 _framework/scripts/validate_state.py docs/sdd/SDD-DTF-0017.md; echo "exit=$?"
```

## Instruções específicas para a IA implementadora

- Implementar só depois de `SDD-DTF-0018` mergeada em `main`.
- Editar `workflow-rules.yaml` só nos dois campos citados; rodar
  `python3 _framework/scripts/render_prompts.py` e commitar a cópia
  gerada da skill no mesmo PR.
- Não renumerar nem reescrever os passos 1–3 além da frase do passo 2.
- Critério 5 não tem teste automatizado de procedimento (é texto); o
  bloco C5 é o sensor: confirma que o comando que o passo 5 manda rodar
  reprova a situação da SDD-EVM-0013 e aprova a SDD correta.
- Branch `sdd/SDD-DTF-0019-verify-sdd-evidencia` a partir de `main`, PR —
  nunca commit direto (gate seção 14). Commits em Conventional Commits
  com `Refs: SDD-DTF-0019`.

## Verificação de escopo (nada a mais, nada a menos)

- [ ] Todo requisito consolidado acima tem alteração correspondente.
- [ ] Arquivos tocados: `_framework/procedures/verify-sdd.md`,
      `_framework/rules/workflow-rules.yaml` e a cópia gerada em
      `_framework/skills/doc-traceability-framework/references/workflow-rules.yaml`
      — qualquer outro arquivo é escopo não registrado ou scope creep.
- [ ] Nenhuma mudança de regra, gate ou script além do descrito.

## Evidência de verificação (preencher antes de status `implemented`)

Preenchida pela skill `verify-sdd`, em sessão separada da que implementou.
A tabela fica **nesta seção**; `docs/sdd/validation.md` é o relatório
complementar.

**Verificador independente:** —

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Rastreabilidade

| Campo | Valor |
|---|---|
| source_docs | (nenhum — sizing small) |
| relates_to | SDD-DTF-0018 (dependência: validate_state sem falso positivo) |
