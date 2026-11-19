"""Fig. 3G (PDF p. 7): mean buckling pressure (Pa) per alginate concentration, four coloured dots
(green 1%, red 1.5%, blue 2%, orange 2.5%) with black SEM error bars.

Calibration (_cal.py): the x axis has ticks below it every 0.25 % from 0.5 % at the y axis (labels
1, 1.5, 2, 2.5 on every second tick); the y axis has ticks left of it every 20 Pa from 0 at the x
axis (labels 0, 40, 80, 120 on every second tick). Ticks are indexed from the axis crossing.
Dots: saturated (coloured) pixels opened with a disk of radius 10 px (a dot is about 45 px
across). Error bars: the black stem through the dot's column, followed to its last ink row each
way. Interval on a dot: 4 px on its centre plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)


def read(image, at):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    xa = C.calibrate_from(xo, C.ticks_x(L), 0.5, 0.25)
    ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, 20.0)
    col = C.saturated(image)
    col[L["xr0"] - 2:, :] = False
    col[:, :L["yc1"] + 2] = False
    m = L["mask"]
    out = []
    for c, r, area in sorted(C.blobs(col, 10, min_area=300)):
        rad = np.sqrt(area / np.pi)
        top = C.stem_end(m, c, r - rad, -1, gap=8)   # the dot's soft rim is not ink: bridge it
        bot = C.stem_end(m, c, r + rad, +1, gap=8)
        rgb = image[int(r), int(c)]
        out.append(C.point(xa, ya, c, r, 4, 4, bar=(top, bot), bar_px=3.0,
                           note=f"dot colour {tuple(int(v) for v in rgb)}; bar rows {top}-{bot}"))
    return out
