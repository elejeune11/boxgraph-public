"""Shared calibration code for the figure readings of pandian2025.

Every panel of this paper is a GraphPad-style plot with a black L-shaped frame: a vertical y axis line
with outward (leftward) tick marks and a horizontal x axis line with outward (downward) tick marks.

`frame(gray, box)` finds the two axis lines inside `box` (column range, row range of the crop that
contains the plot) as the column and the row with the most dark pixels.

`ticks_left(...)` finds the major y ticks: rows where a dark run starts at the y axis line and goes
left at least `min_len` px (minor ticks are shorter and are dropped by `min_len`). Consecutive rows are
grouped and their centres are returned from top to bottom. `ticks_down(...)` does the same for x ticks
below the x axis line, returned left to right.

`fit(pixels, labels)` fits value = a + b * pixel by least squares to the matched ticks (labels are the
printed numbers; for a log axis, pass their log10 and convert the reading with 10**) and returns
(a, b, misfit_px), the misfit being the largest residual of a tick, in px.
"""

import numpy as np


def gray(image):
    return image[..., :3].astype(float).mean(axis=2)


def runs(v):
    v = np.asarray(v, bool).astype(int)
    d = np.diff(np.concatenate([[0], v, [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def frame(g, box, dark=110):
    """The y axis line (column range) and x axis line (row range) inside box = (c0, c1, r0, r1)."""
    c0, c1, r0, r1 = box
    ink = g[r0:r1, c0:c1] < dark
    cs = ink.sum(axis=0)
    ycols = np.flatnonzero(cs >= 0.85 * cs.max())
    ya = runs(np.isin(np.arange(c1 - c0), ycols))[0]
    rs = ink.sum(axis=1)
    xrows = np.flatnonzero(rs >= 0.85 * rs.max())
    xa = runs(np.isin(np.arange(r1 - r0), xrows))[-1]
    return (ya[0] + c0, ya[1] + c0), (xa[0] + r0, xa[1] + r0)


def ticks_left(g, ycol, rows, min_len, dark=110, gap=1):
    """Rows (centres, top to bottom) of y ticks: dark runs at least min_len px long to the left of ycol[0]."""
    hits = []
    for r in range(*rows):
        n, c, miss = 0, ycol[0] - 1, 0
        while c > 0 and miss <= gap:
            if g[r, c] < dark:
                n, miss = n + 1 + miss, 0
            else:
                miss += 1
            c -= 1
        hits.append(n >= min_len)
    return [rows[0] + (a + b - 1) / 2.0 for a, b in runs(hits)]


def ticks_down(g, xrow, cols, min_len, dark=110, gap=1):
    """Columns (centres, left to right) of x ticks: dark runs at least min_len px long below xrow[1]."""
    hits = []
    for c in range(*cols):
        n, r, miss = 0, xrow[1], 0
        while r < g.shape[0] and miss <= gap:
            if g[r, c] < dark:
                n, miss = n + 1 + miss, 0
            else:
                miss += 1
            r += 1
        hits.append(n >= min_len)
    return [cols[0] + (a + b - 1) / 2.0 for a, b in runs(hits)]


def fit(pixels, labels):
    p = np.asarray(pixels, float)
    v = np.asarray(labels, float)
    if len(p) != len(v):
        raise RuntimeError(f"expected {len(v)} ticks, found {len(p)}: {list(np.round(p, 1))}")
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    return float(a), float(b), mis


def peaks(field, min_value, min_sep):
    """Local maxima of a 2D field above min_value, at least min_sep px apart (greedy, highest first)."""
    from scipy import ndimage as ndi
    mx = ndi.maximum_filter(field, size=int(min_sep))
    cand = np.argwhere((field == mx) & (field >= min_value))
    cand = sorted(cand.tolist(), key=lambda rc: -field[rc[0], rc[1]])
    keep = []
    for r, c in cand:
        if all((r - r2) ** 2 + (c - c2) ** 2 >= min_sep ** 2 for r2, c2 in keep):
            keep.append((r, c))
    return keep
