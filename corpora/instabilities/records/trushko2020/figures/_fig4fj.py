"""Shared reading code for Fig. 4F and Fig. 4J (PDF p. 9).

Fig. 4F: fold depth delta (um, blue dots, left axis) and opening angle Phi (degrees, red dots,
right axis) of single folds against time (h); time 0 is monolayer confluence (legend). The
x axis is broken just right of its -5 h tick (a "//" on both frame lines); only the part from the
break on is linear, so only dots right of the break are read.
Calibration (_cal.py): the frame is a box; x ticks point up from the bottom frame line, and the
ticks right of the break are indexed from the tick labelled 0 (found as the fourth tick from the
right end of the axis, labelled 15, 10, 5, 0), every 2.5 h; the left axis ticks point right,
every 10 um from 0 at the bottom frame (labels 0, 20, ..., 100 on every second tick); the right
axis ticks point right (outwards), every 5 degrees from 0 (labels 0, 10, ..., 50 on every
second tick). Dots: pixels near the series colour opened with a disk of radius 6 px (a dot is
about 25 px across; the joining lines are thinner). Interval: 3 px on a dot's centre plus misfit.

Fig. 4J: spring constant (N/m) of 2.5% alginate capsules without (black dots) and with (red
dots) a monolayer, each dot at x = its rank: see _box.py.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)
_b = importlib.util.spec_from_file_location("trushko2020__box", Path(__file__).with_name("_box.py"))
B = importlib.util.module_from_spec(_b)
_b.loader.exec_module(B)

DOT4F = {"delta": (30, 100, 190), "phi": (225, 70, 25)}


def read_4f(image, which):
    L = C.axes_lines(image)
    m = L["mask"]
    H, W = m.shape
    # right frame line: longest ink column in the right half
    rcol = max(range(W // 2, W), key=lambda c: C.longest_run(m[:, c])[0])
    R = C.axes_lines(image, xrow=L["xr0"], ycol=rcol)
    yo = (L["xr0"] + L["xr1"]) / 2
    xt = sorted(C.ticks_x(L, side="out", depth=(3, 9), lim=(L["yc1"] + 5, R["yc0"] - 5)))
    # ticks right of the break: from the right end (the frame line is the 15 h position)
    right = (R["yc0"] + R["yc1"]) / 2
    p, idx = C.whole_spacings(float(right), [t for t in xt if t > L["yc1"] + 0.3 * (right - L["yc1"])])
    xa = C.Axis(p, [15.0 - 2.5 * i for i in idx])
    x_break = xa.pix(-5.0) + 10
    if which == "delta":
        ya = C.calibrate_from(yo, C.ticks_y(L, side="out", depth=(1, 4), lim=(0, L["xr0"] - 6)), 0.0, 10.0)
    else:
        ya = C.calibrate_from(yo, C.ticks_y(R, side="out", depth=(2, 10), lim=(0, L["xr0"] - 6), right=True),
                              0.0, 5.0)
    cm = C.colour(image, DOT4F[which], 70.0)
    cm[:, :int(x_break)] = False
    cm[:, R["yc0"] + 25:] = False
    out = []
    for c, r, area in sorted(C.blobs(cm, 6, min_area=150)):
        out.append(C.point(xa, ya, c, r, 3, 3, note=f"{which}; x ticks {len(xa.px)}, y ticks {len(ya.px)}"))
    return out


def read_4j(image, group):
    if group == "empty":
        return B.read_group(image, "4J", None, None, cols=(0.25, 0.53), open_radius=9, black=True)
    return B.read_group(image, "4J", (225, 35, 40), 70.0, cols=(0.53, 0.85), open_radius=9)
