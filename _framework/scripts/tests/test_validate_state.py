"""Testes de validate_state.py — ver SDD-DTF-0018.

Usa o workflow-rules.yaml real: as datas do changelog (1.7.0 em
2026-08-29) são histórico fixo, não mudam com o tempo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate_state import check_sdd, check_source_fidelity, check_verification_rounds, table_rows  # noqa: E402

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


HEADER_RODADA = "| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? |\n|---|---|---|---|---|---|\n"


def test_tres_rodadas_sem_escalonamento_reprova(tmp_path):
    table = HEADER_RODADA + (
        "| 1 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
        "| 2 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
        "| 3 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
    )
    problems = _with_evidence(tmp_path, table)
    assert any("teto de 3 rodadas" in p for p in problems)


def test_tres_rodadas_com_escalonamento_passa(tmp_path):
    body = (
        CRITERIA
        + "\n"
        + SCOPE_OK
        + "\n## Evidência de verificação\n\n"
        + HEADER_RODADA
        + "| 1 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
        + "| 2 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
        + "| 3 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
        + "\n## Escalonado ao humano\n"
        + "Rodadas tentadas: 3. Veredito de cada uma: FAIL, FAIL, FAIL.\n"
        + "Motivo de cada falha: resumo.\n"
    )
    problems, _ = check_sdd(_sdd(tmp_path, "2026-09-01", body), version="2.1.0")
    assert not any("teto de 3 rodadas" in p for p in problems)


def test_duas_rodadas_sem_escalonamento_passa(tmp_path):
    table = HEADER_RODADA + (
        "| 1 | 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
        "| 2 | 1 | `pytest` | 3 passed | teste reintroduzido | Sim |\n"
    )
    problems = _with_evidence(tmp_path, table)
    assert not any("teto de 3 rodadas" in p for p in problems)


def test_tabela_sem_coluna_rodada_trata_como_unica(tmp_path):
    table = HEADER_5 + "| 1 | `pytest` | 1 failed | teste reintroduzido | Não |\n"
    problems = _with_evidence(tmp_path, table)
    assert not any("teto de 3 rodadas" in p for p in problems)


def test_check_verification_rounds_sem_evidencia():
    assert check_verification_rounds("SDD-TST-0001", None, "") == []


def test_sensor_vazio_reprova(tmp_path):
    """STRAT-DTF-0003 item A: coluna Sensor vazia é evidência assumida,
    igual a 'n/a' na saída — declare o resultado ou 'sem teste
    automatizado', célula em branco não."""
    table = HEADER_5 + "| 1 | `pytest` | 1 passed |  | Sim |\n"
    problems = _with_evidence(tmp_path, table)
    assert any("'Sensor' vazia" in p for p in problems)


def test_sensor_sem_teste_automatizado_e_valido(tmp_path):
    table = HEADER_5 + "| 1 | `grep -n foo bar.md` | sem saída | sem teste automatizado | Sim |\n"
    problems = _with_evidence(tmp_path, table)
    assert not any("'Sensor' vazia" in p for p in problems)


def test_tabela_sem_coluna_sensor_nao_reprova_retroativamente(tmp_path):
    """Tabela de 4 colunas (sem Sensor) é o formato anterior a esta
    convenção — a ausência da coluna não é reprovada, só a presença
    vazia."""
    header_sem_sensor = "| # | Comando rodado | Saída (resumo) | Passou? |\n|---|---|---|---|\n"
    table = header_sem_sensor + "| 1 | `pytest` | 1 passed | Sim |\n"
    problems = _with_evidence(tmp_path, table)
    assert not any("Sensor" in p for p in problems)


CRITERIA_PERFIL_AUTOMATIZADO = """## Critérios de aceite / definição de pronto

| # | Critério | Comando | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF1 | `pytest` | exit 0 | automatizado |
"""

CRITERIA_PERFIL_MANUAL = """## Critérios de aceite / definição de pronto

| # | Critério | Comando | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF1 | revisão visual | ok | manual |
"""

HEADER_PERFIL = (
    "| # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |\n"
    "|---|---|---|---|---|---|---|\n"
)


def _with_criteria_and_evidence(tmp_path: Path, criteria: str, table: str, created: str = "2026-09-01") -> list:
    body = criteria + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + table
    problems, _ = check_sdd(_sdd(tmp_path, created, body), version="2.1.0")
    return problems


def test_perfil_automatizado_sem_assertion_reprova(tmp_path):
    """STRAT-DTF-0003 item 7/E4: perfil automatizado sem file:line da
    asserção não prova que o comando testa o valor certo."""
    table = HEADER_PERFIL + "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim |  | automatizado |\n"
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_PERFIL_AUTOMATIZADO, table)
    assert any("Assertion (file:line)' vazia" in p for p in problems)


def test_perfil_automatizado_com_assertion_passa(tmp_path):
    table = HEADER_PERFIL + "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim | test_foo.py:42 | automatizado |\n"
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_PERFIL_AUTOMATIZADO, table)
    assert problems == []


def test_perfil_divergente_sem_justificativa_reprova(tmp_path):
    """STRAT-DTF-0003 item 7/E5: trocar automatizado por manual sem
    justificar é o que esta checagem pega."""
    table = HEADER_PERFIL + "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim | test_foo.py:42 | manual |\n"
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_PERFIL_AUTOMATIZADO, table)
    assert any("'Perfil usado'" in p and "divergente" in p for p in problems)


def test_perfil_divergente_com_justificativa_passa(tmp_path):
    table = HEADER_PERFIL + (
        "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim | n/a | "
        "manual (motivo: sensor de mutação incompatível com CI atual) |\n"
    )
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_PERFIL_AUTOMATIZADO, table)
    assert not any("divergente" in p for p in problems)


def test_perfil_manual_nao_exige_assertion(tmp_path):
    """Célula 'Assertion' de fato vazia (não 'n/a' literal) — sensor real:
    sem a guarda `esperado == "automatizado"`, esta linha reprovaria."""
    table = HEADER_PERFIL + "| 1 | revisão visual | ok | n/a | Sim |  | manual |\n"
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_PERFIL_MANUAL, table)
    assert problems == []


def test_sem_colunas_novas_nao_reprova_retroativamente(tmp_path):
    """Evidência no formato anterior a esta SDD (sem Assertion/Perfil
    usado) não é afetada — não retroativo por construção."""
    table = HEADER_5 + "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim |\n"
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_PERFIL_AUTOMATIZADO, table)
    assert not any("Assertion" in p or "Perfil" in p for p in problems)


HEADER_PERFIL_COM_RODADA = (
    "| Rodada | # | Comando rodado | Saída (resumo) | Sensor | Passou? | Assertion (file:line) | Perfil usado |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def test_evidencia_com_coluna_rodada_usa_numero_certo_do_criterio(tmp_path):
    """Achado real, rodada 2 de verificação de SDD-DTF-0036: com a coluna
    'Rodada' antes de '#', ler '#' pela posição 0 lê o número da rodada,
    não do critério — critério #2 numa rodada #1 seria comparado por
    engano contra o 'Perfil esperado' do critério #1. Aqui o critério #1
    é `manual` e o #2 é `automatizado`; a linha da rodada 1 do critério
    #2 tem perfil usado `automatizado` (bate com o #2, reprovaria por
    engano contra o #1 se a coluna 'Rodada' fosse lida como '#')."""
    criteria = (
        "## Critérios de aceite / definição de pronto\n\n"
        "| # | Critério | Comando | Resultado esperado | Perfil esperado |\n"
        "|---|---|---|---|---|\n"
        "| 1 | RF1 | `revisão` | ok | manual |\n"
        "| 2 | RF2 | `pytest` | exit 0 | automatizado |\n"
    )
    table = HEADER_PERFIL_COM_RODADA + (
        "| 1 | 1 | `revisão` | ok | sem teste automatizado | Sim | n/a | manual |\n"
        "| 1 | 2 | `pytest` | 1 passed | teste reintroduzido | Sim | test_foo.py:10 | automatizado |\n"
    )
    problems = _with_criteria_and_evidence(tmp_path, criteria, table)
    assert not any("Perfil usado" in p or "Assertion" in p for p in problems)


def test_criterios_sem_coluna_perfil_esperado_nao_reprova(tmp_path):
    """SDD anterior a esta convenção, sem 'Perfil esperado' nos
    critérios — sem valor esperado, não há o que comparar."""
    table = HEADER_PERFIL + "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim |  | automatizado |\n"
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA, table)
    assert not any("Assertion" in p or "Perfil" in p for p in problems)


def _sdd_com_source_docs(tmp_path: Path, created: str, source_docs_yaml: str, body: str) -> Path:
    path = tmp_path / "SDD-TST-0002.md"
    path.write_text(
        "---\n"
        "id: SDD-TST-0002\n"
        "type: SDD\n"
        'title: "teste"\n'
        "status: implemented\n"
        f'created: "{created}"\n' + source_docs_yaml + "\n---\n\n# teste\n\n" + body,
        encoding="utf-8",
    )
    return path


SOURCE_DOCS_YAML = 'source_docs:\n  - id: "SPEC-DTF-0014"\n    url: "https://x/SPEC-DTF-0014.md"\n'

EVIDENCE_COM_FIDELIDADE = HEADER_5 + (
    "| Fidelidade à origem | check_source_docs.py SDD-TST-0002.md central/ | "
    "RF01-06 representados, nenhum critério relaxado | sem teste automatizado | Sim |\n"
    "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim |\n"
)
EVIDENCE_SEM_FIDELIDADE = HEADER_5 + "| 1 | `pytest` | 1 passed | teste reintroduzido | Sim |\n"


def test_check_source_fidelity_unit_source_docs_vazio_nao_reprova():
    assert check_source_fidelity("SDD-TST-0002", [], EVIDENCE_SEM_FIDELIDADE) == []


def test_check_source_fidelity_unit_evidence_none_nao_reprova():
    assert check_source_fidelity("SDD-TST-0002", [{"id": "SPEC-DTF-0014"}], None) == []


def test_check_source_fidelity_unit_com_linha_fidelidade_passa():
    problems = check_source_fidelity("SDD-TST-0002", [{"id": "SPEC-DTF-0014"}], EVIDENCE_COM_FIDELIDADE)
    assert problems == []


def test_check_source_fidelity_unit_sem_linha_fidelidade_reprova():
    problems = check_source_fidelity("SDD-TST-0002", [{"id": "SPEC-DTF-0014"}], EVIDENCE_SEM_FIDELIDADE)
    assert any("Fidelidade à origem" in p for p in problems)


def test_rf04_via_check_sdd_created_depois_da_regra_sem_linha_reprova(tmp_path):
    """`created` estritamente posterior a 2026-09-22 (data da versão
    2.2.0, RULE_SINCE['source_fidelity']) — regra se aplica."""
    body = CRITERIA + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + EVIDENCE_SEM_FIDELIDADE
    sdd = _sdd_com_source_docs(tmp_path, "2026-09-23", SOURCE_DOCS_YAML, body)
    problems, _ = check_sdd(sdd, version="2.2.0")
    assert any("Fidelidade à origem" in p for p in problems)


def test_rf04_via_check_sdd_created_depois_da_regra_com_linha_passa(tmp_path):
    body = CRITERIA + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + EVIDENCE_COM_FIDELIDADE
    sdd = _sdd_com_source_docs(tmp_path, "2026-09-23", SOURCE_DOCS_YAML, body)
    problems, _ = check_sdd(sdd, version="2.2.0")
    assert not any("Fidelidade à origem" in p for p in problems)


def test_rf05_source_docs_vazio_nao_exige_linha(tmp_path):
    body = CRITERIA + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + EVIDENCE_SEM_FIDELIDADE
    sdd = _sdd_com_source_docs(tmp_path, "2026-09-23", "source_docs: []\n", body)
    problems, _ = check_sdd(sdd, version="2.2.0")
    assert not any("Fidelidade à origem" in p for p in problems)


def test_rf06_created_no_mesmo_dia_da_regra_nao_reprova_retroativamente(tmp_path):
    """SDD-DTF-0036 foi criada em 2026-09-22, mesmo dia da versão 2.2.0
    (RULE_SINCE['source_fidelity']) — sensor real do achado que motivou
    `applies_strict` (>, não >=): sem a comparação estrita, esta SDD
    (criada no mesmo dia) seria reprovada retroativamente."""
    body = CRITERIA + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + EVIDENCE_SEM_FIDELIDADE
    sdd = _sdd_com_source_docs(tmp_path, "2026-09-22", SOURCE_DOCS_YAML, body)
    problems, _ = check_sdd(sdd, version="2.2.0")
    assert not any("Fidelidade à origem" in p for p in problems)


def test_rf06_created_antes_da_regra_nao_reprova(tmp_path):
    body = CRITERIA + "\n" + SCOPE_OK + "\n## Evidência de verificação\n\n" + EVIDENCE_SEM_FIDELIDADE
    sdd = _sdd_com_source_docs(tmp_path, "2026-09-01", SOURCE_DOCS_YAML, body)
    problems, _ = check_sdd(sdd, version="2.2.0")
    assert not any("Fidelidade à origem" in p for p in problems)


def test_nenhum_validador_chama_rule_applies_direto():
    offenders = [
        p.name
        for p in sorted(SCRIPTS_DIR.glob("*.py"))
        if p.name != "framework_lib.py" and "rule_applies(" in p.read_text(encoding="utf-8")
    ]
    assert offenders == []


CRITERIA_ESCAPADO = """## Critérios de aceite / definição de pronto

| # | Critério | Comando | Resultado esperado | Perfil esperado |
|---|---|---|---|---|
| 1 | RF1 | `grep -E 'a\\|b' f` | exit 0 | automatizado |
"""


def test_pipe_escapado_nao_desloca_perfil_esperado():
    """SDD-DTF-0047 RF04: pipe escapado no comando não desloca colunas."""
    from validate_state import table_with_header

    header, rows = table_with_header(CRITERIA_ESCAPADO)
    idx = next(i for i, h in enumerate(header) if "perfil esperado" in h)
    assert rows[0][idx] == "automatizado"
    assert rows[0][2] == "`grep -E 'a|b' f`"


def test_check_sdd_pipe_escapado_em_comando_nao_reprova(tmp_path):
    table = HEADER_PERFIL + (
        "| 1 | `grep -E 'a\\|b' f` | 1 passed | teste reintroduzido | Sim | test_foo.py:42 | automatizado |\n"
    )
    problems = _with_criteria_and_evidence(tmp_path, CRITERIA_ESCAPADO, table)
    assert problems == []
