"""Testes de framework_check.discover — ver SDD-DTF-0023."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework_check import discover  # noqa: E402

REGISTRY_DIRS = [
    "docs/sdd",
    "docs/EVM",
    "node_modules/pkg/docs",
    "_framework/examples",
    ".claude/worktrees/a/docs/sdd",
    "docs/node_modules_notes",
]


def test_discover_poda_node_modules_framework_e_worktrees(tmp_path):
    for rel in REGISTRY_DIRS:
        d = tmp_path / rel
        d.mkdir(parents=True)
        (d / "registry.yaml").write_text("documents: []\n", encoding="utf-8")

    found = [p.relative_to(tmp_path).as_posix() for p in discover(tmp_path)]

    assert found == ["docs/EVM", "docs/node_modules_notes", "docs/sdd"]
