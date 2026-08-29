#!/usr/bin/env python3
"""
framework_check.py

Entrada única dos validators do framework — o que o hook de pre-commit e o
CI chamam. Roda, para cada diretório de documentos informado:

    registry_tools.py validate   consistência registry ↔ front-matter
    validate_doc.py              gate_content_quality (seção 15)
    validate_state.py            gate_scope_verification (seção 16)

Uso:
    python3 framework_check.py <docs_dir> [<docs_dir> ...] [--report-only]
    python3 framework_check.py --auto [--report-only]

--auto descobre sozinho todo diretório que contenha um registry.yaml a
partir do diretório atual — é o modo usado pelo CI.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registry_tools  # noqa: E402
import validate_doc  # noqa: E402
import validate_state  # noqa: E402
from framework_lib import iter_documents  # noqa: E402


def discover(root: Path) -> list[Path]:
    """Todo diretório com registry.yaml, ignorando o que está sob _framework/."""
    found = []
    for path in sorted(root.rglob("registry.yaml")):
        if "_framework" in path.parts or ".git" in path.parts:
            continue
        found.append(path.parent)
    return found


def main() -> int:
    report_only = "--report-only" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if "--auto" in sys.argv or not args:
        dirs = discover(Path.cwd())
        if not dirs:
            print("Nenhum registry.yaml encontrado a partir de", Path.cwd())
            return 0
    else:
        dirs = [Path(a) for a in args]

    failures = 0
    for docs_dir in dirs:
        print(f"\n=== {docs_dir} ===")

        print("-- registry ↔ front-matter")
        failures += registry_tools.cmd_validate(docs_dir, report_only=report_only)

        paths = list(iter_documents(docs_dir))

        print("-- qualidade de conteúdo (seção 15)")
        problems, warnings = [], []
        for path in paths:
            p, w = validate_doc.check_document(path)
            problems += p
            warnings += w
        from framework_lib import report as emit
        failures += emit(
            problems, warnings,
            f"✅ {len(paths)} documento(s) ok.", report_only=report_only,
        )

        print("-- verificação de escopo (seção 16)")
        problems, warnings = [], []
        for path in paths:
            p, w = validate_state.check_sdd(path)
            problems += p
            warnings += w
        failures += emit(
            problems, warnings,
            f"✅ {len(paths)} documento(s) ok.", report_only=report_only,
        )

    print()
    if report_only:
        print(
            "Modo --report-only: o que foi listado acima não falha o build. "
            "Tire a flag quando os achados estiverem tratados."
        )
        return 0
    if failures:
        print(f"❌ {failures} verificação(ões) falharam.")
        return 1
    print("✅ Todas as verificações do framework passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
