"""Testes de approval_hash.py — SDD-DTF-0054, RF04 (SPEC-DTF-0029).

Usa o workflow-rules.yaml real para as seções excluídas do hash.
"""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from approval_hash import content_hash  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SCRIPTS_DIR.parent / "schemas" / "approval-hash.schema.json"

FRONT = '---\nid: SDD-TST-0001\ntype: SDD\ntitle: "teste"\nstatus: {status}\n---\n'
BODY = (
    "\n# Título\n\n## Requisitos consolidados\n\nRF01 faz X.\n\n"
    "## Evidência de verificação (preencher antes de status `implemented`)\n\n{evidencia}\n\n"
    "## Rastreabilidade\n\nSPEC-TST-0001\n"
)


def _doc(tmp_path: Path, name: str = "doc.md", status: str = "approved", evidencia: str = "", body: str = None) -> Path:
    path = tmp_path / name
    text = FRONT.format(status=status) + (body if body is not None else BODY.format(evidencia=evidencia))
    path.write_bytes(text.encode("utf-8"))
    return path


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "approval_hash.py"), *args],
        capture_output=True,
        text=True,
    )


def test_hash_e_hexadecimal_de_64(tmp_path):
    h = content_hash(_doc(tmp_path))
    assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)


def test_hash_estavel_com_crlf(tmp_path):
    lf = _doc(tmp_path, "lf.md")
    crlf = tmp_path / "crlf.md"
    crlf.write_bytes(lf.read_bytes().replace(b"\n", b"\r\n"))
    assert content_hash(crlf) == content_hash(lf)


def test_hash_ignora_front_matter(tmp_path):
    a = _doc(tmp_path, "a.md", status="approved")
    b = _doc(tmp_path, "b.md", status="implemented")
    assert content_hash(a) == content_hash(b)


def test_hash_ignora_secao_excluida_preenchida(tmp_path):
    vazio = _doc(tmp_path, "vazio.md", evidencia="")
    cheio = _doc(tmp_path, "cheio.md", evidencia="| A01 | pytest | 3 passed | sim | sim | t.py:1 | automatizado |")
    assert content_hash(cheio) == content_hash(vazio)


def test_hash_muda_com_corpo_mudado(tmp_path):
    a = _doc(tmp_path, "a.md")
    b = _doc(tmp_path, "b.md", body=BODY.format(evidencia="").replace("RF01 faz X.", "RF01 faz Y."))
    assert content_hash(a) != content_hash(b)


def test_secao_seguinte_a_excluida_entra_no_hash(tmp_path):
    a = _doc(tmp_path, "a.md")
    b = _doc(tmp_path, "b.md", body=BODY.format(evidencia="").replace("SPEC-TST-0001\n", "SPEC-TST-0002\n"))
    assert content_hash(a) != content_hash(b)


def test_hash_ignora_espacos_no_fim_e_linhas_em_branco_finais(tmp_path):
    a = _doc(tmp_path, "a.md")
    b = _doc(tmp_path, "b.md", body=BODY.format(evidencia="").replace("RF01 faz X.", "RF01 faz X.   ") + "\n\n\n")
    assert content_hash(a) == content_hash(b)


def test_sem_exclusao_explicita_a_secao_conta(tmp_path):
    vazio = _doc(tmp_path, "vazio.md", evidencia="")
    cheio = _doc(tmp_path, "cheio.md", evidencia="preenchida")
    assert content_hash(cheio, excluded=[]) != content_hash(vazio, excluded=[])


def test_cli_imprime_so_o_hash(tmp_path):
    path = _doc(tmp_path)
    r = _run(str(path))
    assert r.returncode == 0
    assert r.stdout.strip() == content_hash(path)


def test_cli_json_valida_contra_o_esquema(tmp_path):
    path = _doc(tmp_path)
    r = _run(str(path), "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    jsonschema.validate(data, json.loads(SCHEMA.read_text(encoding="utf-8")))
    assert data["schema"] == "dtf.approval-hash/1"
    assert data["documento"] == "SDD-TST-0001"
    assert data["content_sha256"] == content_hash(path)
    assert "Evidência de verificação" in data["secoes_excluidas"]


def test_cli_sem_front_matter_sai_com_1(tmp_path):
    path = tmp_path / "solto.md"
    path.write_text("# sem front-matter\n", encoding="utf-8")
    r = _run(str(path))
    assert r.returncode == 1
    assert r.stdout == ""
    assert "front-matter" in r.stderr


def test_cli_sem_argumento_sai_com_1():
    assert _run().returncode == 1
