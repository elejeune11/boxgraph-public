"""Shared reading code for Fig. 5(g) (PDF p. 13): the (k, d) bifurcation diagram.

The panel is vector art: a black horizontal axis (k = -kappa_b, d = 0) and a black vertical axis
(d, at k = 0), short black ticks standing above the horizontal axis (k = 1 ... 8) and right of the
vertical axis (every 0.25 in d, labelled 0.5, 1, 1.5, 2 at every second tick), twelve curves each
drawn in one flat colour (six blue solid lines, large-bending model, and six red dashed lines,
classical model, one per w; darker is smaller w), and a grey vertical line labelled |eta| = 1.

Calibration, all from the image (black = every channel below 60):
  the horizontal axis is the band of rows holding the longest black runs, the vertical axis the
  band of columns holding the longest black column runs;
  x ticks are columns where black runs on at least 15 px straight up from the axis band, away from
  the vertical axis and from the arrowhead at the right end; the eight found are matched in order
  to the printed labels 1 ... 8, and the vertical axis column is checked against k = 0;
  y ticks are rows where black runs on at least 15 px straight right of the vertical axis band,
  away from the horizontal axis and from the arrowhead at the top; they are numbered by their
  distance from the horizontal axis in units of the median gap, and tick n is n * 0.25, the step
  read from the printed labels 0.5, 1, 1.5, 2 on ticks 2, 4, 6, 8.
  Both axes are fitted by straight lines through their ticks; the largest misfit is reported.

A curve: pixels within 20 (RGB distance) of its colour (sampled from the rendered page), opened
by a 3 x 3 square, which drops the one-pixel anti-aliased edges of a darker curve whose blend
with white passes through a paler curve's colour. The stroke width w is the median run length in
columns holding a single run where the curve is nearly flat (its centre moves at most 3 px over
10 columns, without a kink).

Each reading follows the lower branch (the branch that starts at d near 0.23 at k = 0), traced
column by column from the first k read: the trace starts at the lowest run of the colour in the
first column, at or after the first k, that has a run in the band 0.2 < d < 0.5 (where every lower
branch lies for k < 3; the upper branches and loops of the pale curves lie above d = 1.3 there);
in each next column the run whose centre is nearest the line fitted through the last 40 traced
columns (the last traced centre while fewer than 15, or spanning under 20 columns), within
max(2 w, 12 px), is taken; a column without one (a gap between dashes, or the curve
hidden under another curve) is skipped. The line is fitted only through traced columns within the last 100. The trace stops
where the curve turns steep (|slope| above 3 px per column: the fold). After 150 columns without a
run (the curve hidden under others) it is taken up again at the lowest run of the colour between
the last traced d and 0.5 above it: the lower branch only rises before its fold, and the middle
and upper branches of the S-shaped and looped curves lie higher than that.
At each k read: a traced run in that column gives its centre +- 2 px if it is as long as the
stroke (within 4 px of h = w sqrt(1 + slope^2)); a shorter run (partly hidden under another curve)
gives every centre whose stroke covers it, widened by 2 px; a longer run (another curve touching
it) gives the run less half a stroke on each side, widened by 2 px. A column without a traced run
gives the parabola through the traced centres within 40 columns on each side, +- (w + 4) px, if
there are traced runs on both sides; otherwise no value. Every interval is widened by the y
misfit + 1 px and |slope| times (the x misfit + 0.5 px). Past the end of the trace there is no
value.

The grey line: pixels within 20 of its colour; at each d, the run of grey in the row of that d
nearest the line's median column; its centre is k, +- 2 px widened by the x misfit + 1 px.
"""

import numpy as np
from scipy import ndimage


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    return max((b - a for a, b in _runs(v)), default=0)


def _band(lengths):
    lengths = np.asarray(lengths)
    m = int(np.argmax(lengths))
    idx = [i for i in np.flatnonzero(lengths > 0.8 * lengths.max()) if abs(i - m) < 15]
    return min(idx), max(idx)


def _centres(flags):
    return [(a + b - 1) / 2.0 for a, b in _runs(flags)]


def _fit(pix, vals):
    p, v = np.asarray(pix, float), np.asarray(vals, float)
    k, m = np.polyfit(p, v, 1)
    return m, k, float(np.max(np.abs((v - m) / k - p)))


def calibrate(image):
    black = (image[..., :3] < 60).all(axis=2)
    H, W = black.shape
    r0, r1 = _band([_longest(black[i]) for i in range(H)])
    c0, c1 = _band([_longest(black[:, j]) for j in range(W)])
    # x ticks: black straight up from the axis band
    up = np.zeros(W, int)
    for j in range(W):
        n, i = 0, r0 - 1
        while i >= 0 and black[i, j]:
            n += 1
            i -= 1
        up[j] = n
    flag = up >= 15
    flag[: c1 + 30] = False
    right_end = int(np.flatnonzero(black[(r0 + r1) // 2]).max())
    flag[right_end - 80:] = False
    xt = _centres(flag)
    labels = [1, 2, 3, 4, 5, 6, 7, 8]
    if len(xt) != len(labels):
        raise ValueError(f"x axis: found ticks at {xt}, expected {len(labels)}")
    xa, xb, xm = _fit(xt, labels)
    x0_off = abs((c0 + c1) / 2.0 - (0 - xa) / xb)
    # y ticks: black straight right of the axis band
    rt = np.zeros(H, int)
    for i in range(H):
        n, j = 0, c1 + 1
        while j < W and black[i, j]:
            n += 1
            j += 1
        rt[i] = n
    flag = rt >= 15
    flag[r0 - 30:] = False
    top = int(np.flatnonzero(black[:, (c0 + c1) // 2]).min())
    flag[: top + 80] = False
    yt = _centres(flag)
    axis_row = (r0 + r1) / 2.0
    sp = float(np.median(np.diff(sorted(yt))))
    ns = [int(round((axis_row - t) / sp)) for t in yt]
    if len(set(ns)) != len(ns) or any(abs((axis_row - t) / sp - n) > 0.1 for t, n in zip(yt, ns)):
        raise ValueError(f"y axis: ticks at {yt} are not evenly spaced from the axis row {axis_row}")
    y_labels = {2: 0.5, 4: 1.0, 6: 1.5, 8: 2.0}
    steps = {lab / n for n, lab in y_labels.items()}
    if len(steps) != 1 or not all(n in ns for n in y_labels):
        raise ValueError(f"y axis: ticks {ns} do not carry the labels {y_labels}")
    step = steps.pop()
    ya, yb, ym = _fit(yt, [n * step for n in ns])
    y0_off = abs(axis_row - (0 - ya) / yb)
    return dict(x=(xa, xb, xm), y=(ya, yb, ym), x0_off=x0_off, y0_off=y0_off, nx=len(xt), ny=len(yt))


def mask(image, color, tol=20.0):
    d = np.sqrt(((image[..., :3].astype(float) - np.array(color, float)) ** 2).sum(axis=2))
    return ndimage.binary_opening(d < tol, structure=np.ones((3, 3)))


def _cal_note(cal):
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    return (f"{cal['nx']} x ticks, {cal['ny']} y ticks; x misfit {xm:.1f} px, y misfit {ym:.1f} px; "
            f"axis offsets from 0: x {cal['x0_off']:.1f} px, y {cal['y0_off']:.1f} px")


def read_curve(image, at, color):
    cal = calibrate(image)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    m = mask(image, color)
    cols = {c: _runs(m[:, c]) for c in range(m.shape[1])}
    # stroke width: the median run in columns with a single run where the curve is nearly flat
    # (its centre moves less than 0.3 px per column over 5 columns on both sides)
    single = {c: r[0] for c, r in cols.items() if len(r) == 1}
    flat = []
    for c, (a, b) in single.items():
        if c - 5 in single and c + 5 in single:
            ctr = [(sum(single[k]) - 1) / 2.0 for k in (c - 5, c, c + 5)]
            if abs(ctr[2] - ctr[0]) <= 3.0 and abs(ctr[1] - (ctr[0] + ctr[2]) / 2.0) <= 1.0:
                flat.append(b - a)
    w = float(np.median(flat)) if flat else 8.0
    W = m.shape[1]

    # trace the lower branch
    c_start = int(round((min(at) - xa) / xb)) if at else 0
    r_top, r_bot = (0.5 - ya) / yb, (0.2 - ya) / yb
    trace = {}
    c0 = None
    for c in range(max(c_start, 0), W):
        cand = [(a, b) for a, b in cols[c] if r_top <= (a + b - 1) / 2.0 <= r_bot]
        if cand:
            c0 = c
            trace[c] = max(cand)
            break
    end = c0 if c0 is not None else -1
    if c0 is not None:
        tol = max(2 * w, 12.0)
        miss = 0
        for c in range(c0 + 1, W):
            if miss > 150:
                # lost under other curves: take it up again at the lowest run between the last
                # traced d and 0.5 above it (the lower branch only rises before its fold; the middle
                # and upper branches lie higher)
                last = (sum(trace[max(trace)]) - 1) / 2.0
                d_last = ya + yb * last
                r_hi = (d_last + 0.5 - ya) / yb
                cand = [(a, b) for a, b in cols[c] if r_hi <= (a + b - 1) / 2.0 <= last + 2]
                if cand:
                    trace[c] = max(cand)
                    end = c
                    miss = 0
                continue
            recent = [(k, (sum(trace[k]) - 1) / 2.0) for k in sorted(trace)[-40:] if k >= c - 100]
            kk = np.array([p[0] for p in recent], float)
            yy = np.array([p[1] for p in recent], float)
            if not recent:
                pred = (sum(trace[max(trace)]) - 1) / 2.0
            elif len(recent) >= 15 and np.ptp(kk) >= 20:
                p1 = np.polyfit(kk, yy, 1)
                pred, sl = float(np.polyval(p1, c)), float(p1[0])
                if abs(sl) > 3.0:
                    break
            else:
                pred = float(yy[-1])
            best = None
            for a, b in cols[c]:
                dd = abs((a + b - 1) / 2.0 - pred)
                if dd <= tol and (best is None or dd < best[0]):
                    best = (dd, a, b)
            if best is None:
                miss += 1
                continue
            miss = 0
            trace[c] = (best[1], best[2])
            end = c

    def fit_near(c):
        pts = [(k, (a + b - 1) / 2.0) for k, (a, b) in trace.items() if abs(k - c) <= 40 and k != c]
        left = [p for p in pts if p[0] < c]
        right = [p for p in pts if p[0] > c]
        if len(pts) < 6 or not left or not right:
            return None
        kk = np.array([p[0] for p in pts], float)
        yy = np.array([p[1] for p in pts], float)
        poly = np.polyfit(kk, yy, 2)
        return float(np.polyval(poly, c)), float(np.polyval(np.polyder(poly), c))

    res = []
    for x in at:
        cx = (x - xa) / xb
        c = int(round(cx))
        if c0 is None or c < c0 or c > end:
            res.append({"x": x, "y": None, "note": "outside the traced lower branch (hidden, or past its fold)"})
            continue
        fn = fit_near(c)
        if fn is None and c not in trace:
            res.append({"x": x, "y": None, "note": "curve hidden here and not traced on both sides"})
            continue
        pred, slope = fn if fn is not None else ((sum(trace[c]) - 1) / 2.0, 0.0)
        h = w * np.sqrt(1 + slope * slope)
        best = (0.0, trace[c][0], trace[c][1] - 1) if c in trace else None
        if best is None:
            yc, lo, hi = pred, pred - (w + 4), pred + (w + 4)
            state = "no run here (dash gap or hidden); predicted from the traced columns on both sides"
        else:
            _, a, b = best
            if b - a < h - 4:
                lo, hi = b - h / 2.0 - 2.0, a + h / 2.0 + 2.0
                state = "partly hidden under another curve"
            elif b - a <= h + 4:
                lo, hi = (a + b) / 2.0 - 2.0, (a + b) / 2.0 + 2.0
                state = "line"
            else:
                lo, hi = a + h / 2.0 - 2.0, b - h / 2.0 + 2.0
                if hi < lo:
                    lo, hi = (a + b) / 2.0 - 2.0, (a + b) / 2.0 + 2.0
                state = "run longer than the stroke (another curve touching it)"
            yc = (lo + hi) / 2.0
        pad = ym + 1.0 + abs(slope) * (xm + 0.5)
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
        res.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cx), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; stroke {w:.0f} px; {_cal_note(cal)}"})
    return res


def read_vertical_line(image, at, color):
    """The grey line: x of the reading is d (rows), y is k (columns)."""
    cal = calibrate(image)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    m = mask(image, color)
    colsum = m.sum(axis=0)
    cmed = float(np.argmax(colsum))
    res = []
    for d in at:
        r = int(round((d - ya) / yb))
        runs = [(a, b) for a, b in _runs(m[r]) if abs((a + b - 1) / 2.0 - cmed) < 30]
        if not runs:
            res.append({"x": d, "y": None, "note": "the grey line is broken here (label)"})
            continue
        a, b = min(runs, key=lambda q: abs((q[0] + q[1] - 1) / 2.0 - cmed))
        cc = (a + b - 1) / 2.0
        lo, hi = cc - 2.0 - xm - 1.0, cc + 2.0 + xm + 1.0
        res.append({"x": d, "y": float(xa + xb * cc), "lo": float(xa + xb * lo), "hi": float(xa + xb * hi),
                    "px": [float(cc), float(r)],
                    "note": f"grey run {b - a} px wide; {_cal_note(cal)}"})
    return res
