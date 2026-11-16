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

import fnmatch
import json
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
_FALLBACK_OPERATIONAL_ARTIFACTS = ("LESSONS.md", "HANDOFF.md", "validation.md", "validation-*.md")


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


def is_operational_artifact(name: str) -> bool:
    """Nome casa com alguma chave de operational_artifacts (glob, sensível a maiúsculas)."""
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in OPERATIONAL_ARTIFACTS)


def iter_documents(docs_dir: Path):
    """
    Percorre os .md de documento sob docs_dir, ignorando registry.md e
    INDEX.md (saídas geradas, sem front-matter),
    qualquer arquivo dentro de templates/ (templates têm placeholder por
    desenho — validar template como documento é falso positivo garantido)
    e os artefatos operacionais (LESSONS.md, HANDOFF.md, validation*.md),
    que o framework manda criar sem front-matter.
    """
    for path in sorted(docs_dir.rglob("*.md")):
        if path.name in ("registry.md", "INDEX.md") or is_operational_artifact(path.name):
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


RESULT_SCHEMA_ID = "dtf.resultado-validador/1"
_LEADING_ID_RE = re.compile(r"^(" + ID_PATTERN.pattern.replace(r"\b", "", 1) + r"):")


def json_flag(argv: list[str]) -> tuple[list[str], bool]:
    """Tira `--json` dos argumentos e diz se estava presente (SPEC-DTF-0028, RF01)."""
    return [a for a in argv if a != "--json"], "--json" in argv


def _item(message: str) -> dict:
    """Mensagem com o id do documento quando ela começa por um id seguido de `:` (RF02)."""
    found = _LEADING_ID_RE.match(message)
    return {"documento": found.group(1) if found else None, "mensagem": message}


def report(
    problems,
    warnings,
    ok_message: str,
    report_only: bool = False,
    *,
    as_json: bool = False,
    script: str = "",
) -> int:
    """
    Imprime avisos e problemas no formato usado por todos os validators.
    Retorna o exit code: 0 se não houver problema (ou se report_only), 1 caso
    contrário. Com `as_json`, imprime só o objeto de
    `_framework/schemas/resultado-validador.schema.json`, com o mesmo exit
    code (SPEC-DTF-0028).
    """
    exit_code = 1 if problems and not report_only else 0
    if as_json:
        print(
            json.dumps(
                {
                    "schema": RESULT_SCHEMA_ID,
                    "script": script,
                    "framework_version": (load_rules().get("framework") or {}).get("version"),
                    "ok": not problems,
                    "exit_code": exit_code,
                    "problemas": [_item(p) for p in problems],
                    "avisos": [_item(w) for w in warnings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return exit_code

    for w in warnings:
        print(f"⚠️  {w}")

    if problems:
        print(f"❌ {len(problems)} problema(s) encontrado(s):")
        for p in problems:
            print(f"  - {p}")
        if report_only:
            print("\n(modo --report-only: exit 0 mesmo com problemas)")
        return exit_code

    print(ok_message)
    return 0


def run_main(main, script: str, argv: list[str]) -> int:
    """Roda `main`; com `--json`, um erro operacional vira problema no JSON, com exit 1 (SPEC-DTF-0028)."""
    if "--json" not in argv:
        return main()
    try:
        return main()
    except SystemExit as saida:
        if saida.code is None or isinstance(saida.code, int):
            raise
        return report([f"erro operacional: {saida.code}"], [], "", as_json=True, script=script)
    except Exception as erro:  # noqa: BLE001 — qualquer erro operacional vira resultado legível
        return report([f"erro operacional: {type(erro).__name__}: {erro}"], [], "", as_json=True, script=script)


def usage_error(doc: str, as_json: bool, script: str) -> int:
    """Uso inválido: imprime o docstring, ou o devolve como problema no JSON. Exit 1, como antes."""
    if as_json:
        return report([doc.strip()], [], "", as_json=True, script=script)
    print(doc)
    return 1


_ESCAPED_PIPE = "\\|"
_SENTINEL = "\x00"


def split_table_row(line: str) -> list[str]:
    """Células de uma linha de tabela markdown, com strip() em cada uma.

    O par barra-pipe é conteúdo de célula (GFM) e volta desescapado como
    um pipe simples. Sem par escapado, equivale a
    [c.strip() for c in line.strip("|").split("|")].
    """
    masked = line.replace(_ESCAPED_PIPE, _SENTINEL)
    return [c.strip().replace(_SENTINEL, "|") for c in masked.strip("|").split("|")]
