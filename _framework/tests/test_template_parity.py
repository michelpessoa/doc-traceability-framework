"""Paridade byte a byte dos templates `*.md` entre original e bundle — SDD-DTF-0042 (RF08, RF09)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "_framework" / "templates"
BUNDLE_TEMPLATES_DIR = REPO_ROOT / "_framework" / "skills" / "doc-traceability-framework" / "templates"


def _templates_md(directory: Path) -> list[str]:
    return sorted(p.name for p in directory.glob("*.md"))


def _divergentes(original_dir: Path, bundle_dir: Path) -> list[str]:
    """Nomes de *.md de original_dir ausentes ou com bytes diferentes em bundle_dir."""
    out = []
    for name in _templates_md(original_dir):
        twin = bundle_dir / name
        if not twin.is_file() or twin.read_bytes() != (original_dir / name).read_bytes():
            out.append(name)
    return out


def test_sdd_template_paridade():
    original = TEMPLATES_DIR / "sdd.template.md"
    bundled = BUNDLE_TEMPLATES_DIR / "sdd.template.md"
    assert original.is_file()
    assert bundled.is_file()
    assert original.read_bytes() == bundled.read_bytes()


def test_templates_md_paridade():
    assert TEMPLATES_DIR.is_dir()
    assert BUNDLE_TEMPLATES_DIR.is_dir()
    assert _templates_md(TEMPLATES_DIR), "nenhum template original encontrado"
    divergentes = _divergentes(TEMPLATES_DIR, BUNDLE_TEMPLATES_DIR)
    assert divergentes == [], f"templates divergentes ou ausentes no bundle: {divergentes}"


def test_bundle_sem_template_orfao():
    assert BUNDLE_TEMPLATES_DIR.is_dir()
    orfaos = sorted(set(_templates_md(BUNDLE_TEMPLATES_DIR)) - set(_templates_md(TEMPLATES_DIR)))
    assert not orfaos, f"templates no bundle sem original: {orfaos}"


def test_divergentes_detecta_diferenca(tmp_path):
    orig = tmp_path / "orig"
    bundle = tmp_path / "bundle"
    orig.mkdir()
    bundle.mkdir()
    (orig / "igual.md").write_bytes(b"a\n")
    (bundle / "igual.md").write_bytes(b"a\n")
    (orig / "diferente.md").write_bytes(b"a\n")
    (bundle / "diferente.md").write_bytes(b"a \n")
    (orig / "ausente.md").write_bytes(b"a\n")
    assert _divergentes(orig, bundle) == ["ausente.md", "diferente.md"]
