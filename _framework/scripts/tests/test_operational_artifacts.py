"""Testes de artefatos operacionais por padrão glob — ver SDD-DTF-0023.

Usa o workflow-rules.yaml real, que declara `validation-*.md` em
operational_artifacts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework_lib import (  # noqa: E402
    _FALLBACK_OPERATIONAL_ARTIFACTS,
    is_operational_artifact,
    iter_documents,
)

FILES = [
    "SDD-X-0001.md",
    "LESSONS.md",
    "HANDOFF.md",
    "validation.md",
    "validation-X-0001.md",
    "Validation-X-0002.md",
    "registry.md",
    "templates/t.md",
]


def test_iter_documents_pula_artefatos_operacionais(tmp_path):
    (tmp_path / "registry.yaml").write_text("documents: []\n", encoding="utf-8")
    for name in FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# x\n", encoding="utf-8")

    names = [p.name for p in iter_documents(tmp_path)]

    assert names == ["SDD-X-0001.md", "Validation-X-0002.md"]


def test_is_operational_artifact_glob_sensivel_a_maiusculas():
    assert is_operational_artifact("validation-X-0001.md") is True
    assert is_operational_artifact("SDD-X-0001.md") is False
    assert is_operational_artifact("Validation-X-0002.md") is False


def test_fallback_inclui_validation_por_sdd():
    assert "validation-*.md" in _FALLBACK_OPERATIONAL_ARTIFACTS
