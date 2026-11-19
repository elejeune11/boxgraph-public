"""Fig. 2a (PDF p. 6): kbar against eps; the bifurcation curve (solid, then dashed beyond M) and the
chain curve of the lower bound of the crease strain.

Calibration by `_diab.calibrate` (see its docstring): x ticks labelled 0, 0.1, ..., 0.5 and y ticks
labelled 0, 2, ..., 10, all found as tick marks outside the axes.
The legend box (two long thin horizontal lines inside the plot) is found and everything between its
lines is ignored. The ink is opened with a 15 px square, which removes the dotted guide lines (kbar_M,
eps_M, eps_H, eps_B, about 8 px thick) and keeps the curves (about 18-24 px); pieces smaller than
2.5 line widths squared (the dots of the chain line, serifs of labels) are then dropped.
Bifurcation curve: followed column by column (`_diab.track`) from the lowest stroke at eps = 0.1
(where nothing else is drawn) to both ends, so the labels M, eps_M, eps_H, eps_B under the curve
are not taken; dashes' gaps are bridged by extrapolation.
Chain curve: the stroke pieces lying wholly more than two line thicknesses above the followed
bifurcation curve, between eps = 0.24 and 0.36 and below the legend (`chain_points`).
At each position the curve points within 80 px (along the curve) of the point nearest the position's
column are fitted by a local line (`_diab.fit_points`).
"""
import importlib.util
from pathlib import Path

import numpy as np


def _d():
    spec = importlib.util.spec_from_file_location("diab2013_d", Path(__file__).with_name("_diab.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


WIN = 80


def legend_rows(d, dk, cal):
    """Rows of the legend box: the long thin dark rows inside the plot."""
    c0, c1 = cal["y_col"][1] + 5, cal["x_end"] - 5
    frac = dk[cal["y_top"]:cal["x_row"][0] - 5, c0:c1].mean(1)
    rows = np.where(frac > 0.3)[0] + cal["y_top"]
    gs = d.groups(rows)
    if len(gs) < 2:
        return None
    return gs[0][0], gs[-1][-1]


def chain_points(d, m, bif, leg, cal, lw):
    """Centre-line points of the chain curve's dashes: the stroke pieces lying wholly more than two
    line widths above the followed bifurcation curve, between eps = 0.24 and 0.36 and below the
    legend box. A piece's centre line is the run centres along its longer extent (per column for a
    shallow dash, per row for a steep one). Returned as a list of (col, row)."""
    from scipy import ndimage
    X = cal["x"]
    bc = sorted(bif)
    lab, n = ndimage.label(m)
    pts = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rs, cs = np.where(lab[sl] == i)
        rs = rs + sl[0].start
        cs = cs + sl[1].start
        if cs.min() < X.pix_of(0.24) or cs.max() > X.pix_of(0.36):
            continue
        if leg is not None and rs.min() <= leg[1] + 5:
            continue
        rb = np.interp(cs, bc, [bif[c] for c in bc])
        if not np.all(rs < rb - 2 * lw):
            continue
        if np.ptp(cs) >= np.ptp(rs):
            for c in np.unique(cs):
                pts.append((float(c), float(rs[cs == c].mean())))
        else:
            for r in np.unique(rs):
                pts.append((float(cs[rs == r].mean()), float(r)))
    return pts


def read_curves(image, at, which):
    d = _d()
    dk = d.dark(image)
    cal = d.calibrate(dk, [0, 0.1, 0.2, 0.3, 0.4, 0.5], [0, 2, 4, 6, 8, 10])
    m = d.open_mask(dk, 15)
    leg = legend_rows(d, dk, cal)
    r_top, r_bot = cal["y_top"], cal["x_row"][0] - 3
    X = cal["x"]
    lw = d.thickness(m, range(int(X.pix_of(0.08)), int(X.pix_of(0.12))), r_top, r_bot)
    m = d.drop_small(m, 2.5 * lw * lw)

    def runs(c):
        rr = d.runs_in_col(m, c, r_top, r_bot)
        if leg is not None:
            rr = [(a, b) for a, b in rr if not (leg[0] - 5 <= a and b <= leg[1] + 5)]
        return rr

    c0 = int(round(X.pix_of(0.1)))
    a, b = runs(c0)[-1]
    bif = d.track(runs, c0, (a + b) / 2, cal["x_end"] - 5, lw)
    bif.update(d.track(runs, c0, (a + b) / 2, int(X.pix_of(0.005)), lw))
    curve = bif
    if which == "chain":
        curve = chain_points(d, m, bif, leg, cal, lw)

    out = []
    for x in at:
        x = float(x)
        col = X.pix_of(x)
        items = list(curve.items() if isinstance(curve, dict) else curve)
        near = [(c, r) for c, r in items if abs(c - col) <= WIN]
        if not near:
            out.append({"x": x, "y": None, "note": "curve not followed here"})
            continue
        # the points along the curve within WIN (arc length) of the one nearest the position's column
        c0, r0 = min(near, key=lambda p: abs(p[0] - col))
        pts = [(c, r) for c, r in items if (c - c0) ** 2 + (r - r0) ** 2 <= WIN**2]
        f = d.fit_points(pts, col, lw)
        if f is None:
            out.append({"x": x, "y": None, "note": "curve not followed here"})
            continue
        row, slope, rms, n = f
        y, lo, hi, dpx = d.value(cal, col, row, slope, lw, rms)
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(col), float(row)],
                    "px_lo": float(row + dpx), "px_hi": float(row - dpx),
                    "note": f"line {lw:.0f} px; calibration misfit x {X.misfit:.1f} px, y {cal['y'].misfit:.1f} px; "
                            f"local slope {slope:.2f} px/px, fit rms {rms:.1f} px over {n} columns"})
    return out
