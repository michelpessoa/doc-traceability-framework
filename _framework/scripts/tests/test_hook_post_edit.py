"""Testes de hook_post_edit.py — ver SDD-DTF-0020 (RF03).

Roda o script por subprocess com o payload que o Claude Code envia em
PostToolUse, sobre documentos mínimos em tmp_path com registry.yaml.
Usa o workflow-rules.yaml real (datas do changelog são histórico fixo).
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "hook_post_edit.py"

FRONTMATTER = """---
id: {id}
type: {type}
title: "teste"
status: {status}
project: "TST"
owner: "Teste"
created: "{created}"
updated: "{created}"
---

"""

SPEC_DRAFT_BODY = """# teste

## Objetivo

Algo — detalhar depois.

## Requisitos funcionais

| RF-ID | Requisito | Critério de aceite (EARS) |
|---|---|---|
| RF01 | Faz algo | Quando X acontecer, o sistema deve fazer Y. |

## Contratos técnicos

`src/app.py`

## Estratégia de teste

pytest.

## Fora de escopo

Nada.
"""

SDD_BODY = """# teste

## Requisitos consolidados

| RF-ID | Requisito | Critério |
|---|---|---|
| RF01 | Faz algo | Quando X, o sistema deve Y. |

## Critérios de aceite / definição de pronto

| # | Critério | Comando | Resultado esperado |
|---|---|---|---|
| 1 | RF01 | `pytest` | exit 0 |

## Verificação de escopo (nada a mais, nada a menos)

- [x] Todo requisito tem código.

## Evidência de verificação

| # | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
{evidence}"""


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "registry.yaml").write_text('framework_version: "2.1.0"\ndocuments: []\n', encoding="utf-8")
    return tmp_path


def _doc(tmp_path: Path, name: str, content: str) -> Path:
    path = _repo(tmp_path) / name
    path.write_text(content, encoding="utf-8")
    return path


def _run(file_path, stdin: str | None = None) -> subprocess.CompletedProcess:
    if stdin is None:
        stdin = json.dumps(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Edit",
                "tool_input": {"file_path": str(file_path)},
            }
        )
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def _sdd(tmp_path: Path, evidence: str) -> Path:
    fm = FRONTMATTER.format(id="SDD-TST-0001", type="SDD", status="implemented", created="2026-09-01")
    return _doc(tmp_path, "SDD-TST-0001.md", fm + SDD_BODY.format(evidence=evidence))


def test_arquivo_py_fora_do_escopo(tmp_path):
    path = _doc(tmp_path, "app.py", "print('oi')\n")
    result = _run(path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_readme_sem_front_matter(tmp_path):
    path = _doc(tmp_path, "README.md", "# Projeto\n\nTBD\n")
    result = _run(path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_tipo_fora_do_framework(tmp_path):
    fm = FRONTMATTER.format(id="NOTE-1", type="NOTE", status="implemented", created="2026-09-01")
    path = _doc(tmp_path, "nota.md", fm + "TBD\n")
    result = _run(path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_spec_draft_com_placeholder_so_aviso(tmp_path):
    fm = FRONTMATTER.format(id="SPEC-TST-0001", type="SPEC", status="draft", created="2026-09-01")
    path = _doc(tmp_path, "SPEC-TST-0001.md", fm + SPEC_DRAFT_BODY)
    result = _run(path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_sdd_implemented_com_evidencia_vazia_bloqueia(tmp_path):
    path = _sdd(tmp_path, evidence="")
    result = _run(path)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "viola gate(s)" in result.stderr
    assert "SDD-TST-0001" in result.stderr


def test_sdd_implemented_com_evidencia_preenchida(tmp_path):
    row = "| 1 | `pytest` | 3 passed | teste quebrado falhou | sim |\n"
    path = _sdd(tmp_path, evidence=row)
    result = _run(path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_stdin_invalido(tmp_path):
    result = _run(None, stdin="{quebrado")
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_arquivo_inexistente(tmp_path):
    result = _run(tmp_path / "nao-existe.md")
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
