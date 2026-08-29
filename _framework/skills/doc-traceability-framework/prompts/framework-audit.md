# Prompt de Auditoria de Aderência (v1.3.0)

Use este prompt **periodicamente, sob demanda** — não é um gate de CI, não
bloqueia PR nem merge, e não presume que o time seguiu qualquer convenção
de commit à risca. Implementa a seção `audit` de
`_framework/rules/workflow-rules.yaml`: a adesão de todo o time à
convenção de referenciar documentos em commits/PRs nunca pode ser
garantida, então em vez de tentar impor isso, este prompt assume que vai
haver desvio e transforma isso em achado revisável.

Cole este prompt numa IA com acesso de leitura ao histórico de commits do
repositório do projeto (Claude Code, Cursor, etc.) e ao(s) registry(ies)
relevantes (o do repositório central para este projeto, e o
`docs/sdd/registry.yaml` do próprio repositório de código).

---

Você vai auditar se os commits/PRs recentes deste repositório têm um
documento do framework por trás, ou se são código que apareceu sem
rastro. Isto NÃO é uma cobrança de disciplina — é um levantamento
honesto do estado real.

## Passo 0 — Descubra qual repositório auditar

Leia o campo `repository` de `docs/{PROJECT_CODE}/registry.yaml` no
repositório central — é ele que diz qual repositório de código
inspecionar. **Nunca assuma ou adivinhe** essa URL. Se o campo estiver
ausente ou vazio, pergunte a URL ao usuário e grave-a nesse campo antes de
continuar para o Passo 1.

## Passo 1 — Reúna o histórico

Gere (ou peça para gerarem) o histórico de commits desde a última
auditoria (ou desde o início, na primeira vez):

```
git log --since="<data da última auditoria>" \
  --pretty=format:'%H%n%s%n%b%n===END===' > gitlog.txt
```

Se preferir rodar de forma assistida por script em vez de ler o histórico
manualmente, use:

```
python3 _framework/scripts/registry_tools.py audit gitlog.txt \
  docs/{PROJECT_CODE}  docs/sdd
```

(ajuste os caminhos dos registries conforme onde este projeto guarda o
central e o `docs/sdd/` local — pode passar mais de um).

## Passo 2 — Classifique cada commit/PR

Para cada commit ou PR do período:

- **Coberto**: a mensagem/descrição cita um id (`{TIPO}-{PROJECT_CODE}-NNNN`)
  que existe em algum registry conhecido.
- **Referência quebrada**: cita um id que não existe em nenhum registry —
  provavelmente erro de digitação. Sinalize para correção, não invente
  qual seria o id certo.
- **Não documentado**: nenhum id reconhecível na mensagem.

## Passo 3 — Triagem do que não está documentado

Para cada commit/PR não documentado, aplique os mesmos 5 critérios do
gate RFC→ADR (`decision_gates.rfc_to_adr`):

1. Introduz ou altera um padrão arquitetural
2. Decisão de alto custo ou difícil reversão
3. Trade-off técnico relevante entre alternativas
4. Impacto cross-team
5. Troca ou introdução de tecnologia/vendor relevante

- **Se algum critério se aplica**: proponha um ADR reconstruído — mesmas
  regras do onboarding (`_framework/prompts/onboarding-bootstrap.md`):
  `provenance: reconstructed`, `status: in_review` (nunca `approved`
  direto), referenciando o(s) commit(s)/PR(s) de origem no corpo.
- **Se nenhum critério se aplica**: não crie nenhum documento. Um ajuste
  pontual sem significância arquitetural não precisa virar burocracia —
  só entra no relatório como "sem documento, sem necessidade aparente".

Não reconstrua SPEC de commits passados, pela mesma razão do
onboarding: o código já é a especificação do "como"; o que vale a pena
recuperar é o "porquê" (ADR), e só quando for arquiteturalmente
significativo.

## Passo 4 — Apresente o relatório para revisão humana

Assim como no onboarding, **nenhum ADR reconstruído nesta auditoria é
aprovado sozinho pela IA**. Apresente:

- Contagem de commits cobertos / referência quebrada / não documentados
- Lista de referências quebradas (para alguém corrigir a mensagem ou o id)
- ADRs reconstruídos propostos, aguardando confirmação humana

## Passo 5 — Registre o que for aprovado

Documentos aprovados a partir desta auditoria ganham `tags: [audit]` no
registry correspondente (diferente de `tags: [onboarding]`, para
distinguir descoberta contínua de bootstrap inicial).

## O que este prompt NÃO faz

- Não bloqueia commit, PR ou merge — é diagnóstico, não gate.
- Não exige que todo commit tenha referência daqui pra frente — mede e
  reporta, não força adesão.
- Não julga quem fez o commit — o objetivo é fechar a lacuna de
  rastreabilidade, não apontar culpados.
