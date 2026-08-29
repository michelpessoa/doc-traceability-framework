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

# Renderizações antigas: só o miolo entre marcadores é gerado; o texto ao
# redor continua escrito à mão. Viram arquivos inteiros gerados na etapa 2
# de SPEC-DTF-0001.
TARGETS = [
    "prompts/universal.md",
    "prompts/cursor/doc-framework.mdc",
    "prompts/copilot/copilot-instructions.md",
]

# Adaptadores da camada 3 gerados por INTEIRO — nada neles é escrito à
# mão, e `--check` reprova qualquer edição manual. Caminhos relativos à
# raiz de _framework; `../` aponta para a raiz do repositório.
FULL_TARGETS = [
    ("../AGENTS.md", "build_agents"),
    ("../QUICKSTART.md", "build_quickstart"),
    ("../docs/especificacao.md", "build_spec_doc"),
    ("../CHANGELOG.md", "build_changelog"),
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


def apply(path: Path, block: str, check: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        current = text[start:end]
        if current == block:
            print(f"✅ {path}: bloco em dia.")
            return True
        if check:
            print(f"❌ {path}: bloco gerado desatualizado.")
            return False
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")
    else:
        if check:
            print(f"❌ {path}: sem bloco gerado — rode render_prompts.py.")
            return False
        path.write_text(text.rstrip("\n") + "\n\n" + block + "\n", encoding="utf-8")
    print(f"✅ {path}: bloco {'ok' if check else 'atualizado'}.")
    return True


def main() -> int:
    check = "--check" in sys.argv
    rules_file = find_rules_file()
    if not rules_file:
        raise SystemExit("workflow-rules.yaml não encontrado.")
    root = rules_file.parent.parent
    block = build_block(load_rules())

    ok = True
    for rel, builder in FULL_TARGETS:
        ok &= write_full((root / rel).resolve(), globals()[builder](load_rules()), check)

    for rel in TARGETS:
        path = root / rel
        if not path.is_file():
            print(f"⚠️  {rel}: não encontrado — pulando.")
            continue
        ok &= apply(path, block, check)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
