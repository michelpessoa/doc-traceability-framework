"""Testes de .gitattributes do bundle gerado — SDD-DTF-0046 (RF01, RF02)."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = "_framework/skills/doc-traceability-framework"
LINHAS = [
    f"{BUNDLE}/scripts/*.py linguist-generated=true",
    f"{BUNDLE}/references/workflow-rules.yaml linguist-generated=true",
    f"{BUNDLE}/templates/*.md linguist-generated=true",
]


def _ativas() -> list[str]:
    texto = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    return [
        ln.strip()
        for ln in texto.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]


def test_gitattributes_declara_copias_geradas() -> None:
    ativas = _ativas()
    for linha in LINHAS:
        assert linha in ativas, f"linha ausente em .gitattributes: {linha}"
    assert len(ativas) == 3, f"esperadas exatamente 3 linhas ativas: {ativas}"


def test_gitattributes_sem_diff_nem_merge() -> None:
    for linha in _ativas():
        for token in linha.split()[1:]:
            nome = token.split("=")[0].lstrip("-!")
            assert nome not in ("diff", "merge"), f"token proibido {token!r} em {linha!r}"


def _attrs(paths: list[str]) -> dict[str, dict[str, str]]:
    out = subprocess.run(
        ["git", "check-attr", "linguist-generated", "diff", "merge", "--", *paths],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    res: dict[str, dict[str, str]] = {}
    for ln in out.splitlines():
        path, attr, val = ln.rsplit(": ", 2)
        res.setdefault(path, {})[attr] = val
    return res


def test_git_check_attr_gerados_e_manuais() -> None:
    if shutil.which("git") is None:
        pytest.skip("git ausente")
    probe = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if probe.returncode != 0:
        pytest.skip("não é árvore de trabalho Git")
    gerados = [f"{BUNDLE}/scripts/{p.name}" for p in (ROOT / "_framework/scripts").glob("*.py")]
    gerados.append(f"{BUNDLE}/references/workflow-rules.yaml")
    gerados += [f"{BUNDLE}/templates/{p.name}" for p in (ROOT / "_framework/templates").glob("*.md")]
    for path, attrs in _attrs(sorted(gerados)).items():
        assert attrs == {"linguist-generated": "true", "diff": "unspecified", "merge": "unspecified"}, path
    manuais = [f"{BUNDLE}/SKILL.md"] + [
        f"{BUNDLE}/prompts/{p.name}" for p in (ROOT / BUNDLE / "prompts").glob("*.md")
    ]
    for path, attrs in _attrs(sorted(manuais)).items():
        assert attrs["linguist-generated"] == "unspecified", path
