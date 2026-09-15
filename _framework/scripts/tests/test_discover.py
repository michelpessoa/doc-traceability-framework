"""Testes de framework_check.discover — ver SDD-DTF-0023, SDD-DTF-0025."""

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
    # SDD-DTF-0025: discriminam duas mutações que a fixture acima não pega.
    "docs/worktrees/registry_dir",  # "worktrees" fora de .claude/, não é o padrão podado
    ".git/x",  # dentro de .git, sempre podado
]


def test_discover_poda_node_modules_framework_e_worktrees(tmp_path):
    for rel in REGISTRY_DIRS:
        d = tmp_path / rel
        d.mkdir(parents=True)
        (d / "registry.yaml").write_text("documents: []\n", encoding="utf-8")

    found = [p.relative_to(tmp_path).as_posix() for p in discover(tmp_path)]

    assert found == [
        "docs/EVM",
        "docs/node_modules_notes",
        "docs/sdd",
        "docs/worktrees/registry_dir",
    ]


def test_discover_poda_worktrees_so_relativo_a_root(tmp_path):
    """RF4 (SDD-DTF-0023): só `root/.claude/worktrees` é podado por nome.

    Um diretório chamado `worktrees` em outro nível da árvore (aqui,
    `docs/worktrees/`) não é o padrão de cópia de sub-agent e deve ser
    descoberto normalmente. Mutação que pegaria (não pega hoje sem este
    teste): podar qualquer diretório chamado `worktrees`, em qualquer
    nível — a fixture original nunca cria um `worktrees` fora de
    `.claude/`, então essa mutação sobrevivia.
    """
    d = tmp_path / "docs" / "worktrees" / "registry_dir"
    d.mkdir(parents=True)
    (d / "registry.yaml").write_text("documents: []\n", encoding="utf-8")

    found = [p.relative_to(tmp_path).as_posix() for p in discover(tmp_path)]

    assert found == ["docs/worktrees/registry_dir"]


def test_discover_nunca_desce_em_git(tmp_path):
    """RF4 (SDD-DTF-0023): `.git/` nunca é descoberto, mesmo com registry.yaml
    dentro. Mutação que pegaria (não pega hoje sem este teste): tirar
    `.git` de `PRUNED_DIR_NAMES` — a fixture original nunca coloca um
    `registry.yaml` dentro de `.git/`, então essa mutação sobrevivia.
    """
    d = tmp_path / ".git" / "x"
    d.mkdir(parents=True)
    (d / "registry.yaml").write_text("documents: []\n", encoding="utf-8")

    found = [p.relative_to(tmp_path).as_posix() for p in discover(tmp_path)]

    assert found == []
