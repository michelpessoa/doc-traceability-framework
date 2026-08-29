# Prompt de Onboarding — Bootstrap de Projeto Já Existente (v1.3.0)

Use este prompt **uma única vez por projeto**, no dia em que um projeto
que já tem código em produção (mas nunca usou este framework) vai passar
a usá-lo. Cole este prompt numa IA com acesso de leitura ao repositório
de código do projeto (Claude Code, Cursor, etc.). Ele implementa a seção
`onboarding` de `_framework/rules/workflow-rules.yaml` — não é um fluxo
alternativo, é a Fase 1 do mesmo framework.

Não use este prompt para um projeto novo que ainda não tem código — nesse
caso, comece direto por um Strategy Doc ou RFC com o `prompts/universal.md`.

---

Você vai fazer o levantamento de baseline de um projeto que já existe,
para trazê-lo para dentro do Framework de Documentação & Rastreabilidade.
Isto acontece em duas fases. Você só executa a Fase 1 agora — a Fase 2 é
o time voltando a usar o fluxo normal depois que você terminar.

## Fase 1 — Levantamento (o que você faz agora)

**Passo 1 — Leia o repositório antes de escrever qualquer coisa.**
Identifique: linguagens e frameworks usados, como o projeto está
estruturado (módulos, camadas, serviços), quais integrações e
dependências externas existem (bancos de dados, filas, APIs de
terceiros, outros serviços internos), e qualquer dívida técnica visível
no próprio código (TODOs, workarounds documentados, versões
desatualizadas críticas).

**Passo 1.1 — Grave a URL do repositório de código no registry.**
Antes de escrever o BASE, confirme (ou pergunte ao usuário, se não
souber) a URL do repositório de código deste projeto, e grave-a no campo
`repository` de `docs/{PROJECT_CODE}/registry.yaml` no repositório
central. Nunca adivinhe essa URL. Este campo é o que a auditoria de
aderência (`prompts/framework-audit.md`) vai ler no futuro para saber
qual repositório inspecionar — sem ele, a auditoria não tem como rodar.

**Passo 2 — Escreva UM documento BASE.**
Use `templates/base.template.md`. Id: `BASE-{PROJECT_CODE}-0001` (pergunte
o PROJECT_CODE se não souber). Preencha com o que você encontrou no Passo
1 — descreva o que existe, não invente motivos que você não pode
confirmar pelo código. Tudo que você não conseguir inferir com segurança
vai no campo `known_gaps`, não vira afirmação disfarçada de certeza.

**Passo 3 — Para cada decisão de arquitetura que você conseguir inferir
do código, escreva um ADR.**
Exemplos do tipo de decisão que vale reconstruir: escolha de banco de
dados principal, padrão de autenticação/autorização, modelo de deploy
(monolito vs serviços, servidor vs serverless), escolha de linguagem ou
framework principal, estratégia de cache, padrão de comunicação entre
serviços. Use `templates/adr.template.md` com estas particularidades:

- `provenance: reconstructed`
- `status: in_review` (**nunca** `approved` — você está inferindo a
  partir do código, não relatando uma decisão que presenciou)
- `parent_rfc:` aponte para o id do BASE do Passo 2 (não existe RFC
  retroativa — não invente uma)
- No corpo do ADR, seja honesto sobre o nível de confiança: se o código
  deixa claro o "porquê", registre; se você só consegue inferir o "o
  quê" mas não o motivo, diga isso explicitamente em vez de supor um
  motivo plausível.

**O que você NÃO deve fazer nesta fase:** não reconstrua SPEC
do que já foi construído. O código já é a especificação do que existe —
reconstruir esses dois tipos para trabalho passado é esforço alto e
baixo valor. O que importa recuperar é o "porquê" (os ADRs), não o
"como" (isso já está no código).

**Passo 4 — Pare aqui e peça revisão humana.**
Apresente a lista de ADRs propostos (todos em `in_review`) para uma
pessoa do time confirmar ou corrigir. Você não aprova ADR reconstruído
sozinho — isso só acontece depois que alguém confirma que o raciocínio
está certo, ou corrige com o motivo real (a correção em si já é
conhecimento institucional valioso, registre-a no ADR).

**Passo 5 — Depois da revisão, registre tudo.**
Para cada documento aprovado (BASE + ADRs confirmados), adicione a
entrada correspondente em `docs/{PROJECT_CODE}/registry.yaml` no
repositório central, com `tags: [onboarding]`.

## Fase 2 — Retomando o fluxo normal (não é você quem faz isso agora)

Depois que a Fase 1 estiver completa e revisada, diga claramente ao time:
"o levantamento de baseline terminou — a partir de agora, qualquer
trabalho novo neste projeto segue o fluxo normal do framework, começando
por `RFC-{PROJECT_CODE}-0001`". Use `prompts/universal.md` a partir daí.
Não é preciso mais nenhum tratamento especial: RFC, gate, SPEC e
a primeira SDD (criada no repositório do projeto) funcionam exatamente
como em um projeto que nasceu dentro do framework.

## Checklist de saída da Fase 1
- [ ] Existe exatamente um `BASE-{PROJECT_CODE}-0001`
- [ ] Todo ADR reconstruído tem `provenance: reconstructed`
- [ ] Nenhum ADR reconstruído foi aprovado sem revisão humana
- [ ] `known_gaps` no BASE está preenchido honestamente (não vazio "para
      parecer completo")
- [ ] `docs/{PROJECT_CODE}/registry.yaml` tem entradas para todos os
      documentos desta fase, com `tags: [onboarding]`
- [ ] Nenhuma SPEC retroativa foi criada
- [ ] Campo `repository` em `docs/{PROJECT_CODE}/registry.yaml` está
      preenchido com a URL do repositório de código do projeto
