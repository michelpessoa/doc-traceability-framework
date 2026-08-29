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

TARGETS = [
    "prompts/universal.md",
    "prompts/cursor/doc-framework.mdc",
    "prompts/copilot/copilot-instructions.md",
]


def build_block(rules: dict) -> str:
    fw = rules.get("framework") or {}
    types = rules.get("document_types") or {}
    lines = [
        BEGIN,
        "",
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

    lines += ["", END]
    return "\n".join(lines)


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
    for rel in TARGETS:
        path = root / rel
        if not path.is_file():
            print(f"⚠️  {rel}: não encontrado — pulando.")
            continue
        ok &= apply(path, block, check)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
