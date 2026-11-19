"""Shared reading code for Fig. 3 (PDF p. 10) and its inset: coefficients of Eq. 63 against eta.

The figure is vector art: black axes crossing at the origin (the horizontal axis is y = 0, the
vertical axis is eta = 0), short black tick marks crossing each axis, and each curve drawn in one
flat colour (sampled from the rendered page; one colour per legend entry).

Calibration, all from the image (black = every channel below 60):
  the horizontal axis is the band of rows holding the longest black runs, the vertical axis the band
  of columns holding the longest black column runs;
  x ticks are columns where the black run through the horizontal axis reaches at least 10 px beyond
  the axis band on both sides, on the axis line, of the common tick width (the vertical axis, the
  arrowhead and glyphs are left out); they are matched in order to the printed labels passed in the
  spec (all labels but 0, which sits on the vertical axis); where curves hide some ticks, the ticks
  found are numbered by their distance from the vertical axis in units of the smallest tick gap
  (each must fall within 5 px of that even spacing). The vertical axis column is then checked
  against eta = 0 and its offset reported;
  y ticks are rows where the black run through the vertical axis reaches 10 px beyond its band on
  both sides; they are evenly spaced, the spacing being the median gap; tick n counted from the
  horizontal axis has the value n * step, where step is read from the printed labels (spec
  "y_labels" gives {tick number: printed label}, read off the image; the labels must agree on the
  step). Labelled ticks hidden under a curve are not needed. The horizontal axis row is then
  checked against y = 0 and its offset reported.
  Both axes are fitted by straight lines through the ticks; the largest misfit is reported.
  For an axis with only two labelled ticks and no minor ticks (the inset) the spec gives "y_ticks":
  the labels of the ticks found, in order from the horizontal axis upward.

The curve: pixels within 40 (RGB distance) of the curve's colour, opened by a 5 x 5 square (this
drops the anti-aliased edges of a darker line of the same hue, whose blend with white can match a
paler curve's colour). Connected parts narrower than 500 columns are
dropped (legend samples). The line width w is the median run length where the curve is flat.
At each x: the column's run of the curve's colour nearest the centre predicted from the
neighbouring 30 columns on each side; its centre is the value. Interval (95%): +-2 px when the run
is a clean line (length within 4 px of h = w sqrt(1 + slope^2)); a shorter run (partly hidden
under an overdrawn curve) gives every centre whose line of thickness h covers the visible run,
widened by 2 px; a longer run (another curve of the same colour
touching it) or a run cut short by an overdrawn curve gives the run less half the line thickness
on each side, widened by 2 px; a column where the curve is hidden under another curve gives the
prediction from its neighbours +- (w + 4) px. Every interval is widened by the y misfit + 1 px and
by |slope| times (the x misfit + the rounding of x to a column).
Where the curve is steep (|slope| > 1.5 px/px) a vertical cut through the thick curved stroke is
biased, so the stroke is read row by row instead: the centres of its horizontal runs over 60 rows
either side are fitted by a parabola in the row and the row where it meets the column of x is the
value; interval +-(2 px + the local fit's misfit) across the stroke, converted to rows.
"""

import numpy as np
from scipy import ndimage


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    r = _runs(v)
    return max((b - a for a, b in r), default=0)


def _band(lengths):
    lengths = np.asarray(lengths)
    idx = np.flatnonzero(lengths > 0.8 * lengths.max())
    # the contiguous group holding the maximum
    m = int(np.argmax(lengths))
    grp = [i for i in idx if abs(i - m) < 15]
    return min(grp), max(grp)


def _beyond(line, a, b):
    """Black pixels contiguous with the band [a, b], the smaller count of the two sides (a tick
    crosses the axis)."""
    n = 0
    i = a - 1
    while i >= 0 and line[i]:
        n += 1
        i -= 1
    m = 0
    i = b + 1
    while i < len(line) and line[i]:
        m += 1
        i += 1
    return min(n, m)


def _groups(flags, maxlen=40):
    """Centres of the flagged runs no longer than maxlen whose width is that of the typical tick
    (within 3 px of the median width): an arrowhead or a glyph has another width."""
    runs = [(a, b) for a, b in _runs(flags) if b - a <= maxlen]
    if not runs:
        return []
    med = float(np.median([b - a for a, b in runs]))
    return [(a + b - 1) / 2.0 for a, b in runs if abs((b - a) - med) <= 3]


def _fit(pix, vals):
    p, v = np.asarray(pix, float), np.asarray(vals, float)
    k, m = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - m) / k - p)))
    return m, k, mis


def calibrate(image, spec):
    black = (image[..., :3] < 60).all(axis=2)
    H, W = black.shape
    r0, r1 = _band([_longest(black[i]) for i in range(H)])
    c0, c1 = _band([_longest(black[:, j]) for j in range(W)])
    # x ticks
    xflag = np.array([_beyond(black[:, j], r0, r1) >= 10 for j in range(W)])
    xflag[c0 - 3:c1 + 4] = False
    xt = _groups(xflag)
    # the arrowhead at the right end of the axis is not a tick
    ax_end = int(np.flatnonzero(black[(r0 + r1) // 2]).max())
    xt = [t for t in xt if t < ax_end - 50]
    # a tick lies on the axis line: the axis row is black 15 px left and right of it (this leaves
    # out the glyph eta beyond the arrowhead)
    rr = (r0 + r1) // 2
    xt = [t for t in xt if black[rr, max(int(t) - 15, 0):int(t) + 16].all()]
    labels = spec["x_labels"]
    if len(xt) == len(labels):
        vals = labels
    else:
        # ticks hidden under curves: the labels are evenly spaced; number the ticks found by their
        # distance from the vertical axis (eta = 0) in units of the smallest tick gap
        step_px = float(np.min(np.diff(xt)))
        step_v = float(np.min(np.diff(sorted(labels))))
        cax = (c0 + c1) / 2.0
        rel = [(t - xt[0]) / step_px for t in xt]
        if len(xt) < 3 or any(abs(i - round(i)) * step_px > 5 for i in rel):
            raise ValueError(f"x axis: ticks at {xt} do not fall on an even spacing for {labels}")
        # the first tick's number: its distance from the vertical axis in tick gaps
        step_px = (xt[-1] - xt[0]) / round(rel[-1])
        n0 = (xt[0] - cax) / step_px
        if abs(n0 - round(n0)) > 0.25:
            raise ValueError(f"x axis: ticks at {xt} are not a whole number of gaps from the vertical axis")
        vals = [(round(n0) + round(i)) * step_v for i in rel]
        if any(min(abs(v - lab) for lab in labels) > 1e-9 for v in vals):
            raise ValueError(f"x axis: ticks at {xt} numbered {vals}, not among the labels {labels}")
    xa, xb, xm = _fit(xt, vals)
    x0_off = abs(((c0 + c1) / 2.0) - (0 - xa) / xb)
    # y ticks
    yflag = np.array([_beyond(black[i], c0, c1) >= 10 for i in range(H)])
    yflag[r0 - 3:r1 + 4] = False
    yt = _groups(yflag)
    # the arrowhead at the top end of the axis is not a tick
    vline = black[:, (c0 + c1) // 2]
    ay_top = int(np.flatnonzero(vline).min())
    yt = [t for t in yt if t > ay_top + 50]
    # a tick lies on the axis line: the axis column is black 15 px above and below it (this
    # leaves out the strokes of the label "0" under the axis)
    cc = (c0 + c1) // 2
    yt = [t for t in yt if black[max(int(t) - 15, 0):int(t) + 16, cc].all()]
    axis_row = (r0 + r1) / 2.0
    if "y_ticks" in spec:
        above = sorted([t for t in yt if t < axis_row], reverse=True)
        if len(above) != len(spec["y_ticks"]):
            raise ValueError(f"y axis: found ticks {above}, expected {spec['y_ticks']}")
        ya, yb, ym = _fit(above, spec["y_ticks"])
        y0_off = abs(axis_row - (0 - ya) / yb)
        return dict(black=black, axis=(r0, r1, c0, c1), x=(xa, xb, xm), y=(ya, yb, ym), xt=xt, yt=above,
                    x0_off=x0_off, y0_off=y0_off)
    gaps = np.diff(sorted(yt))
    sp = float(np.min(gaps))  # some ticks may be hidden: gaps are then multiples of the spacing
    ns = [int(round((axis_row - t) / sp)) for t in yt]
    if len(yt) < 3 or len(set(ns)) != len(ns):
        raise ValueError(f"y axis: ticks {ns} at rows {yt} (axis row {axis_row}, spacing {sp})")
    steps = [lab / n for n, lab in spec["y_labels"].items()]
    if max(steps) - min(steps) > 1e-12:
        raise ValueError(f"y axis: labels {spec['y_labels']} are not evenly spaced")
    ya, yb, ym = _fit(yt, [n * steps[0] for n in ns])
    y0_off = abs(axis_row - (0 - ya) / yb)
    return dict(black=black, axis=(r0, r1, c0, c1), x=(xa, xb, xm), y=(ya, yb, ym), xt=xt, yt=yt,
                x0_off=x0_off, y0_off=y0_off)


def curve_mask(image, spec):
    col = np.array(spec["color"], float)
    d = np.sqrt(((image[..., :3].astype(float) - col) ** 2).sum(axis=2))
    m = d < 40
    x0, y0, x1, y1 = spec.get("box", (0, 0, m.shape[1], m.shape[0]))
    keep = np.zeros_like(m)
    keep[y0:y1, x0:x1] = True
    for bx in spec.get("exclude", []):
        keep[bx[1]:bx[3], bx[0]:bx[2]] = False
    m &= keep
    # drop the anti-aliased edges of darker lines of the same hue (a pale colour is also the blend
    # of a darker one with white): an opening keeps only strokes at least 5 px across
    m = ndimage.binary_opening(m, structure=np.ones((5, 5)))
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    sl = ndimage.find_objects(lab)
    ok = np.zeros(n + 1, bool)
    for k, s in enumerate(sl, start=1):
        if s[1].stop - s[1].start >= spec.get("min_width", 500):
            ok[k] = True
    return ok[lab]


def read_spec(image, at, spec):
    cal = calibrate(image, spec)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    m = curve_mask(image, spec)
    W = m.shape[1]
    cols = {}
    for c in range(W):
        r = _runs(m[:, c])
        if r:
            cols[c] = r
    # line width: single runs in flat stretches
    single = {c: r[0] for c, r in cols.items() if len(r) == 1}
    lens = [b - a for a, b in single.values()]
    w = float(np.percentile(lens, 20)) if lens else 10.0

    def centres(c0, c1):
        out = []
        for k in range(c0, c1):
            if k in single:
                a, b = single[k]
                if b - a <= 6 * w:
                    out.append((k, (a + b - 1) / 2.0))
        return out

    res = []
    for x in at:
        c = int(round((x - xa) / xb))
        nb = centres(c - 30, c - 1) + centres(c + 2, c + 31)
        if len(nb) < 6:
            res.append({"x": x, "y": None, "note": "curve not found near this column"})
            continue
        ks = np.array([p[0] for p in nb], float)
        ys = np.array([p[1] for p in nb], float)
        deg = 2 if len(nb) >= 12 else 1
        poly = np.polyfit(ks, ys, deg)
        pred = float(np.polyval(poly, c))
        slope = float(np.polyval(np.polyder(poly), c))
        h = w * np.sqrt(1 + slope * slope)
        cx = (x - xa) / xb
        if abs(slope) > 1.5:
            # steep: a vertical cut through a thick curved stroke is biased, so read the stroke
            # row by row (horizontal runs) and find the row whose stroke centre is at column cx
            pts = []
            for r in range(int(pred) - 60, int(pred) + 61):
                if r < 0 or r >= m.shape[0]:
                    continue
                rr = [(a + b - 1) / 2.0 for a, b in _runs(m[r]) if b - a <= 3 * w]
                near = [q for q in rr if abs(q - cx) <= 2 * w]
                if len(near) == 1:
                    pts.append((r, near[0]))
            if len(pts) >= 10:
                rs = np.array([p[0] for p in pts], float)
                qs = np.array([p[1] for p in pts], float)
                P = np.polyfit(rs, qs, 2)
                roots = [z.real for z in np.roots(P - np.array([0, 0, cx])) if abs(z.imag) < 1e-9]
                if not roots:
                    res.append({"x": x, "y": None, "note": "steep stretch: no row meets this column"})
                    continue
                yc = float(min(roots, key=lambda z: abs(z - pred)))
                B = float(np.polyval(np.polyder(P), yc))
                fit_mis = float(np.max(np.abs(np.polyval(P, rs) - qs)))
                half = (2.0 + fit_mis) / abs(B)
                pad = ym + 1.0 + abs(slope) * xm
                lo, hi = yc - half - pad, yc + half + pad
                v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
                res.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                            "px": [float(cx), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                            "note": f"steep: read row by row, stroke centre +-2 px across, local fit misfit "
                                    f"{fit_mis:.1f} px; x misfit {xm:.1f} px, y misfit {ym:.1f} px; axis offsets "
                                    f"from 0: x {cal['x0_off']:.1f} px, y {cal['y0_off']:.1f} px"})
                continue
        runs = cols.get(c, [])
        best = None
        for a, b in runs:
            dd = 0.0 if a <= pred <= b - 1 else min(abs(pred - a), abs(pred - (b - 1)))
            if dd <= h and (best is None or dd < best[0]):
                best = (dd, a, b - 1)
        if best is None:
            yc = pred
            lo, hi = pred - (w + 4), pred + (w + 4)
            state = "hidden under another curve; predicted from neighbouring columns"
        else:
            _, a, b = best
            if b - a < h - 4:
                # partly hidden under another curve: the line still covers the visible run
                lo, hi = b - h / 2.0 - 2.0, a + h / 2.0 + 2.0
                yc = (lo + hi) / 2.0
                state = "partly hidden under another curve"
            elif b - a <= h + 4:
                yc = (a + b) / 2.0
                lo, hi = yc - 2.0, yc + 2.0
                state = "line"
            else:
                lo, hi = a + h / 2.0 - 2.0, b - h / 2.0 + 2.0
                if hi < lo:
                    lo, hi = (a + b) / 2.0 - 2.0, (a + b) / 2.0 + 2.0
                yc = (lo + hi) / 2.0
                state = "run longer than the line (touching another curve)"
            if abs(yc - pred) > h:
                yc = pred
                lo, hi = min(lo, pred - (w + 4)), max(hi, pred + (w + 4))
                state += "; centre far from the neighbours' trend, interval widened"
        pad = ym + 1.0 + abs(slope) * (xm + abs(c - cx))
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
        res.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; w {w:.0f} px; x misfit {xm:.1f} px, y misfit {ym:.1f} px; "
                            f"axis offsets from 0: x {cal['x0_off']:.1f} px, y {cal['y0_off']:.1f} px"})
    return res
