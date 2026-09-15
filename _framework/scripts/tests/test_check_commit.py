"""Testes de check_commit.py — ver SDD-DTF-0021 (RF08).

Monta um repositório git temporário em tmp_path e roda o script por
subprocess dentro dele: merge real (mais de um pai, ou MERGE_HEAD
presente no modo commit-msg) é pulado independente do assunto; commit
comum fora do formato continua reprovando.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "check_commit.py"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Teste",
    "GIT_AUTHOR_EMAIL": "teste@example.com",
    "GIT_COMMITTER_NAME": "Teste",
    "GIT_COMMITTER_EMAIL": "teste@example.com",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, env=GIT_ENV, capture_output=True, text=True, check=True
    ).stdout.strip()


def commit_file(repo: Path, name: str, message: str) -> None:
    (repo / name).write_text(name, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", message)


def run_check(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=repo, env=GIT_ENV, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "develop")
    commit_file(tmp_path, "base.txt", "chore: base")
    return tmp_path


def prepare_branch(repo: Path) -> None:
    """Branch verify/x com um commit válido e develop avançado, para o
    merge ser de fato um commit com dois pais."""
    git(repo, "checkout", "-q", "-b", "verify/x")
    commit_file(repo, "x.txt", "docs: verifica x")
    git(repo, "checkout", "-q", "develop")
    commit_file(repo, "y.txt", "docs: avança develop")


def test_range_pula_merge_local_com_assunto_minusculo(repo):
    base = git(repo, "rev-parse", "HEAD")
    prepare_branch(repo)
    git(repo, "merge", "--no-ff", "-q", "-m", "merge verify/x into develop", "verify/x")
    assert len(git(repo, "log", "-1", "--pretty=%P").split()) == 2

    result = run_check(repo, "--range", f"{base}..HEAD")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "merge verify/x" not in result.stdout


def test_range_reprova_commit_comum_fora_do_formato(repo):
    base = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "z.txt", "merge verify/x into develop")

    result = run_check(repo, "--range", f"{base}..HEAD")
    assert result.returncode == 1
    assert "fora de Conventional Commits" in result.stdout + result.stderr


def test_arquivo_com_merge_head_pula_checagem(repo):
    prepare_branch(repo)
    git(repo, "merge", "--no-ff", "--no-commit", "-q", "verify/x")
    assert Path(repo / git(repo, "rev-parse", "--git-path", "MERGE_HEAD")).is_file()

    msg = repo / "COMMIT_EDITMSG_TESTE"
    msg.write_text("merge verify/x into develop\n", encoding="utf-8")
    result = run_check(repo, str(msg))
    assert result.returncode == 0, result.stdout + result.stderr


def test_arquivo_sem_merge_head_reprova_fora_do_formato(repo):
    msg = repo / "COMMIT_EDITMSG_TESTE"
    msg.write_text("merge verify/x into develop\n", encoding="utf-8")
    result = run_check(repo, str(msg))
    assert result.returncode == 1
    assert "fora de Conventional Commits" in result.stdout + result.stderr
