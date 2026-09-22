#!/usr/bin/env python3
"""
selftest.py

Mecaniza a mutação dos validadores do kit: para cada mutação declarada
em `mutations.yaml`, aplica `find`→`replace` no validador, roda a suíte
de teste indicada, confirma que ela falha (mutante morto), e reverte o
arquivo ao conteúdo original. Reporta mutante sobrevivente (suíte
passou com a mutação aplicada) e mutação não aplicável (`find` ausente
no código atual) como falha (SDD-DTF-0038, RF01-RF04).

Uso:
    python3 selftest.py [mutations.yaml]
"""

import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import report  # noqa: E402

DEFAULT_MUTATIONS = Path(__file__).resolve().parent / "tests" / "mutations.yaml"
KIT_ROOT = Path(__file__).resolve().parent.parent.parent


def apply_mutation(target: Path, find: str, replace: str) -> str:
    """Aplica `find`→`replace` em `target`, retorna o conteúdo original
    (para revert). Levanta ValueError se `find` não estiver presente —
    nunca aplica silenciosamente."""
    original = target.read_text(encoding="utf-8")
    if find not in original:
        raise ValueError(f"`find` não encontrado em {target}: {find!r}")
    target.write_text(original.replace(find, replace, 1), encoding="utf-8")
    return original


def run_mutation(mutation: dict, kit_root: Path) -> dict:
    """Aplica a mutação, roda o `test_file` via pytest, reverte sempre.
    Retorna {"survived": bool, "error": str | None}."""
    target = kit_root / mutation["validator"]
    test_file = kit_root / mutation["test_file"]

    if not target.is_file():
        return {"survived": False, "error": f"validator inexistente: {target}"}
    if not test_file.is_file():
        return {"survived": False, "error": f"test_file inexistente: {test_file}"}

    try:
        original = apply_mutation(target, mutation["find"], mutation["replace"])
    except ValueError as exc:
        return {"survived": False, "error": str(exc)}

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-q"],
            capture_output=True,
            text=True,
        )
        survived = result.returncode == 0
        return {"survived": survived, "error": None}
    finally:
        try:
            target.write_text(original, encoding="utf-8")
        except OSError as exc:
            raise SystemExit(
                f"FALHA AO REVERTER {target} — estado mutado ficou no disco: {exc}"
            ) from exc


def main() -> int:
    mutations_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MUTATIONS
    if not mutations_path.is_file():
        raise SystemExit(f"Não encontrado: {mutations_path}")

    mutations = yaml.safe_load(mutations_path.read_text(encoding="utf-8")) or []

    problems = []
    for mutation in mutations:
        outcome = run_mutation(mutation, KIT_ROOT)
        label = f"{mutation['validator']} — {mutation['description']}"
        if outcome["error"] is not None:
            problems.append(f"{label}: mutação não aplicável — {outcome['error']}")
        elif outcome["survived"]:
            problems.append(
                f"{label}: mutante SOBREVIVEU — `{mutation['test_file']}` não "
                f"discriminou a mutação `{mutation['find']}` → `{mutation['replace']}`."
            )

    return report(
        problems,
        [],
        f"✅ {len(mutations)} mutação(ões): todos os mutantes morreram.",
    )


if __name__ == "__main__":
    sys.exit(main())
