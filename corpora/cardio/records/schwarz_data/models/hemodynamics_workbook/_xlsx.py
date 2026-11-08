# Our own reader for the released .xlsx workbooks (Office Open XML): the cells of one sheet, numbers as
# floats, text as str. No spreadsheet library is needed; nothing of the workbooks is copied.
import os
import pathlib
import re
import zipfile
from xml.etree import ElementTree as ET

_M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def source_file(name):
    return pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / name


def _colnum(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def sheet(path, name):
    """{(column number, row number): value} of the named sheet."""
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rid = next(s.get(_R + "id") for s in wb.iter(_M + "sheet") if s.get("name") == name)
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = next(r.get("Target") for r in rels if r.get("Id") == rid).lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(_M + "si"):
                shared.append("".join(t.text or "" for t in si.iter(_M + "t")))
        cells = {}
        for c in ET.fromstring(z.read(target)).iter(_M + "c"):
            kind, v = c.get("t"), c.find(_M + "v")
            if kind == "inlineStr":
                val = "".join(t.text or "" for t in c.iter(_M + "t"))
            elif v is None:
                continue
            elif kind == "s":
                val = shared[int(v.text)]
            elif kind in ("str", "e"):
                val = v.text
            else:
                val = float(v.text)
            m = re.fullmatch(r"([A-Z]+)(\d+)", c.get("r"))
            cells[(_colnum(m.group(1)), int(m.group(2)))] = val
    return cells


def cell(cells, ref):
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    return cells.get((_colnum(m.group(1)), int(m.group(2))))


def column(cells, letter, first_row=2):
    """The numbers of one column from first_row down, None where a cell is empty or text, up to the
    last row that holds anything in column A."""
    c = _colnum(letter)
    last = max(r for (k, r) in cells if k == 1)
    out = []
    for r in range(first_row, last + 1):
        v = cells.get((c, r))
        out.append(v if isinstance(v, float) else None)
    return out
