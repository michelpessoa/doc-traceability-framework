#!/usr/bin/env python3
"""
registry_tools.py

Ferramentas de linha de comando sobre docs/registry.yaml, implementando
as capacidades "validate_registry" e "trace" descritas em
_framework/rules/workflow-rules.yaml (seção 8).

Uso:
    python3 registry_tools.py validate <caminho_para_docs>
    python3 registry_tools.py trace <caminho_para_docs> <ID>
    python3 registry_tools.py audit <git_log_file> <docs_dir_1> [<docs_dir_2> ...]

validate: procura ids duplicados, referências quebradas em relates_to/
          parent_*, status inválidos, divergência entre o front-matter do
          .md e a entrada do registry, documento em disco fora do registry,
          `path` que não resolve, `framework_version` desconhecida e
          `source_docs` sem url utilizável.
          Aceita --report-only para listar sem falhar (exit 0).
trace:    imprime a cadeia completa de um id (ancestrais e descendentes),
          percorrendo relates_to recursivamente.
audit:    implementa a seção 11 (audit) de workflow-rules.yaml — cruza um
          histórico de commits com os ids conhecidos em um ou mais
          registries e classifica cada commit em coberto / referência
          quebrada / não documentado. Não bloqueia nada, é só relatório.
          Gere o arquivo de log com:
            git log --pretty=format:'%H%n%s%n%b%n===END===' > gitlog.txt

Requer PyYAML (pip install pyyaml --break-system-packages).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import (  # noqa: E402
    ID_PATTERN,
    INCIDENT_STATUSES,
    VALID_STATUSES,
    framework_versions,
    iter_documents,
    load_registry,
    load_rules,
    read_frontmatter,
    registry_mode,
    report,
    version_key,
)

# Campos presentes tanto no registry quanto no front-matter do documento.
# Por registry.update_rule (workflow-rules.yaml, seção 9) eles NUNCA podem
# divergir — era exatamente o que este validator prometia checar e não
# checava, porque nunca abria o .md.
MIRRORED_FIELDS = ["type", "title", "status", "owner", "created", "updated"]


def load(docs_dir: Path):
    """Mantido por compatibilidade — delega para framework_lib."""
    return load_registry(docs_dir)


def cmd_validate(docs_dir: Path, report_only: bool = False) -> int:
    data, docs = load(docs_dir)
    problems = []
    mode = registry_mode(data)

    def is_expected_external(target_id):
        if not isinstance(target_id, str):
            return False
        if mode == "project":
            # Registry de projeto só tem SDD; qualquer referência a outro
            # tipo (PRD/TS/ADR/...) é esperada — vive no repositório central.
            return not target_id.startswith("SDD-")
        # Registry central nunca contém SDD por desenho (vive no
        # repositório de projeto) — referência a SDD é esperada, não erro.
        return target_id.startswith("SDD-")

    seen = {}
    for d in data.get("documents", []):
        did = d.get("id")
        if did in seen:
            problems.append(f"ID duplicado: {did}")
        seen[did] = True

        status = d.get("status")
        allowed = INCIDENT_STATUSES if d.get("type") == "INC" else VALID_STATUSES
        if status not in allowed:
            problems.append(f"{did}: status inválido '{status}'")

        for rel in d.get("relates_to") or []:
            if rel not in docs and not is_expected_external(rel):
                problems.append(f"{did}: relates_to aponta para id inexistente '{rel}'")

        for field in ("parent_rfc", "parent_adr", "parent_strategy", "parent_postmortem", "supersedes", "superseded_by"):
            val = d.get(field)
            if val and val not in docs and not is_expected_external(val):
                problems.append(f"{did}: {field} aponta para id inexistente '{val}'")

        for sd in d.get("source_docs") or []:
            sid = sd.get("id") if isinstance(sd, dict) else sd
            if sid not in docs and not is_expected_external(sid):
                problems.append(f"{did}: source_docs aponta para id inexistente '{sid}'")

    warnings = []
    if mode == "central" and not data.get("repository"):
        warnings.append(
            "registry.yaml não tem o campo `repository` (URL do repositório "
            "de código do projeto) — a auditoria vai precisar perguntar antes "
            "de rodar."
        )

    problems += check_framework_version(data, docs_dir, warnings)
    problems += check_documents_on_disk(docs_dir, data, docs, warnings)

    return report(
        problems,
        warnings,
        f"✅ registry.yaml e documentos consistentes ({len(docs)} documentos, "
        "nenhum problema encontrado).",
        report_only=report_only,
    )


def check_framework_version(data: dict, docs_dir: Path, warnings: list) -> list:
    """
    `framework_version` do registry declara sob QUAL versão do framework o
    projeto opera — não é um espelho automático da versão atual do kit. Um
    projeto mapeado sob 1.6.0 continua legitimamente em 1.6.0 depois de o
    kit ir para 2.0.0 (evolução do framework não é retroativa).

    Logo o que se valida é: o campo existe, tem uma versão CONHECIDA do
    framework, e não é do futuro. Ficar para trás é aviso, não erro.
    """
    problems = []
    declared = data.get("framework_version")
    rules = load_rules(docs_dir)
    current, known = framework_versions(rules)

    if not declared:
        problems.append(
            "registry.yaml não declara `framework_version` — sem isso não dá "
            "para saber sob quais regras este projeto foi mapeado."
        )
        return problems

    declared = str(declared)
    if known and declared not in known:
        problems.append(
            f"`framework_version: {declared}` não é uma versão conhecida do "
            f"framework (conhecidas: {', '.join(known)})."
        )
    elif current and version_key(declared) > version_key(current):
        problems.append(
            f"`framework_version: {declared}` é posterior à versão atual do "
            f"kit ({current}) — registry aponta para uma versão que não existe."
        )
    elif current and declared != current:
        warnings.append(
            f"projeto opera sob framework {declared}; kit atual é {current}. "
            "Isso é válido (evolução do framework não é retroativa) — migre "
            "só quando decidir remapear o projeto."
        )
    return problems


def check_documents_on_disk(docs_dir: Path, data: dict, docs: dict, warnings: list) -> list:
    """
    Cruza cada entrada do registry com o .md correspondente em disco, nas
    duas direções. É a checagem que a capability `validate_registry` sempre
    prometeu ("front-matter divergente do registry") e nunca fez, porque
    este script nunca abria um documento.
    """
    problems = []
    registered_paths = set()

    for did, entry in docs.items():
        rel_path = entry.get("path")
        if not rel_path:
            problems.append(f"{did}: entrada do registry sem campo `path`.")
            continue

        doc_path = resolve_doc_path(docs_dir, rel_path)
        if doc_path is None:
            problems.append(f"{did}: `path: {rel_path}` não resolve para nenhum arquivo existente.")
            continue
        registered_paths.add(doc_path.resolve())

        try:
            fm, _ = read_frontmatter(doc_path)
        except ValueError as exc:
            problems.append(str(exc))
            continue

        if not fm:
            problems.append(f"{did}: {rel_path} não tem bloco de front-matter.")
            continue

        if fm.get("id") != did:
            problems.append(
                f"{did}: front-matter declara id '{fm.get('id')}', registry diz '{did}'."
            )

        for field in MIRRORED_FIELDS:
            doc_value = fm.get(field)
            reg_value = entry.get(field)
            if isinstance(doc_value, str) and isinstance(reg_value, str):
                if doc_value.strip() == reg_value.strip():
                    continue
            elif str(doc_value) == str(reg_value):
                continue
            problems.append(
                f"{did}: `{field}` diverge — documento: '{doc_value}', "
                f"registry: '{reg_value}'."
            )

        problems += check_source_docs_urls(did, fm)

    for path in iter_documents(docs_dir):
        if path.resolve() not in registered_paths:
            warnings.append(
                f"{path} existe em disco mas não está em nenhuma entrada do "
                "registry (documento não registrado, ou `path` errado)."
            )

    return problems


def check_source_docs_urls(did: str, fm: dict) -> list:
    """
    SDD vive no repositório do projeto e aponta para PRD/TS/ADR do central,
    então cada source_doc precisa de url utilizável — sem ela a cadeia
    quebra ao atravessar repositórios (repository_topology.cross_repo_reference).
    """
    problems = []
    for sd in fm.get("source_docs") or []:
        if not isinstance(sd, dict):
            problems.append(f"{did}: source_docs tem entrada sem id+url ('{sd}').")
            continue
        sid, url = sd.get("id"), sd.get("url")
        if not sid:
            problems.append(f"{did}: source_docs tem entrada sem `id`.")
        if not url:
            problems.append(f"{did}: source_docs '{sid}' não tem `url` — obrigatória (cross-repo).")
        elif not str(url).startswith(("http://", "https://")):
            problems.append(f"{did}: source_docs '{sid}' tem url não resolvível: '{url}'.")
    return problems


def resolve_doc_path(docs_dir: Path, rel_path: str) -> Path | None:
    """
    `path` no registry é relativo à raiz do repositório (ex.:
    'docs/EVM/01-rfc/RFC-EVM-0001.md'), mas o validator é chamado apontando
    para docs_dir. Sobe procurando a raiz em que o caminho resolve.
    """
    candidates = [Path.cwd(), docs_dir, *docs_dir.resolve().parents]
    for root in candidates:
        candidate = root / rel_path
        if candidate.is_file():
            return candidate
    tail = (docs_dir / Path(rel_path).name)
    return tail if tail.is_file() else None


def cmd_trace(docs_dir: Path, target_id: str) -> int:
    _, docs = load(docs_dir)
    if target_id not in docs:
        print(f"❌ id não encontrado no registry: {target_id}")
        return 1

    visited = set()

    def walk(doc_id, depth=0):
        if doc_id in visited or doc_id not in docs:
            return
        visited.add(doc_id)
        d = docs[doc_id]
        prefix = "  " * depth
        print(f"{prefix}- {doc_id} [{d.get('type')}] {d.get('title')} ({d.get('status')})")
        for rel in d.get("relates_to") or []:
            walk(rel, depth + 1)

    print(f"Cadeia de rastreabilidade a partir de {target_id}:\n")
    walk(target_id)
    return 0


def parse_git_log(path: Path):
    """
    Espera um arquivo gerado com:
      git log --pretty=format:'%H%n%s%n%b%n===END===' > gitlog.txt
    Retorna uma lista de dicts {sha, subject, message}.
    """
    if not path.exists():
        raise SystemExit(f"Não encontrado: {path}")
    text = path.read_text(encoding="utf-8")
    commits = []
    for chunk in text.split("===END==="):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue
        lines = chunk.split("\n")
        sha = lines[0].strip() if lines else ""
        subject = lines[1].strip() if len(lines) > 1 else ""
        body = "\n".join(lines[2:]).strip()
        commits.append({"sha": sha, "subject": subject, "message": f"{subject}\n{body}"})
    return commits


def cmd_audit(git_log_path: Path, docs_dirs) -> int:
    known_ids = set()
    for dd in docs_dirs:
        _, docs = load(dd)
        known_ids |= set(docs.keys())

    commits = parse_git_log(git_log_path)
    covered, broken, undocumented = [], [], []

    for c in commits:
        ids_found = set(ID_PATTERN.findall(c["message"]))
        if not ids_found:
            undocumented.append(c)
            continue
        valid = ids_found & known_ids
        invalid = ids_found - known_ids
        if valid:
            covered.append((c, valid))
        if invalid:
            broken.append((c, invalid))

    print(
        f"Auditoria de {len(commits)} commit(s) contra {len(known_ids)} "
        f"id(s) conhecido(s) em {len(docs_dirs)} registry(ies).\n"
    )

    print(f"✅ Cobertos (referência válida): {len(covered)}")
    for c, ids in covered:
        print(f"  - {c['sha'][:8]} {c['subject']}  [{', '.join(sorted(ids))}]")

    print(f"\n⚠️  Referência quebrada (id citado não existe em nenhum registry): {len(broken)}")
    for c, ids in broken:
        print(f"  - {c['sha'][:8]} {c['subject']}  [{', '.join(sorted(ids))}]")

    print(f"\n❓ Sem referência (nenhum id encontrado na mensagem): {len(undocumented)}")
    for c in undocumented:
        print(f"  - {c['sha'][:8]} {c['subject']}")

    print(
        "\nPróximo passo (audit.procedure, step 4): para cada commit sem "
        "referência, aplique os 5 critérios de decision_gates.rfc_to_adr — "
        "se algum se aplica, proponha um ADR reconstruído (provenance: "
        "reconstructed, status: in_review, tags: [audit]) referenciando o "
        "commit; se nenhum se aplica, não é necessário nenhum documento."
    )
    return 0


def main():
    args = [a for a in sys.argv[1:] if a != "--report-only"]
    report_only = "--report-only" in sys.argv
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    action = args[0]
    sys.argv = [sys.argv[0], *args]
    if action == "validate":
        sys.exit(cmd_validate(Path(args[1]), report_only=report_only))
    elif action == "trace":
        if len(sys.argv) < 4:
            print("Uso: registry_tools.py trace <docs_dir> <ID>")
            sys.exit(1)
        sys.exit(cmd_trace(Path(sys.argv[2]), sys.argv[3]))
    elif action == "audit":
        if len(sys.argv) < 4:
            print("Uso: registry_tools.py audit <git_log_file> <docs_dir_1> [<docs_dir_2> ...]")
            sys.exit(1)
        git_log_path = Path(sys.argv[2])
        docs_dirs = [Path(p) for p in sys.argv[3:]]
        sys.exit(cmd_audit(git_log_path, docs_dirs))
    else:
        print(f"Ação desconhecida: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
