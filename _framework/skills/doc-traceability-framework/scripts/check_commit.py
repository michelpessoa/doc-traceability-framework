#!/usr/bin/env python3
"""
check_commit.py

Checa mensagens de commit: formato Conventional Commits e, opcionalmente,
referência a um id do framework.

Motivação: hoje o vínculo commit↔documento é reconstruído DEPOIS pelo
`registry_tools.py audit` — arqueologia sobre o histórico. Checar na hora
do commit faz o vínculo nascer junto com ele, e reduz a auditoria ao papel
que ela deveria ter: rede de segurança para quem não opera sob o framework
(workflow-rules.yaml, seção 11).

Uso:
    python3 check_commit.py <arquivo_com_a_mensagem>      # hook commit-msg
    python3 check_commit.py --range <git_range>           # ex.: main..HEAD
    python3 check_commit.py --last <N>
    ... [--require-refs] [--report-only]

--require-refs transforma "commit sem id do framework" de aviso em erro.
Fora dele, a convenção de referência segue sendo recomendada e não
obrigatória, como a seção 11 define.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import ID_PATTERN, report  # noqa: E402

CONVENTIONAL = re.compile(
    r"^(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"(?P<scope>\([^)]+\))?(?P<breaking>!)?: (?P<subject>.+)$"
)

MAX_SUBJECT = 72

# Tipos em que a ausência de id do framework é mais suspeita: mudam
# comportamento do produto, logo deveriam ter uma SDD/PRD/TS por trás.
IMPLEMENTATION_TYPES = {"feat", "fix", "perf", "refactor"}


def check_message(message: str, label: str, require_refs: bool) -> tuple[list, list]:
    problems, warnings = [], []
    lines = [ln for ln in message.strip().splitlines()]
    if not lines:
        return [f"{label}: mensagem vazia."], []

    subject = lines[0].strip()
    if subject.startswith("Merge ") or subject.startswith("Revert "):
        return [], []

    m = CONVENTIONAL.match(subject)
    if not m:
        problems.append(
            f"{label}: assunto fora de Conventional Commits — "
            f"'{subject[:60]}'. Esperado 'tipo(escopo): descrição'."
        )
        return problems, warnings

    if len(subject) > MAX_SUBJECT:
        warnings.append(f"{label}: assunto com {len(subject)} caracteres (>{MAX_SUBJECT}).")

    if len(lines) > 1 and lines[1].strip():
        problems.append(f"{label}: falta linha em branco entre assunto e corpo.")

    ids = set(ID_PATTERN.findall(message))
    if not ids and m.group("type") in IMPLEMENTATION_TYPES:
        msg = (
            f"{label}: commit '{m.group('type')}' sem id do framework na mensagem "
            "(ex.: 'Refs: SDD-PROJETO-0001')."
        )
        (problems if require_refs else warnings).append(msg)

    return problems, warnings


def messages_from_range(rev_range: str) -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "log", "--pretty=format:%H%x00%B%x00---END---", rev_range],
        capture_output=True, text=True, check=True,
    ).stdout
    result = []
    for chunk in out.split("---END---"):
        chunk = chunk.strip("\n\x00 ")
        if not chunk:
            continue
        sha, _, body = chunk.partition("\x00")
        result.append((sha[:8], body.strip()))
    return result


def main() -> int:
    argv = sys.argv[1:]
    report_only = "--report-only" in argv
    require_refs = "--require-refs" in argv
    positional = [a for a in argv if not a.startswith("--")]

    entries: list[tuple[str, str]] = []
    if "--range" in argv:
        idx = argv.index("--range")
        entries = messages_from_range(argv[idx + 1])
    elif "--last" in argv:
        idx = argv.index("--last")
        entries = messages_from_range(f"-{argv[idx + 1]}")
    elif positional:
        path = Path(positional[0])
        if not path.is_file():
            raise SystemExit(f"Não encontrado: {path}")
        entries = [(path.name, path.read_text(encoding="utf-8"))]
    else:
        print(__doc__)
        return 1

    problems, warnings = [], []
    for label, message in entries:
        # Comentários do template de commit não fazem parte da mensagem.
        clean = "\n".join(ln for ln in message.splitlines() if not ln.startswith("#"))
        p, w = check_message(clean, label, require_refs)
        problems += p
        warnings += w

    return report(
        problems,
        warnings,
        f"✅ {len(entries)} mensagem(ns) de commit no formato esperado.",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
