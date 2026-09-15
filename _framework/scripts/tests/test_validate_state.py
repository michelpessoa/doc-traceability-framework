"""Testes de validate_state.py — ver SDD-DTF-0018.

Usa o workflow-rules.yaml real: as datas do changelog (1.7.0 em
2026-08-29) são histórico fixo, não mudam com o tempo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate_state import check_sdd  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parents[1]

CRITERIA = """## Critérios de aceite / definição de pronto

| # | Critério | Comando | Resultado esperado |
|---|---|---|---|
| 1 | RF1 | `pytest` | exit 0 |
"""

SCOPE_OK = """## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito tem código.
"""

HEADER_5 = "| # | Comando rodado | Saída (resumo) | Sensor | Passou? |\n|---|---|---|---|---|\n"
HEADER_6 = "| # | Critério | Comando | Saída | Sensor | Passou? |\n|---|---|---|---|---|---|\n"


def _sdd(tmp_path: Path, created: str, body: str) -> Path:
    path = tmp_path / "SDD-TST-0001.md"
    path.write_text(
        "---\n"
        "id: SDD-TST-0001\n"
        "type: SDD\n"
        'title: "teste"\n'
        "status: implemented\n"
        f'created: "{created}"\n'
        "---\n\n"
        "# teste\n\n" + body,
        encoding="utf-8",
    )
    return path


def _with_evidence(tmp_path: Path, table: str, created: str = "2026-09-01") -> list:
    body = CRITERIA + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + table
    problems, _ = check_sdd(_sdd(tmp_path, created, body), version="2.1.0")
    return problems


def _assumed(problems: list) -> list:
    return [p for p in problems if "resultado assumido" in p]


def test_legado_antes_da_regra_nao_reprova(tmp_path):
    problems, _ = check_sdd(_sdd(tmp_path, "2026-08-25", CRITERIA), version="2.1.0")
    assert problems == []


def test_criada_depois_da_regra_reprova(tmp_path):
    problems, _ = check_sdd(_sdd(tmp_path, "2026-09-01", CRITERIA), version="2.1.0")
    assert any("Evidência de verificação" in p for p in problems)


def test_mesmo_dia_da_regra_reprova(tmp_path):
    problems = _with_evidence(tmp_path, HEADER_5, created="2026-08-29")
    assert any("está vazia" in p for p in problems)


def test_na_no_sensor_nao_reprova(tmp_path):
    table = HEADER_5 + "| 1 | `pytest` | 3 passed | n/a (checagem estática) | sim |\n"
    assert _assumed(_with_evidence(tmp_path, table)) == []


def test_na_na_saida_reprova(tmp_path):
    table = HEADER_5 + "| 1 | `pytest` | n/a | teste reintroduzido | sim |\n"
    assert _assumed(_with_evidence(tmp_path, table))


def test_na_no_passou_reprova(tmp_path):
    table = HEADER_5 + "| 1 | `pytest` | 3 passed | teste reintroduzido | n/a |\n"
    assert _assumed(_with_evidence(tmp_path, table))


def test_tabela_seis_colunas_comando_vazio(tmp_path):
    table = HEADER_6 + "| 1 | RF1 |  | 3 passed | teste reintroduzido | sim |\n"
    problems = _with_evidence(tmp_path, table)
    assert any("sem comando rodado" in p for p in problems)


def test_tabela_seis_colunas_ok(tmp_path):
    table = HEADER_6 + "| 1 | RF1 | `pytest` | 3 passed | teste reintroduzido | sim |\n"
    assert _with_evidence(tmp_path, table) == []


def test_sem_cabecalho_reconhecivel_linha_inteira(tmp_path):
    table = "| a | b | c |\n|---|---|---|\n| 1 | `pytest` | n/a |\n"
    assert _assumed(_with_evidence(tmp_path, table))


def test_nenhum_validador_chama_rule_applies_direto():
    offenders = [
        p.name
        for p in sorted(SCRIPTS_DIR.glob("*.py"))
        if p.name != "framework_lib.py" and "rule_applies(" in p.read_text(encoding="utf-8")
    ]
    assert offenders == []
