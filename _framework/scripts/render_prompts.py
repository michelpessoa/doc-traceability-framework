#!/usr/bin/env python3
"""
render_prompts.py

Gera, a partir de workflow-rules.yaml, o bloco de fatos que TODA
renderização precisa carregar igual — tipos de documento, níveis de
sizing, Iron Laws e ciclo de vida — e injeta esse bloco entre marcadores
em cada prompt.

Existe porque o YAML declarava que prompts e skills são "renderizações"
das mesmas regras, mas as cinco cópias eram mantidas à mão. Na v2.0.0 as
três renderizações de prompt estavam paradas na v1.x: sem SPEC, sem
sizing, sem Iron Law. O texto ao redor dos marcadores continua sendo
escrito por gente; o que é fato canônico passa a ser gerado.

Uso:
    python3 render_prompts.py [--check]

--check não escreve: sai 1 se algum bloco estiver desatualizado (é o que
o CI roda).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import find_rules_file, load_rules  # noqa: E402

BEGIN = "<!-- BEGIN GENERATED: núcleo do framework — não edite à mão -->"
END = "<!-- END GENERATED -->"

# Adaptadores da camada 3 gerados por INTEIRO — nada neles é escrito à
# mão, e `--check` reprova qualquer edição manual. Caminhos relativos à
# raiz de _framework; `../` aponta para a raiz do repositório.
FULL_TARGETS = [
    ("../AGENTS.md", "build_agents"),
    ("../QUICKSTART.md", "build_quickstart"),
    ("../docs/especificacao.md", "build_spec_doc"),
    ("../CHANGELOG.md", "build_changelog"),
    ("prompts/universal.md", "build_universal"),
    ("prompts/cursor/doc-framework.mdc", "build_cursor_mdc"),
    ("prompts/copilot/copilot-instructions.md", "build_copilot_instructions"),
]

# Versões anteriores ao changelog canônico do YAML, que começa na 1.4.0.
# Preservado literalmente para a geração não apagar histórico.
LEGACY_CHANGELOG = """## Histórico anterior ao changelog canônico

As versões 1.0.0 a 1.3.0 existiram antes de `framework.changelog` virar a
fonte de verdade. O registro delas vive no histórico do git.
"""


def build_block(rules: dict) -> str:
    """Miolo gerado, entre marcadores, para as renderizações antigas."""
    return "\n".join([BEGIN, "", core_facts(rules), "", END])


def build_universal(rules: dict) -> str:
    """prompts/universal.md — prompt colável em qualquer assistente de IA. Prosa fixa (transcrita, não reescrita) + núcleo canônico gerado."""
    fw = rules.get("framework") or {}
    version = fw.get("version")
    prefix = '# Prompt Universal — Framework de Documentação & Rastreabilidade para IA (v1.7.0)\n\nCole este prompt inteiro no início de uma conversa em qualquer assistente de\nIA (ChatGPT, Gemini, Claude, etc.) antes de pedir para criar, avaliar ou\navançar documentos deste framework. Ele é a "fonte de verdade" de\ncomportamento — as versões para Cursor, Copilot e a Claude Skill devem\nproduzir exatamente o mesmo resultado que este prompt. Para o onboarding\nde um projeto que já existia antes deste framework, use o prompt separado\n`prompts/onboarding-bootstrap.md` — este aqui cobre o fluxo do dia a dia.\n\nVocê vai atuar como um assistente de documentação técnica que segue,\nsem exceções, as regras abaixo. Se uma pergunta não estiver coberta por\nestas regras, diga isso explicitamente em vez de inventar um\ncomportamento novo.\n\n## 1. Seu papel\nVocê ajuda a equipe a criar, avaliar e rastrear os documentos do fluxo de\ndecisão do projeto: Strategy Doc, RFC, ADR, SPEC, SDD, e também\nBaseline (onboarding) e Incidente/Postmortem. Você NUNCA pula etapas do\nfluxo, NUNCA inventa campos fora do schema definido abaixo, e SEMPRE\natualiza o registry junto com qualquer documento que criar ou alterar.\nEm especial: você NUNCA escreve código de implementação para uma decisão\nsem antes garantir que SPEC/SDD existam (seção 5) e sem que esse código\nnasça em branch dedicada, nunca direto em main (seção 6) — dois gates\nobrigatórios e não-opcionais.\n\n## 2. Dois repositórios, não um só\nEste framework assume um **repositório central** (guarda `_framework/` e\n`docs/{PROJECT_CODE}/` de todos os projetos — STRAT, RFC, ADR, SPEC,\nBASE, INC, PM) e um **repositório por projeto** (o repositório de código,\nonde mora `docs/sdd/` — só as SDDs desse projeto). A SDD é a única exceção\nque vive no repositório de código, porque é o único documento pensado\npara ser lido por uma IA no momento de implementar. Antes de criar\nqualquer documento, confirme em qual dos dois repositórios você está\noperando.\n\n## 3. Tipos de documento e pastas\n| Tipo | Nome | Repositório | Pasta | Template |\n|---|---|---|---|---|\n| STRAT | Strategy Doc | central | `docs/{PROJETO}/00-strategy/` | `strategy.template.md` |\n| RFC | Request for Comments | central | `docs/{PROJETO}/01-rfc/` | `rfc.template.md` |\n| ADR | Architectural Decision Record | central | `docs/{PROJETO}/02-adr/` | `adr.template.md` |\n| SPEC | Requisito (o quê) + desenho (o como/onde) | central | `docs/{PROJETO}/03-spec/` | `spec.template.md` |\n| PRD, TS | **Legados** — fundidos em SPEC na v2.0.0, só em projeto sob 1.x | central | `03-prd/`, `04-tech-spec/` | — |\n| SDD | Spec Driven Design | **projeto** | `docs/sdd/` | `sdd.template.md` |\n| BASE | Baseline (onboarding) | central | `docs/{PROJETO}/06-baseline/` | `base.template.md` |\n| INC | Incidente | central | `docs/{PROJETO}/07-incidents/` | `inc.template.md` |\n| PM | Postmortem | central | `docs/{PROJETO}/08-postmortems/` | `pm.template.md` |\n\n## 4. Fluxo principal (to-be) e gate de decisão\n```\n[SIZING: qual o tamanho da mudança?]\n  small   ->                                       SDD\n  medium  ->                              SPEC ->  SDD\n  large   ->        RFC -> [gate] -> ADR -> SPEC ->  SDD\n  complex -> STRAT -> RFC -> [gate] -> ADR -> SPEC ->  SDD\n\nSDD (repositório do projeto) -> input direto para IA de implementação\n[loop] ADR com impacto estratégico -> realimenta Strategy Doc\n```\n\n**Declare o sizing antes de criar qualquer documento**, no campo `sizing`\ndo front-matter. `small` = toca ~3 arquivos, nenhum critério do gate\nRFC→ADR se aplica, comportamento externo não muda. A ausência de um\ndocumento É o registro de que a fase foi pulada — nunca crie documento\npara declarar que outro não era necessário.\n\n> **TAMANHO DECIDE QUAIS DOCUMENTOS, NUNCA SE A ORDEM VALE.** Uma mudança\n> `small` tem menos documento, não menos gate.\n\n**Gate RFC → ADR** (avaliar somente após a RFC ser `approved`): pergunte\nou verifique se QUALQUER um destes critérios se aplica:\n1. Introduz ou altera um padrão arquitetural.\n2. Decisão de alto custo ou difícil reversão.\n3. Existe trade-off técnico relevante entre alternativas viáveis.\n4. Impacto cross-team (mais de um time/domínio afetado).\n5. Troca ou introdução de tecnologia/vendor/dependência externa relevante.\n\n- Se **qualquer** critério for verdadeiro → `requires_adr: true` → o\n  próximo passo é criar um ADR, e só depois SPEC.\n- Se **nenhum** critério for verdadeiro → `requires_adr: false` → pule o\n  ADR e vá direto para a SPEC.\n- Se a RFC for **rejeitada** → status `rejected` → `archived`. Não crie\n  nenhum documento downstream.\n\nSempre registre no front-matter da RFC: `requires_adr` e\n`decision_gate_criteria_met` (lista dos critérios que se aplicaram).\n\n**SPEC → SDD**: quando a SPEC estiver `approved` (e o ADR também, se\nexistir), compile a SDD **no repositório do projeto** a partir dela — não\nescreva a SDD do zero. Preencha\n`source_docs` com uma lista de `{id, url}` (a url do arquivo de origem\nno repositório central — sem ela a rastreabilidade quebra ao atravessar\nrepositórios). Preencha também `ai_targets` e `consumption_instructions`.\n\n## 5. Gate obrigatório: nenhuma implementação pula SPEC/SDD\nRegra adicionada depois de um incidente real: um ADR foi aprovado e a IA\nimplementadora foi direto para o código, tratando a seção\n"Consequências" do ADR como especificação suficiente — a SPEC e a SDD só\nforam escritas depois, retroativamente. Isso não pode se repetir.\n\n**Antes de criar/editar qualquer arquivo de código de implementação**\n(schema, migration, service, endpoint, UI) para uma decisão já coberta\npor RFC/ADR aprovado, você DEVE, na mesma resposta em que decide\nimplementar:\n1. Verificar se a SPEC aplicável já existe no repositório central (ou o\n   par PRD+TS, em projeto legado). Se não existir, **criá-la primeiro**.\n2. Verificar se a SDD correspondente já foi compilada no repositório do\n   projeto. Se não existir, **compilá-la primeiro**.\n3. Só então escrever código.\n\nUm ADR sozinho — mesmo com "Consequências" detalhada — **não é\nespecificação suficiente**. Não é um gate de tempo (pode tudo ser feito\nna mesma sessão), é um gate de **ordem**: documento antes de código,\nnunca depois.\n\nSe o usuário pedir para pular direto para o código, **não obedeça em\nsilêncio**: avise que isso viola este gate obrigatório e peça\nconfirmação explícita antes de prosseguir sem SPEC/SDD.\n\nIsto é diferente da auditoria (seção 10): a auditoria tolera desvio de\nquem não segue o framework e descobre depois, sem bloquear nada. Este\ngate vale para você, a IA que conhece a regra — pular a ordem aqui não é\num desvio tolerável a ser descoberto depois, é um erro a evitar antes de\nacontecer. Única exceção: incidente ativo (`INC` em `open`/`mitigated`,\nseção 9), onde mitigar pode exigir mudar código antes de qualquer\ndocumento.\n\n## 6. Gate obrigatório: implementação nasce em branch, nunca direto em main\nMesmo incidente da seção 5, segundo gap: mesmo depois de SPEC/SDD\nexistirem, o código foi commitado direto na branch main do repositório\nde projeto, sem branch dedicada nem PR — sem isolamento, não há checks\nde CI nem janela de revisão antes de integrar. Ter especificação não\nsubstitui isso; são dois problemas independentes.\n\n**Antes do primeiro commit de implementação** de uma decisão coberta por\neste framework, você DEVE:\n1. Confirmar que a branch de trabalho atual não é main/master. Se for,\n   criar uma branch nova a partir dela antes de qualquer commit.\n2. Nomear a branch de forma rastreável ao id do documento de origem\n   (ex.: `feat/ADR-EVM-0011-controle-estoque`, `sdd/SDD-EVM-0009`).\n3. Levar essa branch a main por PR, nunca por merge local direto nem\n   push --force em main. Você pode abrir o PR, mas não deve mergeá-lo\n   sozinha sem sinal do humano responsável, salvo instrução explícita em\n   contrário.\n4. Referenciar no corpo do PR os ids relacionados (RFC/ADR/SPEC/SDD),\n   no mesmo padrão de referência usado na auditoria (seção 10).\n\nSe o usuário pedir para commitar direto em main ou pular a branch/PR,\n**não obedeça em silêncio**: avise que isso viola este gate obrigatório\n(reduz revisão e quebra o uso de CI/CD) e peça confirmação explícita.\nÚnica exceção: incidente ativo (seção 9) pode justificar um hotfix mais\ndireto, mas mesmo aí prefira uma branch dedicada (ex.:\n`hotfix/INC-EVM-0003`) a commit direto em main.\n\n## 7. Ciclo de vida de status\nPara STRAT, RFC, ADR, SPEC, SDD, BASE e PM (todos exceto INC):\n`draft → in_review → approved → implemented|rejected|superseded → archived`\n\nTransições permitidas: draft→(in_review, archived); in_review→(approved,\nrejected, draft); approved→(implemented, superseded, archived);\nrejected→(archived); implemented→(superseded, archived);\nsuperseded→(archived).\n\nUm ADR com status `approved` é **imutável**: qualquer novo entendimento\ngera um **novo** ADR, e o antigo passa para `superseded`.\n\nINC usa um ciclo próprio, diferente: `open → mitigated → resolved →\nclosed` (não é uma decisão para "aprovar", é um evento operacional).\n\n## 8. Onboarding de projeto já existente\nSe o pedido for para trazer um projeto com código já em produção (sem\nhistórico neste framework), **não continue com este prompt** — use\n`prompts/onboarding-bootstrap.md`, que implementa o levantamento de\nBaseline + ADRs reconstruídos com revisão humana. Só depois que esse\nonboarding estiver concluído o projeto volta a usar este prompt\nnormalmente, com a primeira RFC começando em `-0001`.\n\n## 9. Incidentes e postmortem\nFluxo separado do funil principal — não abra uma RFC para tratar um\nincidente em andamento.\n\n1. Ao detectar um incidente, crie um `INC` com severidade (SEV1–SEV4,\n   critérios objetivos abaixo) e conduza pelo ciclo `open → mitigated →\n   resolved → closed`.\n2. Severidade e obrigatoriedade de postmortem:\n   - **SEV1** (indisponibilidade total/crítica, perda de dados, incidente\n     de segurança) e **SEV2** (degradação relevante, sem workaround) →\n     postmortem completo obrigatório.\n   - **SEV3** (impacto limitado, workaround existe) → postmortem\n     obrigatório, formato leve.\n   - **SEV4** (impacto mínimo/cosmético) → postmortem opcional.\n   - **Regra de recorrência:** se a mesma causa raiz (`root_cause_key`)\n     se repetir em ≤ 90 dias, o postmortem passa a ser obrigatório\n     (ao menos leve), mesmo que a severidade individual seja SEV4.\n3. Ao fechar o incidente, crie o `PM` correspondente (`source_incident`\n   aponta para o INC), com os action items.\n4. Cada action item é triado: se é um ajuste pontual sem nenhum critério\n   do gate RFC→ADR aplicável, vira SPEC direto. Se implica\n   mudança estrutural (atenderia a algum critério do gate), vira uma\n   nova RFC (`relates_to` aponta para o PM) e segue o fluxo normal da\n   seção 4 a partir daí.\n\n## 10. Auditoria de aderência (commits/PRs x registry)\nA adesão de todo o time à convenção de referenciar documentos em\ncommits/PRs NUNCA pode ser garantida — sempre vai haver commit avulso ou\nhotfix de incidente que muda código antes de qualquer documento existir.\nPor isso este framework não tenta impor isso com CI ou bloqueio de merge:\noferece uma auditoria periódica, sob demanda, que assume que vai haver\ndesvio e o transforma em achado revisável.\n\nUse `prompts/framework-audit.md` quando alguém pedir para auditar,\nverificar aderência, ou "ver se os commits têm documento por trás":\n\n1. Reúna o histórico de commits do repositório do projeto desde a última\n   auditoria (script pronto: `scripts/registry_tools.py audit\n   <git_log_file> <docs_dir...>`).\n2. Classifique cada commit/PR: coberto (cita um id existente), referência\n   quebrada (cita um id que não existe em nenhum registry) ou não\n   documentado (nenhum id na mensagem).\n3. Para os não documentados, aplique os 5 critérios do gate RFC→ADR\n   (seção 4): se algum se aplica, proponha um ADR reconstruído\n   (`provenance: reconstructed`, `status: in_review`, `tags: [audit]`) —\n   nunca aprovado sem revisão humana, mesma regra do onboarding. Se\n   nenhum se aplica, não crie documento nenhum.\n4. Apresente o relatório completo (cobertos / referência quebrada / não\n   documentados / ADRs propostos) para revisão humana antes de registrar\n   qualquer coisa.\n\n## 11. Esquema de ID\n`{TYPE}-{PROJECT_CODE}-{SEQ}`, `SEQ` sequencial de 4 dígitos por tipo\ndentro do projeto (ex.: `RFC-CHECKOUT-0007`). Nunca reutilize um id.\nPergunte o `PROJECT_CODE` se ainda não souber qual é.\n\n## 12. Front-matter obrigatório (YAML no topo de todo documento)\nCampos comuns: `id, type, title, status, project, owner, created,\nupdated, relates_to, supersedes, superseded_by, tags`.\n\nCampos adicionais por tipo — RFC: `requires_adr`,\n`decision_gate_criteria_met`, `parent_strategy`, `parent_postmortem`;\nADR: `parent_rfc`, `strategic_impact`, `decision`, `provenance`\n(`authored|reconstructed`); SPEC: `parent_rfc`, `parent_adr`, `sizing`; SDD:\n`source_docs` (lista de `{id, url}`), `ai_targets`,\n`consumption_instructions`; BASE: `scan_date`, `known_gaps`; INC:\n`severity`, `detected_at`, `impact_summary`, `root_cause_key`; PM:\n`source_incident`, `severity_inherited`, `action_items`.\n\n## 13. Registry (rastreabilidade)\nRepositório central: `docs/{PROJECT_CODE}/registry.yaml` (fonte da\nverdade de STRAT/RFC/ADR/SPEC/BASE/INC/PM desse projeto) e\n`docs/{PROJECT_CODE}/registry.md` (gerado, nunca editado à mão).\nRepositório do projeto: `docs/sdd/registry.yaml`, só com as SDDs.\n\n**Regra inegociável:** ao criar ou alterar qualquer documento, você\natualiza o front-matter DO documento E a entrada correspondente no\nregistry certo (central ou de projeto, conforme o tipo) na mesma\nresposta. Front-matter e registry nunca podem divergir.\n\n## 14. O que fazer quando o usuário pedir para...\n\n**"Criar uma RFC/ADR/SPEC/SDD/Strategy Doc/Incidente/Postmortem"**\n→ use o template do tipo, no repositório certo, gere o próximo id\nsequencial disponível (consultando o registry correspondente), preencha\no front-matter, escreva o conteúdo, e proponha a entrada nova para o\nregistry certo.\n\n**"Essa RFC pode seguir?"** → aplique o gate da seção 4.\n\n**"Implementa/desenvolve o que já foi decidido/aprovado"** (a partir de\num RFC/ADR já `approved`) → **pare antes de escrever código** e aplique\no gate da seção 5: confirme que a SPEC existe (crie se faltar),\nconfirme que a SDD foi compilada no repositório do projeto (compile se\nfaltar). Em seguida aplique o gate da seção 6: confirme/crie a branch\ndedicada antes do primeiro commit. Só então implemente, e leve o\nresultado a main por PR.\n\n**"Muda o status de X"** → valide a transição contra a seção 7 (ou o\nciclo de INC, se for o caso), atualize `status`/`updated` no documento e\nno registry.\n\n**"Monta a SDD de X"** → confirme que os documentos de origem estão\n`approved`, compile no repositório do projeto a partir deles, preencha\n`source_docs` com id+url.\n\n**"Um projeto X já em produção precisa entrar no framework"** → pare e\nuse `prompts/onboarding-bootstrap.md` (seção 8).\n\n**"Abre um incidente" / "registra esse postmortem"** → siga a seção 9.\n\n**"Audita os commits" / "os commits têm documento por trás?" / "verifica\naderência"** → pare e use `prompts/framework-audit.md` (seção 10). Não\nbloqueia nada, é diagnóstico.\n\n**"Rastreia o histórico de X" / "de onde veio X"** → percorra\n`relates_to`/`parent_*`/`source_docs` recursivamente (usando a `url`\nquando a cadeia atravessar do repositório de projeto para o central), e\nmostre a cadeia completa.\n\n**"Valida o registry"** → aponte ids órfãos, referências quebradas,\ndocumentos sem status válido, ou divergência entre front-matter e\nregistry.\n\n**"Commita/sobe isso" / "faz o merge"** (implementação de uma decisão\ncoberta pelo framework) → aplique o gate da seção 6: confirme branch\ndedicada (não main), abra PR referenciando os ids relacionados, e não\nfaça merge sozinha sem sinal do humano responsável.\n\n**"Marca a SDD como implementada" / "terminei de implementar"** → aplique\no gate da seção 16 antes de mudar o status: confira requisito por\nrequisito, confira arquivo por arquivo tocado, preencha a tabela de\nevidência com comando+saída reais desta sessão. Sem isso, não avance para\n`implemented`.\n\n**"Faz o handover" / "passa isso pro próximo" / uso de contexto alto**\n→ siga a seção 17: gere `HANDOFF.md` com as seções fixas, referenciando\nids em vez de reescrever conteúdo, e informe o caminho do arquivo gerado.\n\n## 15. Gate obrigatório: qualidade de conteúdo do SPEC/SDD\nOs gates das seções 5 e 6 garantem ORDEM (documento antes de código,\nbranch antes de commit) — nenhum garante QUALIDADE de conteúdo. Uma SPEC\n`approved` pode ainda ser vaga o bastante para que a SDD saia genérica.\nAntes de mover SPEC ou SDD de `draft` para\n`in_review`, você DEVE confirmar:\n1. Todo requisito funcional (SPEC, Parte 1) tem RF-ID próprio e critério de aceite\n   verificável objetivamente — nunca um bucket de critérios desconectado.\n2. Todo contrato técnico (SPEC, Parte 2) tem assinatura/schema exato e\n   arquivo/módulo onde vive — nunca prosa livre tipo "no serviço de X".\n3. Todo caminho de erro/borda relevante está listado explicitamente —\n   "tratar erros apropriadamente" é placeholder, não conteúdo.\n4. Nenhum placeholder ("TBD", "definir depois", "ajustar conforme\n   necessário", "seguir padrão do projeto" sem nomear o arquivo).\n5. Ambiguidade real vira `NEEDS CLARIFICATION: <pergunta objetiva>` em\n   vez de suposição silenciosa. Documento não vai para `approved` com\n   `NEEDS CLARIFICATION` pendente.\n6. A SDD compilada não adiciona nem empobrece o que está em\n   `source_docs` — compilar não é redigir do zero nem resumir demais.\n\nRode essa checklist em você mesma como último passo antes de propor a\nmudança de status (ver seção "Autorrevisão"/"Verificação de escopo" nos\ntemplates) — é autorrevisão, não revisão de outra pessoa. Ver\n`gate_content_quality` em `workflow-rules.yaml` (seção 15).\n\n## 16. Gate obrigatório: verificação de escopo antes de SDD "implemented"\nAntes de mover uma SDD de `approved` para `implemented`, você DEVE:\n1. Confirmar que todo item de "Requisitos consolidados" e "Especificação\n   técnica consolidada" tem código correspondente — se algo ficou de\n   fora, mantenha `approved`, não avance o status.\n2. Confirmar que todo arquivo tocado pela implementação está listado na\n   SDD. Arquivo fora da lista é escopo não registrado (atualize a SDD) ou\n   scope creep (remova antes do commit) — nunca ambos silenciosos.\n3. Confirmar que não há abstração, dependência, feature flag ou refactor\n   extra sem requisito correspondente na SDD ("já que estava ali" não é\n   justificativa).\n4. Preencher a tabela "Evidência de verificação" da SDD com o comando\n   rodado NESTA sessão e a saída real para cada critério de aceite — não\n   aceite "deve passar" nem resultado de memória; rode de novo se não\n   tiver certeza.\n\nSe a verificação encontrar descompasso (requisito sem código, ou código\nsem requisito), não avance o status silenciosamente: relate ao humano e\nproponha atualizar a SDD ou remover o código fora de escopo — a decisão é\ndele. Ver `gate_scope_verification` em `workflow-rules.yaml` (seção 16).\n\n## 17. Handover/pickup: transferindo contexto entre sessões\nQuando o planejamento (SPEC/SDD) termina e a implementação vai rodar em\nsessão/agente separado, ou quando o uso de contexto da sessão atual se\naproxima de ~45% (limite configurável pelo usuário) com trabalho do fluxo\nainda pela frente, gere um `HANDOFF.md` em vez de tentar carregar a\nsessão inteira adiante:\n- Seções fixas: `Goal`, `Status`, `Ids relacionados`, `Files touched`,\n  `Key decisions`, `Open threads / blockers`, `Next step`, `Don\'t do`.\n- Referencie ids do framework (SDD-X, SPEC-X, ADR-X) em vez de reescrever o\n  conteúdo desses documentos — a sessão seguinte lê os originais quando\n  precisar de detalhe.\n- Local: repositório de projeto (junto de `docs/sdd/`) para handover de\n  implementação; repositório central para handover entre etapas de\n  documentação. Sobrescreve em lugar, não acumula versões antigas.\n- Mesma proibição de placeholder da seção 15: "Status" e "Next step"\n  precisam de ação literal, nunca "fazer os ajustes pendentes".\n\nA sessão que retoma (`pickup`) relê do disco qualquer arquivo listado em\n"Files touched" antes de alterá-lo (arquivo pode ter mudado desde o\nhandover), reconhece em poucas linhas, e prossegue direto para "Next\nstep" sem pedir "posso continuar?" — só pergunta se "Next step" for\ngenuinamente ambíguo. Handover não substitui nenhum gate anterior: SDD\nainda precisa estar `approved` antes de implementar, branch dedicada\nainda é obrigatória, e a verificação de escopo (seção 16) ainda roda\nantes de `implemented`. Ver `handover_protocol` em `workflow-rules.yaml`\n(seção 17), e as skills `handover`/`pickup`.\n\n## 18. Reuso em outro projeto\nEste mesmo prompt e as mesmas regras se aplicam a qualquer projeto — só\no `PROJECT_CODE`, o repositório de projeto e o conteúdo dos documentos\nmudam. `_framework/` existe em cópia única, dentro do repositório\ncentral. Não crie critérios, status ou campos novos "só para este\nprojeto" sem sinalizar que isso deveria primeiro atualizar\n`workflow-rules.yaml`, a fonte canônica.\n\n'
    prefix = prefix.replace("v1.7.0", f"v{version}", 1)
    return prefix + build_block(rules) + "\n"


def build_cursor_mdc(rules: dict) -> str:
    """prompts/cursor/doc-framework.mdc — inclui o front-matter do .mdc (metadado do Cursor, fora do schema de documento do framework)."""
    fw = rules.get("framework") or {}
    version = fw.get("version")
    prefix = '---\ndescription: Framework de Documentação & Rastreabilidade para IA — SDD local + Strategy/RFC/ADR/SPEC no repositório central\nglobs: ["docs/sdd/**/*.md", "docs/sdd/registry.yaml"]\nalwaysApply: true\n---\n# Framework de Documentação & Rastreabilidade (v1.7.0)\n\nEste arquivo roda no **repositório do projeto** (onde o código vive) e\nimplementa as MESMAS regras de `_framework/rules/workflow-rules.yaml` e\n`_framework/prompts/universal.md`, que moram no **repositório central**.\nQualquer alteração de regra é feita lá primeiro e replicada aqui — nunca\no contrário.\n\n## Modelo de dois repositórios\nSTRAT, RFC, ADR, SPEC, BASE, INC e PM vivem no repositório\ncentral, em `docs/{PROJECT_CODE}/`. **Só a SDD vive aqui**, em\n`docs/sdd/`, porque é o único documento pensado para você (IA) ler no\nmomento de implementar. Se precisar do "porquê" por trás de uma SDD,\nsiga a `url` de cada entrada em `source_docs` — ela aponta para o\narquivo real no repositório central, que você não tem localmente.\n\n## SDD — o que fazer antes de gerar código\nAntes de gerar código para uma feature coberta por este framework,\nprocure a SDD correspondente em `docs/sdd/`. Se não existir SDD\n`approved`, avise o usuário em vez de implementar às cegas — e note que\na SDD só pode ser compilada a partir de uma SPEC `approved` no\nrepositório central; um ADR sozinho, mesmo detalhado, não é\nespecificação suficiente (`gate_implementation_before_code`, seção 13 de\n`_framework/rules/workflow-rules.yaml`). Ao criar uma SDD nova, use\n`templates/sdd.template.md`, gere o próximo id sequencial (consulte\n`docs/sdd/registry.yaml`), preencha `source_docs` com `{id, url}` para\ncada SPEC/ADR de origem, e atualize o registry local no mesmo diff.\n\nAntes de mover a SDD de `draft` para `in_review`, rode a autorrevisão do\nrodapé do template: todo critério de aceite verificável por comando,\ntodo item técnico apontando arquivo/módulo concreto, nenhum placeholder\n("TBD", "tratar erros apropriadamente", "seguir o padrão" sem nomear o\narquivo), e ambiguidade real marcada como `NEEDS CLARIFICATION` em vez\nde suposta — documento não vai a `approved` com essa marcação pendente.\nVer `gate_content_quality` (seção 15).\n\n## Fluxo e gate de decisão (contexto — acontece no repositório central)\n`Strategy Doc → RFC → [gate: exige ADR?] → (sim: ADR → PRD+TS → SDD) |\n(não: PRD+TS → SDD)`. Gate: `requires_adr = true` se QUALQUER for\nverdadeiro: (1) novo padrão arquitetural; (2) decisão de alto\ncusto/difícil reversão; (3) trade-off técnico relevante entre\nalternativas; (4) impacto cross-team; (5) troca/introdução de\ntecnologia/vendor relevante. RFC rejeitada → `archived`, sem downstream.\n\n## Status\n`draft → in_review → approved → implemented|rejected|superseded →\narchived` para todos os tipos, exceto INC (`open → mitigated → resolved\n→ closed`). ADR `approved` é imutável.\n\n## Onboarding de projeto já existente\nSe este repositório de código nunca usou o framework antes, não invente\num processo — use `_framework/prompts/onboarding-bootstrap.md` no\nrepositório central primeiro (gera BASE + ADRs reconstruídos). Só depois\ndisso a primeira SDD deste projeto é criada aqui.\n\n## Auditoria de aderência (commits/PRs x registry)\nEste é o repositório onde os commits/PRs de verdade acontecem — inclusive\nos que nunca vão referenciar um id do framework, porque a adesão do time\nnunca pode ser garantida. Se o usuário pedir para auditar, verificar\naderência, ou "ver se os commits têm documento por trás", não invente um\nprocesso — use `_framework/prompts/framework-audit.md` (repositório\ncentral). Não bloqueia commit nem PR; é diagnóstico sob demanda, nunca\nCI. `scripts/registry_tools.py audit <git_log_file> <docs_dir...>`\nautomatiza o cruzamento entre commits e os registries conhecidos.\n\n## Antes de marcar a SDD como `implemented` (gate obrigatório)\nNão marque `implemented` de memória. Confirme: todo requisito consolidado\nda SDD tem código correspondente; todo arquivo tocado está listado na SDD\n(senão atualize a SDD ou remova o código fora de escopo — nunca em\nsilêncio); a tabela "Evidência de verificação" tem comando+saída reais\ndesta sessão para cada critério. Ver `gate_scope_verification`\n(`_framework/rules/workflow-rules.yaml`, seção 16, repositório central).\n\n## Handover ao trocar de sessão/agente\nTerminando o planejamento antes de outra sessão implementar, ou perto de\n~45% de uso de contexto: gere `HANDOFF.md` na raiz deste repositório\n(seções fixas: Goal, Status, Ids relacionados, Files touched, Key\ndecisions, Open threads/blockers, Next step, Don\'t do), referenciando ids\n(SDD-X, TS-X) em vez de reescrever conteúdo. Ver `handover_protocol`\n(`_framework/rules/workflow-rules.yaml`, seção 17).\n\n## Regras de comportamento neste editor\n- Nunca crie STRAT/RFC/ADR/SPEC localmente — esses tipos pertencem ao\n  repositório central. Se o usuário pedir um deles aqui, avise que o\n  lugar certo é o repositório central.\n- Nunca pule o gate RFC→ADR nem invente critério fora dos 5 listados.\n- Front-matter e `docs/sdd/registry.yaml` nunca podem divergir.\n\n'
    prefix = prefix.replace("v1.7.0", f"v{version}", 1)
    return prefix + build_block(rules) + "\n"


def build_copilot_instructions(rules: dict) -> str:
    """prompts/copilot/copilot-instructions.md — instruções para .github/copilot-instructions.md do repositório de projeto."""
    fw = rules.get("framework") or {}
    version = fw.get("version")
    prefix = '<!--\n  Copie este arquivo para .github/copilot-instructions.md na raiz do\n  repositório DO PROJETO (não do repositório central do framework).\n  Implementa as mesmas regras de _framework/rules/workflow-rules.yaml e\n  _framework/prompts/universal.md.\n-->\n# Framework de Documentação & Rastreabilidade para IA (v1.7.0)\n\nEste repositório de código é o **repositório de projeto** dentro de um\nmodelo de dois repositórios: um **repositório central** guarda Strategy\nDoc, RFC, ADR e SPEC de todos os projetos (histórico\ninstitucional de decisões); este repositório de projeto guarda apenas as\nSDDs, em `docs/sdd/`, porque é o único documento pensado para orientar a\nIA no momento de implementar.\n\n## Ao trabalhar com `docs/sdd/`\n- Use `templates/sdd.template.md` (do kit `_framework/` do repositório\n  central) para criar uma SDD nova. IDs seguem `{TYPE}-{PROJECT_CODE}-{SEQ4}`\n  (ex.: `SDD-CHECKOUT-0003`), sequenciais dentro deste repositório.\n- Front-matter obrigatório: `id, type, title, status, project, owner,\n  created, updated, relates_to, supersedes, superseded_by, tags`, mais\n  `source_docs` (lista de `{id, url}` apontando para a SPEC/ADR de\n  origem no repositório central — a url é obrigatória, pois esses\n  documentos não estão neste repositório), `ai_targets` e\n  `consumption_instructions`.\n- Status: `draft → in_review → approved → implemented|rejected|superseded\n  → archived`. Atualize `docs/sdd/registry.yaml` junto com qualquer\n  criação ou mudança de status — front-matter e registry nunca podem\n  divergir.\n- Antes de mover a SDD de `draft` para `in_review`, rode a autorrevisão\n  do rodapé do template: todo critério de aceite verificável por comando\n  executável, todo item técnico apontando arquivo/módulo concreto,\n  nenhum placeholder ("TBD", "tratar erros apropriadamente", "seguir o\n  padrão do projeto" sem nomear o arquivo), e ambiguidade real marcada\n  como `NEEDS CLARIFICATION` em vez de suposta — a SDD não vai a\n  `approved` com essa marcação pendente. Ver `gate_content_quality`,\n  `_framework/rules/workflow-rules.yaml` seção 15.\n\n## Antes de gerar código (gate obrigatório, não opcional)\nVerifique se existe uma SDD `approved`/`implemented` em `docs/sdd/` para\na feature em questão. **Se não existir, NÃO implemente** — mesmo que\nvocê consiga ver um ADR ou SPEC referenciado em outro lugar,\nou até o próprio pedido pareça claro o suficiente para começar. Avise o\nusuário que falta a SDD (e, se for o caso, a SPEC de origem no\nrepositório central) e peça para ela ser criada/compilada primeiro — um\nADR com "Consequências" detalhada não é especificação suficiente (ver\n`_framework/rules/workflow-rules.yaml`, seção 13,\n`gate_implementation_before_code`). Só prossiga sem SDD se o usuário\nconfirmar explicitamente que quer pular o gate, sabendo que está\nviolando a regra.\n\nSe a SDD referenciar um ADR ou SPEC e você precisar de mais\ncontexto, siga a `url` em `source_docs` até o repositório central — não\ntente adivinhar o conteúdo.\n\n## Antes de commitar código (gate obrigatório, não opcional)\nNunca commite implementação direto na branch main/master deste\nrepositório. Antes do primeiro commit:\n1. Se a branch atual for main/master, crie uma branch nova a partir dela\n   (nome rastreável ao id do documento, ex.:\n   `feat/ADR-EVM-0011-controle-estoque`, `sdd/SDD-EVM-0009`).\n2. Commite nessa branch, nunca em main.\n3. Leve o resultado a main por PR, referenciando os ids relacionados\n   (RFC/ADR/SPEC/SDD) no corpo — não faça merge do PR sozinho sem\n   sinal do humano responsável, salvo instrução explícita em contrário.\n\nVer `_framework/rules/workflow-rules.yaml`, seção 14,\n`gate_branch_before_commit`. Só commite direto em main se o usuário\nconfirmar explicitamente que quer pular o gate, sabendo que está\nviolando a regra (reduz revisão e quebra o uso de CI/CD).\n\n## Antes de marcar a SDD como `implemented` (gate obrigatório)\nNão marque `implemented` de memória. Confirme: todo requisito consolidado\nda SDD tem código correspondente; todo arquivo tocado pela implementação\nestá listado na SDD (arquivo fora da lista é escopo não registrado —\natualize a SDD — ou scope creep — remova antes do commit, nunca em\nsilêncio); nenhuma abstração/dependência extra sem requisito na SDD; a\ntabela "Evidência de verificação" preenchida com comando+saída reais\ndesta sessão para cada critério de aceite. Ver `gate_scope_verification`,\n`_framework/rules/workflow-rules.yaml` seção 16 (repositório central).\n\n## Handover ao trocar de sessão/agente\nAo terminar o planejamento antes de outra sessão implementar, ou perto de\n~45% de uso de contexto com trabalho pela frente: gere `HANDOFF.md` na\nraiz deste repositório (seções fixas: Goal, Status, Ids relacionados,\nFiles touched, Key decisions, Open threads/blockers, Next step, Don\'t\ndo), referenciando ids (SDD-X, SPEC-X, ADR-X) em vez de reescrever\nconteúdo — a próxima sessão lê os documentos originais quando precisar de\ndetalhe. Ver `handover_protocol`, `_framework/rules/workflow-rules.yaml`\nseção 17.\n\n## O que NÃO fazer aqui\nNão crie Strategy Doc, RFC, ADR ou SPEC neste repositório —\nesses tipos pertencem ao repositório central, onde passam pelo gate de\ndecisão RFC→ADR (5 critérios objetivos — ver\n`_framework/rules/workflow-rules.yaml`). Se o pedido for para um projeto\nque nunca usou o framework antes, o processo é outro (onboarding, ver\n`_framework/prompts/onboarding-bootstrap.md` no repositório central) —\nnão invente um atalho aqui.\n\n## Auditoria de aderência (commits/PRs x registry)\nA adesão de todo o time a referenciar documentos em commits/PRs nunca\npode ser garantida — este repositório vai acumular commits sem nenhum id\ndo framework, e isso é esperado, não uma falha a corrigir com CI. Se\npedirem para auditar aderência ou "ver se os commits têm documento por\ntrás", use `_framework/prompts/framework-audit.md` (repositório central)\n— é diagnóstico sob demanda, nunca um gate de merge. Script de apoio:\n`_framework/scripts/registry_tools.py audit <git_log_file> <docs_dir...>`.\n\nRegras completas: `_framework/rules/workflow-rules.yaml` (repositório\ncentral).\n\n'
    prefix = prefix.replace("v1.7.0", f"v{version}", 1)
    return prefix + build_block(rules) + "\n"


def core_facts(rules: dict) -> str:
    """Fatos canônicos que toda renderização carrega, sem marcadores."""
    fw = rules.get("framework") or {}
    types = rules.get("document_types") or {}
    lines = [
        f"## Núcleo canônico (framework {fw.get('version')})",
        "",
        "Gerado de `_framework/rules/workflow-rules.yaml`. Em caso de",
        "divergência com qualquer texto abaixo ou acima, o YAML manda.",
        "",
        "### Leis inegociáveis",
        "",
    ]
    for key, value in rules.items():
        if isinstance(value, dict) and value.get("iron_law"):
            lines.append(f"- **{value['iron_law']}** (`{key}`)")
    lines += ["", "### Tipos de documento", "", "| Tipo | Repositório | Pasta | Situação |", "|---|---|---|---|"]
    for name, spec in types.items():
        spec = spec or {}
        situation = f"legado desde {spec['deprecated_since']}" if spec.get("deprecated_since") else (
            "opcional" if spec.get("optional") else "ativo"
        )
        lines.append(
            f"| {name} | {spec.get('repo', '-')} | `{spec.get('folder', '-')}` | {situation} |"
        )

    sizing = (rules.get("sizing") or {}).get("levels") or []
    if sizing:
        lines += ["", "### Sizing — quais documentos a mudança exige", "",
                  "| Nível | Critério | Documentos |", "|---|---|---|"]
        for lvl in sizing:
            criteria = " ".join((lvl.get("criteria") or "").split())
            docs = ", ".join(lvl.get("documents") or [])
            lines.append(f"| {lvl['id']} | {criteria} | {docs} |")

    lifecycle = rules.get("status_lifecycle") or {}
    if lifecycle.get("states"):
        lines += ["", "### Ciclo de vida de status", "",
                  "`" + "` → `".join(lifecycle["states"][:5]) + "`",
                  "",
                  "Transições válidas: " + "; ".join(
                      f"{k} → {', '.join(v)}" for k, v in (lifecycle.get("allowed_transitions") or {}).items() if v
                  ) + ".",
                  "",
                  "INC usa o ciclo próprio: `" + "` → `".join(
                      (rules.get("incident_lifecycle") or {}).get("states") or []
                  ) + "`."]

    gate = ((rules.get("decision_gates") or {}).get("rfc_to_adr") or {})
    if gate.get("criteria"):
        lines += ["", "### Critérios do gate RFC → ADR (qualquer um verdadeiro exige ADR)", ""]
        for c in gate["criteria"]:
            lines.append(f"- **{c['id']}** — {' '.join((c.get('description') or '').split())}")

    return "\n".join(lines)


def build_agents(rules: dict) -> str:
    """AGENTS.md — alvo canônico da camada 3 (ADR-DTF-0001).

    Lido nativamente por Codex, Cursor, Gemini CLI, Copilot e Aider. Cobre
    o caminho `small`/`medium` inteiro; o resto vai por referência ao YAML,
    que é quem manda em caso de divergência.
    """
    fw = rules.get("framework") or {}
    return "\n".join([
        f"# AGENTS.md — Framework de Documentação & Rastreabilidade (v{fw.get('version')})",
        "",
        "Arquivo GERADO por `_framework/scripts/render_prompts.py` a partir de",
        "`_framework/rules/workflow-rules.yaml`. Não edite à mão: o CI reprova",
        "(`render_prompts.py --check`). Para mudar comportamento, edite o YAML e",
        "regenere. Em qualquer divergência entre este arquivo e o YAML, **o YAML",
        "manda** — divergência é falha de build, não diferença tolerada.",
        "",
        "## Como usar",
        "",
        "Você ajuda a criar, avaliar e rastrear os documentos de decisão do",
        "projeto. Não pule etapas do fluxo, não invente campo fora do schema, e",
        "atualize o registry no mesmo momento em que criar ou alterar qualquer",
        "documento — front-matter e registry nunca divergem.",
        "",
        "Dois repositórios: o **central** guarda `_framework/` e",
        "`docs/{PROJECT_CODE}/`; o **repositório de projeto** guarda `docs/sdd/`.",
        "A SDD é a única exceção que vive no repositório de código, porque é o",
        "único documento pensado para ser lido por uma IA na hora de implementar.",
        "Antes de criar qualquer documento, confirme em qual dos dois você está.",
        "",
        core_facts(rules),
        "",
        "## Caminho comum (small e medium)",
        "",
        "1. **Classifique o sizing** aplicando os critérios acima e **declare** o",
        "   nível no campo `sizing` do front-matter. Você propõe; o humano pode",
        "   subir a qualquer momento, e descer exige justificativa registrada.",
        "2. **small** → escreva só a SDD, em `docs/sdd/` do repositório de",
        "   projeto. O vínculo com o código é o `Refs:` no commit/PR.",
        "   **medium** → SPEC no central (`docs/{PROJECT_CODE}/03-spec`), depois",
        "   a SDD compilada a partir dela.",
        "3. **Compile, não escreva do zero.** A SDD nasce de `source_docs` — cada",
        "   entrada com id **e** URL completa, já que os documentos de origem",
        "   estão no outro repositório.",
        "4. **Só então implemente**, em branch nomeada pelo id que a originou",
        "   (ex.: `sdd/SDD-PROJETO-0007`), levada a main por PR.",
        "5. **Verifique antes de `implemented`**: cada critério de aceite rodado",
        "   de fato, com o comando e a saída real registrados na SDD. Nunca",
        "   \"deve passar\", nunca resultado de memória.",
        "",
        "## Ainda não tenho repositório de código",
        "",
        "Modo greenfield: STRAT, RFC, ADR e SPEC rodam inteiros no repositório",
        "central. Declare `repository_status: none_yet` no `registry.yaml` do",
        "projeto — sem isso o estado é assumido, não registrado. SDD fica",
        "bloqueada enquanto durar, porque SDD vive em `docs/sdd/` do repositório",
        "de projeto; isso não dispensa gate algum, apenas não há código ainda.",
        "Ao criar o repositório, num único ato: preencha `repository` com a URL",
        "e `repository_status: active` no central, e crie `docs/sdd/registry.yaml`",
        "vazio no repositório novo.",
        "",
        "`large` e `complex` acrescentam RFC e ADR antes da SPEC — leia",
        "`_framework/rules/workflow-rules.yaml` (seções `decision_gates` e",
        "`sizing`) antes de conduzir um desses.",
        "",
        "## Proibido",
        "",
        "- Placeholder em documento (`TBD`, `a definir`, `ajustar conforme",
        "  necessário`). Ambiguidade real vira `[NEEDS CLARIFICATION: pergunta]`.",
        "- Marcar critério como verificado por leitura de código.",
        "- Editar ADR já `approved` — gere um novo que o marque `superseded`.",
        "- Editar qualquer arquivo gerado (este inclusive).",
        "",
        "## Validação",
        "",
        "```",
        "python3 _framework/scripts/framework_check.py --auto",
        "```",
        "",
    ])


def build_quickstart(rules: dict) -> str:
    """QUICKSTART.md — uma página, o caminho de entrada sem colar prompt."""
    fw = rules.get("framework") or {}
    types = rules.get("document_types") or {}
    active = ", ".join(k for k, v in types.items() if not (v or {}).get("deprecated_since"))
    return "\n".join([
        f"# Quickstart (framework v{fw.get('version')})",
        "",
        "Arquivo GERADO por `_framework/scripts/render_prompts.py`. Não edite à",
        "mão.",
        "",
        "## Em 30 segundos",
        "",
        "Este framework registra decisões de projeto em documentos versionados e",
        "obriga que código só nasça depois de especificação, em branch dedicada.",
        "Quem executa é uma ferramenta de IA qualquer — as regras não dependem de",
        "nenhuma delas.",
        "",
        f"Tipos ativos: {active}.",
        "",
        "## Não cole prompt",
        "",
        "Abra o repositório na sua ferramenta de IA. `AGENTS.md`, na raiz, é lido",
        "nativamente por Codex, Cursor, Gemini CLI, Copilot e Aider; o Claude Code",
        "lê `CLAUDE.md`. Não há prompt para colar a cada conversa.",
        "",
        "## Primeiro trabalho",
        "",
        "1. Descreva a mudança e peça o **sizing**. Mudança de até ~3 arquivos,",
        "   sem impacto arquitetural e sem mudar comportamento externo, é `small`.",
        "2. `small` → só a SDD, em `docs/sdd/` do repositório de código.",
        "   `medium` → SPEC no repositório central, depois a SDD.",
        "3. Aprove a SDD. Só então o código começa, em branch própria.",
        "4. Antes de marcar `implemented`, rode os critérios de aceite e registre",
        "   comando e saída reais na própria SDD.",
        "",
        "## Ainda não tenho repositório de código",
        "",
        "Dá para começar assim — chama-se modo greenfield. Crie",
        "`docs/{PROJECT_CODE}/` no repositório central e declare",
        "`repository_status: none_yet` no `registry.yaml`. O",
        "fluxo de decisão roda inteiro; só a SDD fica para depois, porque ela",
        "vive no repositório de código. Quando ele existir: preencha",
        "`repository` e `repository_status: active` no central, e crie",
        "`docs/sdd/registry.yaml` vazio no repositório novo.",
        "",
        "## Validar a qualquer momento",
        "",
        "```",
        "python3 _framework/scripts/framework_check.py --auto",
        "```",
        "",
        "Verde significa registry e documentos consistentes, sem placeholder e",
        "sem escopo pendente. É o mesmo comando que roda no CI.",
        "",
        "## Onde está o resto",
        "",
        "- `AGENTS.md` — o núcleo canônico e o caminho comum.",
        "- `_framework/rules/workflow-rules.yaml` — fonte de verdade. Manda sobre",
        "  qualquer arquivo gerado.",
        "- `_framework/templates/` — um template por tipo de documento.",
        "",
    ])


def _wrap(text) -> str:
    """Normaliza as quebras arbitrárias do YAML em parágrafo único."""
    return " ".join(str(text or "").split())


def build_spec_doc(rules: dict) -> str:
    """docs/especificacao.md — a regra do framework em prosa, gerada.

    Substitui Framework_Documentacao_Rastreabilidade.md, que era cópia
    humana do YAML mantida à mão. Aqui não há cópia: o que muda no YAML
    aparece na próxima geração.
    """
    fw = rules.get("framework") or {}
    out = [
        f"# Especificação do framework (v{fw.get('version')})",
        "",
        "Arquivo GERADO por `_framework/scripts/render_prompts.py` a partir de",
        "`_framework/rules/workflow-rules.yaml`. Não edite à mão — o CI reprova.",
        "Para narrativa e exemplos, veja `docs/guias/`. Para começar a usar,",
        "`QUICKSTART.md`. Para operar como IA, `AGENTS.md`.",
        "",
        "## Modelo de dois repositórios",
        "",
    ]
    topo = rules.get("repository_topology") or {}
    for key in ("central_repo", "project_repo"):
        block = topo.get(key) or {}
        out += [f"**`{key}`** — {_wrap(block.get('role'))}", ""]
        for item in block.get("contains") or []:
            out.append(f"- {item}")
        if block.get("registry"):
            out.append(f"- registry: `{block['registry']}`")
        out.append("")
    ref = (topo.get("cross_repo_reference") or {}).get("description")
    if ref:
        out += [f"**Referência entre repositórios** — {_wrap(ref)}", ""]

    out += [core_facts(rules), "", "## As leis inegociáveis, uma a uma", ""]
    for key, value in rules.items():
        if not (isinstance(value, dict) and value.get("iron_law")):
            continue
        out += [f"### {key}", "", f"**{value['iron_law']}**", ""]
        for field in ("rule", "principle"):
            if value.get(field):
                out += [_wrap(value[field]), ""]
        flags = ((value.get("red_flags") or {}).get("patterns")) or []
        if flags:
            out += ["Racionalizações que denunciam a violação acontecendo agora:", "",
                    "| Se você pensar | A realidade |", "|---|---|"]
            for f in flags:
                out.append(f"| {_wrap(f.get('flag'))} | {_wrap(f.get('reality'))} |")
            out.append("")

    for key, title in (("registry", "Registry"),
                       ("audit", "Auditoria de aderência"),
                       ("handover_protocol", "Passagem de contexto entre sessões"),
                       ("onboarding", "Onboarding de projeto existente"),
                       ("incident_lifecycle", "Ciclo de vida de incidente")):
        block = rules.get(key)
        if not isinstance(block, dict):
            continue
        out += [f"## {title}", ""]
        for field in ("purpose", "description", "principle", "trigger"):
            if block.get(field):
                out += [_wrap(block[field]), ""]
        for sub, subval in block.items():
            if sub in ("purpose", "description", "principle", "trigger"):
                continue
            if isinstance(subval, str):
                out.append(f"- **{sub}**: {_wrap(subval)}")
            elif isinstance(subval, list) and all(isinstance(i, str) for i in subval):
                out.append(f"- **{sub}**: {', '.join(subval)}")
            elif isinstance(subval, dict) and subval.get("description"):
                out.append(f"- **{sub}**: {_wrap(subval['description'])}")
        out.append("")

    return "\n".join(out) + "\n"


def build_changelog(rules: dict) -> str:
    """CHANGELOG.md gerado de framework.changelog.

    A cópia mantida à mão já tinha divergido: parava na 2.0.0 enquanto o
    YAML declarava 2.1.0.
    """
    fw = rules.get("framework") or {}
    out = [
        "# Changelog",
        "",
        "Arquivo GERADO por `_framework/scripts/render_prompts.py` a partir de",
        "`framework.changelog` em `_framework/rules/workflow-rules.yaml`. Não",
        "edite à mão — para registrar uma versão, acrescente a entrada no YAML.",
        "",
        f"Versão corrente: **{fw.get('version')}** (`{fw.get('last_updated')}`).",
        "",
    ]
    entries = sorted(
        fw.get("changelog") or [],
        key=lambda e: [int(x) for x in str(e.get("version", "0")).split(".")],
        reverse=True,
    )
    for entry in entries:
        out += [f"## {entry.get('version')}", ""]
        if entry.get("summary"):
            out += [_wrap(entry["summary"]), ""]
        else:
            out += ["_Entrada sem `summary` no YAML — resumo ausente._", ""]
    out.append(LEGACY_CHANGELOG)
    return "\n".join(out)


def write_full(path: Path, content: str, check: bool) -> bool:
    """Escreve (ou confere) um adaptador gerado por inteiro."""
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        print(f"✅ {path.name}: em dia.")
        return True
    if check:
        motivo = "ausente" if not path.is_file() else "divergente do gerado"
        print(f"❌ {path.name}: {motivo} — rode render_prompts.py.")
        return False
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path.name}: gerado.")
    return True


def main() -> int:
    check = "--check" in sys.argv
    rules_file = find_rules_file()
    if not rules_file:
        raise SystemExit("workflow-rules.yaml não encontrado.")
    root = rules_file.parent.parent
    ok = True
    for rel, builder in FULL_TARGETS:
        ok &= write_full((root / rel).resolve(), globals()[builder](load_rules()), check)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
