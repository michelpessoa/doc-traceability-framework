"""Testes de validate_doc.py (RF06, RF07) — ver SDD-DTF-0030."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_doc import check_document  # noqa: E402

SPEC_FRONTMATTER = """---
id: SPEC-TEST-0001
type: SPEC
title: "Teste"
status: draft
project: "TEST"
owner: "Teste"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: []
parent_rfc: null
parent_adr: null
sizing: "medium"
supersedes: null
superseded_by: null
tags: []
---
"""

SDD_FRONTMATTER_TEMPLATE = """---
id: SDD-TEST-0001
type: SDD
title: "Teste"
status: draft
project: "TEST"
owner: "Teste"
created: "2026-09-15"
updated: "2026-09-15"
relates_to: []
source_docs: []
consumption_instructions: "fixture de teste"
supersedes: null
superseded_by: null
tags: []
{sizing}
---
"""


SWEEP_TABLE_COMPLETA = """
## Requisitos transversais (sweep)
| Categoria | Destino (RF-ID ou n/a) | Motivo (obrigatório se n/a) |
|---|---|---|
| Autorização / permissão | n/a | sem controle de acesso nesta feature |
| Concorrência | RF01 | |
| Idempotência | n/a | operação read-only |
| Observabilidade | n/a | sem log novo |
| Falha de dependência externa | n/a | sem dependência externa |
| Validação de entrada | n/a | sem entrada de usuário |
| Limite de volume / rate | n/a | volume fixo e pequeno |
"""


def _spec(arquivos_cell: str, sweep: str = SWEEP_TABLE_COMPLETA, created: str = "2026-09-22") -> str:
    fm = SPEC_FRONTMATTER.replace('created: "2026-09-15"', f'created: "{created}"')
    return (
        fm
        + f"""
## Objetivo
Teste.

## Requisitos funcionais
| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |
|---|---|---|---|
| RF01 | Algo | O sistema deve fazer algo | {arquivos_cell} |
{sweep}
## Contratos técnicos
`foo.py`

## Estratégia de teste
Teste.

## Fora de escopo
Nada.
"""
    )


def _sdd(rf_ids: list[str], tasks_section: str = "", sizing: str = "") -> str:
    rf_rows = "\n".join(f"| {rf} | fixture |" for rf in rf_ids)
    return (
        SDD_FRONTMATTER_TEMPLATE.format(sizing=sizing)
        + f"""
## Requisitos consolidados
| RF-ID | Requisito |
|---|---|
{rf_rows}
{tasks_section}
## Critérios de aceite / definição de pronto
| # | Critério | Comando | Resultado |
|---|---|---|---|
"""
    )


def test_gate_arquivos_vazio_falha(tmp_path):
    path = tmp_path / "spec.md"
    path.write_text(_spec(""), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("Arquivos vazia" in p and "RF06" in p for p in problems)


def test_ears_nao_confunde_coluna_arquivos_com_criterio(tmp_path):
    """Regressão: check_ears usava cells[-1] como critério, que virou a
    coluna Arquivos (SDD-DTF-0030) em vez do critério real (cells[2])."""
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`"), encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("não está em EARS" in p for p in problems)


def test_ears_ainda_pega_criterio_malformado_com_coluna_arquivos(tmp_path):
    """Sensor: com critério real quebrado (sem 'deve'), o problema tem que
    aparecer citando o critério, não o conteúdo da coluna Arquivos."""
    path = tmp_path / "spec.md"
    broken = SPEC_FRONTMATTER + (
        "\n## Objetivo\nTeste.\n\n## Requisitos funcionais\n"
        "| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |\n"
        "|---|---|---|---|\n"
        "| RF01 | Algo | falta o verbo de obrigação | `caminho/qualquer.py` |\n"
        "\n## Contratos técnicos\n`foo.py`\n\n## Estratégia de teste\nTeste.\n"
        "\n## Fora de escopo\nNada.\n"
    )
    path.write_text(broken, encoding="utf-8")
    problems, _ = check_document(path)
    matches = [p for p in problems if "não está em EARS" in p and "RF01" in p]
    assert matches, problems
    assert "falta o verbo de obrigação" in matches[0]
    assert "caminho/qualquer.py" not in matches[0]


def test_arquivos_decisao_pura_nao_falha_spec(tmp_path):
    path = tmp_path / "spec.md"
    path.write_text(_spec("(decisão pura)"), encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("RF06" in p for p in problems)


def test_gate_arquivos_vazio_falha_sdd(tmp_path):
    tasks = (
        "\n## Decomposição em tasks\n"
        "| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |\n"
        "|---|---|---|---|---|\n"
        "| 1 | foo | RF01 |  | |\n"
    )
    path = tmp_path / "sdd.md"
    path.write_text(_sdd(["RF01", "RF02"], tasks_section=tasks), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("Arquivos vazia" in p and "RF06" in p for p in problems)


def test_gate_dispensa_tasks_sizing_small(tmp_path):
    """RF07: sizing small dispensa a seção 'Decomposição em tasks' mesmo com >1 RF."""
    path = tmp_path / "sdd.md"
    path.write_text(_sdd(["RF01", "RF02", "RF03"], sizing='sizing: "small"'), encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("RF07" in p for p in problems)


def test_gate_dispensa_tasks_rf_unico(tmp_path):
    """RF07: um único RF consolidado dispensa a seção, mesmo sem sizing declarado."""
    path = tmp_path / "sdd.md"
    path.write_text(_sdd(["RF01"]), encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("RF07" in p for p in problems)


def test_gate_tasks_ausente_sem_dispensa_falha(tmp_path):
    path = tmp_path / "sdd.md"
    path.write_text(_sdd(["RF01", "RF02"]), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("RF07" in p for p in problems)


def test_gate_nao_retroativo_para_sdd_ja_implementada(tmp_path):
    """SDD já implementada (fora de draft/in_review) não é reprovada retroativamente."""
    text = _sdd(["RF01", "RF02"]).replace("status: draft", "status: implemented")
    path = tmp_path / "sdd.md"
    path.write_text(text, encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("RF07" in p for p in problems)


def test_vocabulario_vago_reprova_documento_approved(tmp_path):
    """STRAT-DTF-0003 item G: 'gracefully' etc. são placeholder tanto
    quanto 'TBD' — descrevem o resultado desejado sem dizer como
    verificá-lo. Só reprova (problems, não warnings) em status decidido."""
    path = tmp_path / "spec.md"
    text = _spec("`caminho/qualquer.py`").replace(
        "O sistema deve fazer algo", "O sistema deve tratar o erro gracefully"
    ).replace("status: draft", "status: approved")
    path.write_text(text, encoding="utf-8")
    problems, _ = check_document(path)
    assert any("gracefully" in p for p in problems)


def test_vocabulario_vago_em_draft_e_so_warning(tmp_path):
    path = tmp_path / "spec.md"
    text = _spec("`caminho/qualquer.py`").replace(
        "O sistema deve fazer algo", "O sistema deve tratar o erro gracefully"
    )
    path.write_text(text, encoding="utf-8")
    problems, warnings = check_document(path)
    assert not any("gracefully" in p for p in problems)
    assert any("gracefully" in w for w in warnings)


# STRAT-DTF-0003 item 10 / SDD-DTF-0039: seção "Requisitos transversais (sweep)".


def test_sweep_ausente_falha(tmp_path):
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`", sweep=""), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("Requisitos transversais (sweep)" in p for p in problems)


def test_sweep_completo_passa(tmp_path):
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`"), encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("sweep" in p.lower() for p in problems)


def test_sweep_categoria_faltando_falha(tmp_path):
    """Sensor: remover uma linha da tabela (categoria 'Concorrência') tem
    que ser pego — sem isso o gate não distingue tabela completa de
    tabela parcial."""
    sweep_incompleto = SWEEP_TABLE_COMPLETA.replace("| Concorrência | RF01 | |\n", "")
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`", sweep=sweep_incompleto), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("concorrência" in p.lower() for p in problems)


def test_sweep_destino_vazio_falha(tmp_path):
    sweep = SWEEP_TABLE_COMPLETA.replace("| Concorrência | RF01 | |\n", "| Concorrência |  |  |\n")
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`", sweep=sweep), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("Destino vazia" in p for p in problems)


def test_sweep_na_sem_motivo_falha(tmp_path):
    sweep = SWEEP_TABLE_COMPLETA.replace(
        "| Observabilidade | n/a | sem log novo |\n", "| Observabilidade | n/a | |\n"
    )
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`", sweep=sweep), encoding="utf-8")
    problems, _ = check_document(path)
    assert any("sem motivo" in p for p in problems)


def test_sweep_nao_retroativo_para_spec_antiga(tmp_path):
    """SPEC criada antes de 2026-09-22 (data de introdução da regra) não é
    reprovada por não ter a seção que ainda não existia no template."""
    path = tmp_path / "spec.md"
    path.write_text(_spec("`caminho/qualquer.py`", sweep="", created="2026-09-15"), encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("sweep" in p.lower() for p in problems)


def test_pipe_escapado_em_tabela_de_rf(tmp_path):
    """SDD-DTF-0047 RF05: pipe escapado na célula Requisito não desloca o critério EARS."""
    path = tmp_path / "spec.md"
    text = _spec("`caminho/qualquer.py`").replace("| RF01 | Algo |", "| RF01 | Algo \\| outro |")
    path.write_text(text, encoding="utf-8")
    problems, _ = check_document(path)
    assert not any("não está em EARS" in p for p in problems), problems


def test_pipe_escapado_em_tabela_de_arquivos(tmp_path):
    """SDD-DTF-0047 RF05: com Arquivos vazio e pipe escapado antes, o gate ainda pega."""
    path = tmp_path / "spec.md"
    text = _spec("").replace("| RF01 | Algo |", "| RF01 | Algo \\| outro |")
    path.write_text(text, encoding="utf-8")
    problems, _ = check_document(path)
    assert any("Arquivos vazia" in p and "RF06" in p for p in problems), problems
