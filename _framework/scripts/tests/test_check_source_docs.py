"""Testes de check_source_docs.py — ver SDD-DTF-0037 (SPEC-DTF-0014)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_source_docs import check_sdd_source_docs  # noqa: E402

REL_PATH = "docs/DTF/03-spec/SPEC-DTF-0014.md"
URL = f"https://github.com/michelpessoa/doc-traceability-central/blob/main/{REL_PATH}"


def _central(tmp_path: Path, status: str = "approved", path: str = REL_PATH) -> Path:
    central = tmp_path / "central"
    (central / Path(path).parent).mkdir(parents=True, exist_ok=True)
    (central / path).write_text("---\nid: SPEC-DTF-0014\n---\n", encoding="utf-8")
    (central / "registry.yaml").write_text(
        f'documents:\n  - id: SPEC-DTF-0014\n    type: SPEC\n    status: {status}\n    path: "{path}"\n',
        encoding="utf-8",
    )
    return central


def _sdd(tmp_path: Path, source_docs_yaml: str) -> Path:
    path = tmp_path / "SDD-DTF-0037.md"
    path.write_text(
        "---\nid: SDD-DTF-0037\ntype: SDD\n" + source_docs_yaml + "\n---\n\n# teste\n",
        encoding="utf-8",
    )
    return path


def test_source_docs_vazio_nao_reporta_nada(tmp_path):
    sdd = _sdd(tmp_path, "source_docs: []")
    central = _central(tmp_path)
    assert check_sdd_source_docs(sdd, central) == []


def test_id_valido_status_approved_url_certa_nao_reporta_nada(tmp_path):
    central = _central(tmp_path, status="approved")
    sdd = _sdd(tmp_path, f'source_docs:\n  - id: "SPEC-DTF-0014"\n    url: "{URL}"')
    assert check_sdd_source_docs(sdd, central) == []


def test_id_inexistente_no_registry_central_reprova(tmp_path):
    central = _central(tmp_path)
    sdd = _sdd(tmp_path, f'source_docs:\n  - id: "SPEC-DTF-9999"\n    url: "{URL}"')
    problems = check_sdd_source_docs(sdd, central)
    assert len(problems) == 1
    assert "SPEC-DTF-9999" in problems[0]
    assert "não encontrado" in problems[0]


def test_status_fora_de_approved_implemented_reprova(tmp_path):
    central = _central(tmp_path, status="draft")
    sdd = _sdd(tmp_path, f'source_docs:\n  - id: "SPEC-DTF-0014"\n    url: "{URL}"')
    problems = check_sdd_source_docs(sdd, central)
    assert len(problems) == 1
    assert "draft" in problems[0]


def test_status_implemented_e_aceito(tmp_path):
    central = _central(tmp_path, status="implemented")
    sdd = _sdd(tmp_path, f'source_docs:\n  - id: "SPEC-DTF-0014"\n    url: "{URL}"')
    assert check_sdd_source_docs(sdd, central) == []


def test_url_divergente_do_path_do_registry_reprova(tmp_path):
    central = _central(tmp_path)
    sdd = _sdd(
        tmp_path,
        'source_docs:\n  - id: "SPEC-DTF-0014"\n    url: "https://github.com/x/y/blob/main/docs/outro/arquivo.md"',
    )
    problems = check_sdd_source_docs(sdd, central)
    assert len(problems) == 1
    assert "não aponta pro mesmo arquivo" in problems[0]


def test_entrada_sem_id_reprova_via_check_source_docs_urls(tmp_path):
    central = _central(tmp_path)
    sdd = _sdd(tmp_path, f'source_docs:\n  - url: "{URL}"')
    problems = check_sdd_source_docs(sdd, central)
    assert any("sem `id`" in p for p in problems)


def test_entrada_sem_url_reprova_via_check_source_docs_urls(tmp_path):
    central = _central(tmp_path)
    sdd = _sdd(tmp_path, 'source_docs:\n  - id: "SPEC-DTF-0014"')
    problems = check_sdd_source_docs(sdd, central)
    assert any("não tem `url`" in p for p in problems)


def test_uma_entrada_valida_outra_com_id_errado_so_reporta_a_errada(tmp_path):
    central = _central(tmp_path)
    sdd = _sdd(
        tmp_path,
        "source_docs:\n"
        f'  - id: "SPEC-DTF-0014"\n    url: "{URL}"\n'
        '  - id: "SPEC-DTF-9999"\n    url: "https://github.com/x/y/blob/main/docs/x.md"',
    )
    problems = check_sdd_source_docs(sdd, central)
    assert len(problems) == 1
    assert "SPEC-DTF-9999" in problems[0]


def test_tipo_legado_prd_reconhecido_igual_a_spec(tmp_path):
    central = _central(tmp_path, path="docs/DTF/03-prd/PRD-DTF-0001.md")
    (central / "registry.yaml").write_text(
        "documents:\n"
        "  - id: PRD-DTF-0001\n"
        "    type: PRD\n"
        "    status: approved\n"
        '    path: "docs/DTF/03-prd/PRD-DTF-0001.md"\n',
        encoding="utf-8",
    )
    url = "https://github.com/michelpessoa/doc-traceability-central/blob/main/docs/DTF/03-prd/PRD-DTF-0001.md"
    sdd = _sdd(tmp_path, f'source_docs:\n  - id: "PRD-DTF-0001"\n    url: "{url}"')
    assert check_sdd_source_docs(sdd, central) == []


def test_registry_central_inacessivel_levanta_erro_explicito(tmp_path):
    sdd = _sdd(tmp_path, f'source_docs:\n  - id: "SPEC-DTF-0014"\n    url: "{URL}"')
    import pytest

    with pytest.raises(SystemExit):
        check_sdd_source_docs(sdd, tmp_path / "nao-existe")


# --- Fidelidade por projeto (SPEC-DTF-0032, RF02; SDD-DTF-0058) --------------

import yaml  # noqa: E402
from check_source_docs import _project, check_rf_fidelity  # noqa: E402

P_SPEC = "SPEC-TST-0009"
P_REL = f"docs/TST/03-spec/{P_SPEC}.md"
P_URL = f"https://example.invalid/central/blob/main/{P_REL}"
P_HEADER = "| RF-ID | Origem | Requisito (resumo) | Arquivos |\n|---|---|---|---|\n"


def _p_central(tmp_path: Path, rfs: dict[str, str | None]) -> Path:
    """SPEC com a coluna Projeto; `None` em todos os valores tira a coluna."""
    com_coluna = any(v is not None for v in rfs.values())
    if com_coluna:
        cab = "| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos | Projeto |\n|---|---|---|---|---|\n"
        linhas = "".join(f"| {rf} | R | O sistema deve | `a.py` | {p} |\n" for rf, p in rfs.items())
    else:
        cab = "| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |\n|---|---|---|---|\n"
        linhas = "".join(f"| {rf} | R | O sistema deve | `a.py` |\n" for rf in rfs)
    central = tmp_path / "central"
    (central / Path(P_REL).parent).mkdir(parents=True, exist_ok=True)
    (central / P_REL).write_text(
        f"---\nid: {P_SPEC}\ntype: SPEC\n---\n\n## Requisitos funcionais\n\n" + cab + linhas, encoding="utf-8"
    )
    (central / "registry.yaml").write_text(
        f'documents:\n  - id: {P_SPEC}\n    type: SPEC\n    status: approved\n    path: "{P_REL}"\n',
        encoding="utf-8",
    )
    return central


def _p_sdd(tmp_path: Path, rfs: list[str], project: str | None = "AAA") -> Path:
    sdd_dir = tmp_path / "projeto" / "docs" / "sdd"
    sdd_dir.mkdir(parents=True, exist_ok=True)
    reg = {"framework_version": "2.7.0", "documents": []}
    if project is not None:
        reg = {"project": project, **reg}
    (sdd_dir / "registry.yaml").write_text(yaml.safe_dump(reg), encoding="utf-8")
    fm = {
        "id": "SDD-TST-0009",
        "type": "SDD",
        "status": "draft",
        "created": "2099-01-01",
        "sizing": "medium",
        "source_docs": [{"id": P_SPEC, "url": P_URL}],
    }
    linhas = "".join(f"| {rf} | {P_SPEC} | Resumo | `a.py` |\n" for rf in rfs)
    path = sdd_dir / "SDD-TST-0009.md"
    path.write_text(
        "---\n" + yaml.safe_dump(fm) + "---\n\n## Requisitos consolidados\n\n" + P_HEADER + linhas,
        encoding="utf-8",
    )
    return path


def test_projeto_sdd_de_cada_projeto_passa(tmp_path):
    central = _p_central(tmp_path, {"RF01": "AAA", "RF02": "AAA", "RF03": "BBB"})
    assert check_sdd_source_docs(_p_sdd(tmp_path, ["RF01", "RF02"], "AAA"), central) == []
    assert check_sdd_source_docs(_p_sdd(tmp_path, ["RF03"], "BBB"), central) == []


def test_projeto_celula_com_dois_projetos_vale_para_os_dois(tmp_path):
    central = _p_central(tmp_path, {"RF01": "AAA, BBB", "RF02": "BBB"})
    assert check_sdd_source_docs(_p_sdd(tmp_path, ["RF01"], "AAA"), central) == []
    assert check_sdd_source_docs(_p_sdd(tmp_path, ["RF01", "RF02"], "BBB"), central) == []


def test_projeto_rf_de_outro_projeto_reprova(tmp_path):
    central = _p_central(tmp_path, {"RF01": "AAA", "RF02": "BBB"})
    problems = check_sdd_source_docs(_p_sdd(tmp_path, ["RF01", "RF02"], "AAA"), central)
    assert problems == [f"SDD-TST-0009: RF02 de {P_SPEC} é do projeto BBB, não de AAA."]


def test_projeto_spec_sem_rf_do_projeto_reprova(tmp_path):
    central = _p_central(tmp_path, {"RF01": "BBB", "RF02": "BBB"})
    problems = check_sdd_source_docs(_p_sdd(tmp_path, ["RF01"], "AAA"), central)
    assert problems == [f"SDD-TST-0009: {P_SPEC} não tem RF do projeto AAA na coluna Projeto."]


def test_projeto_rf_do_projeto_faltando_reprova_so_com_os_do_projeto(tmp_path):
    central = _p_central(tmp_path, {"RF01": "AAA", "RF02": "AAA", "RF03": "BBB"})
    problems = check_sdd_source_docs(_p_sdd(tmp_path, ["RF01", "RF09"], "AAA"), central)
    assert problems == [f"SDD-TST-0009: RFs de {P_SPEC} fora da SDD: RF02; RFs da SDD fora de {P_SPEC}: RF09."]


def test_projeto_spec_sem_coluna_igual_a_2_7_0(tmp_path):
    central = _p_central(tmp_path, {"RF01": None, "RF02": None})
    problems = check_sdd_source_docs(_p_sdd(tmp_path, ["RF01"], "AAA"), central)
    assert problems == [f"SDD-TST-0009: RFs de {P_SPEC} fora da SDD: RF02; RFs da SDD fora de {P_SPEC}: nenhum."]


def test_projeto_registry_sem_project_igual_a_2_7_0(tmp_path):
    central = _p_central(tmp_path, {"RF01": "AAA", "RF02": "BBB"})
    problems = check_sdd_source_docs(_p_sdd(tmp_path, ["RF01"], None), central)
    assert problems == [f"SDD-TST-0009: RFs de {P_SPEC} fora da SDD: RF02; RFs da SDD fora de {P_SPEC}: nenhum."]


def test_projeto_check_rf_fidelity_sem_project_e_a_assinatura_antiga(tmp_path):
    central = _p_central(tmp_path, {"RF01": "AAA", "RF02": "BBB"})
    rows = [{"rf": "RF01", "origem": P_SPEC, "resumo": "", "arquivos": "a.py"}]
    spec = {P_SPEC: central / P_REL}
    assert check_rf_fidelity("X", rows, spec) == [
        f"X: RFs de {P_SPEC} fora da SDD: RF02; RFs da SDD fora de {P_SPEC}: nenhum."
    ]
    assert check_rf_fidelity("X", rows, spec, project="AAA") == []


def test_projeto__project_le_o_registry_mais_proximo(tmp_path):
    assert _project(_p_sdd(tmp_path, ["RF01"], "AAA")) == "AAA"
    assert _project(_p_sdd(tmp_path, ["RF01"], None)) is None
