"""Saída --json dos validadores — ver SDD-DTF-0053 (SPEC-DTF-0028, RF01 e RF02)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCRIPTS = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS.parents[1]
SCHEMA = REPO_ROOT / "_framework" / "schemas" / "resultado-validador.schema.json"

sys.path.insert(0, str(SCRIPTS))

from framework_lib import json_flag, report  # noqa: E402

SPEC_RUIM = '---\nid: SPEC-X-0001\ntype: SPEC\ntitle: "t"\nstatus: in_review\n---\n\n# t\n'


def rodar(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)


def valida(objeto: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    erros = [e.message for e in Draft202012Validator(schema).iter_errors(objeto)]
    assert erros == []


# ---------------------------------------------------------------------------
# json_flag e report
# ---------------------------------------------------------------------------


def test_json_flag_tira_a_flag_e_avisa():
    assert json_flag(["a", "--json", "b"]) == (["a", "b"], True)
    assert json_flag(["a", "b"]) == (["a", "b"], False)


def test_report_json_com_problema(capsys):
    codigo = report(
        ["SPEC-X-0001: seção ausente", "mensagem sem id"],
        ["ADR-X-0002: aviso"],
        "ok",
        as_json=True,
        script="validate_doc.py",
    )
    objeto = json.loads(capsys.readouterr().out)
    assert codigo == 1
    assert objeto["ok"] is False and objeto["exit_code"] == 1
    assert objeto["script"] == "validate_doc.py"
    assert objeto["problemas"] == [
        {"documento": "SPEC-X-0001", "mensagem": "SPEC-X-0001: seção ausente"},
        {"documento": None, "mensagem": "mensagem sem id"},
    ]
    assert objeto["avisos"] == [{"documento": "ADR-X-0002", "mensagem": "ADR-X-0002: aviso"}]
    valida(objeto)


def test_report_json_sem_problema(capsys):
    assert report([], [], "ok", as_json=True, script="validate_doc.py") == 0
    objeto = json.loads(capsys.readouterr().out)
    assert objeto["ok"] is True and objeto["exit_code"] == 0 and objeto["problemas"] == []
    valida(objeto)


def test_report_json_report_only_sai_zero_mas_nao_ok(capsys):
    assert report(["X-1: p"], [], "ok", report_only=True, as_json=True, script="s.py") == 0
    objeto = json.loads(capsys.readouterr().out)
    assert objeto["ok"] is False and objeto["exit_code"] == 0


def test_id_no_meio_da_mensagem_nao_vira_documento(capsys):
    report(["veja SPEC-X-0001: no meio"], [], "ok", as_json=True, script="s.py")
    assert json.loads(capsys.readouterr().out)["problemas"][0]["documento"] is None


def test_report_sem_json_igual_ao_de_antes(capsys):
    assert report(["SPEC-X-0001: p"], ["w"], "ok") == 1
    assert capsys.readouterr().out == "⚠️  w\n❌ 1 problema(s) encontrado(s):\n  - SPEC-X-0001: p\n"
    assert report([], [], "tudo certo") == 0
    assert capsys.readouterr().out == "tudo certo\n"


# ---------------------------------------------------------------------------
# Os cinco scripts, em processo real
# ---------------------------------------------------------------------------


@pytest.fixture
def spec_ruim(tmp_path) -> Path:
    caminho = tmp_path / "SPEC-X-0001.md"
    caminho.write_text(SPEC_RUIM, encoding="utf-8")
    return caminho


def _comparar(sem: subprocess.CompletedProcess, com: subprocess.CompletedProcess, script: str) -> dict:
    objeto = json.loads(com.stdout)
    valida(objeto)
    assert objeto["script"] == script
    assert com.returncode == sem.returncode == objeto["exit_code"]
    return objeto


def test_validate_doc_json(spec_ruim):
    script = "_framework/scripts/validate_doc.py"
    sem, com = rodar(script, str(spec_ruim)), rodar(script, str(spec_ruim), "--json")
    objeto = _comparar(sem, com, "validate_doc.py")
    assert objeto["ok"] is False
    assert all(p["documento"] == "SPEC-X-0001" for p in objeto["problemas"])
    assert sem.stdout.startswith("❌") or sem.stdout.startswith("⚠️")


def test_validate_state_json(tmp_path):
    script = "_framework/scripts/validate_state.py"
    sdd = tmp_path / "SDD-X-0001.md"
    sdd.write_text("---\nid: SDD-X-0001\ntype: SDD\nstatus: approved\n---\n\n# s\n", encoding="utf-8")
    objeto = _comparar(rodar(script, str(sdd)), rodar(script, str(sdd), "--json"), "validate_state.py")
    assert objeto["ok"] is True


def test_check_source_docs_json(tmp_path):
    script = "_framework/scripts/check_source_docs.py"
    sdd = tmp_path / "SDD-X-0001.md"
    sdd.write_text(
        '---\nid: SDD-X-0001\ntype: SDD\nsource_docs:\n  - id: "SPEC-X-0009"\n    url: "u"\n---\n', encoding="utf-8"
    )
    central = tmp_path / "central"
    central.mkdir()
    (central / "registry.yaml").write_text("documents: []\n", encoding="utf-8")
    sem, com = rodar(script, str(sdd), str(central)), rodar(script, str(sdd), str(central), "--json")
    objeto = _comparar(sem, com, "check_source_docs.py")
    assert objeto["ok"] is False and sem.returncode == 1


def test_registry_tools_validate_json(tmp_path):
    script = "_framework/scripts/registry_tools.py"
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "registry.yaml").write_text(
        'project: "X"\ndocuments:\n  - id: SPEC-X-0001\n    type: SPEC\n'
        '    status: inventado\n    path: "nao-existe.md"\n',
        encoding="utf-8",
    )
    sem, com = rodar(script, "validate", str(docs)), rodar(script, "validate", str(docs), "--json")
    objeto = _comparar(sem, com, "registry_tools.py")
    assert objeto["ok"] is False
    assert any(p["documento"] == "SPEC-X-0001" for p in objeto["problemas"])


def test_check_commit_json(tmp_path):
    script = "_framework/scripts/check_commit.py"
    msg = tmp_path / "MSG"
    msg.write_text("mensagem fora do formato\n", encoding="utf-8")
    objeto = _comparar(rodar(script, str(msg)), rodar(script, str(msg), "--json"), "check_commit.py")
    assert objeto["ok"] is False


def test_sem_argumentos_com_json_mesmo_codigo():
    for script in ("validate_doc.py", "validate_state.py", "check_source_docs.py", "check_commit.py"):
        caminho = f"_framework/scripts/{script}"
        sem, com = rodar(caminho), rodar(caminho, "--json")
        objeto = json.loads(com.stdout)
        valida(objeto)
        assert com.returncode == sem.returncode == 1 and objeto["ok"] is False


def test_erro_operacional_vira_json(tmp_path):
    script = "_framework/scripts/registry_tools.py"
    sem, com = (
        rodar(script, "validate", str(tmp_path / "nao-existe")),
        rodar(script, "validate", str(tmp_path / "nao-existe"), "--json"),
    )
    objeto = json.loads(com.stdout)
    valida(objeto)
    assert com.returncode == sem.returncode == 1
    assert objeto["problemas"][0]["mensagem"].startswith("erro operacional:")


# ---------------------------------------------------------------------------
# A02 — saída em texto igual à do framework 2.3.2, contra fixture gravada
# ---------------------------------------------------------------------------
# `fixtures/saida_texto_2_3_2.json` foi gravada rodando CASOS com os scripts
# do framework 2.3.2 (kit em 279b10a), antes do --json existir, cada caso
# num diretório novo e com caminhos relativos a ele. Não regravar a fixture
# para acomodar mudança de texto: mudança de texto quebra quem lê a saída.

FIXTURE_TEXTO = Path(__file__).resolve().parent / "fixtures" / "saida_texto_2_3_2.json"

SPEC_RUIM_CASO = '---\nid: SPEC-X-0001\ntype: SPEC\ntitle: "t"\nstatus: in_review\n---\n\n# t\n'
SDD_OK = "---\nid: SDD-X-0001\ntype: SDD\nstatus: approved\n---\n\n# s\n"
SDD_ORIGEM = '---\nid: SDD-X-0001\ntype: SDD\nsource_docs:\n  - id: "SPEC-X-0009"\n    url: "u"\n---\n'
REGISTRY_RUIM = (
    'project: "X"\nframework_version: "2.3.2"\ndocuments:\n  - id: SPEC-X-0001\n    type: SPEC\n'
    '    status: inventado\n    path: "nao-existe.md"\n'
)


def _escrever(raiz: Path, arquivos: dict[str, str]) -> None:
    for nome, texto in arquivos.items():
        caminho = raiz / nome
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")


CASOS = {
    "validate_doc_problemas": ({"SPEC-X-0001.md": SPEC_RUIM_CASO}, ["validate_doc.py", "SPEC-X-0001.md"]),
    "validate_doc_report_only": (
        {"SPEC-X-0001.md": SPEC_RUIM_CASO},
        ["validate_doc.py", "SPEC-X-0001.md", "--report-only"],
    ),
    "validate_doc_uso": ({}, ["validate_doc.py"]),
    "validate_state_ok": ({"SDD-X-0001.md": SDD_OK}, ["validate_state.py", "SDD-X-0001.md"]),
    "validate_state_uso": ({}, ["validate_state.py"]),
    "check_source_docs_problema": (
        {"SDD-X-0001.md": SDD_ORIGEM, "central/registry.yaml": "documents: []\n"},
        ["check_source_docs.py", "SDD-X-0001.md", "central"],
    ),
    "check_source_docs_uso": ({}, ["check_source_docs.py"]),
    "registry_tools_validate_problemas": (
        {"docs/registry.yaml": REGISTRY_RUIM},
        ["registry_tools.py", "validate", "docs"],
    ),
    "registry_tools_uso": ({}, ["registry_tools.py"]),
    "check_commit_problema": ({"MSG": "mensagem fora do formato\n"}, ["check_commit.py", "MSG"]),
    "check_commit_ok": ({"MSG": "docs: mensagem no formato\n\nRefs: SDD-X-0001\n"}, ["check_commit.py", "MSG"]),
    "check_commit_uso": ({}, ["check_commit.py"]),
}


def preparar(caso: str, raiz: Path) -> list[str]:
    arquivos, args = CASOS[caso]
    _escrever(raiz, arquivos)
    return args


@pytest.mark.parametrize("caso", sorted(CASOS))
def test_saida_em_texto_igual_a_2_3_2(caso, tmp_path):
    esperado = json.loads(FIXTURE_TEXTO.read_text(encoding="utf-8"))[caso]
    args = preparar(caso, tmp_path)
    obtido = rodar(str(SCRIPTS / args[0]), *args[1:], cwd=tmp_path)
    assert obtido.stdout == esperado["stdout"]
    assert obtido.returncode == esperado["exit"]


def test_fixture_de_texto_cobre_todos_os_casos():
    assert set(json.loads(FIXTURE_TEXTO.read_text(encoding="utf-8"))) == set(CASOS)
