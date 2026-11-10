"""Fig. 2F (p. 3): point-enclosure time (s, log axis) against the number of points, mesh-based (red)
against partial implicit volume (blue); shading +-2 SD, N = 25. Each colour has a dashed and a solid
line drawn on top of each other (the legend shows the dashed ones); the reading follows the line of that
colour, solid and dashed together, and the interval covers both where they part.

Calibration: the y axis has three long (decade) ticks, labelled from the top "10^-5", "10^-4", "10^-5".
The top label cannot be right on a log axis whose next decade down is 10^-4 (it would be 10^-3; see
q_fig2f_axis_label). Only the two lower labelled ticks, 10^-4 and 10^-5, are used; the top one is
dropped. The x axis has major ticks below it labelled 100 ... 500 (the 0 tick is the y axis). See
_curves.py. Seeds at 300 points, where each line is the only run of its colour.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _curves as K  # noqa: E402

COLOURS = {"mesh": (230, 35, 45), "piv": (45, 80, 165)}


def read(image, at, which):
    rows, cols = C.frame(image, 160, 0.45)
    yc = cols[0]
    xr = rows[-1]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 40, 0, xr[2] + 20, 160, 36)]
    if len(yt) != 3:
        raise RuntimeError(f"expected 3 decade ticks, found {yt}")
    ax_y = C.Axis(yt[1:], [1e-4, 1e-5], "log10")
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 30, yc[2] + 10, image.shape[1], 160, 25)]
    if len(xt) != 5:
        raise RuntimeError(f"expected 5 x ticks, found {xt}")
    ax_x = C.Axis(xt, [100, 200, 300, 400, 500])
    box = (yc[2] + 1, rows[0][2] + 1, image.shape[1], xr[1])
    out = K.read_traced(image, at, ax_x, ax_y, box, COLOURS[which], 70, 300, pick="lowest")
    top = ax_y.val(yt[0])
    for r in out:
        r["note"] = (r["note"] + f"; the top decade tick's printed label 10^-5 is not used (by the fit it is {top:.3g})")
    return out


_ = np
