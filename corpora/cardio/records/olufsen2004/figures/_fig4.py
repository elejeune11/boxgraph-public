"""Shared reading code for Fig. 4 (PDF p. 14): flow q against time t after a pressure step.

Calibration, all from the image:
  * the plot box is the black frame (the longest dark rows and columns);
  * x: the frame's left and right edges are the corner labels t = -2 and 2, and the tick marks
    hanging down from the top edge are t = -1, 0, 1;
  * y: the frame's top edge is the label q = 10, and the tick marks pointing right from the left
    edge are q = 8, 6, 4, 2, 0, -2 (the bottom edge has no label and is not used). The flat solid
    line at the top meets the left edge too, but its run is far longer than a tick and is skipped.
  Each axis is a straight-line fit through these marks; its largest misfit enters every interval.
Curves are black: the solid curve (rigid vessel) and the dashed curve (windkessel), as the caption
says. The dotted grid is black too, but its dots are short runs and are ignored by a minimum run
length. The curves are drawn as polylines with vertices every 0.1 in t (kinks are visible), so
each interval carries the offset of the centre from the chord through the centres CHORD columns
either side (more than one vertex spacing), besides placement and slope.
"""
import numpy as np

X_EDGES = (-2.0, 2.0)
X_TICKS = [-1.0, 0.0, 1.0]
Y_TOP = 10.0
Y_TICKS = [8.0, 6.0, 4.0, 2.0, 0.0, -2.0]
MIN_RUN = 8   # pixels: a grid dot is shorter
CHORD = 60    # columns either side for the chord offset and the slope (vertices are about 56 apart)


def _runs(v):
    idx = np.nonzero(v)[0]
    if idx.size == 0:
        return []
    cuts = np.nonzero(np.diff(idx) > 1)[0]
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]
    return list(zip(starts.tolist(), ends.tolist()))


def ink(image):
    return image.astype(float).mean(axis=2) < 110


def _fit(marks):
    p = np.array([m[0] for m in marks])
    v = np.array([m[1] for m in marks])
    b, a = np.polyfit(p, v, 1)
    return a, b, max(float(np.max(np.abs(p - (v - a) / b))), 0.5)


def calibrate(image):
    k = ink(image)
    H, W = k.shape
    rows = np.nonzero(k.sum(axis=1) > 0.6 * W)[0]
    cols = np.nonzero(k.sum(axis=0) > 0.6 * H)[0]
    top = [r for r in rows if r < rows.min() + 10]
    left = [c for c in cols if c < cols.min() + 10]
    right = [c for c in cols if c > cols.max() - 10]
    bot = [r for r in rows if r > rows.max() - 10]
    top_in, left_in, right_in, bot_in = max(top) + 1, max(left) + 1, min(right), min(bot)
    xt = []
    for c in range(left_in + 3, right_in - 3):
        n = 0
        while k[top_in + n, c]:
            n += 1
        if 8 <= n <= 80:
            xt.append(c)
    xt = [(s + e) / 2 + 0.5 for s, e in _runs(np.isin(np.arange(W), xt))]
    yt = []
    for r in range(top_in + 3, bot_in - 3):
        n = 0
        while k[r, left_in + n]:
            n += 1
        if 8 <= n <= 80:
            yt.append(r)
    yt = [(s + e) / 2 + 0.5 for s, e in _runs(np.isin(np.arange(H), yt))]
    if len(xt) != len(X_TICKS) or len(yt) != len(Y_TICKS):
        raise ValueError(f"unexpected ticks: x {xt}, y {yt}")
    xm = [(np.mean(left) + 0.5, X_EDGES[0])] + list(zip(xt, X_TICKS)) + [(np.mean(right) + 0.5, X_EDGES[1])]
    ym = [(np.mean(top) + 0.5, Y_TOP)] + list(zip(yt, Y_TICKS))
    xa, xb, xmis = _fit(xm)
    ya, yb, ymis = _fit(ym)
    return {"xa": xa, "xb": xb, "xmis": xmis, "ya": ya, "yb": yb, "ymis": ymis,
            "box": (left_in, top_in, right_in, bot_in), "k": k}


def _pick(k, col, box, which):
    """The upper curve is the highest run in the column. The lower (dashed) curve is a run below
    the upper one; a column with a single run is a gap between dashes (None)."""
    left, top, right, bot = box
    runs = [(s + top + 2, e + top + 2) for s, e in _runs(k[top + 2:bot - 2, col]) if e - s + 1 >= MIN_RUN]
    if not runs:
        return None
    if which == "upper":
        return min(runs)
    return max(runs) if len(runs) >= 2 else None


def read_curve(image, at, which, dashed=False):
    """which: 'upper' (the solid curve, above the dashed one) or 'lower' (the dashed curve)."""
    cal = calibrate(image)
    k, box = cal["k"], cal["box"]
    out = []
    for x in at:
        x = float(x)
        cx = (x - cal["xa"]) / cal["xb"]
        c = int(round(cx - 0.5))

        def centre(q):
            se = _pick(k, q, box, which)
            return None if se is None else ((se[0] + se[1]) / 2 + 0.5, se)

        # the curves jump at t = 0: the chord and slope use columns on the same side of it only
        c0 = (0.0 - cal["xa"]) / cal["xb"]
        lo_col, hi_col = (int(c0) + 6, box[2] - 3) if x > 0 else (box[0] + 3, int(c0) - 6)

        here = centre(c)
        note = ""
        if here is None and dashed:
            # a gap between dashes: take the nearest dash on each side and join them
            lft = next(((q, centre(q)) for q in range(c - 1, c - 60, -1) if centre(q)), None)
            rgt = next(((q, centre(q)) for q in range(c + 1, c + 60) if centre(q)), None)
            if lft and rgt:
                (ql, (rl, _)), (qr, (rr, _)) = lft, rgt
                row = rl + (rr - rl) * (c - ql) / (qr - ql)
                note = f"in a gap between dashes, joined across columns {ql}-{qr}"
                here = (row, None)
        if here is None:
            out.append({"x": x, "y": None, "note": "no curve found in this column"})
            continue
        row = here[0]
        side = []
        for dc in (-CHORD, CHORD):
            q, got = None, None
            for d2 in ([0] + [s * j for j in range(1, 40) for s in (1, -1)]) if dashed else [0]:
                qq = min(max(c + dc + d2, lo_col), hi_col)
                if qq == c:
                    continue
                got = centre(qq)
                if got is not None:
                    q = qq
                    break
            if got is not None:
                side.append((q, got[0]))
        if len(side) == 2:
            (q1, r1), (q2, r2) = side
            slope = (r2 - r1) / (q2 - q1)
            chord = abs(row - (r1 + slope * (c - q1)))
        else:
            slope, chord = 0.0, 0.0
        half_px = cal["ymis"] + abs(slope) * cal["xmis"] + 1.0 + abs(slope) * 1.0 + chord
        if note:
            half_px += 2.0
        y = cal["ya"] + cal["yb"] * row
        lo = cal["ya"] + cal["yb"] * (row + half_px)
        hi = cal["ya"] + cal["yb"] * (row - half_px)
        out.append({"x": x, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [c + 0.5, row],
                    "px_lo": row - half_px, "px_hi": row + half_px,
                    "note": (note + "; " if note else "") + f"slope {slope:.2f} px/px, chord offset {chord:.1f} px"})
    return out
