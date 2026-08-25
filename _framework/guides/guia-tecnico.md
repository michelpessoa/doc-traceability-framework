# Guia de Uso — Framework de Documentação & Rastreabilidade (Técnico)

Este guia é para quem vai efetivamente criar documentos, revisar ADRs,
rodar os scripts e configurar o framework em um repositório novo. Se
você só precisa entender o que cada documento significa e quando pedir
um, veja `guia-nao-tecnico.md` — é mais curto e sem jargão.

A fonte de verdade de tudo que está aqui é
`_framework/rules/workflow-rules.yaml`. Este guia é um resumo prático;
em caso de dúvida ou divergência, o YAML manda.

## 1. Os dois repositórios

Você sempre vai estar operando em um destes dois lugares — confirme qual
antes de criar qualquer documento:

- **Repositório central** (`framework-central`, ou o nome que vocês
  derem): guarda `_framework/` (cópia única do kit) e
  `docs/{PROJECT_CODE}/` de **todos** os projetos, mas só os tipos
  STRAT, RFC, ADR, PRD, TS, BASE, INC, PM.
- **Repositório de cada projeto** (o repositório de código): guarda só
  `docs/sdd/` — as SDDs desse projeto específico.

A SDD é a única exceção porque é o único documento pensado para ser lido
por uma IA (Claude Code, Cursor, Copilot) no momento de implementar — ela
precisa estar perto do código, os outros tipos não.

## 2. Estrutura de pastas

**No repositório central:**
```
_framework/
  rules/workflow-rules.yaml       (fonte canônica)
  templates/*.template.md
  prompts/ (universal.md, onboarding-bootstrap.md, cursor/, copilot/)
  skills/doc-traceability-framework/
  scripts/ (generate_registry_md.py, registry_tools.py)
docs/
  {PROJECT_CODE}/
    00-strategy/
    01-rfc/
    02-adr/
    03-prd/
    04-tech-spec/
    06-baseline/
    07-incidents/
    08-postmortems/
    registry.yaml
    registry.md   (gerado)
```

**No repositório de cada projeto:**
```
docs/
  sdd/
    SDD-{PROJECT_CODE}-0001.md
    registry.yaml
    registry.md   (gerado)
```

## 3. Criando um projeto novo

1. No repositório central, crie `docs/{PROJECT_CODE}/` com as subpastas
   acima e um `registry.yaml` vazio (`project`, `framework_version`,
   `documents: []`).
2. No repositório de código do projeto, crie `docs/sdd/` com seu próprio
   `registry.yaml` vazio.
3. Escolha o `PROJECT_CODE` (curto, maiúsculo, sem espaços) — ele é usado
   em todos os IDs desse projeto dali para frente e não muda depois.
4. Copie (ou aponte para) `prompts/universal.md` e use-o com a IA de sua
   preferência a partir daqui.

## 4. Criando um documento — passo a passo

1. Abra o template do tipo em `_framework/templates/{tipo}.template.md`.
2. Descubra o próximo ID: olhe `docs/{PROJECT_CODE}/registry.yaml` (ou
   `docs/sdd/registry.yaml` para SDD), conte quantos documentos daquele
   tipo já existem, o próximo é `{TYPE}-{PROJECT_CODE}-{N+1, 4 dígitos}`.
3. Preencha o front-matter (bloco YAML no topo) e o conteúdo.
4. Adicione a entrada correspondente no `registry.yaml` certo — **na
   mesma tarefa**, não depois.
5. Rode `python3 _framework/scripts/generate_registry_md.py docs/{PROJECT_CODE}`
   (ou `docs/sdd` no repo de projeto) para regenerar a tabela legível.

## 5. O gate RFC → ADR na prática

Depois que uma RFC é aprovada, responda objetivamente:

```
[ ] Introduz ou altera um padrão arquitetural?
[ ] Decisão de alto custo ou difícil reversão?
[ ] Trade-off técnico relevante entre alternativas viáveis?
[ ] Impacto cross-team (mais de um time/domínio afetado)?
[ ] Troca ou introdução de tecnologia/vendor/dependência externa relevante?
```

Qualquer `[x]` → crie um ADR antes de PRD/Tech Spec. Nenhum marcado →
pule direto para PRD/Tech Spec. Registre o resultado em
`requires_adr` e `decision_gate_criteria_met` no front-matter da RFC —
isso é o que torna a decisão auditável depois.

## 6. Compilando a SDD

A SDD nasce no repositório do projeto, não no central. Regras práticas:

- Só compile quando PRD e Tech Spec (e o ADR, se existir) estiverem
  `approved`.
- Não escreva conteúdo novo — consolide o que já está em PRD/Tech
  Spec/ADR.
- `source_docs` é uma lista de `{id, url}`: a `url` é a URL completa do
  arquivo no repositório central (ex.:
  `https://github.com/org/framework-central/blob/main/docs/CHECKOUT/03-prd/PRD-CHECKOUT-0002.md`).
  Sem essa URL, quem olhar a SDD depois não consegue chegar à origem.

## 7. Scripts disponíveis

```bash
# Regenerar a tabela legível (registry.md) a partir do registry.yaml
python3 _framework/scripts/generate_registry_md.py docs/{PROJECT_CODE}

# Validar consistência do registry (ids órfãos, referências quebradas, status inválido)
python3 _framework/scripts/registry_tools.py validate docs/{PROJECT_CODE}

# Rastrear a cadeia completa de um documento (ancestrais e descendentes)
python3 _framework/scripts/registry_tools.py trace docs/{PROJECT_CODE} RFC-CHECKOUT-0001
```

Rode `validate` como parte do PR/CI sempre que `docs/` mudar — é a
melhor forma de pegar divergência entre front-matter e registry antes
que ela vire hábito.

## 8. Onboarding de um projeto já existente

Use `_framework/prompts/onboarding-bootstrap.md` — não improvise um
processo alternativo. Resumo do que acontece (detalhes completos no
próprio prompt):

1. Uma IA lê o repositório de código do projeto.
2. Gera um único `BASE-{PROJECT_CODE}-0001` (retrato do estado atual).
3. Propõe ADRs reconstruídos (`provenance: reconstructed`, sempre
   começando em `status: in_review`).
4. Alguém do time revisa e confirma/corrige cada ADR proposto antes de
   qualquer um virar `approved`.
5. A partir daí, o projeto segue o fluxo normal — a próxima RFC real é
   `RFC-{PROJECT_CODE}-0001`.

Não reconstrua PRD ou Tech Spec do que já foi construído — não vale o
esforço, o código já é a especificação do que existe.

## 9. Auditoria de aderência (commits/PRs x registry)

A adesão de todo o time a referenciar documentos em commits/PRs nunca
pode ser garantida — sempre vai ter commit avulso, hotfix de incidente
feito sob pressão, ou simplesmente alguém que esqueceu. Por isso este
framework não tenta impor isso com CI ou bloqueio de merge: em vez de um
gate, existe uma auditoria periódica e sob demanda, que assume que vai
haver desvio e o transforma em achado revisável — reaproveitando o mesmo
mecanismo de reconstrução do onboarding (seção 8), só que contínuo em vez
de único.

Use `_framework/prompts/framework-audit.md` quando quiser rodar:

1. Gere o log de commits desde a última auditoria:
   ```bash
   git log --since="<data>" --pretty=format:'%H%n%s%n%b%n===END===' > gitlog.txt
   ```
2. Cruze com o(s) registry(ies) conhecidos:
   ```bash
   python3 _framework/scripts/registry_tools.py audit gitlog.txt docs/{PROJECT_CODE} docs/sdd
   ```
3. O relatório separa commits em cobertos, referência quebrada (id citado
   não existe) e não documentados. Para os não documentados, aplique os 5
   critérios do gate RFC→ADR (seção 5): se algum se aplica, proponha um
   ADR reconstruído (`provenance: reconstructed`, `status: in_review`,
   `tags: [audit]`); se nenhum se aplica, não crie documento nenhum.
4. Nenhum ADR reconstruído por auditoria é aprovado sem revisão humana —
   mesma regra do onboarding.

Não é CI, não bloqueia PR, não exige disciplina perfeita de commit — só
torna visível o que já é verdade sobre o repositório.

## 10. Incidentes e postmortem

INC tem ciclo de vida próprio: `open → mitigated → resolved → closed`
(não é `draft/review/approved`, é operacional).

Severidade e obrigatoriedade de postmortem:

| Severidade | Critério | Postmortem |
|---|---|---|
| SEV1 | Indisponibilidade total/crítica, perda de dados, incidente de segurança | Obrigatório, completo |
| SEV2 | Degradação relevante, sem workaround | Obrigatório, completo |
| SEV3 | Impacto limitado, workaround existe | Obrigatório, leve |
| SEV4 | Impacto mínimo/cosmético | Opcional |

Regra de recorrência: 2ª ocorrência da mesma `root_cause_key` em ≤ 90
dias torna o postmortem obrigatório mesmo em SEV4.

Cada action item do postmortem é triado: ajuste pontual → PRD/Tech Spec
direto; mudança estrutural (bateria em algum critério do gate) → nova
RFC, com `relates_to` apontando para o PM de origem.

## 11. Configurando as ferramentas de IA

- **Qualquer chat de IA (ChatGPT, Gemini, Claude):** cole
  `_framework/prompts/universal.md` no início da conversa.
- **Cursor/Windsurf:** copie
  `_framework/prompts/cursor/doc-framework.mdc` para
  `.cursor/rules/doc-framework.mdc` **no repositório do projeto** (não
  no central).
- **GitHub Copilot:** copie
  `_framework/prompts/copilot/copilot-instructions.md` para
  `.github/copilot-instructions.md` **no repositório do projeto**.
- **Claude / Cowork:** instale a skill `doc-traceability-framework.skill`
  — ela já embute templates, regra canônica e scripts.

## 12. Paralelização por trilhas de negócio (opcional)

Para projetos com módulos de negócio razoavelmente independentes, existe
um padrão opcional de organização — uma skill por trilha, uma sessão de
IA (ou pessoa) por trilha, grafo de dependências entre trilhas — em
`paralelizacao-trilhas.md`. Não é obrigatório e não altera o fluxo
principal de documentos; é um padrão de execução de código, não de
decisão. Veja o exemplo real em `docs/EVM/`.

## 13. Erros comuns a evitar

- Criar STRAT/RFC/ADR/PRD/TS dentro do repositório de projeto (esses
  tipos são sempre do repositório central).
- Aprovar um ADR reconstruído sem revisão humana.
- Editar um ADR `approved` no lugar em vez de criar um novo e marcar o
  antigo como `superseded`.
- Esquecer de atualizar o `registry.yaml` junto com o documento.
- Reconstruir PRD/Tech Spec retroativos durante onboarding ou auditoria.
- Transformar a auditoria de aderência em gate de CI ou bloqueio de PR —
  ela é diagnóstico sob demanda, não um portão obrigatório.
