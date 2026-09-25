"""Testes de parallel_plan.py — ver SDD-DTF-0030 (RF03, RF04, RF05)."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from parallel_plan import TaskEntry, derive_groups, files_overlap, parse_tasks  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCRIPT = REPO_ROOT / "_framework" / "scripts" / "parallel_plan.py"


def _entry(label: str, files=None, depends_on=None) -> TaskEntry:
    return TaskEntry(source="t", label=label, files=files or [], depends_on=depends_on or [], key=label)


def test_sem_interseccao_e_paralelizavel():
    a = _entry("a", files=["src/a.py"])
    b = _entry("b", files=["src/b.py"])
    plan = derive_groups([a, b])
    assert plan.blocked_pairs == []
    assert sorted(g[0] for g in plan.parallel_groups) == ["a", "b"] or ["a", "b"] in plan.parallel_groups


def test_interseccao_bloqueia_mesmo_sem_depends_on():
    """RF04: interseção de arquivo força bloqueio mesmo sem depends_on declarado."""
    a = _entry("a", files=["src/shared.py"])
    b = _entry("b", files=["src/shared.py"])
    plan = derive_groups([a, b])
    assert len(plan.blocked_pairs) == 1
    label_a, label_b, files = plan.blocked_pairs[0]
    assert {label_a, label_b} == {"a", "b"}
    assert files == ["src/shared.py"]
    assert not any({"a", "b"} <= set(g) for g in plan.parallel_groups)


def test_depends_on_bloqueia_sem_interseccao_de_arquivo():
    a = _entry("a", files=["src/a.py"])
    b = _entry("b", files=["src/b.py"], depends_on=["a"])
    plan = derive_groups([a, b])
    assert len(plan.blocked_pairs) == 1
    label_a, label_b, files = plan.blocked_pairs[0]
    assert {label_a, label_b} == {"a", "b"}
    assert files == ["depends_on"]


def test_mesmo_rf_arquivos_diferentes_e_paralelizavel():
    """Caso de borda da SPEC-DTF-0010: mesmo RF, arquivos diferentes -> paralelizável."""
    a = _entry("a", files=["src/a.py"])
    b = _entry("b", files=["src/b.py"])
    plan = derive_groups([a, b])
    assert plan.blocked_pairs == []


def test_glob_casa_com_path_exato():
    a = _entry("a", files=["src/**/*.ts"])
    b = _entry("b", files=["src/models/user.ts"])
    assert files_overlap(a.files, b.files)
    plan = derive_groups([a, b])
    assert len(plan.blocked_pairs) == 1


def test_path_inexistente_no_disco_nao_e_erro():
    a = _entry("a", files=["src/nao_existe_no_disco.py"])
    b = _entry("b", files=["src/tambem_nao_existe.py"])
    plan = derive_groups([a, b])  # não faz stat, não levanta exceção
    assert plan.blocked_pairs == []


def test_linha_vazia_gera_aviso():
    """RF05: linha com coluna de arquivos vazia gera aviso e é excluída do cálculo."""
    entries, warnings = parse_tasks(FIXTURES / "sdd_fixture_b.md")
    assert any("Arquivos vazia" in w for w in warnings)
    labels = [e.label for e in entries]
    assert not any("#4" in label for label in labels)


def test_decisao_pura_nao_gera_aviso_e_e_excluida_do_calculo():
    entries, warnings = parse_tasks(FIXTURES / "sdd_fixture_b.md")
    assert not any("#3" in w for w in warnings)
    pura = next(e for e in entries if "#3" in e.label)
    assert pura.files == []


def test_parse_fixture_a_tasks_e_dependencia():
    entries, warnings = parse_tasks(FIXTURES / "sdd_fixture_a.md")
    assert warnings == []
    assert len(entries) == 3
    task3 = next(e for e in entries if "#3" in e.label)
    assert any("#2" in dep for dep in task3.depends_on)


def test_cli_ponta_a_ponta_sem_traceback():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "sdd_fixture_a.md"), str(FIXTURES / "sdd_fixture_b.md")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr
    assert "Grupos paralelizáveis" in result.stdout
    assert "Pares bloqueados" in result.stdout
    # fixture_a#2 e fixture_b#2 colidem em src/shared/utils.py
    assert "shared/utils.py" in result.stdout


def test_cli_json():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "sdd_fixture_a.md"), "--json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    import json

    data = json.loads(result.stdout)
    assert "parallel_groups" in data
    assert "blocked_pairs" in data


def test_pipe_escapado_na_celula_de_task_nao_desloca_arquivos(tmp_path):
    """SDD-DTF-0047 RF06: pipe escapado na célula da task não desloca Arquivos tocados."""
    sdd = tmp_path / "SDD-X-0001.md"
    sdd.write_text(
        "---\nid: SDD-X-0001\ntype: SDD\n---\n\n## Decomposição em tasks\n\n"
        "| # | Task | RF(s) | Arquivos tocados | Depende de (#) |\n|---|---|---|---|---|\n"
        "| 1 | roda `grep a\\|b` | RF01 | src/a.py | |\n"
        "| 2 | outra | RF02 | src/b.py | 1 |\n",
        encoding="utf-8",
    )
    entries, warnings = parse_tasks(sdd)
    assert warnings == []
    assert entries[0].files == ["src/a.py"]
    assert entries[1].depends_on == ["SDD-X-0001.md#1"]
