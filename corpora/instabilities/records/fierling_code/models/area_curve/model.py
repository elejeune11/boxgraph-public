# Reads a released tab-separated .gdat (first line: column names) from $BOXGRAPH_SOURCE and interpolates one column
# against the time column, as area_AP_DV_paper.plot plots it for Fig. 3a. Nothing of the data is copied into the record.
import math
import os
import pathlib

import numpy as np


def _table(name):
    lines = [l for l in (pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / name).read_text(errors="replace").splitlines()
             if l.strip() and not l.startswith("#")]
    header = lines[0].rstrip("\n").split("\t")
    rows = []
    for l in lines[1:]:
        parts = l.split("\t")
        vals = []
        for p in parts:
            try:
                vals.append(float(p))
            except ValueError:
                vals.append(math.nan)
        rows.append(vals)
    return header, rows


def run(inputs, settings):
    header, rows = _table(settings["file"])
    ti, yi = header.index(settings["t_column"]), header.index(settings["y_column"])
    need = settings.get("need_column") or ""
    ni = header.index(need) if need else None
    pts = []
    for r in rows:
        if max(ti, yi) >= len(r):
            continue
        if ni is not None and not (ni < len(r) and r[ni] >= float(settings["need_value"])):
            continue
        if math.isnan(r[ti]) or math.isnan(r[yi]):
            continue
        pts.append((r[ti], r[yi]))
    pts.sort()
    ts = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    t = inputs["t"]
    if t < ts[0] - 1e-9 or t > ts[-1] + 1e-9:
        raise ValueError(f"t = {t} min is outside the file's times {ts[0]}-{ts[-1]}")
    y = float(np.interp(t, ts, ys))
    return {"y": y, "reduction": 1 - y}
