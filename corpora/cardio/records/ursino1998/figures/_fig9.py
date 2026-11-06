"""Shared reading code for Fig. 9 (p. 9): percent changes of SAP, CO, HR and R 80 s after a 10%
hemorrhage, as bars on both sides of the zero line. Top: model (grey) and Kumada et al.'s data
(white), two bars per group. Bottom: sensitivity analysis, five bars per group in the legend's
order (basal, no resistance, no unstressed volume, no Emax, no HR).

Calibration as in _excel.py: the y ticks at every printed label (the 0 label where the zero line
crosses). The groups are the stretches of the zero line between the y axis and the short ticks
standing on the zero line. In each group the bars stand side by side: the outermost ink of each
column (above or below the zero line) traces their ends, the bar width is the common length of
the flat stretches of that trace, and bar k of a group spans [left + k w, left + (k + 1) w] from
the first bar's left side. A bar's value is the median end over its middle 60% of columns; a bar
of almost zero height is read where its end merges with the zero line, and says so.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "_excel", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_excel.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)
u = X.u

PANELS = {
    "top": dict(yvals=[-20, -10, 0, 10, 20, 30], legend=(950, 230, 1800, 820), nbars=2),
    "bottom": dict(yvals=[-20, -15, -10, -5, 0, 5, 10, 15], legend=(2900, 1700, 4375, 2805), nbars=5),
}


def read_series(image, name, k):
    """Bar k of each of the four groups; x is the group's index (1 SAP, 2 CO, 3 HR, 4 R)."""
    spec = PANELS[name]
    p = X.Panel(image, xvals=None, yvals=spec["yvals"], x_axis="middle", y_at_xaxis=True,
                legend=spec["legend"])
    groups = [trace(p, g) for g in range(4)]
    # one bar width for the chart: the widest group span over its number of bars (a group whose
    # last bar is of zero height spans fewer)
    w = max((g["right"] - g["left"]) / spec["nbars"] for g in groups)
    return p.finish([read_bar(p, g, k, w, i) for i, g in enumerate(groups)])


def trace(p, group):
    m = p.m.copy()
    m[: p.yaxis[2] - 10, :] = False  # the group titles (SAP, CO, HR, R) above the plot
    z0, z1 = p.xaxis[0], p.xaxis[1]
    zc = (z0 + z1) / 2.0
    # group boundaries: ticks standing on the zero line, right of the y axis
    # (they cross the line: marks on both sides, unlike the sides of the bars, which stand on one)
    above = [c for c, n in u.tick_marks(p.m0, (z0, z1), 0, -1, length=(12, 80)) if n >= 20]
    below = [c for c, n in u.tick_marks(p.m0, (z0, z1), 0, +1, length=(12, 80)) if n >= 20]
    seps = sorted(c for c in above if c > p.yaxis[1] + 50 and any(abs(c - d) <= 7 for d in below))
    bounds = [p.yaxis[1]] + seps
    if len(bounds) < 5:
        raise ValueError(f"expected 4 groups, found boundaries {bounds}")
    # (clear of the y axis' ticks and the separators' own ink)
    g0, g1 = int(bounds[group]) + 60, int(bounds[group + 1]) - 30
    ends = np.full(g1 - g0, np.nan)
    for i, c in enumerate(range(g0, g1)):
        up = np.flatnonzero(m[: z0 - 2, c])
        dn = np.flatnonzero(m[z1 + 2:, c])
        e_up = (z0 - 2 - up.min()) if len(up) else 0
        e_dn = (dn.max() + 1) if len(dn) else 0
        if e_up >= e_dn and e_up > 0:
            ends[i] = up.min()
        elif e_dn > 0:
            ends[i] = z1 + 2 + dn.max() + 1
    # (ink within 60 px of the zero line's centre is the line and its ticks, not a bar's end)
    has = ~np.isnan(ends) & (np.abs(np.nan_to_num(ends, nan=zc) - zc) > 60)
    if not has.any():
        raise ValueError("no bars in this group")
    idx = np.flatnonzero(has)
    return dict(g0=g0, ends=ends, zc=zc, z=(z0, z1), left=g0 + idx[0], right=g0 + idx[-1] + 1)


def read_bar(p, g, k, w, group):
    a, b = g["left"] + k * w, g["left"] + (k + 1) * w
    ia, ib = int(a + 0.2 * w) - g["g0"], int(b - 0.2 * w) - g["g0"]
    seg = g["ends"][max(0, ia):ib]
    seg = seg[~np.isnan(seg)]
    col = (a + b) / 2.0
    zc = g["zc"]
    if len(seg) == 0 or np.all(np.abs(seg - zc) < 60):
        row = zc
        err = (g["z"][1] - g["z"][0]) / 2.0 + 25.0
        note = "a bar of about zero height: its end is within the zero line and its ticks"
    else:
        row = float(np.median(seg))
        err = 6.0 + float(np.ptp(seg)) / 2.0  # the outline: the outermost ink is half its width beyond the end
        note = f"bar {k + 1} of the group, {w:.0f} px wide"
    d = u.point(p.xcal, p.ycal, col, row, err + p.ycal.err, note + "; " + p.note())
    d["x"] = float(group + 1)
    return d
