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
        "documents:\n"
        "  - id: SPEC-DTF-0014\n"
        "    type: SPEC\n"
        f"    status: {status}\n"
        f'    path: "{path}"\n',
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
