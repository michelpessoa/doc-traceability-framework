# Lições locais

Registro de falhas de execução (gate violado, achado tardio) neste
repositório. Acumula, não sobrescreve. Ver `lessons_policy` em
`_framework/rules/workflow-rules.yaml` (seção 18).

## 2026-09-04 — Gate 13 violado ao corrigir o próprio gate_content_quality

**O que falhou:** ao investigar por que bumpar `framework_version` do
projeto EVM (`docs/EVM/registry.yaml`, repo `doc-traceability-central`)
de 1.6.0 para 2.1.0 reprovava retroativamente 11 PRD/TS antigas no gate
RF-ID, a sessão editou `workflow-rules.yaml` (campo `date` no
changelog), `framework_lib.py` (`version_date`,
`rule_applies_since_date`) e `validate_doc.py` (troca de
`rule_applies` por `rule_applies_since_date`) e só depois escreveu
`SDD-DTF-0016` descrevendo essa mudança.

**Red flag que teria pegado antes:** "já entendi o que fazer, documentar
é burocracia" — a causa raiz ficou clara rápido (comparação por versão
única de registry, não por data do documento) e a implementação parecia
óbvia o bastante pra pular a SDD. É exatamente a racionalização listada
em `gate_implementation_before_code` como falsa.

**Correção:** SDD-DTF-0016 escrita imediatamente após perceber o gap,
antes de commitar; código formalmente coberto por ela; verificação
independente (`verify-sdd`/subagente separado) rodada antes de mover
para `implemented`, como se a ordem correta tivesse sido seguida — não
se finge que o gate rodou quando não rodou (mesmo tratamento dado ao
gap equivalente achado em `SDD-EVM-0010`, `docs/sdd/validation.md` do
repo `espaco-viver-melhor`).

**Padrão notado:** este é o segundo caso na mesma sessão (o outro em
`SDD-EVM-0010`, projeto EVM) de código nascendo antes da SDD que devia
guiá-lo, ambos sob pressão de "a correção é óbvia, documentar depois
não muda o resultado". Ainda não atende ao critério de virar regra
global (`lessons_policy`: precisa de dois PROJETOS diferentes + checagem
mecânica possível) — DTF e EVM são projetos diferentes, mas a causa aqui
é comportamento do agente numa única sessão, não um gap estrutural do
framework. Registrar aqui para o caso de se repetir numa terceira vez.
