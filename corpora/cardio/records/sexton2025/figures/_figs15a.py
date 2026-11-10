"""Fig. S15A(i) (p. 65): frequency distribution of cell area (um^2), live (green) and dead (red) cells, bars
side by side in each bin.

Calibration: the y axis is the leftmost long dark vertical line, its ticks point left, matched to 0, 200,
400, 600, 800 from the bottom (the 0 tick is at the x axis). The x axis (lowest long dark line) has ticks
below it; the first 15 are labelled 60, 120, ..., 900 (two more unlabelled ticks follow), matched in
order. Linear fits; misfit widens intervals.

Bars: boxgraph.digitize.read_bars on each colour's mask (within 70 of the bar colour). Each bar's x is
put on its bin centre: the bins' spacing is the median distance between successive bars of one colour
(read from the image), and a bar's x is rounded to the nearest centre on that grid starting at the first
labelled tick (60); live bars stand left of the centre, dead bars right of it. The bar's top edge is its
value; interval 1 px + misfit. The legend swatches, also found as bars, are dropped: they are more than
three times as wide as the median bar. Bars only a few pixels tall stay readings with intervals reaching to 0.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from boxgraph import digitize as D  # noqa: E402

COLOURS = {"live": (20, 145, 70), "dead": (235, 50, 40)}


def calibrate(image):
    rows, cols = C.frame(image, 100, 0.4)
    yc = cols[0]
    xr = [r for r in rows if r[0] > 0.3 * image.shape[0]][0]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 20, 0, xr[2] + 10, 100)]
    if len(yt) != 5:
        raise RuntimeError(f"expected 5 y ticks, found {yt}")
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 20, yc[1] - 5, image.shape[1], 100)]
    if len(xt) < 15:
        raise RuntimeError(f"expected at least 15 x ticks, found {xt}")
    ax_x = D.Axis("linear", list(zip(xt[:15], range(60, 901, 60))))
    ax_y = D.Axis("linear", list(zip(yt, [800, 600, 400, 200, 0])))
    # the box starts at the y axis line itself: the first green bar touches it (the mask is colour-only)
    return ax_x, ax_y, (yc[1] - 1, 0, xt[-1] + 40, xr[1] - 1)


def read(image, at, which):
    from scipy import ndimage

    ax_x, ax_y, box = calibrate(image)
    c0, r0, c1, r1 = [int(v) for v in box]
    m = np.zeros(image.shape[:2], bool)
    m[r0:r1, c0:c1] = C.hue_mask(image, COLOURS[which], 70)[r0:r1, c0:c1]
    # anti-aliased tick rows can break a bar's colour for a few rows: close vertical gaps up to 12 px
    m = ndimage.binary_closing(m, structure=np.ones((13, 1), bool))
    cols = [c for c in range(c0, c1) if m[r1 - 10, c]]  # a bar stands on the x axis
    groups = C.merge(cols, gap=1)
    bars = []
    for _, a, b in groups:
        tops = []
        for c in range(a, b + 1):
            rs = C.column_runs(m, c, r0, r1)
            tops.append(rs[-1][0])  # the run standing on the axis
        top = float(np.median(tops))
        bars.append((a, b, top, max(tops) - min(tops)))
    widths = [b - a + 1 for a, b, _, _ in bars]
    wmed = float(np.median(widths))
    out = []
    xs = sorted(ax_x.to_value((a + b + 1) / 2.0) for a, b, _, _ in bars if b - a + 1 >= 3)
    step = float(np.median(np.diff(xs)))
    mis = max(ax_y.residual_px, 0.5)
    for a, b, top, spread in bars:
        if b - a + 1 < 3 or b - a + 1 > 3 * wmed:
            continue
        xc = ax_x.to_value((a + b + 1) / 2.0)
        k = round((xc - 60) / step)
        centre = 60 + k * step
        h = 1.0 + mis + spread / 2.0
        lo, hi = sorted((ax_y.to_value(top + h), ax_y.to_value(top - h)))
        out.append({"x": round(centre, 6), "y": ax_y.to_value(top), "lo": max(lo, 0.0), "hi": hi,
                    "px": [(a + b + 1) / 2.0, top],
                    "note": f"bar columns {a}-{b}, top row {top:.0f}; drawn at x = {xc:.1f}, put on the bin centre "
                            f"{centre:.1f} (bin spacing {step:.2f} read from the bars)"})
    return sorted(out, key=lambda o: o["x"])
