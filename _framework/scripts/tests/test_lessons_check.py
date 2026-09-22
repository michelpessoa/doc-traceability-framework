"""Testes de lessons_check.py — ver SDD-DTF-0038 (SPEC-DTF-0015)."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lessons_check import extract_entries, find_candidates  # noqa: E402

KIT_ROOT = Path(__file__).resolve().parents[3]


def _lessons(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


LESSON_COM_SLUG = """\
# LESSONS.md

## 2026-09-04 — Título A

**O que falhou:** algo.

**Chave de recorrência:** verificador-mesma-sessao

**Escopo desta lição:** um projeto.
"""

LESSON_SEM_SLUG = """\
# LESSONS.md

## 2026-09-05 — Título B

**O que falhou:** outra coisa, sem o campo novo.
"""

LESSON_CONFIRMADA = """\
# LESSONS.md

## 2026-09-06 — Título C

**Chave de recorrência:** verificador-mesma-sessao

**Status da lição:** confirmada
"""

LESSON_SLUG_DUPLICADO_MESMO_ARQUIVO = """\
# LESSONS.md

## 2026-09-04 — Título A

**Chave de recorrência:** dup-slug

## 2026-09-05 — Título A2

**Chave de recorrência:** dup-slug
"""


def test_extract_entries_ignora_entrada_sem_chave_de_recorrencia(tmp_path):
    path = _lessons(tmp_path, "LESSONS.md", LESSON_SEM_SLUG)
    assert extract_entries(path) == []


def test_extract_entries_extrai_entrada_com_chave(tmp_path):
    path = _lessons(tmp_path, "LESSONS.md", LESSON_COM_SLUG)
    entries = extract_entries(path)
    assert len(entries) == 1
    assert entries[0]["date"] == "2026-09-04"
    assert entries[0]["title"] == "Título A"
    assert entries[0]["slug"] == "verificador-mesma-sessao"
    assert entries[0]["confirmed"] is False
    assert entries[0]["file"] == str(path)


def test_extract_entries_arquivo_inexistente_levanta_systemexit(tmp_path):
    try:
        extract_entries(tmp_path / "nao_existe.md")
        assert False, "deveria ter levantado SystemExit"
    except SystemExit as exc:
        assert "nao_existe.md" in str(exc)


def test_extract_entries_marca_confirmada(tmp_path):
    path = _lessons(tmp_path, "LESSONS.md", LESSON_CONFIRMADA)
    entries = extract_entries(path)
    assert entries[0]["confirmed"] is True


def test_find_candidates_slug_em_dois_arquivos_e_candidata(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_COM_SLUG)
    b = _lessons(tmp_path, "b_LESSONS.md", LESSON_COM_SLUG)
    entries_by_file = {a: extract_entries(a), b: extract_entries(b)}
    candidates = find_candidates(entries_by_file)
    assert "verificador-mesma-sessao" in candidates
    assert len(candidates["verificador-mesma-sessao"]) == 2


def test_find_candidates_slug_em_um_arquivo_so_nao_e_candidata(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_COM_SLUG)
    entries_by_file = {a: extract_entries(a)}
    assert find_candidates(entries_by_file) == {}


def test_find_candidates_duas_ocorrencias_mesmo_arquivo_nao_conta(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_SLUG_DUPLICADO_MESMO_ARQUIVO)
    entries_by_file = {a: extract_entries(a)}
    assert find_candidates(entries_by_file) == {}


def test_find_candidates_exclui_confirmada(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_CONFIRMADA)
    b = _lessons(tmp_path, "b_LESSONS.md", LESSON_COM_SLUG)
    entries_by_file = {a: extract_entries(a), b: extract_entries(b)}
    assert find_candidates(entries_by_file) == {}


def test_cli_menos_de_dois_paths_retorna_1(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_COM_SLUG)
    result = subprocess.run(
        [sys.executable, str(KIT_ROOT / "_framework/scripts/lessons_check.py"), str(a)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_cli_reporta_candidata(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_COM_SLUG)
    b = _lessons(tmp_path, "b_LESSONS.md", LESSON_COM_SLUG)
    result = subprocess.run(
        [sys.executable, str(KIT_ROOT / "_framework/scripts/lessons_check.py"), str(a), str(b)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "verificador-mesma-sessao" in result.stdout


def test_cli_sem_candidata_relata_zero(tmp_path):
    a = _lessons(tmp_path, "a_LESSONS.md", LESSON_SEM_SLUG)
    b = _lessons(tmp_path, "b_LESSONS.md", LESSON_SEM_SLUG)
    result = subprocess.run(
        [sys.executable, str(KIT_ROOT / "_framework/scripts/lessons_check.py"), str(a), str(b)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Nenhuma candidata" in result.stdout
