"""Seções opcionais da SPEC e Documentos originados fora dos templates.

SDD-DTF-0057 (SPEC-DTF-0031, RF07, RF08, RF09, RF11). Usa o
workflow-rules.yaml e os templates reais.
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_renderings import OPTIONAL_MARK, check_optional_sections  # noqa: E402
from framework_lib import load_rules  # noqa: E402
from validate_doc import check_document  # noqa: E402

FRAMEWORK = Path(__file__).resolve().parents[2]
SPEC_TEMPLATE = FRAMEWORK / "templates" / "spec.template.md"
RFC_TEMPLATE = FRAMEWORK / "templates" / "rfc.template.md"
VERIFY_SDD = FRAMEWORK / "procedures" / "verify-sdd.md"

ESPERADAS = [
    "Usuários / personas afetadas",
    "Observabilidade (métricas, logs, alertas)",
    "Plano de rollout / rollback",
    "Times consumidores impactados",
    "Dependências",
]


def _optional() -> list[dict]:
    return load_rules()["document_types"]["SPEC"]["optional_sections"]


def test_optional_sections_declaradas_no_yaml():
    secoes = _optional()
    assert [s["heading"] for s in secoes] == ESPERADAS
    assert all(isinstance(s["returns_when"], str) and s["returns_when"] for s in secoes)


def test_template_real_concorda_com_o_yaml():
    assert check_optional_sections(load_rules(), SPEC_TEMPLATE) == []


def test_template_repete_o_returns_when():
    texto = SPEC_TEMPLATE.read_text(encoding="utf-8")
    for s in _optional():
        assert f"{OPTIONAL_MARK}{s['returns_when']}" in texto


def _template_com(tmp_path: Path, texto: str) -> Path:
    path = tmp_path / "spec.template.md"
    path.write_text(texto, encoding="utf-8")
    return path


def test_secao_sem_marca_reprova(tmp_path):
    texto = SPEC_TEMPLATE.read_text(encoding="utf-8")
    alvo = f"## Dependências\n{OPTIONAL_MARK}"
    assert alvo in texto
    path = _template_com(tmp_path, texto.replace(alvo, "## Dependências\n> Texto qualquer. "))
    assert check_optional_sections(load_rules(), path) == [
        "spec.template.md: seção opcional 'Dependências' de optional_sections sem a marca de opcional no template."
    ]


def test_secao_marcada_fora_da_lista_reprova(tmp_path):
    texto = SPEC_TEMPLATE.read_text(encoding="utf-8")
    texto += f"\n## Glossário\n{OPTIONAL_MARK}Tem termo novo.\n"
    path = _template_com(tmp_path, texto)
    assert check_optional_sections(load_rules(), path) == [
        "spec.template.md: 'Glossário' marcada como opcional no template e fora de optional_sections."
    ]


def test_returns_when_diferente_reprova(tmp_path):
    rules = load_rules()
    secao = _optional()[0]
    texto = SPEC_TEMPLATE.read_text(encoding="utf-8").replace(
        f"{OPTIONAL_MARK}{secao['returns_when']}", f"{OPTIONAL_MARK}Quando quiser."
    )
    path = _template_com(tmp_path, texto)
    assert check_optional_sections(rules, path) == [
        f"spec.template.md: '{secao['heading']}' com \"Volta quando\" diferente de returns_when."
    ]


def test_spec_sem_as_cinco_secoes_passa(tmp_path):
    (tmp_path / "registry.yaml").write_text('project: "TST"\nframework_version: "2.7.0"\n', encoding="utf-8")
    fm = {
        "id": "SPEC-TST-0001",
        "type": "SPEC",
        "title": "t",
        "status": "draft",
        "project": "TST",
        "owner": "o",
        "created": "2099-01-01",
        "updated": "2099-01-01",
        "sizing": "medium",
    }
    sweep = "".join(
        f"| {c} | RF01 | |\n"
        for c in [
            "Autorização / permissão",
            "Concorrência",
            "Idempotência",
            "Observabilidade",
            "Falha de dependência externa",
            "Validação de entrada",
            "Limite de volume / rate",
        ]
    )
    corpo = (
        "\n# t\n\n## Objetivo\n\nX.\n\n## Requisitos funcionais\n\n"
        "| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |\n|---|---|---|---|\n"
        "| RF01 | R | O sistema deve fazer X | `a.py` |\n\n"
        "## Requisitos transversais (sweep)\n\n| Categoria | Destino | Motivo |\n|---|---|---|\n" + sweep + "\n"
        "## Fora de escopo\n\nY.\n\n## Contratos técnicos\n\n`a.py`: f()\n\n"
        "## Estratégia de teste\n\n| RF | Tipo | Mock? | Arquivo |\n|---|---|---|---|\n| RF01 | unit | Não | `t.py` |\n"
    )
    path = tmp_path / "SPEC-TST-0001.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True) + "---\n" + corpo, encoding="utf-8")
    problems, _ = check_document(path)
    assert problems == []


def test_documentos_originados_fora_dos_templates_e_no_hash():
    for template in (SPEC_TEMPLATE, RFC_TEMPLATE):
        texto = template.read_text(encoding="utf-8")
        assert "## Documentos originados" not in texto
        assert "visão gerada no registry.md" in texto
    assert "Documentos originados" in load_rules()["approval_policy"]["hash_excluded_sections"]


def test_gate_e_verify_sdd_citam_a_parte_2_da_spec():
    regra = load_rules()["gate_scope_verification"]["rule"]
    frase = "Na SDD enxuta (2.7.0, com source_docs), o desenho a conferir é a Parte 2 da SPEC de source_docs"
    assert " ".join(regra.split()).count(frase) == 2
    procedimento = " ".join(VERIFY_SDD.read_text(encoding="utf-8").split())
    assert procedimento.count("Parte 2 da SPEC, lida pela url de `source_docs`") >= 2
