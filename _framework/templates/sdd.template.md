---
id: SDD-{PROJECT_CODE}-{SEQ}
type: SDD
title: "{Título — o que será implementado}"
status: draft
project: "{PROJECT_CODE}"
owner: "{pessoa ou time responsável}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
relates_to: []
# source_docs: SPEC e ADR (se houver) que originaram esta SDD. Em sizing
# `small` a lista é vazia — não há upstream, e isso é registro, não lacuna.
# Este documento vive no repositório do PROJETO, mas SPEC e ADR vivem no
# repositório CENTRAL — por isso cada entrada precisa do id E da url
# completa (sem isso a rastreabilidade quebra ao atravessar repositórios).
source_docs:
  - id: "{ex: SPEC-PROJETO-0001}"
    url: "{URL completa do arquivo no repositório central}"
  - id: "{ex: ADR-PROJETO-0001}"
    url: "{URL completa do arquivo no repositório central}"
consumption_instructions: "{como uma IA deve usar este documento antes de implementar}"
sizing: "{small | medium | large | complex}"   # herdado da SPEC; obrigatório quando há source_docs (2.7.0)
# molde: crud   # opcional, só em sizing small: nome de um padrão do projeto que a SDD
#              # referencia em vez de repetir (^[a-z0-9][a-z0-9-]*$); onde o molde mora é do executor
supersedes: null
superseded_by: null
tags: []
---

# {Título}

> Este documento é COMPILADO a partir de `source_docs` — não é escrito do
> zero. É o artefato de entrada (input) para ferramentas de IA realizarem
> a implementação. Vive no repositório de CÓDIGO deste projeto (não no
> repositório central do framework) porque é o único documento pensado
> para ser lido pela IA no momento de implementar. Traz o que o executor
> e os gates usam (requisitos por RF-ID, arquivos, tasks, critérios com
> comando, instruções); o desenho e a decisão ficam na SPEC e na ADR,
> lidos pela url de `source_docs` (id + url, já que os documentos de
> origem estão em outro repositório).

## Resumo executivo
O que será construído e por quê (1 parágrafo).

## Requisitos consolidados
> Um RF por linha, com a SPEC de origem, um resumo de até 200 caracteres
> e os arquivos que ele toca. O critério EARS, o desenho (Parte 2) e a
> decisão da ADR ficam na SPEC e na ADR de `source_docs`, por referência:
> não copie "Especificação técnica consolidada" nem "Decisão(ões) de
> arquitetura aplicável(is)" — `validate_doc.py` reprova a SDD com
> `source_docs` que tiver essas seções, e `check_source_docs.py` reprova
> RF da SPEC fora da SDD e RF da SDD fora da SPEC (SPEC-DTF-0031).
>
> Os arquivos permitidos são a união da coluna `Arquivos` dos requisitos
> e das tasks — o gate de escopo confere o diff contra ela.
>
> Em SDD sem `source_docs` (sizing `small`), o requisito é escrito aqui
> mesmo, com critério EARS no resumo e `Origem` igual a `—`. `molde`
> (front-matter) vale só em `small`: a SDD continua com requisito,
> critério executável e arquivos.

| RF-ID | Origem | Requisito (resumo) | Arquivos |
|---|---|---|---|

## Decomposição em tasks
Opcional quando a SDD herdar sizing `small` da SPEC de origem ou tiver um
único RF consolidado — nesses casos, omita a seção (não deixe tabela
vazia). Cada task cita os arquivos que toca; interseção de arquivo entre
tasks força bloqueio de paralelismo mesmo sem "Depende de" declarado
(`parallel_plan.py` deriva isso automaticamente, não escreva o grafo à
mão).

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|

## Critérios de aceite / definição de pronto
Cada item vem do RF/critério da Parte 1 e do contrato/caso de erro da
Parte 2 da SPEC — não invente critério novo aqui, consolide o que já existe a
montante. Todo item tem que ser verificável por comando executável, não
por leitura de código.

Coluna "Perfil esperado": `automatizado` (tem comando/teste que roda
sozinho), `manual` (checagem que exige julgamento humano) ou `n/a`
(critério não verificável por comando nem por inspeção manual pontual,
ex.: decisão pura já coberta por outro critério). O perfil declarado
aqui é o que a Evidência de verificação vai comparar contra o "Perfil
usado" (SDD-DTF-0036, STRAT-DTF-0003 item 7/E5) — trocar automatizado
por manual sem justificar é o que essa comparação pega.

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado | Perfil esperado |
|---|---|---|---|---|

## Instruções específicas para a IA implementadora
Instruções objetivas — arquivos/módulos esperados, padrões de código a
seguir, testes obrigatórios, o que NÃO alterar.

## Verificação de escopo (nada a mais, nada a menos)
Antes de marcar `implemented`, confirme as duas direções — SDD incompleta
tanto quanto SDD estourada são falha:
- [ ] Todo requisito consolidado acima tem código correspondente (nada
      da SPEC ficou de fora).
- [ ] Todo arquivo tocado pela implementação aparece na coluna
      `Arquivos` dos requisitos ou das tasks, ou em "Instruções
      específicas" — se a
      implementação tocou um arquivo não listado aqui, ou é escopo que
      faltou registrar na SDD (atualize-a) ou é scope creep a remover
      antes do merge.
- [ ] Nenhuma abstração, config, feature flag ou refactor extra que não
      foi pedido por nenhum requisito consolidado ("já que estava ali").

## Evidência de verificação (preencher antes de status `implemented`)
Preenchida pela skill `verify-sdd`, em sessão separada da que implementou —
quem escreveu o código tem o resultado como conclusão desejada. Para cada
critério da tabela acima: comando rodado de fato nesta sessão e saída real,
nunca "deve passar" nem resultado de memória.

**Verificador independente:** {sim | não — mesma sessão que implementou}

A coluna "Sensor" registra o sensor de discriminação: falha de
comportamento introduzida em espaço descartável, teste tem que FALHAR, e
volta ao normal depois. Teste que passa com a implementação quebrada é
ruído verde. Critério sem teste automatizado: escreva "sem teste", nunca
marque como verificado por leitura de código.

Coluna "Assertion (file:line)": caminho e linha exatos da asserção (não
do comando) que resolve o critério — ex. `test_foo.py:42`. Prova que o
comando testa o valor certo, não só que rodou e voltou verde
(STRAT-DTF-0003 item 7/E4). Critério `manual` ou `n/a` (ver "Perfil
esperado" acima): use `n/a` nesta célula. Coluna "Perfil usado": repita
o "Perfil esperado" do critério correspondente, ou declare divergência
com justificativa entre parênteses (ex.: `manual (motivo: sensor de
mutação incompatível com CI atual)`) — divergência sem parênteses é
reprovada.

| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |
|---|---|---|---|---|---|---|

## Rastreabilidade
| Campo | Valor |
|---|---|
| source_docs | {lista de ids} |
