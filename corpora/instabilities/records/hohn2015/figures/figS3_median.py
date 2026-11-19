"""Fig. S3 (PDF p. 7): the short black horizontal line, the median surface-area decrease (caption:
"the median surface area decrease is approx 10%"). Found as the rows inside the box whose neutral
dark run is between 25% and 80% of the box width (the zero line is full width; markers are short
and coloured). Its value is the middle of those rows, +-(half their height + 0.5 px + calibration
misfit). Returned at x = 5.5, the middle rank of ten markers, so it can sit beside figS3_points.
"""
import importlib.util
from pathlib import Path

import numpy as np


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_figS3", Path(__file__).with_name("_figS3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal = m.calibrate(image)
    c0, r0, c1, r1 = cal["box"]
    dark = (cal["hi"] < 140) & cal["neutral"]
    w = c1 - c0
    rows, cols = [], []
    for r in range(r0 + 1, r1 - 1):
        best, run, end = 0, 0, 0
        for c in range(c0 + 1, c1 - 1):
            run = run + 1 if dark[r, c] else 0
            if run > best:
                best, end = run, c
        if 0.25 * w <= best <= 0.8 * w:
            rows.append(r)
            cols.append(end - best / 2 + 0.5)
    if not rows:
        return [{"x": 5.5, "y": None, "note": "median line not found"}]
    g = m._groups(rows)
    g = max(g, key=len)
    mid = float(np.mean(g)) + 0.5
    half = len(g) / 2 + 0.5 + cal["misfit"]
    a, b = m.value(cal, mid - half), m.value(cal, mid + half)
    return [{"x": 5.5, "y": m.value(cal, mid), "lo": min(a, b), "hi": max(a, b),
             "px": [float(np.mean(cols)), mid], "px_lo": mid - half, "px_hi": mid + half,
             "note": f"line rows {g[0]}-{g[-1]}; calibration misfit {cal['misfit']:.2f} px"}]
