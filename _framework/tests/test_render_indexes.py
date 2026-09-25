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
    # multi-linha: título é a primeira linha
    assert sections[3].title == "BANNER EM VÁRIAS LINHAS QUE CONTINUA"


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
