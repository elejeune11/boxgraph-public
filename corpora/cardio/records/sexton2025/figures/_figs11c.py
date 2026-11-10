"""Fig. S11C (p. 60): example PIV velocity profiles across three channels (Bottom blue, Middle red, Top
green): the solid lines are parabolic fits symmetric about r = 0 (caption). The squares (hundreds of
translucent, overlapping measurements) are not read; the fitted lines are.

Calibration: frame lines (dark < 120); y ticks out to the left matched to 0, 200, 400, 600, 800 (from the
bottom), x ticks out below matched to -800, -600, ..., 800. The lines are traced (see _curves.py) on a
mask within 60 of their saturated colour, which excludes the pale squares; seeds at r = 0. The dashed
vertical lines (channel boundaries) have the lines' colours and meet them at v = 0, so readings stay
inside +-0.9 of each channel's half-width.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _curves as K  # noqa: E402

COLOURS = {"bottom": (55, 75, 165), "middle": (230, 35, 40), "top": (20, 125, 55)}


def read(image, at, which):
    rows, cols = C.frame(image, 120, 0.45)
    yc, xr = cols[0], rows[-1]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 15, 0, xr[2] + 15, 120)]
    if len(yt) != 5:
        raise RuntimeError(f"expected 5 y ticks, found {yt}")
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 15, 0, image.shape[1], 120)]
    if len(xt) != 9:
        raise RuntimeError(f"expected 9 x ticks, found {xt}")
    ax_x = C.Axis(xt, [-800, -600, -400, -200, 0, 200, 400, 600, 800])
    ax_y = C.Axis(yt, [800, 600, 400, 200, 0])
    box = (yc[2] + 1, rows[0][2] + 1, cols[-1][1], xr[1])
    return K.read_traced(image, at, ax_x, ax_y, box, COLOURS[which], 60, 0, pick="lowest", max_gap=20)
