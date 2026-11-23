"""Shared reading code for the figures of baker2015. Everything a reading returns comes from the
rendered crop; the only numbers typed in are the printed tick labels, listed bottom to top.

- axes: the axis lines are the longest straight runs of dark ink; tick marks are short runs
  perpendicular to them, outside the plot. The tick labels are matched to the ticks in order and a
  straight line is fitted (pixel against value); its largest residual, in pixels, is the misfit
  carried into every interval.
- bars: a bar is a run of columns holding its fill colour and standing on the x axis; its value is
  its top edge. Its error bar is the thin stem above the bar's centre; the upper end is the centre of
  the cap. Where the lower half is hidden inside the bar (all bars here), it is taken as the mirror of
  the upper half, and the reading says so.
- markers: blobs of a marker colour; error bars followed up and down along the stem through the
  marker's centre.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def runs(idx):
    idx = np.asarray(idx)
    if len(idx) == 0:
        return []
    cuts = np.nonzero(np.diff(idx) > 1)[0] + 1
    return [(int(g[0]), int(g[-1])) for g in np.split(idx, cuts)]


def dark(img, thr=110.0, max_sat=80.0):
    f = img.astype(float)
    sat = f.max(axis=2) - f.min(axis=2)
    return (f.mean(axis=2) < thr) & (sat < max_sat)


def near(img, rgb, tol):
    d = np.sqrt(((img.astype(float) - np.array(rgb, float)) ** 2).sum(axis=2))
    return d < tol


def longest_run(v):
    if not v.any():
        return 0, -1, -1
    p = np.concatenate([[0], v.astype(np.int8), [0]])
    d = np.diff(p)
    s, e = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    k = int(np.argmax(e - s))
    return int(e[k] - s[k]), int(s[k]), int(e[k] - 1)


def hlines(mask, min_len):
    """Horizontal straight lines: bands of rows whose longest run >= min_len -> [(r0, r1, c0, c1)]."""
    hit = {}
    for r in range(mask.shape[0]):
        n, a, b = longest_run(mask[r])
        if n >= min_len:
            hit[r] = (a, b)
    out = []
    for r0, r1 in runs(sorted(hit)):
        c0 = int(np.median([hit[r][0] for r in range(r0, r1 + 1)]))
        c1 = int(np.median([hit[r][1] for r in range(r0, r1 + 1)]))
        out.append((r0, r1, c0, c1))
    return out


def vlines(mask, min_len):
    """Vertical straight lines -> [(c0, c1, r0, r1)]."""
    return hlines(mask.T, min_len)


class Axis:
    """A fitted axis: pixel <-> value (linear or log10)."""

    def __init__(self, px, values, log=False, what=""):
        px = np.asarray(px, float)
        v = np.log10(np.asarray(values, float)) if log else np.asarray(values, float)
        if len(px) != len(v) or len(px) < 2:
            raise ValueError(f"axis {what}: {len(px)} marks found for {len(v)} labels: {list(np.round(px, 1))}")
        self.log = log
        self.slope, self.icpt = np.polyfit(v, px, 1)
        self.misfit = float(np.max(np.abs(np.polyval([self.slope, self.icpt], v) - px))) if len(px) > 2 else 0.0
        self.px = px

    def to_px(self, value):
        u = np.log10(value) if self.log else value
        return self.icpt + self.slope * u

    def to_val(self, p):
        u = (p - self.icpt) / self.slope
        return float(10 ** u if self.log else u)


def side_ticks(ink, line, along, side, min_len=10, max_len=90, max_thick=24):
    """Tick marks on an axis line. line: (a0, a1, s0, s1) as returned by hlines (along='row' axis,
    i.e. a horizontal x axis) or vlines (a vertical y axis). side: 'out' direction, +1 or -1 across
    the line. Returns tick centres along the line."""
    m = ink if along == "x" else ink.T
    a0, a1, s0, s1 = line
    lens = {}
    for c in range(max(s0 - 30, 0), min(s1 + 31, m.shape[1])):
        r = (a1 + 1) if side > 0 else (a0 - 1)
        n = 0
        while 0 <= r < m.shape[0] and m[r, c]:
            n += 1
            r += side
        if min_len <= n <= max_len:
            lens[c] = n
    return [(a + b) / 2.0 for a, b in runs(sorted(lens)) if b - a + 1 <= max_thick]


def frame(ink, min_frac=0.35):
    """The y-axis line (leftmost long vertical) and the x-axis line (lowest long horizontal)."""
    H, W = ink.shape
    vs = vlines(ink, int(min_frac * H))
    hs = hlines(ink, int(min_frac * W))
    if not vs or not hs:
        raise ValueError("axis lines not found")
    vs = [v for v in vs if v[1] - v[0] < 30]          # thin lines only (not a black bar)
    yl = min(vs, key=lambda v: v[0])
    xl = max(hs, key=lambda h: h[1])
    return yl, xl


def y_axis(ink, yl, values, log=False, min_len=10, max_len=90, keep=None):
    t = side_ticks(ink, yl, "y", -1, min_len, max_len)
    if keep is not None:
        t = [p for p in t if keep(p)]
    rows = sorted(t, reverse=True)
    return Axis(rows, values, log=log, what=f"y ticks {[round(r) for r in rows]}")


def x_axis(ink, xl, values, log=False, min_len=10, max_len=90, keep=None):
    t = side_ticks(ink, xl, "x", +1, min_len, max_len)
    if keep is not None:
        t = [p for p in t if keep(p)]
    cols = sorted(t)
    return Axis(cols, values, log=log, what=f"x ticks {[round(c) for c in cols]}")


# ------------------------------------------------------------------ bars

def follow_stem(mask, col, start_row, direction, max_gap=3, half=2):
    H = mask.shape[0]
    c0, c1 = int(round(col)) - half, int(round(col)) + half + 1
    r, last, gap = start_row, None, 0
    while 0 <= r < H:
        if mask[r, c0:c1].any():
            last, gap = r, 0
        else:
            gap += 1
            if gap > max_gap:
                break
        r += direction
    return last


def cap_centre(mask, col, end_row, direction, stem_w):
    """Row centre (and half-thickness) of the cap at the end of a stem."""
    wide = []
    for r in range(end_row, end_row - direction * max(4 * stem_w, 16), -direction):
        if r < 0 or r >= mask.shape[0]:
            continue
        line = mask[r]
        a = b = int(round(col))
        if not line[a]:
            continue
        while a > 0 and line[a - 1]:
            a -= 1
        while b < len(line) - 1 and line[b + 1]:
            b += 1
        if b - a + 1 >= 2.5 * stem_w:
            wide.append(r)
    if not wide:
        return float(end_row), 1.0
    g = runs(sorted(wide))
    a, b = min(g, key=lambda ab: min(abs(ab[0] - end_row), abs(ab[1] - end_row)))
    return (a + b) / 2.0, (b - a + 1) / 2.0


def stem_column(mask, c_lo, c_hi, rows):
    sub = mask[rows[0]:rows[1], c_lo:c_hi]
    if sub.size == 0:
        return None, 0
    prof = sub.mean(axis=0)
    idx = np.nonzero(prof > 0.6)[0]
    if len(idx) == 0:
        return None, 0
    a, b = min(runs(idx), key=lambda ab: abs((ab[0] + ab[1]) / 2 - (c_hi - c_lo) / 2))
    return c_lo + (a + b) / 2.0, b - a + 1


def find_bars(fill, base_row, min_width=25, min_height=6):
    """Bars: runs of columns whose fill reaches down to the x axis."""
    H, W = fill.shape
    ok = np.zeros(W, bool)
    for c in range(W):
        col = fill[max(base_row - 8, 0):base_row, c]
        ok[c] = col.sum() >= 3 and fill[:base_row, c].sum() >= min_height
    merged = []
    for a, b in runs(np.nonzero(ok)[0]):
        if merged and a - merged[-1][1] <= 14:                 # an error-bar stem drawn down a bar
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return [(a, b) for a, b in merged if b - a + 1 >= min_width]


def read_bar(fill, ink, yax, c0, c1, base_row, index, x_value=None, outline=False):
    w = c1 - c0 + 1
    cb = (c0 + c1) / 2.0
    cols = [c for c in range(int(c0 + 0.1 * w), int(c1 - 0.1 * w) + 1) if abs(c - cb) > 0.15 * w]
    tops = []
    for c in cols:
        r = base_row - 1
        while r > 0 and not fill[r, c] and r > base_row - 10:     # anti-aliased foot of the bar
            r -= 1
        if not fill[r, c]:
            continue
        while r > 0 and fill[r - 1, c]:                            # the run standing on the axis
            r -= 1
        tops.append(r)
    top_fill = float(np.median(tops))
    stroke = 0.0
    if outline:
        ths = []
        for c in cols:
            r, n = int(top_fill) - 1, 0
            while r >= 0 and ink[r, c]:
                n += 1
                r -= 1
            ths.append(n)
        stroke = float(np.median(ths)) if ths else 0.0
    edge = top_fill - stroke / 2.0
    prec = max(stroke / 2.0, 0.5) + 1.0 + yax.misfit
    val = yax.to_val(edge)
    lo, hi = sorted([yax.to_val(edge + prec), yax.to_val(edge - prec)])
    r = {"x": float(index if x_value is None else x_value), "y": val, "lo": lo, "hi": hi,
         "px": [cb, edge], "px_lo": edge + prec, "px_hi": edge - prec}
    notes = [f"bar top at row {edge:.0f}, y misfit {yax.misfit:.1f} px"]
    top_i = int(round(top_fill - stroke))
    sc, sw = stem_column(ink, int(c0 + 0.25 * w), int(c1 - 0.25 * w) + 1, (max(top_i - 25, 0), max(top_i - 3, 1)))
    start = top_i - 2
    if sc is None:
        # a short error bar: its cap sits just above the bar, with little or no stem between
        ci = int(round(cb))
        for rr in range(top_i - 3, max(top_i - 40, 0), -1):
            if ink[rr, ci - 2:ci + 3].any():
                sc, sw, start = float(ci), 3, rr
                notes.append("short error bar: cap found just above the bar")
                break
    if sc is None:
        r["note"] = "; ".join(notes + ["no error-bar stem above the bar (hidden in the bar or absent)"])
        return r
    up = follow_stem(ink, sc, start, -1)
    if start != top_i - 2 and top_i - up <= 10:
        # the cap lies on the bar top: the end of the bar is the middle of the cap stroke
        up_c, up_t = (up + top_i - 1) / 2.0, (top_i - up) / 2.0
        notes.append("cap drawn on the bar top")
    else:
        up_c, up_t = cap_centre(ink, sc, up, -1, sw)
    lo_row = edge + (edge - up_c)
    notes.append("lower end hidden inside the bar: taken as the mirror of the upper end")
    m = 1.0 + yax.misfit
    r.update({"bar_lo": yax.to_val(lo_row), "bar_hi": yax.to_val(up_c),
              "bar_lo_outer": yax.to_val(lo_row + up_t + m), "bar_hi_outer": yax.to_val(up_c - up_t - m),
              "px_lo": max(r["px_lo"], lo_row), "px_hi": min(r["px_hi"], up_c)})
    notes.append(f"error-bar cap at row {up_c:.0f}")
    r["note"] = "; ".join(notes)
    return r


def outlined_bars(ink, base, left, min_h=30, min_w=50, max_w=260, max_side=14):
    """White bars drawn as an outline: two thin vertical lines standing on the x axis whose tops are
    at the same row and joined by a horizontal line. Returns [(c0, c1, interior mask)]."""
    H, W = ink.shape
    hgt = np.zeros(W, int)
    for c in range(left, W):
        r = base - 1
        while r > 0 and ink[r, c]:
            r -= 1
        hgt[c] = base - 1 - r
    sides = [(a, b) for a, b in runs(np.nonzero(hgt >= min_h)[0]) if b - a + 1 <= max_side]
    out = []
    for (a1, b1), (a2, b2) in zip(sides, sides[1:]):
        if not (min_w <= a2 - b1 <= max_w):
            continue
        t1, t2 = base - 1 - int(np.max(hgt[a1:b1 + 1])), base - 1 - int(np.max(hgt[a2:b2 + 1]))
        if abs(t1 - t2) > 6:
            continue
        mid = (b1 + a2) // 2
        top = min(t1, t2)
        if not ink[top:top + 12, mid - 5:mid + 6].any():   # a top edge joins the two sides
            continue
        r = top
        while r < base and ink[r, mid - 10:mid - 4].any():
            r += 1
        f = np.zeros_like(ink)
        f[r:base, b1 + 1:a2] = True
        out.append((b1 + 1, a2 - 1, f))
    return out


def bar_panel(img, fills, ticks, ink_thr=110.0, min_width=25, log=False, x_values=None, outline=False,
              exclude_cols=None, outlined=False):
    """All bars of the given fill colours [(rgb, tol), ...], left to right, as indices 1, 2, ...
    (or x_values in that order). outlined: also white bars drawn as an outline."""
    ink = dark(img, ink_thr)
    yl, xl = frame(ink)
    yax = y_axis(ink, yl, ticks, log=log)
    base = xl[0]
    bars = []
    if outlined:
        for a, b, f in outlined_bars(ink, base, yl[1] + 4):
            bars.append((a, b, f, True))
    for rgb, tol in fills:
        f = near(img, rgb, tol)
        f[:, : yl[1] + 3] = False
        f[base:, :] = False
        if exclude_cols:
            for a, b in exclude_cols:
                f[:, a:b] = False
        for a, b in find_bars(f, base, min_width=min_width):
            bars.append((a, b, f, outline))
    bars.sort(key=lambda t: t[0])
    out = []
    for i, (a, b, f, ol) in enumerate(bars):
        xv = None if x_values is None else x_values[i]
        out.append(read_bar(f, ink, yax, a, b, base, i + 1, xv, outline=ol))
    return out


# ------------------------------------------------------------------ histograms

def histogram(img, fill_rgb, tol, yticks, xticks, ink_thr=170.0):
    """Outlined histogram bins of one fill colour. A bin's sides are the dark vertical outline strokes
    standing on the x axis; a bin is the space between two consecutive sides that holds fill colour.
    Its top is the dark top stroke found by walking up each interior column from the axis through
    anything not dark (fill, or a fitted curve drawn over the bin); the median over the interior is
    taken, at the centre of the stroke. x is the bin's centre column through the x axis."""
    ink = dark(img, ink_thr)
    yl, xl = frame(ink)
    yax = y_axis(ink, yl, yticks)
    H, W = ink.shape
    # the fitted curve is drawn over the right end of the x axis line: look for ticks along the whole
    # row, right of the y axis
    xt = sorted(p for p in side_ticks(ink, (xl[0], xl[1], yl[0], W - 31), "x", +1) if p >= yl[0] - 3)
    xax = Axis(xt, xticks, what=f"x ticks {[round(p) for p in xt]}")
    base = xl[0]
    fill = near(img, fill_rgb, tol)
    f = img.astype(float)
    curve = (f.max(axis=2) - f.min(axis=2)) > 60          # a saturated fitted curve over the bins
    # side strokes: columns that are dark in (nearly) every row just above the axis that the curve
    # does not cover
    win = slice(base - 40, base - 2)
    seen = (~curve[win, :]).sum(axis=0)
    frac = (ink[win, :] & ~curve[win, :]).sum(axis=0) / np.maximum(seen, 1)
    is_side = (frac >= 0.45) & (seen >= 8)
    is_side[: yl[1] + 3] = False
    sides = [(a, b) for a, b in runs(np.nonzero(is_side)[0]) if b - a + 1 <= 24]   # a shared edge is two strokes
    inside = fill | curve
    out = []
    for (a1, b1), (a2, b2) in zip(sides, sides[1:]):
        c0, c1 = b1 + 1, a2 - 1
        if c1 - c0 < 6 or not fill[base - 14:base - 2, c0:c1 + 1].any():
            continue                                       # a gap between bins, not a bin
        tops, strokes, hidden = [], [], 0
        for c in range(c0 + 2, c1 - 1):
            r = base - 1
            while r > 0 and ink[r, c] and not inside[r, c]:   # the axis stroke
                r -= 1
            last_curve = None
            while r > 0 and inside[r, c]:
                if curve[r, c] and not fill[r, c]:
                    last_curve = r if last_curve is None else last_curve
                else:
                    last_curve = None
                r -= 1
            k = 0
            while k < 8 and r - k > 0 and not ink[r - k, c] and not inside[r - k, c]:
                k += 1                                     # an anti-aliased row under the stroke
            if ink[r - k, c]:
                r -= k
            if ink[r, c]:
                n = 0
                while r - n > 0 and ink[r - n, c]:
                    n += 1
                tops.append(r - (n - 1) / 2.0)
                strokes.append(n)
            elif last_curve is not None:
                # the top stroke lies under the curve: somewhere between the curve's lower edge and r
                tops.append((last_curve + r) / 2.0)
                strokes.append(last_curve - r)
                hidden += 1
        if not tops:
            continue
        edge = float(np.median(tops))
        if base - edge < 8:
            continue                                       # no bin standing here: only the axis stroke
        spread = float(np.percentile(tops, 90) - np.percentile(tops, 10))
        stroke = float(np.median(strokes))
        prec = stroke / 2.0 + 1.0 + yax.misfit + spread / 2.0
        cx = (a1 + b1 + a2 + b2) / 4.0
        out.append({"x": round(xax.to_val(cx), 3) + 0.0, "y": yax.to_val(edge), "lo": yax.to_val(edge + prec),
                    "hi": yax.to_val(edge - prec), "px": [cx, edge], "px_lo": edge + prec, "px_hi": edge - prec,
                    "note": f"bin between sides at columns {(a1 + b1) / 2:.0f} and {(a2 + b2) / 2:.0f}; top stroke "
                            f"{stroke:.0f} px, spread over the bin {spread:.1f} px; y misfit {yax.misfit:.1f} px, "
                            f"x misfit {xax.misfit:.1f} px"})
    return out


# ------------------------------------------------------------------ box plots

def box_plot(img, rgb, tol, ticks, x_tick_index, n_xticks):
    """One box of a box plot, drawn in colour rgb, standing over x tick number x_tick_index (1-based,
    of n_xticks). Returns the median (y) with the whisker ends (bar_lo, bar_hi), and the quartiles."""
    ink = dark(img, 110.0)
    yl, xl = frame(ink)
    yax = y_axis(ink, yl, ticks)
    xt = sorted(side_ticks(ink, xl, "x", +1))
    xt = [c for c in xt if c > yl[1] + 5]
    if len(xt) != n_xticks:
        raise ValueError(f"{len(xt)} x ticks found, {n_xticks} expected: {xt}")
    xc = xt[x_tick_index - 1]
    half = 0.45 * (xt[1] - xt[0])
    m = near(img, rgb, tol)
    m[:, : int(xc - half)] = False
    m[:, int(xc + half):] = False
    m[xl[0] - 2:, :] = False
    lab, n = ndi.label(m)
    best, size = None, 0
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        s = int((lab[sl] == i).sum())
        if s > size and sl[1].start <= xc <= sl[1].stop:
            best, size = i, s
    comp = lab == best
    rows = np.nonzero(comp.any(axis=1))[0]
    width = np.array([longest_run(comp[r])[0] for r in range(comp.shape[0])])
    wmax = width.max()
    bands = runs(np.nonzero(width >= 0.8 * wmax)[0])
    if len(bands) != 3:
        raise ValueError(f"box edges and median: {len(bands)} wide bands found: {bands}")
    (q3a, q3b), (mda, mdb), (q1a, q1b) = bands
    q3, md, q1 = (q3a + q3b) / 2, (mda + mdb) / 2, (q1a + q1b) / 2
    caps = runs(np.nonzero((width >= 2.5 * np.median(width[q3b + 3:mda - 2] if mda - q3b > 6 else [4]))
                           & (width < 0.8 * wmax))[0])
    top_cap = caps[0] if caps and caps[0][1] < q3a else (rows.min(), rows.min())
    bot_cap = caps[-1] if caps and caps[-1][0] > q1b else (rows.max(), rows.max())
    wt, wb = (top_cap[0] + top_cap[1]) / 2, (bot_cap[0] + bot_cap[1]) / 2
    th = (mdb - mda + 1) / 2
    prec = th + 1.0 + yax.misfit
    mm = 1.0 + yax.misfit
    note = (f"box drawn in RGB {rgb}; median row {md:.0f}, quartile rows {q3:.0f} and {q1:.0f}, whisker ends "
            f"{wt:.0f} and {wb:.0f}; y misfit {yax.misfit:.1f} px")
    x = float(x_tick_index)
    med = {"x": x, "y": yax.to_val(md), "lo": yax.to_val(md + prec), "hi": yax.to_val(md - prec),
           "px": [xc, md], "px_lo": wb, "px_hi": wt,
           "bar_lo": yax.to_val(wb), "bar_hi": yax.to_val(wt),
           "bar_lo_outer": yax.to_val(wb + th + mm), "bar_hi_outer": yax.to_val(wt - th - mm), "note": note}
    q = {"q3": {"x": x, "y": yax.to_val(q3), "lo": yax.to_val(q3 + prec), "hi": yax.to_val(q3 - prec),
                "px": [xc, q3], "note": note},
         "q1": {"x": x, "y": yax.to_val(q1), "lo": yax.to_val(q1 + prec), "hi": yax.to_val(q1 - prec),
                "px": [xc, q1], "note": note}}
    return med, q


# ------------------------------------------------------------------ markers

def blobs(mask, open_px=5, min_area=30):
    m = ndi.binary_fill_holes(mask)
    if open_px > 1:
        m = ndi.binary_opening(m, structure=np.ones((open_px, open_px), bool))
    lab, n = ndi.label(m)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        blob = lab[sl] == i
        if blob.sum() < min_area:
            continue
        rr = np.nonzero(blob.any(axis=1))[0]
        cc = np.nonzero(blob.any(axis=0))[0]
        out.append(((sl[1].start + cc.min() + sl[1].start + cc.max()) / 2.0,
                    (sl[0].start + rr.min() + sl[0].start + rr.max()) / 2.0,
                    float(rr.max() - rr.min() + 1), float(cc.max() - cc.min() + 1), int(blob.sum())))
    out.sort(key=lambda t: t[0])
    return out
