#!/usr/bin/env python3
"""
validate_doc.py

Mecaniza o gate_content_quality (workflow-rules.yaml, seção 15). O gate
existia só como autorrevisão em prosa — uma IA checando a si mesma no
momento em que tem incentivo para não checar. Este script é o sinal
externo que faltava.

Uso:
    python3 validate_doc.py <arquivo.md | diretório> [...] [--report-only]

Checa, por documento:
  1. Front-matter completo (campos obrigatórios de frontmatter_schema).
  2. Nenhum placeholder banido ("TBD", "definir depois", ...).
  3. `NEEDS CLARIFICATION` pendente não passa de in_review.
  4. Seções obrigatórias do tipo presentes.
  5. PRD: todo requisito funcional tem RF-ID próprio.
  6. TS: a seção de contratos aponta arquivo/módulo ("onde"), não só prosa.

Exit 1 se houver problema; --report-only sempre sai 0.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import (  # noqa: E402
    INCIDENT_STATUSES,
    VALID_STATUSES,
    iter_documents,
    read_frontmatter,
    report,
)

# gate_content_quality item 4: termos que descrevem o que fazer sem mostrar
# como. A busca é literal e case-insensitive, igual ao "scan de placeholder"
# descrito no self_review_checklist.
BANNED_PLACEHOLDERS = [
    "tbd",
    "to be defined",
    "definir depois",
    "a definir",
    "ajustar conforme necessário",
    "conforme necessário",
    "seguir o padrão do projeto",
    "seguir padrão do projeto",
    "tratar erros apropriadamente",
    "tratamento de erro apropriado",
    "preencher depois",
    "detalhar depois",
]

NEEDS_CLARIFICATION = re.compile(r"NEEDS CLARIFICATION", re.IGNORECASE)

# Status a partir dos quais o documento é tratado como decidido — daí em
# diante placeholder e ambiguidade pendente deixam de ser tolerados.
DECIDED_STATUSES = {"approved", "implemented"}

REQUIRED_FRONTMATTER = ["id", "type", "title", "status", "project", "owner", "created", "updated"]

REQUIRED_SECTIONS = {
    "RFC": ["Contexto", "Problema", "Objetivos", "Alternativas", "Proposta", "Riscos"],
    "ADR": ["Contexto", "Decisão", "Consequências"],
    "PRD": ["Objetivo", "Requisitos funcionais", "Critérios de aceite"],
    "TS": ["Contratos técnicos"],
    "SDD": ["Requisitos consolidados", "Critérios de aceite"],
}

# Um RF-ID é o identificador próprio de um requisito funcional, exigido
# pelo item 1 do gate. "1." numerado não serve: não sobrevive a reordenação
# e não dá para referenciar de um critério de aceite.
RF_ID = re.compile(r"\bRF-\d+\b")

# "onde" de um contrato: caminho de arquivo com extensão, ou módulo com barra.
FILE_HINT = re.compile(r"[\w./-]+\.(?:ts|tsx|js|jsx|py|go|rs|java|kt|rb|sql|yaml|yml|json|prisma|mjs)\b")


def section_body(body: str, heading: str) -> str | None:
    """Retorna o texto de uma seção `## Heading` até o próximo heading de mesmo nível."""
    pattern = re.compile(
        rf"^#{{2,3}}\s*{re.escape(heading)}.*?$(.*?)(?=^#{{2,3}}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else None


def check_document(path: Path) -> tuple[list, list]:
    problems, warnings = [], []

    try:
        fm, body = read_frontmatter(path)
    except ValueError as exc:
        return [str(exc)], []

    if not fm:
        return [f"{path}: sem bloco de front-matter."], []

    doc_id = fm.get("id") or path.name
    doc_type = fm.get("type")
    status = fm.get("status")

    for field in REQUIRED_FRONTMATTER:
        if fm.get(field) in (None, ""):
            problems.append(f"{doc_id}: front-matter sem `{field}` (obrigatório).")

    allowed = INCIDENT_STATUSES if doc_type == "INC" else VALID_STATUSES
    if status and status not in allowed:
        problems.append(f"{doc_id}: status inválido '{status}'.")

    lowered = body.lower()
    for term in BANNED_PLACEHOLDERS:
        if term in lowered:
            line = next(
                (i for i, ln in enumerate(body.splitlines(), 1) if term in ln.lower()),
                None,
            )
            where = f" (linha {line})" if line else ""
            msg = f"{doc_id}: placeholder banido '{term}'{where} — gate_content_quality item 4."
            (problems if status in DECIDED_STATUSES else warnings).append(msg)

    if NEEDS_CLARIFICATION.search(body):
        msg = (
            f"{doc_id}: tem `NEEDS CLARIFICATION` pendente — "
            "gate_content_quality item 5 proíbe avançar para approved assim."
        )
        (problems if status in DECIDED_STATUSES else warnings).append(msg)

    for heading in REQUIRED_SECTIONS.get(doc_type, []):
        if section_body(body, heading) is None:
            problems.append(f"{doc_id}: seção obrigatória ausente: '{heading}'.")

    if doc_type == "PRD":
        reqs = section_body(body, "Requisitos funcionais")
        if reqs and not RF_ID.search(reqs):
            problems.append(
                f"{doc_id}: 'Requisitos funcionais' sem RF-ID próprio "
                "(gate_content_quality item 1) — lista numerada não é id."
            )

    if doc_type == "TS":
        contracts = section_body(body, "Contratos técnicos")
        if contracts and not FILE_HINT.search(contracts):
            warnings.append(
                f"{doc_id}: 'Contratos técnicos' não aponta nenhum arquivo/módulo "
                "('onde' do gate_content_quality item 2)."
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
        p, w = check_document(path)
        problems += p
        warnings += w

    return report(
        problems,
        warnings,
        f"✅ {len(paths)} documento(s) passaram no gate de qualidade de conteúdo.",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
