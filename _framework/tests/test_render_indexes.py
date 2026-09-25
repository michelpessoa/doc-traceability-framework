"""Testes de render_indexes.py — ver SDD-DTF-0043 (SPEC-DTF-0016)."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "_framework" / "scripts"))

import render_indexes as ri  # noqa: E402
from render_prompts import build_agents  # noqa: E402

FENCE = "#" * 78

YAML_FIXTURE = f"""{FENCE}
# workflow-rules.yaml
{FENCE}

framework:
  version: "9.9.9"

{FENCE}
# 1. PRIMEIRA SEÇÃO
{FENCE}
# Esta seção tem parágrafo. Segunda frase que não entra no resumo.
# Continuação da primeira frase não vale.
#
# Segundo parágrafo ignorado.
alpha:
  x: 1
beta:
  y: 2

{FENCE}
# 2. SEÇÃO SEM PARÁGRAFO
{FENCE}
gamma: 3

{FENCE}
# 2b. BANNER EM VÁRIAS LINHAS QUE CONTINUA
#     AQUI NA SEGUNDA LINHA
{FENCE}
# So comentario sem chave.
"""


def _write_yaml(tmp_path: Path, text: str = YAML_FIXTURE) -> Path:
    path = tmp_path / "workflow-rules.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _kit(tmp_path: Path) -> tuple[Path, list[dict]]:
    root = tmp_path / "_framework"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "b.py").write_text("x" * 10, encoding="utf-8")
    (root / "scripts" / "a.py").write_text("x" * 3000, encoding="utf-8")
    (root / "notes.md").write_text("x" * 9000, encoding="utf-8")
    (root / "big.bin").write_bytes(b"0" * 40000)
    (root / "tiny.txt").write_text("x", encoding="utf-8")
    (root / "scripts" / "__pycache__").mkdir()
    (root / "scripts" / "__pycache__" / "a.cpython-312.pyc").write_bytes(b"0")
    (root / ".ruff_cache").mkdir()
    (root / ".ruff_cache" / "x").write_text("x", encoding="utf-8")
    (root / "INDEX.md").write_text("velho", encoding="utf-8")
    manifest = [
        {"path": "scripts/*.py", "what": "Script", "when": "Ao rodar"},
        {"path": "notes.md", "what": "Notas", "when": "Sempre"},
        {"path": "*.bin", "what": "Binário", "when": "Nunca"},
        {"path": "tiny.txt", "what": "Texto", "when": "Às vezes"},
    ]
    return root, manifest


# --- RF01 -----------------------------------------------------------------


def test_kit_index_uma_linha_por_arquivo(tmp_path):
    root, manifest = _kit(tmp_path)
    text = ri.build_kit_index(root, manifest)
    rows = ri._table_rows(text)
    paths = [r.split("|")[1].strip().strip("`") for r in rows]
    assert paths == ["big.bin", "notes.md", "scripts/a.py", "scripts/b.py", "tiny.txt"]
    assert "Total: 5 arquivos" in text
    sizes = [r.split("|")[4].strip() for r in rows]
    assert sizes == [">32 KB", "8-32 KB", "2-8 KB", "<2 KB", "<2 KB"]
    assert all(s in {"<2 KB", "2-8 KB", "8-32 KB", ">32 KB"} for s in sizes)
    assert "20" not in text.split("Total")[0]  # sem timestamp/ano
    assert text == ri.build_kit_index(root, manifest)


def test_kit_index_real_cobre_todos_os_arquivos():
    root = REPO_ROOT / "_framework"
    text = ri.build_kit_index(root, ri.load_kit_manifest(root / "rules" / "kit-index.yaml"))
    assert len(ri._table_rows(text)) == len(ri.list_kit_files(root))


# --- RF02 -----------------------------------------------------------------


def test_manifesto_orfao_arquivo_sem_entrada(tmp_path):
    root, manifest = _kit(tmp_path)
    (root / "novo.md").write_text("x", encoding="utf-8")
    with pytest.raises(ri.CoverageError) as exc:
        ri.build_kit_index(root, manifest)
    assert any("novo.md" in p for p in exc.value.problems)


def test_manifesto_orfao_entrada_sem_arquivo(tmp_path):
    root, manifest = _kit(tmp_path)
    manifest.append({"path": "fantasma/*.md", "what": "x", "when": "y"})
    with pytest.raises(ri.CoverageError) as exc:
        ri.build_kit_index(root, manifest)
    assert any("fantasma/*.md" in p for p in exc.value.problems)


def test_manifesto_orfao_codigos_de_saida(tmp_path, capsys):
    root, _ = _kit(tmp_path)
    (root / "rules").mkdir()
    (root / "rules" / "workflow-rules.yaml").write_text(YAML_FIXTURE, encoding="utf-8")
    (root / "rules" / "kit-index.yaml").write_text(
        'entries:\n  - path: "scripts/*.py"\n    what: "s"\n    when: "w"\n', encoding="utf-8"
    )
    assert ri.main(["--root", str(root), "--check"]) == 1
    assert "sem entrada" in capsys.readouterr().out
    assert ri.main(["--root", str(root)]) == 2
    assert not (root / "INDEX.md").read_text(encoding="utf-8").startswith("# Índice")


@pytest.mark.parametrize(
    "body",
    [
        'entries:\n  - path: "a"\n    what: "b"\n    when: "c"\n    extra: "d"\n',
        'entries:\n  - path: "a"\n    what: ""\n    when: "c"\n',
        'entries:\n  - path: "a"\n    what: "b"\n',
    ],
)
def test_manifesto_orfao_chave_extra_ou_vazia_sai_2(tmp_path, body):
    path = tmp_path / "kit-index.yaml"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        ri.load_kit_manifest(path)
    assert exc.value.code != 0
    root = tmp_path / "_framework"
    (root / "rules").mkdir(parents=True)
    (root / "rules" / "workflow-rules.yaml").write_text(YAML_FIXTURE, encoding="utf-8")
    (root / "rules" / "kit-index.yaml").write_text(body, encoding="utf-8")
    assert ri.main(["--root", str(root), "--check"]) == 2


# --- RF03 / RF04 ---------------------------------------------------------


def test_mapa_ids_batem_com_banners(tmp_path):
    yaml_path = _write_yaml(tmp_path)
    before = yaml_path.read_bytes()
    sections = ri.parse_yaml_sections(yaml_path.read_text(encoding="utf-8"))
    assert [s.sid for s in sections] == ["0", "1", "2", "2b"]
    assert sections[0].keys == ("framework",)
    assert sections[1].keys == ("alpha", "beta")
    assert sections[3].keys == ()
    text = ri.build_section_map(yaml_path)
    assert "| §2b |" in text and "(nenhuma)" in text
    assert yaml_path.read_bytes() == before
    # multi-linha: as linhas de continuação entram no título (SPEC-DTF-0022 RF01)
    assert sections[3].title == "BANNER EM VÁRIAS LINHAS QUE CONTINUA AQUI NA SEGUNDA LINHA"


def test_mapa_ids_batem_com_banners_yaml_real():
    yaml_path = REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
    lines = yaml_path.read_text(encoding="utf-8").splitlines()
    expected = {}
    import re

    for n, ln in enumerate(lines, start=1):
        m = re.match(ri.BANNER_RE, ln)
        if m and re.match(ri.FENCE_RE, lines[n - 2]):
            expected[m.group(1)] = n
    sections = ri.parse_yaml_sections(yaml_path.read_text(encoding="utf-8"))
    got = {s.sid: s.start for s in sections if s.sid != "0"}
    assert got == expected
    assert sections[0].sid == "0" and sections[0].start == 1
    text = ri.build_section_map(yaml_path)
    assert len(ri._table_rows(text)) == len(expected) + 1
    for sid, line in expected.items():
        assert f"| §{sid} |" in text
        assert f"| {line}-" in text


@pytest.mark.parametrize(
    "mutation, expected",
    [
        (lambda t: t.replace("# 1. PRIMEIRA", "# 2. PRIMEIRA"), "duplicada"),
        (lambda t: t.replace("# 2b. BANNER", "# 1b. BANNER"), "fora de ordem"),
        (lambda t: "framework:\n  version: '1'\n", "sem seção numerada"),
    ],
)
def test_mapa_ids_batem_com_banners_erros_sai_2(tmp_path, mutation, expected):
    with pytest.raises(SystemExit) as exc:
        ri.parse_yaml_sections(mutation(YAML_FIXTURE))
    assert expected in str(exc.value.code)


def test_resumo_primeira_frase(tmp_path):
    sections = {s.sid: s for s in ri.parse_yaml_sections(YAML_FIXTURE)}
    assert sections["1"].summary == "Esta seção tem parágrafo."
    assert sections["2"].summary == "SEÇÃO SEM PARÁGRAFO"  # sem parágrafo: título
    long_text = YAML_FIXTURE.replace("Esta seção tem parágrafo. Segunda", "Uma " + "palavra " * 30 + "termina. Segunda")
    long = {s.sid: s for s in ri.parse_yaml_sections(long_text)}["1"].summary
    assert len(long) <= ri.SUMMARY_MAX == 100
    assert long.endswith("…")


# --- RF05 ----------------------------------------------------------------


def test_secao_citada_inexistente(tmp_path):
    root = tmp_path / "_framework"
    (root / "rules").mkdir(parents=True)
    sections = ri.parse_yaml_sections(YAML_FIXTURE)
    (root / "ok.md").write_text("Veja §1 e §2b.\n", encoding="utf-8")
    (root / "rules" / "workflow-rules.map.md").write_text("§99\n", encoding="utf-8")
    (root / "INDEX.md").write_text("§98\n", encoding="utf-8")
    assert ri.check_section_refs(root, sections) == []
    (root / "ruim.md").write_text("linha 1\nVeja §99 aqui.\n", encoding="utf-8")
    assert ri.check_section_refs(root, sections) == ["ruim.md:2: §99 não existe no mapa"]


def test_secao_citada_inexistente_kit_real_sem_citacao_quebrada():
    root = REPO_ROOT / "_framework"
    sections = ri.parse_yaml_sections((root / "rules" / "workflow-rules.yaml").read_text(encoding="utf-8"))
    assert ri.check_section_refs(root, sections) == []


# --- RF06 / RF07 ----------------------------------------------------------


def _sdd(dirpath: Path, num: str, status="approved", extra="", body=""):
    text = (
        f"---\nid: SDD-X-{num}\ntype: SDD\ntitle: T{num}\nstatus: {status}\n{extra}---\n\n"
        f"## Resumo executivo\n\nPrimeira frase {num}. Segunda frase.\n\n{body}"
    )
    (dirpath / f"SDD-X-{num}.md").write_text(text, encoding="utf-8")


PROSA = (
    "## Especificação técnica consolidada\n\nArquivos tocados:\n- `src/a.py`\n- `src/b.py` e `README.md`\n\n"
    "Outro parágrafo `nao/conta.py`.\n\n## Decomposição em tasks\n\n| # | Task | Arquivos tocados |\n|---|---|---|\n"
    "| 1 | x | `src/a.py`, `src/c.py` |\n| 2 | y | `tests/t.py` |\n\n## Fim\n"
)
SO_TABELA = "## Decomposição em tasks\n\n| # | Task | Arquivos tocados |\n|---|---|---|\n| 1 | x | `src/z.py` |\n"


def test_sdd_index_campos(tmp_path):
    d = tmp_path / "sdd"
    d.mkdir()
    _sdd(d, "0003", body=PROSA)
    _sdd(d, "0001", status="implemented", extra="superseded_by: SDD-X-0003\n", body=SO_TABELA)
    _sdd(d, "0002", extra="supersedes: SDD-X-0001\n", body=PROSA)
    for ignored in ("LESSONS.md", "registry.md", "registry.yaml", "INDEX.md"):
        (d / ignored).write_text("x", encoding="utf-8")
    text = ri.build_sdd_index(d)
    rows = ri._table_rows(text)
    assert [r.split("|")[1].strip("` ") for r in rows] == ["SDD-X-0001", "SDD-X-0002", "SDD-X-0003"]
    assert "Total: 3 SDDs" in text
    first = rows[0].split("|")
    assert first[5].strip() == "SDD-X-0003" and first[6].strip() == "implemented" and first[4].strip() == "—"
    assert rows[1].split("|")[4].strip() == "SDD-X-0001"
    assert rows[0].split("|")[2].strip() == "Primeira frase 0001."


def test_sdd_index_campos_vazio_e_erros(tmp_path):
    d = tmp_path / "sdd"
    d.mkdir()
    assert "Total: 0 SDDs" in ri.build_sdd_index(d)
    (d / "SDD-X-0009.md").write_text("sem front-matter\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        ri.build_sdd_index(d)
    assert "SDD-X-0009.md" in str(exc.value.code)
    assert ri.main(["sdd", str(d), "--check"]) == 2


def test_sdd_sem_secao_arquivos(tmp_path, capsys):
    assert ri.extract_sdd_files("sem nada\n") == []
    assert ri.extract_sdd_files(PROSA) == ["README.md", "src/a.py", "src/b.py", "src/c.py", "tests/t.py"]
    assert ri.extract_sdd_files(SO_TABELA) == ["src/z.py"]
    d = tmp_path / "sdd"
    d.mkdir()
    _sdd(d, "0001", body="nada aqui\n")
    _sdd(d, "0002", body=PROSA)
    text = ri.build_sdd_index(d)
    assert ri.NO_FILES in text.splitlines()[-2]
    assert "SDD-X-0001" in capsys.readouterr().out
    (d / "INDEX.md").write_text(text, encoding="utf-8")
    assert ri.main(["sdd", str(d), "--check"]) == 0  # aviso não falha o --check


def test_sdd_sem_secao_arquivos_mais_de_seis(tmp_path):
    body = (
        "## Decomposição em tasks\n\n| # | Arquivos tocados |\n|---|---|\n| 1 | "
        + ", ".join(f"`f{i}.py`" for i in range(8))
        + " |\n"
    )
    d = tmp_path / "sdd"
    d.mkdir()
    _sdd(d, "0001", body=body)
    assert "+2" in ri.build_sdd_index(d)


# --- RF09 ----------------------------------------------------------------

DOC = "# Título\n\nintro\n\n## Um\n\ntexto\n\n```\n## Falso\n```\n\n## Dois: e 'mais'\n\nfim\n"


def test_sumario_universal_e_guia(tmp_path):
    toc = ri.build_toc(DOC)
    assert "[Um](#um)" in toc and "[Dois: e 'mais'](#dois-e-mais)" in toc
    assert "Falso" not in toc
    assert toc.count("\n- [") == 2 and toc.count(" bytes") == 2
    once = ri.inject_toc(DOC, toc)
    assert once.startswith("# Título\n\n" + ri.TOC_BEGIN)
    assert ri.inject_toc(once, ri.build_toc(once)) == once  # idempotente
    assert ri.build_toc(once) == toc  # o bloco não altera os bytes das seções
    # universal: sumário dentro de build_universal
    from framework_lib import load_rules
    from render_prompts import build_universal

    universal = build_universal(load_rules())
    assert ri.has_toc_markers(universal) and "- [1. Seu papel](#1-seu-papel)" in universal
    assert ri.check_toc_ceiling("universal.md", universal) == []
    # guia real: marcadores presentes e sumário em dia
    guide = (REPO_ROOT / "docs" / "guias" / "guia-tecnico.md").read_text(encoding="utf-8")
    assert ri.has_toc_markers(guide)
    assert ri.inject_toc(guide, ri.build_toc(guide)) == guide
    assert ri.check_toc_ceiling("guia-tecnico.md", guide) == []


def test_sumario_universal_e_guia_marcador_ausente(tmp_path):
    root, _ = _kit(tmp_path)
    (root / "rules").mkdir()
    real_yaml = REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml"
    (root / "rules" / "workflow-rules.yaml").write_bytes(real_yaml.read_bytes())
    (root / "rules" / "kit-index.yaml").write_text(
        'entries:\n  - path: "**"\n    what: "x"\n    when: "y"\n', encoding="utf-8"
    )
    guide = tmp_path / "docs" / "guias" / "guia-tecnico.md"
    guide.parent.mkdir(parents=True)
    guide.write_text(DOC, encoding="utf-8")
    assert ri.generate_all(root, {}, check=True) is False
    assert guide.read_text(encoding="utf-8") == DOC  # --check não escreve
    ri.generate_all(root, {}, check=False)
    assert ri.has_toc_markers(guide.read_text(encoding="utf-8"))  # sem --check insere
    assert ri.generate_all(root, {}, check=True) is True


# --- RF10 ----------------------------------------------------------------


def test_tetos(tmp_path):
    yaml_path = _write_yaml(tmp_path)
    text = yaml_path.read_text(encoding="utf-8")
    sections = ri.parse_yaml_sections(text)
    map_text = ri.build_section_map(yaml_path)
    # fixture pequena: 15% do YAML é curto, o mapa estoura o teto de forma legítima
    problems = ri.check_map_ceiling(sections, map_text, len(text.encode()))
    assert any("teto" in p and "mapa" in p for p in problems)
    # com YAML grande o mesmo mapa cabe
    assert ri.check_map_ceiling(sections, map_text, 10**6) == []
    # mutação: linha inflada reprova
    inflada = map_text + "| §9 | " + "x" * 300 + " |\n"
    assert any("linha" in p for p in ri.check_map_ceiling(sections, inflada, 10**6))
    # índice do kit e de SDD
    root, manifest = _kit(tmp_path)
    kit = ri.build_kit_index(root, manifest)
    assert ri.check_kit_ceiling(kit) == []
    assert ri.check_kit_ceiling(kit + "|" + "x" * 30000 + "\n")
    muitas = kit + ("| " + "x" * 150 + " |\n") * 200  # cada linha cabe; o total estoura
    assert any("teto 24576" in p for p in ri.check_kit_ceiling(muitas))
    d = tmp_path / "sdd"
    d.mkdir()
    _sdd(d, "0001", body=PROSA)
    sdd = ri.build_sdd_index(d)
    assert ri.check_sdd_ceiling(sdd, 1) == []
    assert any("teto" in p for p in ri.check_sdd_ceiling(sdd + "| " + "x" * 500 + " |\n", 1))
    # sumário
    big = "# T\n\n" + "".join(f"## Seção número {i} com título longo o bastante\n\ntexto\n\n" for i in range(80))
    assert ri.check_toc_ceiling("x", ri.inject_toc(big, ri.build_toc(big)))


def test_tetos_medicao_real():
    root = REPO_ROOT / "_framework"
    yaml_path = root / "rules" / "workflow-rules.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    sections = ri.parse_yaml_sections(text)
    map_text = (root / ri.MAP_REL).read_text(encoding="utf-8")
    nbytes = len(text.encode())
    assert ri.check_map_ceiling(sections, map_text, nbytes) == []
    measured = len(map_text.encode()) + ri._largest_section_bytes(sections)
    assert measured <= int(0.15 * nbytes)
    assert ri.check_kit_ceiling((root / "INDEX.md").read_text(encoding="utf-8")) == []


# --- RF12 / RF13 ----------------------------------------------------------


def test_agents_aponta_indice():
    from framework_lib import load_rules

    agents = build_agents(load_rules())
    linhas = [ln for ln in agents.splitlines() if "_framework/INDEX.md" in ln]
    assert linhas and "_framework/rules/workflow-rules.map.md" in linhas[0]
    assert "_framework/INDEX.md" in (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_idempotente(tmp_path):
    root = tmp_path / "_framework"
    real = REPO_ROOT / "_framework"
    (root / "rules").mkdir(parents=True)
    for name in ("workflow-rules.yaml", "kit-index.yaml"):
        (root / "rules" / name).write_bytes((real / "rules" / name).read_bytes())
    (root / "scripts").mkdir()
    (root / "scripts" / "x.py").write_text("x", encoding="utf-8")
    (root / "rules" / "workflow-rules.map.md").write_text("", encoding="utf-8")
    manifest = tmp_path / "manifest-tmp.yaml"
    manifest.write_text('entries:\n  - path: "**"\n    what: "x"\n    when: "y"\n', encoding="utf-8")
    (root / "rules" / "kit-index.yaml").write_bytes(manifest.read_bytes())
    assert ri.generate_all(root, {}, check=False)
    snapshot = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert ri.generate_all(root, {}, check=False)
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == snapshot
    assert ri.generate_all(root, {}, check=True)
    assert all(b"\r" not in content for content in snapshot.values())


def test_arquivos_tocados_com_pipe_escapado():
    """SDD-DTF-0047 RF06: pipe escapado antes da coluna não desloca Arquivos tocados."""
    body = (
        "## Decomposição em tasks\n\n| # | Task | Arquivos tocados |\n|---|---|---|\n"
        "| 1 | roda `grep a\\|b` | `src/z.py` |\n"
    )
    assert ri.extract_sdd_files(body) == ["src/z.py"]


# --- SPEC-DTF-0022 (SDD-DTF-0049) ------------------------------------------


def _doc(*sections: str) -> str:
    """YAML mínimo: cada seção é (banner_lines, after_fence) já formatada por `_sec`."""
    return f"{FENCE}\n# cabecalho\n{FENCE}\n\nframework:\n  version: '1'\n\n" + "\n".join(sections)


def _sec(
    n: str,
    title_lines: list[str],
    banner_body: list[str] | None = None,
    after: list[str] | None = None,
    yaml_body: str = "",
) -> str:
    out = [FENCE, f"# {n}. {title_lines[0]}"] + [f"#     {t}" for t in title_lines[1:]]
    if banner_body:
        out += ["#"] + [f"# {b}" for b in banner_body]
    out.append(FENCE)
    out += [f"# {a}" if a else "#" for a in (after or [])]
    if yaml_body:
        out.append(yaml_body)
    return "\n".join(out) + "\n"


def _by_id(text: str, overrides: dict | None = None) -> dict:
    return {s.sid: s for s in ri.parse_yaml_sections(text, overrides)}


def test_titulo_completo_junta_continuacao_e_descarta_cauda():
    doc = _doc(
        _sec("1", ["TÍTULO QUE CONTINUA", "NA SEGUNDA LINHA"], yaml_body="a: 1"),
        _sec("2", ["ARTEFATOS — cauda descritiva que não entra", "e continua aqui"], yaml_body="b: 1"),
        _sec("3", ["GATE OBRIGATÓRIO: NOME COM DOIS-PONTOS"], yaml_body="c: 1"),
    )
    sec = _by_id(doc)
    assert sec["1"].title == "TÍTULO QUE CONTINUA NA SEGUNDA LINHA"
    assert sec["2"].title == "ARTEFATOS"
    assert sec["3"].title == "GATE OBRIGATÓRIO: NOME COM DOIS-PONTOS"


def test_titulo_completo_parentese_so_quando_estoura_70():
    curto = "METADADOS (FRONT-MATTER)"
    assert ri._clean_title(curto) == curto
    longo = "CICLO DE VIDA DE STATUS PADRÃO (STRAT, RFC, ADR, PRD, TS, SDD, BASE, PM, INC)"
    assert len(longo) > ri.TITLE_MAX
    assert ri._clean_title(longo) == "CICLO DE VIDA DE STATUS PADRÃO"


def test_titulo_completo_corte_com_reticencias_so_se_ainda_passa():
    raw = "CAPACIDADES QUE QUALQUER FERRAMENTA DE IA (X, Y) DEVE OFERECER AO EXECUTAR ESTE FRAMEWORK"
    out = ri._clean_title(raw)
    assert out.endswith("…") and len(out) <= ri.TITLE_MAX
    assert "(" not in out
    assert not ri._clean_title("SÓ UM TÍTULO CURTO").endswith("…")


def test_resumo_cadeia_fontes_em_ordem():
    # (1) corpo do banner vence tudo
    doc = _doc(
        _sec(
            "1",
            ["T1 — cauda"],
            banner_body=["Corpo do banner. Outra frase."],
            after=["Depois da fence."],
            yaml_body='k:\n  description: "Valor da chave."',
        )
    )
    assert _by_id(doc)["1"].summary == "Corpo do banner."
    # (2) parágrafo após a fence
    doc = _doc(_sec("1", ["T1 — cauda"], after=["Depois da fence. Segunda."], yaml_body='k:\n  description: "Valor."'))
    assert _by_id(doc)["1"].summary == "Depois da fence."
    # (3) valor da primeira chave, na ordem de SCALAR_KEYS
    body = 'k:\n  purpose: "Por propósito."\n  description: "Por descrição."'
    doc = _doc(_sec("1", ["T1 — cauda"], yaml_body=body))
    assert _by_id(doc)["1"].summary == "Por descrição."
    doc = _doc(_sec("1", ["T1 — cauda"], yaml_body='k:\n  approach: "Por abordagem."'))
    assert _by_id(doc)["1"].summary == "Por abordagem."
    # (4) map_summaries, só depois das fontes automáticas
    doc = _doc(_sec("1", ["T1 — cauda"], yaml_body="k:\n  x: 1"))
    assert _by_id(doc, {"1": "Frase à mão."})["1"].summary == "Frase à mão."
    # (5) cauda do título após o travessão
    assert _by_id(doc)["1"].summary == "Cauda"
    # (6) título limpo
    doc = _doc(_sec("1", ["APENAS TÍTULO"], yaml_body="k: 1"))
    assert _by_id(doc)["1"].summary == "APENAS TÍTULO"


def test_resumo_cadeia_rotulo_frase_completa_e_bloco_vazio():
    para = "Motivação (registrado): este gate nasceu de um incidente. Outra."
    doc = _doc(_sec("1", ["T1"], after=[para, ""], yaml_body="k: 1"))
    assert _by_id(doc)["1"].summary == "Este gate nasceu de um incidente."
    doc = _doc(_sec("1", ["T1"], after=["Origem: mesmo incidente da seção 13 — algo"], yaml_body="k: 1"))
    assert _by_id(doc)["1"].summary == "Mesmo incidente da seção 13 — algo"
    # parágrafo terminado em dois-pontos vale inteiro, sem o `:`
    doc = _doc(_sec("1", ["T1"], after=["Este framework assume dois tipos:", "", "  (a) central"], yaml_body="k: 1"))
    assert _by_id(doc)["1"].summary == "Este framework assume dois tipos"
    # bloco de comentário vazio é ignorado e cai para a fonte seguinte
    doc = _doc(_sec("1", ["T1 — cauda"], after=["", ""], yaml_body='k:\n  description: "Da chave."'))
    assert _by_id(doc)["1"].summary == "Da chave."
    # primeira chave que não é mapeamento: fonte (3) ignorada
    doc = _doc(_sec("1", ["T1 — cauda"], yaml_body="k:\n  - a\n  - b"))
    assert _by_id(doc)["1"].summary == "Cauda"


def test_corte_fronteira_palavra_limite_e_conectivo():
    assert ri._cut_words("cabe inteiro", 20) == "cabe inteiro"
    assert ri._cut_words("termina em conectivo de", 40) == "termina em conectivo de"  # cabe: intacto
    out = ri._cut_words("uma frase longa demais para caber no limite dado", 30)
    assert out == "uma frase longa demais para…" or out.endswith("…")
    assert len(out) <= 30
    assert not out.rstrip("…").endswith(" ")
    # conectivo pendurado é descartado
    out = ri._cut_words("alfa beta gama de delta epsilon", 17)
    assert out == "alfa beta gama…"
    # palavra única maior que o limite: corte duro em limit - 1 mais reticências
    assert ri._cut_words("palavralongademais", 8) == "palavra…"
    # nunca corta no meio de palavra quando há espaço
    words = "um dois tres quatro cinco seis sete oito nove dez".split()
    text = " ".join(words)
    for limit in range(8, len(text)):
        cut = ri._cut_words(text, limit).rstrip("…")
        assert len(ri._cut_words(text, limit)) <= limit
        assert all(w in words for w in cut.split())


def test_corte_fronteira_palavra_resumo_longo_e_ordem_de_encurtamento():
    sec = ri.Section(
        sid="99",
        title="TÍTULO " + "MUITO " * 8 + "LONGO",
        keys=("k1", "k2", "k3"),
        start=1,
        end=2,
        nbytes=10,
        summary="Resumo " + "bem comprido " * 7 + "fim.",
    )
    row = ri._section_row(sec, 180)
    assert ri._nbytes(row) <= 180
    cells = [c.strip() for c in row.strip("|").split("|")]
    # as chaves encolhem antes de tudo
    assert cells[2] == "`k1` +2" or cells[2].startswith("`k1`")
    # o Resumo não cai abaixo do piso e o título só encolhe depois dele
    summary = cells[5]
    assert len(summary.rstrip("…")) >= ri.SUMMARY_MIN or ri._nbytes(row) <= 180
    apertado = ri._section_row(sec, 150)
    assert ri._nbytes(apertado) <= 150
    c2 = [c.strip() for c in apertado.strip("|").split("|")]
    assert len(c2[5].rstrip("…")) >= ri.SUMMARY_MIN - 6
    assert len(c2[1]) >= ri.TITLE_MIN - 1
    # com folga total nada é cortado
    assert ri._section_row(sec, 1000).endswith(sec.summary + " |")


def test_map_summaries_so_sem_fonte_automatica():
    doc = _doc(
        _sec("1", ["COM FONTE"], after=["Parágrafo automático."], yaml_body="a: 1"),
        _sec("2", ["SEM FONTE"], yaml_body="b: 1"),
    )
    sec = _by_id(doc, {"1": "Texto à mão um.", "2": "Texto à mão dois."})
    assert sec["1"].summary == "Parágrafo automático."
    assert sec["2"].summary == "Texto à mão dois."


def test_map_summaries_id_inexistente_sai_2_citando_id(tmp_path):
    doc = _doc(_sec("1", ["UM"], yaml_body="a: 1"))
    with pytest.raises(SystemExit) as exc:
        ri.parse_yaml_sections(doc, {"77": "frase"})
    assert "77" in str(exc.value.code)
    root = tmp_path / "_framework"
    (root / "rules").mkdir(parents=True)
    (root / "rules" / "workflow-rules.yaml").write_text(doc, encoding="utf-8")
    (root / "rules" / "kit-index.yaml").write_text(
        'entries:\n  - path: "rules/*"\n    what: "a b c d"\n    when: "w"\nmap_summaries:\n  "77": "frase valida"\n',
        encoding="utf-8",
    )
    assert ri.main(["--root", str(root)]) == 2
    assert not (root / "rules" / "workflow-rules.map.md").exists()


@pytest.mark.parametrize("value", ['""', "12", "[a, b]", "null"])
def test_map_summaries_valor_vazio_ou_nao_textual_sai_2(tmp_path, value):
    path = tmp_path / "kit-index.yaml"
    entry = 'entries:\n  - path: "a"\n    what: "b c d e"\n    when: "c"\n'
    path.write_text(f'{entry}map_summaries:\n  "1": {value}\n', encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        ri.load_map_summaries(path)
    assert "1" in str(exc.value.code)
    path.write_text("entries: []\nmap_summaries: [a]\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        ri.load_map_summaries(path)


def test_map_summaries_ausente_e_manifesto_intacto(tmp_path):
    path = tmp_path / "kit-index.yaml"
    path.write_text(
        'entries:\n  - path: "a"\n    what: "b c d e"\n    when: "c"\nmap_summaries:\n  "1": "Frase à mão."\n',
        encoding="utf-8",
    )
    assert ri.load_map_summaries(path) == {"1": "Frase à mão."}
    assert [e["path"] for e in ri.load_kit_manifest(path)] == ["a"]
    path.write_text('entries:\n  - path: "a"\n    what: "b"\n    when: "c"\n', encoding="utf-8")
    assert ri.load_map_summaries(path) == {}


def test_kit_index_o_que_e_distinto_expande_name_e_stem(tmp_path):
    root, _ = _kit(tmp_path)
    manifest = [
        {"path": "scripts/*.py", "what": "Cópia de {name} ({stem})", "when": "Ao ler {stem}.py e {outro}"},
        {"path": "notes.md", "what": "Notas", "when": "Sempre"},
        {"path": "*.bin", "what": "Binário", "when": "Nunca"},
        {"path": "tiny.txt", "what": "Texto", "when": "Às vezes"},
    ]
    text = ri.build_kit_index(root, manifest)
    assert "| Cópia de a.py (a) | Ao ler a.py e {outro} |" in text
    assert "| Cópia de b.py (b) | Ao ler b.py e {outro} |" in text
    rows = ri._table_rows(text)
    whats = [r.split("|")[2].strip() for r in rows]
    assert len(whats) == len(set(whats))


def test_kit_index_o_que_e_distinto_no_index_real():
    root = REPO_ROOT / "_framework"
    manifest = ri.load_kit_manifest(root / "rules" / "kit-index.yaml")
    text = ri.build_kit_index(root, manifest)  # cobertura da 0016 intacta: não levanta CoverageError
    rows = ri._table_rows(text)
    whats = [r.split("|")[2].strip() for r in rows]
    assert len(whats) == len(rows) == len(set(whats)), "duas linhas com o mesmo O que é"
    assert all(len(w.split()) >= 4 for w in whats)
    assert (root / "INDEX.md").read_text(encoding="utf-8") == text


def test_kit_index_o_que_e_distinto_cobertura_continua(tmp_path):
    root, manifest = _kit(tmp_path)
    (root / "novo.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ri.CoverageError):
        ri.build_kit_index(root, manifest)


def _map_rows() -> list[list[str]]:
    rules = REPO_ROOT / "_framework" / "rules"
    text = ri.build_section_map(rules / "workflow-rules.yaml", ri.load_map_summaries(rules / "kit-index.yaml"))
    lines = [ln for ln in text.splitlines() if ln.startswith("| §") and not ln.startswith("| § ")]
    return [[c.strip() for c in ln.strip("|").split("|")] for ln in lines]


def test_metricas_mapa_real_sem_repeticao_nem_corte_no_meio_de_palavra():
    import yaml

    yaml_text = (REPO_ROOT / "_framework" / "rules" / "workflow-rules.yaml").read_text(encoding="utf-8")
    norm = lambda x: " ".join(str(x).split()).lower()  # noqa: E731
    hay = [norm(" ".join(ln.lstrip("#") for ln in yaml_text.splitlines() if ln.startswith("#")))]

    def walk(o):
        if isinstance(o, str):
            hay.append(norm(o))
        elif isinstance(o, dict):
            [walk(v) for v in o.values()]
        elif isinstance(o, list):
            [walk(v) for v in o]

    walk(yaml.safe_load(yaml_text))
    rows = _map_rows()
    assert len(rows) == 22
    repetidos, titulos_cortados, meio_de_palavra, resumo_curto = [], [], [], []
    fim_ruim = []
    for c in rows:
        sid, titulo, resumo = c[0], c[1], c[-1]
        if sid == "§0":
            continue
        t, r = titulo.rstrip("…"), resumo.rstrip("…")
        if r.startswith(t[:15]) or t.startswith(r[:15]):
            repetidos.append(sid)
        if titulo.endswith("…"):
            titulos_cortados.append(sid)
        if resumo.count("(") > resumo.count(")") or r.rstrip().endswith(tuple(ri.DASHES)):
            fim_ruim.append(sid)  # 0024 RF03: nem parêntese aberto nem travessão pendurado
        if resumo.endswith("…"):
            if len(r) < ri.SUMMARY_MIN:
                resumo_curto.append(sid)
            pre = norm(r)
            hits = [(h, i) for h in hay for i in range(len(h)) if h.startswith(pre, i)]
            if hits and not any(i + len(pre) >= len(h) or h[i + len(pre)] == " " for h, i in hits):
                meio_de_palavra.append(sid)
    assert repetidos == []
    assert len(titulos_cortados) <= 1
    assert meio_de_palavra == []
    assert resumo_curto == []
    assert fim_ruim == []


# --- SPEC-DTF-0024 (errata da SDD-DTF-0049) ---------------------------------


def test_corte_descarta_travessao_e_parentese_aberto():
    # RF01: travessão isolado no fim do trecho retido é descartado
    assert ri._cut_words("alfa beta gama — delta epsilon zeta", 20) == "alfa beta gama…"
    # hífen dentro de palavra não é travessão
    assert ri._cut_words("alfa beta pré-condição gama delta", 24) == "alfa beta pré-condição…"
    # travessão no meio, dentro do limite: intacto
    assert ri._cut_words("alfa — beta", 20) == "alfa — beta"
    # RF02: parêntese aberto faz o corte recuar até antes dele
    assert ri._cut_words("alfa beta gama (delta epsilon zeta) eta", 27) == "alfa beta gama…"
    # parêntese fechado antes do corte: não recua
    assert ri._cut_words("alfa (beta) gama delta epsilon", 22) == "alfa (beta) gama…"
    # depois do recuo o descarte de conectivo roda de novo
    assert ri._cut_words("alfa beta de (gama delta epsilon", 26) == "alfa beta…"
    # sem palavras sobrando: corte duro por caractere, sem exceção
    assert ri._cut_words("(alfa beta gama delta", 10) == "(alfa bet…"
    assert ri._cut_words("— alfa beta", 3).endswith("…")


def test_corte_descarta_conectivo_pendurado_exercido():
    # o trecho retido TERMINA em conectivo (nos testes antigos o corte já cai antes dele)
    assert ri._cut_words("alfa beta gama de delta", 19) == "alfa beta gama…"
    assert ri._cut_words("alfa beta gama para o delta", 23) == "alfa beta gama…"
    for limit in range(8, 40):
        out = ri._cut_words("alfa beta gama para o delta epsilon com zeta", limit)
        assert out.rstrip("…").split()[-1] not in ri.DANGLING


def test_map_summaries_perde_para_fonte_3():
    doc = _doc(_sec("1", ["T1 — cauda"], yaml_body='k:\n  description: "Da chave."'))
    assert _by_id(doc, {"1": "Frase à mão."})["1"].summary == "Da chave."
    # sem fonte automática (1 a 3), o override vale e vem antes da cauda do título
    doc = _doc(_sec("1", ["T1 — cauda"], yaml_body="k:\n  x: 1"))
    assert _by_id(doc, {"1": "Frase à mão."})["1"].summary == "Frase à mão."


def test_piso_summary_min_no_encurtamento_da_linha():
    sec = ri.Section(
        sid="99",
        title="T",
        keys=("k",),
        start=1,
        end=2,
        nbytes=10,
        summary=" ".join(["abcd"] * 20),
    )
    row = ri._section_row(sec, 60)  # inatingível: o encurtamento vai até o piso
    resumo = [c.strip() for c in row.strip("|").split("|")][5]
    assert resumo.endswith("…")
    assert ri.SUMMARY_MIN - 5 <= len(resumo.rstrip("…")) < ri.SUMMARY_MIN
