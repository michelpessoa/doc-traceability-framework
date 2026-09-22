#!/usr/bin/env python3
"""
ci_gate_verify_sdd.py

Camada 2 (obrigatória, tool-agnostic) do gate `verify-sdd`
(workflow-rules.yaml, seção 16, `gate_scope_verification`): script de CI
que bloqueia merge de PR que muda uma SDD para `implemented` sem
`validation-SDD-{ID}.md` de veredito PASS real, cobertura completa de
RF-ID e critérios de aceite não afrouxados entre `approved` e
`implemented` — com válvula de escape para incidente ativo validada
contra o registry central (SDD-DTF-0032, SPEC-DTF-0011, ADR-DTF-0004,
ADR-DTF-0005).

Uso:
    python3 ci_gate_verify_sdd.py --base <sha> --head <sha>
        --project-code <CODE> [--central-registry-path <path>]
        --pr-labels <label1,label2,...> --pr-body-file <path> [--json]

Roda `git show <rev>:<path>` no repositório corrente (cwd) para comparar
front-matter entre base e head — nunca regex sobre texto de diff.

Códigos de saída:
    0 = gate passou.
    1 = gate reprovado (falha de conteúdo/evidência).
    2 = erro operacional (front-matter que não parseia, ou registry
        central inacessível quando a válvula de escape foi usada).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402
from framework_lib import FRONTMATTER_RE  # noqa: E402

RF_ID_RE = re.compile(r"\bRF-?\d+\b")
INC_ID_RE = re.compile(r"\bINC-[A-Z0-9]+-\d{4}\b")
VEREDITO_PASS_RE = re.compile(r"\*\*Veredito:\*\*\s*PASS\b")
INCIDENT_OVERRIDE_LABEL = "incident-override"
OPEN_INCIDENT_STATUSES = {"open", "mitigated"}


class GateOperationalError(Exception):
    """Erro operacional (exit 2) — não é reprovação de conteúdo."""


# ---------------------------------------------------------------------------
# Contratos (SDD-DTF-0032)
# ---------------------------------------------------------------------------


@dataclass
class SddCheckResult:
    sdd_id: str
    status_transition: str | None
    outcome: str  # "pass" | "fail" | "skipped"
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "sdd_id": self.sdd_id,
            "status_transition": self.status_transition,
            "outcome": self.outcome,
            "reasons": self.reasons,
        }


@dataclass
class OverrideLog:
    inc_id: str
    status: str
    timestamp: str

    def to_dict(self) -> dict:
        return {"inc_id": self.inc_id, "status": self.status, "timestamp": self.timestamp}


@dataclass
class GateResult:
    passed: bool
    per_sdd: list[SddCheckResult]
    overrides_used: list[OverrideLog]

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "per_sdd": [r.to_dict() for r in self.per_sdd],
            "overrides_used": [o.to_dict() for o in self.overrides_used],
        }


@dataclass
class OverrideCheck:
    """Resultado de `validate_incident_override`."""

    applies: bool
    ok: bool = False
    error: str | None = None
    log: OverrideLog | None = None


# ---------------------------------------------------------------------------
# Git / parsing
# ---------------------------------------------------------------------------


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def read_file_at_revision(revision: str, path: str) -> str | None:
    """Conteúdo de `path` em `revision`, ou None se não existir lá."""
    result = _git("show", f"{revision}:{path}")
    if result.returncode != 0:
        return None
    return result.stdout


def parse_frontmatter_at_revision(revision: str, path: str) -> tuple[dict, str] | None:
    """(front-matter, corpo) de `path` em `revision`, ou None se o
    arquivo não existir naquela revisão (RF01).

    Levanta `GateOperationalError` (RF09) se o bloco de front-matter
    existir mas não parsear como YAML válido — nunca tratado como
    ausência silenciosa de mudança de status.
    """
    text = read_file_at_revision(revision, path)
    if text is None:
        return None
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise GateOperationalError(f"{path}@{revision}: sem bloco de front-matter.")
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise GateOperationalError(f"{path}@{revision}: front-matter não é YAML válido — {exc}") from exc
    if not isinstance(fm, dict):
        raise GateOperationalError(f"{path}@{revision}: front-matter não é um mapa YAML.")
    return fm, text[m.end() :]


def discover_renames(base: str, head: str, pathspec: str = "docs/sdd/SDD-*.md") -> dict[str, str | None]:
    """head_path -> old_path (None se o arquivo nasceu em `head`, sem
    equivalente em `base`) — resolve rename antes de comparar status
    (RF01, caso de borda "SDD renomeada/movida")."""
    result = _git("diff", "--find-renames", "--name-status", f"{base}..{head}", "--", pathspec)
    mapping: dict[str, str | None] = {}
    if result.returncode != 0:
        return mapping
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) == 3:
            old, new = parts[1], parts[2]
            mapping[new] = old
        elif status in ("A", "M") and len(parts) == 2:
            path = parts[1]
            mapping[path] = path if status == "M" else None
    return mapping


def section_body(body: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^#{{2,3}}\s*{re.escape(heading)}.*?$(.*?)(?=^#{{2,3}}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else None


def table_with_header(section: str) -> tuple[list[str], list[list[str]]]:
    """(cabeçalho normalizado em minúsculas, linhas de dados), ignorando
    blocos cercados por ``` — mesmo padrão de validate_state.py."""
    rows = []
    in_fence = False
    for line in section.splitlines():
        line = line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not any(cells):
            continue
        if all(set(c) <= set("-: ") for c in cells if c):
            continue
        rows.append(cells)
    if not rows:
        return [], []
    return [h.lower() for h in rows[0]], rows[1:]


def normalize_row(cells: list[str]) -> str:
    """Conteúdo normalizado de uma linha de critério, sem a coluna `#`
    (índice) — reordenar linhas não conta como alteração (RF05, caso de
    borda "reordenado")."""
    body_cells = cells[1:] if len(cells) > 1 else cells
    return " ".join(" ".join(body_cells).split()).lower()


# ---------------------------------------------------------------------------
# RF02-RF05
# ---------------------------------------------------------------------------


def check_validation_presence(sdd_id: str, head: str) -> tuple[str, str] | list[str]:
    """RF02: presença de `validation-{sdd_id}.md` com `**Veredito:** PASS`.

    Retorna (path, texto) em caso de sucesso de presença, ou lista de
    motivos de falha (arquivo ausente).
    """
    path = f"docs/sdd/validation-{sdd_id}.md"
    text = read_file_at_revision(head, path)
    if text is None:
        return [f"{path} ausente para transição approved->implemented (RF02)."]
    return path, text


def check_rf_coverage(sdd_id: str, sdd_body: str, validation_text: str) -> list[str]:
    """RF03: todo RF-ID de 'Requisitos consolidados' tem linha de
    evidência correspondente em `validation_text`."""
    consolidated = section_body(sdd_body, "Requisitos consolidados") or sdd_body
    rf_ids = sorted(set(RF_ID_RE.findall(consolidated)), key=lambda r: r.upper())
    if not rf_ids:
        return []
    _, rows = table_with_header(validation_text)
    covered = set()
    for row in rows:
        covered |= set(RF_ID_RE.findall(" | ".join(row)))
    missing = [r for r in rf_ids if r not in covered and r.upper() not in {c.upper() for c in covered}]
    return [f"{sdd_id}: RF-ID {rf} sem linha de evidência em validation-{sdd_id}.md (RF03)." for rf in missing]


def check_evidence_rows(sdd_id: str, validation_text: str) -> list[str]:
    """RF04: recusa PASS contradito por linha — qualquer linha da tabela
    de evidência com resultado != PASS reprova, mesmo com o `**Veredito:**`
    global dizendo PASS (tlc-spec-lean E1)."""
    header, rows = table_with_header(validation_text)
    if not rows:
        return []
    idx = next((i for i, h in enumerate(header) if "passou" in h), None)
    if idx is None:
        return []
    problems = []
    for row in rows:
        if idx >= len(row):
            continue
        value = row[idx].strip().lower()
        if value not in ("sim", "yes", "pass"):
            problems.append(
                f"{sdd_id}: linha de evidência com resultado '{row[idx]}' != PASS "
                f"(RF04) mesmo que o veredito global diga PASS."
            )
    return problems


def check_criteria_frozen(sdd_id: str, base_body: str, head_body: str, pr_body: str) -> list[str]:
    """RF05: critério removido/alterado entre `approved` e `implemented`
    sem `**Justificativa de mudança:**` citando o RF-ID no corpo do PR
    reprova (tlc-spec-lean E2). Comparação por conteúdo normalizado —
    reordenar linha com texto idêntico não conta como alteração."""
    base_section = section_body(base_body, "Critérios de aceite / definição de pronto") or section_body(
        base_body, "Critérios de aceite"
    )
    head_section = section_body(head_body, "Critérios de aceite / definição de pronto") or section_body(
        head_body, "Critérios de aceite"
    )
    if base_section is None:
        return []
    _, base_rows = table_with_header(base_section)
    _, head_rows = table_with_header(head_section or "")
    head_normalized = {normalize_row(r) for r in head_rows}

    problems = []
    for row in base_rows:
        normalized = normalize_row(row)
        if normalized in head_normalized:
            continue
        rf_ids = RF_ID_RE.findall(" ".join(row))
        rf_id = rf_ids[0] if rf_ids else f"critério #{row[0] if row else '?'}"
        justified = bool(
            re.search(r"\*\*Justificativa de mudança:\*\*.*" + re.escape(rf_id), pr_body or "", re.IGNORECASE)
        )
        if not justified:
            problems.append(
                f"{sdd_id}: critério de {rf_id} alterado/removido entre approved e implemented sem "
                f"'**Justificativa de mudança:**' citando {rf_id} no corpo do PR (RF05)."
            )
    return problems


# ---------------------------------------------------------------------------
# RF06-RF08 — válvula de escape
# ---------------------------------------------------------------------------


def validate_incident_override(
    pr_labels: list[str], pr_body: str, project_code: str, central_registry_path: str | None
) -> OverrideCheck:
    """RF06/RF07/RF08: label `incident-override` + `INC-{ID}` no corpo do
    PR só libera a válvula se o INC existir no registry central e estiver
    `open`/`mitigated`. Levanta `GateOperationalError` (exit 2) se o
    registry central não puder ser lido — nunca confundido com "INC não
    encontrado" (exit 1)."""
    if INCIDENT_OVERRIDE_LABEL not in (pr_labels or []):
        return OverrideCheck(applies=False)
    inc_ids = INC_ID_RE.findall(pr_body or "")
    if not inc_ids:
        # Label sozinha não libera — RF06, caso de borda.
        return OverrideCheck(applies=False)
    inc_id = inc_ids[0]

    if not central_registry_path:
        raise GateOperationalError("falha ao acessar o registry central: caminho não fornecido (RF07).")

    registry_file = Path(central_registry_path)
    try:
        data = yaml.safe_load(registry_file.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise GateOperationalError(f"falha ao acessar o registry central: {exc} (RF07).") from exc
    except yaml.YAMLError as exc:
        raise GateOperationalError(f"falha ao acessar o registry central: YAML inválido — {exc} (RF07).") from exc

    entry = next((d for d in data.get("documents", []) if d.get("id") == inc_id), None)
    timestamp = datetime.now(timezone.utc).isoformat()
    if entry is None:
        return OverrideCheck(applies=True, ok=False, error=f"INC {inc_id} não encontrado no registry central (RF07).")
    status = entry.get("status")
    if status not in OPEN_INCIDENT_STATUSES:
        return OverrideCheck(
            applies=True,
            ok=False,
            error=f"INC {inc_id} em status '{status}', esperado open/mitigated (RF07).",
        )
    return OverrideCheck(applies=True, ok=True, log=OverrideLog(inc_id=inc_id, status=status, timestamp=timestamp))


# ---------------------------------------------------------------------------
# Avaliação por SDD e agregada
# ---------------------------------------------------------------------------


def evaluate_sdd(
    base: str, head: str, old_path: str | None, head_path: str, override: OverrideCheck, pr_body: str = ""
) -> SddCheckResult:
    head_parsed = parse_frontmatter_at_revision(head, head_path)
    if head_parsed is None:
        return SddCheckResult(head_path, None, "skipped", ["arquivo ausente em head."])
    fm_head, body_head = head_parsed
    sdd_id = fm_head.get("id") or Path(head_path).stem
    status_head = fm_head.get("status")

    status_base = None
    body_base = ""
    if old_path:
        base_parsed = parse_frontmatter_at_revision(base, old_path)
        if base_parsed:
            fm_base, body_base = base_parsed
            status_base = fm_base.get("status")

    transition = f"{status_base} -> {status_head}" if status_base != status_head else None

    if status_head != "implemented" or status_base == "implemented":
        return SddCheckResult(sdd_id, transition, "skipped", ["não é transição para implemented."])

    if override.applies and override.ok:
        return SddCheckResult(sdd_id, transition, "pass", [f"liberado por válvula de escape ({override.log.inc_id})."])

    reasons: list[str] = []
    if override.applies and not override.ok and override.error:
        reasons.append(override.error)

    presence = check_validation_presence(sdd_id, head)
    if isinstance(presence, list):
        reasons += presence
        return SddCheckResult(sdd_id, transition, "fail", reasons)
    validation_path, validation_text = presence

    if not VEREDITO_PASS_RE.search(validation_text):
        reasons.append(f"{validation_path} não contém a linha '**Veredito:** PASS' (RF02).")

    reasons += check_rf_coverage(sdd_id, body_head, validation_text)
    reasons += check_evidence_rows(sdd_id, validation_text)

    if status_base == "approved":
        reasons += check_criteria_frozen(sdd_id, body_base, body_head, pr_body)

    outcome = "fail" if reasons else "pass"
    return SddCheckResult(sdd_id, transition, outcome, reasons)


def evaluate_gate(
    base: str,
    head: str,
    changed_sdd_paths: list[str],
    pr_labels: list[str],
    pr_body: str,
    project_code: str,
    central_registry_path: str | None = None,
) -> GateResult:
    override = validate_incident_override(pr_labels, pr_body, project_code, central_registry_path)
    renames = discover_renames(base, head)

    per_sdd = []
    for head_path in changed_sdd_paths:
        old_path = renames.get(head_path, head_path)
        result = evaluate_sdd(base, head, old_path, head_path, override, pr_body)
        per_sdd.append(result)

    passed = all(r.outcome != "fail" for r in per_sdd)
    overrides_used = [override.log] if override.applies and override.ok and override.log else []
    return GateResult(passed=passed, per_sdd=per_sdd, overrides_used=overrides_used)


def collect_pr_labels(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [label.strip() for label in raw.split(",") if label.strip()]


def discover_changed_sdd_paths(base: str, head: str) -> list[str]:
    result = _git("diff", "--find-renames", "--name-only", f"{base}..{head}", "--", "docs/sdd/SDD-*.md")
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def format_report(gate: GateResult) -> str:
    lines = []
    for r in gate.per_sdd:
        icon = {"pass": "✅", "fail": "❌", "skipped": "⏭️ "}[r.outcome]
        lines.append(f"{icon} {r.sdd_id} ({r.status_transition or 'sem transição'}): {r.outcome}")
        for reason in r.reasons:
            lines.append(f"    - {reason}")
    for o in gate.overrides_used:
        lines.append(f"🔓 override aceito: {o.inc_id} (status {o.status}, {o.timestamp}).")
    lines.append("✅ gate passou." if gate.passed else "❌ gate reprovado.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--project-code", required=True)
    parser.add_argument("--central-registry-path", default=None)
    parser.add_argument("--pr-labels", default="")
    parser.add_argument("--pr-body-file", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pr_body = Path(args.pr_body_file).read_text(encoding="utf-8") if args.pr_body_file else ""
    pr_labels = collect_pr_labels(args.pr_labels)
    changed = discover_changed_sdd_paths(args.base, args.head)

    if not changed:
        print("✅ PR não toca nenhuma docs/sdd/SDD-*.md — gate passa trivialmente.")
        return 0

    try:
        gate = evaluate_gate(
            args.base,
            args.head,
            changed,
            pr_labels,
            pr_body,
            args.project_code,
            args.central_registry_path,
        )
    except GateOperationalError as exc:
        print(f"❌ erro operacional: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(gate.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(gate))

    return 0 if gate.passed else 1


if __name__ == "__main__":
    sys.exit(main())
