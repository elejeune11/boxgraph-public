"""Fig. S4B (p. 42): time (s, log) of implicit reconstruction against the number of points (log): partition
of unity (blue) and global (orange).

Calibration: frame lines (dark < 100); the decade ticks are the long ticks outside the frame (runs of
at least 12 of the 15 px next to it at 1000 dpi; the minor ticks are shorter): y 10^2, 10^1, 10^0 from
the top, x 10^2, 10^3. Log fits; misfit widens intervals. Lines traced as in _curves.py (colour within 50
of the plotting library's standard blue and orange; the grey grid is excluded), seeds at 1000 points.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _curves as K  # noqa: E402

COLOURS = {"pu": (31, 119, 180), "global": (255, 127, 14)}


def read(image, at, which):
    rows, cols = C.frame(image, 100, 0.45)
    yc, xr = cols[0], rows[-1]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 15, 0, xr[2] + 15, 100, 12)]
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 15, yc[2] + 5, image.shape[1], 100, 12)]
    if len(yt) != 3 or len(xt) != 2:
        raise RuntimeError(f"expected 3 y and 2 x decade ticks, found {yt} {xt}")
    ax_y = C.Axis(yt, [1e2, 1e1, 1e0], "log10")
    ax_x = C.Axis(xt, [1e2, 1e3], "log10")
    box = (yc[2] + 1, rows[0][2] + 1, cols[-1][1], xr[1])
    return K.read_traced(image, at, ax_x, ax_y, box, COLOURS[which], 50, 1000, pick="lowest",
                           max_gap=40)  # bridges where one line is drawn over the other at their crossing
