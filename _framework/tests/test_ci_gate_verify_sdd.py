"""Testes de ci_gate_verify_sdd.py — ver SDD-DTF-0032 (RF01-RF10)."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from ci_gate_verify_sdd import (  # noqa: E402
    GateOperationalError,
    evaluate_gate,
    parse_frontmatter_at_revision,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "_framework" / "scripts" / "ci_gate_verify_sdd.py"


# ---------------------------------------------------------------------------
# Fixture: repositório git real (nenhum mock, SPEC-DTF-0011 exige)
# ---------------------------------------------------------------------------


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def make_repo(tmp_path: Path, name: str = "repo") -> Path:
    repo = tmp_path / name
    repo.mkdir()
    _run_git(repo, "init", "-q")
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Test")
    return repo


def commit_file(repo: Path, relpath: str, content: str, message: str) -> str:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _run_git(repo, "add", relpath)
    _run_git(repo, "commit", "-q", "-m", message)
    return _run_git(repo, "rev-parse", "HEAD").stdout.strip()


def sdd_content(sdd_id: str, status: str, rf_ids=("RF01",), criteria_rows=None) -> str:
    reqs = "\n".join(f"| {rf} | requisito {rf} |" for rf in rf_ids)
    if criteria_rows is None:
        criteria_rows = [f"| 1 | {rf_ids[0]} — critério de {rf_ids[0]} | `cmd` | saída esperada |"]
    crit = "\n".join(criteria_rows)
    return f"""---
id: {sdd_id}
type: SDD
title: "SDD de teste"
status: {status}
project: "DTF"
owner: "Test"
created: "2026-09-22"
updated: "2026-09-22"
relates_to: []
tags: []
---

# SDD de teste

## Requisitos consolidados

| RF-ID | Requisito |
|---|---|
{reqs}

## Critérios de aceite / definição de pronto

| # | Critério (origem: RF-ID / contrato) | Comando de verificação | Resultado esperado |
|---|---|---|---|
{crit}
"""


def validation_content(sdd_id: str, veredito: str = "PASS", rows=None) -> str:
    if rows is None:
        rows = ["| RF01 — critério de RF01 | `cmd` | saída | sem teste | Sim |"]
    body = "\n".join(rows)
    return f"""# Verificação — {sdd_id}

- **Veredito:** {veredito}
- **Verificador independente:** sim

| Critério | Comando rodado | Saída (resumo) | Sensor | Passou? |
|---|---|---|---|---|
{body}
"""


# ---------------------------------------------------------------------------
# RF01
# ---------------------------------------------------------------------------


def test_parse_frontmatter_base_head(tmp_path):
    repo = make_repo(tmp_path)
    base = commit_file(repo, "docs/sdd/SDD-DTF-0001.md", sdd_content("SDD-DTF-0001", "approved"), "base")
    head = commit_file(repo, "docs/sdd/SDD-DTF-0001.md", sdd_content("SDD-DTF-0001", "implemented"), "head")

    import os

    old_cwd = os.getcwd()
    os.chdir(repo)
    try:
        fm_base, _ = parse_frontmatter_at_revision(base, "docs/sdd/SDD-DTF-0001.md")
        fm_head, _ = parse_frontmatter_at_revision(head, "docs/sdd/SDD-DTF-0001.md")
    finally:
        os.chdir(old_cwd)

    assert fm_base["status"] == "approved"
    assert fm_head["status"] == "implemented"


# ---------------------------------------------------------------------------
# Helper comum para os testes de gate completo
# ---------------------------------------------------------------------------


def _prepare_transition(tmp_path, sdd_id="SDD-DTF-0001", rf_ids=("RF01",), criteria_rows=None, repo_name="repo"):
    repo = make_repo(tmp_path, repo_name)
    base = commit_file(
        repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "approved", rf_ids, criteria_rows), "approved"
    )
    return repo, base, sdd_id


def _run_gate(repo, base, head, sdd_id, pr_labels=None, pr_body="", central_registry_path=None):
    import os

    old_cwd = os.getcwd()
    os.chdir(repo)
    try:
        return evaluate_gate(
            base,
            head,
            [f"docs/sdd/{sdd_id}.md"],
            pr_labels or [],
            pr_body,
            "DTF",
            central_registry_path,
        )
    finally:
        os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# RF02
# ---------------------------------------------------------------------------


def test_validation_ausente_reprova(tmp_path):
    repo, base, sdd_id = _prepare_transition(tmp_path)
    head = commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented"), "implemented")

    gate = _run_gate(repo, base, head, sdd_id)

    assert gate.passed is False
    assert gate.per_sdd[0].outcome == "fail"
    assert any("ausente" in r for r in gate.per_sdd[0].reasons)


# ---------------------------------------------------------------------------
# RF03
# ---------------------------------------------------------------------------


def test_rf_sem_cobertura_reprova(tmp_path):
    rf_ids = ("RF01", "RF02")
    criteria_rows = [
        "| 1 | RF01 — critério de RF01 | `cmd` | ok |",
        "| 2 | RF02 — critério de RF02 | `cmd` | ok |",
    ]
    repo, base, sdd_id = _prepare_transition(tmp_path, rf_ids=rf_ids, criteria_rows=criteria_rows)
    commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented", rf_ids, criteria_rows), "wip")
    head = commit_file(
        repo,
        f"docs/sdd/validation-{sdd_id}.md",
        validation_content(sdd_id, rows=["| RF01 — critério de RF01 | `cmd` | ok | sem teste | Sim |"]),
        "validation",
    )

    gate = _run_gate(repo, base, head, sdd_id)

    assert gate.passed is False
    assert any("RF02" in r for r in gate.per_sdd[0].reasons)


# ---------------------------------------------------------------------------
# RF04 — sensor de discriminação
# ---------------------------------------------------------------------------


def test_linha_fail_reprova_apesar_de_veredito_pass(tmp_path):
    repo, base, sdd_id = _prepare_transition(tmp_path)
    commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented"), "wip")
    head = commit_file(
        repo,
        f"docs/sdd/validation-{sdd_id}.md",
        validation_content(
            sdd_id, veredito="PASS", rows=["| RF01 — critério de RF01 | `cmd` | falhou | sem teste | Não |"]
        ),
        "validation com linha reprovada",
    )

    gate = _run_gate(repo, base, head, sdd_id)

    assert gate.passed is False
    assert any("RF04" in r or "!= PASS" in r for r in gate.per_sdd[0].reasons)

    # Sensor de discriminação: com todas as linhas "Sim", o mesmo cenário passa.
    repo2, base2, sdd_id2 = _prepare_transition(tmp_path, sdd_id="SDD-DTF-0002", repo_name="repo2")
    commit_file(repo2, f"docs/sdd/{sdd_id2}.md", sdd_content(sdd_id2, "implemented"), "wip")
    head2 = commit_file(
        repo2,
        f"docs/sdd/validation-{sdd_id2}.md",
        validation_content(sdd_id2, veredito="PASS"),
        "validation ok",
    )
    gate_ok = _run_gate(repo2, base2, head2, sdd_id2)
    assert gate_ok.passed is True


# ---------------------------------------------------------------------------
# RF05 — sensor de discriminação
# ---------------------------------------------------------------------------


def test_criterio_afrouxado_reprova(tmp_path):
    rf_ids = ("RF01",)
    base_rows = ["| 1 | RF01 — critério rígido original | `cmd` | ok |"]
    head_rows = ["| 1 | RF01 — critério afrouxado | `cmd` | ok |"]
    repo, base, sdd_id = _prepare_transition(tmp_path, rf_ids=rf_ids, criteria_rows=base_rows)
    commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented", rf_ids, head_rows), "wip")
    head = commit_file(repo, f"docs/sdd/validation-{sdd_id}.md", validation_content(sdd_id), "validation")

    gate = _run_gate(repo, base, head, sdd_id, pr_body="")

    assert gate.passed is False
    assert any("RF05" in r for r in gate.per_sdd[0].reasons)

    # Sensor de discriminação: com a justificativa citando o RF-ID, passa.
    gate_justified = _run_gate(
        repo, base, head, sdd_id, pr_body="**Justificativa de mudança:** simplificação aprovada para RF01."
    )
    assert gate_justified.passed is True


def test_criterio_reordenado_nao_reprova(tmp_path):
    rf_ids = ("RF01", "RF02")
    base_rows = [
        "| 1 | RF01 — critério A | `cmd` | ok |",
        "| 2 | RF02 — critério B | `cmd` | ok |",
    ]
    head_rows = [
        "| 1 | RF02 — critério B | `cmd` | ok |",
        "| 2 | RF01 — critério A | `cmd` | ok |",
    ]
    repo, base, sdd_id = _prepare_transition(tmp_path, rf_ids=rf_ids, criteria_rows=base_rows)
    commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented", rf_ids, head_rows), "wip")
    head = commit_file(
        repo,
        f"docs/sdd/validation-{sdd_id}.md",
        validation_content(
            sdd_id,
            rows=[
                "| RF01 — critério A | `cmd` | ok | sem teste | Sim |",
                "| RF02 — critério B | `cmd` | ok | sem teste | Sim |",
            ],
        ),
        "validation",
    )

    gate = _run_gate(repo, base, head, sdd_id)

    assert gate.passed is True
    assert gate.per_sdd[0].outcome == "pass"


# ---------------------------------------------------------------------------
# RF06/RF07 — override
# ---------------------------------------------------------------------------


def _registry_with_inc(tmp_path, inc_id: str, status: str) -> str:
    registry_path = tmp_path / "central-registry.yaml"
    registry_path.write_text(
        yaml.safe_dump({"documents": [{"id": inc_id, "type": "INC", "status": status}]}),
        encoding="utf-8",
    )
    return str(registry_path)


def test_override_inc_valido_libera(tmp_path):
    repo, base, sdd_id = _prepare_transition(tmp_path)
    head = commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented"), "implemented")
    registry_path = _registry_with_inc(tmp_path, "INC-DTF-0099", "open")

    gate = _run_gate(
        repo,
        base,
        head,
        sdd_id,
        pr_labels=["incident-override"],
        pr_body="Hotfix para INC-DTF-0099.",
        central_registry_path=registry_path,
    )

    assert gate.passed is True
    assert gate.per_sdd[0].outcome == "pass"
    assert gate.overrides_used and gate.overrides_used[0].inc_id == "INC-DTF-0099"


# ---------------------------------------------------------------------------
# RF07 — sensor de discriminação
# ---------------------------------------------------------------------------


def test_override_inc_invalido_reprova(tmp_path):
    repo, base, sdd_id = _prepare_transition(tmp_path)
    head = commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented"), "implemented")
    registry_path = _registry_with_inc(tmp_path, "INC-DTF-0099", "closed")

    gate = _run_gate(
        repo,
        base,
        head,
        sdd_id,
        pr_labels=["incident-override"],
        pr_body="Hotfix para INC-DTF-0099.",
        central_registry_path=registry_path,
    )

    assert gate.passed is False
    assert any("closed" in r or "RF07" in r for r in gate.per_sdd[0].reasons)


def test_falha_credencial_exit_2(tmp_path):
    repo, base, sdd_id = _prepare_transition(tmp_path)
    head = commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented"), "implemented")

    with pytest.raises(GateOperationalError):
        _run_gate(
            repo,
            base,
            head,
            sdd_id,
            pr_labels=["incident-override"],
            pr_body="Hotfix para INC-DTF-0099.",
            central_registry_path=str(tmp_path / "nao-existe.yaml"),
        )


def test_log_override_aceito(tmp_path):
    repo, base, sdd_id = _prepare_transition(tmp_path)
    head = commit_file(repo, f"docs/sdd/{sdd_id}.md", sdd_content(sdd_id, "implemented"), "implemented")
    registry_path = _registry_with_inc(tmp_path, "INC-DTF-0042", "mitigated")

    gate = _run_gate(
        repo,
        base,
        head,
        sdd_id,
        pr_labels=["incident-override"],
        pr_body="Hotfix para INC-DTF-0042.",
        central_registry_path=registry_path,
    )

    assert len(gate.overrides_used) == 1
    log = gate.overrides_used[0]
    assert log.inc_id == "INC-DTF-0042"
    assert log.status == "mitigated"
    assert log.timestamp


# ---------------------------------------------------------------------------
# RF09
# ---------------------------------------------------------------------------


def test_frontmatter_malformado_exit_2(tmp_path):
    repo = make_repo(tmp_path)
    commit_file(repo, "docs/sdd/SDD-DTF-0001.md", sdd_content("SDD-DTF-0001", "approved"), "approved")
    broken = "---\nid: SDD-DTF-0001\nstatus: [implemented\n---\n\n# corpo\n"
    head = commit_file(repo, "docs/sdd/SDD-DTF-0001.md", broken, "malformado")

    import os

    old_cwd = os.getcwd()
    os.chdir(repo)
    try:
        with pytest.raises(GateOperationalError):
            parse_frontmatter_at_revision(head, "docs/sdd/SDD-DTF-0001.md")
    finally:
        os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# CLI ponta a ponta
# ---------------------------------------------------------------------------


def test_cli_pr_fixture_duas_sdds(tmp_path):
    repo = make_repo(tmp_path)
    base = commit_file(repo, "docs/sdd/SDD-DTF-0001.md", sdd_content("SDD-DTF-0001", "approved"), "base 1")
    commit_file(repo, "docs/sdd/SDD-DTF-0002.md", sdd_content("SDD-DTF-0002", "approved"), "base 2")

    commit_file(repo, "docs/sdd/SDD-DTF-0001.md", sdd_content("SDD-DTF-0001", "implemented"), "wip 1")
    commit_file(repo, "docs/sdd/validation-SDD-DTF-0001.md", validation_content("SDD-DTF-0001"), "validation 1")
    commit_file(repo, "docs/sdd/SDD-DTF-0002.md", sdd_content("SDD-DTF-0002", "implemented"), "wip 2 (sem validation)")
    head = _run_git(repo, "rev-parse", "HEAD").stdout.strip()

    body_file = tmp_path / "pr-body.txt"
    body_file.write_text("", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--base",
            base,
            "--head",
            head,
            "--project-code",
            "DTF",
            "--pr-body-file",
            str(body_file),
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "SDD-DTF-0001" in result.stdout
    assert "SDD-DTF-0002" in result.stdout
    assert "Traceback" not in result.stderr
