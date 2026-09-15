"""Testes de guard_bash.sh — ver SDD-DTF-0021 (RF07).

Roda o script gerado por subprocess com o payload que o Claude Code envia
em PreToolUse (matcher Bash) e confere o exit: 0 deixa passar, 2 bloqueia.
Cada comando é avaliado por subcomando, com padrões ancorados no início
do segmento e `git -C <caminho>` normalizado para `git`.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "guard_bash.sh"

CASES = [
    ("git push -u origin feat/x && gh pr create --base main", 0),
    ("git push origin main", 2),
    ("git -C /repo push origin main", 2),
    ("git push --force origin feat/x", 2),
    ('gh pr create --body "bloqueia push direto em main"', 0),
    ("cd /x && git reset --hard origin/main", 2),
    ("echo ok; rm -rf /", 2),
    ("git status", 0),
    ("git push origin HEAD:main", 2),
    ("git push -f", 2),
    ("git push origin feature/maintenance", 0),
    ("git push -u origin docs/sdd-dtf-0018-validate-state-data", 0),
    ('git commit -m "fix: evita push em main"', 0),
    ('git commit -m "evita push em main agora"', 0),
    ('git -C /repo commit -m "x push main y"', 0),
    ("git -C /repo reset --hard HEAD", 2),
    ("git -C /repo push -f origin feat/x", 2),
]


def run_guard(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT)], input=stdin, capture_output=True, text=True)


@pytest.mark.parametrize(("command", "expected"), CASES)
def test_guard_bash_por_segmento(command, expected):
    result = run_guard(json.dumps({"tool_input": {"command": command}}))
    assert result.returncode == expected, result.stderr
    if expected == 2:
        assert "guard_bash: bloqueado" in result.stderr


def test_guard_bash_stdin_invalido_falha_aberta():
    result = run_guard("isto não é json")
    assert result.returncode == 0
    assert result.stdout == ""
