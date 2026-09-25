"""Testes de consistência entre SKILL.md e workflow-rules.yaml (RF02, SDD-DTF-0034).

Não hardcode a tabela esperada aqui: leia do YAML, senão o teste não
pega divergência futura entre os dois arquivos.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from framework_lib import allowed_transitions, load_rules, read_frontmatter  # noqa: E402

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


# --- SDD-DTF-0044: skills enxutas (RF01 a RF07) ---------------------------

SKILL_BUDGET_BYTES = 9216
DESCRIPTION_MAX_CHARS = 450
POINTER = re.compile(r"workflow-rules\.yaml:([a-z_]+)")

FRAMEWORK_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = FRAMEWORK_DIR.parent
SKILL_DIR = FRAMEWORK_DIR / "skills" / "doc-traceability-framework"
REFERENCES_DIR = SKILL_DIR / "references"
PROCEDURE_SKILLS = ("handover", "pickup", "verify-sdd")
ACTIVE_TYPES = ("STRAT", "RFC", "ADR", "SPEC", "SDD", "BASE", "INC", "PM")
SIZING_LEVELS = ("small", "medium", "large", "complex")
REFERENCE_FILES = ("incidents.md", "onboarding.md", "audit.md")


def _scanned_files() -> list[Path]:
    """Arquivos varridos para ponteiros e "seção N"."""
    files = [SKILL_MD_PATH] + [REFERENCES_DIR / name for name in REFERENCE_FILES]
    files += [FRAMEWORK_DIR / "skills" / s / "SKILL.md" for s in PROCEDURE_SKILLS]
    return files


def _normalize(text: str) -> str:
    """Mesma normalização de check_renderings.py."""
    text = re.sub(r"[`*]", "", text)
    return " ".join(text.replace(".", "").lower().split())


def _iron_laws() -> dict[str, str]:
    rules = load_rules()
    return {
        key: value["iron_law"]
        for key, value in rules.items()
        if isinstance(value, dict) and value.get("iron_law")
    }


def test_skill_md_within_size_budget():
    size = SKILL_MD_PATH.stat().st_size
    assert size <= SKILL_BUDGET_BYTES, (
        f"SKILL.md tem {size} bytes, teto {SKILL_BUDGET_BYTES}; "
        "mova conteúdo para references/, não suba o teto"
    )
    text = SKILL_MD_PATH.read_text(encoding="utf-8")
    for doc_type in ACTIVE_TYPES:
        assert re.search(rf"\b{doc_type}\b", text), f"SKILL.md não menciona o tipo {doc_type}"
    for level in SIZING_LEVELS:
        assert level in text, f"SKILL.md não menciona o nível {level}"
    assert "Transições válidas:" in text
    assert "O que fazer em cada pedido comum" in text


def test_skill_md_has_every_iron_law_with_pointer():
    laws = _iron_laws()
    assert laws, "workflow-rules.yaml não tem nenhuma chave com iron_law"
    text = SKILL_MD_PATH.read_text(encoding="utf-8")
    norm_text = _normalize(text)
    pointers = set(POINTER.findall(text))
    for key, law in laws.items():
        assert _normalize(law) in norm_text, (
            f"SKILL.md não tem a iron law de `{key}` inteira: {law!r}"
        )
        assert key in pointers, f"SKILL.md não tem o ponteiro `workflow-rules.yaml:{key}`"


def test_skill_md_has_no_rationalization_tables_or_section_numbers():
    for line in SKILL_MD_PATH.read_text(encoding="utf-8").splitlines():
        assert not (line.lstrip().startswith("|") and "Racionalização" in line), (
            f"tabela 'Racionalização' no roteador: {line!r}"
        )
        assert not re.search(r"[Ss]eção\s+\d", line), f"citação 'seção N' no roteador: {line!r}"
    for path in _scanned_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            assert not re.search(r"[Ss]eção\s+\d", line), (
                f"{path.name}: citação 'seção N': {line!r}"
            )


def test_yaml_pointers_resolve_to_top_level_keys():
    keys = set(load_rules().keys())
    for path in _scanned_files():
        for key in POINTER.findall(path.read_text(encoding="utf-8")):
            assert key in keys, (
                f"{path.relative_to(FRAMEWORK_DIR)}: ponteiro para chave inexistente no YAML: {key!r}"
            )


def test_references_exist_and_are_cited():
    skill_text = SKILL_MD_PATH.read_text(encoding="utf-8")
    for name in REFERENCE_FILES:
        path = REFERENCES_DIR / name
        assert path.is_file(), f"references/{name} ausente em {REFERENCES_DIR}"
        assert f"references/{name}" in skill_text, f"references/{name} existe mas o SKILL.md não o cita"
    cited = set(re.findall(r"references/([A-Za-z0-9_.-]+)", skill_text))
    for name in cited - {"workflow-rules.yaml"}:
        assert (REFERENCES_DIR / name).is_file(), f"SKILL.md cita references/{name}, que não existe"
    on_disk = {p.name for p in REFERENCES_DIR.iterdir() if p.is_file()}
    for name in on_disk - {"workflow-rules.yaml"}:
        assert name in cited, f"references/{name} existe e nunca é citado no SKILL.md"
    assert "Leia sob demanda" in skill_text


def test_moved_sections_keep_normative_content():
    expected = {
        "incidents.md": ("root_cause_key", "SEV1", "90 dias"),
        "audit.md": ("prompts/framework-audit.md",),
        "onboarding.md": ("prompts/onboarding-bootstrap.md",),
    }
    for name, needles in expected.items():
        text = (REFERENCES_DIR / name).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"references/{name} perdeu {needle!r}"
    skill_text = SKILL_MD_PATH.read_text(encoding="utf-8")
    for forbidden in ("SEV1", "root_cause_key"):
        assert forbidden not in skill_text, f"SKILL.md ainda contém {forbidden!r}, que é de references/"


def _all_skill_mds() -> list[Path]:
    return sorted((FRAMEWORK_DIR / "skills").glob("*/SKILL.md"))


def test_skill_descriptions_within_limit_and_triggers():
    paths = _all_skill_mds()
    assert len(paths) == 4, f"esperava 4 skills, achei {[p.parent.name for p in paths]}"
    for path in paths:
        skill = path.parent.name
        try:
            fm, _ = read_frontmatter(path)
        except ValueError as exc:
            raise AssertionError(f"{skill}: front-matter inválido — {exc}") from exc
        description = fm.get("description")
        assert isinstance(description, str) and description.strip(), (
            f"{skill}: front-matter inválido ou sem description"
        )
        description = description.rstrip("\n")
        assert len(description) <= DESCRIPTION_MAX_CHARS, (
            f"{skill}: description tem {len(description)} caracteres, teto {DESCRIPTION_MAX_CHARS}"
        )
        assert "Use when" in description, f"{skill}: description sem 'Use when'"
        assert "Do NOT use for" in description, f"{skill}: description sem 'Do NOT use for'"


def test_procedure_skills_use_repo_root_path():
    if shutil.which("git") is None:
        pytest.skip("git ausente no ambiente de teste")
    for skill in PROCEDURE_SKILLS:
        text = (FRAMEWORK_DIR / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        command = f'cat "$(git rev-parse --show-toplevel)/_framework/procedures/{skill}.md"'
        assert command in text, f"{skill}/SKILL.md não contém o comando: {command}"
        assert f"_framework/procedures/{skill}.md" in text
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0 and result.stdout.strip(), (
            f"{skill}: comando não resolveu de _framework/tests/: {result.stderr!r}"
        )


def test_claude_skills_layout_exposes_skill_dir():
    link = REPO_ROOT / ".claude" / "skills" / "doc-traceability-framework"
    assert os.path.islink(link), (
        f"{link} não é symlink de pasta (RF07 exige symlink; checkout com core.symlinks=false?)"
    )
    target = os.readlink(link)
    assert target == "../../_framework/skills/doc-traceability-framework", (
        f"symlink aponta para {target!r}"
    )
    resolved = link.resolve()
    assert resolved == SKILL_DIR.resolve(), f"symlink resolve para {resolved}, fora da skill"
    for rel in ("SKILL.md", "references/incidents.md", "references/onboarding.md",
                "references/audit.md", "references/workflow-rules.yaml",
                "prompts/onboarding-bootstrap.md", "prompts/framework-audit.md"):
        assert (link / rel).is_file(), f"{rel} não resolve a partir de {link}"
    for other in PROCEDURE_SKILLS:
        assert (REPO_ROOT / ".claude" / "skills" / other / "SKILL.md").is_file()
