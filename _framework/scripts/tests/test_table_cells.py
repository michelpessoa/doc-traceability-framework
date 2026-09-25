"""Testes de split_table_row — ver SDD-DTF-0047."""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework_lib import split_table_row  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
ESC = "\\|"


def _antigo(line: str) -> list[str]:
    return [c.strip() for c in line.strip("|").split("|")]


@pytest.mark.parametrize(
    "line",
    [
        "| a | b | c |",
        "|a|b|c|",
        "| 1 | `pytest -q` | exit 0 |",
        "||| x |||",
        "",
        "|---|---|---|",
        "| C:\\dir | b |",
        "| a | | c |",
    ],
)
def test_split_sem_pipe_escapado_igual_ao_antigo(line: str) -> None:
    assert split_table_row(line) == _antigo(line)


def test_pipe_escapado_fica_na_celula_e_desescapado() -> None:
    assert split_table_row(f"| 1 | a{ESC}b | c |") == ["1", "a|b", "c"]


def test_dois_pipes_escapados_uma_celula() -> None:
    assert split_table_row(f"| a{ESC}b{ESC}c | d |") == ["a|b|c", "d"]


def test_pipe_escapado_dentro_de_crases() -> None:
    assert split_table_row(f"| 1 | `grep -E 'a{ESC}b' f` | x |") == ["1", "`grep -E 'a|b' f`", "x"]


def test_pipe_escapado_antes_do_delimitador_final() -> None:
    assert split_table_row(f"| a | b{ESC}|") == ["a", "b|"]


def test_barra_sem_pipe_preservada() -> None:
    assert split_table_row("| C:\\dir | x |") == ["C:\\dir", "x"]


def test_nenhum_script_divide_linha_por_pipe_direto() -> None:
    pat = re.compile(r"""split\(\s*["']\|["']\s*\)""")
    achados = []
    for path in sorted(SCRIPTS_DIR.glob("*.py")):
        if path.name == "framework_lib.py":
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pat.search(line):
                achados.append(f"{path.name}:{n}")
    assert not achados, achados
