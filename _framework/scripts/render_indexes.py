#!/usr/bin/env python3
"""
render_indexes.py

Gera os índices navegáveis do kit (SDD-DTF-0043, SPEC-DTF-0016):

- `_framework/INDEX.md`: uma linha por arquivo do kit (RF01, RF02);
- `_framework/rules/workflow-rules.map.md`: mapa de seções do YAML (RF03, RF04);
- `docs/sdd/INDEX.md`: uma linha por SDD de um repositório de projeto (RF06, RF07);
- sumário de `universal.md` e de `docs/guias/guia-tecnico.md` (RF09).

Toda a lógica vive aqui; `render_prompts.py` só faz a fiação (RF11).
Saída determinística: sem timestamp, ordenada, LF, UTF-8.

Uso:
    python3 render_indexes.py [--check]              # índices do kit
    python3 render_indexes.py sdd <dir> [--check]    # INDEX.md de SDDs

Códigos de saída: 0 em dia, 1 divergência ou teto excedido, 2 erro estrutural.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from framework_lib import find_rules_file, read_frontmatter, split_table_row  # noqa: E402

BANNER_RE = r"^# (\d+[a-z]?)\. (.+)$"
FENCE_RE = r"^#{20,}$"
LARGEST_SECTION_EXCLUDES = {"0"}
SUMMARY_MAX = 100
SUMMARY_MIN = 30  # piso do Resumo ao encurtar a linha do mapa (SPEC-DTF-0022 RF03)
TITLE_MAX = 70  # caracteres do título da linha do mapa (RF01)
TITLE_MIN = 20  # piso do título ao encurtar a linha do mapa (RF03)
SDD_SUMMARY_MAX = 140
SIZE_BUCKETS = [(2048, "<2 KB"), (8192, "2-8 KB"), (32768, "8-32 KB"), (None, ">32 KB")]
CEILINGS = {
    "kit_index_row": 200,
    "kit_index_total": 24576,
    "map_row": 180,
    "map_header": 400,
    "sdd_row": 400,
    "sdd_base": 1024,
    "toc_total": 3072,
}
MAP_FRACTION = 0.15
LABEL_RE = re.compile(r"^(?:Motivação|Origem)(?:\s*\([^)]*\))?\s*:\s*")  # rótulo removido (RF02)
SCALAR_KEYS = ("description", "purpose", "instructions", "approach", "applies_when")  # fonte (3)
DANGLING = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na",
    "nos", "nas", "por", "para", "com", "sem", "ao", "aos", "e", "ou", "que", "como", "se",
    "->", "+",
}  # conectivos que não podem terminar um corte (RF03)
SDD_MAX_FILES = 6
IGNORED_DIRS = {"__pycache__", ".ruff_cache", ".pytest_cache", ".mypy_cache"}
TOC_BEGIN = "<!-- BEGIN GENERATED: sumário -->"
TOC_END = "<!-- END GENERATED -->"
MAP_REL = "rules/workflow-rules.map.md"
GUIDE_REL = "docs/guias/guia-tecnico.md"
NO_FILES = "(sem seção de arquivos)"
SDD_NAME_RE = re.compile(r"^SDD-[A-Z0-9]+-\d{4}\.md$")


@dataclass(frozen=True)
class Section:
    sid: str  # "0", "3b", "13" (exibido como "§13")
    title: str  # título completo e limpo (RF01); "preâmbulo" para §0
    keys: tuple[str, ...]  # chaves de topo YAML na faixa
    start: int  # linha (1-based) da linha `# N. TÍTULO`; 1 para §0
    end: int  # última linha da seção
    nbytes: int
    summary: str  # RF02, <= SUMMARY_MAX


class CoverageError(Exception):
    """Cobertura do manifesto quebrada (RF02): guarda cada órfão."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def _first_sentence(text: str, limit: int) -> str:
    flat = " ".join(text.split())
    parts = re.split(r"(?<=[.!?])\s", flat, maxsplit=1)
    sentence = parts[0]
    if len(sentence) > limit:
        sentence = sentence[: limit - 1].rstrip() + "…"
    return sentence


def _cut_words(text: str, limit: int) -> str:
    """Corta em fronteira de palavra, sem conectivo pendurado; no máximo `limit` com o `…` (RF03)."""
    if len(text) <= limit:
        return text
    head = text[: limit - 1]
    if text[limit - 1] != " ":
        idx = head.rfind(" ")
        head = head[:idx] if idx > 0 else ""
    words = head.split()
    while words and (words[-1].lower() in DANGLING or words[-1][-1] in "(:,;"):
        words.pop()
    if not words:
        return text[: limit - 1].rstrip() + "…"
    return " ".join(words) + "…"


def _sentence(text: str, limit: int) -> str:
    """Primeira frase completa de `text`, sem rótulo, capitalizada e cortada em `limit` (RF02)."""
    flat = LABEL_RE.sub("", " ".join(text.split()), count=1)
    m = re.search(r"[.!?](?=\s+[A-ZÀ-ÖØ-Þ\"'`(])", flat)
    sentence = (flat[: m.end()] if m else flat).rstrip(":;, ")
    if not sentence:
        return ""
    return _cut_words(sentence[0].upper() + sentence[1:], limit)


def _clean_title(raw: str) -> str:
    """Título completo e limpo até o fim de uma expressão (RF01)."""
    title = " ".join(raw.split()).split(" — ")[0].strip()
    if len(title) > TITLE_MAX:
        title = " ".join(re.sub(r"\s*\([^)]*\)", "", title).split())
    return _cut_words(title, TITLE_MAX)


def _cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


def _nbytes(text: str) -> int:
    return len(text.encode("utf-8"))


def _emit(path: Path, label: str, content: str, check: bool) -> bool:
    """Escreve (ou confere) um índice gerado."""
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        print(f"✅ {label}: em dia.")
        return True
    if check:
        motivo = "ausente" if not path.is_file() else "divergente do gerado"
        print(f"❌ {label}: {motivo} — rode render_indexes.py.")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"✅ {label}: gerado.")
    return True


def _table_rows(text: str) -> list[str]:
    """Linhas de corpo de tabela (exclui cabeçalho e separador)."""
    rows = [ln for ln in text.splitlines() if ln.startswith("|")]
    return rows[2:]


# ---------------------------------------------------------------------------
# Mapa de seções do YAML (RF03, RF04)
# ---------------------------------------------------------------------------


def _is_fence(line: str) -> bool:
    return bool(re.match(FENCE_RE, line.rstrip("\n")))


def _banner_parts(lines: list[str], title_idx: int, hi: int) -> tuple[str, str, int]:
    """(continuação do título, parágrafo do corpo do banner, índice logo após a fence de fechamento)."""
    i = title_idx + 1
    cont: list[str] = []
    while i < hi and not _is_fence(lines[i]) and lines[i].startswith("#"):
        body = lines[i].rstrip("\n")[1:].strip()
        if not body:
            break
        cont.append(body)
        i += 1
    para: list[str] = []
    if i < hi and lines[i].rstrip("\n").strip() == "#":
        j = i
        while j < hi and not _is_fence(lines[j]) and lines[j].startswith("#"):
            body = lines[j].rstrip("\n")[1:].strip()
            if body:
                para.append(body)
            elif para:
                break
            j += 1
    k = title_idx + 1
    while k < hi and not _is_fence(lines[k]):
        k += 1
    return " ".join(cont), " ".join(para), k + 1


def _scalar_source(value) -> str:
    """Fonte (3): primeiro valor textual não vazio de SCALAR_KEYS num mapeamento."""
    if not isinstance(value, dict):
        return ""
    for name in SCALAR_KEYS:
        v = value.get(name)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def _section_summary(
    lines: list[str],
    title_idx: int,
    hi: int,
    first_key_value=None,
    override: str = "",
    tail: str = "",
) -> str:
    """Resumo pela cadeia de fontes 1 a 5 (RF02); "" se nenhuma."""
    _cont, body, after = _banner_parts(lines, title_idx, hi)
    para: list[str] = []
    i = after
    while i < hi:
        ln = lines[i].rstrip("\n")
        if not ln.startswith("#"):
            break
        text = ln[1:].strip()
        if not text:
            if para:
                break
        else:
            para.append(text)
        i += 1
    for source in (body, " ".join(para), _scalar_source(first_key_value), override, tail):
        summary = _sentence(source, SUMMARY_MAX) if source else ""
        if summary:
            return summary
    return ""


def parse_yaml_sections(text: str, overrides: dict[str, str] | None = None) -> list[Section]:
    overrides = overrides or {}
    lines = text.splitlines(keepends=True)
    banners: list[tuple[str, str, int]] = []  # (sid, title, índice 0-based da linha de título)
    for i, raw in enumerate(lines):
        m = re.match(BANNER_RE, raw.rstrip("\n"))
        if m and i > 0 and re.match(FENCE_RE, lines[i - 1].rstrip("\n")):
            banners.append((m.group(1), m.group(2).strip(), i))
    if not banners:
        raise SystemExit("workflow-rules.yaml sem seção numerada")

    def order_key(sid: str) -> tuple[int, str]:
        m2 = re.match(r"(\d+)([a-z]?)$", sid)
        return int(m2.group(1)), m2.group(2)

    seen: dict[str, int] = {}
    for n, (sid, _title, idx) in enumerate(banners):
        if sid in seen:
            raise SystemExit(f"workflow-rules.yaml: seção §{sid} duplicada nas linhas {seen[sid] + 1} e {idx + 1}")
        seen[sid] = idx
        if n > 0 and order_key(sid) <= order_key(banners[n - 1][0]):
            raise SystemExit(
                f"workflow-rules.yaml: ids fora de ordem crescente — §{banners[n - 1][0]} "
                f"(linha {banners[n - 1][2] + 1}) antes de §{sid} (linha {idx + 1})"
            )
    for sid in overrides:
        if sid not in seen:
            raise SystemExit(f"map_summaries: id §{sid} não existe no mapa")

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        data = None
    data = data if isinstance(data, dict) else {}

    # Faixas: cada seção começa na linha de fence que antecede o banner.
    starts = [0] + [idx - 1 for _sid, _t, idx in banners]
    starts.append(len(lines))
    heads = [("0", "preâmbulo", 0)] + banners
    sections: list[Section] = []
    for n, (sid, title, title_idx) in enumerate(heads):
        lo, hi = starts[n], starts[n + 1]
        chunk = lines[lo:hi]
        keys = tuple(m.group(1) for ln in chunk if (m := re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):", ln)))
        if sid == "0":
            summary = "Cabeçalho e bloco `framework:` (versão e changelog)"
        else:
            cont, _body, _after = _banner_parts(lines, title_idx, hi)
            raw = f"{title} {cont}".strip()
            title = _clean_title(raw)
            tail = " — ".join(" ".join(raw.split()).split(" — ")[1:])
            first_value = data.get(keys[0]) if keys else None
            summary = (
                _section_summary(lines, title_idx, hi, first_value, overrides.get(sid, ""), tail) or title
            )
        sections.append(
            Section(
                sid=sid,
                title=title,
                keys=keys,
                start=title_idx + 1 if sid != "0" else 1,
                end=hi,
                nbytes=sum(_nbytes(ln) for ln in chunk),
                summary=summary,
            )
        )
    return sections


def load_map_summaries(path: Path) -> dict[str, str]:
    """`map_summaries` opcional de kit-index.yaml: id de seção -> frase (RF04)."""
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = data.get("map_summaries") if isinstance(data, dict) else None
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise SystemExit(f"{path}: `map_summaries` deve ser um mapeamento de id de seção para frase")
    out: dict[str, str] = {}
    for sid, value in raw.items():
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"{path}: map_summaries §{sid} tem valor vazio ou não textual")
        out[str(sid)] = value
    return out


def _section_row(sec: Section, max_bytes: int) -> str:
    """Linha do mapa, encurtada até caber em `max_bytes`: chaves, Resumo (piso 30), título (piso 20)."""
    keys = list(sec.keys)
    shown = len(keys)
    base_title = _cell(sec.title).rstrip("…")
    base_summary = _cell(sec.summary).rstrip("…")
    title = _cell(sec.title)
    summary = _cell(sec.summary)

    def render() -> str:
        if not keys:
            ks = "(nenhuma)"
        else:
            ks = ", ".join(f"`{k}`" for k in keys[:shown])
            if shown < len(keys):
                ks += f" +{len(keys) - shown}"
        return f"| §{sec.sid} | {title} | {ks} | {sec.start}-{sec.end} | {sec.nbytes} | {summary} |"

    row = render()
    while _nbytes(row) > max_bytes and shown > 1:
        shown -= 1
        row = render()
    limit = len(summary)
    while _nbytes(row) > max_bytes and limit > SUMMARY_MIN:
        limit = max(SUMMARY_MIN, limit - 6)
        summary = _cut_words(base_summary, limit)
        row = render()
    limit = len(title)
    while _nbytes(row) > max_bytes and limit > TITLE_MIN:
        limit = max(TITLE_MIN, limit - 6)
        title = _cut_words(base_title, limit)
        row = render()
    return row


def _largest_section_bytes(sections: list[Section]) -> int:
    return max((s.nbytes for s in sections if s.sid not in LARGEST_SECTION_EXCLUDES), default=0)


def build_section_map(yaml_path: Path, overrides: dict[str, str] | None = None) -> str:
    text = yaml_path.read_text(encoding="utf-8")
    sections = parse_yaml_sections(text, overrides)
    yaml_bytes = _nbytes(text)
    largest = _largest_section_bytes(sections)
    rows = [_section_row(s, CEILINGS["map_row"]) for s in sections]

    def render(measured: int) -> str:
        pct = measured / yaml_bytes * 100
        head = [
            "# Mapa de seções do workflow-rules.yaml",
            "",
            "Gerado por `render_indexes.py` — não edite à mão. Ids `§N` = numeração dos banners do YAML.",
            f"YAML: {yaml_bytes} bytes; mapa + maior seção: {measured} ({pct:.1f}% de 15%)",
            f"Total: {len(sections)} seções",
            "",
            "| § | Seção | Chaves | Linhas | Bytes | Resumo |",
            "|---|---|---|---|---|---|",
        ]
        return "\n".join(head + rows) + "\n"

    measured = 0
    out = render(measured)
    for _ in range(10):  # ponto fixo: o tamanho do mapa aparece no próprio mapa
        new = _nbytes(out) + largest
        if new == measured:
            break
        measured = new
        out = render(measured)
    return out


def check_map_ceiling(sections: list[Section], map_text: str, yaml_bytes: int) -> list[str]:
    problems: list[str] = []
    limit = int(MAP_FRACTION * yaml_bytes)
    measured = _nbytes(map_text) + _largest_section_bytes(sections)
    if measured > limit:
        problems.append(f"mapa: mapa + maior seção = {measured} bytes, teto {limit}")
    header = map_text.split("\n| §", 1)[0]
    if _nbytes(header) > CEILINGS["map_header"]:
        problems.append(f"mapa: cabeçalho = {_nbytes(header)} bytes, teto {CEILINGS['map_header']}")
    for row in _table_rows(map_text):
        if _nbytes(row) > CEILINGS["map_row"]:
            problems.append(f"mapa: linha = {_nbytes(row)} bytes, teto {CEILINGS['map_row']}: {row[:40]}…")
    return problems


def check_section_refs(root: Path, sections: list[Section]) -> list[str]:
    """RF05: todo `§id` citado em .md sob `root` (exceto mapa e INDEX.md) existe no mapa."""
    valid = {s.sid for s in sections}
    skip = {root / MAP_REL, root / "INDEX.md"}
    problems: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if path in skip or IGNORED_DIRS & set(path.parts):
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for m in re.finditer(r"§(\d+[a-z]?)", line):
                if m.group(1) not in valid:
                    problems.append(f"{path.relative_to(root).as_posix()}:{n}: §{m.group(1)} não existe no mapa")
    return problems


# ---------------------------------------------------------------------------
# Índice do kit (RF01, RF02)
# ---------------------------------------------------------------------------


def load_kit_manifest(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"manifesto ausente: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SystemExit(f"{path}: chave `entries` ausente ou vazia")
    for i, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict) or set(entry) != {"path", "what", "when"}:
            raise SystemExit(f"{path}: entrada {i} deve ter exatamente as chaves path, what e when")
        for key in ("path", "what", "when"):
            if not isinstance(entry[key], str) or not entry[key].strip():
                raise SystemExit(f"{path}: entrada {i} tem `{key}` vazio ou não textual")
    return entries


def _glob_re(pattern: str) -> re.Pattern:
    out = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + r"\Z")


def list_kit_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if not p.is_file() or IGNORED_DIRS & set(rel.parts) or p.suffix == ".pyc" or rel.as_posix() == "INDEX.md":
            continue
        files.append(p)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def _bucket(size: int) -> str:
    for limit, label in SIZE_BUCKETS:
        if limit is None or size < limit:
            return label
    return SIZE_BUCKETS[-1][1]


def _expand(text: str, name: str) -> str:
    """Só `{name}` (com extensão) e `{stem}` (sem extensão) são substituídos (RF05)."""
    return text.replace("{name}", name).replace("{stem}", Path(name).stem)


def build_kit_index(root: Path, manifest: list[dict]) -> str:
    files = list_kit_files(root)
    patterns = [(_glob_re(e["path"]), e) for e in manifest]
    used = [False] * len(patterns)
    rows: list[str] = []
    problems: list[str] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        hit = None
        for n, (rx, entry) in enumerate(patterns):
            if rx.match(rel):
                used[n] = True
                if hit is None:
                    hit = entry
        if hit is None:
            problems.append(f"arquivo sem entrada em kit-index.yaml: {rel}")
            continue
        what = _expand(hit["what"], f.name)
        when = _expand(hit["when"], f.name)
        rows.append(f"| `{rel}` | {_cell(what)} | {_cell(when)} | {_bucket(f.stat().st_size)} |")
    for n, (_rx, entry) in enumerate(patterns):
        if not used[n]:
            problems.append(f"entrada de kit-index.yaml sem arquivo: {entry['path']}")
    if problems:
        raise CoverageError(problems)
    head = [
        "# Índice do kit",
        "",
        "Gerado por `render_indexes.py` — não edite à mão. Fonte: `rules/kit-index.yaml`.",
        f"Total: {len(files)} arquivos",
        "",
        "| Caminho (relativo a `_framework/`) | O que é | Quando ler | Tamanho |",
        "|---|---|---|---|",
    ]
    return "\n".join(head + rows) + "\n"


def check_kit_ceiling(text: str) -> list[str]:
    problems: list[str] = []
    if _nbytes(text) > CEILINGS["kit_index_total"]:
        problems.append(f"INDEX.md: {_nbytes(text)} bytes, teto {CEILINGS['kit_index_total']}")
    for row in _table_rows(text):
        if _nbytes(row) > CEILINGS["kit_index_row"]:
            problems.append(f"INDEX.md: linha = {_nbytes(row)} bytes, teto {CEILINGS['kit_index_row']}: {row[:50]}…")
    return problems


# ---------------------------------------------------------------------------
# Índice de SDDs (RF06, RF07)
# ---------------------------------------------------------------------------


def _paths_in(text: str) -> list[str]:
    out = []
    for tok in re.findall(r"`([^`\s]+)`", text):
        if "/" in tok or re.search(r"\.[A-Za-z0-9]+$", tok):
            out.append(tok)
    return out


def _section_body(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    out: list[str] = []
    inside = False
    for ln in lines:
        if ln.startswith("## "):
            if inside:
                break
            inside = ln[3:].strip() == heading
            continue
        if inside:
            out.append(ln)
    return out


def extract_sdd_files(body: str) -> list[str]:
    found: set[str] = set()
    # (a) bloco em prosa dentro da especificação técnica
    spec = _section_body(body, "Especificação técnica consolidada")
    i = 0
    while i < len(spec):
        if re.match(r"^\**\s*Arquivos (tocados|a alterar)", spec[i]):
            found.update(_paths_in(spec[i]))
            i += 1
            while i < len(spec):
                ln = spec[i]
                if not ln.strip() or re.match(r"^\s*([-*]\s|\s+\S)", ln):
                    found.update(_paths_in(ln))
                    i += 1
                else:
                    break
            continue
        i += 1
    # (b) coluna "Arquivos tocados" da tabela de tasks
    col = None
    for ln in _section_body(body, "Decomposição em tasks"):
        if not ln.startswith("|"):
            continue
        cells = split_table_row(ln.strip())
        if col is None:
            if "Arquivos tocados" in cells:
                col = cells.index("Arquivos tocados")
            continue
        if col < len(cells):
            found.update(_paths_in(cells[col]))
    return sorted(found)


def _sdd_summary(body: str, title: str) -> str:
    para: list[str] = []
    for ln in _section_body(body, "Resumo executivo"):
        s = ln.strip()
        if not s or s.startswith(">"):
            if para:
                break
            continue
        para.append(s)
    if not para:
        return title
    return _first_sentence(" ".join(para), SDD_SUMMARY_MAX)


def _link(value) -> str:
    if not value:
        return "—"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value) or "—"
    return str(value)


def _sdd_row(sid: str, summary: str, files: list[str], fm: dict) -> str:
    """Linha do índice, encurtada (arquivos primeiro, depois resumo) até caber no teto."""
    shown = min(len(files), SDD_MAX_FILES)

    def render() -> str:
        if not files:
            cell = NO_FILES
        else:
            cell = ", ".join(f"`{f}`" for f in files[:shown])
            if shown < len(files):
                cell += f" +{len(files) - shown}"
        return (
            f"| `{sid}` | {summary} | {cell} | {_link(fm.get('supersedes'))} "
            f"| {_link(fm.get('superseded_by'))} | {fm.get('status', '')} |"
        )

    row = render()
    while _nbytes(row) > CEILINGS["sdd_row"] and shown > 1:
        shown -= 1
        row = render()
    while _nbytes(row) > CEILINGS["sdd_row"] and len(summary) > 20:
        summary = summary[: len(summary) - 6].rstrip() + "…"
        row = render()
    return row


def build_sdd_index(sdd_dir: Path) -> str:
    entries = []
    missing: list[str] = []
    for path in sorted(p for p in sdd_dir.iterdir() if p.is_file() and SDD_NAME_RE.match(p.name)):
        try:
            fm, body = read_frontmatter(path)
        except ValueError as exc:
            raise SystemExit(f"{path}: front-matter inválido — {exc}") from exc
        if not fm.get("id"):
            raise SystemExit(f"{path}: SDD sem front-matter válido ou sem `id`")
        files = extract_sdd_files(body)
        if not files:
            missing.append(str(fm["id"]))
        summary = _cell(_sdd_summary(body, str(fm.get("title", ""))))
        entries.append((str(fm["id"]), summary, files, fm))
    entries.sort(key=lambda e: e[0])
    if missing:
        print(f"⚠️ {len(missing)} SDD(s) sem seção de arquivos: {', '.join(sorted(missing))}")
    rows = [_sdd_row(sid, summary, files, fm) for sid, summary, files, fm in entries]
    head = [
        "# Índice de SDDs",
        "",
        "Gerado por `render_indexes.py sdd` — não edite à mão.",
        f"Total: {len(entries)} SDDs",
        "",
        "| ID | Resumo | Arquivos de código | Substitui | Substituída por | Status |",
        "|---|---|---|---|---|---|",
    ]
    return "\n".join(head + rows) + "\n"


def check_sdd_ceiling(text: str, count: int) -> list[str]:
    problems: list[str] = []
    total_limit = CEILINGS["sdd_base"] + CEILINGS["sdd_row"] * count
    if _nbytes(text) > total_limit:
        problems.append(f"docs/sdd/INDEX.md: {_nbytes(text)} bytes, teto {total_limit}")
    for row in _table_rows(text):
        if _nbytes(row) > CEILINGS["sdd_row"]:
            problems.append(f"docs/sdd/INDEX.md: linha = {_nbytes(row)} bytes, teto {CEILINGS['sdd_row']}: {row[:50]}…")
    return problems


# ---------------------------------------------------------------------------
# Sumário (RF09)
# ---------------------------------------------------------------------------


def _anchor(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"\s", "-", slug.strip())


def _iter_headings(markdown: str):
    """(índice de linha, linha) dos títulos `##` fora de bloco cercado."""
    fenced = False
    for i, ln in enumerate(markdown.splitlines()):
        if re.match(r"^\s*(```|~~~)", ln):
            fenced = not fenced
            continue
        if not fenced and ln.startswith("## "):
            yield i, ln


def build_toc(markdown: str) -> str:
    lines = markdown.splitlines(keepends=True)
    heads = list(_iter_headings(markdown))
    counts: dict[str, int] = {}
    items = ["**Sumário**", ""]
    for n, (idx, ln) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        size = sum(_nbytes(x) for x in lines[idx:end])
        title = ln[3:].strip()
        anchor = _anchor(title)
        seen = counts.get(anchor, 0)
        counts[anchor] = seen + 1
        if seen:
            anchor = f"{anchor}-{seen}"
        items.append(f"- [{title}](#{anchor}) — {size} bytes")
    return "\n".join(items)


def has_toc_markers(text: str) -> bool:
    return TOC_BEGIN in text and TOC_END in text.split(TOC_BEGIN, 1)[1]


def inject_toc(text: str, toc: str) -> str:
    block = f"{TOC_BEGIN}\n{toc}\n{TOC_END}"
    if has_toc_markers(text):
        head, rest = text.split(TOC_BEGIN, 1)
        tail = rest.split(TOC_END, 1)[1]
        return head + block + tail
    lines = text.splitlines(keepends=True)
    fenced = False
    for i, ln in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", ln):
            fenced = not fenced
        elif not fenced and ln.startswith("# "):
            return "".join(lines[: i + 1]) + "\n" + block + "\n" + "".join(lines[i + 1 :])
    return block + "\n\n" + text


def _toc_of(text: str) -> str:
    if not has_toc_markers(text):
        return ""
    return text.split(TOC_BEGIN, 1)[1].split(TOC_END, 1)[0]


def check_toc_ceiling(label: str, text: str) -> list[str]:
    size = _nbytes(_toc_of(text))
    if size > CEILINGS["toc_total"]:
        return [f"sumário de {label}: {size} bytes, teto {CEILINGS['toc_total']}"]
    return []


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def _report(problems: list[str]) -> bool:
    for p in problems:
        print(f"❌ {p}")
    return not problems


def _generate_sdd(sdd_dir: Path, check: bool, label: str) -> bool:
    text = build_sdd_index(sdd_dir)
    count = int(re.search(r"^Total: (\d+) SDDs$", text, re.M).group(1))
    if not _report(check_sdd_ceiling(text, count)):
        return False
    return _emit(sdd_dir / "INDEX.md", label, text, check)


def generate_all(root: Path, rules: dict, check: bool) -> bool:
    """Gera (ou confere) os índices do kit. `root` é a pasta `_framework`."""
    ok = True
    repo = root.parent
    yaml_path = root / "rules/workflow-rules.yaml"
    yaml_text = yaml_path.read_text(encoding="utf-8")
    overrides = load_map_summaries(root / "rules/kit-index.yaml")
    sections = parse_yaml_sections(yaml_text, overrides)

    # 1. sumário do guia técnico (marcadores obrigatórios em --check)
    guide = repo / GUIDE_REL
    if guide.is_file():
        current = guide.read_text(encoding="utf-8")
        if check and not has_toc_markers(current):
            print(f"❌ {GUIDE_REL}: marcador ausente — rode render_indexes.py.")
            ok = False
        else:
            new = inject_toc(current, build_toc(current))
            ok &= _report(check_toc_ceiling("guia-tecnico.md", new))
            ok &= _emit(guide, GUIDE_REL, new, check)
    universal = root / "prompts/universal.md"
    if universal.is_file():
        ok &= _report(check_toc_ceiling("universal.md", universal.read_text(encoding="utf-8")))

    # 2. mapa de seções
    map_text = build_section_map(yaml_path, overrides)
    map_problems = check_map_ceiling(sections, map_text, _nbytes(yaml_text))
    ok &= _report(map_problems)
    if not map_problems:
        ok &= _emit(root / MAP_REL, f"_framework/{MAP_REL}", map_text, check)
    measured = _nbytes(map_text) + _largest_section_bytes(sections)
    print(f"mapa+maior seção = {measured} ({measured / _nbytes(yaml_text) * 100:.1f}% do YAML)")
    ok &= _report(check_section_refs(root, sections))

    # 3. índice do kit
    try:
        kit_text = build_kit_index(root, load_kit_manifest(root / "rules/kit-index.yaml"))
    except CoverageError as exc:
        if not check:
            raise SystemExit("\n".join(exc.problems + ["kit-index.yaml não cobre o kit"])) from exc
        ok &= _report(exc.problems)
    else:
        kit_problems = check_kit_ceiling(kit_text)
        ok &= _report(kit_problems)
        if not kit_problems:
            ok &= _emit(root / "INDEX.md", "_framework/INDEX.md", kit_text, check)

    # 4. índice de SDDs do próprio repositório (só onde há docs/sdd)
    sdd_dir = repo / "docs/sdd"
    if sdd_dir.is_dir():
        ok &= _generate_sdd(sdd_dir, check, "docs/sdd/INDEX.md")
    return ok


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check = "--check" in args
    args = [a for a in args if a != "--check"]
    try:
        if args and args[0] == "sdd":
            if len(args) != 2:
                raise SystemExit("uso: render_indexes.py sdd <dir> [--check]")
            sdd_dir = Path(args[1])
            if not sdd_dir.is_dir():
                raise SystemExit(f"diretório inexistente: {sdd_dir}")
            return 0 if _generate_sdd(sdd_dir, check, f"{sdd_dir}/INDEX.md") else 1
        if args and args[0] == "--root":
            root = Path(args[1]).resolve()
        else:
            rules_file = find_rules_file()
            if not rules_file:
                raise SystemExit("workflow-rules.yaml não encontrado.")
            root = rules_file.parent.parent
        return 0 if generate_all(root, {}, check) else 1
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
