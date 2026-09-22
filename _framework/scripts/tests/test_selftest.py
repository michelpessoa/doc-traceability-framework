"""Testes de selftest.py — ver SDD-DTF-0038 (SPEC-DTF-0015)."""

import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from selftest import KIT_ROOT, apply_mutation, run_mutation  # noqa: E402

MUTATIONS_PATH = Path(__file__).resolve().parent / "mutations.yaml"
VALIDATORS = {"validate_state.py", "check_commit.py", "check_hooks.py", "check_source_docs.py"}


def _fixture_validator(tmp_path: Path, body: str) -> Path:
    target = tmp_path / "fake_validator.py"
    target.write_text(textwrap.dedent(body), encoding="utf-8")
    return target


def _fixture_test(tmp_path: Path, body: str) -> Path:
    test_file = tmp_path / "test_fake_validator.py"
    test_file.write_text(textwrap.dedent(body), encoding="utf-8")
    return test_file


FIXTURE_VALIDATOR = """\
    def check(value):
        if value == "bad":
            return ["problema"]
        return []
    """

FIXTURE_TEST_DISCRIMINA = """\
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fake_validator import check

    def test_bad_reprova():
        assert check("bad") == ["problema"]
    """

FIXTURE_TEST_NAO_DISCRIMINA = """\
    def test_sempre_passa():
        assert True
    """


def test_mutations_yaml_cobre_os_4_validadores_com_5_campos():
    mutations = yaml.safe_load(MUTATIONS_PATH.read_text(encoding="utf-8"))
    assert mutations
    covered = set()
    for mutation in mutations:
        assert set(mutation) == {"validator", "test_file", "description", "find", "replace"}
        covered.add(Path(mutation["validator"]).name)
    assert VALIDATORS <= covered


def test_apply_mutation_retorna_original_e_escreve_replace(tmp_path):
    target = _fixture_validator(tmp_path, FIXTURE_VALIDATOR)
    original = target.read_text(encoding="utf-8")
    returned = apply_mutation(target, 'value == "bad"', "False")
    assert returned == original
    assert "False" in target.read_text(encoding="utf-8")


def test_apply_mutation_find_ausente_levanta_erro(tmp_path):
    target = _fixture_validator(tmp_path, FIXTURE_VALIDATOR)
    try:
        apply_mutation(target, "inexistente_no_arquivo", "x")
        assert False, "deveria ter levantado ValueError"
    except ValueError as exc:
        assert "inexistente_no_arquivo" in str(exc)
    assert "inexistente_no_arquivo" not in target.read_text(encoding="utf-8")


def test_run_mutation_mutante_morto_reverte_arquivo(tmp_path):
    target = _fixture_validator(tmp_path, FIXTURE_VALIDATOR)
    test_file = _fixture_test(tmp_path, FIXTURE_TEST_DISCRIMINA)
    original = target.read_text(encoding="utf-8")
    mutation = {
        "validator": str(target.relative_to(tmp_path)),
        "test_file": str(test_file.relative_to(tmp_path)),
        "find": 'value == "bad"',
        "replace": "False",
    }
    outcome = run_mutation(mutation, tmp_path)
    assert outcome == {"survived": False, "error": None}
    assert target.read_text(encoding="utf-8") == original


def test_run_mutation_mutante_sobrevivente(tmp_path):
    target = _fixture_validator(tmp_path, FIXTURE_VALIDATOR)
    test_file = _fixture_test(tmp_path, FIXTURE_TEST_NAO_DISCRIMINA)
    mutation = {
        "validator": str(target.relative_to(tmp_path)),
        "test_file": str(test_file.relative_to(tmp_path)),
        "find": 'value == "bad"',
        "replace": "False",
    }
    outcome = run_mutation(mutation, tmp_path)
    assert outcome == {"survived": True, "error": None}


def test_run_mutation_find_ausente_reporta_erro_nao_sobrevivente(tmp_path):
    target = _fixture_validator(tmp_path, FIXTURE_VALIDATOR)
    test_file = _fixture_test(tmp_path, FIXTURE_TEST_DISCRIMINA)
    mutation = {
        "validator": str(target.relative_to(tmp_path)),
        "test_file": str(test_file.relative_to(tmp_path)),
        "find": "nao_existe_nesse_arquivo",
        "replace": "x",
    }
    outcome = run_mutation(mutation, tmp_path)
    assert outcome["survived"] is False
    assert outcome["error"] is not None
    assert "nao_existe_nesse_arquivo" in outcome["error"]


def test_run_mutation_validator_inexistente_reporta_erro(tmp_path):
    mutation = {
        "validator": "nao_existe.py",
        "test_file": "tambem_nao.py",
        "find": "x",
        "replace": "y",
    }
    outcome = run_mutation(mutation, tmp_path)
    assert outcome["survived"] is False
    assert "inexistente" in outcome["error"]


def test_cli_exit_0_quando_todos_mutantes_morrem():
    result = subprocess.run(
        [sys.executable, str(KIT_ROOT / "_framework/scripts/selftest.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_exit_nao_zero_quando_mutante_sobrevive(tmp_path):
    """Sensor de discriminação real (RF02/RF04): copia mutations.yaml real,
    neutraliza uma entrada (replace == find, mutação vira no-op), confirma
    que selftest.py reporta o mutante como sobrevivente e sai != 0."""
    mutations = yaml.safe_load(MUTATIONS_PATH.read_text(encoding="utf-8"))
    mutations[0]["replace"] = mutations[0]["find"]
    broken = tmp_path / "mutations.yaml"
    broken.write_text(yaml.safe_dump(mutations), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(KIT_ROOT / "_framework/scripts/selftest.py"), str(broken)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "SOBREVIVEU" in result.stdout
