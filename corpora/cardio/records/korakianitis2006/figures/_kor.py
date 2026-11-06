"""Shared reading code for the line plots of this paper (Figs. 2, 4-13). Every reading renders one
panel at 900 dpi; each figure is an embedded low-resolution raster (about 150 dpi: one raster pixel
is about 6 px at 900 dpi), black on white.

Calibration, all from the image:
- ink is darker than halfway between the paper (99th percentile) and the darkest pixel;
- the y axis is the column (left third) with the most ink, the x axis the row (lower half) with
  the most ink; their centres are used;
- tick marks point inwards from both axes. Every short run of ink leaving an axis is a candidate;
  the labelled (major) ticks are the longer ones, evenly spaced. They are matched in order to the
  printed labels the reading names (bottom to top, left to right). Where the axis corner itself
  carries the lowest y label (the x axis is drawn at that value) the x axis row is that mark;
- a straight line is fitted to the marks of each axis; its largest misfit (px) widens every
  interval; a misfit over 8 px raises an error (a label matched to the wrong tick).

Curves: the plots draw several black curves (solid, dotted, dash-dot, with or without triangle
markers) that cross and coincide. A reading names, per stretch of x, which of the separate tracks
of ink in the column it takes (counted from the top or from the bottom) and how many tracks it
expects there; a column with another number of tracks is not read. At x, the ink of the columns
within +-W px (enough to bridge the gaps of dotted and dashed lines) is split into tracks where
rows of ink are more than GAP px apart. The value is the centre of the chosen track's ink in the
centre columns (+-2 px) if any, else in the whole window; the interval is half the track's extent
plus one raster pixel plus the calibration misfit (with the local slope for the x misfit). Where
two curves coincide they form one track, and the reading is of both: the interval covers it.
A track taller than STEEP px in the centre columns is a near-vertical stretch and is not read.
"""

import numpy as np

W = 9        # px: half-width of the window that bridges dotted/dashed gaps
GAP = 10     # px: rows of ink further apart than this are separate tracks
BLUR = 6.0   # px: one pixel of the embedded raster
STEEP = 90   # px


def gray(image):
    return image[..., :3].astype(float).mean(axis=2)


def ink_mask(image):
    g = gray(image)
    thr = (np.percentile(g, 99) + g.min()) / 2.0
    return g < thr


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def axes_lines(ink):
    H, Wd = ink.shape
    # the axis line: the strongest column (row) and its neighbours within 20 px that are nearly
    # as strong (a long flat curve elsewhere is not part of it)
    cs = ink[:, : Wd // 3].sum(axis=0)
    k = int(np.argmax(cs))
    ycols = [c for c in range(max(k - 20, 0), min(k + 21, len(cs))) if cs[c] > 0.85 * cs.max()]
    yl, yr = int(min(ycols)), int(max(ycols)) + 1
    rs = ink[H // 2:, :].sum(axis=1)
    k = int(np.argmax(rs))
    xrows = [r + H // 2 for r in range(max(k - 20, 0), min(k + 21, len(rs))) if rs[r] > 0.85 * rs.max()]
    xt, xb = int(min(xrows)), int(max(xrows)) + 1
    yc = (yl + yr - 1) / 2.0
    xc = (xt + xb - 1) / 2.0
    col = ink[:, int(round(yc))]
    top = min(a for a, b in _runs(col) if b >= xt)
    row = ink[int(round(xc)), :]
    right = max(b for a, b in _runs(row) if a <= yr)
    return dict(yl=yl, yr=yr, xt=xt, xb=xb, yc=yc, xc=xc, top=top, right=right)


def tick_candidates(ink, ax, min_len=6):
    """(position, length) of runs of ink leaving the y axis to the right and the x axis upwards."""
    ylen = []
    for r in range(ax["top"], ax["xt"]):
        n = 0
        while ax["yr"] + n < ink.shape[1] and ink[r, ax["yr"] + n] and n < 200:
            n += 1
        ylen.append(n)
    ylen = np.array(ylen)
    yt = []
    for a, b in _runs((ylen >= min_len) & (ylen < 150)):
        if b - a > 40:
            continue
        yt.append(((a + b - 1) / 2.0 + ax["top"], int(ylen[a:b].max())))
    xlen = []
    for c in range(ax["yr"], ax["right"]):
        n = 0
        while ax["xt"] - 1 - n >= 0 and ink[ax["xt"] - 1 - n, c] and n < 200:
            n += 1
        xlen.append(n)
    xlen = np.array(xlen)
    xt = []
    for a, b in _runs((xlen >= min_len) & (xlen < 150)):
        if b - a > 40:
            continue
        xt.append(((a + b - 1) / 2.0 + ax["yr"], int(xlen[a:b].max())))
    return yt, xt


def _majors(cands, n_want):
    """The labelled ticks: among candidates longer than 1.3 times the median candidate, the
    longest chain of evenly spaced ones (each about one spacing, within 12%, after the previous)."""
    L = 1.3 * float(np.median([l for _, l in cands]))
    c = sorted(p for p, l in cands if l > L)
    best = []
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            d = c[j] - c[i]
            if d < 60:
                continue
            chain = [c[i], c[j]]
            while True:
                nxt = [p for p in c if abs(p - chain[-1] - d) <= 0.12 * d]
                if not nxt:
                    break
                chain.append(min(nxt, key=lambda p: abs(p - chain[-1] - d)))
            if len(chain) > len(best) or (len(chain) == len(best) and chain[1] - chain[0] > best[1] - best[0]):
                best = chain
    return best


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    if mis > 8.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, max(mis, 0.5)


def calibrate(image, ylabels, xlabels, y_corner=None):
    ink = ink_mask(image)
    ax = axes_lines(ink)
    yt, xt = tick_candidates(ink, ax)
    ym = _majors([c for c in yt if c[0] < ax["xt"] - 15], len(ylabels))[::-1]   # bottom to top
    xm = _majors([c for c in xt if c[0] > ax["yr"] + 15], len(xlabels))
    if len(ym) != len(ylabels) or len(xm) != len(xlabels):
        raise RuntimeError(f"major ticks: y {ym} for {ylabels}; x {xm} for {xlabels}")
    ymarks = list(zip(ym, ylabels))
    if y_corner is not None:
        ymarks.append((ax["xc"], y_corner))
    xmarks = list(zip(xm, xlabels))
    ya, yb, ymis = _fit(ymarks)
    xa, xb, xmis = _fit(xmarks)
    return dict(ax=ax, ink=ink, xa=xa, xb=xb, xmis=xmis, ya=ya, yb=yb, ymis=ymis,
                xmarks=xmarks, ymarks=ymarks)


def to_col(cal, x):
    return (x - cal["xa"]) / cal["xb"]


def yval(cal, row):
    return cal["ya"] + cal["yb"] * row


def interior(cal, legend_box=None, tick_margin=60, above=None):
    """Ink inside the plot, without the axes, their inward ticks and the legend: either a box
    (c0, r0, c1, r1) or, with `above`, every row above that y value (a reader's choice of region
    holding the legend's sample lines and text, not data)."""
    ax = cal["ax"]
    m = cal["ink"].copy()
    m[:, : ax["yr"] + tick_margin] = False
    m[ax["xt"] - tick_margin:, :] = False
    m[: ax["top"], :] = False
    m[:, ax["right"]:] = False
    if legend_box is not None:
        boxes = legend_box if isinstance(legend_box[0], (list, tuple)) else [legend_box]
        for c0, r0, c1, r1 in boxes:
            m[r0:r1, c0:c1] = False
    if above is not None:
        r = int(round((above - cal["ya"]) / cal["yb"]))
        m[: max(r, 0), :] = False
    return m


def tracks(m, c):
    """Separate tracks of ink at column c: (r0, r1) row extents of the ink within +-W columns."""
    win = m[:, max(c - W, 0): c + W + 1].any(axis=1)
    rs = _runs(win)
    out = []
    for a, b in rs:
        if out and a - out[-1][1] <= GAP:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def _centre(m, c, a, b):
    nar = m[a:b, max(c - 2, 0): c + 3].any(axis=1)
    rows = np.flatnonzero(nar)
    if len(rows):
        return a + rows.min(), a + rows.max() + 1, True
    return a, b, False


def read_tracks(image, at, ylabels, xlabels, y_corner, legend, rules, above=None):
    """rules: list of (x0, x1, rank, n): for x0 <= x <= x1, take the track `rank` (0 = top,
    -1 = bottom, ...) where exactly n tracks are found (n None: any number). x outside every rule
    is not read."""
    cal = calibrate(image, ylabels, xlabels, y_corner)
    m = interior(cal, legend, above=above)
    out = []
    for x in at:
        x = float(x)
        rule = next((r for r in rules if r[0] - 1e-9 <= x <= r[1] + 1e-9), None)
        if rule is None:
            out.append({"x": x, "y": None, "note": "not read here: the curve is not separable from the others"})
            continue
        _, _, rank, n = rule
        col = to_col(cal, x)
        c = int(round(col))
        tr = tracks(m, c)
        if n is not None and len(tr) != n:
            out.append({"x": x, "y": None, "note": f"{len(tr)} tracks of ink in this column, expected {n}"})
            continue
        if not tr or not (-len(tr) <= rank < len(tr)):
            out.append({"x": x, "y": None, "note": f"no track {rank} among {len(tr)}"})
            continue
        a, b = tr[rank]
        a2, b2, narrow = _centre(m, c, a, b)
        if b2 - a2 > STEEP:
            out.append({"x": x, "y": None, "note": f"track {b2 - a2} px tall here: a near-vertical stretch"})
            continue
        row = (a2 + b2 - 1) / 2.0
        # local slope from the same track 2W px either side
        sl = 0.0
        nb = []
        for k in (c - 2 * W, c + 2 * W):
            tk = [t for t in tracks(m, k) if t[0] - 30 <= row <= t[1] + 30]
            if len(tk) == 1:
                nb.append((tk[0][0] + tk[0][1]) / 2.0)
        if len(nb) == 2:
            sl = abs(nb[1] - nb[0]) / (4.0 * W)
        e = (b - a) / 2.0 + BLUR + cal["ymis"] + sl * cal["xmis"]
        y, lo, hi = yval(cal, row), yval(cal, row + e), yval(cal, row - e)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [float(col), float(row)],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": f"track {rank} of {len(tr)}, {b - a} px tall in the window"
                            f"{'' if narrow else ' (no ink in the centre columns)'}"})
    return out


def load(path):
    """Import a sibling helper or the shared module by file name (the runner has no package)."""
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    spec = importlib.util.spec_from_file_location(os.path.splitext(path)[0], p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
