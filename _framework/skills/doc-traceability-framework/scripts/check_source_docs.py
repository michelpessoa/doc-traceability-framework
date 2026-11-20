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

from framework_lib import (  # noqa: E402
    json_flag,
    load_registry,
    load_rules,
    project_version,
    read_frontmatter,
    report,
    rule_applies_since_date,
    run_main,
    split_table_row,
    usage_error,
)
from registry_tools import check_source_docs_urls, resolve_doc_path  # noqa: E402
from validate_doc import (  # noqa: E402
    RF_ID,
    RULE_SINCE,
    consolidated_rf_rows,
    first_table_lines,
    is_lean_sdd,
    section_body,
)

OK_STATUSES = {"approved", "implemented"}


# Na SDD enxuta (com source_docs, desde a 2.7.0) também confere os RF-IDs
# de "Requisitos consolidados" contra "Requisitos funcionais" de cada SPEC
# de origem, nas duas direções (SPEC-DTF-0031, RF05, SDD-DTF-0057). Fora
# da docstring, que é a saída de uso congelada desde a 2.3.2.


def _rf_key(rf: str) -> str:
    """`RF-01` e `RF01` são o mesmo RF."""
    return rf.replace("-", "")


def check_rf_fidelity(doc_id: str, rows: list[dict], spec_paths: dict[str, Path]) -> list[str]:
    """
    RF05 da SPEC-DTF-0031: para cada SPEC, os RF-IDs da tabela "Requisitos
    funcionais" contra os RFs da SDD com `Origem` igual ao id da SPEC.
    """
    problems = []
    for spec_id in sorted(spec_paths):
        _, body = read_frontmatter(spec_paths[spec_id])
        lines = first_table_lines(section_body(body, "Requisitos funcionais") or "")
        spec_rfs = set()
        for line in lines[2:]:
            found = RF_ID.search(split_table_row(line)[0])
            if found:
                spec_rfs.add(_rf_key(found.group(0)))
        sdd_rfs = {_rf_key(r["rf"]) for r in rows if r["rf"] and r["origem"] == spec_id}
        missing, extra = sorted(spec_rfs - sdd_rfs), sorted(sdd_rfs - spec_rfs)
        if missing or extra:
            problems.append(
                f"{doc_id}: RFs de {spec_id} fora da SDD: {', '.join(missing) or 'nenhum'}; "
                f"RFs da SDD fora de {spec_id}: {', '.join(extra) or 'nenhum'}."
            )
    return problems


def _lean(sdd_path: Path, fm: dict) -> bool:
    """SDD enxuta: criada desde a 2.7.0, em projeto sob 2.7.0 ou maior."""
    rules, version = load_rules(), project_version(sdd_path)

    def applies(rule: str) -> bool:
        since = RULE_SINCE[rule]
        return rule_applies_since_date(rules, since, fm.get("created"), version) and rule_applies_since_date(
            rules, since, None, version
        )

    return is_lean_sdd(fm, applies)


def check_sdd_source_docs(sdd_path: Path, central_docs_dir: Path) -> list[str]:
    fm, body = read_frontmatter(sdd_path)
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
    spec_paths: dict[str, Path] = {}

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
        elif entry.get("type") == "SPEC" and status in OK_STATUSES:
            spec_paths[sid] = resolved

    rows = consolidated_rf_rows(body)
    if rows is not None and spec_paths and _lean(sdd_path, fm):
        problems += check_rf_fidelity(doc_id, rows, spec_paths)
    return problems


def main() -> int:
    argv, as_json = json_flag(sys.argv[1:])
    args = [a for a in argv if not a.startswith("--")]
    report_only = "--report-only" in argv
    if len(args) != 2:
        return usage_error(__doc__, as_json, "check_source_docs.py")

    sdd_path, central_docs_dir = Path(args[0]), Path(args[1])
    problems = check_sdd_source_docs(sdd_path, central_docs_dir)
    return report(
        problems,
        [],
        f"✅ source_docs de {sdd_path.name} conferem com o registry central.",
        report_only=report_only,
        as_json=as_json,
        script="check_source_docs.py",
    )


if __name__ == "__main__":
    sys.exit(run_main(main, "check_source_docs.py", sys.argv[1:]))
