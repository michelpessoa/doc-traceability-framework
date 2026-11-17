#!/usr/bin/env python3
"""
approval_hash.py

Hash do conteúdo aprovado de um documento (SPEC-DTF-0029, RF04): sha256
do corpo, sem o front-matter, com CRLF normalizado para LF e sem as seções
de `approval_policy.hash_excluded_sections` — as que o próprio framework
manda preencher depois da aprovação. É o valor de
`approved_by.content_sha256`, conferido por `validate_state.py`.

Uso:
    python3 approval_hash.py <documento> [--json]

Exit 1 se o documento não existir ou não tiver front-matter.
"""

import hashlib
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import FRONTMATTER_RE, json_flag, load_rules  # noqa: E402

SCHEMA_ID = "dtf.approval-hash/1"


def excluded_sections() -> list[str]:
    """Títulos de `approval_policy.hash_excluded_sections`; chave ausente, nenhum."""
    policy = load_rules().get("approval_policy") or {}
    return list(policy.get("hash_excluded_sections") or [])


def split_document(path: Path) -> tuple[str, str]:
    """(front-matter, corpo) com CRLF normalizado; ValueError sem front-matter."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: documento sem front-matter")
    return m.group(1), text[m.end() :]


def hashed_body(body: str, excluded: list[str]) -> str:
    """Corpo sem as seções `## ` excluídas, sem espaço no fim das linhas e sem linhas em branco no fim."""
    kept, skipping = [], False
    for line in body.split("\n"):
        if line.startswith("## "):
            title = line[3:].strip()
            skipping = any(title.startswith(item) for item in excluded)
        if not skipping:
            kept.append(line.rstrip())
    return "\n".join(kept).rstrip("\n")


def content_hash(path: Path, excluded: list[str] | None = None) -> str:
    if excluded is None:
        excluded = excluded_sections()
    _, body = split_document(path)
    return hashlib.sha256(hashed_body(body, excluded).encode("utf-8")).hexdigest()


def main() -> int:
    args, as_json = json_flag(sys.argv[1:])
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 1
    path = Path(args[0])
    if not path.is_file():
        print(f"Não encontrado: {path}", file=sys.stderr)
        return 1
    try:
        front, _ = split_document(path)
        digest = content_hash(path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not as_json:
        print(digest)
        return 0

    fm = yaml.safe_load(front) or {}
    print(
        json.dumps(
            {
                "schema": SCHEMA_ID,
                "documento": str(fm.get("id") or path.name) if isinstance(fm, dict) else path.name,
                "content_sha256": digest,
                "secoes_excluidas": excluded_sections(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
