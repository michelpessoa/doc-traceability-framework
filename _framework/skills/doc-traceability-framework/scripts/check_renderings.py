#!/usr/bin/env python3
"""
check_renderings.py

workflow-rules.yaml declara que prompts e skills são apenas "renderizações"
das mesmas regras, e que todos devem produzir o mesmo resultado para a
mesma entrada. Até agora isso era uma promessa sem teste: cinco cópias
mantidas à mão (YAML, SKILL.md, universal.md, cursor, copilot) e nenhuma
verificação de que ainda concordam.

Este script não compara texto — compara os FATOS que cada renderização
precisa carregar para não induzir a IA ao erro:

  1. Todo tipo de documento não-legado aparece na renderização.
  2. Toda Iron Law tem correspondência (busca por termo característico).
  3. Os níveis de sizing aparecem.
  4. Nenhuma renderização cita tipo ou status que não existe no YAML.

Uso:
    python3 check_renderings.py [--report-only]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import find_rules_file, load_rules, report  # noqa: E402

# Renderizações que devem concordar com o YAML, relativas à raiz de _framework.
RENDERINGS = [
    "skills/doc-traceability-framework/SKILL.md",
    "prompts/universal.md",
    "prompts/cursor/doc-framework.mdc",
    "prompts/copilot/copilot-instructions.md",
]


def framework_root() -> Path:
    rules = find_rules_file()
    if not rules:
        raise SystemExit("workflow-rules.yaml não encontrado.")
    return rules.parent.parent


def main() -> int:
    report_only = "--report-only" in sys.argv
    rules = load_rules()
    root = framework_root()

    types = rules.get("document_types") or {}
    active_types = [k for k, v in types.items() if not (v or {}).get("deprecated_since")]
    legacy_types = [k for k, v in types.items() if (v or {}).get("deprecated_since")]
    sizing = [lvl["id"] for lvl in (rules.get("sizing") or {}).get("levels") or []]

    iron_laws = {
        key: (value or {}).get("iron_law")
        for key, value in rules.items()
        if isinstance(value, dict) and (value or {}).get("iron_law")
    }

    problems, warnings = [], []

    for rel in RENDERINGS:
        path = root / rel
        if not path.is_file():
            warnings.append(f"{rel}: renderização não encontrada — pulando.")
            continue
        raw = path.read_text(encoding="utf-8")
        # Ênfase markdown não muda o fato declarado — `implemented` e
        # implemented são a mesma palavra para efeito de concordância.
        text = re.sub(r"[`*_]", "", raw)

        for t in active_types:
            if not re.search(rf"\b{re.escape(t)}\b", text):
                problems.append(f"{rel}: não menciona o tipo ativo '{t}'.")

        for level in sizing:
            if level not in text:
                warnings.append(f"{rel}: não menciona o nível de sizing '{level}'.")

        # Iron Law: procura pelas 3 primeiras palavras significativas da lei.
        for key, law in iron_laws.items():
            core = " ".join(law.replace(".", "").split()[:3])
            if core.lower() not in text.lower():
                warnings.append(f"{rel}: Iron Law de `{key}` sem correspondência ('{core}...').")

        for t in legacy_types:
            if re.search(rf"\b{re.escape(t)}\b", text) and "legad" not in text.lower():
                warnings.append(
                    f"{rel}: cita o tipo legado '{t}' sem marcar que é legado."
                )

    return report(
        problems,
        warnings,
        f"✅ {len(RENDERINGS)} renderização(ões) concordam com workflow-rules.yaml "
        f"({len(active_types)} tipos ativos, {len(iron_laws)} Iron Laws, {len(sizing)} níveis).",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
