"""Testes de consistência entre SKILL.md e workflow-rules.yaml (RF02, SDD-DTF-0034).

Não hardcode a tabela esperada aqui: leia do YAML, senão o teste não
pega divergência futura entre os dois arquivos.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from framework_lib import allowed_transitions  # noqa: E402

SKILL_MD_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "doc-traceability-framework"
    / "SKILL.md"
)


def _parse_skill_md_transitions(text: str) -> dict[str, set[str]]:
    """Extrai o resumo "Transições válidas: draft → in_review, ...; ..." do SKILL.md."""
    match = re.search(r"[Vv]álidas:\s*(.+?)\.", text, re.DOTALL)
    assert match, "SKILL.md não tem a frase 'Transições válidas: ...' esperada"
    parsed: dict[str, set[str]] = {}
    for fragment in match.group(1).split(";"):
        fragment = fragment.strip()
        if not fragment:
            continue
        state, _, targets = fragment.partition("→")
        state = state.strip()
        targets = {t.strip() for t in targets.split(",") if t.strip()}
        parsed[state] = targets
    return parsed


def test_status_lifecycle_matches_yaml():
    yaml_transitions = allowed_transitions()
    assert yaml_transitions, "workflow-rules.yaml não foi encontrado ou não tem status_lifecycle"

    skill_text = SKILL_MD_PATH.read_text(encoding="utf-8")
    skill_transitions = _parse_skill_md_transitions(skill_text)

    for state, yaml_targets in yaml_transitions.items():
        if not yaml_targets:
            # Estado terminal (ex.: archived: []) — SKILL.md pode omitir.
            continue
        assert state in skill_transitions, (
            f"SKILL.md não menciona transições de '{state}', mas o YAML tem: {yaml_targets}"
        )
        assert skill_transitions[state] == set(yaml_targets), (
            f"SKILL.md diz que '{state}' vai para {skill_transitions[state]}, "
            f"mas workflow-rules.yaml diz {set(yaml_targets)}"
        )

    for state in skill_transitions:
        assert state in yaml_transitions, (
            f"SKILL.md menciona transições de '{state}', que não existe em status_lifecycle do YAML"
        )
