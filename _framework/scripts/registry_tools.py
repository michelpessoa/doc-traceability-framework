#!/usr/bin/env python3
"""
registry_tools.py

Ferramentas de linha de comando sobre docs/registry.yaml, implementando
as capacidades "validate_registry" e "trace" descritas em
_framework/rules/workflow-rules.yaml (seção 8).

Uso:
    python3 registry_tools.py validate <caminho_para_docs>
    python3 registry_tools.py trace <caminho_para_docs> <ID>

validate: procura ids duplicados, referências quebradas em relates_to/
          parent_* e status inválidos.
trace:    imprime a cadeia completa de um id (ancestrais e descendentes),
          percorrendo relates_to recursivamente.

Requer PyYAML (pip install pyyaml --break-system-packages).
"""
import sys
from pathlib import Path
import yaml

VALID_STATUSES = {
    "draft", "in_review", "approved", "rejected",
    "implemented", "superseded", "archived",
}
# INC não usa o ciclo de vida padrão (ver workflow-rules.yaml, incident_lifecycle)
INCIDENT_STATUSES = {"open", "mitigated", "resolved", "closed"}


def load(docs_dir: Path):
    path = docs_dir / "registry.yaml"
    if not path.exists():
        raise SystemExit(f"Não encontrado: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    docs = {d["id"]: d for d in data.get("documents", [])}
    return data, docs


def registry_mode(data):
    """
    'project'  -> registry só contém SDD (repositório de projeto)
    'central'  -> qualquer outro caso (repositório central)
    Usado para decidir quais referências cruzando repositório são
    esperadas (externas) em vez de um erro de consistência.
    """
    types = {d.get("type") for d in data.get("documents", [])}
    if types and types <= {"SDD"}:
        return "project"
    return "central"


def cmd_validate(docs_dir: Path) -> int:
    data, docs = load(docs_dir)
    problems = []
    mode = registry_mode(data)

    def is_expected_external(target_id):
        if not isinstance(target_id, str):
            return False
        if mode == "project":
            # Registry de projeto só tem SDD; qualquer referência a outro
            # tipo (PRD/TS/ADR/...) é esperada — vive no repositório central.
            return not target_id.startswith("SDD-")
        # Registry central nunca contém SDD por desenho (vive no
        # repositório de projeto) — referência a SDD é esperada, não erro.
        return target_id.startswith("SDD-")

    seen = {}
    for d in data.get("documents", []):
        did = d.get("id")
        if did in seen:
            problems.append(f"ID duplicado: {did}")
        seen[did] = True

        status = d.get("status")
        allowed = INCIDENT_STATUSES if d.get("type") == "INC" else VALID_STATUSES
        if status not in allowed:
            problems.append(f"{did}: status inválido '{status}'")

        for rel in d.get("relates_to") or []:
            if rel not in docs and not is_expected_external(rel):
                problems.append(f"{did}: relates_to aponta para id inexistente '{rel}'")

        for field in ("parent_rfc", "parent_adr", "parent_strategy", "parent_postmortem", "supersedes", "superseded_by"):
            val = d.get(field)
            if val and val not in docs and not is_expected_external(val):
                problems.append(f"{did}: {field} aponta para id inexistente '{val}'")

        for sd in d.get("source_docs") or []:
            sid = sd.get("id") if isinstance(sd, dict) else sd
            if sid not in docs and not is_expected_external(sid):
                problems.append(f"{did}: source_docs aponta para id inexistente '{sid}'")

    if problems:
        print(f"❌ {len(problems)} problema(s) encontrado(s):")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"✅ registry.yaml consistente ({len(docs)} documentos, nenhum problema encontrado).")
    return 0


def cmd_trace(docs_dir: Path, target_id: str) -> int:
    _, docs = load(docs_dir)
    if target_id not in docs:
        print(f"❌ id não encontrado no registry: {target_id}")
        return 1

    visited = set()

    def walk(doc_id, depth=0):
        if doc_id in visited or doc_id not in docs:
            return
        visited.add(doc_id)
        d = docs[doc_id]
        prefix = "  " * depth
        print(f"{prefix}- {doc_id} [{d.get('type')}] {d.get('title')} ({d.get('status')})")
        for rel in d.get("relates_to") or []:
            walk(rel, depth + 1)

    print(f"Cadeia de rastreabilidade a partir de {target_id}:\n")
    walk(target_id)
    return 0


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    action = sys.argv[1]
    docs_dir = Path(sys.argv[2])
    if action == "validate":
        sys.exit(cmd_validate(docs_dir))
    elif action == "trace":
        if len(sys.argv) < 4:
            print("Uso: registry_tools.py trace <docs_dir> <ID>")
            sys.exit(1)
        sys.exit(cmd_trace(docs_dir, sys.argv[3]))
    else:
        print(f"Ação desconhecida: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
