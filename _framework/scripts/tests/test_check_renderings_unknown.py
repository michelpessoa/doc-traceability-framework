"""Checagem 4 de check_renderings.py: status e tipo inexistentes reprovam.

SDD-DTF-0063 (RF01 a RF05). As regras são chamadas direto em
check_unknown_names com textos curtos, e o script roda como subprocesso
sobre o kit real para o RF04 (sem falso positivo).
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework_lib import load_rules  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "check_renderings.py"
REPO = Path(__file__).resolve().parents[3]
REL = "SKILL.md"


def _sets() -> tuple[set[str], set[str]]:
    rules = load_rules()
    statuses = set(rules["status_lifecycle"]["states"]) | set(rules["incident_lifecycle"]["states"])
    types = set(rules["document_types"]) | set(rules.get("legacy_document_types") or {})
    return statuses, types


def _check(raw: str) -> list[str]:
    # Import tardio: antes da task 2 a função não existe e cada teste
    # falha sozinho, em vez de a coleta inteira quebrar.
    from check_renderings import check_unknown_names

    statuses, types = _sets()
    return check_unknown_names(REL, raw, statuses, types)


def _status(palavra: str) -> str:
    return f"{REL}: cita o status inexistente '{palavra}'."


def _tipo(prefixo: str) -> str:
    return f"{REL}: cita o tipo inexistente '{prefixo}'."


# RF01: status em cadeia


def test_rf01_cadeia_com_status_inexistente_reprova():
    assert _check("Ciclo: draft → obsolete → approved.\n") == [_status("obsolete")]


def test_rf01_cadeia_com_alternativas_e_crases_reprova():
    raw = "`draft` → `in_review` → `approved` → `implemented|retired|superseded` → **archived**\n"
    assert _check(raw) == [_status("retired")]


def test_rf01_cadeia_quebrada_em_linhas_reprova():
    assert _check("draft → in_review →\n   obsolete → archived\n") == [_status("obsolete")]


def test_rf01_cadeias_validas_passam():
    raw = (
        "draft → in_review → approved → implemented|rejected|superseded → archived\n"
        "open → mitigated → resolved → closed\n"
    )
    assert _check(raw) == []


def test_rf01_negativo_cadeia_de_dois_termos_nao_acusa():
    assert _check("Promova draft → obsolete só depois da revisão.\n") == []


def test_rf01_negativo_palavra_com_barra_nao_acusa():
    assert _check("Fluxo de branch: feature/x → develop → main.\n") == []


# RF02: status declarado entre crases


def test_rf02_status_declarado_inexistente_reprova():
    assert _check("Marque `status: obsolete` no front-matter.\n") == [_status("obsolete")]


def test_rf02_status_declarado_valido_passa():
    assert _check("Só com `status: approved` a SDD pode ser implementada.\n") == []


def test_rf02_negativo_repository_status_sem_crases_nao_acusa():
    assert _check("No registry: repository_status: none_yet enquanto não houver repo.\n") == []


def test_status_reportado_uma_vez_por_renderizacao():
    raw = "draft → obsolete → approved\n`status: obsolete`\ndraft → in_review → obsolete\n"
    assert _check(raw) == [_status("obsolete")]


# RF03: tipo em id


def test_rf03_tipo_inexistente_em_id_reprova():
    assert _check("Veja XYZ-EVM-0001 para o contexto.\n") == [_tipo("XYZ")]


def test_rf03_placeholders_reprovam_tipo_inexistente():
    raw = "`FOO-{PROJECT_CODE}-X` e BAR-DTF-N\n"
    assert _check(raw) == [_tipo("FOO"), _tipo("BAR")]


def test_rf03_tipos_ativos_e_legados_passam():
    raw = "SPEC-{PROJECT_CODE}-{SEQ4}, SDD-DTF-0063, ADR-EVM-N, PRD-EVM-0001 (legado), TS-EVM-{SEQ}\n"
    assert _check(raw) == []


def test_rf03_negativo_formato_que_nao_e_id_nao_acusa():
    assert _check("Use UTF-8, ISO-8601 e XYZ-EVM-12 à vontade.\n") == []


def test_tipo_reportado_uma_vez_por_renderizacao():
    assert _check("XYZ-EVM-0001 e XYZ-EVM-0002\n") == [_tipo("XYZ")]


# RF04: sem falso positivo no kit real


def test_rf04_kit_real_passa():
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "inexistente" not in r.stdout + r.stderr
