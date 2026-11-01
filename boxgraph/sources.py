"""Sources that are not paged documents: code (a folder of files) and data (a spreadsheet).

Neither is committed: like a PDF, it lives under the project's ignored `corpus/`, and the
record pins it by a digest of its contents (`version: sha256:...`), so a build can tell when
it is not the code or data that was read.
"""

from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SKIP = {"__MACOSX", ".git", "__pycache__", ".DS_Store"}


def tree_digest(path: Path) -> str:
    """'sha256:<hex>' over a file's bytes, or over every file of a folder (sorted relative
    path and bytes; hidden files, __MACOSX and caches left out)."""
    path = Path(path)
    h = hashlib.sha256()
    if path.is_file():
        h.update(path.read_bytes())
    else:
        for f in sorted(p for p in path.rglob("*") if p.is_file()):
            rel = f.relative_to(path)
            if any(part in SKIP or part.startswith(".") for part in rel.parts):
                continue
            h.update(rel.as_posix().encode() + b"\0" + f.read_bytes() + b"\0")
    return "sha256:" + h.hexdigest()


def code_lines(folder: Path, file: str, lines: str) -> str | None:
    """The text of lines 'a' or 'a-b' (1-based) of a file in a code folder, or None if they do not exist."""
    f = Path(folder) / file
    if not f.is_file():
        return None
    m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", str(lines))
    if not m:
        return None
    a = int(m.group(1))
    b = int(m.group(2) or a)
    text = f.read_text(errors="replace").splitlines()
    if not (1 <= a <= b <= len(text)):
        return None
    return "\n".join(text[a - 1:b])


# ---- spreadsheets ---------------------------------------------------------------

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
       "p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def _col(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def _split(ref: str) -> tuple[int, int]:
    m = re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", ref.strip().upper())
    if not m:
        raise ValueError(f"not a cell reference: {ref!r}")
    return _col(m.group(1)), int(m.group(2))


def read_cells(path: Path, sheet: str, ref: str) -> list:
    """The values of one cell ('B2') or of one row or column range ('B2:B8', 'A1:D1') of a named
    sheet of an .xlsx file: numbers as numbers, text as text, empty cells as None."""
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rid = None
        for s in wb.iter(f"{{{_NS['m']}}}sheet"):
            if s.get("name") == sheet:
                rid = s.get(f"{{{_NS['r']}}}id")
        if rid is None:
            raise KeyError(f"no sheet {sheet!r}")
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = next(r.get("Target") for r in rels if r.get("Id") == rid)
        target = target.lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(f"{{{_NS['m']}}}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
        cells = {}
        for c in ET.fromstring(z.read(target)).iter(f"{{{_NS['m']}}}c"):
            kind, v = c.get("t"), c.find(f"{{{_NS['m']}}}v")
            if kind == "inlineStr":
                val = "".join(t.text or "" for t in c.iter(f"{{{_NS['m']}}}t"))
            elif v is None:
                val = None
            elif kind == "s":
                val = shared[int(v.text)]
            elif kind in ("str", "e"):
                val = v.text
            elif kind == "b":
                val = v.text == "1"
            else:
                f = float(v.text)
                val = int(f) if f.is_integer() and "." not in v.text and "e" not in v.text.lower() else f
            cells[_split(c.get("r"))] = val
    a, _, b = ref.partition(":")
    (c0, r0), (c1, r1) = _split(a), _split(b or a)
    if c0 != c1 and r0 != r1:
        raise ValueError(f"{ref!r} is not a single row or column")
    return [cells.get((c, r)) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)]
