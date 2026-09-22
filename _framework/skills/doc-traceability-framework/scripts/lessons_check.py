#!/usr/bin/env python3
"""
lessons_check.py

Mecaniza a contagem de recorrência do critério "2 projetos" da
`lessons_policy` (workflow-rules.yaml, seção 18): extrai de cada
`LESSONS.md` as entradas que declaram `**Chave de recorrência:** <slug>`
(campo novo, opcional, retrocompatível) e reporta como candidata a
promoção todo slug que aparecer em entradas de 2+ arquivos distintos.
Entrada com `**Status da lição:** confirmada` já foi promovida e não
entra na contagem (SDD-DTF-0038, RF05-RF07).

Uso:
    python3 lessons_check.py <LESSONS.md...>   # 2 ou mais paths
"""

import re
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+(\S+)\s+—\s+(.+?)\s*$", re.MULTILINE)
RECORRENCIA = re.compile(r"\*\*Chave de recorrência:\*\*\s*(\S+)")
STATUS_CONFIRMADA = re.compile(r"\*\*Status da lição:\*\*\s*confirmada", re.IGNORECASE)


def extract_entries(path: Path) -> list[dict]:
    """Cada entrada `## <data> — <título>` do arquivo que tiver
    `**Chave de recorrência:** <slug>` no corpo vira
    {date, title, slug, confirmed, file}. Entrada sem o campo é
    ignorada, não é erro (RF05)."""
    if not path.is_file():
        raise SystemExit(f"Não encontrado: {path}")

    text = path.read_text(encoding="utf-8")
    headings = list(HEADING.finditer(text))
    entries = []
    for i, m in enumerate(headings):
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body = text[start:end]

        slug_match = RECORRENCIA.search(body)
        if not slug_match:
            continue

        entries.append(
            {
                "date": m.group(1),
                "title": m.group(2),
                "slug": slug_match.group(1),
                "confirmed": bool(STATUS_CONFIRMADA.search(body)),
                "file": str(path),
            }
        )
    return entries


def find_candidates(entries_by_file: dict[Path, list[dict]]) -> dict[str, list[dict]]:
    """Agrupa entradas não confirmadas por slug (RF07), reporta só os
    slugs com ocorrência em 2+ arquivos distintos (RF06)."""
    by_slug: dict[str, list[dict]] = {}
    for entries in entries_by_file.values():
        for entry in entries:
            if entry["confirmed"]:
                continue
            by_slug.setdefault(entry["slug"], []).append(entry)

    return {
        slug: occurrences for slug, occurrences in by_slug.items() if len({occ["file"] for occ in occurrences}) >= 2
    }


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if len(paths) < 2:
        print(__doc__)
        return 1

    entries_by_file = {path: extract_entries(path) for path in paths}
    candidates = find_candidates(entries_by_file)

    if not candidates:
        print("✅ Nenhuma candidata a promoção (nenhum slug recorre em 2+ arquivos).")
        return 0

    print(f"🔎 {len(candidates)} candidata(s) a promoção:")
    for slug, occurrences in candidates.items():
        print(f"  - {slug}:")
        for occ in occurrences:
            print(f"      {occ['date']} — {occ['file']} — {occ['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
