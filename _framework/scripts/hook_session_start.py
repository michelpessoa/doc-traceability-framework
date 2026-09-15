#!/usr/bin/env python3
"""
hook_session_start.py

Hook SessionStart do Claude Code — ver SDD-DTF-0020 (RF01, RF02).

Hook `type: "prompt"` não injeta texto na sessão; o que um hook
SessionStart imprime em stdout, sim. Por isso a instrução ao modelo sai
daqui, por stdout.

Uso (gerado em .claude/settings.json por render_prompts.py):
    python3 hook_session_start.py pickup        # matcher "*"
    python3 hook_session_start.py post-compact  # matcher "compact"

Sempre sai 0: payload inválido ou modo desconhecido não imprimem nada
(falha aberta, mesmo princípio de guard_bash.sh) — check_hooks.py é quem
pega configuração errada.
"""

import json
import os
import sys
from pathlib import Path

PICKUP_MESSAGE = (
    "HANDOFF.md encontrado em: {paths}. Antes de qualquer outra coisa, use a skill pickup: "
    "confirme o status real dos ids citados e releia do disco os arquivos que vai alterar."
)

POST_COMPACT_MESSAGE = (
    "O contexto desta sessão foi compactado. Se o trabalho do fluxo vai continuar em outra "
    "sessão, use a skill handover para atualizar HANDOFF.md referenciando os ids dos documentos."
)


def project_root(payload: dict) -> Path:
    """CLAUDE_PROJECT_DIR > payload["cwd"] > diretório corrente do processo."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    return Path.cwd()


def find_handoffs(root: Path) -> list[Path]:
    """HANDOFF.md da raiz primeiro, depois docs/*/HANDOFF.md ordenados; só existentes."""
    candidates = [root / "HANDOFF.md", *sorted(root.glob("docs/*/HANDOFF.md"))]
    return [p for p in candidates if p.is_file()]


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else None
    if mode not in {"pickup", "post-compact"}:
        return 0
    try:
        payload = json.loads(sys.stdin.read())
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0

    if mode == "post-compact":
        print(POST_COMPACT_MESSAGE)
        return 0

    root = project_root(payload)
    handoffs = find_handoffs(root)
    if handoffs:
        paths = ", ".join(str(p.relative_to(root)) for p in handoffs)
        print(PICKUP_MESSAGE.format(paths=paths))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
