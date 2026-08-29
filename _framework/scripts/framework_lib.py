#!/usr/bin/env python3
"""
framework_lib.py

Base compartilhada pelos validators do framework. Concentra o que antes
estava duplicado em cada script: leitura de front-matter, leitura das
constantes canônicas de workflow-rules.yaml e resolução de caminhos.

Nenhum validator deve redeclarar status, tipos ou o padrão de id — tudo
vem daqui, e daqui vem de workflow-rules.yaml sempre que o arquivo estiver
acessível (fallback embutido só para uso fora do repositório).

Requer PyYAML (pip install pyyaml --break-system-packages).
"""
import re
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constantes canônicas (fallback — a fonte real é workflow-rules.yaml)
# ---------------------------------------------------------------------------

DOC_TYPES = ["STRAT", "RFC", "ADR", "PRD", "TS", "SDD", "BASE", "INC", "PM"]

ID_PATTERN = re.compile(r"\b(?:" + "|".join(DOC_TYPES) + r")-[A-Z0-9]+-\d{4}\b")

VALID_STATUSES = {
    "draft", "in_review", "approved", "rejected",
    "implemented", "superseded", "archived",
}
# INC não usa o ciclo de vida padrão (workflow-rules.yaml, incident_lifecycle)
INCIDENT_STATUSES = {"open", "mitigated", "resolved", "closed"}

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


# ---------------------------------------------------------------------------
# Front-matter
# ---------------------------------------------------------------------------

def read_frontmatter(path: Path):
    """
    Retorna (frontmatter_dict, corpo_markdown).

    Documento sem bloco de front-matter retorna ({}, texto_inteiro) — quem
    chama decide se isso é erro no contexto dele.
    """
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: front-matter não é YAML válido — {exc}") from exc
    if not isinstance(fm, dict):
        raise ValueError(f"{path}: front-matter não é um mapa YAML")
    return fm, text[m.end():]


def iter_documents(docs_dir: Path):
    """
    Percorre os .md de documento sob docs_dir, ignorando registry.md e
    qualquer arquivo dentro de templates/ (templates têm placeholder por
    desenho — validar template como documento é falso positivo garantido).
    """
    for path in sorted(docs_dir.rglob("*.md")):
        if path.name == "registry.md":
            continue
        if "templates" in path.parts:
            continue
        yield path


# ---------------------------------------------------------------------------
# Regras canônicas
# ---------------------------------------------------------------------------

def find_rules_file(start: Path = None) -> Path | None:
    """
    Sobe a partir de `start` (ou deste arquivo) procurando
    _framework/rules/workflow-rules.yaml. Retorna None se não achar —
    os validators seguem com os fallbacks embutidos.
    """
    base = (start or Path(__file__)).resolve()
    for parent in [base, *base.parents]:
        candidate = parent / "_framework" / "rules" / "workflow-rules.yaml"
        if candidate.is_file():
            return candidate
        candidate = parent / "rules" / "workflow-rules.yaml"
        if candidate.is_file():
            return candidate
    return None


def load_rules(start: Path = None) -> dict:
    """Carrega workflow-rules.yaml. Retorna {} se o arquivo não for achado."""
    path = find_rules_file(start)
    if not path:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def framework_versions(rules: dict) -> tuple[str | None, list[str]]:
    """
    Retorna (versão_atual, todas_as_versões_conhecidas) a partir do bloco
    `framework` de workflow-rules.yaml.

    "Conhecidas" = as que aparecem no changelog + a atual. É o que permite
    ao validator distinguir um registry legitimamente parado numa versão
    antiga (projeto mapeado sob ela, ver `framework_version` no registry)
    de um registry com valor inventado.
    """
    fw = rules.get("framework") or {}
    current = fw.get("version")
    known = {entry.get("version") for entry in (fw.get("changelog") or [])}
    known.discard(None)
    if current:
        known.add(current)
    return current, sorted(known, key=version_key)


def version_key(v: str) -> tuple:
    """Chave de ordenação semver-ish tolerante a lixo."""
    parts = []
    for chunk in str(v).split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def load_registry(docs_dir: Path):
    """Retorna (dados_do_registry, {id: entrada})."""
    path = docs_dir / "registry.yaml"
    if not path.exists():
        raise SystemExit(f"Não encontrado: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    docs = {d["id"]: d for d in data.get("documents", [])}
    return data, docs


def registry_mode(data: dict) -> str:
    """
    'project'  -> registry só contém SDD (repositório de projeto)
    'central'  -> registry do repositório central (todos os outros tipos)
    """
    types = {d.get("type") for d in data.get("documents", [])}
    if types and types <= {"SDD"}:
        return "project"
    return "central"


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

def report(problems, warnings, ok_message: str, report_only: bool = False) -> int:
    """
    Imprime avisos e problemas no formato usado por todos os validators.
    Retorna o exit code: 0 se não houver problema (ou se report_only), 1 caso
    contrário.
    """
    for w in warnings:
        print(f"⚠️  {w}")

    if problems:
        print(f"❌ {len(problems)} problema(s) encontrado(s):")
        for p in problems:
            print(f"  - {p}")
        if report_only:
            print("\n(modo --report-only: exit 0 mesmo com problemas)")
            return 0
        return 1

    print(ok_message)
    return 0
