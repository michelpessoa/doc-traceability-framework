"""Testes de validate_state.py — ver SDD-DTF-0018.

Usa o workflow-rules.yaml real: as datas do changelog (1.7.0 em
2026-08-29) são histórico fixo, não mudam com o tempo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate_state import check_sdd, table_rows  # noqa: E402

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


def test_bloco_cercado_com_pipe_nao_conta_como_linha_de_tabela():
    """SDD-DTF-0024: uma linha de continuação de comando shell dentro de um
    bloco cercado (ex.: `  | grep -c ...`) começa com `|` mas não é linha
    de tabela markdown — não pode inflar a contagem de critérios."""
    section = (
        HEADER_5
        + "| 1 | `pytest` | 3 passed | teste reintroduzido | sim |\n"
        + "\n"
        + "Bloco fora da tabela porque usa pipe de shell:\n\n"
        + "```bash\n"
        + "python3 script.py --report-only |\n"
        + "  | grep -c -e algo\n"
        + "```\n"
    )
    assert table_rows(section) == [["1", "`pytest`", "3 passed", "teste reintroduzido", "sim"]]


def test_bloco_cercado_nao_gera_descompasso_criterios_x_evidencia(tmp_path):
    """Mesma situação, mas fim a fim: 1 critério de aceite e 1 linha de
    evidência real não deve reprovar por 'critérios vs linhas' mesmo com um
    bloco cercado contendo `|` dentro da seção de evidência."""
    table = (
        HEADER_5
        + "| 1 | `pytest` | 3 passed | teste reintroduzido | sim |\n"
        + "\n```bash\npython3 script.py --report-only |\n  | grep -c -e algo\n```\n"
    )
    problems = _with_evidence(tmp_path, table)
    assert not any("critério(s) de aceite mas só" in p for p in problems)


def test_tabela_real_depois_de_bloco_cercado_fechado_e_contada():
    """SDD-DTF-0028: linha de tabela real que vem DEPOIS de um bloco
    cercado já fechado precisa ser contada. Discrimina a mutação M2
    (fazer `in_fence` nunca voltar a `False` — uma cerca de abertura
    que nunca "fecha" de verdade no parser): com essa mutação, toda
    linha depois da abertura do bloco cercado, inclusive uma tabela real
    mais adiante, seria ignorada e `table_rows` devolveria menos linhas
    do que devia."""
    section = (
        HEADER_5
        + "| 1 | `pytest` | 3 passed | teste reintroduzido | sim |\n"
        + "\nBloco fora da tabela porque usa pipe de shell:\n\n"
        + "```bash\n"
        + "python3 script.py --report-only |\n"
        + "  | grep -c -e algo\n"
        + "```\n"
        + "\n"
        + "| 2 | `pytest -k outro` | 5 passed | segunda evidência | sim |\n"
    )
    assert table_rows(section) == [
        ["1", "`pytest`", "3 passed", "teste reintroduzido", "sim"],
        ["2", "`pytest -k outro`", "5 passed", "segunda evidência", "sim"],
    ]


def test_nenhum_validador_chama_rule_applies_direto():
    offenders = [
        p.name
        for p in sorted(SCRIPTS_DIR.glob("*.py"))
        if p.name != "framework_lib.py" and "rule_applies(" in p.read_text(encoding="utf-8")
    ]
    assert offenders == []
