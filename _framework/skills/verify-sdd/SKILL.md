---
name: verify-sdd
description: >
  Verifica de forma independente se uma SDD foi de fato implementada antes
  de o status virar `implemented`: confere requisito↔código nas duas
  direções, roda cada critério de aceite e registra comando e saída reais,
  e testa se os testes realmente discriminam implementação certa de errada.
  Use quando o usuário disser "verifica a SDD", "pode marcar implemented?",
  "confere se ficou tudo", "roda a verificação de escopo", ou quando uma
  sessão de implementação terminar e o status precisar avançar de
  `approved` para `implemented`. Do NOT use for escrever ou corrigir a
  implementação (isso é da sessão que implementa), para revisar qualidade
  de código em geral (use uma skill de code review), nem para verificar
  documento que não seja SDD.
---

# Verificação independente de SDD

> **QUEM IMPLEMENTOU NÃO VERIFICA. NENHUM `implemented` SEM COMANDO RODADO NESTA SESSÃO E SAÍDA REAL.**

Esta skill existe porque o gate da seção 16 pedia que a própria sessão que
escreveu o código preenchesse a tabela de evidência que a aprova. Quem
implementou tem o resultado como conclusão desejada, e o custo de rodar de
novo parece desnecessário justamente quando mais importa. Verificação é
papel, não etapa: **o verificador não pode ser quem escreveu o código.**

Na prática: rode esta skill numa sessão ou subagente separado da que
implementou, com contexto limpo. Se for inevitável ser a mesma sessão,
declare isso na tabela de evidência — verificação não-independente é dado
mais fraco, e o humano precisa saber disso.

## Entrada

- A SDD (`docs/sdd/SDD-*.md`) com status `approved`.
- O diff da implementação (`git diff <base>..HEAD`).
- Nada mais. **Não leia o histórico da sessão que implementou** — herdar o
  raciocínio dela é herdar os pontos cegos dela.

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

### 2. Evidência fresca

Para cada linha de "Critérios de aceite", rode o comando **nesta sessão** e
registre a saída real na tabela "Evidência de verificação".

Não aceite, de você mesma nem de subagente: "deve passar", "rodei antes",
"o teste existe", "assumo que sim". Se não tem a saída, não tem evidência.

### 3. Sensor de discriminação

Um teste que nunca falhou pode não estar testando nada. Para cada critério
com teste automatizado:

1. Num espaço descartável (`git stash`, cópia, ou worktree — **nunca** um
   commit), introduza uma falha de comportamento real no código que aquele
   critério cobre: inverta uma condição, retorne valor fixo, pule uma
   validação.
2. Rode o teste. **Ele tem que falhar.**
3. Desfaça a alteração e confirme que o teste volta a passar.

Teste que passa com a implementação quebrada não verifica o critério — ele
é ruído verde. Registre o resultado do sensor na tabela.

Se não houver teste automatizado para um critério, diga isso explicitamente
em vez de marcar o critério como verificado por leitura de código.

### 4. Veredito

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

`FAIL` não avança status. Relate o descompasso ao humano e proponha os dois
caminhos possíveis — atualizar a SDD para o escopo real acordado, ou
remover o código fora de escopo. **A escolha é dele, não sua.**

`PASS` autoriza mover a SDD para `implemented` e atualizar o registry.

## Checagem mecânica complementar

```
python3 _framework/scripts/validate_state.py docs/sdd
```

Confere o que dá para conferir de fora: tabela preenchida, uma linha por
critério, sem resultado assumido, checklist de escopo marcada. Passar nele
é necessário e não suficiente — ele não sabe se o comando foi mesmo rodado
nesta sessão, e não roda o sensor.

## Red flags

| Racionalização | Realidade |
|---|---|
| "Eu implementei, sei que funciona" | É exatamente por isso que você não é o verificador |
| "Rodei a suíte há pouco" | Sem a saída desta sessão, não há evidência |
| "Passou de primeira, ótimo sinal" | Ou é bom sinal, ou o teste não testa nada. O sensor decide |
| "O sensor é overhead, o teste é bom" | Custa um comando. A alternativa é confiar sem verificar |
| "Faltou pouca coisa, marco implemented" | Faltando é parcial. Mantenha `approved` |
| "O subagente disse que passou" | Relato próprio não é verificação independente |
