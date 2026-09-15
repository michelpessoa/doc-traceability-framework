#!/usr/bin/env python3
"""
hook_post_edit.py

Hook PostToolUse (Edit|Write) do Claude Code — ver SDD-DTF-0020 (RF03).

O stdout de PostToolUse vai para o log de debug; só exit 2 mostra o
stderr ao modelo. Por isso este hook valida SÓ o arquivo editado e, havendo
problema de gate, escreve em stderr e sai 2.

    0  sem problema, fora do escopo (não .md, sem front-matter, tipo fora
       do framework) ou payload inválido — sem saída
    2  documento do framework viola gate — problemas em stderr
    1  exceção interna — não bloqueante, visível ao usuário e não ao modelo

Nunca imprime warnings nem valida registry: o registry costuma ser
atualizado num passo seguinte da mesma tarefa (pre-commit e CI cobrem).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_doc  # noqa: E402
import validate_state  # noqa: E402
from framework_lib import load_rules, read_frontmatter  # noqa: E402


def framework_types() -> set[str]:
    """document_types + legacy_document_types de workflow-rules.yaml."""
    rules = load_rules()
    return set(rules.get("document_types") or {}) | set(rules.get("legacy_document_types") or {})


def problems_for(path: Path) -> list[str]:
    try:
        fm, _ = read_frontmatter(path)
    except ValueError:
        return []
    if fm.get("type") not in framework_types():
        return []
    problems, _warnings = validate_doc.check_document(path)
    if fm.get("type") == "SDD":
        sdd_problems, _sdd_warnings = validate_state.check_sdd(path)
        problems = problems + sdd_problems
    return list(problems)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0
    tool_input = payload.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(file_path, str) or not file_path:
        return 0
    path = Path(file_path)
    if not path.is_absolute() and isinstance(payload.get("cwd"), str):
        path = Path(payload["cwd"]) / path
    if path.suffix != ".md" or not path.is_file():
        return 0

    try:
        problems = problems_for(path)
    except Exception as exc:  # noqa: BLE001 — falha do validador não pode bloquear a edição
        print(f"hook_post_edit: erro interno — {exc}", file=sys.stderr)
        return 1

    if not problems:
        return 0
    lines = [f"framework: {path} viola gate(s) — corrija antes de seguir:"]
    lines += [f"  - {p}" for p in problems]
    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
