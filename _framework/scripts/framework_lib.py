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


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# ---------------------------------------------------------------------------
# Constantes canônicas
# ---------------------------------------------------------------------------
# Estas constantes são DERIVADAS de workflow-rules.yaml no import, não
# redeclaradas aqui. Até a v1.7.0 o YAML se chamava "fonte única de verdade"
# mas nenhum programa o lia — os tipos e status viviam hardcoded no script,
# e as duas cópias só não divergiram por sorte.
#
# Os valores abaixo são fallback para uso fora do repositório (script
# copiado solto, kit não encontrado). Se o YAML for achado, ele vence.

_FALLBACK_DOC_TYPES = ["STRAT", "RFC", "ADR", "SPEC", "PRD", "TS", "SDD", "BASE", "INC", "PM"]
_FALLBACK_STATUSES = {
    "draft",
    "in_review",
    "approved",
    "rejected",
    "implemented",
    "superseded",
    "archived",
}
_FALLBACK_INCIDENT_STATUSES = {"open", "mitigated", "resolved", "closed"}
# Arquivos que o framework manda criar dentro das pastas de documento mas
# que não são documento: sem front-matter, sem id, fora do registry.
_FALLBACK_OPERATIONAL_ARTIFACTS = ("LESSONS.md", "HANDOFF.md")


def _derive_constants():
    """Lê workflow-rules.yaml e devolve (tipos, status, status de incidente,
    artefatos operacionais)."""
    try:
        rules = load_rules()
    except Exception:
        rules = {}

    # Tipos legados (PRD, TS) saíram de document_types na v2.1.0 mas seguem
    # válidos em projeto já mapeado: sem a união, ID_PATTERN pararia de
    # reconhecer ids PRD-*/TS-* já emitidos (lessons_policy.non_retroactive).
    active = list((rules.get("document_types") or {}).keys())
    legacy = list((rules.get("legacy_document_types") or {}).keys())
    types = active + [t for t in legacy if t not in active] or _FALLBACK_DOC_TYPES
    statuses = set((rules.get("status_lifecycle") or {}).get("states") or ()) or _FALLBACK_STATUSES
    incident = set((rules.get("incident_lifecycle") or {}).get("states") or ()) or _FALLBACK_INCIDENT_STATUSES
    artifacts = tuple(rules.get("operational_artifacts") or ()) or _FALLBACK_OPERATIONAL_ARTIFACTS
    return types, statuses, incident, artifacts


DOC_TYPES, VALID_STATUSES, INCIDENT_STATUSES, OPERATIONAL_ARTIFACTS = _derive_constants()

# Tipos ordenados por tamanho decrescente: sem isso a alternância do regex
# casaria "TS" dentro de um id que começa com outro prefixo mais longo.
ID_PATTERN = re.compile(r"\b(?:" + "|".join(sorted(DOC_TYPES, key=len, reverse=True)) + r")-[A-Z0-9]+-\d{4}\b")


def allowed_transitions(doc_type: str = None) -> dict:
    """Transições de status válidas, lidas do YAML (vazio se não achado)."""
    rules = load_rules()
    key = "incident_lifecycle" if doc_type == "INC" else "status_lifecycle"
    return (rules.get(key) or {}).get("allowed_transitions") or {}


def sizing_levels() -> list:
    """Níveis de sizing (seção 19), lidos do YAML."""
    return (load_rules().get("sizing") or {}).get("levels") or []


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
    return fm, text[m.end() :]


def iter_documents(docs_dir: Path):
    """
    Percorre os .md de documento sob docs_dir, ignorando registry.md,
    qualquer arquivo dentro de templates/ (templates têm placeholder por
    desenho — validar template como documento é falso positivo garantido)
    e os artefatos operacionais (LESSONS.md, HANDOFF.md), que o framework
    manda criar sem front-matter.
    """
    for path in sorted(docs_dir.rglob("*.md")):
        if path.name == "registry.md" or path.name in OPERATIONAL_ARTIFACTS:
            continue
        if "templates" in path.parts:
            continue
        yield path


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def project_version(path: Path) -> str | None:
    """
    Versão do framework sob a qual o projeto DONO deste arquivo opera —
    campo `framework_version` do registry.yaml mais próximo subindo a
    árvore. É o que torna a não-retroatividade mecânica: uma regra
    introduzida na 1.7.0 não pode reprovar documento de projeto mapeado
    sob 1.6.0.
    """
    for parent in [path if path.is_dir() else path.parent, *path.resolve().parents]:
        registry = parent / "registry.yaml"
        if registry.is_file():
            data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
            version = data.get("framework_version")
            return str(version) if version else None
    return None


def rule_applies(rule_since: str, project: str | None) -> bool:
    """
    Uma regra vale para um documento se o projeto opera sob uma versão
    igual ou posterior à que introduziu a regra. Projeto sem versão
    declarada é tratado como atual — declarar é responsabilidade do
    registry, e o validator já reclama da ausência.
    """
    if not project:
        return True
    return version_key(project) >= version_key(rule_since)


def version_date(rules: dict, version: str) -> str | None:
    """Data (YYYY-MM-DD) em que `version` entrou no changelog, ou None se
    a versão não tiver `date` registrada (changelog anterior a essa
    convenção)."""
    fw = rules.get("framework") or {}
    for entry in fw.get("changelog") or []:
        if entry.get("version") == version:
            return entry.get("date")
    return None


def rule_applies_since_date(rules: dict, rule_since: str, doc_created: str | None, project: str | None) -> bool:
    """
    Uma regra de conteúdo (RULE_SINCE) vale para um documento se ele foi
    CRIADO em ou depois da data em que a regra passou a existir — não se
    o registry do projeto declara uma versão recente. Isso é o que torna
    a não-retroatividade granular por documento: subir `framework_version`
    do registry (projeto decide adotar SPEC/2.x daqui pra frente) não pode
    reprovar retroativamente documento antigo que a regra nova nunca
    poderia ter guiado.

    Sem `date` conhecida para `rule_since` (changelog legado) ou sem
    `created` no documento, cai no comportamento anterior por versão do
    projeto (`rule_applies`) — nunca menos rígido, só menos preciso.
    """
    since_date = version_date(rules, rule_since)
    if since_date and doc_created:
        return str(doc_created) >= since_date
    return rule_applies(rule_since, project)


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
