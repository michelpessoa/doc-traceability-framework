#!/usr/bin/env python3
"""
generate_registry_md.py

Gera docs/registry.md (visão humana em tabela) a partir de docs/registry.yaml
(fonte da verdade). Nunca editar registry.md à mão — ele é sempre
regenerado a partir do YAML.

Uso:
    python3 generate_registry_md.py <caminho_para_docs>

Se <caminho_para_docs> for omitido, assume "docs" no diretório atual.
Requer PyYAML (pip install pyyaml --break-system-packages).
"""
import sys
import yaml
from pathlib import Path
from datetime import datetime

TYPE_ORDER = ["STRAT", "RFC", "ADR", "PRD", "TS", "SDD"]
TYPE_LABEL = {
    "STRAT": "Strategy Doc",
    "RFC": "RFC",
    "ADR": "ADR",
    "PRD": "PRD",
    "TS": "Tech Spec",
    "SDD": "SDD",
}


def load_registry(docs_dir: Path) -> dict:
    registry_path = docs_dir / "registry.yaml"
    if not registry_path.exists():
        raise SystemExit(f"Não encontrado: {registry_path}")
    with registry_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def render_table(docs: list) -> str:
    header = "| ID | Título | Status | Owner | Atualizado | Relacionados |\n"
    header += "|---|---|---|---|---|---|\n"
    rows = []
    for d in docs:
        related = ", ".join(d.get("relates_to") or []) or "—"
        rows.append(
            f"| `{d['id']}` | {d.get('title','')} | {d.get('status','')} "
            f"| {d.get('owner','')} | {d.get('updated','')} | {related} |"
        )
    return header + "\n".join(rows) + "\n"


def main():
    docs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    data = load_registry(docs_dir)
    project = data.get("project", "N/D")
    fw_version = data.get("framework_version", "N/D")
    documents = data.get("documents", [])

    by_type = {t: [] for t in TYPE_ORDER}
    for d in documents:
        by_type.setdefault(d.get("type", "?"), []).append(d)

    lines = []
    lines.append(f"# Registry — Projeto {project}\n")
    lines.append(
        f"_Gerado automaticamente a partir de `registry.yaml` em "
        f"{datetime.now():%Y-%m-%d %H:%M}. Não editar manualmente. "
        f"Framework v{fw_version}._\n"
    )
    total = len(documents)
    lines.append(f"Total de documentos: **{total}**\n")

    for t in TYPE_ORDER:
        docs_of_type = by_type.get(t, [])
        if not docs_of_type:
            continue
        lines.append(f"\n## {TYPE_LABEL[t]} ({len(docs_of_type)})\n")
        lines.append(render_table(docs_of_type))

    out_path = docs_dir / "registry.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: {out_path} gerado com {total} documentos.")


if __name__ == "__main__":
    main()
