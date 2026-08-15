# Guia de Uso — Framework de Documentação & Rastreabilidade (Sem Jargão Técnico)

Este guia explica o framework para quem participa das decisões de
produto/negócio mas não vai mexer em código, YAML ou scripts. O objetivo
é você entender o que cada documento significa, quando pedir um, e como
interpretar o que já foi decidido — sem precisar saber nada de git ou
front-matter.

## Por que isso existe

Decisões importantes de um projeto normalmente ficam espalhadas: uma
conversa no Slack, uma decisão tomada numa reunião que ninguém anotou,
um "por que fizemos assim mesmo?" que ninguém mais lembra. Esse framework
existe para que qualquer decisão relevante fique escrita, num lugar
único, ligada às decisões anteriores que a motivaram e ao trabalho que
ela gerou depois. Assim, seis meses depois, dá para perguntar "por que
escolhemos isso?" e ter uma resposta de verdade, não uma reconstrução de
memória.

## Os documentos, em ordem de quando aparecem

**Strategy Doc** — o ponto de partida. Uma ideia ou direção ainda meio
crua, antes de virar qualquer trabalho concreto. Se você tem uma
intuição de para onde o produto/projeto deveria ir, isso é o que você
pede para registrar.

**RFC (Request for Comments)** — usada antes de qualquer decisão
relevante: uma mudança que afeta vários times, algo caro de fazer ou de
desfazer, algo tecnicamente arriscado, uma tecnologia nova, ou uma
mudança que afeta como sistemas conversam entre si. É o documento onde a
proposta é colocada na mesa e discutida antes de qualquer coisa ser
construída.

**ADR (registro de decisão de arquitetura)** — só existe quando a RFC
envolveu de fato uma decisão técnica estrutural (nem toda RFC gera um).
Registra o que foi decidido e por quê, de forma permanente — depois de
aprovado, esse documento não é mais editado, porque ele é a "ata" de uma
decisão que já aconteceu.

**PRD** — o requisito de produto: o que vai ser construído, para quem,
com que critérios de sucesso.

**Tech Spec** — a tradução da decisão em plano de execução técnico. Você
normalmente não vai escrever este, mas pode ser convidado a validar se
ele reflete corretamente o que foi combinado no PRD.

**SDD** — o documento final, feito para a inteligência artificial ler
antes de programar. Você não precisa interagir com ele diretamente; ele
é a consolidação de tudo que veio antes, pronta para virar código.

## Como saber se sua proposta precisa de uma discussão mais profunda

Depois que uma RFC é aprovada, o time verifica objetivamente se ela se
encaixa em pelo menos um destes casos:

- Muda como o sistema é montado por dentro
- É cara ou difícil de desfazer se der errado
- Existe mais de um jeito de fazer, e vale registrar por que escolhemos
  um e não outro
- Afeta mais de um time
- Envolve trocar ou introduzir uma tecnologia/fornecedor novo

Se qualquer um desses se aplicar, um ADR é criado antes de seguir
adiante — é o time parando para registrar formalmente essa decisão antes
de construir. Se nenhum se aplicar, o trabalho segue direto, sem essa
etapa extra. Isso significa que uma proposta simples não vira burocracia
desnecessária, mas uma decisão estrutural sempre fica documentada.

## Como interpretar o status de um documento

Todo documento passa por: **rascunho** → **em revisão** → **aprovado** →
(eventualmente) **implementado**. Também pode ser **rejeitado** (não vai
adiante) ou **arquivado** (não está mais ativo). Quando você olhar um
documento e quiser saber "isso já está valendo?", o que importa é o
status: só considere uma decisão como definitiva quando ela estiver
`aprovado` ou além.

## Rastreabilidade — o que isso significa na prática para você

Cada documento aponta para os documentos que o originaram e para os que
ele gerou. Isso significa que, dado qualquer PRD ou funcionalidade
entregue, dá para caminhar para trás e responder: "que RFC motivou isso?
Teve alguma decisão de arquitetura por trás? Isso veio de uma direção
estratégica específica, ou de um problema que tivemos em produção?" — e
para frente também: "essa decisão de arquitetura já gerou quais
entregas?"

## Quando um projeto já existente entra no framework

Se um projeto que já está em produção há tempos começa a usar este
framework, ele não ganha um histórico falso do passado. O time faz um
levantamento único do estado atual (o que existe, como foi construído,
que decisões dá para inferir do próprio sistema) e, a partir daquele
momento, passa a seguir o processo normal para qualquer trabalho novo.
Ou seja: o passado é resumido honestamente uma vez; o futuro segue o
processo completo.

## E quando alguém esquece de documentar?

Na prática, nem todo mundo vai lembrar de ligar cada mudança a um
documento o tempo todo — isso é esperado, não uma falha grave. Em vez de
tentar impedir isso com regras rígidas que travam o trabalho, o framework
tem uma checagem periódica (feita sob demanda, não toda hora) que compara
o que realmente foi feito no código com o que está documentado. O que
encontra um "por quê" registrado fica marcado como coberto; o que não
encontra vira um item para alguém olhar — se for algo relevante o
suficiente, o time reconstrói o registro depois (do mesmo jeito que faz
para um projeto antigo que está entrando no framework, ver seção acima);
se for algo pequeno, não vira trabalho nenhum. Ninguém fica bloqueado
esperando essa checagem.

## Incidentes e o que isso tem a ver com o roadmap

Quando algo quebra em produção, isso segue um processo separado e mais
rápido (não faz sentido discutir formalmente no meio de uma emergência).
Depois que o incidente é resolvido, o time registra um **postmortem** —
uma análise do que aconteceu e por quê. A obrigatoriedade desse registro
depende da gravidade do incidente: quanto maior o impacto, mais
obrigatório e detalhado é o postmortem. Mesmo incidentes pequenos, se
acontecem repetidas vezes pelo mesmo motivo, acabam exigindo essa análise
— porque um problema pequeno que se repete toda semana não é mais
pequeno.

O que importa para você: um postmortem pode gerar itens de trabalho
novos. Ajustes pequenos entram direto no backlog; mudanças maiores
passam pelo mesmo processo de discussão de qualquer outra proposta
estrutural (viram uma RFC). Ou seja, um incidente pode literalmente
originar uma entrada no roadmap, e a rastreabilidade deixa claro, mais
tarde, que aquele item existe por causa daquele incidente.

## Como pedir algo dentro deste framework

Você não precisa saber a mecânica interna — basta pedir em linguagem
natural para quem (ou qual IA) estiver operando o framework:

- "Preciso registrar uma ideia de direção para o projeto X" → Strategy Doc
- "Quero propor essa mudança para discussão" → RFC
- "Essa proposta foi aprovada, isso já pode ser implementado?" → verificar
  status e se passou pelo gate de decisão
- "Por que decidimos fazer assim?" → pedir a rastreabilidade daquele item
- "Tivemos um problema em produção, preciso registrar" → Incidente
