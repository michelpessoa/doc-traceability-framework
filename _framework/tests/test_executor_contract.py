"""Contrato do executor — ver SDD-DTF-0053 (SPEC-DTF-0028, RF03 a RF05 e RF07).

Lê `executor_contract` do workflow-rules.yaml real, roda cada saída de
máquina declarada sobre fixtures e valida contra o esquema declarado. Se
algo declarado ali quebrar, este teste reprova o CI do kit.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES = REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
SCRIPTS = REPO_ROOT / "_framework" / "scripts"
PROCEDURE = REPO_ROOT / "_framework" / "procedures" / "verify-sdd.md"


def contrato(rules_path: Path = RULES) -> dict:
    return yaml.safe_load(rules_path.read_text(encoding="utf-8"))["executor_contract"]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def entradas(tmp_path) -> dict:
    """Valor de cada marcador `<...>` usado em `machine_outputs[].args`."""
    sdd = tmp_path / "docs" / "sdd" / "SDD-X-0001.md"
    sdd.parent.mkdir(parents=True)
    sdd.write_text(
        '---\nid: SDD-X-0001\ntype: SDD\ntitle: "s"\nstatus: approved\nsource_docs: []\n---\n\n'
        "# s\n\n## Decomposição em tasks\n\n| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |\n"
        "|---|---|---|---|---|\n| 1 | t | RF01 | a.py | |\n",
        encoding="utf-8",
    )
    (sdd.parent / "registry.yaml").write_text(
        'project: "X"\nframework_version: "2.4.0"\ndocuments:\n  - id: SDD-X-0001\n    type: SDD\n    title: "s"\n'
        '    status: approved\n    owner: "o"\n    created: "2026-11-16"\n    updated: "2026-11-16"\n'
        '    relates_to: []\n    path: "SDD-X-0001.md"\n',
        encoding="utf-8",
    )
    central = tmp_path / "central"
    central.mkdir()
    (central / "registry.yaml").write_text("documents: []\n", encoding="utf-8")
    mensagem = tmp_path / "MSG"
    mensagem.write_text("docs: mensagem no formato\n\nRefs: SDD-X-0001\n", encoding="utf-8")
    corpo = tmp_path / "PR_BODY"
    corpo.write_text("", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "-c", "user.email=t@e", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "base")
    sha = _git(tmp_path, "rev-parse", "HEAD")
    return {
        "cwd": tmp_path,
        "<documento>": str(sdd),
        "<sdd>": str(sdd),
        "<docs_dir>": str(sdd.parent),
        "<central_docs_dir>": str(central),
        "<mensagem_de_commit>": str(mensagem),
        "<base>": sha,
        "<head>": sha,
        "<project_code>": "X",
        "<pr_body_file>": str(corpo),
    }


def test_contract_version_e_campos():
    c = contrato()
    assert isinstance(c["contract_version"], int) and c["contract_version"] >= 1
    for chave in ("reads", "machine_outputs", "writes"):
        assert c[chave], chave


def test_reads_existem_no_yaml():
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    faltando = [k for k in contrato()["reads"] if k not in rules]
    assert faltando == [], f"chaves de reads ausentes do YAML: {faltando}"


def test_esquemas_declarados_existem_e_sao_validos():
    for saida in contrato()["machine_outputs"]:
        caminho = REPO_ROOT / saida["schema"]
        assert caminho.is_file(), f"esquema inexistente: {saida['schema']}"
        Draft202012Validator.check_schema(json.loads(caminho.read_text(encoding="utf-8")))


def test_saidas_declaradas_validam_contra_o_esquema(entradas):
    saidas = contrato()["machine_outputs"]
    assert {s["script"] for s in saidas} >= {
        "validate_doc.py",
        "validate_state.py",
        "check_source_docs.py",
        "registry_tools.py",
        "check_commit.py",
        "ci_gate_verify_sdd.py",
        "parallel_plan.py",
    }
    for saida in saidas:
        script = SCRIPTS / saida["script"]
        assert script.is_file(), f"script inexistente: {saida['script']}"
        args = [entradas.get(a, a) for a in saida["args"]]
        assert not [a for a in args if re.fullmatch(r"<[^>]+>", a)], f"marcador sem valor em {saida['script']}"
        resultado = subprocess.run(
            [sys.executable, str(script), *args], cwd=entradas["cwd"], capture_output=True, text=True
        )
        try:
            objeto = json.loads(resultado.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"{saida['script']} não emitiu JSON: {resultado.stdout[:300]!r} {resultado.stderr[:300]!r}")
        schema = json.loads((REPO_ROOT / saida["schema"]).read_text(encoding="utf-8"))
        erros = [e.message for e in Draft202012Validator(schema).iter_errors(objeto)]
        assert erros == [], f"{saida['script']}: {erros}"


def test_exemplo_do_m4_valida_contra_o_esquema():
    texto = PROCEDURE.read_text(encoding="utf-8")
    m4 = texto[texto.index("**M4.") :]
    bloco = re.search(r"```json\n(.*?)\n```", m4, re.DOTALL)
    assert bloco, "M4 sem exemplo em bloco json"
    schema_path = "_framework/schemas/resultado-verificacao.schema.json"
    schema = json.loads((REPO_ROOT / schema_path).read_text(encoding="utf-8"))
    assert [e.message for e in Draft202012Validator(schema).iter_errors(json.loads(bloco.group(1)))] == []


def test_entrega_e_arquivo_declarados():
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    assert rules["repository_topology"]["project_repo"]["delivered"] == "docs/sdd/arquivo/"
    assert "entrega" in rules["registry"]["optional_entry_fields"]


def test_sensor_reads_pega_chave_renomeada(tmp_path):
    """Sensor de discriminação do teste acima, sobre uma cópia do YAML."""
    texto = RULES.read_text(encoding="utf-8").replace("\nsizing:\n", "\nsizing_renomeado:\n", 1)
    copia = tmp_path / "workflow-rules.yaml"
    copia.write_text(texto, encoding="utf-8")
    rules = yaml.safe_load(texto)
    assert [k for k in contrato(copia)["reads"] if k not in rules] == ["sizing"]


def test_chaves_do_contrato_sao_as_da_spec():
    """SPEC-DTF-0028 declara exatamente estas chaves; campo novo exige emendar a SPEC antes."""
    assert set(contrato()) == {"contract_version", "description", "reads", "machine_outputs", "writes"}
    assert all(set(s) == {"script", "args", "schema"} for s in contrato()["machine_outputs"])


def test_campos_da_verificacao_sao_os_da_spec():
    schema = json.loads(
        (REPO_ROOT / "_framework/schemas/resultado-verificacao.schema.json").read_text(encoding="utf-8")
    )
    assert (
        set(schema["required"])
        == set(schema["properties"])
        == {
            "status",
            "causa",
            "criterios",
            "evidencias",
            "descompassos",
        }
    )
    assert set(schema["properties"]["criterios"]["items"]["required"]) == {
        "numero",
        "comando",
        "saida",
        "sensor",
        "passou",
        "assertion",
        "perfil",
    }
