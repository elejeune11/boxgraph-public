"""Fig. S10A-B (p. 58): histograms of the average distance of tissue subregions to the nearest vessel, for
trees of 1E4 (blue), 1E5 (orange) and 1E6 (green) terminal vessels, in a biventricle (A) and an annulus
(B). The three histograms overlap; in the overlap the later-drawn colour hides the earlier one.

Calibration: frame lines (dark < 120; the y axis is the leftmost long line, the bars to its right are
also long dark columns), y ticks out to the left matched to the printed labels (A: 2500 ... 0; B: 500
... 0), x ticks out below matched to 0.00, 0.05, ..., 0.30.

Reading a histogram at x: in that column, the topmost pixel of the histogram's colour (within 45 of the
plotting library's standard blue, orange or green). It is that bin's top only if the pixels just above it
are background (the bar is not covered by another colour there) and the pixel below is the same colour;
otherwise the bin is hidden and returned without a value. A legend swatch is not a bar: below a bar's top
there is only histogram colour down to the x axis. Interval: the top edge's anti-aliasing (1 px),
the calibration misfit, and the spread of the top edge over +-3 columns (a reading next to a bin edge
covers both bins' heights).
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

COLOURS = {"1e4": (31, 119, 180), "1e5": (255, 127, 14), "1e6": (44, 160, 44)}
YLABELS = {"A": [2500, 2000, 1500, 1000, 500, 0], "B": [500, 400, 300, 200, 100, 0]}
XLABELS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]


def calibrate(image, panel):
    rows, cols = C.frame(image, 120, 0.45)
    yc = cols[0]
    xr = rows[-1]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 15, 0, xr[2] + 15, 120)]
    if len(yt) != len(YLABELS[panel]):
        raise RuntimeError(f"expected {len(YLABELS[panel])} y ticks, found {yt}")
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 15, yc[1], image.shape[1], 120)]
    if len(xt) != len(XLABELS):
        raise RuntimeError(f"expected {len(XLABELS)} x ticks, found {xt}")
    return C.Axis(xt, XLABELS), C.Axis(yt, YLABELS[panel]), rows[0][2] + 2, xr[1]


def _top(mask, bg, col, top, bottom):
    rows = np.flatnonzero(mask[top:bottom, col])
    if len(rows) == 0:
        return None
    r = top + int(rows[0])
    above = bg[max(r - 4, top): r, col]
    if len(above) == 0 or not above.all() or r + 2 >= bottom or not mask[r + 2, col]:
        return None
    # a bar stands on the x axis: below its top there is only histogram colour (a legend swatch has paper)
    below = bg[r + 3: bottom - 3, col]
    if len(below) and below.mean() > 0.02:
        return None
    return r


def read(image, at, panel, which):
    ax_x, ax_y, top, bottom = calibrate(image, panel)
    m = C.hue_mask(image, COLOURS[which], 45)
    other = np.zeros_like(m)
    for k, rgb in COLOURS.items():
        if k != which:
            other |= C.hue_mask(image, rgb, 90)
    # light: paper, or the lighter edge of a neighbouring bar of the same colour; not another histogram
    bg = ~other & ~m & (C.gray(image) > 120)
    out = []
    for xv in at:
        x = float(xv)
        c0 = int(np.floor(ax_x.pix(x)))
        r, c = None, c0
        for d in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6):  # thin light lines separate the bars
            r = _top(m, bg, c0 + d, top, bottom)
            if r is not None:
                c = c0 + d
                break
        if r is None:
            out.append({"x": x, "y": None, "note": "this histogram's bin is absent or covered by another colour here"})
            continue
        near = [_top(m, bg, c + d, top, bottom) for d in range(-3, 4)]
        near = [n for n in near if n is not None]
        spread = (max(near) - min(near)) if near else 0
        lo, hi = ax_y.interval(r + 0.5, 1.0 + spread)
        out.append({"x": x, "y": ax_y.val(r + 0.5), "lo": max(lo, 0.0), "hi": hi, "px": [c + 0.5, r + 0.5],
                    "note": f"bin top at row {r}" + (f"; top edge varies {spread} px within 3 columns" if spread else "")})
    return out
