"""Testes de `mechanization` em render_prompts.py — ver SDD-DTF-0009.

Cobre os RF01-RF04 e RF07 com fixtures mínimas de `rules`, sem depender
do workflow-rules.yaml real (que muda com o tempo) para os casos
sintéticos, e usa o YAML real só onde o teste é justamente "o gerado bate
com o que está em disco".
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from framework_lib import find_rules_file, load_rules  # noqa: E402
from render_prompts import (  # noqa: E402
    build_claude_agent,
    build_claude_command,
    build_claude_settings,
    build_guard_bash,
    find_capability,
    validate_mechanizations,
)


def _cap(id_, **kw):
    base = {"id": id_, "description": f"desc {id_}"}
    base.update(kw)
    return base


def test_build_claude_settings_agrupa_por_evento():
    rules = {
        "capabilities": [
            _cap(
                "pickup_handoff",
                mechanization={
                    "artifact_type": "hook_sessionstart",
                    "matcher": "*",
                    "prompt": "faça pickup",
                },
            ),
            _cap(
                "enforce_branch_before_commit",
                mechanization={
                    "artifact_type": "hook_pretooluse",
                    "matcher": "Bash",
                    "hook_command": ["bash", "_framework/scripts/guard_bash.sh"],
                },
            ),
            _cap("create_document"),  # sem mechanization — não deve gerar nada
        ]
    }
    settings = json.loads(build_claude_settings(rules))
    assert sorted(settings["hooks"].keys()) == ["PreToolUse", "SessionStart"]
    assert settings["hooks"]["SessionStart"][0]["matcher"] == "*"
    assert settings["hooks"]["SessionStart"][0]["hooks"][0]["type"] == "prompt"
    assert settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "bash"


def test_build_claude_agent_e_command():
    agent_cap = _cap(
        "verify_sdd_independently",
        procedure="procedures/verify-sdd.md",
        mechanization_filename="sdd-verifier",
    )
    agent_md = build_claude_agent(agent_cap, {})
    assert agent_md.startswith("---\nname: sdd-verifier\n")
    assert "procedures/verify-sdd.md" in agent_md
    assert "verify_sdd_independently" in agent_md

    command_cap = _cap(
        "audit_repo_adherence",
        mechanization={"hook_command": ["python3", "_framework/scripts/framework_check.py", "--auto"]},
        mechanization_filename="framework-check",
    )
    command_md = build_claude_command(command_cap, {})
    assert "python3 _framework/scripts/framework_check.py --auto" in command_md
    assert "audit_repo_adherence" in command_md


def test_build_guard_bash_padroes_identicos_ao_atual():
    """A migração para gerado não pode mudar o que o script recusa —
    compara o guard_bash.sh gerado a partir do YAML real com o arquivo
    hoje em disco."""
    rules_path = find_rules_file(Path(__file__).resolve().parents[3])
    rules = load_rules(rules_path)
    gerado = build_guard_bash(rules)
    em_disco = (Path(__file__).resolve().parents[1] / "guard_bash.sh").read_text()
    assert gerado == em_disco


def test_capacidade_sem_mechanization_nao_gera_hook():
    rules = {"capabilities": [_cap("create_document")]}
    settings = json.loads(build_claude_settings(rules))
    assert settings["hooks"] == {}


def test_find_capability_ausente_leva_erro_nomeando_id():
    with pytest.raises(ValueError, match="nao-existe"):
        find_capability({"capabilities": []}, "nao-existe")


def test_validate_mechanizations_rejeita_artifact_type_desconhecido():
    rules = {
        "capabilities": [
            _cap("x", mechanization={"artifact_type": "bogus"}),
        ]
    }
    with pytest.raises(SystemExit, match="bogus"):
        validate_mechanizations(rules)


def test_validate_mechanizations_rejeita_colisao_de_filename():
    rules = {
        "capabilities": [
            _cap("a", mechanization={"artifact_type": "command"}),
            _cap("b", mechanization={"artifact_type": "command"}, mechanization_filename="a"),
        ]
    }
    with pytest.raises(SystemExit, match="colisão"):
        validate_mechanizations(rules)
