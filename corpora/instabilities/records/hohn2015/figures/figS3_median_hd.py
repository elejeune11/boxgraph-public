"""Fig. S3 (PDF p. 7) at high resolution: the short black horizontal line, the median surface-area
decrease (caption: "the median surface area decrease is approx 10%").

Calibration as in _figS3.py. At high resolution the markers drawn over the line break it into
short pieces, so the line's rows are found by the number of neutral dark pixels inside the box
(between 25% and 80% of the box width: the zero line is full width, marker outlines are few
pixels), not by one unbroken run. The value is the middle of the largest group of such rows,
+-(half its height + 0.5 px + calibration misfit). Returned at x = 5.5, the middle rank of ten
markers.
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
    inner = dark[:, c0 + 5:c1 - 5]
    rows = [r for r in range(r0 + 5, r1 - 5) if 0.25 * w <= inner[r].sum() <= 0.8 * w]
    if not rows:
        return [{"x": 5.5, "y": None, "note": "median line not found"}]
    g = max(m._groups(rows), key=len)
    cols = np.nonzero(inner[g[len(g) // 2]])[0]
    mid = float(np.mean(g)) + 0.5
    half = len(g) / 2 + 0.5 + cal["misfit"]
    a, b = m.value(cal, mid - half), m.value(cal, mid + half)
    return [{"x": 5.5, "y": m.value(cal, mid), "lo": min(a, b), "hi": max(a, b),
             "px": [float(c0 + 5 + np.median(cols)), mid], "px_lo": mid - half, "px_hi": mid + half,
             "note": f"line rows {g[0]}-{g[-1]}; calibration misfit {cal['misfit']:.2f} px"}]
