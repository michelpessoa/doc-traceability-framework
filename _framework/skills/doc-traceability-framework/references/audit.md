# Auditoria de aderência (commits/PRs x registry)

A adesão de todo o time a documentar tudo NUNCA pode ser garantida —
sempre vai haver commit/PR avulso ou hotfix de incidente que muda código
antes de qualquer documento existir. Em vez de tentar impor isso com CI
ou bloqueio de merge, use `prompts/framework-audit.md` **periodicamente,
sob demanda** (não é um gate): ele cruza o histórico de commits do
repositório do projeto com os registries conhecidos, classifica cada
commit em coberto / referência quebrada / não documentado, e para os não
documentados aplica os mesmos 5 critérios do gate RFC→ADR — se algum se
aplica, propõe um ADR reconstruído (igual ao onboarding, nunca aprovado
sem revisão humana, com `tags: [audit]`); se nenhum se aplica, não gera
documento algum. `scripts/registry_tools.py audit` automatiza o
cruzamento a partir de um log de commits, e `scripts/framework_check.py --auto`
roda a auditoria de ponta a ponta sem exigir o log preparado à mão.

Ver `workflow-rules.yaml:audit` para precondição, convenção de referência e classificação.
