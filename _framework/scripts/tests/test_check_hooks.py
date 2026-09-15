"""Testes de check_hooks.py — ver SDD-DTF-0020 (RF06).

Um caso por regra com `settings.json` em tmp_path/.claude/ (o
`${CLAUDE_PROJECT_DIR}` resolve para tmp_path), um válido e o
`.claude/settings.json` real do kit.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_hooks import check_settings  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_ARG = "${CLAUDE_PROJECT_DIR}/_framework/scripts/hook.py"


def _settings(tmp_path: Path, hooks: dict, with_script: bool = True) -> Path:
    if with_script:
        script = tmp_path / "_framework/scripts/hook.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("")
    path = tmp_path / ".claude/settings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"hooks": hooks}), encoding="utf-8")
    return path


def _command(*args: str) -> dict:
    return {"type": "command", "command": "python3", "args": list(args)}


def test_valido_sem_problema(tmp_path):
    hooks = {
        "SessionStart": [{"matcher": "*", "hooks": [_command(SCRIPT_ARG, "pickup")]}],
        "PostToolUse": [{"matcher": "Edit|Write", "hooks": [_command(SCRIPT_ARG)]}],
    }
    assert check_settings(_settings(tmp_path, hooks)) == []


def test_command_shell_com_prefixo_com_chaves(tmp_path):
    """SDD-DTF-0027: "python3 ${CLAUDE_PROJECT_DIR}/x.py" como `command` único (sem `args`)."""
    hooks = {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": f"python3 {SCRIPT_ARG}"}]}]}
    assert check_settings(_settings(tmp_path, hooks)) == []


def test_command_shell_com_prefixo_sem_chaves_entre_aspas(tmp_path):
    """SDD-DTF-0027: forma do exemplo oficial de hooks, `"$CLAUDE_PROJECT_DIR"/x.py`."""
    hooks = {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'python3 "$CLAUDE_PROJECT_DIR"/_framework/scripts/hook.py',
                    }
                ],
            }
        ]
    }
    assert check_settings(_settings(tmp_path, hooks)) == []


def test_command_shell_sem_referencia_reprova(tmp_path):
    """SDD-DTF-0027: shlex tokeniza, mas continua reprovando sem qualquer referência ao diretório do projeto."""
    hooks = {
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 _framework/scripts/hook.py"}]}
        ]
    }
    problems = check_settings(_settings(tmp_path, hooks))
    assert len(problems) == 1
    assert "PreToolUse" in problems[0] and "sem o prefixo" in problems[0]


def test_prompt_em_sessionstart(tmp_path):
    hooks = {"SessionStart": [{"matcher": "*", "hooks": [{"type": "prompt", "prompt": "faça pickup"}]}]}
    problems = check_settings(_settings(tmp_path, hooks))
    assert len(problems) == 1
    assert "SessionStart" in problems[0] and "'*'" in problems[0] and "prompt" in problems[0]


def test_prompt_em_precompact(tmp_path):
    hooks = {"PreCompact": [{"matcher": "*", "hooks": [{"type": "prompt", "prompt": "handover"}]}]}
    problems = check_settings(_settings(tmp_path, hooks))
    assert len(problems) == 1 and "PreCompact" in problems[0]


def test_report_only_em_posttooluse(tmp_path):
    hooks = {"PostToolUse": [{"matcher": "Edit|Write", "hooks": [_command(SCRIPT_ARG, "--auto", "--report-only")]}]}
    problems = check_settings(_settings(tmp_path, hooks))
    assert len(problems) == 1
    assert "PostToolUse" in problems[0] and "Edit|Write" in problems[0] and "--report-only" in problems[0]


def test_caminho_relativo(tmp_path):
    hooks = {"PreToolUse": [{"matcher": "Bash", "hooks": [_command("_framework/scripts/hook.py")]}]}
    problems = check_settings(_settings(tmp_path, hooks))
    assert len(problems) == 1
    assert "PreToolUse" in problems[0] and "sem o prefixo" in problems[0]


def test_script_inexistente(tmp_path):
    hooks = {"PreToolUse": [{"matcher": "Bash", "hooks": [_command(SCRIPT_ARG)]}]}
    problems = check_settings(_settings(tmp_path, hooks, with_script=False))
    assert len(problems) == 1
    assert "inexistente" in problems[0] and "hook.py" in problems[0]


def test_json_invalido(tmp_path):
    path = tmp_path / ".claude/settings.json"
    path.parent.mkdir(parents=True)
    path.write_text("{quebrado", encoding="utf-8")
    problems = check_settings(path)
    assert len(problems) == 1
    assert problems[0].startswith("settings.json ilegível: ")


def test_settings_real_do_kit_sem_problema():
    assert check_settings(REPO_ROOT / ".claude/settings.json") == []
