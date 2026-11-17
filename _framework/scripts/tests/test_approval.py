"""Testes de approval_policy e validate_state.check_approval — SDD-DTF-0054.

RF01, RF02, RF03, RF05 a RF08 da SPEC-DTF-0029. Usa o workflow-rules.yaml
real. Documentos novos usam `created` em 2099 para ficar depois de
qualquer data da 2.5.0; os antigos, 2026-01-01, antes dela.
"""

import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from approval_hash import content_hash  # noqa: E402
from framework_lib import load_rules  # noqa: E402
from validate_state import RULE_SINCE, check_approval  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
NOVO = "2099-01-01"
ANTIGO = "2026-01-01"

BODY = (
    "\n# Documento\n\n## Requisitos consolidados\n\nRF01 faz X.\n\n"
    "## Evidência de verificação (preencher antes de status `implemented`)\n\n{evidencia}\n"
)


def _project(tmp_path: Path, version: str = "2.5.0") -> Path:
    (tmp_path / "registry.yaml").write_text(f'project: "TST"\nframework_version: "{version}"\n', encoding="utf-8")
    return tmp_path


def _doc(
    tmp_path: Path,
    *,
    doc_type: str = "SDD",
    status: str = "approved",
    created: str = NOVO,
    sizing: str | None = None,
    approved_by="valido",
    evidencia: str = "",
    version: str = "2.5.0",
) -> Path:
    _project(tmp_path, version)
    doc_id = f"{doc_type}-TST-0001"
    path = tmp_path / f"{doc_id}.md"
    fm = {"id": doc_id, "type": doc_type, "title": "teste", "status": status, "created": created}
    if sizing:
        fm["sizing"] = sizing
    body = BODY.format(evidencia=evidencia)
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True) + "---\n" + body, encoding="utf-8")
    if approved_by == "valido":
        approved_by = {
            "kind": "policy",
            "actor": "executor",
            "at": "2099-01-01T10:00:00Z",
            "content_sha256": content_hash(path),
        }
    if approved_by is not None:
        fm["approved_by"] = approved_by
        path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True) + "---\n" + body, encoding="utf-8")
    return path


def _humano(path: Path, **extra) -> dict:
    data = {
        "kind": "human",
        "actor": "owner",
        "at": "2099-01-01",
        "content_sha256": content_hash(path),
        "evidence": "https://example.invalid/pull/1#pullrequestreview-1",
    }
    data.update(extra)
    return data


def _problems(path: Path) -> list[str]:
    problems, _ = check_approval(path)
    return problems


# --- RF01, RF02: a política no YAML real ------------------------------------


def test_approval_policy_tem_as_chaves_da_spec():
    policy = load_rules()["approval_policy"]
    assert set(policy) == {"default_approver", "hash_excluded_sections", "rules"}
    assert policy["default_approver"] == "human"
    assert policy["hash_excluded_sections"] == [
        "Evidência de verificação",
        "Verificação de escopo (nada a mais, nada a menos)",
        "Gate de decisão: esta RFC exige um ADR?",
        "Documentos originados",
    ]


def test_regras_iniciais_em_ordem():
    rules = load_rules()["approval_policy"]["rules"]
    assert rules[0] == {"types": ["STRAT", "RFC", "ADR", "BASE", "PM"], "approver": "human"}
    assert rules[1] == {"types": ["SPEC"], "sizing": ["medium", "large", "complex"], "approver": "human"}
    assert rules[2]["types"] == ["SDD"] and rules[2]["approver"] == "policy" and "sizing" not in rules[2]
    assert rules[2]["checks"] == [
        "validate_doc.py",
        "registry_tools.py validate",
        "check_source_docs.py (com source_docs)",
        "verify-sdd passo 0 (com source_docs)",
    ]
    assert len(rules) == 3


def test_approved_by_declarado_no_frontmatter_schema():
    assert "approved_by" in load_rules()["frontmatter_schema"]["common_fields"]


def test_rule_since_da_aprovacao():
    assert RULE_SINCE["approved_by"] == "2.5.0"


# --- RF05: cobrança ---------------------------------------------------------


def test_sdd_aprovada_por_politica_com_hash_certo_passa(tmp_path):
    assert _problems(_doc(tmp_path)) == []


def test_sem_approved_by_reprova_nomeando_documento(tmp_path):
    problems = _problems(_doc(tmp_path, approved_by=None))
    assert len(problems) == 1
    assert problems[0].startswith("SDD-TST-0001:") and "approved_by ausente" in problems[0]


def test_implemented_e_superseded_tambem_cobram(tmp_path):
    for status in ("implemented", "superseded"):
        assert any("approved_by ausente" in p for p in _problems(_doc(tmp_path, status=status, approved_by=None)))


def test_status_sem_aprovacao_nao_cobra(tmp_path):
    for status in ("draft", "in_review", "rejected", "archived"):
        assert _problems(_doc(tmp_path, status=status, approved_by=None)) == []


def test_inc_fora_da_cobranca(tmp_path):
    assert _problems(_doc(tmp_path, doc_type="INC", status="closed", approved_by=None)) == []


# --- RF03: formato ----------------------------------------------------------


def test_approved_by_que_nao_e_mapa_reprova(tmp_path):
    assert any("approved_by deve ser um mapa" in p for p in _problems(_doc(tmp_path, approved_by="sim")))


def test_campo_ausente_reprova_nomeando_o_campo(tmp_path):
    path = _doc(tmp_path)
    fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])
    for campo in ("kind", "actor", "at", "content_sha256"):
        dados = dict(fm["approved_by"])
        del dados[campo]
        problems = _problems(_doc(tmp_path, approved_by=dados))
        assert any(f"`{campo}`" in p for p in problems), (campo, problems)


def test_kind_invalido_reprova(tmp_path):
    path = _doc(tmp_path)
    dados = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])["approved_by"]
    dados["kind"] = "robo"
    assert any("`kind`" in p for p in _problems(_doc(tmp_path, approved_by=dados)))


def test_hash_que_nao_e_hexadecimal_de_64_reprova(tmp_path):
    path = _doc(tmp_path)
    dados = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])["approved_by"]
    for ruim in ("abc", "Z" * 64, "A" * 64):
        dados["content_sha256"] = ruim
        assert any("`content_sha256`" in p for p in _problems(_doc(tmp_path, approved_by=dict(dados)))), ruim


def test_at_fora_de_iso_8601_reprova(tmp_path):
    path = _doc(tmp_path)
    dados = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])["approved_by"]
    dados["at"] = "ontem"
    assert any("`at`" in p for p in _problems(_doc(tmp_path, approved_by=dados)))


def test_human_sem_evidence_reprova(tmp_path):
    path = _doc(tmp_path, doc_type="RFC", approved_by=None)
    dados = _humano(path)
    del dados["evidence"]
    assert any("`evidence`" in p for p in _problems(_doc(tmp_path, doc_type="RFC", approved_by=dados)))


def test_human_com_evidence_passa(tmp_path):
    path = _doc(tmp_path, doc_type="RFC", approved_by=None)
    assert _problems(_doc(tmp_path, doc_type="RFC", approved_by=_humano(path))) == []


def test_draft_com_campo_invalido_reprova_formato(tmp_path):
    assert any("approved_by deve ser um mapa" in p for p in _problems(_doc(tmp_path, status="draft", approved_by="x")))


def test_draft_com_hash_diferente_nao_reprova(tmp_path):
    path = _doc(tmp_path, status="draft")
    dados = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])["approved_by"]
    dados["content_sha256"] = "0" * 64
    assert _problems(_doc(tmp_path, status="draft", approved_by=dados)) == []


# --- RF06: política ---------------------------------------------------------


def test_policy_em_spec_large_reprova(tmp_path):
    problems = _problems(_doc(tmp_path, doc_type="SPEC", sizing="large"))
    assert any("política" in p for p in problems), problems


def test_policy_em_rfc_sem_sizing_reprova(tmp_path):
    assert any("política" in p for p in _problems(_doc(tmp_path, doc_type="RFC")))


def test_spec_small_cai_no_default_human(tmp_path):
    assert any("política" in p for p in _problems(_doc(tmp_path, doc_type="SPEC", sizing="small")))


def test_human_em_sdd_passa(tmp_path):
    path = _doc(tmp_path, approved_by=None)
    assert _problems(_doc(tmp_path, approved_by=_humano(path))) == []


# --- RF07: conteúdo mudado --------------------------------------------------


def test_hash_diferente_reprova(tmp_path):
    path = _doc(tmp_path)
    path.write_text(path.read_text(encoding="utf-8").replace("RF01 faz X.", "RF01 faz Y."), encoding="utf-8")
    problems = _problems(path)
    assert any("mudou depois da aprovação" in p for p in problems), problems


def test_secao_excluida_preenchida_depois_nao_reprova(tmp_path):
    path = _doc(tmp_path)
    texto = path.read_text(encoding="utf-8") + "| A01 | pytest | 3 passed |\n"
    path.write_text(texto, encoding="utf-8")
    assert _problems(path) == []


# --- RF08: não retroativo ---------------------------------------------------


def test_documento_antigo_nao_e_cobrado(tmp_path):
    assert _problems(_doc(tmp_path, created=ANTIGO, approved_by=None)) == []


def test_documento_sem_created_nao_e_cobrado(tmp_path):
    path = _doc(tmp_path, approved_by=None)
    path.write_text(path.read_text(encoding="utf-8").replace(f"created: '{NOVO}'\n", ""), encoding="utf-8")
    assert "created" not in path.read_text(encoding="utf-8")
    assert _problems(path) == []


def test_projeto_em_2_4_0_nao_e_cobrado(tmp_path):
    assert _problems(_doc(tmp_path, version="2.4.0", approved_by=None)) == []


def test_documento_antigo_com_campo_e_validado(tmp_path):
    path = _doc(tmp_path, created=ANTIGO)
    path.write_text(path.read_text(encoding="utf-8").replace("RF01 faz X.", "RF01 faz Y."), encoding="utf-8")
    assert any("mudou depois da aprovação" in p for p in _problems(path))


def test_projeto_antigo_com_policy_em_spec_e_validado(tmp_path):
    assert any("política" in p for p in _problems(_doc(tmp_path, doc_type="SPEC", sizing="large", version="2.4.0")))


# --- CLI ----------------------------------------------------------------------


def test_validate_state_cli_reprova(tmp_path):
    path = _doc(tmp_path, approved_by=None)
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "validate_state.py"), str(path)], capture_output=True, text=True
    )
    assert r.returncode == 1
    assert "approved_by ausente" in r.stdout


def test_framework_check_reprova(tmp_path):
    _doc(tmp_path, approved_by=None)
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_check.py"), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1
    assert "approved_by ausente" in r.stdout


# --- SPEC-DTF-0030, RF02: actor contra approvers (SDD-DTF-0055) -------------


def _com_lista(tmp_path: Path, approvers) -> None:
    (tmp_path / "registry.yaml").write_text(
        yaml.safe_dump({"project": "TST", "framework_version": "2.5.0", "approvers": approvers}), encoding="utf-8"
    )


def test_actor_na_lista_passa(tmp_path):
    path = _doc(tmp_path, doc_type="RFC", approved_by=None)
    doc = _doc(tmp_path, doc_type="RFC", approved_by=_humano(path))
    _com_lista(tmp_path, ["owner", "outro"])
    assert _problems(doc) == []


def test_actor_fora_da_lista_reprova_com_a_mensagem(tmp_path):
    path = _doc(tmp_path, doc_type="RFC", approved_by=None)
    doc = _doc(tmp_path, doc_type="RFC", approved_by=_humano(path, actor="intruso"))
    _com_lista(tmp_path, ["owner", "outro"])
    assert _problems(doc) == [
        "RFC-TST-0001: approved_by.actor intruso não está em approvers (owner, outro) do registry central."
    ]


def test_sem_lista_actor_qualquer_passa(tmp_path):
    path = _doc(tmp_path, doc_type="RFC", approved_by=None)
    assert _problems(_doc(tmp_path, doc_type="RFC", approved_by=_humano(path, actor="intruso"))) == []


def test_policy_nao_e_conferido_contra_a_lista(tmp_path):
    doc = _doc(tmp_path)
    _com_lista(tmp_path, ["owner"])
    assert _problems(doc) == []
