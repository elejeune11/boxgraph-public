"""Shared helpers for this record's figure readings.

Calibration comes from the image only: the plot frame, and the centres of the printed tick labels
(digits found as connected dark components just outside the frame, grouped into numbers). The caller
matches the labels it sees, in order, to their printed values; a straight line is fitted through the
(label centre, value) pairs and its largest misfit in pixels is reported.
"""

import numpy as np
from scipy import ndimage


def dark(img, thr=None):
    g = img.astype(float).mean(axis=2) if img.ndim == 3 else img.astype(float)
    if thr is None:
        paper = float(np.percentile(g, 60))
        ink = float(np.percentile(g, 0.5))
        thr = (paper + ink) / 2
    return g < thr


def frame(d, frac=0.5):
    """Rows and columns of the plot frame: (left, top, right, bottom) as the inner edges of the lines,
    and the line positions (centres)."""
    H, W = d.shape

    def longest(v):
        # longest run of ink, bridging gaps of up to 3 pixels (a scanned line is not perfect)
        best = cur = gap = 0
        for x in v:
            if x:
                cur += 1 + gap
                gap = 0
            elif cur:
                gap += 1
                if gap > 3:
                    cur = gap = 0
            best = max(best, cur)
        return best

    # frame lines are long unbroken lines; text (an axis title) is not
    # (on the mask widened by 3 pixels across the line, so a slightly rotated thin line stays unbroken)
    dv = d.copy()
    dh = d.copy()
    for k in (1, 2, 3):
        dv[k:, :] |= d[:-k, :]
        dv[:-k, :] |= d[k:, :]
        dh[:, k:] |= d[:, :-k]
        dh[:, :-k] |= d[:, k:]
    rows = np.array([r for r in range(H) if d[r].sum() > 0.4 * frac * W and longest(dv[r]) > frac * W])
    cols = np.array([c for c in range(W) if d[:, c].sum() > 0.4 * frac * H * 0.6 and longest(dh[:, c]) > frac * H * 0.6])

    def groups(v):
        out, cur = [], [v[0]]
        for a in v[1:]:
            if a - cur[-1] <= 2:
                cur.append(a)
            else:
                out.append(cur)
                cur = [a]
        out.append(cur)
        return out

    rg, cg = groups(rows), groups(cols)
    top, bot = rg[0], rg[-1]
    left, right = cg[0], cg[-1]
    return {"top": (top[0], top[-1]), "bottom": (bot[0], bot[-1]), "left": (left[0], left[-1]),
            "right": (right[0], right[-1])}


def _components(mask, min_px=15):
    lab, n = ndimage.label(mask)
    objs = ndimage.find_objects(lab)
    out = []
    for i, sl in enumerate(objs):
        cnt = int((lab[sl] == i + 1).sum())
        if cnt >= min_px:
            out.append((sl[0].start, sl[0].stop, sl[1].start, sl[1].stop, cnt))
    return out


def x_labels(d, fr, c0=None, c1=None, gap=None):
    """Centres (columns) of the tick labels in the first band of text under the frame, left to right."""
    b = fr["bottom"][1] + 3
    H, W = d.shape
    c0 = 0 if c0 is None else c0
    c1 = W if c1 is None else c1
    prof = d[b:, c0:c1].sum(axis=1)
    k = 0
    while k < len(prof) and prof[k] > 0.3 * (c1 - c0):  # what is left of the frame line
        k += 1
    # the first band of rows with ink that is tall enough to be text (not a tick or a sliver of the axis)
    bands = [(a, b) for a, b in runs(prof > 0, k) if b - a >= 15]
    if not bands:
        return []
    r0, r1 = bands[0][0], bands[0][1] - 1
    band = d[b + r0:b + r1 + 1, c0:c1]
    hgt = r1 - r0 + 1
    # digits are about as tall as the band; a flat sliver is what a slightly skewed axis line leaves
    comps = [c for c in _components(band) if c[1] - c[0] >= 0.4 * hgt]
    gap = gap if gap is not None else 0.6 * hgt
    comps = sorted(comps, key=lambda c: c[2])
    labels, cur = [], None
    for c in comps:
        if cur is not None and c[2] - cur[1] <= gap:
            cur = [cur[0], max(cur[1], c[3])]
        else:
            if cur is not None:
                labels.append(cur)
            cur = [c[2], c[3]]
    if cur is not None:
        labels.append(cur)
    return [c0 + (a + bb) / 2.0 for a, bb in labels]


def y_labels(d, fr, r0=None, r1=None, gap=None):
    """Centres (rows) of the tick labels in the first band of text left of the frame, top to bottom."""
    lft = fr["left"][0] - 3
    H, W = d.shape
    r0 = max(0, fr["top"][0] - 40) if r0 is None else r0
    r1 = min(H, fr["bottom"][1] + 1) if r1 is None else r1
    prof = d[r0:r1, :lft].sum(axis=0)
    k = len(prof) - 1
    while k >= 0 and prof[k] > 0.3 * (r1 - r0):  # what is left of the frame line
        k -= 1
    # the last band of columns with ink that is wide enough to be text (outward ticks are narrow)
    bands = [(a, b) for a, b in runs(prof[:k + 1] > 0) if b - a >= 20]
    if not bands:
        return []
    s, e = bands[-1][0], bands[-1][1] - 1
    band = d[r0:r1, s:e + 1]
    comps = _components(band)
    if comps:  # digits are large; specks of a wavy frame line next to the band are not
        med = float(np.median([c[4] for c in comps]))
        comps = [c for c in comps if c[4] >= 0.3 * med]
    comps = sorted(comps, key=lambda c: c[0])
    gap = gap if gap is not None else 8
    labels, cur = [], None
    for c in comps:
        if cur is not None and c[0] - cur[1] <= gap:
            cur = [cur[0], max(cur[1], c[1])]
        else:
            if cur is not None:
                labels.append(cur)
            cur = [c[0], c[1]]
    if cur is not None:
        labels.append(cur)
    return [r0 + (a + b) / 2.0 for a, b in labels]


def y_ticks(d, fr, label_rows, search=40, depth=(3, 30), side="in"):
    """Row of the tick mark nearest each label: a short horizontal mark on the left frame line
    (inside the plot when side='in', outside when 'out'). None where no tick is found."""
    l0, l1 = fr["left"]
    if side == "in":
        c0, c1 = l1 + 1 + depth[0], l1 + 1 + depth[1]
    else:
        c0, c1 = l0 - depth[1], l0 - depth[0]
    out = []
    for r in label_rows:
        lo, hi = int(r - search), int(r + search)
        cnt = d[lo:hi, c0:c1].sum(axis=1)
        rows = np.where(cnt >= 0.6 * (c1 - c0))[0]
        if len(rows) == 0:
            out.append(None)
            continue
        # the longest consecutive group
        groups, cur = [], [rows[0]]
        for a in rows[1:]:
            if a - cur[-1] <= 1:
                cur.append(a)
            else:
                groups.append(cur)
                cur = [a]
        groups.append(cur)
        g = max(groups, key=lambda g: (cnt[g].sum(), -abs(lo + np.mean(g) - r)))
        out.append(lo + float(np.mean(g)))
    return out


def x_ticks(d, fr, label_cols, search=40, depth=(3, 30), side="in"):
    """Column of the tick mark nearest each label: a short vertical mark on the bottom frame line."""
    b0, b1 = fr["bottom"]
    if side == "in":
        r0, r1 = b0 - depth[1], b0 - depth[0]
    else:
        r0, r1 = b1 + 1 + depth[0], b1 + 1 + depth[1]
    out = []
    for c in label_cols:
        lo, hi = int(c - search), int(c + search)
        cnt = d[r0:r1, lo:hi].sum(axis=0)
        cols = np.where(cnt >= 0.6 * (r1 - r0))[0]
        if len(cols) == 0:
            out.append(None)
            continue
        groups, cur = [], [cols[0]]
        for a in cols[1:]:
            if a - cur[-1] <= 1:
                cur.append(a)
            else:
                groups.append(cur)
                cur = [a]
        groups.append(cur)
        g = max(groups, key=lambda g: (cnt[g].sum(), -abs(lo + np.mean(g) - c)))
        out.append(lo + float(np.mean(g)))
    return out


def centre(span):
    return (span[0] + span[1]) / 2.0


def _line_fit(d, fr, which):
    """A frame line as a straight line in the image (the scan may be rotated a little):
    for 'bottom'/'top', row = a + s * column; for 'left'/'right', column = a + s * row."""
    lo, hi = fr[which]
    pad = 15
    pts = []
    if which in ("bottom", "top"):
        c0, c1 = fr["left"][1] + 40, fr["right"][0] - 40
        for c in range(c0, c1, 20):
            rs = runs(d[:, c], max(0, lo - pad), hi + pad + 1)
            if len(rs) == 1 and abs((rs[0][1] - rs[0][0]) - (hi - lo + 1)) <= 4:
                pts.append((c, (rs[0][0] + rs[0][1] - 1) / 2.0))
    else:
        r0, r1 = fr["top"][1] + 40, fr["bottom"][0] - 40
        for r in range(r0, r1, 20):
            rs = runs(d[r, :], max(0, lo - pad), hi + pad + 1)
            if len(rs) == 1 and abs((rs[0][1] - rs[0][0]) - (hi - lo + 1)) <= 4:
                pts.append((r, (rs[0][0] + rs[0][1] - 1) / 2.0))
    if len(pts) < 5:  # too few clean samples (lines crowd the frame): take the line as straight
        return float(centre(fr[which])), 0.0
    p = np.array(pts, float)
    s, a = np.polyfit(p[:, 0], p[:, 1], 1)
    return float(a), float(s)


class Cal:
    """Axes of a framed plot, allowing for a small rotation of the scan: a pixel (c, r) is first
    straightened, r' = r - sb (c - c_ref) and c' = c - sl (r - r_ref), with sb the slope of the bottom
    frame line and sl that of the left frame line; X and Y map c' and r' to values."""

    def __init__(self, d, xvals, yvals, x_ends=True, y_ends=True, side="in", depth=(3, 30)):
        fr = frame(d)
        self.fr = fr
        ab, self.sb = _line_fit(d, fr, "bottom")
        at_, st = _line_fit(d, fr, "top")
        al, self.sl = _line_fit(d, fr, "left")
        ar, sr = _line_fit(d, fr, "right")
        # reference point: the bottom-left corner of the frame
        self.r_ref = ab + self.sb * centre(fr["left"])
        self.c_ref = al + self.sl * self.r_ref
        xl, yl = x_labels(d, fr), y_labels(d, fr)
        if len(xl) != len(xvals) or len(yl) != len(yvals):
            raise ValueError(f"expected {len(xvals)} x labels and {len(yvals)} y labels, found {len(xl)} and {len(yl)}")
        tside = "in" if side == "labels_y" else side
        xt, yt = x_ticks(d, fr, xl, side=tside, depth=depth), y_ticks(d, fr, yl, side=tside, depth=depth)
        if side == "labels_y":  # tick marks too small to find: the y labels' own centres stand for them
            yt = list(yl)
        # ticks: x ticks lie on the bottom line, y ticks on the left line; straighten them
        xt = [None if c is None else self.cs(c, self.r_ref) for c in xt]
        yt = [None if r is None else self.rs(self.c_ref, r) for r in yt]
        if x_ends:
            xt[0] = self.cs(al + self.sl * self.r_ref, self.r_ref)
            xt[-1] = self.cs(ar + sr * self.r_ref, self.r_ref)
        if y_ends == "drop":  # the corner labels are moved off their places: use neither them nor the frame
            yt[0] = yt[-1] = None
        elif y_ends:
            yt[0] =self.rs(self.c_ref, at_ + st * self.c_ref)
            yt[-1] = self.rs(self.c_ref, ab + self.sb * self.c_ref)
        self.X = Lin([(p, float(v)) for p, v in zip(xt, xvals) if p is not None])
        self.Y = Lin([(p, float(v)) for p, v in zip(yt, yvals) if p is not None])

    def cs(self, c, r):
        return c - self.sl * (r - self.r_ref)

    def rs(self, c, r):
        return r - self.sb * (c - self.c_ref)

    def col(self, x, r):
        """Image column of the value x on the image row r."""
        return self.X.px(x) + self.sl * (r - self.r_ref)

    def yval(self, c, r):
        return self.Y.val(self.rs(c, r))

    def note(self):
        return (f"x misfit {self.X.misfit_px:.1f} px, y misfit {self.Y.misfit_px:.1f} px, "
                f"rotation {np.degrees(np.arctan(self.sb)):.2f} deg")


def calibrate(d, xvals, yvals, x_ends=True, y_ends=True, side="in", depth=(3, 30)):
    cal = Cal(d, xvals, yvals, x_ends, y_ends, side, depth)
    return cal.fr, cal.X, cal.Y, cal


def reading(x, r, c, half, cal, note=""):
    lo, hi = sorted((cal.yval(c, r + half), cal.yval(c, r - half)))
    return {"x": x, "y": cal.yval(c, r), "lo": lo, "hi": hi, "px": [float(c), float(r)],
            "px_lo": float(r - half), "px_hi": float(r + half), "note": note}


def read_trace(tr, w, at, cal, extra_note=""):
    """Readings of a traced curve at the x positions `at`, each with a 95% interval of half a line
    width (widened where the line slopes), the calibration misfits and the trace's local spread."""
    X, Y = cal.X, cal.Y
    out = []
    for x in at:
        c = X.px(x)
        r, spread = at_col(tr, c, half=4)
        if r is not None:  # the column of x on the curve's own row (rotation)
            c = cal.col(x, r)
            r, spread = at_col(tr, c, half=4)
        if r is None:
            out.append({"x": x, "y": None, "note": "no ink of this curve at this x"})
            continue
        ks = [k for k in range(int(c) - 25, int(c) + 26) if k in tr]
        slope = np.polyfit(ks, [tr[k][0] for k in ks], 1)[0] if len(ks) > 5 else 0.0
        half = 0.5 * w * np.sqrt(1 + slope ** 2) + Y.misfit_px + abs(slope) * X.misfit_px + spread / 2
        out.append(reading(x, r, c, half, cal, f"{cal.note()}, line {w} px{extra_note}"))
    return out


def stacked_lines(d, cal, at, y_lo, y_hi, n, which, win=12, min_gap=8, from_bottom=None):
    """Several nearly flat lines lying one above another: at each x, the dark runs between the values
    y_lo and y_hi in the columns within +-win of x are pooled and split into groups at gaps of more than
    min_gap rows (dashed lines leave some columns empty, so a window is pooled). Exactly n groups must be
    found; the group number `which` (0 = top) is read at its median row, with an interval of half its
    median thickness plus the calibration misfit and half the spread of the group."""
    X, Y = cal.X, cal.Y
    out = []
    for x in at:
        c = cal.col(x, Y.px(0.5 * (y_lo + y_hi)))
        r_top, r_bot = int(Y.px(y_hi)), int(Y.px(y_lo))
        pts = []
        for k in range(int(c) - win, int(c) + win + 1):
            for a, b in runs(d[:, k], r_top, r_bot):
                pts.append(((a + b - 1) / 2.0, b - a))
        pts.sort()
        groups, cur = [], []
        for p in pts:
            if cur and p[0] - cur[-1][0] > min_gap:
                groups.append(cur)
                cur = []
            cur.append(p)
        if cur:
            groups.append(cur)
        if from_bottom is not None:  # any number of lines above: take the k-th from the bottom
            if len(groups) <= from_bottom:
                out.append({"x": x, "y": None, "note": f"only {len(groups)} lines here"})
                continue
            g = groups[-1 - from_bottom]
            which, n = len(groups) - 1 - from_bottom, len(groups)
        elif len(groups) != n:
            out.append({"x": x, "y": None, "note": f"found {len(groups)} lines here, not {n}: they touch or "
                                                   f"cross"})
            continue
        else:
            g = groups[which]
        rows = [p[0] for p in g]
        r = float(np.median(rows))
        w = float(np.median([p[1] for p in g]))
        half = 0.5 * w + Y.misfit_px + 0.5 * (np.percentile(rows, 90) - np.percentile(rows, 10))
        out.append(reading(x, r, c, half, cal, f"line {which + 1} of {n} from the top; {cal.note()}"))
    return out


def band(d, cal, at, y_lo, y_hi, win=6, max_gap=60, note=""):
    """Lines that run together, read as one band: at each x, the ink between y_lo and y_hi in the
    columns within +-win of x (the group of runs nearest the middle of the window's ink, joined across
    gaps of up to max_gap rows); y is the middle of the band and its interval the band itself, widened
    by the calibration misfit."""
    X, Y = cal.X, cal.Y
    out = []
    for x in at:
        c = cal.col(x, Y.px(0.5 * (y_lo + y_hi)))
        r_top, r_bot = int(Y.px(y_hi)), int(Y.px(y_lo))
        rs = sorted(r for k in range(int(c) - win, int(c) + win + 1) for r in runs(d[:, k], r_top, r_bot))
        if not rs:
            out.append({"x": x, "y": None, "note": "no ink here"})
            continue
        groups, cur = [], [rs[0]]
        for a, b in rs[1:]:
            if a - max(e for _, e in cur) > max_gap:
                groups.append(cur)
                cur = []
            cur.append((a, b))
        groups.append(cur)
        g = max(groups, key=lambda g: sum(b - a for a, b in g))
        top, bot = min(a for a, _ in g), max(b for _, b in g) - 1
        r = 0.5 * (top + bot)
        half = 0.5 * (bot - top) + Y.misfit_px
        out.append(reading(x, r, c, half, cal, f"band of the lines, rows {top}-{bot}; {cal.note()}{note}"))
    return out


class Lin:
    """value = a + b * pixel, fitted through (pixel, value) marks."""

    def __init__(self, marks):
        p = np.array([m[0] for m in marks], float)
        v = np.array([m[1] for m in marks], float)
        self.b, self.a = np.polyfit(p, v, 1)
        self.misfit_px = float(np.max(np.abs(p - (v - self.a) / self.b)))
        self.marks = marks

    def val(self, p):
        return float(self.a + self.b * p)

    def px(self, v):
        return float((v - self.a) / self.b)


def runs(col_mask, r0=0, r1=None):
    """(start, end exclusive) of dark runs in one column between rows r0 and r1."""
    v = col_mask[r0:r1]
    out = []
    i, n = 0, len(v)
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]:
                j += 1
            out.append((r0 + i, r0 + j))
            i = j
        else:
            i += 1
    return out


def trace(d, c_start, r_start, c_end, r_lo, r_hi, max_jump=12, width=None, prefer=None, max_gap=60,
          exclude=None, monotone=None):
    """Follow one curve column by column from (c_start, r_start) to c_end (either direction).
    At each column the dark run nearest the predicted row is taken; columns with no run near enough
    are gaps (dashed lines), bridged by the last slope. `prefer='low'` / 'high' takes, when a run is
    much thicker than the line (another line or marker merged with it), the centre one line width up
    from its lower edge / down from its upper edge. Returns {col: (row, thick)} for columns with ink."""
    step = 1 if c_end >= c_start else -1
    out = {}
    row, slope, last_c = float(r_start), 0.0, c_start
    for c in range(c_start, c_end + step, step):
        if exclude is not None and exclude(c):
            continue
        pred = row + slope * (c - last_c)
        rs = [(a, b) for a, b in runs(d[:, c], r_lo, r_hi)]
        best, bd = None, None
        for a, b in rs:
            ctr = (a + b - 1) / 2.0
            if width is not None and (b - a) > 1.8 * width:
                if prefer == "low":
                    ctr = b - 1 - (width - 1) / 2.0
                elif prefer == "high":
                    ctr = a + (width - 1) / 2.0
            dd = abs(ctr - pred)
            if out and monotone == "down" and ctr < row - 1:  # the curve only falls (rows grow) to the right
                continue
            if out and monotone == "up" and ctr > row + 1:
                continue
            if bd is None or dd < bd:
                best, bd, bab = ctr, dd, (a, b)
        jump = max_jump * (1 + min(abs(c - last_c), max_gap) / 10.0)
        if best is not None and bd <= jump:
            if abs(c - last_c) > 0:
                hist = [(k, out[k][0]) for k in out if abs(k - c) <= 40] + [(c, best)]
                if len(hist) >= 6:
                    slope = float(np.polyfit([h[0] for h in hist], [h[1] for h in hist], 1)[0])
                else:
                    slope = (best - row) / (c - last_c)
                if monotone == "down":
                    slope = max(slope, 0.0)
                elif monotone == "up":
                    slope = min(slope, 0.0)
            row, last_c = best, c
            out[c] = (best, (bab[1] - bab[0]) > (1.8 * width if width else 1e9))
        elif abs(c - last_c) > max_gap:
            break
    return out


def at_col(tr, c, half=4):
    """Row of a traced curve at column c: the median of traced rows within +-half columns, with the
    spread; None if the curve has no ink there."""
    rows = [tr[k][0] for k in range(int(round(c)) - half, int(round(c)) + half + 1) if k in tr]
    if len(rows) < 2:
        return None, None
    return float(np.median(rows)), float(np.max(rows) - np.min(rows))


def line_width(d, c, r_lo, r_hi):
    rs = runs(d[:, c], r_lo, r_hi)
    return min((b - a) for a, b in rs) if rs else None
