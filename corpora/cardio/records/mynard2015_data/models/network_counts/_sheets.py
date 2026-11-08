# Our own reader for the two released supplemental workbooks of mynard2015 (Office Open XML), shared by the
# adapters of this record. No spreadsheet library is needed and nothing of the workbooks is copied: the
# adapters read the cells from $BOXGRAPH_SOURCE every time they run.
#
#   MOESM1_1D_segments.xlsx, sheet '1D segments': header row 7 (B 'Segment Name', C 'Segment Abbreviation',
#     D 'Length' (cm), E 'Inlet A0' (cm2), F 'Outlet A0' (cm2), G 'Inlet connects To', H 'Outlet connects to');
#     a block title (text in column A, e.g. 'Systemic Arteries') above each block; one row per segment with
#     its number in column A.
#   MOESM2_vascular_beds.xlsx, sheet 'Sheet1': header row 7 (B 'Bed Name', C 'Abbreviated Name',
#     D 'Resistance' (mmHg.s/mL), E 'Arterial Compliance' (mL/mmHg), F 'Venous Compliance' (mL/mmHg));
#     block titles in column A ('Systemic Vascular Beds', 'Coronary Vascular Beds', 'Pulmonary Vascular
#     Beds ...'); one row per bed with its number in column A, except the row 'Liver (arterial)', which has
#     no number and belongs to the liver above it.
import math
import os
import pathlib
import re
import zipfile
from xml.etree import ElementTree as ET

_M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

SEGMENTS = ("MOESM1_1D_segments.xlsx", "1D segments")
BEDS = ("MOESM2_vascular_beds.xlsx", "Sheet1")


def _colnum(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def sheet(file, name):
    """{(column number, row number): value} of a named sheet; numbers as floats, text as str."""
    path = pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / file
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


def _blocks(cells, first_row, cols):
    """Rows below first_row, each as {'row', 'block', column letter: value}: a row with text in column A
    starts a block; a row with a number in column A, or with a name in column B (an unnumbered sub-row),
    is a member of the current block."""
    last = max(r for (_, r) in cells)
    block, out = None, []
    for r in range(first_row, last + 1):
        a = cells.get((1, r))
        if isinstance(a, str):
            block = a.strip()
            continue
        if a is None and cells.get((2, r)) is None:
            continue
        row = {"row": r, "block": block}
        for i, k in enumerate(cols, 1):
            row[k] = cells.get((i, r))
        out.append(row)
    return out


def segments():
    """The 1D segments, in sheet order."""
    return [s for s in _blocks(sheet(*SEGMENTS), 9, "ABCDEFGH") if isinstance(s["A"], float)]


def beds():
    """The vascular beds, in sheet order (the unnumbered 'Liver (arterial)' row included)."""
    return _blocks(sheet(*BEDS), 9, "ABCDEF")


def names(text):
    """The comma-separated names of a connectivity cell."""
    return [t.strip() for t in (text or "").split(",") if t.strip()]


def multiplicity(segment):
    """N of a name ending in '[xN]' (Note 2 of the sheet: N identical vessels), else 1."""
    m = re.search(r"\[x(\d+)\]", segment["B"] or "")
    return int(m.group(1)) if m else 1


def diameter(area):
    """Diameter (cm) of a circular lumen of area A0 (cm2)."""
    return 2.0 * math.sqrt(area / math.pi)
