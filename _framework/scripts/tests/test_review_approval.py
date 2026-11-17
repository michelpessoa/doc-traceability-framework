"""Testes de review_approval.py e de approvers no registry — SDD-DTF-0055.

RF01, RF03, RF04 e RF05 da SPEC-DTF-0030. Os testes de `approvers` no
registry têm "approvers" no nome (critério A02); os de decisão e CLI, não
(critério A01).
"""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from approval_hash import content_hash  # noqa: E402
from registry_tools import check_approvers, cmd_validate  # noqa: E402
from review_approval import approvers_for, approves, decide  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SCRIPTS_DIR.parent / "schemas" / "review-approval.schema.json"
HEAD = "a" * 40
ANTIGO = "b" * 40
PR = "https://github.com/dono/central/pull/7"


def _review(login="owner", state="APPROVED", body="", commit=HEAD, at="2099-01-01T10:00:00Z", rid=1) -> dict:
    return {
        "id": rid,
        "user": {"login": login},
        "state": state,
        "body": body,
        "commit_id": commit,
        "submitted_at": at,
    }


def _central(tmp_path: Path, approvers=("owner",), status: str = "in_review") -> Path:
    docs = tmp_path / "docs" / "TST"
    (docs / "03-spec").mkdir(parents=True)
    registry: dict = {"project": "TST", "framework_version": "2.5.0"}
    if approvers is not None:
        registry["approvers"] = list(approvers)
    (docs / "registry.yaml").write_text(yaml.safe_dump(registry), encoding="utf-8")
    doc = docs / "03-spec" / "SPEC-TST-0001.md"
    doc.write_text(
        f'---\nid: SPEC-TST-0001\ntype: SPEC\ntitle: "t"\nstatus: {status}\n---\n\n# t\n\n## Objetivo\n\nX.\n',
        encoding="utf-8",
    )
    return doc


def _run(doc: Path, reviews, *extra: str, head: str = HEAD, pr: str = PR) -> subprocess.CompletedProcess:
    arquivo = doc.parent / "reviews.json"
    arquivo.write_text(reviews if isinstance(reviews, str) else json.dumps(reviews), encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "review_approval.py"),
            str(doc),
            "--reviews",
            str(arquivo),
            "--head",
            head,
            "--pr-url",
            pr,
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def _json(resultado: subprocess.CompletedProcess) -> dict:
    objeto = json.loads(resultado.stdout)
    jsonschema.validate(objeto, json.loads(SCHEMA.read_text(encoding="utf-8")))
    return objeto


# --- RF04: decide -----------------------------------------------------------


def test_approved_sobre_o_head_vale():
    r = decide([_review()], HEAD, ["owner"])
    assert r["valida"] is True and r["motivos"] == [] and r["review"]["id"] == 1


def test_commented_com_aprovado_exato_vale():
    assert decide([_review(state="COMMENTED", body="  Aprovado\n")], HEAD, ["owner"])["valida"] is True


@pytest.mark.parametrize("corpo", ["aprovado", "Aprovado.", "Aprovado, mas ajuste X", "", None])
def test_commented_com_outro_corpo_nao_aprova(corpo):
    r = decide([_review(state="COMMENTED", body=corpo)], HEAD, ["owner"])
    assert r["valida"] is False and r["motivos"] == ["nenhuma review de aprovador"]


def test_sem_review_e_invalida():
    assert decide([], HEAD, ["owner"]) == {"valida": False, "motivos": ["nenhuma review de aprovador"], "review": None}


def test_review_de_login_fora_da_lista_e_ignorada():
    assert decide([_review(login="intruso")], HEAD, ["owner"])["motivos"] == ["nenhuma review de aprovador"]


def test_aprovacao_seguida_de_changes_requested_e_invalida():
    reviews = [
        _review(at="2099-01-01T10:00:00Z", rid=1),
        _review(login="outro", state="CHANGES_REQUESTED", at="2099-01-01T11:00:00Z", rid=2),
    ]
    r = decide(reviews, HEAD, ["owner", "outro"])
    assert r["valida"] is False
    assert r["motivos"] == ["a review decisiva de outro pede mudanças (2099-01-01T11:00:00Z)"]


def test_changes_requested_seguida_de_aprovacao_vale():
    reviews = [
        _review(state="CHANGES_REQUESTED", at="2099-01-01T09:00:00Z", rid=1),
        _review(at="2099-01-01T10:00:00Z", rid=2),
    ]
    r = decide(reviews, HEAD, ["owner"])
    assert r["valida"] is True and r["review"]["id"] == 2


def test_decisiva_e_a_mais_recente_mesmo_fora_de_ordem():
    reviews = [
        _review(at="2099-01-01T12:00:00Z", rid=2),
        _review(state="CHANGES_REQUESTED", at="2099-01-01T09:00:00Z", rid=1),
    ]
    assert decide(reviews, HEAD, ["owner"])["review"]["id"] == 2


def test_dismissed_e_comentario_qualquer_nao_contam_na_decisiva():
    reviews = [
        _review(at="2099-01-01T10:00:00Z", rid=1),
        _review(state="DISMISSED", at="2099-01-01T11:00:00Z", rid=2),
        _review(state="COMMENTED", body="vou olhar depois", at="2099-01-01T12:00:00Z", rid=3),
    ]
    r = decide(reviews, HEAD, ["owner"])
    assert r["valida"] is True and r["review"]["id"] == 1


def test_aprovacao_sobre_commit_anterior_e_invalida():
    r = decide([_review(commit=ANTIGO)], HEAD, ["owner"])
    assert r["valida"] is False
    assert r["motivos"] == [f"review sobre {ANTIGO}, head é {HEAD}: nova review necessária"]


def test_approves_so_aceita_os_dois_formatos():
    assert approves(_review(state="APPROVED"))
    assert approves(_review(state="COMMENTED", body="Aprovado"))
    assert not approves(_review(state="CHANGES_REQUESTED", body="Aprovado"))


# --- RF03, RF05: CLI --------------------------------------------------------


def test_cli_valida_devolve_approved_by_e_sai_0(tmp_path):
    doc = _central(tmp_path)
    resultado = _run(doc, [_review(rid=99)], "--json")
    assert resultado.returncode == 0, resultado.stderr
    objeto = _json(resultado)
    assert objeto["schema"] == "dtf.review-approval/1"
    assert objeto["documento"] == "SPEC-TST-0001" and objeto["head"] == HEAD and objeto["valida"] is True
    assert objeto["approved_by"] == {
        "kind": "human",
        "actor": "owner",
        "at": "2099-01-01T10:00:00Z",
        "content_sha256": content_hash(doc),
        "evidence": f"{PR}#pullrequestreview-99",
    }


def test_cli_hash_igual_ao_do_approval_hash(tmp_path):
    doc = _central(tmp_path)
    hash_cli = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "approval_hash.py"), str(doc)], capture_output=True, text=True
    ).stdout.strip()
    assert _json(_run(doc, [_review()], "--json"))["approved_by"]["content_sha256"] == hash_cli


def test_cli_invalida_sai_1_com_motivo(tmp_path):
    resultado = _run(_central(tmp_path), [_review(commit=ANTIGO)], "--json")
    assert resultado.returncode == 1
    objeto = _json(resultado)
    assert objeto["valida"] is False and objeto["approved_by"] is None
    assert objeto["motivos"] == [f"review sobre {ANTIGO}, head é {HEAD}: nova review necessária"]


def test_cli_sem_lista_no_registry_sai_1(tmp_path):
    resultado = _run(_central(tmp_path, approvers=None), [_review()], "--json")
    assert resultado.returncode == 1
    assert _json(resultado)["motivos"] == ["approvers não declarado no registry"]


def test_cli_documento_fora_de_in_review_sai_1(tmp_path):
    resultado = _run(_central(tmp_path, status="draft"), [_review()], "--json")
    assert resultado.returncode == 1
    assert _json(resultado)["motivos"] == ["documento está draft, não in_review"]


@pytest.mark.parametrize("pr", ["https://github.com/dono/central/pulls/7", "http://github.com/d/c/pull/7", "7"])
def test_cli_pr_url_fora_do_formato_sai_2(tmp_path, pr):
    resultado = _run(_central(tmp_path), [_review()], "--json", pr=pr)
    assert resultado.returncode == 2
    assert _json(resultado)["motivos"] == ["--pr-url fora do formato https://github.com/<dono>/<repo>/pull/<n>"]


def test_cli_reviews_que_nao_sao_lista_sai_2(tmp_path):
    resultado = _run(_central(tmp_path), '{"id": 1}', "--json")
    assert resultado.returncode == 2 and _json(resultado)["valida"] is False


@pytest.mark.parametrize("campo", ["id", "user", "state", "commit_id", "submitted_at"])
def test_cli_review_sem_campo_sai_2_nomeando(tmp_path, campo):
    review = _review()
    del review[campo]
    resultado = _run(_central(tmp_path), [review], "--json")
    assert resultado.returncode == 2
    nome = "user.login" if campo == "user" else campo
    assert _json(resultado)["motivos"] == [f"review 0 sem {nome}"]


def test_cli_documento_inexistente_sai_2(tmp_path):
    _central(tmp_path)
    resultado = _run(tmp_path / "docs" / "TST" / "nao-existe.md", [_review()])
    assert resultado.returncode == 2


def test_cli_texto_imprime_bloco_yaml(tmp_path):
    doc = _central(tmp_path)
    resultado = _run(doc, [_review(rid=5)])
    assert resultado.returncode == 0
    bloco = yaml.safe_load(resultado.stdout)
    assert bloco["approved_by"]["actor"] == "owner"
    assert bloco["approved_by"]["evidence"] == f"{PR}#pullrequestreview-5"


def test_cli_texto_invalida_motivo_no_stderr(tmp_path):
    resultado = _run(_central(tmp_path), [])
    assert resultado.returncode == 1 and resultado.stdout == ""
    assert "nenhuma review de aprovador" in resultado.stderr


def test_lista_lida_do_registry_mais_proximo(tmp_path):
    assert approvers_for(_central(tmp_path, approvers=("a", "b"))) == ["a", "b"]
    assert approvers_for(_central(tmp_path / "x", approvers=None)) is None


# --- RF01: approvers no registry central ------------------------------------

ERRO = "registry.yaml: `approvers` deve ser uma lista não vazia de logins do GitHub, sem espaço."


def test_approvers_valido_ou_ausente_passa():
    assert check_approvers({"approvers": ["michelpessoa", "outro-login"]}) == []
    assert check_approvers({}) == []


@pytest.mark.parametrize("valor", [[], "michelpessoa", ["com espaço"], [""], [1], None, ["ok", " "]])
def test_approvers_invalido_reprova(valor):
    assert check_approvers({"approvers": valor}) == [ERRO]


def _registry_central(tmp_path: Path, approvers) -> Path:
    data = {
        "project": "TST",
        "framework_version": "2.5.0",
        "repository": "https://github.com/dono/codigo",
        "repository_status": "active",
        "approvers": approvers,
        "documents": [],
    }
    (tmp_path / "registry.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return tmp_path


def test_approvers_invalido_reprova_no_validate(tmp_path, capsys):
    assert cmd_validate(_registry_central(tmp_path, ["com espaço"])) == 1
    assert ERRO in capsys.readouterr().out


def test_approvers_valido_passa_no_validate(tmp_path):
    assert cmd_validate(_registry_central(tmp_path, ["owner"])) == 0
