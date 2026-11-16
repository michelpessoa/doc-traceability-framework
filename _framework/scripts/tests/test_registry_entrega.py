"""`entrega` no registry e SDD em docs/sdd/arquivo/ — ver SDD-DTF-0053 (SPEC-DTF-0028, RF06)."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "registry_tools.py"

SDD = '---\nid: SDD-X-0001\ntype: SDD\ntitle: "s"\nstatus: implemented\n---\n\n# s\n'


def _registry(docs: Path, entrega: str, path: str = "SDD-X-0001.md") -> None:
    (docs / "registry.yaml").write_text(
        'project: "X"\nframework_version: "2.3.2"\ndocuments:\n  - id: SDD-X-0001\n    type: SDD\n    title: "s"\n'
        f'    status: implemented\n    path: "{path}"\n{entrega}',
        encoding="utf-8",
    )


def _rodar(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_trace_imprime_entrega(tmp_path):
    (tmp_path / "SDD-X-0001.md").write_text(SDD, encoding="utf-8")
    _registry(tmp_path, '    entrega: {pr: 42, data: "2026-11-16", resultado: "merge em develop"}\n')

    saida = _rodar("trace", str(tmp_path), "SDD-X-0001")

    assert saida.returncode == 0
    assert "entrega: PR #42, 2026-11-16, merge em develop" in saida.stdout


def test_trace_sem_entrega_nao_cita_entrega(tmp_path):
    (tmp_path / "SDD-X-0001.md").write_text(SDD, encoding="utf-8")
    _registry(tmp_path, "")

    saida = _rodar("trace", str(tmp_path), "SDD-X-0001")

    assert saida.returncode == 0
    assert "entrega" not in saida.stdout


def test_trace_entrega_incompleta_imprime_o_que_existe(tmp_path):
    (tmp_path / "SDD-X-0001.md").write_text(SDD, encoding="utf-8")
    _registry(tmp_path, "    entrega: {pr: 7}\n")

    saida = _rodar("trace", str(tmp_path), "SDD-X-0001")

    assert saida.returncode == 0
    assert "entrega: PR #7" in saida.stdout


def test_validate_aceita_sdd_arquivada_com_entrega(tmp_path):
    (tmp_path / "arquivo").mkdir()
    (tmp_path / "arquivo" / "SDD-X-0001.md").write_text(SDD, encoding="utf-8")
    _registry(tmp_path, '    entrega: {pr: 42, data: "2026-11-16"}\n', path="arquivo/SDD-X-0001.md")

    assert _rodar("validate", str(tmp_path)).returncode == 0
