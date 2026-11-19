"""Fig. 4A (p. 3): l/t against sigma2/sigma1, one black curve.

Calibration from the image: the x axis is the long horizontal line at the bottom, the y axis the
long vertical line at sigma2/sigma1 = 0. x ticks are the short marks standing on the x axis
(matched to the printed -1, -.75, ..., 1; the y axis itself is the mark at 0); y ticks are the short
crosses on the y axis (matched to the printed 2, 4, 6, 8). The axes are drawn slightly out of square,
so a value is read along lines parallel to the drawn axes. The curve is traced column by column from
a seed on its middle part and read at each requested x; the interval is the ink extent of the curve
in that column plus the calibration misfit.
"""

import numpy as np

X_LABELS = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
Y_LABELS = [8.0, 6.0, 4.0, 2.0]  # top to bottom, as the tick rows are sorted
SEED_X = -0.6  # a value on the rising part, away from both axes


def _runs(v):
    idx = np.flatnonzero(v)
    if idx.size == 0:
        return []
    cuts = np.flatnonzero(np.diff(idx) > 1)
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]
    return list(zip(starts.tolist(), ends.tolist()))


def _longest(v, gap=3):
    best = (0, 0, 0)
    rs = _runs(v)
    if not rs:
        return best
    s, e = rs[0]
    for a, b in rs[1:] + [(10**9, 10**9)]:
        if a - e - 1 <= gap:
            e = b
        else:
            if e - s + 1 > best[0]:
                best = (e - s + 1, s, e)
            s, e = a, b
    return best


def _fit(marks, labels):
    p = np.array(marks, float)
    v = np.array(labels, float)
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, max(misfit, 0.5)


def calibrate(dark):
    H, W = dark.shape
    # x axis: the lowest row whose longest dark run spans most of the width
    # (the drawn x axis leans too, so look at bands of 21 rows)
    rc = np.convolve(dark.sum(axis=1), np.ones(21), mode="same")
    rpk = H // 2 + int(np.argmax(rc[H // 2 :]))
    xr_rows = list(range(rpk - 20, rpk + 21))
    # y axis: a column whose longest dark run spans much of the height
    # the drawn y axis leans by a few pixels, so look at bands of 41 columns
    counts = np.convolve(dark[: min(xr_rows) - 20].sum(axis=0), np.ones(41), mode="same")
    cpk = int(np.argmax(counts))
    yc_cols = list(range(cpk - 30, cpk + 31))
    band = dark[:, cpk - 30 : cpk + 31].any(axis=1)
    _, r_top, r_bot = _longest(band, gap=6)
    # tilt of each axis: centre of the line at two ends
    def ycol_at(r):
        return float(np.mean([c for c in range(min(yc_cols), max(yc_cols) + 1) if dark[r, c]]))
    ra, rb = r_top + 40, min(r_bot - 40, min(xr_rows) - 40)
    ya, yb = ycol_at(ra), ycol_at(rb)
    yslope = (yb - ya) / (rb - ra)  # column change per row along the y axis
    def xrow_at(c):
        return float(np.mean([r for r in range(min(xr_rows), max(xr_rows) + 1) if dark[r, c]]))
    _, c_lft, c_rgt = _longest(dark[min(xr_rows) : max(xr_rows) + 1].any(axis=0), gap=6)
    ca, cb = c_lft + 40, c_rgt - 40
    xa, xb = xrow_at(ca), xrow_at(cb)
    xslope = (xb - xa) / (cb - ca)  # row change per column along the x axis
    x_row = lambda c: xa + xslope * (c - ca)  # noqa: E731
    y_col = lambda r: ya + yslope * (r - ra)  # noqa: E731
    # x ticks: columns with a vertical dark run standing on the x axis
    cand = []
    for c in range(W):
        r0 = int(round(x_row(c)))
        band = dark[r0 - 90 : r0 - 14, c]
        n, s, e = _longest(band, gap=1)
        if n >= 45 and e >= band.size - 4:  # touches the axis
            cand.append(c)
    groups = []
    for c in cand:
        if groups and c - groups[-1][-1] <= 2:
            groups[-1].append(c)
        else:
            groups.append([c])
    xt = [float(np.mean(g)) + 0.5 for g in groups if len(g) <= 40]
    # y ticks: rows where ink spans both sides of the y axis but not far out
    yt_rows = []
    for r in range(H):
        c0 = int(round(y_col(r)))
        if r > min(xr_rows) - 30:
            break
        near = dark[r, c0 - 45 : c0 + 46].mean()
        far = dark[r, c0 + 100 : c0 + 140].any()  # the tick labels stand on the left
        if near > 0.9 and not far:
            yt_rows.append(r)
    ygroups = []
    for r in yt_rows:
        if ygroups and r - ygroups[-1][-1] <= 2:
            ygroups[-1].append(r)
        else:
            ygroups.append([r])
    yt = [float(np.mean(g)) + 0.5 for g in ygroups if len(g) >= 4]
    return xt, yt, x_row, y_col, xr_rows, yc_cols


def trace(dark, seed_c, seed_r, lo_c, hi_c, max_gap=140):
    """column -> (centre, top, bottom) of the curve's run, following the nearest run."""
    def runs(c):
        return _runs(dark[:, c])
    path = {}
    rs = runs(seed_c)
    s, e = min(rs, key=lambda x: abs((x[0] + x[1]) / 2 - seed_r))
    path[seed_c] = ((s + e) / 2 + 0.5, s, e + 1)
    for step in (1, -1):
        hist = [(seed_c, path[seed_c][0])]
        c, gap = seed_c + step, 0
        while lo_c <= c <= hi_c and gap <= max_gap:
            rec = hist[-8:]
            slope = (rec[-1][1] - rec[0][1]) / (rec[-1][0] - rec[0][0]) if len(rec) > 1 else 0.0
            pred = hist[-1][1] + slope * (c - hist[-1][0])
            cand = runs(c)
            if cand:
                s, e = min(cand, key=lambda x: 0 if x[0] <= pred <= x[1] + 1 else min(abs(x[0] - pred), abs(x[1] + 1 - pred)))
                d = 0 if s <= pred <= e + 1 else min(abs(s - pred), abs(e + 1 - pred))
                if d <= 25 + abs(slope) * (gap + 1):
                    path[c] = ((s + e) / 2 + 0.5, s, e + 1)
                    hist.append((c, path[c][0]))
                    gap = 0
                    c += step
                    continue
            gap += 1
            c += step
    return path


def read(image, at):
    gray = image.astype(float).mean(axis=2)
    dark = gray < (np.percentile(gray, 60) + np.percentile(gray, 0.5)) / 2
    xt, yt, x_row, y_col, xr_rows, yc_cols = calibrate(dark)
    if len(xt) != len(X_LABELS) or len(yt) != len(Y_LABELS):
        raise ValueError(f"ticks found: x {xt}, y {yt}")
    xa, xb, xmis = _fit(xt, X_LABELS)  # x = xa + xb * column (measured on the x axis)
    ya_, yb_, ymis = _fit(yt, Y_LABELS)  # y = ya + yb * row (measured on the y axis)
    c_axis0 = (0.0 - xa) / xb
    r_axis0 = float(np.mean(xr_rows))
    y_col0 = y_col(r_axis0)

    def to_x(c, r):  # shift the column back to the x axis along the y axis direction
        return xa + xb * (c - (y_col(r) - y_col0))

    def to_y(c, r):  # shift the row to the y axis along the x axis direction
        return ya_ + yb_ * (r - (x_row(c) - x_row(c_axis0)))

    # mask out the axis lines and ticks before tracing
    curve = dark.copy()
    for r in range(curve.shape[0]):
        c0 = int(round(y_col(r)))
        curve[r, c0 - 60 : c0 + 61] = False
    for c in range(curve.shape[1]):
        r0 = int(round(x_row(c)))
        curve[r0 - 30 :, c] = False
    for t in xt:
        curve[:, int(t) - 12 : int(t) + 13] &= np.arange(curve.shape[0])[:, None] < x_row(t) - 68
    seed_c = int(round((SEED_X - xa) / xb))
    rs = _runs(curve[:, seed_c])
    seed_r = (rs[len(rs) // 2][0] + rs[len(rs) // 2][1]) / 2
    path = trace(curve, seed_c, seed_r, 0, curve.shape[1] - 1)
    cols = sorted(path)
    out = []
    for xv in at:
        # column on the curve where the drawn x equals xv (columns shift slightly with row)
        best = None
        for c in cols:
            if abs(to_x(c, path[c][0]) - xv) < abs(xb) * 0.6:
                best = c
                break
        if best is None:
            out.append({"x": xv, "y": None, "note": "no curve ink at this x (outside the drawn curve or hidden by an axis)"})
            continue
        centre, top, bot = path[best]
        y = to_y(best, centre)
        # the x calibration misfit moves the column: take the ink extent over that many columns
        k = int(np.ceil(xmis))
        near = [path[c] for c in range(best - k, best + k + 1) if c in path]
        top = min(p[1] for p in near)
        bot = max(p[2] for p in near)
        lo = to_y(best, bot) - abs(yb_) * ymis
        hi = to_y(best, top) + abs(yb_) * ymis
        out.append({"x": xv, "y": float(y), "lo": float(min(lo, hi)), "hi": float(max(lo, hi)),
                    "px": [float(best) + 0.5, float(centre)], "px_lo": float(top), "px_hi": float(bot),
                    "note": f"x misfit {xmis:.1f} px, y misfit {ymis:.1f} px; ink rows {top}-{bot}"})
    return out
