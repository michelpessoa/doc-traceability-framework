#!/usr/bin/env python3
"""
validate_state.py

Mecaniza o gate_scope_verification (workflow-rules.yaml, seção 16): uma SDD
só pode estar `implemented` se a evidência de verificação existir de fato.

O gate original pedia que a IA preenchesse uma tabela de evidência e
confirmasse escopo — e depois confiava nela para dizer que tinha feito. Este
script checa a única coisa que dá para checar de fora: a tabela existe, tem
linha para cada critério de aceite, cita comando e saída reais, e a
checklist de escopo está marcada.

Uso:
    python3 validate_state.py <SDD.md | diretório> [...] [--report-only]

Exit 1 se houver problema; --report-only sempre sai 0.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import (  # noqa: E402
    iter_documents,
    load_rules,
    project_version,
    read_frontmatter,
    report,
    rule_applies_since_date,
)

# Em que versão cada exigência do gate 16 entrou. Mesma mecânica de
# validate_doc.RULE_SINCE: regra não vale retroativamente, projeto mapeado
# sob 1.6.0 não é reprovado por regra da 1.7.0
# (lessons_policy.non_retroactive). As duas nasceram com a seção 16.
RULE_SINCE = {
    "evidence_required": "1.7.0",
    "scope_checklist": "1.7.0",
}

# Frases que denunciam evidência de memória em vez de execução — o
# evidence_standard da seção 16 rejeita exatamente isto.
ASSUMED_EVIDENCE = [
    "deve passar",
    "deveria passar",
    "assumido",
    "presumo",
    "provavelmente passa",
    "não rodado",
    "n/a",
    "tbd",
]

CHECKBOX_UNCHECKED = re.compile(r"^\s*-\s*\[\s\]", re.MULTILINE)


def table_rows(section: str) -> list[list[str]]:
    """
    Extrai as linhas de dados de uma tabela markdown, descartando cabeçalho,
    separador e linhas vazias.
    """
    return table_with_header(section)[1]


def table_with_header(section: str) -> tuple[list[str], list[list[str]]]:
    """(cabeçalho normalizado em minúsculas, linhas de dados).

    Ignora linhas dentro de blocos cercados por ``` — uma linha de
    evidência que é continuação de comando shell (ex.: `  | grep -c ...`)
    começa com `|` mas não é linha de tabela markdown (SDD-DTF-0024).
    """
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
            continue  # separador
        rows.append(cells)
    if not rows:
        return [], []
    return [h.lower() for h in rows[0]], rows[1:]


def section_body(body: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^#{{2,3}}\s*{re.escape(heading)}.*?$(.*?)(?=^#{{2,3}}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else None


def check_sdd(path: Path, version: str | None = None) -> tuple[list, list]:
    problems, warnings = [], []
    if version is None:
        version = project_version(path)

    try:
        fm, body = read_frontmatter(path)
    except ValueError as exc:
        return [str(exc)], []

    if not fm or fm.get("type") != "SDD":
        return [], []

    # Não retroatividade por data de criação da SDD, igual a
    # validate_doc.check_document (SDD-DTF-0016, SDD-DTF-0018).
    rules = load_rules()

    def applies(rule: str) -> bool:
        return rule_applies_since_date(rules, RULE_SINCE[rule], fm.get("created"), version)

    doc_id = fm.get("id") or path.name
    status = fm.get("status")

    criteria = section_body(body, "Critérios de aceite") or section_body(
        body, "Critérios de aceite / definição de pronto"
    )
    evidence = section_body(body, "Evidência de verificação")
    scope = section_body(body, "Verificação de escopo")

    n_criteria = len(table_rows(criteria)) if criteria else 0

    if status != "implemented":
        # Antes de `implemented` a evidência ainda pode estar vazia — o que
        # não pode é a SDD nem ter as seções que o gate vai exigir depois.
        if evidence is None and applies("evidence_required"):
            warnings.append(f"{doc_id}: sem seção 'Evidência de verificação' (será exigida em implemented).")
        if scope is None and applies("scope_checklist"):
            warnings.append(f"{doc_id}: sem seção 'Verificação de escopo' (será exigida em implemented).")
        return problems, warnings

    # --- daqui para baixo: status == implemented ---
    # O gate vale integralmente, mas só a partir da versão em que cada
    # exigência entrou: projeto mapeado antes dela não é reprovado.

    if applies("evidence_required"):
        problems += check_evidence(doc_id, evidence, n_criteria)
        problems += check_verification_rounds(doc_id, evidence, body)
        problems += check_evidence_profile(doc_id, criteria, evidence)

    if applies("scope_checklist"):
        problems += check_scope(doc_id, scope)

    return problems, warnings


def check_evidence(doc_id: str, evidence: str | None, n_criteria: int) -> list:
    """gate_scope_verification item 4: a tabela existe, cobre cada critério
    e cita comando rodado — não resultado assumido."""
    if evidence is None:
        return [
            f"{doc_id}: status `implemented` sem seção 'Evidência de verificação' — gate_scope_verification item 4."
        ]

    problems = []
    header, rows = table_with_header(evidence)
    # Colunas por cabeçalho, não por posição: "#", "Critério" e "Sensor" não
    # são resultado — "n/a (checagem estática)" em Sensor é declaração
    # permitida por verify-sdd. Sem cabeçalho reconhecível, linha inteira
    # (nunca mais permissivo por falta de cabeçalho).
    cmd_idx = next((i for i, h in enumerate(header) if "comando" in h), None)
    sensor_idx = next((i for i, h in enumerate(header) if "sensor" in h), None)
    checked_idx = [i for i, h in enumerate(header) if any(k in h for k in ("comando", "saída", "saida", "passou"))]
    if not rows:
        problems.append(
            f"{doc_id}: 'Evidência de verificação' está vazia e o status é "
            "`implemented` — checklist de memória não satisfaz o gate."
        )
    elif n_criteria and len(rows) < n_criteria:
        problems.append(
            f"{doc_id}: {n_criteria} critério(s) de aceite mas só {len(rows)} "
            "linha(s) de evidência — cada critério precisa da sua."
        )

    for row in rows:
        scope_cells = [row[i] for i in checked_idx if i < len(row)] if checked_idx else row
        joined = " | ".join(scope_cells).lower()
        for term in ASSUMED_EVIDENCE:
            if term in joined:
                problems.append(
                    f"{doc_id}: linha de evidência com resultado assumido "
                    f"('{term}') — evidence_standard exige comando rodado e saída real."
                )
                break
        col = cmd_idx if cmd_idx is not None else 1
        if len(row) > col and not row[col].strip():
            problems.append(f"{doc_id}: linha de evidência sem comando rodado.")

        # STRAT-DTF-0003 item A (lição do tlc-spec-lean): um teste que
        # nunca foi provado capaz de falhar não é evidência de que
        # discrimina — a coluna Sensor existe para registrar isso, e
        # deixá-la vazia é o mesmo "assumido" que evidence_standard já
        # proíbe na coluna de saída. "sem teste automatizado" é uma
        # declaração válida (verify-sdd.md, seção 3) — só a ausência de
        # qualquer texto é reprovada.
        if sensor_idx is not None and len(row) > sensor_idx and not row[sensor_idx].strip():
            problems.append(
                f"{doc_id}: linha de evidência com coluna 'Sensor' vazia — "
                "declare o resultado do sensor de discriminação ou "
                "'sem teste automatizado' (STRAT-DTF-0003 item A)."
            )

    return problems


def check_verification_rounds(doc_id: str, evidence: str | None, body: str) -> list:
    """RF07 (SDD-DTF-0033): teto de 3 rodadas de correção-e-reverificação.

    Agrupa as linhas da tabela de evidência por coluna `Rodada`; qualquer
    linha != PASS numa rodada torna aquela rodada "não-PASS". 3+ rodadas
    não-PASS sem a seção `## Escalonado ao humano` no corpo do documento
    reprova, mesmo que o veredito do topo diga PASS. Tabela sem coluna
    `Rodada` (arquivo pré-SPEC-DTF-0012) é tratada como rodada única —
    nunca atinge o teto, não-retroativo por construção.
    """
    if not evidence:
        return []
    header, rows = table_with_header(evidence)
    if not rows:
        return []
    rodada_idx = next((i for i, h in enumerate(header) if "rodada" in h), None)
    passou_idx = next((i for i, h in enumerate(header) if "passou" in h), None)
    if rodada_idx is None or passou_idx is None:
        return []

    rounds_failed: dict[str, bool] = {}
    for row in rows:
        if rodada_idx >= len(row):
            continue
        rodada = row[rodada_idx].strip()
        if not rodada:
            continue
        passed = row[passou_idx].strip().lower() if passou_idx < len(row) else ""
        is_pass = passed in ("sim", "yes", "pass")
        rounds_failed.setdefault(rodada, False)
        if not is_pass:
            rounds_failed[rodada] = True

    failed = [r for r, bad in rounds_failed.items() if bad]
    if len(failed) >= 3 and "## Escalonado ao humano" not in body:
        return [
            f"{doc_id}: {len(failed)} rodada(s) de verificação sem PASS e sem "
            "seção '## Escalonado ao humano' — teto de 3 rodadas exige escalonamento (RF07)."
        ]
    return []


def check_evidence_profile(doc_id: str, criteria: str | None, evidence: str | None) -> list:
    """STRAT-DTF-0003 item 7 (E4/E5, tlc-spec-lean): comando+saída não prova
    que a asserção testada é a certa, e perfil automatizado pode virar
    manual sem ninguém perceber entre rodadas.

    Não-retroativo por construção (mesmo padrão de
    check_verification_rounds): sem as colunas "Assertion (file:line)" e
    "Perfil usado" no cabeçalho de evidência, a função não entra no loop —
    SDD anterior a esta checagem nunca é afetada.
    """
    if not criteria or not evidence:
        return []

    c_header, c_rows = table_with_header(criteria)
    num_idx = 0  # "#" é sempre a primeira coluna, nas duas tabelas
    perfil_esperado_idx = next((i for i, h in enumerate(c_header) if "perfil esperado" in h), None)
    if perfil_esperado_idx is None:
        return []

    esperado_por_criterio = {
        row[num_idx].strip(): row[perfil_esperado_idx].strip().lower()
        for row in c_rows
        if len(row) > perfil_esperado_idx and row[num_idx].strip()
    }

    e_header, e_rows = table_with_header(evidence)
    assertion_idx = next((i for i, h in enumerate(e_header) if "assertion" in h or "file:line" in h), None)
    perfil_usado_idx = next((i for i, h in enumerate(e_header) if "perfil usado" in h), None)
    if assertion_idx is None or perfil_usado_idx is None:
        return []

    problems = []
    for row in e_rows:
        if num_idx >= len(row):
            continue
        esperado = esperado_por_criterio.get(row[num_idx].strip())
        if esperado is None:
            continue

        if esperado == "automatizado" and (len(row) <= assertion_idx or not row[assertion_idx].strip()):
            problems.append(
                f"{doc_id}: critério #{row[num_idx].strip()} com perfil esperado "
                "'automatizado' e 'Assertion (file:line)' vazia — comando rodado "
                "não prova que testa a asserção certa (STRAT-DTF-0003 item 7/E4)."
            )

        usado = row[perfil_usado_idx].strip() if len(row) > perfil_usado_idx else ""
        if usado and usado.split("(")[0].strip().lower() != esperado and "(" not in usado:
            problems.append(
                f"{doc_id}: critério #{row[num_idx].strip()} com 'Perfil usado' "
                f"('{usado}') divergente do 'Perfil esperado' ('{esperado}') sem "
                "justificativa entre parênteses (STRAT-DTF-0003 item 7/E5)."
            )

    return problems


def check_scope(doc_id: str, scope: str | None) -> list:
    """gate_scope_verification itens 1-3: a checklist existe e está toda
    marcada."""
    if scope is None:
        return [
            f"{doc_id}: status `implemented` sem seção 'Verificação de escopo' — gate_scope_verification itens 1-3."
        ]
    if CHECKBOX_UNCHECKED.search(scope):
        return [f"{doc_id}: 'Verificação de escopo' tem item não marcado e o status é `implemented`."]
    return []


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
        p, w = check_sdd(path)
        problems += p
        warnings += w

    return report(
        problems,
        warnings,
        f"✅ {len(paths)} documento(s) verificados: nenhuma SDD `implemented` sem evidência.",
        report_only=report_only,
    )


if __name__ == "__main__":
    sys.exit(main())
