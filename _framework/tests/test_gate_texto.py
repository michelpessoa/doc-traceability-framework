"""Regressão de texto de `gate_implementation_before_code` — SDD-DTF-0042 (RF04).

Impede a volta da defasagem PRD/Tech Spec no gate e a referência a chave
inexistente de `decision_gates`.
"""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
LEGACY_ANCHOR = "Em projeto legado (sob 1.x)"
LEGACY_PATTERN = re.compile(r"PRD|Tech Spec|\bTS\b")


def _rules() -> dict:
    with RULES_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _gate() -> dict:
    return _rules()["gate_implementation_before_code"]


def test_gate_regra_sem_prd_ts_como_passo():
    gate = _gate()
    rule = gate["rule"]
    assert rule.count(LEGACY_ANCHOR) == 1, (
        f"cláusula de legado {LEGACY_ANCHOR!r} sumiu ou está duplicada em rule"
    )
    passos = rule.split(LEGACY_ANCHOR)[0]
    assert LEGACY_PATTERN.search(passos) is None, "rule cita PRD/Tech Spec/TS fora da cláusula de legado"
    for campo in ("not_sufficient_alone", "if_user_asks_to_skip", "relationship_with_audit"):
        assert LEGACY_PATTERN.search(gate[campo]) is None, f"{campo} cita PRD/Tech Spec/TS"
    assert "SPEC" in passos, "passos 1 e 3 devem citar SPEC"


def test_gate_referencias_decision_gates_existem():
    rules = _rules()
    refs = re.findall(r"decision_gates\.(\w+)", rules["gate_implementation_before_code"]["rule"])
    assert refs, "rule não referencia nenhuma decision_gates.<chave>"
    inexistentes = sorted({r for r in refs if r not in rules["decision_gates"]})
    assert not inexistentes, f"chaves inexistentes em decision_gates: {inexistentes}"
