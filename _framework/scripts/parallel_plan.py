#!/usr/bin/env python3
"""
parallel_plan.py

Mecaniza o paralelismo derivado da SDD-DTF-0030: cruza a coluna "Arquivos
tocados" da seção "Decomposição em tasks" de uma ou mais SDDs (por
interseção de conjunto, com suporte a glob via `fnmatch`) e imprime quais
tasks são seguras de rodar em paralelo e quais pares estão bloqueados por
tocarem o mesmo arquivo. É sinal informativo: não é gate, não bloqueia
commit, não dispara execução sozinho.

Interseção de arquivo força bloqueio mesmo sem "Depende de" declarado —
ausência de dependência não é paralelismo automático quando há overlap
(RF04). Dependência declarada (`Depende de (#)`) também força bloqueio,
mesmo sem overlap de arquivo — é ordenação explícita do autor da SDD.

Uso:
    python3 parallel_plan.py <sdd1.md> [sdd2.md ...] [--json]
"""

from __future__ import annotations

import fnmatch
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import read_frontmatter, split_table_row  # noqa: E402

TASK_NUM = re.compile(r"^\d+$")
DECISAO_PURA = "(decisão pura)"


@dataclass
class TaskEntry:
    source: str
    label: str
    files: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    key: str = ""  # "{source}#{num}", estável — label carrega o título e não serve para comparar depends_on


@dataclass
class ParallelPlan:
    parallel_groups: list[list[str]]
    blocked_pairs: list[tuple[str, str, list[str]]]


def section_body(body: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^#{{2,3}}\s*{re.escape(heading)}.*?$(.*?)(?=^#{{2,3}}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else None


def parse_tasks(path: Path) -> tuple[list[TaskEntry], list[str]]:
    """
    Lê "Decomposição em tasks" de uma SDD. Retorna (entries, warnings).

    Linha com coluna de arquivos vazia (e diferente de `(decisão pura)`)
    gera warning e é excluída do cálculo (RF05) — não interrompe a leitura
    das demais linhas nem dos demais arquivos.
    """
    _, body = read_frontmatter(path)
    section = section_body(body, "Decomposição em tasks")
    source = path.name
    entries: list[TaskEntry] = []
    warnings: list[str] = []
    if not section:
        return entries, [f"{source}: sem seção 'Decomposição em tasks' — sem tasks declaradas."]

    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = split_table_row(line)
        if len(cells) < 5 or not TASK_NUM.match(cells[0]):
            continue
        num, task, files_cell, depends_cell = cells[0], cells[1], cells[3], cells[4]
        key = f"{source}#{num}"
        label = f"{key} {task}".strip()

        if not files_cell:
            warnings.append(f"{source}#{num}: coluna Arquivos vazia — excluída do cálculo.")
            continue

        if files_cell == DECISAO_PURA:
            files = []
        else:
            files = [f.strip() for f in files_cell.split(",") if f.strip()]

        depends_on = []
        for token in re.findall(r"\d+", depends_cell):
            depends_on.append(f"{source}#{token}")

        entries.append(TaskEntry(source=source, label=label, files=files, depends_on=depends_on, key=key))

    return entries, warnings


def files_overlap(a: list[str], b: list[str]) -> list[str]:
    """
    Arquivos de `a` e `b` que colidem — igualdade exata ou glob
    (`fnmatch`) casando em qualquer direção. Path inexistente no disco não
    é erro: o script nunca faz `stat`.
    """
    matches = []
    for fa in a:
        for fb in b:
            if fa == fb or fnmatch.fnmatch(fa, fb) or fnmatch.fnmatch(fb, fa):
                matches.append(fa if fa == fb else f"{fa} ~ {fb}")
    return matches


def derive_groups(entries: list[TaskEntry]) -> ParallelPlan:
    """
    Deriva grupos paralelizáveis (nenhum par do grupo colide em arquivo
    nem tem dependência declarada entre si) e pares bloqueados (colisão de
    arquivo, ou dependência declarada em qualquer direção, mesmo sem
    colisão de arquivo).
    """
    blocked_pairs: list[tuple[str, str, list[str]]] = []
    blocked_labels: dict[str, set[str]] = {e.label: set() for e in entries}

    for i, a in enumerate(entries):
        for b in entries[i + 1 :]:
            overlap = files_overlap(a.files, b.files)
            dependency = b.key in a.depends_on or a.key in b.depends_on
            if overlap or dependency:
                reason = overlap if overlap else ["depends_on"]
                blocked_pairs.append((a.label, b.label, reason))
                blocked_labels[a.label].add(b.label)
                blocked_labels[b.label].add(a.label)

    groups: list[list[str]] = []
    for entry in entries:
        placed = False
        for group in groups:
            if all(other not in blocked_labels[entry.label] for other in group):
                group.append(entry.label)
                placed = True
                break
        if not placed:
            groups.append([entry.label])

    return ParallelPlan(parallel_groups=groups, blocked_pairs=blocked_pairs)


def format_text(plan: ParallelPlan) -> str:
    lines = []
    lines.append(f"Grupos paralelizáveis ({len(plan.parallel_groups)}):")
    for i, group in enumerate(plan.parallel_groups, 1):
        lines.append(f"  {i}. " + ", ".join(group))
    lines.append(f"Pares bloqueados ({len(plan.blocked_pairs)}):")
    for a, b, files in plan.blocked_pairs:
        lines.append(f"  - {a} <-> {b} ({', '.join(files)})")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 1

    all_entries: list[TaskEntry] = []
    for path in paths:
        entries, warnings = parse_tasks(path)
        all_entries.extend(entries)
        for w in warnings:
            print(f"aviso: {w}", file=sys.stderr)

    plan = derive_groups(all_entries)

    if as_json:
        print(
            json.dumps(
                {
                    "parallel_groups": plan.parallel_groups,
                    "blocked_pairs": [{"a": a, "b": b, "files": f} for a, b, f in plan.blocked_pairs],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(format_text(plan))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
