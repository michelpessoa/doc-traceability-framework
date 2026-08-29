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
LINK = re.compile(r"\]\(([^)\s]+)\)")

RENDERINGS = [
    "skills/doc-traceability-framework/SKILL.md",
    "prompts/universal.md",
    "prompts/cursor/doc-framework.mdc",
    "prompts/copilot/copilot-instructions.md",
    "../AGENTS.md",
]
# QUICKSTART.md fica de fora deste laço de propósito: é uma página só,
# sem o bloco de Iron Laws nem a tabela de sizing por desenho
# (build_quickstart não chama core_facts) — exigir cobertura total ali
# reprovaria sempre, não é uma divergência real.

# Capacidades de continuidade (SDD-DTF-0006) apontam para procedures/*.md
# via capabilities.<id>.procedure. Não entram em RENDERINGS: um stub de
# poucas linhas ou um procedimento de handover/pickup não tem por que
# citar todo tipo de documento ativo, e o laço de RENDERINGS exige isso
# — incluí-los ali reprovaria sempre, falso positivo estrutural. A
# checagem certa para eles é existência do arquivo referenciado.


def check_links(root: Path) -> list:
    """Links relativos que não resolvem em disco.

    Reorganizar documentação quebra referência em silêncio: o markdown
    continua renderizando, só leva a lugar nenhum. Varre a raiz do
    repositório (root.parent), não a de _framework.
    """
    problems = []
    repo = root.parent
    skip = {".git", "node_modules", "__pycache__", "examples"}
    for md in sorted(repo.rglob("*.md")):
        if skip & set(md.parts):
            continue
        for target in LINK.findall(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (md.parent / target.split("#")[0]).resolve().exists():
                problems.append(
                    f"{md.relative_to(repo)}: link relativo quebrado → '{target}'"
                )
    return problems


def check_capability_procedures(rules: dict, root: Path) -> list:
    """Toda capacidade com campo `procedure` tem que apontar para arquivo
    que existe de fato — sem isso, capabilities.<id>.procedure é uma
    promessa não verificada."""
    problems = []
    for cap in rules.get("capabilities") or []:
        procedure = cap.get("procedure")
        if not procedure:
            continue
        if not (root / procedure).is_file():
            problems.append(f"{cap.get('id')}: procedure aponta para {procedure} (não existe).")
    return problems


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
    # Desde a v2.1.0 os legados moram em chave própria; antes disso eram
    # entradas de document_types marcadas com deprecated_since.
    legacy_types = list((rules.get("legacy_document_types") or {}).keys()) or [
        k for k, v in types.items() if (v or {}).get("deprecated_since")
    ]
    sizing = [lvl["id"] for lvl in (rules.get("sizing") or {}).get("levels") or []]

    iron_laws = {
        key: (value or {}).get("iron_law")
        for key, value in rules.items()
        if isinstance(value, dict) and (value or {}).get("iron_law")
    }

    problems, warnings = [], []
    problems += check_links(root)
    problems += check_capability_procedures(rules, root)

    for rel in RENDERINGS:
        path = root / rel
        if not path.is_file():
            warnings.append(f"{rel}: renderização não encontrada — pulando.")
            continue
        raw = path.read_text(encoding="utf-8")
        # Ênfase markdown não muda o fato declarado — `implemented` e
        # implemented são a mesma palavra para efeito de concordância.
        # Underscore NÃO entra aqui: removê-lo transformaria `in_review`
        # em "inreview" e faria a lei nunca casar.
        text = re.sub(r"[`*]", "", raw)

        for t in active_types:
            if not re.search(rf"\b{re.escape(t)}\b", text):
                problems.append(f"{rel}: não menciona o tipo ativo '{t}'.")

        for level in sizing:
            if level not in text:
                warnings.append(f"{rel}: não menciona o nível de sizing '{level}'.")

        # Iron Law: a lei inteira, normalizada. Comparar só o começo deixa
        # passar divergência no resto — foi assim que uma lei ficou falando
        # de PRD/TS depois de o tipo virar SPEC.
        norm_text = " ".join(text.lower().split())
        for key, law in iron_laws.items():
            norm_law = " ".join(law.replace(".", "").lower().split())
            if norm_law not in norm_text:
                problems.append(f"{rel}: Iron Law de `{key}` diverge ou ausente: \"{law}\"")

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
