#!/usr/bin/env python3
"""
validate_state.py

Mecaniza o gate_scope_verification (workflow-rules.yaml, seção 16): uma SDD
só pode estar `implemented` se a evidência de verificação existir de fato.

O gate original pedia que a IA preenchesse uma tabela de evidência e
confirmasse escopo — e depois confiava nela para dizer que tinha feito. Este
script checa a única coisa que dá para checar de fora: a tabela existe, tem
linha para cada critério de aceite, cita comando e saída reais, e a
checklist de escopo está marcada.

Uso:
    python3 validate_state.py <SDD.md | diretório> [...] [--report-only]

Exit 1 se houver problema; --report-only sempre sai 0.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import iter_documents, read_frontmatter, report  # noqa: E402

# Frases que denunciam evidência de memória em vez de execução — o
# evidence_standard da seção 16 rejeita exatamente isto.
ASSUMED_EVIDENCE = [
    "deve passar",
    "deveria passar",
    "assumido",
    "presumo",
    "provavelmente passa",
    "não rodado",
    "n/a",
    "tbd",
]

CHECKBOX_UNCHECKED = re.compile(r"^\s*-\s*\[\s\]", re.MULTILINE)


def table_rows(section: str) -> list[list[str]]:
    """
    Extrai as linhas de dados de uma tabela markdown, descartando cabeçalho,
    separador e linhas vazias.
    """
    rows = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not any(cells):
            continue
        if all(set(c) <= set("-: ") for c in cells if c):
            continue  # separador
        rows.append(cells)
    return rows[1:] if rows else []  # descarta cabeçalho


def section_body(body: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^#{{2,3}}\s*{re.escape(heading)}.*?$(.*?)(?=^#{{2,3}}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else None


def check_sdd(path: Path) -> tuple[list, list]:
    problems, warnings = [], []

    try:
        fm, body = read_frontmatter(path)
    except ValueError as exc:
        return [str(exc)], []

    if not fm or fm.get("type") != "SDD":
        return [], []

    doc_id = fm.get("id") or path.name
    status = fm.get("status")

    criteria = section_body(body, "Critérios de aceite") or section_body(
        body, "Critérios de aceite / definição de pronto"
    )
    evidence = section_body(body, "Evidência de verificação")
    scope = section_body(body, "Verificação de escopo")

    n_criteria = len(table_rows(criteria)) if criteria else 0

    if status != "implemented":
        # Antes de `implemented` a evidência ainda pode estar vazia — o que
        # não pode é a SDD nem ter as seções que o gate vai exigir depois.
        if evidence is None:
            warnings.append(f"{doc_id}: sem seção 'Evidência de verificação' (será exigida em implemented).")
        if scope is None:
            warnings.append(f"{doc_id}: sem seção 'Verificação de escopo' (será exigida em implemented).")
        return problems, warnings

    # --- daqui para baixo: status == implemented, o gate vale integralmente ---

    if evidence is None:
        problems.append(
            f"{doc_id}: status `implemented` sem seção 'Evidência de verificação' "
            "— gate_scope_verification item 4."
        )
        return problems, warnings

    rows = table_rows(evidence)
    if not rows:
        problems.append(
            f"{doc_id}: 'Evidência de verificação' está vazia e o status é "
            "`implemented` — checklist de memória não satisfaz o gate."
        )
    elif n_criteria and len(rows) < n_criteria:
        problems.append(
            f"{doc_id}: {n_criteria} critério(s) de aceite mas só {len(rows)} "
            "linha(s) de evidência — cada critério precisa da sua."
        )

    for row in rows:
        joined = " | ".join(row).lower()
        for term in ASSUMED_EVIDENCE:
            if term in joined:
                problems.append(
                    f"{doc_id}: linha de evidência com resultado assumido "
                    f"('{term}') — evidence_standard exige comando rodado e saída real."
                )
                break
        if len(row) >= 2 and not row[1].strip():
            problems.append(f"{doc_id}: linha de evidência sem comando rodado.")

    if scope is None:
        problems.append(
            f"{doc_id}: status `implemented` sem seção 'Verificação de escopo' "
            "— gate_scope_verification itens 1-3."
        )
    elif CHECKBOX_UNCHECKED.search(scope):
        problems.append(
            f"{doc_id}: 'Verificação de escopo' tem item não marcado e o status "
            "é `implemented`."
        )

    return problems, warnings


def collect(targets) -> list[Path]:
    paths = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            paths.extend(iter_documents(p))
        elif p.is_file():
            paths.append(p)
        else:
            raise SystemExit(f"Não encontrado: {target}")
    return paths


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    report_only = "--report-only" in sys.argv
    if not args:
        print(__doc__)
        return 1

    paths = collect(args)
    problems, warnings = [], []
    for path in paths:
        p, w = check_sdd(path)
        problems += p
        warnings += w

    return report(
        problems,
        warnings,
        f"✅ {len(paths)} documento(s) verificados: nenhuma SDD `implemented` sem evidência.",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
