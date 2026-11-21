"""Estrutura de _framework/procedures/verify-sdd.md (RF06, SDD-DTF-0044)."""

import re
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PROCEDURE = TESTS_DIR.parent / "procedures" / "verify-sdd.md"
FIXTURE = TESTS_DIR / "fixtures" / "verify_sdd_pre_reorder.md"

# Linhas que podem diferir da fixture: apontamentos do passo 4, título da
# nova subseção e rótulos dos três modelos (contrato 5 da SDD-DTF-0044).
ADDED_LINES = {
    'Na SDD, a seção "Evidência de verificação" segue o modelo M1, em "Modelos de registro".',
    'do modelo M2, em "Modelos de registro", em vez de despachar uma 4ª tentativa.',
    'Escreva `validation.md` ao lado da SDD, conforme o modelo M3, em "Modelos de registro".',
    "### Modelos de registro",
    "**M1. Tabela de evidência na SDD**",
    "**M2. Escalonado ao humano**",
    "**M3. validation.md**",
}
REMOVED_LINES = {
    'Na SDD, a seção "Evidência de verificação" fica assim:',
    "abaixo em vez de despachar uma 4ª tentativa:",
    "Escreva `validation.md` ao lado da SDD:",
}


def _nonblank(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_verify_sdd_step5_before_fenced_templates_headings():
    lines = PROCEDURE.read_text(encoding="utf-8").splitlines()
    step5 = next(i for i, line in enumerate(lines) if line.startswith("### 5."))
    late_titles = (
        "## Evidência de verificação",
        "## Escalonado ao humano",
        "# Verificação —",
        "## Descompassos encontrados",
        "## Lições",
    )
    for title in late_titles:
        found = [i for i, line in enumerate(lines) if line.startswith(title)]
        assert found, f"título ausente: {title!r}"
        assert all(i > step5 for i in found), (
            f"{title!r} (linha {found[0] + 1}) aparece antes de '### 5.' (linha {step5 + 1})"
        )
    order = ["### 4.", "### 5.", "### Modelos de registro", "## Red flags"]
    positions = [next(i for i, ln in enumerate(lines) if ln.startswith(o)) for o in order]
    assert positions == sorted(positions), f"ordem estrutural incorreta: {dict(zip(order, positions))}"
    # Frase de introdução do passo 4 não pode terminar em ":" antes de um título.
    for i, line in enumerate(lines[:-2]):
        if line.rstrip().endswith(":") and not lines[i + 1].strip() and lines[i + 2].startswith("#"):
            raise AssertionError(f"linha {i + 1}: frase termina em ':' seguida de título: {line!r}")
    step4 = "\n".join(lines[next(i for i, ln in enumerate(lines) if ln.startswith("### 4.")) : step5])
    for model in ("M1", "M2", "M3"):
        assert re.search(rf"modelo {model}\b", step4), f"passo 4 não cita o modelo {model}"


M4_INTRO = (
    "Quem roda este procedimento a partir de um executor pode devolver também o",
    "resultado em JSON, conforme o modelo M4, opcional. Ele não substitui M1 nem",
    "M3.",
)


def _without_m4(lines: list[str]) -> list[str]:
    """Tira o que a SDD-DTF-0053 acrescentou (modelo M4 e a frase que o cita):
    este teste guarda a reordenação anterior, não proíbe conteúdo novo."""
    start = next(i for i, line in enumerate(lines) if line.startswith("**M4."))
    end = next(i for i, line in enumerate(lines) if line.startswith("## Red flags"))
    kept = lines[:start] + lines[end:]
    return [line for line in kept if line not in M4_INTRO]


# Linhas que a SDD-DTF-0057 acrescentou (SDD enxuta lê a Parte 2 da SPEC):
# mesmo critério do M4, conteúdo novo não conta como reordenação.
LEAN_LINES = (
    'Na SDD enxuta (2.7.0, com `source_docs`), a SDD não tem "Especificação',
    'técnica consolidada": o desenho a conferir é a Parte 2 da SPEC, lida',
    "pela url de `source_docs`, e o item 2 já é mecanizado pelo",
    "`check_source_docs.py` (RFs nas duas direções).",
    '- Na SDD enxuta, no lugar da "Especificação técnica consolidada", confira',
    "a Parte 2 da SPEC, lida pela url de `source_docs`.",
)


# Linhas que a SDD-DTF-0058 acrescentou (coluna Projeto da SPEC, item 2 do
# passo 0): mesmo critério, conteúdo novo não conta como reordenação.
PROJECT_LINES = (
    "Quando a SPEC tem a coluna `Projeto`, contam só os RFs do `project` do",
    "registry da SDD; o `check_source_docs.py` já confere isso na SDD enxuta.",
)


def test_verify_sdd_reorder_preserves_lines():
    before = _nonblank(FIXTURE)
    after = [
        line
        for line in _without_m4(_nonblank(PROCEDURE))
        if line.strip() not in LEAN_LINES and line.strip() not in PROJECT_LINES
    ]
    from collections import Counter

    b, a = Counter(before), Counter(after)
    lost = b - a
    gained = a - b
    assert set(lost) == REMOVED_LINES, f"linhas perdidas fora do esperado: {sorted(set(lost) ^ REMOVED_LINES)}"
    assert set(gained) == ADDED_LINES, f"linhas novas fora do esperado: {sorted(set(gained) ^ ADDED_LINES)}"
