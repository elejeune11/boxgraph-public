"""Fig. 1F (PDF p. 3): mean cell number per capsule against time, black dots with SD error bars.

Calibration (_cal.py): ticks indexed from the axis crossing (stray marks that are not a whole
number of tick spacings away are dropped): x ticks below the axis every 5 h from 0 at the y axis
(labels 0, 10, ..., 50 on every second tick); y ticks left of the axis every 25 from 100 at the x
axis (labels 100, 150, ..., 450 on every second tick). Dots: the ink opened with a disk of radius 12 px (the bars, line and
ticks are about 4-6 px wide; a dot is about 40 px across). Error bars: the stem through the dot's
column is followed up and down to its last ink row (the cap). The first dot (t = 0) sits on the y
axis and is half hidden by it, so its centre is less certain and its bar cannot be told from the
axis: it is read without a bar. The last dot sits on the right end of the axis box.
Interval on a dot: 4 px on its centre (the raster is soft), 8 px on the half-hidden first one.
"""
import numpy as np

import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)


def read(image, at):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    xa = C.calibrate_from(xo, C.ticks_x(L), 0.0, 5.0)
    ya = C.calibrate_from(yo, C.ticks_y(L), 100.0, 25.0)
    m = L["mask"].copy()
    inner = m.copy()
    inner[L["xr0"] - 2:, :] = False
    bl = C.blobs(inner, 12, min_area=400)
    out = []
    for col, row, area in sorted(bl):
        if row > L["xr0"] - 5 or col < L["yc0"] - 30:
            continue                    # outside the axes (the panel letter)
        on_axis = col < L["yc1"] + 25
        if on_axis:
            out.append(C.point(xa, ya, col, row, 8, 8, note="dot on the y axis, half hidden; bar hidden"))
            continue
        # the blob's extent: a dot cut by the right edge of the plot (t = 55 h) is half a disk,
        # whose centre is on the cut, where its error bar stem also runs
        rr, cc = np.where(m[int(row) - 30:int(row) + 31, int(col) - 30:int(col) + 31])
        h = rr.max() - rr.min() if len(rr) else 0
        w_right = int(col) - 30 + max(c for r, c in zip(rr, cc) if abs(r - 30) < 6)
        rad = np.sqrt(area / np.pi)
        note = ""
        if area < 0.75 * np.pi * (h / 2) ** 2 and col > L["xext"][1] - 60:
            col = float(w_right)
            rad = h / 2
            note = "dot cut in half by the right edge of the plot: centre on the cut; "
        top = C.stem_end(m, col, row - rad, -1)
        bot = C.stem_end(m, col, row + rad, +1)
        out.append(C.point(xa, ya, col, row, 4, 4, bar=(top, bot), bar_px=3.0,
                           note=note + f"bar rows {top}-{bot}"))
    return out
