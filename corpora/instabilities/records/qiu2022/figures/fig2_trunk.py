"""Fig. 2 (PDF p. 4), panels (a) and (b): the shared low-curvature trunk where all ten lines
(five pressures, solid and dashed) lie on top of one another.

Calibration as in _fig2.py (find_axes, ticks matched to the printed labels, misfit added).
The band is found in the union of the five curve colours: in the columns c-3..c+3 the runs of
coloured ink are merged (gaps of at most 4 px), and the reading is accepted only when they form one
connected band (all lines touch). The value is the band's middle and its 95% interval the whole
band (it covers the spread between the pressures drawn there) plus the calibration misfit. The
same code serves both panels; the at-values pick the labels (panel (b)'s x axis ends at 0.3).
"""
import importlib.util
from pathlib import Path

import numpy as np


def _mod():
    spec = importlib.util.spec_from_file_location("qiu2022_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    m = _mod()
    panel = "b" if at and max(at) <= 0.3 else "a"
    spec = dict(m.LABELS[panel])
    xa, ya, box = m.calibrate(image, spec)
    mask = np.zeros(image.shape[:2], bool)
    for name in m.ORDER:
        mask |= m.color_mask(image, name, box)
    mis_y = max(ya.residual_px, 0.5)
    out = []
    for x in at:
        c = int(round(xa.to_pixel(x)))
        runs = []
        for cc in range(c - 3, c + 4):
            runs += m._runs(mask[:, cc])
        if not runs:
            out.append({"x": x, "y": None, "note": "no coloured ink"})
            continue
        runs.sort()
        joined = [list(runs[0])]
        for s0, e0 in runs[1:]:
            if s0 <= joined[-1][1] + 4:
                joined[-1][1] = max(joined[-1][1], e0)
            else:
                joined.append([s0, e0])
        if len(joined) != 1:
            out.append({"x": x, "y": None, "note": f"{len(joined)} separate bands: lines separate here"})
            continue
        top, bot = joined[0]
        row = (top + bot) / 2
        half = (bot - top) / 2 + mis_y
        y, lo, hi = ya.to_value(row), ya.to_value(row + half), ya.to_value(row - half)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, row],
                    "px_lo": row - half, "px_hi": row + half,
                    "note": f"one band of all colours, {bot - top + 1} px tall"})
    return out
