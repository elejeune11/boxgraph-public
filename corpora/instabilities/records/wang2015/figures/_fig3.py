"""Shared reading code for Fig. 3A (p. 4) of wang2015, the phase diagram for strong adhesion:
mismatch strain eM on the horizontal axis (linear, 0 ... 0.6) and mu_f/mu_s on the vertical
axis (logarithmic, 10^-1 ... 10^5).

Calibration: the frame and tick marks are found with boxgraph.digitize.find_axes.
Horizontal: the y axis line is eM = 0 and the six evenly spaced ticks are 0.1 ... 0.6 (the
last on the right frame edge). Vertical: the bottom frame edge is labelled 10^-1 and the top
edge 10^5; the decade ticks 10^0 ... 10^4 between them are matched to the found tick marks
(each decade position predicted from the frame, then snapped to the nearest tick within 6 px;
a decade with no tick found is left out of the fit).

Lines are the dark (black, unsaturated) pixels; coloured markers are not dark.
"""
import math
import sys

import numpy as np


def _digitize():
    try:
        from boxgraph import digitize as D
    except ImportError:  # run outside the package
        sys.path.insert(0, ".")
        from boxgraph import digitize as D
    return D


def _fit(px, vals):
    px, vals = np.asarray(px, float), np.asarray(vals, float)
    b, a = np.polyfit(px, vals, 1)
    mis = float(np.max(np.abs(px - (vals - a) / b)))
    return a, b, max(mis, 0.5)


class Cal:
    """col <-> eM (linear) and row <-> log10(mu_f/mu_s)."""

    def __init__(self, img):
        D = _digitize()
        fa = D.find_axes(img)
        self.box = fa.box
        xt = sorted(fa.x_ticks)
        if len(xt) != 6:
            raise ValueError(f"expected six x ticks 0.1 ... 0.6, found {xt}")
        self.ax, self.bx, self.mx = _fit([fa.y_axis_col] + xt, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        r_bottom, r_top = fa.x_axis_row, fa.box[1] - 0.5
        step = (r_bottom - r_top) / 6.0
        rows, logs = [r_bottom, r_top], [-1.0, 5.0]
        for k in range(1, 6):
            pred = r_bottom - k * step
            near = [c for c in fa.y_candidates if abs(c - pred) <= 6.0]
            if near:
                rows.append(min(near, key=lambda c: abs(c - pred)))
                logs.append(-1.0 + k)
        self.ay, self.by, self.my = _fit(rows, logs)

    def eM(self, col):
        return self.ax + self.bx * col

    def col(self, eM):
        return (eM - self.ax) / self.bx

    def ratio(self, row):
        return 10.0 ** (self.ay + self.by * row)

    def row(self, ratio):
        return (math.log10(ratio) - self.ay) / self.by


def dark(img):
    img = img.astype(int)
    return (img.mean(2) < 110) & ((img.max(2) - img.min(2)) < 60)


def _runs(idx):
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append((cur[0], cur[-1]))
            cur = []
        if i is not None:
            cur.append(int(i))
    return out


def horizontal_line(img, at_eM, ratio_lo, ratio_hi, eM_lo, eM_hi, halfwin=14):
    """A horizontal dotted line between ratio_lo and ratio_hi: its row is first located as
    the peak of the dark-pixel profile over eM_lo ... eM_hi; then at each eM the dark run
    nearest that row, in the columns within halfwin, gives the value."""
    cal = Cal(img)
    d = dark(img)
    r0, r1 = int(cal.row(ratio_hi)), int(cal.row(ratio_lo))
    c0, c1 = int(cal.col(eM_lo)), int(cal.col(eM_hi))
    prof = d[r0:r1, c0:c1].sum(1)
    peak = r0 + int(np.argmax(prof))
    out = []
    for x in at_eM:
        c = int(round(cal.col(x)))
        rows = np.nonzero(d[peak - 30:peak + 31, c - halfwin:c + halfwin + 1].any(1))[0] + peak - 30
        runs = _runs(rows)
        if not runs:
            out.append({"x": x, "y": None, "note": "no dot of the line near this eM"})
            continue
        s, e = min(runs, key=lambda t: abs((t[0] + t[1]) / 2 - peak))
        row = (s + e) / 2.0
        err = (e - s + 1) / 2.0 + cal.my
        out.append({"x": x, "y": cal.ratio(row), "lo": cal.ratio(row + err), "hi": cal.ratio(row - err),
                    "px": [float(c), row], "px_lo": row - err, "px_hi": row + err,
                    "note": f"dotted line rows {s}-{e} (profile peak at row {peak}); misfit {cal.my:.1f} px"})
    return out


def vertical_line(img, at_ratio, eM_lo, eM_hi, halfwin=10):
    """A dotted line read as eM at given ratios (x of the reading = ratio): in the rows within
    halfwin of each ratio's row, the dark runs between eM_lo and eM_hi; the run nearest the
    middle of the window's runs gives the value, its extent (and the rows' spread) the interval."""
    cal = Cal(img)
    d = dark(img)
    c0, c1 = int(cal.col(eM_lo)), int(cal.col(eM_hi))
    out = []
    for ratio in at_ratio:
        r = int(round(cal.row(ratio)))
        cols = np.nonzero(d[r - halfwin:r + halfwin + 1, c0:c1].any(0))[0] + c0
        runs = _runs(cols)
        runs = [t for t in runs if t[1] - t[0] <= 40]  # dots and a slanted line, not a horizontal line
        if not runs:
            out.append({"x": ratio, "y": None, "note": "no dot of the line near this ratio"})
            continue
        s = min(t[0] for t in runs)
        e = max(t[1] for t in runs)
        if e - s > 60:
            out.append({"x": ratio, "y": None, "note": f"dark pixels spread over columns {s}-{e}: not one line"})
            continue
        col = (s + e) / 2.0
        err = (e - s + 1) / 2.0 + cal.mx
        out.append({"x": ratio, "y": cal.eM(col), "lo": cal.eM(col - err), "hi": cal.eM(col + err),
                    "px": [col, float(r)],
                    "note": f"dotted line columns {s}-{e} within rows {r - halfwin}-{r + halfwin}; misfit {cal.mx:.1f} px"})
    return out
