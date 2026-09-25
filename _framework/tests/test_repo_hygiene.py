"""Higiene de repositório: caches fora da busca e do versionamento (SDD-DTF-0045, RF01-RF03, RF08)."""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIRS: tuple[str, ...] = (".ruff_cache", ".pytest_cache", ".mypy_cache", "__pycache__")


def _linhas(texto: str) -> set[str]:
    return {linha.strip() for linha in texto.splitlines()}


def _faltantes(texto: str) -> list[str]:
    linhas = _linhas(texto)
    return [f"{d}/" for d in CACHE_DIRS if f"{d}/" not in linhas]


def test_gitignore_cobre_caches() -> None:
    faltam = _faltantes((REPO_ROOT / ".gitignore").read_text(encoding="utf-8"))
    assert not faltam, f".gitignore sem padrão(ões): {faltam}"


def test_ignore_cobre_caches() -> None:
    caminho = REPO_ROOT / ".ignore"
    assert caminho.is_file(), ".ignore não existe"
    faltam = _faltantes(caminho.read_text(encoding="utf-8"))
    assert not faltam, f".ignore sem padrão(ões): {faltam}"


def test_nenhum_cache_rastreado() -> None:
    saida = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout
    ofensores = [p for p in saida.splitlines() if any(d in p.split("/") for d in CACHE_DIRS)]
    assert not ofensores, f"cache rastreado: {ofensores}"


@pytest.mark.parametrize("removido", [f"{d}/" for d in CACHE_DIRS])
def test_sensor_mutacao_detecta_padrao_removido(removido: str, tmp_path: Path) -> None:
    """Sensor de discriminação (RF01): sem um padrão, a checagem tem que falhar."""
    original = "\n".join(f"{d}/" for d in CACHE_DIRS)
    mutado = "\n".join(linha for linha in original.splitlines() if linha.strip() != removido)
    arquivo = tmp_path / ".gitignore"
    arquivo.write_text(mutado, encoding="utf-8")
    assert _faltantes(arquivo.read_text(encoding="utf-8")) == [removido]
