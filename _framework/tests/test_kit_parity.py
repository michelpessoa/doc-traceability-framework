"""Paridade entre as duas cópias do kit — ver SDD-DTF-0032 (RF10).

`render_prompts.py --check` já mecaniza isso para todo script em
`_framework/scripts/*.py` (sync_copies, byte a byte). Este teste dá um
sinal automatizado independente para o par específico exigido pela
SDD-DTF-0032, sem depender de rodar o CLI do render_prompts.py.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_ci_gate_verify_sdd_paridade():
    original = REPO_ROOT / "_framework" / "scripts" / "ci_gate_verify_sdd.py"
    bundled = REPO_ROOT / "_framework" / "skills" / "doc-traceability-framework" / "scripts" / "ci_gate_verify_sdd.py"
    assert original.is_file()
    assert bundled.is_file()
    assert original.read_bytes() == bundled.read_bytes()
