#!/usr/bin/env python3
"""
check_hooks.py

Sensor de configuração dos hooks do harness — ver SDD-DTF-0020 (RF06).

render_prompts.py recusa gerar hook mudo, mas nada impede alguém de
escrever `.claude/settings.json` à mão com os mesmos defeitos. Este script
reprova, citando evento e matcher:

  1. hook `type: "prompt"` em SessionStart, PreCompact ou PostCompact
     (avaliador de turno único, não injeta texto na sessão);
  2. hook PostToolUse com `--report-only` (sempre exit 0: o modelo nunca vê);
  3. caminho `_framework/` sem o prefixo `${CLAUDE_PROJECT_DIR}/`
     (quebra depois de `cd` ou dentro de worktree);
  4. script `${CLAUDE_PROJECT_DIR}/...` inexistente;
  5. JSON ilegível.

Uso:
    python3 check_hooks.py [settings.json] [--report-only]

Default: .claude/settings.json. Exit 1 se houver problema; --report-only
sempre sai 0.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import report  # noqa: E402

PROJECT_DIR_PREFIX = "${CLAUDE_PROJECT_DIR}/"
PROMPT_FORBIDDEN_EVENTS = {"SessionStart", "PreCompact", "PostCompact"}


def _items(hook: dict) -> list[str]:
    """`command` e cada item de `args`, só os que são string."""
    items = [hook.get("command")]
    args = hook.get("args")
    if isinstance(args, list):
        items += args
    return [i for i in items if isinstance(i, str)]


def check_settings(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"settings.json ilegível: {exc}"]

    project_dir = path.resolve().parent.parent
    problems = []
    hooks_by_event = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks_by_event, dict):
        return problems

    for event, groups in hooks_by_event.items():
        for group in groups if isinstance(groups, list) else []:
            if not isinstance(group, dict):
                continue
            where = f"{event} (matcher {group.get('matcher', '')!r})"
            for hook in group.get("hooks") or []:
                if not isinstance(hook, dict):
                    continue
                if hook.get("type") == "prompt" and event in PROMPT_FORBIDDEN_EVENTS:
                    problems.append(
                        f'{where}: hook type "prompt" não injeta texto na sessão — use type "command" com stdout.'
                    )
                items = _items(hook)
                if event == "PostToolUse" and any("--report-only" in i for i in items):
                    problems.append(
                        f"{where}: hook com --report-only sai sempre 0 e o modelo nunca vê o resultado — "
                        "use exit 2 com stderr."
                    )
                for item in items:
                    if "_framework/" in item and not item.startswith(PROJECT_DIR_PREFIX):
                        problems.append(f"{where}: caminho '{item}' sem o prefixo {PROJECT_DIR_PREFIX}.")
                    if item.startswith(PROJECT_DIR_PREFIX):
                        target = project_dir / item[len(PROJECT_DIR_PREFIX) :]
                        if not target.exists():
                            problems.append(f"{where}: script referenciado inexistente: {target}.")
    return problems


def main() -> int:
    report_only = "--report-only" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = Path(args[0]) if args else Path(".claude/settings.json")
    problems = check_settings(path)
    return report(problems, [], f"✅ {path}: hooks ok.", report_only=report_only)


if __name__ == "__main__":
    sys.exit(main())
