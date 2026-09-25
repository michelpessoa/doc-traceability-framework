"""Testes de generate_registry_md.py — ver SDD-DTF-0043 (RF08)."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generate_registry_md as grm  # noqa: E402

REGISTRY = (
    'project: "X"\nframework_version: "1.5.0"\ndocuments:\n'
    '  - id: SDD-X-0001\n    type: SDD\n    title: "T"\n    status: approved\n'
    '    owner: "O"\n    updated: "2026-01-01"\n'
)


def _docs(tmp_path: Path) -> Path:
    (tmp_path / "registry.yaml").write_text(REGISTRY, encoding="utf-8")
    return tmp_path


def test_render_header_versao_sem_timestamp():
    header = grm.render_header("X", "2.3.1")
    assert "Framework v2.3.1" in header
    assert not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}", header)


def test_versao_corrente_quando_yaml_acessivel(tmp_path, monkeypatch):
    monkeypatch.setattr(grm, "current_framework_version", lambda: "9.9.9")
    assert "Framework v9.9.9" in grm.render_registry(grm.load_registry(_docs(tmp_path)))


def test_fallback_para_framework_version_do_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(grm, "find_rules_file", lambda *a, **k: None)
    text = grm.render_registry(grm.load_registry(_docs(tmp_path)))
    assert "Framework v1.5.0" in text and "N/D" not in text


def test_check_sai_1_se_divergir_e_0_se_em_dia(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(grm, "find_rules_file", lambda *a, **k: None)
    docs = _docs(tmp_path)
    assert grm.main([str(docs), "--check"]) == 1  # ausente
    assert grm.main([str(docs)]) == 0
    assert grm.main([str(docs), "--check"]) == 0
    assert grm.main([str(docs), "--check"]) == 0  # determinístico
    (docs / "registry.md").write_text("editado à mão\n", encoding="utf-8")
    assert grm.main([str(docs), "--check"]) == 1
    assert (docs / "registry.md").read_text(encoding="utf-8") == "editado à mão\n"  # --check não escreve
    assert "divergente" in capsys.readouterr().out
