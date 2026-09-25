"""Testes do sync de templates e da cópia por bytes — SDD-DTF-0046 (RF04 a RF08)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from render_prompts import _sync_file, sync_copies  # noqa: E402

SKILL = "skills/doc-traceability-framework"


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "_framework"
    (root / "scripts").mkdir(parents=True)
    (root / "rules").mkdir()
    (root / "templates").mkdir()
    (root / SKILL).mkdir(parents=True)
    (root / "scripts" / "a.py").write_text("print(1)\n", encoding="utf-8")
    (root / "rules" / "workflow-rules.yaml").write_text("k: v\n", encoding="utf-8")
    (root / "templates" / "spec.template.md").write_text("# spec\n", encoding="utf-8")
    (root / "templates" / "prd.template.md").write_text("# prd\n", encoding="utf-8")
    return root


def test_sync_copies_gera_templates_md(tmp_path):
    root = _root(tmp_path)
    assert sync_copies(root, check=False) is True
    for name in ("spec.template.md", "prd.template.md"):
        assert (root / SKILL / "templates" / name).read_bytes() == (root / "templates" / name).read_bytes()


def test_sync_copies_check_detecta_template_divergente_ou_ausente(tmp_path):
    root = _root(tmp_path)
    assert sync_copies(root, check=False) is True
    assert sync_copies(root, check=True) is True
    twin = root / SKILL / "templates" / "spec.template.md"
    twin.write_text("editado\n", encoding="utf-8")
    assert sync_copies(root, check=True) is False
    twin.unlink()
    assert sync_copies(root, check=True) is False


def test_sync_copies_ignora_subpasta_ci(tmp_path):
    root = _root(tmp_path)
    (root / "templates" / "ci").mkdir()
    (root / "templates" / "ci" / "verify-sdd-gate.yml.example").write_text("x\n")
    sync_copies(root, check=False)
    assert not (root / SKILL / "templates" / "ci").exists()


def test_sync_copies_reprova_template_orfao_nos_dois_modos(tmp_path, capsys):
    root = _root(tmp_path)
    sync_copies(root, check=False)
    orfao = root / SKILL / "templates" / "orfao.md"
    orfao.write_text("x\n", encoding="utf-8")
    assert sync_copies(root, check=True) is False
    assert sync_copies(root, check=False) is False
    assert orfao.exists()
    assert "orfao.md" in capsys.readouterr().out


def test_sync_file_compara_bytes_crlf(tmp_path):
    src = tmp_path / "src.md"
    dest = tmp_path / "dest.md"
    src.write_bytes(b"a\nb\n")
    dest.write_bytes(b"a\r\nb\r\n")
    assert _sync_file(src, dest, check=True) is False
    assert _sync_file(src, dest, check=False) is True
    assert dest.read_bytes() == b"a\nb\n"


def test_sync_file_rejeita_symlink(tmp_path, capsys):
    src = tmp_path / "src.md"
    src.write_bytes(b"a\n")
    real = tmp_path / "real.md"
    real.write_bytes(b"a\n")
    dest = tmp_path / "dest.md"
    dest.symlink_to(real)
    for check in (True, False):
        assert _sync_file(src, dest, check=check) is False
    assert dest.is_symlink()
    assert "dest.md" in capsys.readouterr().out


def test_sync_copies_idempotente(tmp_path):
    root = _root(tmp_path)
    sync_copies(root, check=False)
    snap = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert sync_copies(root, check=False) is True
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == snap
