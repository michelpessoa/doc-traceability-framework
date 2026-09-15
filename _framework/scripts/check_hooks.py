#!/usr/bin/env python3
"""
check_hooks.py

Sensor de configuração dos hooks do harness — ver SDD-DTF-0020 (RF06) e
SDD-DTF-0027 (regra 3: tokenização com shlex).

render_prompts.py recusa gerar hook mudo, mas nada impede alguém de
escrever `.claude/settings.json` à mão com os mesmos defeitos. Este script
reprova, citando evento e matcher:

  1. hook `type: "prompt"` em SessionStart, PreCompact ou PostCompact
     (avaliador de turno único, não injeta texto na sessão);
  2. hook PostToolUse com `--report-only` (sempre exit 0: o modelo nunca vê);
  3. caminho `_framework/` sem referência reconhecível a
     `${CLAUDE_PROJECT_DIR}` — `command` é tokenizado com `shlex.split`
     antes de checar (SDD-DTF-0027), então formas de shell válidas como
     `"python3 ${CLAUDE_PROJECT_DIR}/x.py"` ou
     `'python3 "$CLAUDE_PROJECT_DIR"/x.py'` (exemplo da documentação
     oficial) são aceitas, não só a forma sem shell
     `"${CLAUDE_PROJECT_DIR}/x.py"`;
  4. script `${CLAUDE_PROJECT_DIR}/...` inexistente;
  5. JSON ilegível.

Uso:
    python3 check_hooks.py [settings.json] [--report-only]

Default: .claude/settings.json. Exit 1 se houver problema; --report-only
sempre sai 0.
"""

import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import report  # noqa: E402

# Formas de shell aceitas para referenciar o diretório do projeto: com
# chaves (forma canônica do kit) e sem chaves (forma do exemplo oficial
# de hooks do Claude Code, tipicamente entre aspas — shlex já remove as
# aspas na tokenização, então o token vira "$CLAUDE_PROJECT_DIR/...").
PROJECT_DIR_PREFIXES = ("${CLAUDE_PROJECT_DIR}/", "$CLAUDE_PROJECT_DIR/")
PROMPT_FORBIDDEN_EVENTS = {"SessionStart", "PreCompact", "PostCompact"}


def _items(hook: dict) -> list[str]:
    """`command` e cada item de `args`, só os que são string.

    Usado só para a checagem de substring de `--report-only` — não precisa
    de tokenização shell, substring funciona igual na string inteira.
    """
    items = [hook.get("command")]
    args = hook.get("args")
    if isinstance(args, list):
        items += args
    return [i for i in items if isinstance(i, str)]


def _tokens(hook: dict) -> list[str]:
    """Tokens shell-conscientes de `command` + itens de `args`.

    `command` pode ser uma linha de shell inteira (a forma da
    documentação oficial, ex. `"python3 ${CLAUDE_PROJECT_DIR}/x.py"` ou
    `'python3 "$CLAUDE_PROJECT_DIR"/x.py'`), não só o executável isolado
    — por isso é tokenizado com `shlex.split` antes de procurar a
    referência ao diretório do projeto, em vez de exigir que a string
    inteira comece pelo prefixo. Quociação malformada cai para a string
    inteira como um único token (mesmo comportamento estrito de antes,
    nunca fica mais permissivo). Itens de `args` já chegam como tokens
    discretos do JSON (não passam por shell) e não são retokenizados.
    """
    tokens: list[str] = []
    command = hook.get("command")
    if isinstance(command, str):
        try:
            tokens.extend(shlex.split(command))
        except ValueError:
            tokens.append(command)
    args = hook.get("args")
    if isinstance(args, list):
        tokens.extend(a for a in args if isinstance(a, str))
    return tokens


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
                for token in _tokens(hook):
                    prefix = next((p for p in PROJECT_DIR_PREFIXES if token.startswith(p)), None)
                    if "_framework/" in token and prefix is None:
                        problems.append(
                            f"{where}: caminho '{token}' sem o prefixo ${{CLAUDE_PROJECT_DIR}}/ "
                            "(nem a variante $CLAUDE_PROJECT_DIR/)."
                        )
                    if prefix is not None:
                        target = project_dir / token[len(prefix) :]
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
