"""Testes da SDD enxuta e do molde — SDD-DTF-0057 (SPEC-DTF-0031, RF01 a RF06).

`validate_doc.check_document` (RF01 a RF04, RF06) e
`check_source_docs.check_sdd_source_docs` (RF05). Usa o workflow-rules.yaml
real. SDDs novas usam `created` em 2099, depois de qualquer data da 2.7.0,
em projeto sob 2.7.0; as antigas, 2026-01-01, ou projeto sob 2.6.0.
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_source_docs import check_sdd_source_docs  # noqa: E402
from validate_doc import RULE_SINCE, check_document  # noqa: E402

TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "sdd.template.md"
NOVO = "2099-01-01"
ANTIGO = "2026-01-01"
SPEC_ID = "SPEC-TST-0001"
SPEC2_ID = "SPEC-TST-0002"
ADR_ID = "ADR-TST-0001"
SPEC_PATH = f"docs/TST/03-spec/{SPEC_ID}.md"
SPEC2_PATH = f"docs/TST/03-spec/{SPEC2_ID}.md"
URL = "https://example.invalid/central/blob/main/"

HEADER = "| RF-ID | Origem | Requisito (resumo) | Arquivos |\n|---|---|---|---|\n"
ROWS = f"| RF01 | {SPEC_ID} | Listar itens | `app/lista.py` |\n| RF02 | {SPEC_ID} | Apagar item | `app/lista.py` |\n"

CRITERIOS = (
    "## Critérios de aceite / definição de pronto\n\n"
    "| # | Critério | Comando de verificação | Resultado esperado | Perfil esperado |\n"
    "|---|---|---|---|---|\n"
    "| A01 | RF01 | `pytest -q` | passa | automatizado |\n\n"
)
TASKS = (
    "## Decomposição em tasks\n\n"
    "| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |\n"
    "|---|---|---|---|---|\n"
    "| 1 | Fazer | RF01, RF02 | `app/lista.py` | |\n\n"
)


def _projeto(tmp_path: Path, version: str = "2.7.0") -> Path:
    sdd_dir = tmp_path / "projeto" / "docs" / "sdd"
    sdd_dir.mkdir(parents=True, exist_ok=True)
    (sdd_dir / "registry.yaml").write_text(
        f'project: "TST"\nframework_version: "{version}"\ndocuments: []\n', encoding="utf-8"
    )
    return sdd_dir


def _sdd(
    tmp_path: Path,
    *,
    tabela: str = HEADER + ROWS,
    extra: str = "",
    created: str = NOVO,
    status: str = "draft",
    sizing="medium",
    source_docs=None,
    molde: str | None = None,
    version: str = "2.7.0",
) -> Path:
    sdd_dir = _projeto(tmp_path, version)
    if source_docs is None:
        source_docs = [{"id": SPEC_ID, "url": URL + SPEC_PATH}]
    fm = {
        "id": "SDD-TST-0001",
        "type": "SDD",
        "title": "teste",
        "status": status,
        "project": "TST",
        "owner": "dono",
        "created": created,
        "updated": created,
        "source_docs": source_docs,
    }
    if sizing is not None:
        fm["sizing"] = sizing
    if molde is not None:
        fm["molde"] = molde
    body = (
        "\n# teste\n\n## Resumo executivo\n\nUm resumo.\n\n"
        f"## Requisitos consolidados\n\n{tabela}\n{extra}{TASKS}{CRITERIOS}"
    )
    path = sdd_dir / "SDD-TST-0001.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True) + "---\n" + body, encoding="utf-8")
    return path


def _problems(path: Path) -> list[str]:
    problems, _ = check_document(path)
    return problems


def _lean(problems: list[str]) -> list[str]:
    """Só as mensagens novas da SDD enxuta e do molde."""
    marcas = ("SDD enxuta", "Requisitos consolidados", "Origem", "resumo de", "coluna Arquivos", "`molde`")
    return [p for p in problems if any(m in p for m in marcas)]


# --- RF01 a RF04: SDD enxuta -------------------------------------------------


def test_rule_since_sdd_lean_e_2_7_0():
    assert RULE_SINCE["sdd_lean"] == "2.7.0"


def test_sdd_enxuta_valida_passa(tmp_path):
    assert _problems(_sdd(tmp_path)) == []


def test_sizing_ausente_reprova(tmp_path):
    problems = _lean(_problems(_sdd(tmp_path, sizing=None)))
    assert problems == [
        "SDD-TST-0001: SDD enxuta sem `sizing` válido (None); use small, medium, large ou complex (SPEC-DTF-0031, RF01)."
    ]


def test_sizing_fora_dos_niveis_reprova(tmp_path):
    problems = _lean(_problems(_sdd(tmp_path, sizing="enorme")))
    assert problems == [
        "SDD-TST-0001: SDD enxuta sem `sizing` válido ('enorme'); use small, medium, large ou complex (SPEC-DTF-0031, RF01)."
    ]


def test_tabela_com_colunas_erradas_reprova(tmp_path):
    tabela = "| RF | Requisito | Critério de aceite (EARS) |\n|---|---|---|\n| RF01 | X | O sistema deve X |\n"
    problems = _lean(_problems(_sdd(tmp_path, tabela=tabela)))
    assert problems == [
        "SDD-TST-0001: 'Requisitos consolidados' sem a tabela RF-ID | Origem | Requisito (resumo) | Arquivos (SPEC-DTF-0031, RF02)."
    ]


def test_linha_sem_rf_id_reprova(tmp_path):
    tabela = HEADER + f"| — | {SPEC_ID} | Listar | `a.py` |\n"
    problems = _lean(_problems(_sdd(tmp_path, tabela=tabela)))
    assert problems == ["SDD-TST-0001: linha 1 de 'Requisitos consolidados' sem RF-ID."]


def test_origem_fora_de_source_docs_reprova(tmp_path):
    tabela = HEADER + "| RF01 | SPEC-TST-0099 | Listar | `a.py` |\n"
    problems = _lean(_problems(_sdd(tmp_path, tabela=tabela)))
    assert problems == [f"SDD-TST-0001: RF01 com Origem 'SPEC-TST-0099' que não é SPEC de source_docs ({SPEC_ID})."]


def test_origem_so_com_a_adr_reprova(tmp_path):
    source_docs = [{"id": SPEC_ID, "url": URL + SPEC_PATH}, {"id": ADR_ID, "url": URL + "adr.md"}]
    tabela = HEADER + f"| RF01 | {ADR_ID} | Listar | `a.py` |\n"
    problems = _lean(_problems(_sdd(tmp_path, tabela=tabela, source_docs=source_docs)))
    assert problems == [f"SDD-TST-0001: RF01 com Origem '{ADR_ID}' que não é SPEC de source_docs ({SPEC_ID})."]


def test_resumo_longo_reprova(tmp_path):
    resumo = "x" * 201
    tabela = HEADER + f"| RF01 | {SPEC_ID} | {resumo} | `a.py` |\n"
    problems = _lean(_problems(_sdd(tmp_path, tabela=tabela)))
    assert problems == ["SDD-TST-0001: RF01 com resumo de 201 caracteres; o limite é 200 (o resto fica na SPEC)."]


def test_resumo_de_200_passa(tmp_path):
    tabela = HEADER + f"| RF01 | {SPEC_ID} | {'x' * 200} | `a.py` |\n"
    assert _lean(_problems(_sdd(tmp_path, tabela=tabela))) == []


def test_arquivos_vazio_reprova(tmp_path):
    tabela = HEADER + f"| RF01 | {SPEC_ID} | Listar |  |\n"
    problems = _lean(_problems(_sdd(tmp_path, tabela=tabela)))
    assert problems == ["SDD-TST-0001: RF01 sem caminho na coluna Arquivos."]


def test_secao_de_especificacao_copiada_reprova(tmp_path):
    extra = "## Especificação técnica consolidada\n\nCópia da Parte 2.\n\n"
    problems = _lean(_problems(_sdd(tmp_path, extra=extra)))
    assert problems == [
        "SDD-TST-0001: SDD enxuta com a seção 'Especificação técnica consolidada': o conteúdo fica na SPEC "
        "de source_docs, por referência (SPEC-DTF-0031, RF04)."
    ]


def test_secao_de_decisao_copiada_reprova(tmp_path):
    extra = "## Decisão(ões) de arquitetura aplicável(is)\n\nCópia da ADR.\n\n"
    problems = _lean(_problems(_sdd(tmp_path, extra=extra)))
    assert problems == [
        "SDD-TST-0001: SDD enxuta com a seção 'Decisão(ões) de arquitetura aplicável(is)': o conteúdo fica na ADR "
        "de source_docs, por referência (SPEC-DTF-0031, RF04)."
    ]


def test_sdd_enxuta_aprovada_nao_e_cobrada(tmp_path):
    """As regras de formato valem em draft e in_review, como RF06/RF07 da SDD-DTF-0030."""
    assert _lean(_problems(_sdd(tmp_path, status="approved", sizing=None))) == []


def test_sdd_anterior_a_2_7_0_nao_muda(tmp_path):
    tabela = "| RF | Requisito | Critério de aceite (EARS) |\n|---|---|---|\n| RF01 | X | O sistema deve X |\n"
    extra = "## Especificação técnica consolidada\n\nDesenho.\n\n"
    path = _sdd(tmp_path, tabela=tabela, extra=extra, created=ANTIGO, sizing=None)
    assert _lean(_problems(path)) == []


def test_sdd_em_projeto_sob_2_6_0_nao_muda(tmp_path):
    extra = "## Especificação técnica consolidada\n\nDesenho.\n\n"
    path = _sdd(tmp_path, extra=extra, sizing=None, version="2.6.0")
    assert _lean(_problems(path)) == []


def test_sdd_sem_source_docs_nao_e_enxuta(tmp_path):
    tabela = "| RF | Requisito | Critério de aceite (EARS) |\n|---|---|---|\n| RF01 | X | O sistema deve X |\n"
    extra = "## Especificação técnica consolidada\n\nDesenho.\n\n"
    path = _sdd(tmp_path, tabela=tabela, extra=extra, source_docs=[], sizing="small")
    assert _lean(_problems(path)) == []


# --- RF03: molde -------------------------------------------------------------


def test_molde_em_sdd_small_passa(tmp_path):
    path = _sdd(tmp_path, source_docs=[], sizing="small", molde="crud")
    assert _lean(_problems(path)) == []


def test_molde_em_sdd_medium_reprova(tmp_path):
    problems = _lean(_problems(_sdd(tmp_path, molde="crud")))
    assert problems == ["SDD-TST-0001: `molde` só vale em SDD small (sizing medium)."]


def test_molde_com_nome_invalido_reprova(tmp_path):
    problems = _lean(_problems(_sdd(tmp_path, source_docs=[], sizing="small", molde="Crud_Novo")))
    assert problems == ["SDD-TST-0001: `molde` com nome inválido ('Crud_Novo'); use ^[a-z0-9][a-z0-9-]*$."]


def test_molde_vale_em_qualquer_status(tmp_path):
    problems = _lean(_problems(_sdd(tmp_path, molde="crud", status="approved")))
    assert problems == ["SDD-TST-0001: `molde` só vale em SDD small (sizing medium)."]


def test_molde_em_sdd_anterior_a_2_7_0_nao_muda(tmp_path):
    path = _sdd(tmp_path, created=ANTIGO, molde="Crud_Novo")
    assert _lean(_problems(path)) == []


# --- RF06: template ----------------------------------------------------------


def _secoes(texto: str) -> list[str]:
    return [ln[3:].strip() for ln in texto.splitlines() if ln.startswith("## ")]


def test_template_tem_as_secoes_na_ordem():
    secoes = _secoes(TEMPLATE.read_text(encoding="utf-8"))
    esperado = [
        "Resumo executivo",
        "Requisitos consolidados",
        "Decomposição em tasks",
        "Critérios de aceite / definição de pronto",
        "Instruções específicas para a IA implementadora",
        "Verificação de escopo (nada a mais, nada a menos)",
        "Evidência de verificação",
        "Rastreabilidade",
    ]
    assert [s.split(" (preencher")[0] for s in secoes] == esperado


def test_template_explica_arquivos_origem_e_molde():
    texto = TEMPLATE.read_text(encoding="utf-8")
    assert HEADER.splitlines()[0] in texto
    assert "união da coluna `Arquivos`" in texto
    assert "`Origem` igual a `—`" in texto
    assert "molde: crud" in texto


def test_template_preenchido_passa_como_sdd_enxuta(tmp_path):
    texto = TEMPLATE.read_text(encoding="utf-8")
    corpo = texto.split("\n---\n", 1)[1]
    corpo = corpo.replace(HEADER, HEADER + ROWS, 1)
    corpo = corpo.replace(
        "| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |\n|---|---|---|---|---|\n",
        "| # | Task | RF(s) de origem | Arquivos tocados | Depende de (#) |\n|---|---|---|---|---|\n"
        "| 1 | Fazer | RF01, RF02 | `app/lista.py` | |\n",
        1,
    )
    path = _sdd(tmp_path)
    fm = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    path.write_text(fm + "\n---\n" + corpo, encoding="utf-8")
    assert _problems(path) == []


# --- RF05: fidelidade de RF nas duas direções --------------------------------


def _spec_texto(rfs: list[str]) -> str:
    linhas = "".join(f"| {rf} | Req | O sistema deve fazer | `a.py` |\n" for rf in rfs)
    return (
        "---\nid: X\ntype: SPEC\n---\n\n# Parte 1\n\n## Requisitos funcionais\n\n"
        "| RF-ID | Requisito | Critério de aceite (EARS) | Arquivos |\n|---|---|---|---|\n" + linhas
    )


def _central(tmp_path: Path, specs: dict[str, list[str]]) -> Path:
    central = tmp_path / "central"
    entradas = ""
    for spec_id, rfs in specs.items():
        rel = f"docs/TST/03-spec/{spec_id}.md"
        (central / Path(rel).parent).mkdir(parents=True, exist_ok=True)
        (central / rel).write_text(_spec_texto(rfs), encoding="utf-8")
        entradas += f'  - id: {spec_id}\n    type: SPEC\n    status: approved\n    path: "{rel}"\n'
    (central / "registry.yaml").write_text("documents:\n" + entradas, encoding="utf-8")
    return central


def test_fidelity_spec_e_sdd_iguais_passa(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF01", "RF02"]})
    assert check_sdd_source_docs(_sdd(tmp_path), central) == []


def test_fidelity_rf_da_spec_fora_da_sdd_reprova(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF01", "RF02", "RF03", "RF07"]})
    problems = check_sdd_source_docs(_sdd(tmp_path), central)
    assert problems == [
        f"SDD-TST-0001: RFs de {SPEC_ID} fora da SDD: RF03, RF07; RFs da SDD fora de {SPEC_ID}: nenhum."
    ]


def test_fidelity_rf_da_sdd_fora_da_spec_reprova(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF01"]})
    problems = check_sdd_source_docs(_sdd(tmp_path), central)
    assert problems == [f"SDD-TST-0001: RFs de {SPEC_ID} fora da SDD: nenhum; RFs da SDD fora de {SPEC_ID}: RF02."]


def test_fidelity_hifen_nao_conta(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF-01", "RF-02"]})
    assert check_sdd_source_docs(_sdd(tmp_path), central) == []


def test_fidelity_duas_specs_cada_rf_contra_a_sua(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF01", "RF02"], SPEC2_ID: ["RF01", "RF05"]})
    source_docs = [{"id": SPEC_ID, "url": URL + SPEC_PATH}, {"id": SPEC2_ID, "url": URL + SPEC2_PATH}]
    tabela = HEADER + ROWS + f"| RF01 | {SPEC2_ID} | Outro | `b.py` |\n"
    problems = check_sdd_source_docs(_sdd(tmp_path, tabela=tabela, source_docs=source_docs), central)
    assert problems == [
        f"SDD-TST-0001: RFs de {SPEC2_ID} fora da SDD: RF05; RFs da SDD fora de {SPEC2_ID}: nenhum."
    ]


def test_fidelity_spec_fora_do_registry_nao_compara(tmp_path):
    central = _central(tmp_path, {SPEC2_ID: ["RF09"]})
    problems = check_sdd_source_docs(_sdd(tmp_path), central)
    assert len(problems) == 1
    assert "não encontrado" in problems[0]


def test_fidelity_sdd_anterior_a_2_7_0_nao_compara(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF01", "RF02", "RF03"]})
    assert check_sdd_source_docs(_sdd(tmp_path, created=ANTIGO), central) == []


def test_fidelity_sdd_sem_tabela_enxuta_nao_compara(tmp_path):
    central = _central(tmp_path, {SPEC_ID: ["RF01", "RF02", "RF03"]})
    tabela = "| RF | Requisito |\n|---|---|\n| RF01 | X |\n"
    assert check_sdd_source_docs(_sdd(tmp_path, tabela=tabela), central) == []
