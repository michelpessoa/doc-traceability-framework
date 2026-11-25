"""Testes do núcleo canônico (`core_facts`) em render_prompts.py — SDD-DTF-0062.

Cobre RF01 a RF04: as subseções `### Aprovação` e `### Executor` saem de
`approval_policy` e `executor_contract`, e o ciclo de status lista todos os
estados em vez de uma cadeia que sugere `rejected → implemented`. Usa o
YAML real e, para RF04 e para a ausência das chaves, cópias dele alteradas.
"""

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework_lib import find_rules_file, load_rules  # noqa: E402
from render_prompts import core_facts  # noqa: E402

RULES = load_rules(find_rules_file(Path(__file__).resolve().parents[3]))


def _rule_row(rule: dict) -> str:
    return f"| {', '.join(rule['types'])} | {', '.join(rule.get('sizing') or ['todos'])} | {rule['approver']} |"


def _table_rows(text: str) -> list[str]:
    """Linhas de dados da tabela da subseção `### Aprovação`."""
    section = text.split("### Aprovação", 1)[1].split("\n### ", 1)[0]
    rows = [ln for ln in section.splitlines() if ln.startswith("| ")]
    return rows[1:]  # descarta o cabeçalho


def test_aprovacao_tem_subsecao_depois_do_ciclo_de_status():
    out = core_facts(RULES)
    assert "### Aprovação" in out
    assert out.index("### Ciclo de vida de status") < out.index("### Aprovação")
    assert "| Tipos | Sizing | Quem aprova |" in out


def test_aprovacao_uma_linha_por_regra_na_ordem_do_yaml():
    policy = RULES["approval_policy"]
    out = core_facts(RULES)
    rows = _table_rows(out)
    assert rows == [_rule_row(r) for r in policy["rules"]]
    assert "| SPEC | medium, large, complex | human |" in rows
    assert "| SDD | todos | policy |" in rows


def test_aprovacao_default_e_frase_de_campos_e_scripts():
    policy = RULES["approval_policy"]
    out = core_facts(RULES)
    section = out.split("### Aprovação", 1)[1].split("\n### ", 1)[0]
    assert f"Sem regra que case: {policy['default_approver']}." in section
    for term in ("approved_by", "content_sha256", "approval_hash.py", "review_approval.py"):
        assert term in section, term
    for excluded in policy["hash_excluded_sections"]:
        assert f"`{excluded}`" in section, excluded


def test_executor_tem_subsecao_com_contract_version_e_writes():
    contract = RULES["executor_contract"]
    out = core_facts(RULES)
    assert "### Executor" in out
    assert out.index("### Aprovação") < out.index("### Executor")
    section = out.split("### Executor", 1)[1].split("\n### ", 1)[0]
    assert f"`contract_version` {contract['contract_version']}." in section
    for phrase in contract["writes"]:
        assert f"- {phrase}" in section.splitlines(), phrase


def test_ciclo_lista_todos_os_estados_sem_cadeia():
    out = core_facts(RULES)
    states = RULES["status_lifecycle"]["states"]
    assert "`rejected` → `implemented`" not in out
    assert "Estados: " + ", ".join(f"`{s}`" for s in states) + "." in out.splitlines()
    for s in states:
        assert f"`{s}`" in out, s


def test_regra_extra_no_yaml_ganha_linha_na_tabela():
    rules = copy.deepcopy(RULES)
    base = len(_table_rows(core_facts(rules)))
    extra = {"types": ["INC"], "sizing": ["small"], "approver": "teste_extra"}
    rules["approval_policy"]["rules"].append(extra)
    rows = _table_rows(core_facts(rules))
    assert len(rows) == base + 1
    assert rows[-1] == "| INC | small | teste_extra |"


def test_sem_chaves_no_yaml_nao_gera_subsecoes():
    rules = copy.deepcopy(RULES)
    rules.pop("approval_policy")
    rules.pop("executor_contract")
    out = core_facts(rules)
    assert "### Aprovação" not in out
    assert "### Executor" not in out


# SDD-DTF-0065, RF01 e RF05: itens de checks depois da tabela de Aprovação


def _aprovacao(text: str) -> str:
    return text.split("### Aprovação", 1)[1].split("\n### ", 1)[0]


def _check_items(text: str) -> list[str]:
    return [ln for ln in _aprovacao(text).splitlines() if ln.startswith("- Checks de ")]


def test_sdd0065_item_de_checks_da_regra_sdd_com_yaml_real():
    out = core_facts(RULES)
    item = (
        "- Checks de SDD (policy): `validate_doc.py`, `registry_tools.py validate`,"
        " `check_source_docs.py (com source_docs)`, `verify-sdd passo 0 (com source_docs)`."
    )
    assert _check_items(out) == [item]
    lines = _aprovacao(out).splitlines()
    i = lines.index(item)
    assert lines[i - 1] == ""
    assert lines[i - 2] == "| SDD | todos | policy |"


def test_sdd0065_regra_sem_checks_nao_ganha_item():
    rules = copy.deepcopy(RULES)
    for r in rules["approval_policy"]["rules"]:
        r.pop("checks", None)
    out = core_facts(rules)
    assert _check_items(out) == []
    assert "Checks de" not in out
    assert _table_rows(out) == _table_rows(core_facts(RULES))
