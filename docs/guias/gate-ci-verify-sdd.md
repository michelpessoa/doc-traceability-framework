# Guia de adoção — gate de CI do verify-sdd

Camada 2 do `gate_scope_verification` (seção 16 de `workflow-rules.yaml`):
obrigatória em conteúdo, opt-in em adoção por projeto. Enquanto a Camada 1
(hook de sessão, por ferramenta) protege só enquanto a sessão que fez a
mudança está viva, este gate roda no CI de todo PR que toca `docs/sdd/`.
Ver SDD-DTF-0032, SPEC-DTF-0011, ADR-DTF-0004, ADR-DTF-0005.

## O que o gate confere

Quando um PR muda o `status` de uma SDD para `implemented`:

1. Existe `docs/sdd/validation-SDD-{ID}.md` com a linha `**Veredito:** PASS`.
2. Todo RF-ID de "Requisitos consolidados" tem linha de evidência
   correspondente nesse arquivo.
3. Nenhuma linha da tabela de evidência contradiz o veredito (uma linha
   `Não`/`FAIL` reprova mesmo com `**Veredito:** PASS` no topo).
4. Nenhum critério de aceite foi removido ou afrouxado entre `approved`
   e `implemented` sem `**Justificativa de mudança:**` citando o RF-ID
   afetado no corpo do PR.

PR que não toca nenhuma `docs/sdd/SDD-*.md` passa trivialmente.

## Como ligar

1. Copie `_framework/templates/ci/verify-sdd-gate.yml.example` para
   `.github/workflows/verify-sdd-gate.yml` no **repositório do projeto**
   (nunca no repositório central).
2. Troque `PROJECT_CODE` pelo código do projeto no registry central
   (ex.: `DTF`) e `ORGANIZACAO/doc-traceability-central` pelo
   repositório central real.
3. O passo de checkout raso do registry central roda sempre, mas só
   importa quando a válvula de escape (abaixo) é usada — sem
   credencial configurada, o núcleo do gate (itens 1-4 acima) continua
   funcionando normalmente; só a válvula fica indisponível até a
   credencial existir.

Rollback: remova o step do workflow. Sem migração de dado — o script é
somente leitura.

## Válvula de escape: `incident-override`

Um hotfix sob incidente ativo pode precisar mudar uma SDD para
`implemented` antes de reconstruir toda a evidência formal. Para
liberar o gate nesse caso:

1. Adicione a label `incident-override` ao PR.
2. Cite o id do incidente no corpo do PR, no formato `INC-{PROJECT_CODE}-{SEQ}`
   (ex.: `INC-DTF-0007`).

O gate valida esse `INC` contra o `registry.yaml` do repositório
central (checkout raso, `--depth 1`, só o arquivo necessário) — só
libera se o incidente existir e estiver em status `open` ou
`mitigated`. `INC` inexistente, `resolved` ou `closed` reprova o
override e o gate volta a exigir os itens 1-4 normalmente. Label sem
`INC-{ID}` citado no corpo também não libera nada.

### Credencial cross-repo (`CENTRAL_REPO_TOKEN`)

O checkout raso do registry central precisa de um token com permissão
de leitura no repositório central, configurado como secret do
repositório do projeto (`CENTRAL_REPO_TOKEN` no exemplo do workflow).
Sem essa credencial configurada, qualquer tentativa de usar a válvula
de escape falha com erro operacional ("falha ao acessar o registry
central") — distinto de "INC não encontrado" — e não bloqueia adoção
do núcleo do gate.

### Auditoria

Todo override aceito é logado (id do incidente, status encontrado no
registry, timestamp) no stdout do step de CI — consumido manualmente
por `framework-check` durante auditoria periódica.
