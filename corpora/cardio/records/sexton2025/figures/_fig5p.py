"""Shared reading code for Fig. 5P(iii) (PDF p. 6): two black bar charts, bar 1 = Perfused, bar 2 = Media
Ctrl, each with an upper error bar (mean +- SD, N = 3, as the caption's "37.8 +- 33.6%" matches). The
figure is an embedded raster.

Calibration: the y axis is the leftmost long vertical dark line; its tick marks point left. Their row
centres, from the top, are matched to the printed labels (the last one, 0, lies on the x axis); a straight
line is fitted and its misfit widens every interval. The bars' columns are the x-axis ticks below the
axis (pointing down), numbered from the left.

A bar's value is its top edge: in the bar's column (+-12 px), the first dark row walking up from the x
axis that is no longer bar (the column turns light); measured in two columns 12 px either side of the
error bar stem. A bar no taller than the axis line is read as lying within the axis line: its value is
between 0 and the value of the axis line's top edge.

Error bar: the stem rising from the bar top at the bar centre; its upper end is the cap (the topmost
dark row of the stem, the cap's centre is half the cap thickness below). The lower half is hidden in
the black bar and taken as the mirror of the upper about the bar top.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

DARK = 100


def calibrate(image, labels):
    g = C.gray(image)
    ink = g < DARK
    H, W = ink.shape
    rows, cols = C.frame(image, DARK, 0.6)
    yc = cols[0]
    xr = [r for r in rows if r[0] > 0.5 * H][-1]
    yt = C.ticks_on_vertical(image, yc[1], yc[2], "out", 12, 0, xr[2] + 15, DARK)
    yt = [t[0] for t in yt]
    if len(yt) != len(labels):
        raise RuntimeError(f"expected {len(labels)} y ticks, found {yt}")
    xt = C.ticks_on_horizontal(image, xr[1], xr[2], "out", 12, yc[2] + 6, W, DARK)
    xt = [t[0] for t in xt]
    return C.Axis(yt, labels), xt, xr, yc, ink


def read_bars(image, at, labels):
    ax, xt, xr, yc, ink = calibrate(image, labels)
    out = []
    axis_top = xr[1]
    for xv in at:
        k = int(round(float(xv)))
        cc = int(round(xt[k - 1]))
        tops = []
        for dc in (-14, 14):
            c = cc + dc
            r = axis_top - 1
            while r > 0 and ink[r, c]:
                r -= 1
            tops.append(r + 1)
        top = float(np.mean(tops))
        if top >= axis_top - 1:
            hi_v = ax.val(axis_top - ax.misfit)
            out.append({"x": k, "y": max(ax.val(axis_top), 0.0), "lo": 0.0, "hi": hi_v, "px": [float(cc), float(axis_top)],
                        "note": f"bar {k}: not taller than the x axis line; its value lies between 0 and the value of the axis "
                                f"line's top edge (row {axis_top}); its error bar, if any, is hidden in the axis line"})
            continue
        tol = abs(tops[0] - tops[1]) / 2.0 + 2.0
        y = ax.val(top)
        lo, hi = ax.interval(top, tol)
        if axis_top - top < 8:
            # a bar a few pixels tall: in this blurred raster its top cannot be told from the axis line's
            # edge and any error bar on it; the value is somewhere between 0 and just above what was read
            hi = ax.interval(top, tol)[1]
            out.append({"x": k, "y": y, "lo": 0.0, "hi": hi, "px": [float(cc), top],
                        "note": f"bar {k}: only {axis_top - top:.1f} px above the x axis line (top row {axis_top}); "
                                f"cannot be told from the line's edge or its own error bar, so the interval runs from 0"})
            continue
        # error bar stem: dark columns at the bar centre above the bar top
        probe = int(top) - 15
        cols = [c for c in range(cc - 10, cc + 11) if ink[probe, c]]
        if not cols:
            out.append({"x": k, "y": y, "lo": lo, "hi": hi, "px": [float(cc), top], "note": f"bar {k}: no error bar above"})
            continue
        sc = int(round(np.mean(cols)))
        r = probe
        while r > 0 and ink[r, sc - 1: sc + 2].any():
            r -= 1
        cap_top = r + 1
        cap_rows = [rr for rr in range(cap_top, cap_top + 30) if ink[rr, sc + 12] or ink[rr, sc - 12]]
        cap_bot = (max(cap_rows) + 1) if cap_rows else cap_top + 6
        cap_c = (cap_top + cap_bot) / 2.0
        ctol = (cap_bot - cap_top) / 2.0 + 2
        hi_end = ax.val(cap_c)
        lo_end = 2 * y - hi_end
        hi_out = ax.interval(cap_c, ctol)[1]
        lo_out = 2 * lo - hi_out
        out.append({"x": k, "y": y, "lo": lo, "hi": hi, "px": [float(sc), top],
                    "bar_lo": lo_end, "bar_hi": hi_end, "bar_lo_outer": min(lo_out, lo_end), "bar_hi_outer": max(hi_out, hi_end),
                    "px_lo": 2 * top - cap_c, "px_hi": cap_c,
                    "note": (f"bar {k}: top at row {top:.1f}; cap centre at row {cap_c:.1f}; the lower half of the error bar is "
                             f"hidden in the bar and taken as the mirror of the upper; misfit {ax.misfit:.2f} px")})
    return out
