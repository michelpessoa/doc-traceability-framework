#!/usr/bin/env python3
"""
check_source_docs.py

Mecaniza o item 1 do passo "0. Fidelidade à origem" do `verify-sdd`
(RFC-DTF-0007/ADR-DTF-0007/SPEC-DTF-0014): cada entrada de `source_docs`
de uma SDD — id + url apontando pro repositório central — precisa
existir de fato, estar num status utilizável e apontar pro arquivo
certo. Sem isso, todo o resto da verificação confere a SDD contra uma
origem errada sem saber.

Uso:
    python3 check_source_docs.py <SDD.md> <central_docs_dir>

Exit 1 se houver problema; --report-only sempre sai 0.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import load_registry, read_frontmatter, report  # noqa: E402
from registry_tools import check_source_docs_urls, resolve_doc_path  # noqa: E402

OK_STATUSES = {"approved", "implemented"}


def check_sdd_source_docs(sdd_path: Path, central_docs_dir: Path) -> list[str]:
    fm, _ = read_frontmatter(sdd_path)
    doc_id = fm.get("id") or sdd_path.name
    source_docs = fm.get("source_docs") or []

    # RF03: SDD sem origem declarada (sizing `small`) não tem fidelidade a
    # verificar — lista vazia não é lacuna, é o registro de que a fase de
    # SPEC/ADR foi legitimamente pulada.
    if not source_docs:
        return []

    # Entrada sem `id`/`url` (ou url não resolvível) já é problema aqui —
    # reaproveita check_source_docs_urls (registry_tools.py) em vez de
    # duplicar a mesma checagem. Só entradas com id (mesmo que a url tenha
    # sido reportada como problema por check_source_docs_urls) seguem para
    # a checagem de existência/status/url abaixo.
    problems = check_source_docs_urls(doc_id, fm)

    _, central_docs = load_registry(central_docs_dir)

    for sd in source_docs:
        if not isinstance(sd, dict) or not sd.get("id"):
            continue  # já reportado acima
        sid, url = sd["id"], sd.get("url")

        entry = central_docs.get(sid)
        if entry is None:
            problems.append(f"{doc_id}: source_docs '{sid}' não encontrado no registry central ({central_docs_dir}).")
            continue

        status = entry.get("status")
        if status not in OK_STATUSES:
            problems.append(
                f"{doc_id}: source_docs '{sid}' está com status '{status}' — "
                f"esperado {' ou '.join(sorted(OK_STATUSES))}."
            )

        if not url:
            continue  # já reportado por check_source_docs_urls

        rel_path = entry.get("path")
        resolved = resolve_doc_path(central_docs_dir, rel_path) if rel_path else None
        if resolved is None:
            problems.append(
                f"{doc_id}: source_docs '{sid}' tem `path` de registry ('{rel_path}') "
                "que não resolve a nenhum arquivo real."
            )
        elif not str(url).endswith(str(rel_path)):
            problems.append(
                f"{doc_id}: source_docs '{sid}' tem url ('{url}') que não aponta pro "
                f"mesmo arquivo que o `path` do registry central ('{rel_path}')."
            )

    return problems


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    report_only = "--report-only" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 1

    sdd_path, central_docs_dir = Path(args[0]), Path(args[1])
    problems = check_sdd_source_docs(sdd_path, central_docs_dir)
    return report(
        problems,
        [],
        f"✅ source_docs de {sdd_path.name} conferem com o registry central.",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
