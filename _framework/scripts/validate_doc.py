#!/usr/bin/env python3
"""
validate_doc.py

Mecaniza o gate_content_quality (workflow-rules.yaml, seção 15). O gate
existia só como autorrevisão em prosa — uma IA checando a si mesma no
momento em que tem incentivo para não checar. Este script é o sinal
externo que faltava.

Uso:
    python3 validate_doc.py <arquivo.md | diretório> [...] [--report-only]

Checa, por documento:
  1. Front-matter completo (campos obrigatórios de frontmatter_schema).
  2. Nenhum placeholder banido ("TBD", "definir depois", ...).
  3. `NEEDS CLARIFICATION` pendente não passa de in_review.
  4. Seções obrigatórias do tipo presentes.
  5. SPEC/PRD: todo requisito funcional tem RF-ID próprio.
  6. SPEC/PRD: todo critério de aceite está em notação EARS.
  7. SPEC/TS: a seção de contratos aponta arquivo/módulo ("onde").

Exit 1 se houver problema; --report-only sempre sai 0.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import (  # noqa: E402
    INCIDENT_STATUSES,
    VALID_STATUSES,
    iter_documents,
    project_version,
    read_frontmatter,
    report,
    rule_applies,
)

# Em que versão cada exigência entrou. Regra não vale retroativamente:
# projeto mapeado sob 1.6.0 não é reprovado por regra da 1.7.0
# (lessons_policy.non_retroactive).
RULE_SINCE = {
    "placeholders": "1.7.0",
    "needs_clarification": "1.7.0",
    "rf_id": "1.7.0",
    "contract_where": "1.7.0",
    "ears": "2.0.0",
}

# gate_content_quality item 4: termos que descrevem o que fazer sem mostrar
# como. A busca é literal e case-insensitive, igual ao "scan de placeholder"
# descrito no self_review_checklist.
BANNED_PLACEHOLDERS = [
    "tbd",
    "to be defined",
    "definir depois",
    "a definir",
    "ajustar conforme necessário",
    "conforme necessário",
    "seguir o padrão do projeto",
    "seguir padrão do projeto",
    "tratar erros apropriadamente",
    "tratamento de erro apropriado",
    "preencher depois",
    "detalhar depois",
]

NEEDS_CLARIFICATION = re.compile(r"NEEDS CLARIFICATION", re.IGNORECASE)

# Status a partir dos quais o documento é tratado como decidido — daí em
# diante placeholder e ambiguidade pendente deixam de ser tolerados.
DECIDED_STATUSES = {"approved", "implemented"}

# gate_content_quality.applies_to é explícito: "PRD, Tech Spec e SDD"
# (mais SPEC, que os substitui). Um RFC que difere um detalhe para a Tech
# Spec — "(a definir na Tech Spec)" — está fazendo exatamente o que uma
# RFC deve fazer, e reprovar isso é o validator sendo mais estrito que a
# regra que ele mecaniza. Falso positivo desgasta o gate inteiro.
CONTENT_GATE_TYPES = {"SPEC", "PRD", "TS", "SDD"}

REQUIRED_FRONTMATTER = ["id", "type", "title", "status", "project", "owner", "created", "updated"]

REQUIRED_SECTIONS = {
    "RFC": ["Contexto", "Problema", "Objetivos", "Alternativas", "Proposta", "Riscos"],
    "ADR": ["Contexto", "Decisão", "Consequências"],
    "SPEC": [
        "Objetivo",
        "Requisitos funcionais",
        "Contratos técnicos",
        "Estratégia de teste",
        "Fora de escopo",
    ],
    "PRD": ["Objetivo", "Requisitos funcionais", "Critérios de aceite"],
    "TS": ["Contratos técnicos"],
    "SDD": ["Requisitos consolidados", "Critérios de aceite"],
}

# Um RF-ID é o identificador próprio de um requisito funcional, exigido
# pelo item 1 do gate. "1." numerado não serve: não sobrevive a reordenação
# e não dá para referenciar de um critério de aceite.
RF_ID = re.compile(r"\bRF-?\d+\b")

# EARS (Easy Approach to Requirements Syntax) — mesma notação adotada por
# AWS Kiro e por tlc-spec-driven. Um critério de aceite precisa dizer, em
# forma verificável, QUANDO vale e O QUE o sistema faz. As cinco formas:
#
#   ubíqua      "O sistema deve <resposta>"
#   dirigida a evento   "Quando <gatilho>, o sistema deve <resposta>"
#   dirigida a estado   "Enquanto <estado>, o sistema deve <resposta>"
#   indesejada  "Se <condição>, então o sistema deve <resposta>"
#   opcional    "Onde <capacidade>, o sistema deve <resposta>"
#
# A checagem é deliberadamente rasa: exige o verbo de obrigação (a
# "resposta") e reconhece o gatilho quando existe. Não tenta interpretar
# semântica — um validator que erra e reprova critério bom é pior que
# nenhum.
EARS_RESPONSE = re.compile(r"\b(deve|deverá|devem|deverão)\b", re.IGNORECASE)
EARS_TRIGGER = re.compile(r"^\s*(quando|enquanto|se|onde|ao|após|dado que)\b", re.IGNORECASE)

# "onde" de um contrato: caminho de arquivo com extensão, ou módulo com barra.
FILE_HINT = re.compile(r"[\w./-]+\.(?:ts|tsx|js|jsx|py|go|rs|java|kt|rb|sql|yaml|yml|json|prisma|mjs)\b")


def scannable(body: str) -> str:
    """
    Corpo sem as linhas de instrução do template (blockquote `>`).

    A prosa que ENSINA a regra cita os termos banidos por definição — o
    template diz "proibido usar TBD". Escanear essas linhas faria todo
    documento reprovar pela instrução que ele carrega, não pelo conteúdo
    que o autor escreveu.
    """
    return "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith(">"))


def section_body(body: str, heading: str) -> str | None:
    """Retorna o texto de uma seção `## Heading` até o próximo heading de mesmo nível."""
    pattern = re.compile(
        rf"^#{{2,3}}\s*{re.escape(heading)}.*?$(.*?)(?=^#{{2,3}}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else None


def check_document(path: Path, version: str | None = None) -> tuple[list, list]:
    problems, warnings = [], []
    if version is None:
        version = project_version(path)

    def applies(rule: str) -> bool:
        return rule_applies(RULE_SINCE[rule], version)

    try:
        fm, body = read_frontmatter(path)
    except ValueError as exc:
        return [str(exc)], []

    if not fm:
        return [f"{path}: sem bloco de front-matter."], []

    doc_id = fm.get("id") or path.name
    doc_type = fm.get("type")
    status = fm.get("status")

    for field in REQUIRED_FRONTMATTER:
        if fm.get(field) in (None, ""):
            problems.append(f"{doc_id}: front-matter sem `{field}` (obrigatório).")

    allowed = INCIDENT_STATUSES if doc_type == "INC" else VALID_STATUSES
    if status and status not in allowed:
        problems.append(f"{doc_id}: status inválido '{status}'.")

    prose = scannable(body)
    lowered = prose.lower()
    scan_placeholders = doc_type in CONTENT_GATE_TYPES and applies("placeholders")
    for term in BANNED_PLACEHOLDERS if scan_placeholders else []:
        if term in lowered:
            line = next(
                (i for i, ln in enumerate(body.splitlines(), 1)
                 if term in ln.lower() and not ln.lstrip().startswith(">")),
                None,
            )
            where = f" (linha {line})" if line else ""
            msg = f"{doc_id}: placeholder banido '{term}'{where} — gate_content_quality item 4."
            (problems if status in DECIDED_STATUSES else warnings).append(msg)

    if doc_type in CONTENT_GATE_TYPES and applies("needs_clarification") and NEEDS_CLARIFICATION.search(prose):
        msg = (
            f"{doc_id}: tem `NEEDS CLARIFICATION` pendente — "
            "gate_content_quality item 5 proíbe avançar para approved assim."
        )
        (problems if status in DECIDED_STATUSES else warnings).append(msg)

    for heading in REQUIRED_SECTIONS.get(doc_type, []):
        if section_body(body, heading) is None:
            problems.append(f"{doc_id}: seção obrigatória ausente: '{heading}'.")

    if doc_type in ("PRD", "SPEC"):
        reqs = section_body(body, "Requisitos funcionais")
        if reqs and applies("rf_id") and not RF_ID.search(reqs):
            problems.append(
                f"{doc_id}: 'Requisitos funcionais' sem RF-ID próprio "
                "(gate_content_quality item 1) — lista numerada não é id."
            )

    if doc_type in ("PRD", "SPEC"):
        # Rigor de EARS vale para SPEC (tipo novo). Em PRD legado é aviso:
        # projeto mapeado sob 1.x não migra (lessons_policy.non_retroactive).
        strict = doc_type == "SPEC"
        ears_checker = check_ears if applies("ears") else lambda *_: []
        for problem in ears_checker(doc_id, section_body(body, "Requisitos funcionais")):
            (problems if strict else warnings).append(problem)

    if doc_type in ("TS", "SPEC"):
        contracts = section_body(body, "Contratos técnicos")
        if contracts and applies("contract_where") and not FILE_HINT.search(contracts):
            warnings.append(
                f"{doc_id}: 'Contratos técnicos' não aponta nenhum arquivo/módulo "
                "('onde' do gate_content_quality item 2)."
            )

    return problems, warnings


def check_ears(doc_id: str, section: str | None) -> list:
    """
    Checa a coluna "Critério de aceite" da tabela de requisitos funcionais
    contra a notação EARS. Linha sem RF-ID ou sem critério preenchido é
    ignorada — isso é trabalho do check de RF-ID, não deste.
    """
    if not section:
        return []
    problems = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        rf_id, criterion = cells[0], cells[-1]
        if not RF_ID.search(rf_id) or not criterion:
            continue
        if not EARS_RESPONSE.search(criterion):
            problems.append(
                f"{doc_id}: critério de {rf_id} não está em EARS — falta o verbo "
                f"de obrigação ('deve'): '{criterion[:60]}'."
            )
        elif not EARS_TRIGGER.match(criterion) and not criterion.lower().startswith("o "):
            problems.append(
                f"{doc_id}: critério de {rf_id} não abre com gatilho EARS "
                "(Quando/Enquanto/Se/Onde) nem com a forma ubíqua ('O sistema "
                f"deve...'): '{criterion[:60]}'."
            )
    return problems


def collect(targets) -> list[Path]:
    paths = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            paths.extend(iter_documents(p))
        elif p.is_file():
            paths.append(p)
        else:
            raise SystemExit(f"Não encontrado: {target}")
    return paths


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    report_only = "--report-only" in sys.argv
    if not args:
        print(__doc__)
        return 1

    paths = collect(args)
    problems, warnings = [], []
    for path in paths:
        p, w = check_document(path)
        problems += p
        warnings += w

    return report(
        problems,
        warnings,
        f"✅ {len(paths)} documento(s) passaram no gate de qualidade de conteúdo.",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
