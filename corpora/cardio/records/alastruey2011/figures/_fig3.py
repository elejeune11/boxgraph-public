"""Shared reading code for Fig. 3 (PDF p. 6): P and Q against t at four midpoints.

Each panel is vector art in black ink on white, with three curves told apart by their stroke
(measured from the legend samples at 1200 dpi):
  exp   thick solid line, 14 px wide
  visc  thick dashed line, 14 px wide, dashes about 32 px long with 33 px gaps
  elas  thin solid line, 5 px wide
plus a frame (9 px), inward tick marks and dotted grid lines at the labelled ticks, and a legend box.

Calibration, all from the image: the frame is found as the longest dark rows and columns; the tick
marks are the short dark runs (12-40 px) that stand inward from the bottom frame line (x) and from
the left frame line (y), kept only where a dotted grid line (at least 20 dots) runs across the plot
from them. They are matched
in order to the printed labels passed in the panel's spec (only labels whose tick lies inside the
frame; a label on the frame itself has no tick to find) and fitted by a straight line; the largest
tick misfit is reported and added to every interval.

Separating the curves:
  thick ink = an opening of the ink with a disk 11 px across (removes the thin line, grid and text);
  dashes are the thick components smaller than 70 px in both directions; the rest is the exp line,
  possibly with dashes fused to it where the two curves touch.
  thin ink = ink not within 3 px of thick ink, with the grid lines, legend and frame removed.
Each curve is traced column by column from the left edge, the candidate run nearest a linear
prediction from the previous 12 columns being kept:
  exp:  runs of the large thick components.
  visc: dash runs; across a dash gap (up to 45 columns without a dash near the prediction) the
        prediction is kept; beyond that the dashes are fused with the exp line and the visc curve is
        taken inside the fused thick run.
  elas: thin runs, followed by pixel connectivity first and by prediction across breaks; where none
        is near, the thin line is hidden under a thick line, and its interval spans every thick run
        within 40 px of the prediction (it may lie under either the exp or the visc line).
A curve not found near its prediction (e.g. clipped by the frame) is looked for ever more widely
until it is found again; the columns in between are unreadable and left out of the reading's `at`.
Intervals (95%): the line's centre lies inside the run that holds it, at least half the line's
vertical thickness (w * sqrt(1 + slope^2)) from each end, widened by 2 px; a fused or hidden run gives
the whole run less that half thickness; a dash gap gives the prediction +- 8 px; plus the calibration
misfit in pixels and 1 px. A reading whose interval is wider than max_px (default 120 px) is
reported as unreadable.
"""

import numpy as np
from scipy import ndimage

W_THICK, W_THIN = 14.0, 5.0


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    r = _runs(v)
    return max(r, key=lambda x: x[1] - x[0]) if r else (0, 0)


def frame(dark):
    H, W = dark.shape
    rl = np.array([(lambda r: r[1] - r[0])(_longest(dark[i])) for i in range(H)])
    cl = np.array([(lambda r: r[1] - r[0])(_longest(dark[:, j])) for j in range(W)])
    rows = np.flatnonzero(rl > 0.6 * rl.max())
    cols = np.flatnonzero(cl > 0.6 * cl.max())
    top_rows = rows[rows < rows.min() + 20]
    bot_rows = rows[rows > rows.max() - 20]
    left_cols = cols[cols < cols.min() + 20]
    right_cols = cols[cols > cols.max() - 20]
    return {"top": int(top_rows.max()) + 1, "bottom": int(bot_rows.min()),
            "left": int(left_cols.max()) + 1, "right": int(right_cols.min())}


def _tick_groups(lengths, lo=12, hi=80):
    pos = [i for i, n in enumerate(lengths) if lo <= n <= hi]
    groups, cur = [], []
    for p in pos + [None]:
        if cur and (p is None or p != cur[-1] + 1):
            if len(cur) <= 12:
                groups.append((cur[0] + cur[-1]) / 2.0 + 0.5)
            cur = []
        if p is not None:
            cur.append(p)
    return groups


def _inward(dark_line):
    n = 0
    while n < len(dark_line) and dark_line[n]:
        n += 1
    return n


def ticks(dark, fr):
    t, b, l, r = fr["top"], fr["bottom"], fr["left"], fr["right"]
    xb = [_inward(dark[t:b, c][::-1]) for c in range(l, r)]
    xt = [_inward(dark[t:b, c]) for c in range(l, r)]
    yl = [_inward(dark[rr, l:r]) for rr in range(t, b)]
    yr = [_inward(dark[rr, l:r][::-1]) for rr in range(t, b)]

    def gridded(lengths, line_of, off):
        """Tick marks on one frame side whose dotted grid line crosses the plot."""
        out = []
        for p in _tick_groups(lengths, 12, 40):
            k = int(round(off + p - 0.5))
            dots = max(sum(1 for a, bb in _runs(line_of(j)) if bb - a <= 12) for j in (k - 1, k, k + 1))
            if dots >= 20:
                out.append(off + p)
        return out

    return (gridded(xb, lambda j: dark[t:b, j], l), gridded(yl, lambda j: dark[j, l:r], t))


def _fit(pix, labels, what):
    if len(pix) != len(labels):
        raise ValueError(f"{what}: found {len(pix)} ticks at {pix}, expected {len(labels)} for {labels}")
    p, v = np.array(pix, float), np.array(labels, float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - a) / b - p)))
    return a, b, mis


def _fit_gaps(pix, labels, what):
    """Like _fit, for evenly spaced labels when interior ticks are hidden: the first and last ticks
    found are the first and last labels, and every tick found must fall on the even spacing between
    them (within 5 px; the fit's misfit then says how far)."""
    if len(pix) == len(labels):
        return _fit(pix, labels, what)
    n = len(labels) - 1
    step = (pix[-1] - pix[0]) / n
    idx = [(p - pix[0]) / step for p in pix]
    if len(pix) < 3 or any(abs(i - round(i)) * step > 5 for i in idx):
        raise ValueError(f"{what}: ticks at {pix} do not fall on an even spacing for {labels}")
    return _fit(pix, [labels[int(round(i))] for i in idx], what)


def _legend(dark, fr):
    """Rectangle of the legend box: long dark rows and columns strictly inside the frame."""
    t, b, l, r = fr["top"] + 3, fr["bottom"] - 3, fr["left"] + 3, fr["right"] - 3
    sub = dark[t:b, l:r]
    H, W = sub.shape
    runs = {i: _longest(sub[i]) for i in range(H)}
    rows = [i for i in range(H) if runs[i][1] - runs[i][0] > 0.15 * W]
    if not rows:
        return None
    ca, cb = runs[rows[0]]
    same = [i for i in rows if abs(runs[i][0] - ca) <= 5 and abs(runs[i][1] - cb) <= 5]
    return (t + min(same) - 6, t + max(same) + 6, l + ca - 6, l + cb + 6)


def masks(image, spec):
    g = image[..., :3].astype(float).mean(axis=2)
    dark = g < 128
    fr = frame(dark)
    xt, yt = ticks(dark, fr)
    xa, xb, xm = _fit(xt, spec["x"], "x axis")
    ya, yb, ym = _fit(yt, spec["y"], "y axis")
    inside = np.zeros_like(dark)
    inside[fr["top"] + 2:fr["bottom"] - 2, fr["left"] + 2:fr["right"] - 2] = True
    leg = _legend(dark, fr)
    if leg is not None:
        inside[max(leg[0], 0):leg[1], max(leg[2], 0):leg[3]] = False
    ink = dark & inside
    yy, xx = np.mgrid[-5:6, -5:6]
    disk = (xx * xx + yy * yy) <= 5.5 * 5.5
    thick = ndimage.binary_opening(ink, structure=disk)
    lab, n = ndimage.label(thick, structure=np.ones((3, 3)))
    sl = ndimage.find_objects(lab)
    small = np.zeros(n + 1, bool)
    for k, s in enumerate(sl, start=1):
        if s[0].stop - s[0].start < 70 and s[1].stop - s[1].start < 70:
            small[k] = True
    dash = small[lab] & thick
    big = thick & ~dash
    thin = ink & ~ndimage.binary_dilation(thick, iterations=3)
    # tick marks at the labelled ticks (the grid dots go with the small specks below)
    b, l = fr["bottom"], fr["left"]
    for c in xt:
        thin[b - 45:b, int(round(c)) - 4:int(round(c)) + 5] = False
    for r in yt:
        thin[int(round(r)) - 4:int(round(r)) + 5, l:l + 45] = False
    # specks of the dotted grid left between lines: keep thin components of some size
    tl, tn = ndimage.label(thin, structure=np.ones((3, 3)))
    if tn:
        sizes = ndimage.sum(thin, tl, index=np.arange(1, tn + 1))
        keep = np.concatenate([[False], sizes >= 25])
        thin = keep[tl]
    return {"frame": fr, "x": (xa, xb, xm), "y": (ya, yb, ym), "thick": thick, "dash": dash, "big": big,
            "thin": thin, "legend": leg}


def _col_runs(mask, c):
    return [(a, b) for a, b in _runs(mask[:, c])]


def _nearest(runs, pred):
    best, bd = None, None
    for a, b in runs:
        d = 0.0 if a <= pred <= b - 1 else min(abs(pred - a), abs(pred - (b - 1)))
        if bd is None or d < bd:
            best, bd = (a, b), d
    return best, bd


def _choose(runs, prev, pred, tl):
    """The run touching the previous column's run (8-connected); among several, or when none
    touches, the run nearest the prediction within tl. Returns (run, distance) or (None, None)."""
    if not runs:
        return None, None
    if prev is not None:
        touch = [r for r in runs if r[0] <= prev[1] and r[1] >= prev[0]]
        if len(touch) == 1:
            return touch[0], 0.0
        if touch and pred is not None:
            return _nearest(touch, pred)
    if pred is None:
        return None, None
    run, d = _nearest(runs, pred)
    return (run, d) if d <= tl else (None, None)


def _predict(hist, col):
    if not hist:
        return None
    pts = hist[-12:]
    if len(pts) < 3:
        return pts[-1][1]
    c = np.array([p[0] for p in pts], float)
    y = np.array([p[1] for p in pts], float)
    k, m = np.polyfit(c, y, 1)
    return k * col + m


def trace(m, curve, tol=30.0):
    """Per column: (run, state) or (run, "hidden", row) or (row, "gap" | "lost")."""
    fr = m["frame"]
    c0, c1 = fr["left"] + 4, fr["right"] - 4
    out = {}
    hist = []
    prev = None
    gap = 0
    lost = 0
    hidden = 0
    for c in range(c0, c1):
        pred = _predict(hist, c)
        if pred is not None:
            pred = min(max(pred, fr["top"]), fr["bottom"])
        tl = tol + 4.0 * lost + 2.0 * hidden  # a curve lost (e.g. clipped by the frame) is looked for ever more widely
        first = _col_runs(m["big" if curve == "exp" else ("dash" if curve == "visc" else "thin")], c)
        if pred is None and prev is None:
            runs = first or _col_runs(m["thick"], c)
            if not runs:
                continue
            run = max(runs, key=lambda x: x[1] - x[0])
            out[c] = (run, "line" if first else ("fused" if curve == "visc" else "hidden"))
            hist.append((c, (run[0] + run[1] - 1) / 2.0))
            prev = run if first else None
            continue
        run, d = _choose(first, prev, pred, tl)
        if run is not None:
            gap = lost = hidden = 0
            prev = run
            out[c] = (run, "line")
            hist.append((c, (run[0] + run[1] - 1) / 2.0))
            continue
        prev = None
        if curve == "visc":
            gap += 1
            if gap <= 45:
                out[c] = (pred, "gap")
                continue
        if curve in ("visc", "elas"):
            run, d = _choose(_col_runs(m["thick"], c), None, pred, tol)
            if run is not None:
                lost = 0
                if curve == "visc":
                    out[c] = (run, "fused")
                    hist.append((c, (run[0] + run[1] - 1) / 2.0))
                else:
                    y = min(max(pred, run[0]), run[1] - 1)
                    out[c] = (run, "hidden", y)
                    hidden += 1
                    if hidden > 40:  # a long occlusion: the thin line runs along the thick one
                        hist.append((c, y))
                continue
        lost += 1
        out[c] = (pred, "lost")
    return out


def trace_visc(m, max_gap=50):
    """The dashed curve, read from the dashes themselves (thick runs other than the traced exp
    line's run in the column):
      a column crossed by dashes: their run (several runs of one steep stretch, closer than 60 px,
        are taken together);
      a column between two dashes at most max_gap columns apart: the straight line joining the
        centres of the two facing dash ends ("gap");
      otherwise the dashes are fused with the exp line (no free dash drawn there), and the visc
        curve is taken inside the exp line's run in that column ("fused").
    """
    fr = m["frame"]
    c0, c1 = fr["left"] + 4, fr["right"] - 4
    exp = trace(m, "exp")
    dash_at = {}
    for c in range(c0, c1):
        # dash ink: thick runs other than the exp line's run (a dash fused to the exp line at one
        # end still stands apart from it in the columns where the two do not overlap)
        e = exp.get(c)
        er = e[0] if e is not None and e[1] == "line" else None
        runs = [r for r in _col_runs(m["thick"], c) if r[1] - r[0] >= 6
                and (er is None or r[1] <= er[0] or r[0] >= er[1])]
        if not runs:
            continue
        groups = [list(runs[0])]
        for a, b in runs[1:]:
            if a - groups[-1][1] < 60:
                groups[-1][1] = b
            else:
                groups.append([a, b])
        dash_at[c] = [tuple(g) for g in groups]
    cols = sorted(dash_at)
    out = {}
    import bisect
    for c in range(c0, c1):
        if c in dash_at:
            gs = dash_at[c]
            if len(gs) == 1:
                out[c] = (gs[0], "line")
                continue
            # several separate dashes in one column: the one nearest the neighbouring dash columns
            i = bisect.bisect_left(cols, c)
            ref = [(_mid(dash_at[k][0])) for k in cols[max(0, i - 3):i] if len(dash_at[k]) == 1]
            if not ref:
                out[c] = (None, "lost")
                continue
            r = ref[-1]
            out[c] = (min(gs, key=lambda g: abs(_mid(g) - r)), "line")
            continue
        i = bisect.bisect_left(cols, c)
        cl = cols[i - 1] if i > 0 else None
        cr = cols[i] if i < len(cols) else None
        if cl is not None and cr is not None and cr - cl <= max_gap and len(dash_at[cl]) == 1 \
                and len(dash_at[cr]) == 1:
            yl, yr = _mid(dash_at[cl][0]), _mid(dash_at[cr][0])
            out[c] = (yl + (yr - yl) * (c - cl) / (cr - cl), "gap")
            continue
        e = exp.get(c)
        if e is None or e[1] != "line":
            out[c] = (None, "lost")
            continue
        # fused only if the exp line agrees with the nearest free dash (within 20 px plus half a
        # pixel per column of distance); otherwise the dashes merely stop short of this column
        near = [k for k in (cl, cr) if k is not None and len(dash_at[k]) == 1]
        if near:
            k = min(near, key=lambda q: abs(q - c))
            if abs(k - c) <= 150 and abs(_mid(e[0]) - _mid(dash_at[k][0])) > 20 + 0.5 * abs(k - c):
                out[c] = (None, "lost")
                continue
        out[c] = (e[0], "fused")
    return out


def _mid(run):
    return (run[0] + run[1] - 1) / 2.0


def _centre(entry):
    v = entry[0]
    if isinstance(v, tuple):
        if len(entry) == 3:
            return float(entry[2])
        return (v[0] + v[1] - 1) / 2.0
    return float(v)


def read_spec(image, at, spec):
    m = masks(image, spec)
    xa, xb, xm = m["x"]
    ya, yb, ym = m["y"]
    curve = spec["curve"]
    w = W_THIN if curve == "elas" else W_THICK
    tr = trace_visc(m) if curve == "visc" else trace(m, curve)
    cols = sorted(c for c in tr if tr[c][1] != "lost")
    cen = {c: _centre(tr[c]) for c in cols}
    max_px = spec.get("max_px", 120)
    out = []
    for x in at:
        c = int(round((x - xa) / xb))
        if c not in tr:
            out.append({"x": x, "y": None, "note": "outside the traced columns"})
            continue
        e = tr[c]
        state = e[1]
        nb = [cen[k] for k in range(c - 8, c + 9) if k in cen]
        ks = [k for k in range(c - 8, c + 9) if k in cen]
        slope = abs(np.polyfit(ks, nb, 1)[0]) if len(ks) >= 3 else 0.0
        h = w * np.sqrt(1.0 + slope * slope)
        if state == "lost":
            out.append({"x": x, "y": None, "note": "curve lost by the tracer here"})
            continue
        if state == "gap":
            yc = float(e[0])
            lo, hi = yc - 8.0, yc + 8.0
        else:
            a, b = e[0]
            if state == "hidden":
                # the thin line may be under any thick line near the prediction: take them all
                near = [r for r in _col_runs(m["thick"], c)
                        if _nearest([r], float(e[2]))[1] <= 40.0]
                a, b = min([a] + [r[0] for r in near]), max([b] + [r[1] for r in near])
            b = b - 1
            if state == "line" and b - a <= h + 4:
                yc = (a + b) / 2.0
                lo, hi = yc - 2.0, yc + 2.0
            else:
                lo, hi = a + h / 2.0 - 2.0, b - h / 2.0 + 2.0
                if hi < lo:
                    lo, hi = (a + b) / 2.0 - 2.0, (a + b) / 2.0 + 2.0
                yc = (lo + hi) / 2.0
            if state == "fused":  # no dash drawn here: half a line width more either side
                lo, hi = lo - 7.0, hi + 7.0
        pad = ym + 1.0
        lo, hi = lo - pad, hi + pad
        if hi - lo > max_px:
            out.append({"x": x, "y": None, "note": f"{state}: interval {hi - lo:.0f} px, too wide to read"})
            continue
        val = ya + yb * yc
        v1, v2 = ya + yb * lo, ya + yb * hi
        out.append({"x": x, "y": float(val), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; x misfit {xm:.1f} px, y misfit {ym:.1f} px"})
    return out
