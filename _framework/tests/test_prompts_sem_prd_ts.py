"""Regressão: prompts gerados sem PRD+TS nem TS-X como passo do fluxo — SDD-DTF-0050 (RF03).

Lê os três prompts gerados e reprova `PRD+TS`, `PRD + TS` e `TS-X`. Linha que
marca o tipo como legado (contém "legado") é isenta: é a âncora que o YAML
mantém para projeto sob 1.x (ex.: universal.md, gate da seção 5).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR: Path = REPO_ROOT / "_framework" / "prompts"
GERADOS: tuple = (
    PROMPTS_DIR / "universal.md",
    PROMPTS_DIR / "cursor" / "doc-framework.mdc",
    PROMPTS_DIR / "copilot" / "copilot-instructions.md",
)
PATTERN: re.Pattern = re.compile(r"PRD ?\+ ?TS|TS-X")
LEGACY_ANCHOR = "legado"


def ocorrencias(texto: str) -> list[tuple[int, str]]:
    """Devolve (número da linha, linha) de cada uso proibido fora de âncora de legado."""
    achados: list[tuple[int, str]] = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        if PATTERN.search(linha) and LEGACY_ANCHOR not in linha:
            achados.append((numero, linha))
    return achados


def test_gerados_sem_prd_ts() -> None:
    problemas: list[str] = []
    for caminho in GERADOS:
        for numero, linha in ocorrencias(caminho.read_text(encoding="utf-8")):
            problemas.append(f"{caminho.relative_to(REPO_ROOT)}:{numero}: {linha.strip()}")
    assert not problemas, "PRD+TS/TS-X nos prompts gerados:\n" + "\n".join(problemas)


def test_detector_pega_mutacao_em_memoria() -> None:
    texto = "linha limpa\n(sim: ADR → PRD+TS → SDD)\nids (SDD-X, TS-X)\nPRD + TS aqui\n"
    assert [n for n, _ in ocorrencias(texto)] == [2, 3, 4]
    assert ocorrencias("par PRD+TS, em projeto legado") == []
    assert ocorrencias("ADR → SPEC → SDD\n(SDD-X, SPEC-X, ADR-X)") == []
