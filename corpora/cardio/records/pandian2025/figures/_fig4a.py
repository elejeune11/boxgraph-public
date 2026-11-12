"""Shared reading code for Fig. 4a (PDF p. 8): diffusive permeability P_D (axis 'P_D 10^-6 cm/s', 0 ... 80) of 70 kDa
dextran in the single-channel device, control (dark grey bar, x = 1) and IL-1beta (light grey bar, x = 2), each with
a black error bar drawn upward from the bar top (only the upper half shows) and every measurement as a large black
dot. The caption does not say what the bar and the error bar are (mean and SD is GraphPad's default; unstated).
Raster figure, read at 1500 dpi in the same crop as Fig. 4b.

Calibration (_axes.py): in box (700-2100, 100-2900) the darkest column / row are the axis lines; y ticks (left,
>= 20 px) are matched to the printed 80, 60, 40, 20, 0 (x 10^-6 cm/s), reported in nm/s (x 10: 10^-6 cm/s =
10 nm/s; the unit '1e-6*cm/s' would lose its factor in the unit parser); x ticks below the axis are the bar
centres.

Bar top: in each column across the middle 80 % of the bar, the topmost pixel of the bar's own grey (control
100-175, IL-1beta 200-238) with white 3 px above it and the bar's grey for 12 px below (columns where a dot or
the error bar covers the edge give none); the bar top is the median over columns, the interval +/- (spread of the columns' tops between the 25th and 75th percentiles + 2 px +
misfit).

Error bar cap: black pixels (< 90) in vertical runs of at most 18 px (thin lines; the dots are thicker) that cover
at least 40 % of the +/- 40 px around the bar centre in a row: the topmost such row group above the bar top is the
cap; its centre is the upper end, the lower half is hidden in the bar and taken as the mirror of the upper about
the bar top.

Dots: pixels darker than 90, distance transform > 22 px (the dots have a radius of about 30 px; lines are under
18 px thick); local maxima at least 30 px apart within +/- 0.45 x bar spacing of the bar centre. Overlapping dots
in the control group may merge; the count is reported in the notes.
"""

import numpy as np
from scipy import ndimage as ndi
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_axes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
_spec2 = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(C)

BANDS = {1: (100, 175), 2: (200, 238)}


def calibrate(image):
    # the printed labels 80 ... 0 are in 10^-6 cm/s; the reading is reported in nm/s (10^-6 cm/s = 10 nm/s)
    # because a unit with a numeric factor is not kept by the unit parser
    return C.calibrate(image, (700, 2100, 100, 2900), [10 * v for v in (80, 60, 40, 20, 0)], False)


def bar_extent(cal, k):
    g = cal["g"]
    lo, hi = BANDS[k]
    row = cal["xa"][0] - 20  # clear of the axis line's blurred edge
    c = int(cal["cols"][k - 1])
    w = int(0.48 * cal["sp"])
    seg = (g[row, c - w: c + w] >= lo) & (g[row, c - w: c + w] <= hi)
    # the bar is the longest run of its grey on that row (dots interrupt it, so join gaps under 80 px)
    runs = A.runs(seg)
    s, e = runs[0][0], runs[-1][1]
    return c - w + s, c - w + e


def bar_top(cal, k):
    g = cal["g"]
    lo, hi = BANDS[k]
    c0, c1 = bar_extent(cal, k)
    wid = c1 - c0
    tops = []
    for c in range(int(c0 + 0.1 * wid), int(c1 - 0.1 * wid)):
        col = (g[:, c] >= lo) & (g[:, c] <= hi)
        top_r = int(min(cal["ticks"]))
        # the bar's top edge: a pixel of the bar's grey with white (> 240) 3 px above and the bar's grey for
        # the 12 px below; columns where a dot or the error bar sits on the edge have no such pixel
        cand = [r for r in range(top_r, cal["xa"][0] - 15)
                if col[r] and g[r - 3, c] > 240 and col[r: r + 12].all()]
        if cand:
            tops.append(cand[0])
    tops = np.array(tops, float)
    t = float(np.median(tops))
    spread = float(np.percentile(tops, 75) - np.percentile(tops, 25))
    return t, spread / 2.0 + 2 + cal["mis"], (c0, c1)


def read_bars(image, at):
    cal = calibrate(image)
    g = cal["g"]
    out = []
    for x in at:
        k = int(round(x))
        t, tol, (c0, c1) = bar_top(cal, k)
        cc = (c0 + c1) // 2
        y = C.val(cal, t)
        lo, hi = sorted((C.val(cal, t + tol), C.val(cal, t - tol)))
        rec = {"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(cc), t],
               "note": f"bar {k}: top at row {t:.1f} (columns {c0}-{c1}); misfit {cal['mis']:.2f} px"}
        top_r = int(min(cal["ticks"])) - 5
        sub = g[top_r:int(t) - 2, cc - 40: cc + 41] < 90
        thin = sub & (C.vrun(sub) <= 18)
        frac = thin.mean(axis=1)
        groups = A.runs(frac >= 0.4)
        # ignore the significance bar: it lies above the 80 tick's level only for group 2's neighbour; keep rows
        # below the 70 level
        r70 = C.row_of(cal, 700.0) - top_r
        groups = [(s, e) for s, e in groups if s > r70]
        if groups:
            s, e = groups[0]
            capc = top_r + (s + e - 1) / 2.0
            ctol = (e - s) / 2.0 + 2 + cal["mis"]
            up = C.val(cal, capc)
            rec["bar_hi"] = up
            rec["bar_lo"] = 2 * y - up
            rec["bar_hi_outer"] = C.val(cal, capc - ctol)
            rec["bar_lo_outer"] = 2 * lo - C.val(cal, capc - ctol)
            rec["px_lo"], rec["px_hi"] = 2 * t - capc, capc
            rec["note"] += (f"; error bar cap at row {capc:.1f}; the lower half is hidden in the bar and taken as the "
                            f"mirror of the upper about the bar top")
        else:
            rec["note"] += "; no error bar cap found"
        out.append(rec)
    return out


def read_dots(image):
    cal = calibrate(image)
    g = cal["g"]
    m = g < 90
    m[: int(C.row_of(cal, 700.0)), :] = False  # the significance bar and stars (above 70 x 10^-6 cm/s)
    m[cal["xa"][0] - 3:, :] = False
    m[:, : cal["ya"][1] + 3] = False
    m[:, int(cal["cols"][-1] + 0.5 * cal["sp"]):] = False
    dt = ndi.distance_transform_edt(m)
    out = []
    for k in (1, 2):
        c = cal["cols"][k - 1]
        pk = [(r, cc) for r, cc in A.peaks(dt, 22, 30) if abs(cc - c) <= 0.45 * cal["sp"]]
        pk.sort(key=lambda rc: (rc[0], rc[1]))
        for i, (r, cc) in enumerate(pk):
            tol = 3 + cal["mis"]
            lo, hi = sorted((C.val(cal, r + tol), C.val(cal, r - tol)))
            out.append({"x": round(k + (i + 1) / 100.0, 2), "y": C.val(cal, r), "lo": lo, "hi": hi,
                        "px": [float(cc), float(r)], "px_lo": r + tol, "px_hi": r - tol,
                        "note": f"group {k}, dot {i + 1} of {len(pk)} found (top to bottom; radius {dt[r, cc]:.0f} px); "
                                f"x is the group plus 0.01 x the dot's order"})
    return out
