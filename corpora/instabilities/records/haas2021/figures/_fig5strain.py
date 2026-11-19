"""Shared reading code for the strain panels of Fig. 5 (PDF p. 13): (b), (e) eps E_s and (c), (f) K_s
against s, each with a blue solid line (0, 0, 255; large-bending model, Eq. 63), a red dashed line
(255, 0, 0; classical model, Eq. 67) drawn over it, and a grey band (204, 204, 204) marking the bend
region s0 - w < s < s0. Colours sampled from the rendered page.

Calibration, all from the image (black = every channel below 60):
  the horizontal axis (y = 0) is the band of rows holding the longest black runs, the vertical
  axis (s = 0) the band of columns holding the longest black column runs;
  x ticks are columns right of the vertical axis holding a black run of at least 15 px within
  10-100 px above or below the axis band (the part next to the axis may lie under a curve that runs
  along s), at least 15 px inside the axis's extent (first to last black column of the axis
  band), of the common tick
  width (within 4 px of the median: the arrowhead is wider); ticks stand every 0.5 in s (labels 1, 2, 3
  on every second one): each tick is numbered by its distance from the vertical axis in units of
  the smallest gap between found ticks, which must be one tick spacing (checked: every tick
  within 0.1 spacing of a whole number) and its value is that number times 0.5, the step read off
  the labels;
  y ticks are rows where black runs on at least 15 px straight right of the vertical axis band,
  away from the horizontal axis and from the arrowhead at the top (150 px); they are numbered
  likewise from the horizontal axis and given the values of the spec "y_step" (0.1 for eps E_s,
  read from the labels 0.1, -0.1, -0.2; 2.5 for K_s, read from the label 5 on the second tick).
  Both axes are fitted by straight lines through their ticks; the largest misfit is reported.

A curve: pixels within 30 (RGB distance) of its colour, opened by a 3 x 3 square. For the blue
line, red pixels and the purple blends of red and blue (red or blue channel above 150, green
below 120) count as blue where they are contiguous with blue in a column (the red dashed line is
drawn over it and is narrower), so a blue stroke split by a red dash is one run. The stroke
width w is the median run length in columns holding a single run where the curve is nearly flat.
At each s: the curve is followed outward from the column, 40 columns to the left and then 40 to the
right, each step taking the run nearest the last one (within 3 w), starting from the previous
reading's centre; when that finds fewer than 8 centres or none on one side (after a jump of the
curve), it starts instead from the first column holding a single run; a parabola through the
centres followed is the prediction; the run nearest the prediction within h = w sqrt(1 + slope^2) is
taken. A run as long as the stroke (within 6 px) gives its centre +- 3 px; a shorter one (partly
hidden) gives every centre whose stroke covers it, widened by 3 px; a longer one (another stroke
touching it) gives the run less half a stroke on each side, widened by 3 px; no run (a dash gap, or
hidden) gives the prediction +- (w + 6) px. Intervals are widened by the y misfit + 1 px and
|slope| times (the x misfit + 0.5 px).

The grey band: in the row of a given y, the runs of grey; the band's left edge is where the first
grey run of the band starts, its right edge where the last one ends, each +- 1.5 px widened by the
x misfit; an edge with a curve on it (the pixel outside it not white) gives no value.
"""

import numpy as np
from scipy import ndimage

BLUE, RED, GREY = (0, 0, 255), (255, 0, 0), (204, 204, 204)


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    return max((b - a for a, b in _runs(v)), default=0)


def _band(lengths):
    lengths = np.asarray(lengths)
    m = int(np.argmax(lengths))
    idx = [i for i in np.flatnonzero(lengths > 0.8 * lengths.max()) if abs(i - m) < 20]
    return min(idx), max(idx)


def _centres(flags):
    return [(a + b - 1) / 2.0 for a, b in _runs(flags)]


def _fit(pix, vals):
    p, v = np.asarray(pix, float), np.asarray(vals, float)
    k, m = np.polyfit(p, v, 1)
    return m, k, float(np.max(np.abs((v - m) / k - p)))


def _count(black, i0, j0, di, dj):
    n, i, j = 0, i0, j0
    H, W = black.shape
    while 0 <= i < H and 0 <= j < W and black[i, j]:
        n += 1
        i += di
        j += dj
    return n


def _number(ticks, origin, what):
    """Number ticks by their distance from the origin in units of the smallest gap between them."""
    gap = float(np.min(np.diff(sorted(ticks))))
    ns = [(t - origin) / gap for t in ticks]
    if any(abs(n - round(n)) > 0.1 for n in ns) or len({round(n) for n in ns}) != len(ns):
        raise ValueError(f"{what}: ticks {ticks} are not whole tick spacings from the axis {origin}")
    return [int(round(n)) for n in ns]


def calibrate(image, y_step):
    black = (image[..., :3] < 60).all(axis=2)
    H, W = black.shape
    r0, r1 = _band([_longest(black[i]) for i in range(H)])
    c0, c1 = _band([_longest(black[:, j]) for j in range(W)])
    flag = np.array([max(_longest(black[max(r0 - 100, 0):r0 - 10, j]), _longest(black[r1 + 11:r1 + 101, j])) >= 15
                     for j in range(W)])
    flag[: c1 + 31] = False
    # the axis's extent: first to last black column in the axis band (a curve may cover parts of it)
    cols_black = np.flatnonzero(black[r0:r1 + 1].any(axis=0))
    ax0, ax1 = int(cols_black.min()), int(cols_black.max())
    xt = []
    runs = [(a, b) for a, b in _runs(flag) if a - 15 >= ax0 and b + 15 <= ax1]
    if runs:
        med = float(np.median([b - a for a, b in runs]))
        xt = [(a + b - 1) / 2.0 for a, b in runs if abs((b - a) - med) <= 4]
    nx = _number(xt, (c0 + c1) / 2.0, "x axis")
    xa, xb, xm = _fit(xt, [n * 0.5 for n in nx])
    x0_off = abs((c0 + c1) / 2.0 - (0 - xa) / xb)
    flag = np.array([_count(black, i, c1 + 1, 0, 1) >= 15 for i in range(H)])
    flag[r0 - 30:r1 + 31] = False
    top = int(np.flatnonzero(black[:, (c0 + c1) // 2]).min())
    flag[: top + 150] = False
    yt = _centres(flag)
    ny = _number(yt, (r0 + r1) / 2.0, "y axis")
    ya, yb, ym = _fit(yt, [-n * y_step for n in ny])
    y0_off = abs((r0 + r1) / 2.0 - (0 - ya) / yb)
    return dict(x=(xa, xb, xm), y=(ya, yb, ym), x0_off=x0_off, y0_off=y0_off, xt=nx, yt=ny)


def _near(image, color, tol=30.0):
    return np.sqrt(((image[..., :3].astype(float) - np.array(color, float)) ** 2).sum(axis=2)) < tol


def _note(cal):
    return (f"x ticks {sorted(cal['xt'])} x 0.5, y ticks {sorted(cal['yt'])}; x misfit {cal['x'][2]:.1f} px, "
            f"y misfit {cal['y'][2]:.1f} px; axis offsets from 0: x {cal['x0_off']:.1f} px, y {cal['y0_off']:.1f} px")


def read_curve(image, at, color, y_step):
    cal = calibrate(image, y_step)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    m = ndimage.binary_opening(_near(image, color), structure=np.ones((3, 3)))
    if color == BLUE:
        im = image[..., :3].astype(int)
        coloured = (np.maximum(im[..., 0], im[..., 2]) > 150) & (im[..., 1] < 120)
        both = m | coloured
        merged = np.zeros_like(m)
        for c in range(m.shape[1]):
            for a, b in _runs(both[:, c]):
                if m[a:b, c].any():
                    merged[a:b, c] = True
        m = merged
    cols = {c: _runs(m[:, c]) for c in range(m.shape[1])}
    single = {c: r[0] for c, r in cols.items() if len(r) == 1}
    flat = []
    for c, (a, b) in single.items():
        if c - 8 in single and c + 8 in single:
            ctr = [(sum(single[k]) - 1) / 2.0 for k in (c - 8, c, c + 8)]
            if abs(ctr[2] - ctr[0]) <= 3.0 and abs(ctr[1] - (ctr[0] + ctr[2]) / 2.0) <= 1.0:
                flat.append(b - a)
    w = float(np.median(flat)) if flat else 20.0

    def follow(c0, c1, ref):
        pts, cur = [], ref
        rng = range(c0, c1) if c1 > c0 else range(c0, c1, -1)
        for k in rng:
            rr = cols.get(k, [])
            if not rr:
                continue
            if cur is None:
                if len(rr) != 1:
                    continue
                a, b = rr[0]
            else:
                a, b = min(rr, key=lambda q: abs((q[0] + q[1] - 1) / 2.0 - cur))
                if abs((a + b - 1) / 2.0 - cur) > 3 * w:
                    continue
            cur = (a + b - 1) / 2.0
            pts.append((k, cur))
        return pts

    res = []
    prev = None
    for x in at:
        cx = (x - xa) / xb
        c = int(round(cx))
        nb = []
        for ref in ([prev[1]] if prev is not None else []) + [None]:
            left = follow(c - 1, c - 41, ref)
            right = follow(c + 1, c + 41, left[0][1] if left else ref)
            nb = left + right
            if len(nb) >= 8 and left and right:
                break
        if len(nb) < 8:
            res.append({"x": x, "y": None, "note": "curve not found near this column"})
            continue
        ks = np.array([p[0] for p in nb], float)
        ys = np.array([p[1] for p in nb], float)
        poly = np.polyfit(ks, ys, 2)
        pred = float(np.polyval(poly, c))
        slope = float(np.polyval(np.polyder(poly), c))
        h = w * np.sqrt(1 + slope * slope)
        best = None
        for a, b in cols.get(c, []):
            dd = 0.0 if a <= pred <= b - 1 else min(abs(pred - a), abs(pred - (b - 1)))
            if dd <= h / 2.0 + 3 and (best is None or dd < best[0]):
                best = (dd, a, b - 1)
        if best is None:
            yc, lo, hi = pred, pred - (w + 6), pred + (w + 6)
            state = "no run here (dash gap or hidden); predicted from neighbouring columns"
        else:
            _, a, b = best
            if b - a < h - 6:
                lo, hi = b - h / 2.0 - 3.0, a + h / 2.0 + 3.0
                state = "partly hidden"
            elif b - a <= h + 6:
                lo, hi = (a + b) / 2.0 - 3.0, (a + b) / 2.0 + 3.0
                state = "line"
            else:
                lo, hi = a + h / 2.0 - 3.0, b - h / 2.0 + 3.0
                if hi < lo:
                    lo, hi = (a + b) / 2.0 - 3.0, (a + b) / 2.0 + 3.0
                state = "run longer than the stroke"
            yc = (lo + hi) / 2.0
        prev = (c, yc, slope)
        pad = ym + 1.0 + abs(slope) * (xm + 0.5)
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
        res.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cx), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; stroke {w:.0f} px; {_note(cal)}"})
    return res


def read_band_edge(image, at, side, y_step):
    """The grey band: x of the reading is the y level (rows), y is s of its left or right edge."""
    cal = calibrate(image, y_step)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    g = _near(image, GREY, 10)
    white = (image[..., :3] > 245).all(axis=2)
    res = []
    for lev in at:
        r = int(round((lev - ya) / yb))
        runs = [(a, b) for a, b in _runs(g[r]) if b - a >= 20]
        if not runs:
            res.append({"x": lev, "y": None, "note": "no grey band in this row"})
            continue
        if side == "left":
            edge = runs[0][0]
            ok = edge - 1 >= 0 and white[r, edge - 2:edge].all()
            pos = edge - 0.5
        else:
            edge = runs[-1][1]
            ok = edge + 2 <= g.shape[1] and white[r, edge:edge + 2].all()
            pos = edge - 0.5
        if not ok:
            res.append({"x": lev, "y": None, "note": "a curve lies on the band's edge in this row"})
            continue
        half = 1.5 + xm
        res.append({"x": lev, "y": float(xa + xb * pos), "lo": float(xa + xb * (pos - half)),
                    "hi": float(xa + xb * (pos + half)), "px": [float(pos), float(r)],
                    "note": f"{side} edge of the grey band; {_note(cal)}"})
    return res
