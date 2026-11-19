"""Fig. S1G (PDF p. 23): mean capsule radius (um) per alginate concentration (1, 1.5, 2, 2.5%),
the black horizontal line over each group of points (the caption calls the panel a box plot;
the line is read as drawn, its meaning is not stated). The coloured error bars run through the
point swarms of the same colour and their ends cannot be told from the points: not read. The
individual points (well over 50 per group, in touching rows) are not read.

Calibration (_cal.py): x ticks below the axis, one per group, matched to the labels 1, 1.5, 2,
2.5% (step 0.5 from the leftmost tick); y ticks left of the axis every 50 um from 0 at the x axis
(labels 0, 50, ..., 200 on every tick). Line: the rows of black ink within 45% of the tick
spacing of each group tick that hold black pixels over at least 8% of that window (the
points are coloured and lie partly over the line, so the line is broken; only the line is black
there). Interval: half the line's thickness plus 2 px
plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)


def read(image, at):
    L = C.axes_lines(image)
    yo = (L["xr0"] + L["xr1"]) / 2
    ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, 50.0)
    xt = sorted(t for t in C.ticks_x(L) if t > L["yc1"] + 10)   # the y axis runs past the x axis
    xa = C.calibrate(xt, 1.0, 0.5)
    sp = float(np.median(np.diff(xt)))
    m = C.ink(image, 200, 40)
    out = []
    for t in xt:
        a, b = int(t - 0.45 * sp), int(t + 0.45 * sp)
        sub = m[:L["xr0"] - 5, a:b]
        rows = [r for r in range(sub.shape[0]) if sub[r].sum() >= 0.08 * (b - a)]
        gs = C.groups(rows, gap=2)
        if len(gs) != 1:
            out.append({"x": xa.val(t), "y": None, "note": f"{len(gs)} black lines found"})
            continue
        g = gs[0]
        row, half = (g[0] + g[-1]) / 2, (g[-1] - g[0] + 1) / 2
        p = C.point(xa, ya, t, row, 2, half + 2, note=f"line rows {g[0]}-{g[-1]}")
        p["x"] = xa.val(t)
        out.append(p)
    return out
