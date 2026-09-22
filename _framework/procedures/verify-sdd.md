# Verificação independente de SDD

> **QUEM IMPLEMENTOU NÃO VERIFICA. NENHUM `implemented` SEM COMANDO RODADO NESTA SESSÃO E SAÍDA REAL.**

Este procedimento existe porque o gate da seção 16 pedia que a própria
sessão que escreveu o código preenchesse a tabela de evidência que a
aprova. Quem implementou tem o resultado como conclusão desejada, e o
custo de rodar de novo parece desnecessário justamente quando mais
importa. Verificação é papel, não etapa: **o verificador não pode ser
quem escreveu o código.**

Na prática: rode este procedimento numa sessão ou subagente separado da
que implementou, com contexto limpo. Se for inevitável ser a mesma
sessão, declare isso na tabela de evidência — verificação não-independente
é dado mais fraco, e o humano precisa saber disso.

## Entrada

- Autoridade de despacho: só quem tem a feature inteira que vai a PR
  despacha esta verificação — nunca uma sessão que implementou só uma
  trilha/task paralela isolada (RFC-DTF-0006/ADR-DTF-0006).
- A SDD (`docs/sdd/SDD-*.md`) com status `approved`.
- O diff da implementação (`git diff <base>..HEAD`), onde `<base>` é um
  SHA fixo — o `merge-base` capturado no momento da redação (`git
  merge-base HEAD origin/main`, rodado **antes** de qualquer merge da
  própria mudança) ou o SHA específico citado na SDD/PR. **Nunca
  `origin/main`** direto: é uma ref móvel, e assim que a mudança sendo
  verificada é mergeada, `origin/main` passa a contê-la — o "antes" deixa
  de existir e qualquer bloco comparativo para de discriminar. Em
  features com paralelismo, o diff é sempre `<merge-base>..HEAD` da
  branch consolidada — nunca o diff de uma task/trilha isolada.
- Nada mais. **Não leia o histórico da sessão que implementou** — herdar
  o raciocínio dela é herdar os pontos cegos dela.

## Procedimento

### 1. Conformidade com a spec (as duas direções)

- Todo item de "Requisitos consolidados" e "Especificação técnica
  consolidada" tem código correspondente identificável? Faltou algum → a
  SDD está **parcial**, mantenha `approved`.
- Todo arquivo do diff aparece na SDD? Arquivo fora da lista é escopo não
  registrado (atualize a SDD) ou scope creep (remova) — nunca uma terceira
  coisa silenciosa.
- Alguma abstração, dependência, feature flag ou refactor sem requisito
  correspondente? "Já que eu estava ali" não é requisito.
- Vocabulário vago no critério que você está prestes a marcar como
  cumprido ("gracefully", "de forma eficiente", "corretamente")? Isso é
  gate_content_quality, não gate_scope_verification — mas se passou pelo
  primeiro (STRAT-DTF-0003, item G, `validate_doc.py`), sinalize antes de
  aceitar o critério como verificável.

### 2. Evidência fresca

Para cada linha de "Critérios de aceite", rode o comando **nesta sessão**
e registre a saída real na tabela "Evidência de verificação"
**da própria SDD** — é essa tabela que o gate 16 e `validate_state.py` leem.

Não aceite, de você mesma nem de subagente: "deve passar", "rodei antes",
"o teste existe", "assumo que sim". Se não tem a saída, não tem evidência.

### 3. Sensor de discriminação

Um teste que nunca falhou pode não estar testando nada. Para cada
critério com teste automatizado:

1. Num espaço descartável — cópia do arquivo original (ex.: `cp
   arquivo.py /tmp/backup && ...` ou `git checkout -- <arquivo>` rodado
   dentro da própria worktree) — **nunca `git stash`** (o stash é
   compartilhado entre worktrees e sessões do mesmo repositório; com
   verificadores em paralelo, um `git stash` de uma sessão colide com o
   de outra) e **nunca** um commit, introduza uma falha de comportamento
   real no código que aquele critério cobre: inverta uma condição,
   retorne valor fixo, pule uma validação.
2. Rode o teste. **Ele tem que falhar.**
3. Restaure pela cópia guardada (ou `git checkout -- <arquivo>`) e
   confirme que o teste volta a passar.

Teste que passa com a implementação quebrada não verifica o critério —
ele é ruído verde. Registre o resultado do sensor na tabela.

Se não houver teste automatizado para um critério, diga isso
explicitamente em vez de marcar o critério como verificado por leitura de
código. Mecanizado (STRAT-DTF-0003, item A): `validate_state.py` reprova
`implemented` com a coluna `Sensor` vazia — "sem teste automatizado" é
declaração válida, célula em branco não é.

### 4. Veredito

Na SDD, a seção "Evidência de verificação" fica assim:

```markdown
## Evidência de verificação (preencher antes de status `implemented`)

Verificação independente completa em `docs/sdd/validation.md`. Veredito: **PASS**.

**Verificador independente:** sim

| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|---|
| 1 | 1 | `<comando>` | `<saída real>` | <resultado do sensor ou "sem teste automatizado"> | Sim |
```

`Rodada` é o número da tentativa de correção-e-reverificação,
começando em 1. Teto de 3 rodadas: se o veredito não for `PASS` na 3ª
rodada, a sessão para de tentar sozinha e escreve, na SDD, a seção
abaixo em vez de despachar uma 4ª tentativa:

```markdown
## Escalonado ao humano
Rodadas tentadas: 3. Veredito de cada uma: <FAIL, FAIL, FAIL | resumo>.
Motivo de cada falha: <resumo por rodada>.
```

Histórico de rodadas anteriores não é sobrescrito — a tabela de
evidência mantém as linhas de todas as rodadas, não só a última.

`validation.md` complementa essa tabela com veredito, descompassos e
lições — **não a substitui**. SDD `implemented` com a tabela vazia é
gate 16 violado, mesmo com `validation.md` PASS ao lado.

Escreva `validation.md` ao lado da SDD:

```markdown
# Verificação — SDD-{PROJETO}-{SEQ}

- **Veredito:** PASS | FAIL
- **Diff verificado:** <base>..<head>
- **Verificador independente:** sim | não (mesma sessão que implementou)

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|

## Descompassos encontrados
(requisito sem código, arquivo fora da SDD, código sem requisito — ou "nenhum")

## Lições
(o que causou cada descompasso, em forma de red flag reaproveitável —
entra no LESSONS.md do projeto)
```

`FAIL` não avança status. Relate o descompasso ao humano e proponha os
dois caminhos possíveis — atualizar a SDD para o escopo real acordado, ou
remover o código fora de escopo. **A escolha é dele, não sua.**

`PASS` autoriza o passo 5.

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

## Red flags

| Racionalização | Realidade |
|---|---|
| "Eu implementei, sei que funciona" | É exatamente por isso que você não é o verificador |
| "Rodei a suíte há pouco" | Sem a saída desta sessão, não há evidência |
| "Passou de primeira, ótimo sinal" | Ou é bom sinal, ou o teste não testa nada. O sensor decide |
| "O sensor é overhead, o teste é bom" | Custa um comando. A alternativa é confiar sem verificar |
| "Faltou pouca coisa, marco implemented" | Faltando é parcial. Mantenha `approved` |
| "O subagente disse que passou" | Relato próprio não é verificação independente |
| "O PASS está no validation.md, a tabela da SDD é repetição" | A SDD é o que a próxima sessão lê. Tabela vazia com status implemented é contradição no artefato autoritativo |
| "Eu tenho a feature inteira, então eu mesma despacho e verifico" | Builder despachou a própria verificação da feature — quem implementou não verifica, mesmo tendo a visão completa |
| "Só implementei minha task, mas testo com o diff dela" | Diff de entrada é fatia de task paralela, não a feature consolidada — não discrimina o todo |
