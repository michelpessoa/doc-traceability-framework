#!/usr/bin/env python3
"""
generate_registry_md.py

Gera docs/registry.md (visão humana em tabela) a partir de docs/registry.yaml
(fonte da verdade). Nunca editar registry.md à mão — ele é sempre
regenerado a partir do YAML.

Uso:
    python3 generate_registry_md.py <caminho_para_docs> [--check]

--check não escreve: sai 1 se o registry.md em disco divergir do gerado.
A saída é determinística (sem hora de geração). O cabeçalho mostra a versão
corrente do framework quando workflow-rules.yaml é encontrado; senão,
`framework_version` do registry.yaml (versão de mapeamento).

Se <caminho_para_docs> for omitido, assume "docs" no diretório atual.
Requer PyYAML (pip install pyyaml --break-system-packages).
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import find_rules_file, load_rules  # noqa: E402

# Ordem embutida, usada só quando workflow-rules.yaml não é acessível.
# Com o YAML, vale a ordem de document_types + legacy_document_types
# (SDD-DTF-0055); um teste reprova se as duas divergirem.
TYPE_ORDER = ["STRAT", "RFC", "ADR", "SPEC", "SDD", "BASE", "INC", "PM", "PRD", "TS"]
TYPE_LABEL = {
    "STRAT": "Strategy Doc",
    "RFC": "RFC",
    "ADR": "ADR",
    "SPEC": "SPEC",
    "SDD": "SDD",
    "BASE": "Baseline",
    "INC": "Incidente",
    "PM": "Postmortem",
    "PRD": "PRD",
    "TS": "Tech Spec",
}
UNDECLARED_LABEL = "Tipo não declarado: {type}"


def _declared_types(rules: dict) -> dict:
    return {**(rules.get("document_types") or {}), **(rules.get("legacy_document_types") or {})}


def type_order(rules: dict) -> list[str]:
    """Ordem das seções: chaves de document_types, depois legacy_document_types."""
    order = list(_declared_types(rules))
    return order or list(TYPE_ORDER)


def type_label(doc_type: str, rules: dict) -> str:
    """Rótulo curto embutido; senão o `name` do YAML; senão tipo não declarado."""
    if doc_type in TYPE_LABEL:
        return TYPE_LABEL[doc_type]
    name = (_declared_types(rules).get(doc_type) or {}).get("name")
    return str(name) if name else UNDECLARED_LABEL.format(type=doc_type)


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
            f"| `{d['id']}` | {d.get('title', '')} | {d.get('status', '')} "
            f"| {d.get('owner', '')} | {d.get('updated', '')} | {related} |"
        )
    return header + "\n".join(rows) + "\n"


def render_header(project: str, fw_version: str) -> str:
    """Cabeçalho do registry.md, sem hora de geração (RF08)."""
    return (
        f"# Registry — Projeto {project}\n\n"
        "_Gerado automaticamente a partir de `registry.yaml`. Não editar "
        f"manualmente. Framework v{fw_version}._\n"
    )


def current_framework_version() -> str | None:
    """Versão corrente do framework, se o YAML for acessível a partir deste script."""
    if not find_rules_file():
        return None
    version = (load_rules().get("framework") or {}).get("version")
    return str(version) if version else None


def render_registry(data: dict) -> str:
    project = data.get("project", "N/D")
    fw_version = current_framework_version() or data.get("framework_version", "N/D")
    documents = data.get("documents", [])
    rules = load_rules() if find_rules_file() else {}

    by_type: dict[str, list] = {}
    for d in documents:
        by_type.setdefault(str(d.get("type") or ""), []).append(d)

    lines = [render_header(project, str(fw_version))]
    repository = data.get("repository")
    if repository:
        lines.append(f"Repositório de código: {repository}\n")
    lines.append(f"Total de documentos: **{len(documents)}**\n")

    order = type_order(rules)
    order += sorted(t for t in by_type if t not in order)
    for t in order:
        docs_of_type = by_type.get(t, [])
        if not docs_of_type:
            continue
        lines.append(f"\n## {type_label(t, rules)} ({len(docs_of_type)})\n")
        lines.append(render_table(docs_of_type))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check = "--check" in args
    args = [a for a in args if a != "--check"]
    docs_dir = Path(args[0]) if args else Path("docs")
    data = load_registry(docs_dir)
    content = render_registry(data)
    out_path = docs_dir / "registry.md"
    if check:
        if out_path.is_file() and out_path.read_text(encoding="utf-8") == content:
            print(f"✅ {out_path}: em dia.")
            return 0
        print(f"❌ {out_path}: divergente do gerado — rode generate_registry_md.py.")
        return 1
    out_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"OK: {out_path} gerado com {len(data.get('documents', []))} documentos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
