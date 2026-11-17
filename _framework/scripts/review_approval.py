#!/usr/bin/env python3
"""
review_approval.py

Decide, sem rede, se as reviews de uma PR aprovam o documento e monta o
`approved_by` (SPEC-DTF-0030, RF03 a RF05). Quem chama busca as reviews
(`GET repos/<dono>/<repo>/pulls/<n>/reviews`) e as grava num arquivo.

Regra: só contam reviews de logins em `approvers` do registry central.
Aprova `APPROVED`, ou `COMMENTED` com o corpo exatamente `Aprovado`. A
decisiva é a mais recente entre as que aprovam e as `CHANGES_REQUESTED`;
vale se aprova e se foi feita sobre o head.

Uso:
    python3 review_approval.py <documento> --reviews <arquivo> --head <sha> --pr-url <url> [--json]

Exit 0 aprovação válida, 1 inválida, 2 entrada malformada.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from approval_hash import content_hash  # noqa: E402
from framework_lib import json_flag, read_frontmatter  # noqa: E402

SCHEMA_ID = "dtf.review-approval/1"
PR_URL_RE = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/pull/[0-9]+$")
REQUIRED_FIELDS = ("id", "user.login", "state", "commit_id", "submitted_at")


def approvers_for(path: Path) -> list[str] | None:
    """`approvers` do primeiro registry.yaml subindo a partir do documento; não lista, None."""
    for parent in [path if path.is_dir() else path.parent, *path.resolve().parents]:
        registry = parent / "registry.yaml"
        if registry.is_file():
            data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
            value = data.get("approvers") if isinstance(data, dict) else None
            return list(value) if isinstance(value, list) else None
    return None


def approves(review: dict) -> bool:
    if review.get("state") == "APPROVED":
        return True
    return review.get("state") == "COMMENTED" and (review.get("body") or "").strip() == "Aprovado"


def decide(reviews: list[dict], head: str, approvers: list[str]) -> dict:
    relevant = [
        r
        for r in reviews
        if (r.get("user") or {}).get("login") in approvers and (approves(r) or r.get("state") == "CHANGES_REQUESTED")
    ]
    if not relevant:
        return {"valida": False, "motivos": ["nenhuma review de aprovador"], "review": None}
    # sorted é estável: no empate de submitted_at, a que vem depois na lista fica por último.
    decisive = sorted(relevant, key=lambda r: str(r["submitted_at"]))[-1]
    login = decisive["user"]["login"]
    if decisive.get("state") == "CHANGES_REQUESTED":
        motivo = f"a review decisiva de {login} pede mudanças ({decisive['submitted_at']})"
        return {"valida": False, "motivos": [motivo], "review": None}
    if decisive.get("commit_id") != head:
        motivo = f"review sobre {decisive.get('commit_id')}, head é {head}: nova review necessária"
        return {"valida": False, "motivos": [motivo], "review": None}
    return {"valida": True, "motivos": [], "review": decisive}


def _malformed_reviews(path: Path) -> tuple[list | None, str | None]:
    try:
        reviews = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"arquivo de reviews ilegível: {exc}"
    if not isinstance(reviews, list):
        return None, "arquivo de reviews não é lista JSON"
    for i, review in enumerate(reviews):
        if not isinstance(review, dict):
            return None, f"review {i} não é objeto"
        for field in REQUIRED_FIELDS:
            if field == "user.login":
                present = isinstance(review.get("user"), dict) and review["user"].get("login") is not None
            else:
                present = review.get(field) is not None
            if not present:
                return None, f"review {i} sem {field}"
    return reviews, None


def _emit(as_json: bool, documento: str, head: str, motivos: list[str], approved_by: dict | None, code: int) -> int:
    if as_json:
        objeto = {
            "schema": SCHEMA_ID,
            "documento": documento,
            "valida": approved_by is not None,
            "motivos": motivos,
            "head": head,
            "approved_by": approved_by,
        }
        print(json.dumps(objeto, ensure_ascii=False, indent=2))
    elif approved_by is not None:
        print(yaml.safe_dump({"approved_by": approved_by}, allow_unicode=True, sort_keys=False), end="")
    else:
        for motivo in motivos:
            print(motivo, file=sys.stderr)
    return code


def main() -> int:
    argv, as_json = json_flag(sys.argv[1:])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("documento")
    parser.add_argument("--reviews", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--pr-url", required=True)
    args = parser.parse_args(argv)

    path = Path(args.documento)
    documento = path.name
    if not path.is_file():
        return _emit(as_json, documento, args.head, [f"Não encontrado: {path}"], None, 2)
    try:
        fm, _ = read_frontmatter(path)
    except ValueError as exc:
        return _emit(as_json, documento, args.head, [str(exc)], None, 2)
    if not fm:
        return _emit(as_json, documento, args.head, [f"{path}: documento sem front-matter"], None, 2)
    documento = str(fm.get("id") or path.name)

    if not PR_URL_RE.match(args.pr_url):
        motivo = "--pr-url fora do formato https://github.com/<dono>/<repo>/pull/<n>"
        return _emit(as_json, documento, args.head, [motivo], None, 2)
    reviews, problema = _malformed_reviews(Path(args.reviews))
    if problema:
        return _emit(as_json, documento, args.head, [problema], None, 2)

    approvers = approvers_for(path)
    if approvers is None:
        return _emit(as_json, documento, args.head, ["approvers não declarado no registry"], None, 1)
    status = fm.get("status")
    if status != "in_review":
        return _emit(as_json, documento, args.head, [f"documento está {status}, não in_review"], None, 1)

    decisao = decide(reviews, args.head, approvers)
    if not decisao["valida"]:
        return _emit(as_json, documento, args.head, decisao["motivos"], None, 1)
    review = decisao["review"]
    approved_by = {
        "kind": "human",
        "actor": review["user"]["login"],
        "at": str(review["submitted_at"]),
        "content_sha256": content_hash(path),
        "evidence": f"{args.pr_url}#pullrequestreview-{review['id']}",
    }
    return _emit(as_json, documento, args.head, [], approved_by, 0)


if __name__ == "__main__":
    sys.exit(main())
