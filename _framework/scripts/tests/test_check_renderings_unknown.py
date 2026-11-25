"""Checagem 4 de check_renderings.py: status e tipo inexistentes reprovam.

SDD-DTF-0063 (RF01 a RF05). As regras são chamadas direto em
check_unknown_names com textos curtos, e o script roda como subprocesso
sobre o kit real para o RF04 (sem falso positivo).
"""

import shutil
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


# SDD-DTF-0064: placeholders de sequência e o fim do id


def test_sdd0064_placeholders_de_sequencia_reprovam_tipo_inexistente():
    raw = "`FOO-{PROJECT_CODE}-{SEQ4}`, BAR-DTF-{SEQ4}. e BAZ-{PROJECT_CODE}-{SEQ}\n"
    assert _check(raw) == [_tipo("FOO"), _tipo("BAR"), _tipo("BAZ")]


def test_sdd0064_negativo_sequencia_que_nao_e_id_nao_acusa():
    assert _check("XYZ-EVM-12, XYZ-EVM-00012 e XYZ-EVM-Xy\n") == []


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


# SDD-DTF-0065: o main de check_renderings.py numa cópia do kit (RF02, RF03)

SKILL_REL = Path("_framework/skills/doc-traceability-framework/SKILL.md")


def _copia_do_kit(tmp_path: Path) -> Path:
    """Copia _framework/ (sem __pycache__), .claude/ e AGENTS.md para tmp_path.

    Mesma estrutura da raiz do kit: find_rules_file acha o YAML da cópia,
    RENDERINGS resolve ../AGENTS.md e MECHANIZED_ARTIFACTS acha ../.claude/.
    """
    shutil.copytree(REPO / "_framework", tmp_path / "_framework", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(REPO / ".claude", tmp_path / ".claude")
    shutil.copy2(REPO / "AGENTS.md", tmp_path / "AGENTS.md")
    return tmp_path


def _roda_copia(kit: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(kit / "_framework/scripts/check_renderings.py")],
        cwd=kit,
        capture_output=True,
        text=True,
        check=False,
    )


def _copia_que_passa(tmp_path: Path) -> Path:
    kit = _copia_do_kit(tmp_path)
    r = _roda_copia(kit)
    assert r.returncode == 0, "a cópia sem alteração já reprova: " + r.stdout + r.stderr
    return kit


def test_sdd0065_main_reprova_status_inexistente_na_copia(tmp_path):
    kit = _copia_que_passa(tmp_path)
    skill = kit / SKILL_REL
    raw = skill.read_text(encoding="utf-8")
    if "→ in_review →" in raw:
        raw = raw.replace("→ in_review →", "→ obsolete →", 1)
    else:
        raw += "\n`draft` → `obsolete` → `approved`\n"
    skill.write_text(raw, encoding="utf-8")
    r = _roda_copia(kit)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "cita o status inexistente" in r.stdout + r.stderr


def test_sdd0065_main_aceita_tipos_legados_na_copia(tmp_path):
    kit = _copia_que_passa(tmp_path)
    skill = kit / SKILL_REL
    raw = skill.read_text(encoding="utf-8")
    skill.write_text(raw + "\nIds legados: PRD-EVM-0001 e TS-EVM-0001.\n", encoding="utf-8")
    r = _roda_copia(kit)
    assert r.returncode == 0, r.stdout + r.stderr
