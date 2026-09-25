"""Regressão de texto PRD/Tech Spec/TS no YAML inteiro — SDD-DTF-0048 (RF11).

Lê o texto bruto (comentários incluídos, que `yaml.safe_load` descarta) e
reprova PRD, Tech Spec ou TS como passo do fluxo novo em qualquer seção não
isenta, salvo linhas com âncora explícita de legado ou de histórico.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH: Path = REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
PATTERN: re.Pattern = re.compile(r"PRD|Tech Spec|\bTS\b")  # igual ao LEGACY_PATTERN de test_gate_texto.py
BANNER: re.Pattern = re.compile(r"^# (\d+[a-z]?)\. ")
EXEMPT_SECTIONS: frozenset = frozenset({"0", "3b", "6", "8", "9", "19"})
REQUIRED_SECTIONS: frozenset = frozenset({"3", "12", "13", "14", "15", "17"})
SECTION_15_ANCHOR = "Em projeto legado (sob 1.x), PRD e Tech Spec ocupam o lugar da SPEC"
ALLOWED_FRAGMENTS: tuple = (
    "em projeto legado sob 1.x",
    "PRD e TS em projeto legado",
    "Documento único que substitui o par PRD + Tech Spec",
    'replaces: ["PRD", "TS"]',
    'parent_types: ["SPEC", "PRD", "TS", "ADR"]',
    "sob 1.x, o par PRD + Tech Spec ocupa o lugar da SPEC",
    "em projeto legado, PRD.status == approved AND TS.status == approved",
    "STRAT/RFC/ADR/PRD/TS neste framework",
    "PRD, Tech Spec e SDD só foram escritos DEPOIS",
    "Em projeto legado (sob 1.x), o par PRD + Tech Spec",
    "com PRD/TS/SDD já no lugar",
    "Em PRD legado (projeto sob 1.x)",
    SECTION_15_ANCHOR,
)


def _text() -> str:
    return RULES_PATH.read_text(encoding="utf-8")


def _banners(text: str) -> set:
    return {m.group(1) for line in text.splitlines() if (m := BANNER.match(line))}


def ocorrencias_proibidas(text: str) -> list:
    """(linha, seção, conteúdo) de cada linha fora de EXEMPT_SECTIONS que casa PATTERN
    e não contém nenhuma âncora de ALLOWED_FRAGMENTS."""
    found = []
    section = "0"
    for n, line in enumerate(text.splitlines(), start=1):
        m = BANNER.match(line)
        if m:
            section = m.group(1)
        if section in EXEMPT_SECTIONS:
            continue
        if PATTERN.search(line) and not any(a in line for a in ALLOWED_FRAGMENTS):
            found.append((n, section, line))
    return found


def resumo(text: str) -> tuple:
    """(nº de linhas, nº de ocorrências de PATTERN nessas linhas)."""
    occ = ocorrencias_proibidas(text)
    return len(occ), sum(len(PATTERN.findall(line)) for _, _, line in occ)


def test_yaml_sem_prd_ts_como_passo():
    occ = ocorrencias_proibidas(_text())
    assert occ == [], "PRD/Tech Spec/TS como passo fora das âncoras:\n" + "\n".join(
        f"  linha {n} (seção {s}): {c.strip()}" for n, s, c in occ
    )


def test_ancoras_de_legado_existem():
    text = _text()
    lines = text.splitlines()
    for anchor in ALLOWED_FRAGMENTS:
        assert any(anchor in line for line in lines), f"âncora ausente: {anchor!r}"
    n = sum(1 for line in lines if SECTION_15_ANCHOR in line)
    assert n == 1, f"âncora da seção 15 deve aparecer exatamente 1x, apareceu {n}x"


def test_secoes_isentas_e_escaneadas():
    # a seção "0" é o preâmbulo: não tem banner, é implícita antes do primeiro
    ausentes = sorted((EXEMPT_SECTIONS | REQUIRED_SECTIONS) - {"0"} - _banners(_text()))
    assert not ausentes, f"banners ausentes: {ausentes}"


def test_ocorrencias_proibidas_detecta_mutacao():
    assert ocorrencias_proibidas("# 14. T\nx PRD y\n") == [(2, "14", "x PRD y")]
    assert ocorrencias_proibidas("# 3b. T\nx PRD y\n") == []
    assert ocorrencias_proibidas("x PRD y\n# 14. T\n") == []
    assert ocorrencias_proibidas("# 14. T\nx PRD com PRD/TS/SDD já no lugar\n") == []
    text = _text()
    ok = "Já tenho SPEC/SDD prontos"
    assert ok in text, "trecho a mutar sumiu do YAML"
    assert resumo(text.replace(ok, "Já tenho PRD/TS/SDD prontos")) == (1, 2)
