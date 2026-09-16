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


def _spec(arquivos_cell: str) -> str:
    return (
        SPEC_FRONTMATTER
        + f"""
## Objetivo
Teste.

## Requisitos funcionais
| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |
|---|---|---|---|
| RF01 | Algo | O sistema deve fazer algo | {arquivos_cell} |

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
