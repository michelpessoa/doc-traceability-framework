"""Testes de generate_registry_md.py — ver SDD-DTF-0043 (RF08)."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generate_registry_md as grm  # noqa: E402

REGISTRY = (
    'project: "X"\nframework_version: "1.5.0"\ndocuments:\n'
    '  - id: SDD-X-0001\n    type: SDD\n    title: "T"\n    status: approved\n'
    '    owner: "O"\n    updated: "2026-01-01"\n'
)


def _docs(tmp_path: Path) -> Path:
    (tmp_path / "registry.yaml").write_text(REGISTRY, encoding="utf-8")
    return tmp_path


def test_render_header_versao_sem_timestamp():
    header = grm.render_header("X", "2.3.1")
    assert "Framework v2.3.1" in header
    assert not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}", header)


def test_versao_corrente_quando_yaml_acessivel(tmp_path, monkeypatch):
    monkeypatch.setattr(grm, "current_framework_version", lambda: "9.9.9")
    assert "Framework v9.9.9" in grm.render_registry(grm.load_registry(_docs(tmp_path)))


def test_fallback_para_framework_version_do_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(grm, "find_rules_file", lambda *a, **k: None)
    text = grm.render_registry(grm.load_registry(_docs(tmp_path)))
    assert "Framework v1.5.0" in text and "N/D" not in text


def test_check_sai_1_se_divergir_e_0_se_em_dia(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(grm, "find_rules_file", lambda *a, **k: None)
    docs = _docs(tmp_path)
    assert grm.main([str(docs), "--check"]) == 1  # ausente
    assert grm.main([str(docs)]) == 0
    assert grm.main([str(docs), "--check"]) == 0
    assert grm.main([str(docs), "--check"]) == 0  # determinístico
    (docs / "registry.md").write_text("editado à mão\n", encoding="utf-8")
    assert grm.main([str(docs), "--check"]) == 1
    assert (docs / "registry.md").read_text(encoding="utf-8") == "editado à mão\n"  # --check não escreve
    assert "divergente" in capsys.readouterr().out


# --- SDD-DTF-0055: seção para todo tipo, ordem derivada de document_types ---

ALL_TYPES = ["STRAT", "RFC", "ADR", "SPEC", "SDD", "BASE", "INC", "PM", "PRD", "TS"]


def _registry_with(types: list[str]) -> dict:
    docs = [
        {"id": f"{t}-X-{i:04d}", "type": t, "title": "T", "status": "draft", "owner": "O", "updated": "2026-01-01"}
        for i, t in enumerate(types, start=1)
    ]
    return {"project": "X", "framework_version": "2.5.0", "documents": docs}


def _sections(text: str) -> list[str]:
    return re.findall(r"^## (.+) \(\d+\)$", text, flags=re.M)


def _table_rows(text: str) -> int:
    return len(re.findall(r"^\| `", text, flags=re.M))


def test_type_order_vem_do_yaml_real():
    """RF01: chaves de document_types e depois de legacy_document_types."""
    rules = grm.load_rules()
    assert grm.type_order(rules) == ALL_TYPES


def test_type_order_sem_yaml_usa_ordem_embutida():
    """RF02: sem regras, a ordem embutida tem os dez tipos."""
    assert grm.type_order({}) == ALL_TYPES


def test_fallback_sem_yaml_tem_secao_para_cada_tipo(monkeypatch):
    """RF02: com find_rules_file -> None, nenhum dos dez tipos some."""
    monkeypatch.setattr(grm, "find_rules_file", lambda *a, **k: None)
    text = grm.render_registry(_registry_with(ALL_TYPES))
    assert len(_sections(text)) == len(ALL_TYPES)
    for i, t in enumerate(ALL_TYPES, start=1):
        assert f"`{t}-X-{i:04d}`" in text


def test_tipo_nao_declarado_ganha_secao_propria():
    """RF03: tipo fora da ordem não é descartado; vai depois, em ordem alfabética."""
    text = grm.render_registry(_registry_with(["SDD", "ZZZ", "XYZ"]))
    assert "## Tipo não declarado: XYZ (1)" in text
    assert "`XYZ-X-0003`" in text and "`ZZZ-X-0002`" in text
    assert _sections(text) == ["SDD", "Tipo não declarado: XYZ", "Tipo não declarado: ZZZ"]


def test_rotulos_curtos():
    """RF04: títulos atuais não mudam; SPEC sai como SPEC."""
    text = grm.render_registry(_registry_with(["STRAT", "SPEC", "TS"]))
    assert _sections(text) == ["Strategy Doc", "SPEC", "Tech Spec"]


def test_rotulo_cai_no_name_do_yaml_sem_rotulo_curto(monkeypatch):
    """RF04: tipo declarado sem rótulo curto usa o name do YAML."""
    rules = {"document_types": {"NEW": {"name": "Tipo Novo"}}}
    monkeypatch.setattr(grm, "TYPE_LABEL", {})
    assert grm.type_label("NEW", rules) == "Tipo Novo"
    assert grm.type_label("OUT", rules) == "Tipo não declarado: OUT"


def test_soma_das_linhas_igual_ao_total():
    """RF05: todo documento do registry aparece em alguma seção."""
    data = _registry_with([*ALL_TYPES, "XYZ", ""])
    text = grm.render_registry(data)
    assert f"Total de documentos: **{len(data['documents'])}**" in text
    assert _table_rows(text) == len(data["documents"])


def test_ordem_embutida_e_rotulos_cobrem_o_yaml_real():
    """RF06: tipo novo no YAML sem entrada no script faz este teste falhar."""
    rules = grm.load_rules()
    declared = [*(rules.get("document_types") or {}), *(rules.get("legacy_document_types") or {})]
    assert declared, "workflow-rules.yaml sem document_types"
    assert sorted(declared) == sorted(grm.TYPE_ORDER)
    assert set(declared) <= set(grm.TYPE_LABEL)
