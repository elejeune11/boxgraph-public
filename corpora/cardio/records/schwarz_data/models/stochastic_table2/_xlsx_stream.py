# Our own streaming reader for the large released .xlsx workbooks (Office Open XML): the numeric
# columns of a sheet, row by row with iterparse, so a sheet of 200,000 rows is never held as XML.
# No spreadsheet library is needed; nothing of the workbooks is copied.
import os
import pathlib
import re
import zipfile
from xml.etree import ElementTree as ET

import numpy as np

_M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def source_file(name):
    return pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / name


class Book:
    def __init__(self, name):
        self.z = zipfile.ZipFile(source_file(name))
        wb = ET.fromstring(self.z.read("xl/workbook.xml"))
        rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(self.z.read("xl/_rels/workbook.xml.rels"))}
        self.targets = {}
        for s in wb.iter(_M + "sheet"):
            t = rels[s.get(_R + "id")].lstrip("/")
            self.targets[s.get("name")] = t if t.startswith("xl/") else "xl/" + t
        self.shared = []
        if "xl/sharedStrings.xml" in self.z.namelist():
            with self.z.open("xl/sharedStrings.xml") as f:
                for _, el in ET.iterparse(f):
                    if el.tag == _M + "si":
                        self.shared.append("".join(t.text or "" for t in el.iter(_M + "t")))
                        el.clear()

    def rows(self, sheet):
        """(row number, {column letters: value}) for each row; numbers as float, text as str."""
        with self.z.open(self.targets[sheet]) as f:
            for _, el in ET.iterparse(f):
                if el.tag != _M + "row":
                    continue
                r = {}
                for c in el.iter(_M + "c"):
                    kind, v = c.get("t"), c.find(_M + "v")
                    if kind == "inlineStr":
                        val = "".join(t.text or "" for t in c.iter(_M + "t"))
                    elif v is None:
                        continue
                    elif kind == "s":
                        val = self.shared[int(v.text)]
                    elif kind in ("str", "e"):
                        val = v.text
                    else:
                        val = float(v.text)
                    r[re.match(r"[A-Z]+", c.get("r")).group(0)] = val
                yield int(el.get("r")), r
                el.clear()

    def cells(self, sheet):
        """{(column letters, row): value} of a small sheet."""
        return {(k, rn): v for rn, r in self.rows(sheet) for k, v in r.items()}

    def columns(self, sheet, first_row=2):
        """{column letters: numbers from first_row down} (text cells skipped). A column is a list in row
        order; ragged columns (one per class) simply end."""
        out = {}
        for rn, r in self.rows(sheet):
            if rn < first_row:
                continue
            for k, v in r.items():
                if isinstance(v, float):
                    out.setdefault(k, []).append(v)
        return {k: np.array(v) for k, v in out.items()}

    def column_rows(self, sheet, letter, first_row=2):
        """(row numbers, numbers) of one column, for reading values at given rows."""
        rows, vals = [], []
        for rn, r in self.rows(sheet):
            if rn >= first_row and isinstance(r.get(letter), float):
                rows.append(rn)
                vals.append(r[letter])
        return np.array(rows), np.array(vals)


def percentile(v, p, method):
    v = np.sort(np.asarray(v, float))
    if method == "linear":
        return float(np.percentile(v, p))
    if method == "matlab":   # Matlab prctile: the k-th of n sorted values at the (k - 0.5)/n quantile
        n = len(v)
        return float(np.interp(p / 100.0 * n, np.arange(1, n + 1) - 0.5, v))
    raise ValueError(f"unknown percentile method {method!r}")
