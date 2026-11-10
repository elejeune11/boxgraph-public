# Shared reading code for the line plots of yong2025 (our own code; no values from the paper
# except the tick labels each reading file passes in).
#
# Calibration: the axis lines are the longest dark vertical / horizontal runs in the crop; the
# tick marks are short dark runs just outside them (left of a left y axis, right of a right y
# axis, below the x axis). The ticks found are matched in order to the tick values given by
# the reading file (None for an unlabelled tick); a straight line is fitted through the
# labelled ones and its worst residual (px, at least 0.5) widens every interval.
#
# Curve: pixels of one colour inside the plot area. Black curves are opened with a horizontal
# element so thin vertical lines (the dashed and solid phase markers) drop out. Dashed and
# solid curves of the same colour are separated by the width of their connected pieces. The
# curve is traced column by column (the run nearest the previous one), and at each x the
# reading is the centre of the run, with an interval spanning the run (line thickness) plus
# the calibration misfit. Where the curve is hidden under another one, or between dashes, the
# nearest traced columns on either side are joined and the interval spans both their runs.
import numpy as np
from scipy import ndimage as ndi


def _mask(img, color):
    R, G, B = (img[..., k].astype(int) for k in range(3))
    mx = np.maximum(np.maximum(R, G), B)
    if color == "red":
        return (R > 170) & (G < 120) & (B < 120)
    if color == "red_strong":  # the saturated curve, not a paler reference line of the same hue
        return (R > 200) & (G < 110) & (B < 90)
    if color == "blue":
        return (B > 140) & (R < 110) & (G < 130) & (B - R > 60)
    if color == "green":
        return (G > 70) & (G - R > 30) & (G - B > 30) & (R < 110)
    if color == "black":
        return mx < 90
    if color == "purple":
        return (B > 150) & (R > 110) & (G < 130) & (B - G > 60) & (R - G > 50)
    if color == "darkred":
        return (R > 90) & (R < 200) & (G < 80) & (B < 100) & (R - G > 50)
    raise ValueError(color)


def _runs(v):
    """(start, end exclusive) of True runs in a 1-D boolean array."""
    p = np.concatenate([[0], v.astype(np.int8), [0]])
    d = np.diff(p)
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def _longest(v):
    r = _runs(v)
    return max((e - s for s, e in r), default=0)


def _cluster(idx):
    """Group consecutive integers -> list of (first, last)."""
    out = []
    for i in sorted(idx):
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(x) for x in out]


class Axis:
    def __init__(self, marks):
        p = np.array([m[0] for m in marks], float)
        v = np.array([m[1] for m in marks], float)
        self.b, self.a = np.polyfit(p, v, 1)
        self.misfit = max(float(np.max(np.abs(p - (v - self.a) / self.b))), 0.5)

    def val(self, p):
        return self.a + self.b * p

    def pix(self, v):
        return (v - self.a) / self.b


def _ticks(d, line, side, along, tick_win, min_w=1):
    """Tick centres beside an axis line. line = (first, last) index of the line's thickness;
    side = -1 (before the line) or +1 (after); along = (lo, hi) range along the axis.
    d is the dark mask already transposed so ticks are columns-of-rows."""
    if side < 0:
        win = d[:, line[0] - tick_win:line[0] - 1]
    else:
        win = d[:, line[1] + 2:line[1] + 1 + tick_win]
    hit = np.where(win.mean(axis=1) >= 0.85)[0]
    hit = hit[(hit >= along[0]) & (hit <= along[1])]
    return [(a + b + 1) / 2.0 for a, b in _cluster(hit) if min_w <= b - a + 1 < 60]


def calibrate(img, x_vals, y_vals, y_side="left", dark=110, tick_win=8):
    d = img[..., :3].max(axis=2) < dark
    H, W = d.shape
    col_len = np.array([_longest(d[:, c]) for c in range(W)])
    row_len = np.array([_longest(d[r, :]) for r in range(H)])
    cand = [c for c in range(W // 2) if col_len[c] >= 0.6 * col_len[:W // 2].max()]
    yleft = _cluster(cand)[0]
    if y_side == "left":
        yline = yleft
    else:
        cand = [c for c in range(W // 2, W) if col_len[c] >= 0.6 * col_len[W // 2:].max()]
        yline = _cluster(cand)[-1]
    cand = [r for r in range(H // 2, H) if row_len[r] >= 0.6 * row_len[H // 2:].max()]
    xline = _cluster(cand)[-1]
    mw = 0.5 * min(yleft[1] - yleft[0] + 1, xline[1] - xline[0] + 1)
    yt = _ticks(d, yline, -1 if y_side == "left" else +1, (0, xline[1] + 4), tick_win, mw)
    right_cols = [c for c in range(W // 2, W) if col_len[c] >= 0.6 * col_len[yleft[0]]]
    xmax = _cluster(right_cols)[-1][1] + 4 if right_cols else W - 1  # a right y axis ends the x axis
    xt = _ticks(d.T, xline, +1, (yleft[0] - 4, xmax), tick_win, mw)
    yt = sorted(yt, reverse=True)  # bottom first, as the values increase
    xt = sorted(xt)
    if len(yt) != len(y_vals) or len(xt) != len(x_vals):
        raise ValueError(f"ticks found x {xt} (want {len(x_vals)}), y {yt} (want {len(y_vals)}); "
                         f"x axis rows {xline}, y axis cols {yline}")
    xa = Axis([(p, v) for p, v in zip(xt, x_vals) if v is not None])
    ya = Axis([(p, v) for p, v in zip(yt, y_vals) if v is not None])
    return xa, ya, xline, yline


def curve_mask(img, color, area, parts=None, part_len=None, open_w=None):
    m = _mask(img, color)
    r0, r1, c0, c1 = area
    keep = np.zeros_like(m)
    keep[r0:r1, c0:c1] = True
    m &= keep
    if color == "black":
        m = ndi.binary_opening(m, structure=np.ones((1, open_w or 9), bool))
    else:
        m = ndi.binary_opening(m, structure=np.ones((3, 3), bool))
    if parts is not None:
        lab, n = ndi.label(m, structure=np.ones((3, 3), bool))
        sl = ndi.find_objects(lab)
        widths = np.array([s[1].stop - s[1].start for s in sl])
        sel = np.zeros(n + 1, bool)
        if parts == "long":
            sel[1:] = widths >= part_len
        else:
            sel[1:] = (widths < part_len) & (widths >= 4)
        m = sel[lab]
    return m


def trace(m, c0, c1, start=None, max_jump=0.15):
    """Column -> (top, bottom exclusive) of the curve's run, following the run nearest the last."""
    out = {}
    prev = start
    for c in range(c0, c1):
        rs = _runs(m[:, c])
        if not rs:
            continue
        if prev is None:
            if len(rs) != 1:
                continue
            s, e = rs[0]
        else:
            s, e = min(rs, key=lambda r: abs((r[0] + r[1]) / 2 - prev))
            if abs((s + e) / 2 - prev) > max_jump * m.shape[0]:
                continue
        out[c] = (s, e)
        prev = (s + e) / 2
    return out


def read_curve(img, at, color, x_vals, y_vals, y_side="left", parts=None, part_len=None, top=0,
               max_gap=0.06, open_w=None, start_row=None, right=None, dark=110, tick_win=8, below=False,
               under=None, on_axis=False, drop_hlines=False, max_jump=0.15):
    """under: colours of curves drawn over this one; where this curve is hidden, it is read as the
    run of those curves nearest the traced line (it lies beneath them)."""
    xa, ya, xline, yline = calibrate(img, x_vals, y_vals, y_side=y_side, dark=dark, tick_win=tick_win)
    H, W = img.shape[:2]
    if y_side == "left":
        c0, c1 = yline[1] + 3, (right or W)
    else:
        c0, c1 = 0, yline[0] - 2
    bottom = xline[0] - 4  # clear of the axis line's anti-aliased edge
    if below:  # the x axis is drawn at y = 0 inside the plot: search down to the end of the y axis line
        col = img[..., :3].max(axis=2)[:, yline[0] + 1] < dark
        bottom = max(e for s_, e in _runs(col)) - 2
    area = (top, bottom, c0, c1)
    if on_axis and color != "black":  # a coloured line drawn over the x axis line is still visible there
        area = (top, xline[1] + 1, c0, c1)
    m = curve_mask(img, color, area, parts=parts, part_len=part_len, open_w=open_w)
    if drop_hlines:  # straight horizontal reference lines (a printed mean) are not the curve
        for r in range(m.shape[0]):
            for a, b in _runs(m[r]):
                if b - a >= 0.4 * (c1 - c0):
                    m[r, a:b] = False
        m = ndi.binary_opening(m, structure=np.ones((3, 3), bool))
    tr = trace(m, c0, c1, start=start_row, max_jump=max_jump)
    hidden = set()
    if under:
        um = np.zeros_like(m)
        for uc in under:
            um |= curve_mask(img, uc, area)
        orig = dict(tr)
        for order in (range(c0, c1), range(c1 - 1, c0 - 1, -1)):  # forward, then backward for a hidden start
            prev = None
            for c in order:
                if c in tr:
                    prev = (tr[c][0] + tr[c][1]) / 2
                    continue
                if prev is None:
                    continue
                rs = _runs(um[:, c] | m[:, c])
                if not rs:
                    continue
                s_, e_ = min(rs, key=lambda r: abs((r[0] + r[1]) / 2 - prev))
                if abs((s_ + e_) / 2 - prev) > 0.03 * m.shape[0]:
                    continue
                tr[c] = (s_, e_)
                hidden.add(c)
                prev = (s_ + e_) / 2
        del orig
    on_ax = set()
    if on_axis:  # where the curve runs along the x axis line it cannot be told from it: read the line
        known = np.array(sorted(tr))
        for c in range(c0, c1):
            if c in tr or len(known) == 0:
                continue
            k = known[np.argmin(np.abs(known - c))]
            if tr[k][1] >= xline[0] - 40:
                tr[c] = (xline[0], xline[1] + 1)
                on_ax.add(c)
    cols = np.array(sorted(tr))
    gap_px = max_gap * abs(xa.pix(x_vals[-1] if x_vals[-1] is not None else 1) - xa.pix(x_vals[0] or 0))
    out = []
    for x in at:
        c = int(np.floor(xa.pix(x)))
        note = ""
        if c in tr:
            s, e = tr[c]
            yc = (s + e) / 2.0
            top_r, bot_r = s, e
            if c in hidden:
                note = "hidden under the curves drawn over it: read as their joint line"
            if c in on_ax:
                note = "lies on the x axis line: read as the line's extent"
        else:
            left = cols[cols < c]
            rgt = cols[cols > c]
            if len(left) == 0 or len(rgt) == 0 or c - left[-1] > gap_px or rgt[0] - c > gap_px:
                out.append({"x": x, "y": None, "note": "curve not found at this column"})
                continue
            cl, cr = left[-1], rgt[0]
            (sl, el), (sr, er) = tr[cl], tr[cr]
            ml, mr = (sl + el) / 2, (sr + er) / 2
            yc = ml + (mr - ml) * (c - cl) / (cr - cl)
            top_r, bot_r = min(sl, sr), max(el, er)
            note = f"gap of {cr - cl} px (dash or hidden under another curve) bridged"
        pad = ya.misfit + 0.5
        y = ya.val(yc)
        v1, v2 = ya.val(top_r - pad), ya.val(bot_r + pad)
        lo, hi = min(v1, v2), max(v1, v2)
        # the x misfit moves the column: add the change of the curve across it
        dx = int(np.ceil(xa.misfit))
        for cc in (c - dx, c + dx):
            if cc in tr:
                s2, e2 = tr[cc]
                for rr in (s2 - pad, e2 + pad):
                    lo, hi = min(lo, ya.val(rr)), max(hi, ya.val(rr))
        out.append({"x": x, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [c + 0.5, yc],
                    "px_lo": float(top_r), "px_hi": float(bot_r),
                    "note": (note + "; " if note else "") + f"calibration misfit x {xa.misfit:.2f} px, y {ya.misfit:.2f} px"})
    return out


def read_bars(img, at, y_vals, series, n_series=2, edge="top", dark=110, tick_win=8):
    """Grouped bars, grey and red side by side. Bars are the runs of columns whose ink just above
    the x axis is grey (series 0) or red (series 1); `series` picks which. edge='top' reads the bar's
    top; edge='split' reads the boundary between its darker lower segment and lighter upper one.
    The fill has a dotted texture, so each row's colour is the median over the bar's middle half.
    x of each reading is the bar's position among its series (1, 2, ...)."""
    d = img[..., :3].max(axis=2) < dark
    H, W = d.shape
    col_len = np.array([_longest(d[:, c]) for c in range(W)])
    row_len = np.array([_longest(d[r, :]) for r in range(H)])
    cand = [c for c in range(W // 2) if col_len[c] >= 0.6 * col_len[:W // 2].max()]
    yline = _cluster(cand)[0]
    cand = [r for r in range(H // 2, H) if row_len[r] >= 0.6 * row_len[H // 2:].max()]
    xline = _cluster(cand)[-1]
    mw = 0.5 * min(yline[1] - yline[0] + 1, xline[1] - xline[0] + 1)
    yt = sorted(_ticks(d, yline, -1, (0, xline[1] + 4), tick_win, mw), reverse=True)
    if len(yt) != len(y_vals):
        raise ValueError(f"y ticks found {yt}, want {len(y_vals)}")
    ya = Axis([(p, v) for p, v in zip(yt, y_vals) if v is not None])
    im = img[..., :3].astype(int)
    row = im[xline[0] - 12, :, :]
    R, G, B = row[:, 0], row[:, 1], row[:, 2]
    grey = (np.abs(R - B) < 25) & (R < 200)
    red = (R > 180) & (R - G > 60)
    cls = np.where(grey, 0, np.where(red, 1, -1))
    cls[:yline[1] + 3] = -1
    bars = []
    for c in range(W):
        if cls[c] < 0:
            continue
        if bars and bars[-1][0] == cls[c] and bars[-1][2] == c - 1:
            bars[-1][2] = c
        else:
            bars.append([int(cls[c]), c, c])
    bars = [b for b in bars if b[2] - b[1] > 0.02 * W and b[0] == series]
    out = []
    for i, (_, a, b) in enumerate(bars):
        w = b - a
        cs = slice(a + w // 4, b - w // 4)
        med = np.median(im[:xline[0] - 2, cs, :], axis=1)  # rows x RGB
        ink = med.min(axis=1) < 225
        rows = np.where(ink)[0]
        # the bar is the run of ink rows that reaches the axis
        top = rows[-1]
        while top - 1 >= 0 and ink[top - 1]:
            top -= 1
        if edge == "top":
            e = top
            note = "bar top"
        else:
            lum = med.mean(axis=1) if series == 0 else med[:, 1]
            darkpart = lum < (130 if series == 0 else 100)
            r = xline[0] - 8  # clear of the axis line's anti-aliased edge
            while r > top and darkpart[r]:
                r -= 1
            e = r + 1
            note = "boundary between the dark (lower) and light (upper) segment"
        pad = ya.misfit + 2.0  # the anti-aliased edge
        y = ya.val(e)
        v1, v2 = ya.val(e - pad), ya.val(e + pad)
        out.append({"x": float(i + 1), "y": float(y), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [(a + b) / 2.0, float(e)], "px_lo": float(e - pad), "px_hi": float(e + pad),
                    "note": f"{note}; bar {i + 1} of its series from the left; y misfit {ya.misfit:.2f} px"})
    return out
