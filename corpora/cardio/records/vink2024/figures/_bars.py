"""Shared reading code for the bar charts of vink2024 (GraphPad Prism style: filled bars with a thick black
outline, a black SD error bar with caps above and below the bar top, black dots for the participants).
All figures are embedded rasters; they are read at the crop and dpi given in figures.yaml.

Ink: a pixel is "black" when its brightest channel is below INK (110). The coloured fills (red, blue, the
pinks and the dark purple of 'Negative ICFT', whose red channel is about 170) are not black.

Calibration (y): the y axis is the leftmost column group whose longest vertical black run exceeds 40% of
the image height. Tick marks point left from it: in the columns just left of the axis, each row's black run
leftwards is measured; consecutive rows with a run form a tick. Major (labelled) ticks are those at least
70% as long as the longest; minor ticks are dropped. Their row centres, top to bottom, are matched to the
printed labels and a straight line value = a + b*row is fitted; the rms misfit (px) widens every interval.

Bars: the x axis is the lowest row group whose longest horizontal black run exceeds 40% of the width. In
each column right of the y axis, the black run going up from just above the x axis is measured: a bar's
left and right outlines are column groups with a run longer than MIN_EDGE of the plot height. Groups are
paired left to right into bars, so bars are numbered 1, 2, ... from the left of the panel.

Bar value: the top outline is the topmost group of rows that is black over at least 90% of the bar's
interior and over at least 80% of its leftmost and rightmost 15% (an error bar cap is centred and
narrower, and does not reach the outlines). The value is the outline's outer (top) edge: on the image,
the midpoint of each SD error bar (symmetric about the mean) falls on that edge, not on the outline's
centre (Fig. 2A: within 2 px in all six bars, while the centre is 6-7 px lower). The interval is +-(the
edge blur, i.e. the number of grey rows just above the outline in the median column, at least 2 px) and the
misfit, widened to include the error bar's midpoint when both caps are found.

Error bars (drawn thinner, so greyer after resampling: read with the looser mask brightest channel < 170;
the dark purple fill's red channel is about 170 and its antialiased edges are not read as stem): the stem is the black column(s) at the bar's centre just above the top band. Walking along the
stem up (and down, inside the bar), a cap row is a row whose black run through the stem reaches at least
CAP_HALF of the interior width on both sides (a dot on the stem is narrower). The farthest cap group still
joined to the band by the stem is the end; its centre row is the end's value, its half thickness plus
1.5 px the precision. A lower end not found (hidden) is taken as the mirror of the upper.
"""

import numpy as np

INK = 110
STEM_INK = 170
MIN_EDGE = 0.06
CAP_HALF = 0.22


def ink_mask(image):
    return np.asarray(image)[..., :3].max(axis=2) < INK


def _groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return out


def _longest_run(v):
    best = cur = 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


class Axis:
    def __init__(self, rows, labels):
        self.rows = np.asarray(rows, float)
        self.labels = np.asarray(labels, float)
        b, a = np.polyfit(self.rows, self.labels, 1)
        self.a, self.b = a, b
        res = self.labels - (a + b * self.rows)
        self.misfit = max(float(np.sqrt(np.mean((res / b) ** 2))), 0.5)

    def val(self, row):
        return float(self.a + self.b * row)

    def interval(self, row, tol_px):
        t = tol_px + self.misfit
        v1, v2 = self.val(row - t), self.val(row + t)
        return min(v1, v2), max(v1, v2)


def calibrate(image, labels):
    ink = ink_mask(image)
    H, W = ink.shape
    vr = np.array([_longest_run(ink[:, c]) for c in range(W)])
    axis_cols = [g for g in _groups(np.where(vr > 0.4 * H)[0])]
    yc = axis_cols[0]
    c0 = yc[0]
    rows_on = np.where(ink[:, yc].any(axis=1))[0]
    lens = np.zeros(H, int)
    for r in range(rows_on.min(), rows_on.max() + 1):
        n = 0
        c = c0 - 2
        while c >= 0 and ink[r, c]:
            n += 1
            c -= 1
        lens[r] = n
    ticks = []
    for g in _groups(np.where(lens > 4)[0]):
        ticks.append(((g[0] + g[-1]) / 2.0, int(max(lens[g]))))
    longest = max(t[1] for t in ticks)
    major = [t[0] for t in ticks if t[1] >= 0.7 * longest]
    if len(major) != len(labels):
        raise RuntimeError(f"expected {len(labels)} major y ticks, found {major} (all: {ticks})")
    ax = Axis(major, labels)
    # the x axis (the bars' base): the long horizontal line nearest the row of value 0; when the axis is
    # dotted (no long line there), a band of +-3 px around that row
    zero = (0.0 - ax.a) / ax.b
    hr = np.array([_longest_run(ink[r, :]) for r in range(H)])
    xg = _groups(np.where(hr > 0.4 * W)[0])
    near = [g for g in xg if abs((g[0] + g[-1]) / 2.0 - zero) < 15]
    xr = near[0] if near else list(range(int(round(zero)) - 3, int(round(zero)) + 4))
    return ax, ink, yc, xr


def find_bars(ink, yc, xr):
    H, W = ink.shape
    r0 = xr[0] - 3
    plot_h = r0 - 0
    runs = np.zeros(W, int)
    for c in range(yc[-1] + 6, W):
        n = 0
        r = r0
        while r >= 0 and ink[r, c]:
            n += 1
            r -= 1
        runs[c] = n
    edges = _groups(np.where(runs > MIN_EDGE * plot_h)[0])
    bars = []
    for i in range(0, len(edges) - 1, 2):
        bars.append((edges[i], edges[i + 1]))
    return bars


def _cap_centre(ink, g, sc):
    """Within a group of cap rows (a dot touching the cap may join it), the rows at least 90% as wide as the
    widest are the cap: return their centre and half thickness."""
    w = {r: _half(ink, r, sc) for r in g}
    m = max(w.values())
    rows = [r for r in g if w[r] >= 0.9 * m]
    return (rows[0] + rows[-1]) / 2.0, (rows[-1] - rows[0] + 1) / 2.0


def _half(ink, r, sc):
    left = 0
    while ink[r, sc - left - 1]:
        left += 1
    right = 0
    while ink[r, sc + right + 1]:
        right += 1
    return min(left, right)


def _cap_rows(ink, rows, sc, half_min):
    out = []
    for r in rows:
        left = 0
        c = sc
        while ink[r, c - left - 1]:
            left += 1
        right = 0
        while ink[r, sc + right + 1]:
            right += 1
        if left >= half_min and right >= half_min:
            out.append(r)
    return out


def _stem_end(ink, start, step, sc, stop):
    """Walk from row start in direction step while the stem (sc +-2) is black; return the last black row."""
    r = start
    last = None
    while 0 <= r < ink.shape[0] and r != stop and ink[r, sc - 2: sc + 3].any():
        last = r
        r += step
    return last


def read_bar(ax, ink, bar, xr, k, x, image):
    (le, re_) = bar
    il, ir = le[-1] + 1, re_[0] - 1
    wi = ir - il + 1
    q = max(int(0.15 * wi), 2)
    # the side outlines rise from the x axis to the bar top: search for the top outline only near where they end
    tops = []
    for c in list(le) + list(re_):
        r = xr[0] - 3
        while r >= 0 and ink[r, c]:
            r -= 1
        tops.append(r + 1)
    edge_top = int(np.median(tops))
    band = []
    for r in range(max(edge_top - 8, 0), xr[0] - 5):
        row = ink[r, il: ir + 1]
        if row.mean() > 0.9 and row[:q].mean() > 0.8 and row[-q:].mean() > 0.8:
            band.append(r)
    g = _groups(band)[0]
    bt, bb = g[0], g[-1]
    top = float(bt)
    y = ax.val(top)
    # precision: the width of the grey transition just above the outline (the raster's blur), at least 2 px
    bright = np.median(np.asarray(image)[..., :3].max(axis=2)[:, il + q: ir - q + 1], axis=1)
    ink = np.asarray(image)[..., :3].max(axis=2) < STEM_INK   # error bars are thinner, hence greyer
    blur = sum(1 for r in range(max(bt - 15, 0), bt) if 110 <= bright[r] <= 235)
    tol = max(2.0, float(blur))
    lo, hi = ax.interval(top, tol)
    note = (f"bar {k}: top outline rows {bt}-{bb}, value at its outer (top) edge {top:.1f}; edge blur {blur} px; "
            f"misfit {ax.misfit:.2f} px")
    out = {"x": x, "y": y, "lo": lo, "hi": hi, "px": [float((il + ir) / 2.0), top]}
    cc = (il + ir) // 2
    def run_up(c):
        n, r = 0, bt - 1
        while r >= 0 and ink[r, c]:
            n += 1
            r -= 1
        return n

    runs = {c: run_up(c) for c in range(cc - wi // 4, cc + wi // 4 + 1)}
    best = max(runs.values())
    if best < 6:
        out["note"] = note + "; no error bar above the bar"
        return out
    # the stem is a few px wide: the middle of the adjacent columns whose run is near the longest
    sc0 = max(runs, key=runs.get)
    good = [c for c in range(sc0 - 8, sc0 + 9) if c in runs and runs[c] >= 0.8 * best]
    sc = int(round(np.mean(good)))
    half_min = CAP_HALF * wi
    up_end = _stem_end(ink, bt - 1, -1, sc, -1)
    caps_up = _groups(_cap_rows(ink, range(up_end, bt - 2), sc, half_min))
    if not caps_up:
        out["note"] = note + "; black ink touches the bar top (a dot) but no error bar cap is found: no error bar read"
        return out
    cap_hi, th = _cap_centre(ink, caps_up[0], sc)
    tol_hi = th + tol
    hi_end = ax.val(cap_hi)
    hi_out = max(ax.interval(cap_hi, tol_hi))
    low_end = _stem_end(ink, bb + 1, 1, sc, xr[0] - 2)
    caps_lo = _groups(_cap_rows(ink, range(bb + 3, low_end + 1), sc, half_min)) if low_end else []
    if caps_lo:
        cap_lo, th = _cap_centre(ink, caps_lo[-1], sc)
        tol_lo = th + tol
        lo_end = ax.val(cap_lo)
        lo_out = min(ax.interval(cap_lo, tol_lo))
        mid = (cap_hi + cap_lo) / 2.0
        note += (f"; error bar caps at rows {cap_hi:.1f} (upper) and {cap_lo:.1f} (lower), midpoint {mid:.1f}, "
                 f"{mid - top:+.1f} px from the top edge")
        # the SD bar is symmetric about the mean: where its midpoint and the top edge differ, both are allowed
        lo = min(lo, min(ax.interval(mid, 2.0)))
        hi = max(hi, max(ax.interval(mid, 2.0)))
        out.update({"lo": lo, "hi": hi})
    else:
        cap_lo = 2 * top - cap_hi
        lo_end = 2 * y - hi_end
        lo_out = 2 * y - hi_out
        note += f"; upper cap at row {cap_hi:.1f}; no lower cap found below the top outline, taken as the mirror of the upper"
    out.update({"bar_lo": lo_end, "bar_hi": hi_end, "bar_lo_outer": min(lo_out, lo_end), "bar_hi_outer": max(hi_out, hi_end),
                "px_lo": cap_hi, "px_hi": cap_lo, "note": note})
    return out


def read(image, at, labels, order, expect=None):
    """labels: y tick labels top to bottom; order: {x value: bar number from the left}; expect: number of bars."""
    ax, ink, yc, xr = calibrate(image, labels)
    bars = find_bars(ink, yc, xr)
    if expect is not None and len(bars) != expect:
        raise RuntimeError(f"expected {expect} bars, found {len(bars)}: {[(b[0][0], b[1][-1]) for b in bars]}")
    out = []
    for xv in at:
        x = float(xv)
        k = order[int(round(x))]
        out.append(read_bar(ax, ink, bars[k - 1], xr, k, x, image))
    return out
