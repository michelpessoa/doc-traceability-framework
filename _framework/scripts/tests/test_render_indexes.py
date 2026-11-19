"""Testes de render_indexes.extract_sdd_files — SDD-DTF-0057 (SPEC-DTF-0031, RF07)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from render_indexes import extract_sdd_files  # noqa: E402

ENXUTA = """
## Requisitos consolidados

| RF-ID | Origem | Requisito (resumo) | Arquivos |
|---|---|---|---|
| RF01 | SPEC-X-0001 | Listar | `app/lista.py`, `tests/test_lista.py` |
| RF02 | SPEC-X-0001 | Apagar | `app/apagar.py` |

## Decomposição em tasks

| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |
|---|---|---|---|---|
| 1 | Fazer | RF01 | `app/lista.py` | |
"""


def test_extract_sdd_files_le_a_coluna_arquivos_dos_requisitos():
    assert extract_sdd_files(ENXUTA) == ["app/apagar.py", "app/lista.py", "tests/test_lista.py"]


def test_extract_sdd_files_sem_coluna_arquivos_nos_requisitos_nao_muda():
    body = "## Requisitos consolidados\n\n| RF | Requisito |\n|---|---|\n| RF01 | Ler `x/y.py` |\n"
    assert extract_sdd_files(body) == []
