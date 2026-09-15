"""Testes de hook_session_start.py — ver SDD-DTF-0020 (RF01, RF02).

Roda o script por subprocess, como o Claude Code roda o hook, com um
repositório mínimo em tmp_path e CLAUDE_PROJECT_DIR apontando para ele.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "hook_session_start.py"


def _run(root: Path, mode: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    if stdin is None:
        stdin = json.dumps({"hook_event_name": "SessionStart", "cwd": str(root)})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}
    return subprocess.run(
        [sys.executable, str(SCRIPT), mode],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        cwd=root,
        check=False,
    )


def test_handoff_na_raiz(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("x")
    result = _run(tmp_path, "pickup")
    assert result.returncode == 0
    assert "HANDOFF.md encontrado em: HANDOFF.md." in result.stdout
    assert "skill pickup" in result.stdout


def test_handoff_so_em_docs(tmp_path):
    (tmp_path / "docs/EVM").mkdir(parents=True)
    (tmp_path / "docs/EVM/HANDOFF.md").write_text("x")
    result = _run(tmp_path, "pickup")
    assert result.returncode == 0
    assert "HANDOFF.md encontrado em: docs/EVM/HANDOFF.md." in result.stdout


def test_handoff_raiz_e_docs_raiz_primeiro(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("x")
    (tmp_path / "docs/EVM").mkdir(parents=True)
    (tmp_path / "docs/EVM/HANDOFF.md").write_text("x")
    result = _run(tmp_path, "pickup")
    assert result.returncode == 0
    assert "HANDOFF.md encontrado em: HANDOFF.md, docs/EVM/HANDOFF.md." in result.stdout


def test_sem_handoff_nao_imprime(tmp_path):
    result = _run(tmp_path, "pickup")
    assert result.returncode == 0
    assert result.stdout == ""


def test_post_compact_imprime_handover(tmp_path):
    result = _run(tmp_path, "post-compact")
    assert result.returncode == 0
    assert "skill handover" in result.stdout


def test_stdin_invalido_exit_0_sem_saida(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("x")
    result = _run(tmp_path, "pickup", stdin="não é json")
    assert result.returncode == 0
    assert result.stdout == ""


def test_modo_desconhecido_exit_0_sem_saida(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("x")
    result = _run(tmp_path, "bogus")
    assert result.returncode == 0
    assert result.stdout == ""


def test_sem_claude_project_dir_usa_cwd_do_payload(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("x")
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "pickup"],
        input=json.dumps({"cwd": str(tmp_path)}),
        capture_output=True,
        text=True,
        env=env,
        cwd=SCRIPT.parent,
        check=False,
    )
    assert result.returncode == 0
    assert "HANDOFF.md encontrado em: HANDOFF.md." in result.stdout
