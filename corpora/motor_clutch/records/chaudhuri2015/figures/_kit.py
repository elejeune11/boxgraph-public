"""Shared reading code for the figures of chaudhuri2015 (all panels except Supp. Fig. 1d, which
has its own reader, _s1d.py). Everything a reading returns comes from the rendered crop:

- axes: the axis lines are the long straight runs of grey/black ink; tick marks are the short
  runs perpendicular to them. The printed labels are matched to the ticks in order (the reading
  file lists the value of every tick, labelled or not). Where an axis has no tick marks, the
  centres of the printed labels are found instead (text blobs beside the axis) and matched to
  their values in order. A straight line (or a straight line in log10) is fitted and its
  largest residual, in pixels, is the calibration misfit carried into every interval.
- curves: each pixel is assigned to the nearest of the panel's line colours (sampled from the
  crop); a curve is traced column by column from a starting column, keeping the run of its
  colour nearest the previous centre, so labels and other curves are not taken for it.
- bars: a bar is a run of columns holding its fill colour; its value is the centre of its top
  edge (the outline stroke where there is one). Its error bar is the thin vertical stem at the
  bar's centre; each end is the centre of its cap.
- markers: the marker colour mask is hole-filled and opened so thin lines and stems vanish;
  markers are the remaining blobs, split where touching. Error bars are followed up and down
  from the marker along the stem.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


# ------------------------------------------------------------------ basics

def runs(idx):
    idx = np.asarray(idx)
    if len(idx) == 0:
        return []
    cuts = np.nonzero(np.diff(idx) > 1)[0] + 1
    return [(int(g[0]), int(g[-1])) for g in np.split(idx, cuts)]


def gray(img):
    return img.astype(float).mean(axis=2)


def dark(img, thr=120.0, max_sat=70.0):
    f = img.astype(float)
    sat = f.max(axis=2) - f.min(axis=2)
    return (f.mean(axis=2) < thr) & (sat < max_sat)


def near(img, rgb, tol):
    d = np.sqrt(((img.astype(float) - np.array(rgb, float)) ** 2).sum(axis=2))
    return d < tol


def longest_run(v):
    """(length, start, end) of the longest True run of a 1-D bool array."""
    if not v.any():
        return 0, -1, -1
    p = np.concatenate([[0], v.astype(np.int8), [0]])
    d = np.diff(p)
    s, e = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    k = int(np.argmax(e - s))
    return int(e[k] - s[k]), int(s[k]), int(e[k] - 1)


# ------------------------------------------------------------------ axes

def hlines(mask, min_len, rows=None):
    """Horizontal straight lines: bands of consecutive rows whose longest run >= min_len.
    Returns [(r0, r1, c0, c1)] (c0, c1 the extent of the longest run)."""
    H = mask.shape[0]
    rows = range(H) if rows is None else rows
    hit = {}
    for r in rows:
        n, a, b = longest_run(mask[r])
        if n >= min_len:
            hit[r] = (a, b)
    out = []
    for r0, r1 in runs(sorted(hit)):
        c0 = int(np.median([hit[r][0] for r in range(r0, r1 + 1)]))
        c1 = int(np.median([hit[r][1] for r in range(r0, r1 + 1)]))
        out.append((r0, r1, c0, c1))
    return out


def vlines(mask, min_len, cols=None):
    out = hlines(mask.T, min_len, cols)
    return [(c0, c1, r0, r1) for (c0, c1, r0, r1) in out]   # (c0, c1, r0, r1)


def _perp_ticks(mask, band, span, side, min_len, max_len, max_thick, gap0=3):
    """Tick marks on an axis line. For a horizontal line band=(r0, r1) and span=(c0, c1);
    side 'below'/'above'. Works on mask (rows, cols). Returns [(centre, length)].
    gap0: how far from the line a tick may start (a marker drawn over the line hides its root)."""
    r0, r1 = band
    H = mask.shape[0]
    lens = {}
    for c in range(max(span[0], 0), min(span[1] + 1, mask.shape[1])):
        if side == "below":
            col = mask[r1 + 1:min(r1 + 1 + max_len + 5, H), c]
        else:
            col = mask[max(r0 - max_len - 5, 0):r0, c][::-1]
        k = 0
        while k < gap0 and k < len(col) and not col[k]:
            k += 1
        n = 0
        while k + n < len(col) and col[k + n]:
            n += 1
        if min_len <= n <= max_len:
            lens[c] = n
    out = []
    for a, b in runs(sorted(lens)):
        if b - a + 1 <= max_thick:
            out.append(((a + b) / 2.0, max(lens[c] for c in range(a, b + 1))))
    return out


def ticks_x(mask, xband, span, side="below", min_len=12, max_len=120, max_thick=20):
    return _perp_ticks(mask, xband, span, side, min_len, max_len, max_thick)


def ticks_y(mask, yband, span, side="left", min_len=12, max_len=120, max_thick=20, gap0=3):
    s = {"left": "above", "right": "below"}[side]
    return _perp_ticks(mask.T, yband, span, s, min_len, max_len, max_thick, gap0)


def text_centres(mask, rows, cols, along, gap=25, min_size=8):
    """Centres of text blobs in a region, projected on one axis ('row' or 'col'): positions
    holding ink, grouped where separated by more than `gap` px."""
    sub = mask[rows[0]:rows[1], cols[0]:cols[1]]
    prof = sub.any(axis=1) if along == "row" else sub.any(axis=0)
    idx = np.nonzero(prof)[0]
    groups = []
    for a, b in runs(idx):
        if groups and a - groups[-1][1] <= gap:
            groups[-1] = (groups[-1][0], b)
        else:
            groups.append((a, b))
    off = rows[0] if along == "row" else cols[0]
    return [((a + b) / 2.0 + off, a + off, b + off) for a, b in groups if b - a + 1 >= min_size]


class Axis:
    """A fitted axis: pixel <-> value, linear or log10."""

    def __init__(self, px, values, log=False, what=""):
        px = np.asarray(px, float)
        v = np.log10(np.asarray(values, float)) if log else np.asarray(values, float)
        if len(px) != len(v) or len(px) < 2:
            raise ValueError(f"axis {what}: {len(px)} marks found for {len(v)} labels: {list(np.round(px, 1))}")
        self.log = log
        self.slope, self.icpt = np.polyfit(v, px, 1)
        self.misfit = float(np.max(np.abs(np.polyval([self.slope, self.icpt], v) - px))) if len(px) > 2 else 0.0
        self.px, self.values = px, list(values)

    def to_px(self, value):
        u = np.log10(value) if self.log else value
        return self.icpt + self.slope * u

    def to_val(self, p):
        u = (p - self.icpt) / self.slope
        return 10 ** u if self.log else u

    def per_px(self, value=None):
        """Value change per pixel (linear axes)."""
        return abs(1.0 / self.slope)


# ------------------------------------------------------------------ curves

def classify(img, palette, paper=225.0):
    """Index of the nearest palette colour for each pixel; -1 for paper."""
    f = img.astype(float)
    keys = list(palette)
    d = np.stack([((f - np.array(palette[k], float)) ** 2).sum(axis=2) for k in keys])
    cls = d.argmin(axis=0)
    dmin = np.sqrt(d.min(axis=0))
    cls[(f.mean(axis=2) > paper)] = -1
    return cls, keys, dmin


def trace(mask, c_start, c_end, seed_row=None, max_jump=25, min_run=3, rows=None):
    """Follow one curve through `mask` from column c_start to c_end (either direction).
    Returns centre and half-width arrays over all columns (nan where not traced)."""
    H, W = mask.shape
    r_lo, r_hi = (0, H) if rows is None else rows
    centres = np.full(W, np.nan)
    halfw = np.full(W, np.nan)
    prev, thick, last_c = seed_row, None, c_start
    step = 1 if c_end >= c_start else -1
    for c in range(c_start, c_end + step, step):
        col = np.nonzero(mask[r_lo:r_hi, c])[0] + r_lo
        rr = [(a, b) for a, b in runs(col) if b - a + 1 >= min_run]
        if not rr:
            continue
        if prev is None:
            a, b = max(rr, key=lambda r: r[1] - r[0])
        else:
            a, b = min(rr, key=lambda r: abs((r[0] + r[1]) / 2 - prev))
            # after a hidden stretch the line may come back further away: allow ~1 px per column
            if abs((a + b) / 2 - prev) > max_jump + 1.0 * abs(c - last_c - step):
                continue
        last_c = c
        if thick is not None and b - a + 1 > 1.8 * thick:   # touches a label or another curve
            a = max(a, int(round(prev - thick / 2)))
            b = min(b, int(round(prev + thick / 2)))
            if b < a:
                continue
        centres[c] = (a + b + 1) / 2.0
        halfw[c] = (b - a + 1) / 2.0
        if thick is None:
            thick = b - a + 1
        else:
            thick = 0.9 * thick + 0.1 * min(b - a + 1, 1.5 * thick)
        prev = centres[c]
    return centres, halfw


def read_traced(centres, halfw, xax, yax, at, extra_px=0.0, interp_max=60, note=""):
    """Values of a traced curve at x positions `at`, with 95% intervals in value units."""
    out = []
    W = len(centres)
    for x in at:
        c = float(xax.to_px(x))
        ci = int(round(c))
        if ci < 0 or ci >= W:
            out.append({"x": x, "y": None, "note": "outside the crop"})
            continue
        lo_c, hi_c = max(ci - 2, 0), min(ci + 3, W)
        win = centres[lo_c:hi_c]
        how = ""
        if np.isfinite(win).any():
            row = float(np.nanmedian(win))
            hw = float(np.nanmax(halfw[lo_c:hi_c]))
        else:
            left = [k for k in range(ci - 1, max(ci - interp_max, -1), -1) if np.isfinite(centres[k])]
            right = [k for k in range(ci + 1, min(ci + interp_max, W)) if np.isfinite(centres[k])]
            if left and right:
                kl, kr = left[0], right[0]
                row = float(centres[kl] + (centres[kr] - centres[kl]) * (c - kl) / (kr - kl))
                hw = float(max(halfw[kl], halfw[kr])) + abs(centres[kr] - centres[kl]) / 2
                how = f"interpolated between columns {kl} and {kr} (line hidden); "
            elif left and ci - left[0] <= 20:
                row, hw = float(centres[left[0]]), float(halfw[left[0]]) + 2
                how = f"end of the line, {ci - left[0]} px before this column; "
            elif right and right[0] - ci <= 20:
                row, hw = float(centres[right[0]]), float(halfw[right[0]]) + 2
                how = f"start of the line, {right[0] - ci} px after this column (an axis line covers it); "
            else:
                out.append({"x": x, "y": None, "note": "line not found near this column (hidden or ended)"})
                continue
        nb = centres[max(ci - 12, 0):ci + 13]
        ok = np.isfinite(nb)
        slope = abs(np.polyfit(np.nonzero(ok)[0], nb[ok], 1)[0]) if ok.sum() > 5 else 0.0
        dpx = hw + yax.misfit + slope * (xax.misfit + 2.0) + extra_px + 1.0
        y = float(yax.to_val(row))
        ya, yb = float(yax.to_val(row + dpx)), float(yax.to_val(row - dpx))
        out.append({"x": x, "y": y, "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, row],
                    "px_lo": row + dpx, "px_hi": row - dpx,
                    "note": how + f"line half-width {hw:.1f} px, y misfit {yax.misfit:.1f} px, "
                            f"x misfit {xax.misfit:.1f} px" + (f", {note}" if note else "")})
    return out


# ------------------------------------------------------------------ bars

def _cap_centre(mask, col, end_row, direction, stem_w):
    """Row centre of the cap at the end of a stem: the rows near the end where the ink is
    much wider than the stem."""
    rows = range(end_row, end_row - 4 * direction * max(stem_w, 4), -direction)
    wide = []
    for r in rows:
        if r < 0 or r >= mask.shape[0]:
            continue
        line = mask[r]
        a = b = int(col)
        while a > 0 and line[a - 1]:
            a -= 1
        while b < len(line) - 1 and line[b + 1]:
            b += 1
        if line[int(col)] and b - a + 1 >= 2.5 * stem_w:
            wide.append(r)
    if not wide:
        return float(end_row), 1.0
    g = runs(sorted(wide))
    # the group touching the end
    a, b = min(g, key=lambda ab: min(abs(ab[0] - end_row), abs(ab[1] - end_row)))
    return (a + b) / 2.0, (b - a + 1) / 2.0


def follow_stem(mask, col, start_row, direction, max_gap=3, half=2):
    """Last row of ink along a vertical stem from start_row, going up (direction=-1) or down."""
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


def stem_column(mask, c_lo, c_hi, rows):
    """Centre column and width of the thin vertical stem within columns [c_lo, c_hi) over rows."""
    sub = mask[rows[0]:rows[1], c_lo:c_hi]
    if sub.size == 0:
        return None, 0
    prof = sub.mean(axis=0)
    idx = np.nonzero(prof > 0.6)[0]
    if len(idx) == 0:
        return None, 0
    a, b = max(runs(idx), key=lambda ab: (ab[1] - ab[0], -abs((ab[0] + ab[1]) / 2 - (c_hi - c_lo) / 2)))
    return c_lo + (a + b) / 2.0, b - a + 1


def find_bars(fill, min_width=25, min_height=4, cols=None):
    """Bars as runs of columns holding at least `min_height` px of fill colour."""
    prof = fill.sum(axis=0)
    if cols is not None:
        prof[: cols[0]] = 0
        prof[cols[1]:] = 0
    idx = np.nonzero(prof >= min_height)[0]
    return [(a, b) for a, b in runs(idx) if b - a + 1 >= min_width]


def read_bar(img, fill, ink, yax, c0, c1, base_row, index, outline=True, cal_px=0.0, ink_up=None):
    """One bar between columns c0..c1: its top and its error bar (ink = mask of the stem; ink_up,
    if given, the mask of the stem above the bar, on paper)."""
    ink_up = ink if ink_up is None else ink_up
    w = c1 - c0 + 1
    cb = (c0 + c1) / 2.0
    # top of the fill, away from the stem in the middle
    tops = []
    for c in list(range(int(c0 + 0.12 * w), int(cb - 0.12 * w))) + list(range(int(cb + 0.12 * w), int(c1 - 0.12 * w))):
        rr = np.nonzero(fill[:base_row, c])[0]
        if len(rr):
            tops.append(rr.min())
    top_fill = float(np.median(tops))
    stroke = 0.0
    if outline:
        cs = [c for c in range(int(c0 + 0.12 * w), int(c1 - 0.12 * w)) if abs(c - cb) > 0.12 * w]
        ths = []
        for c in cs:
            r = int(top_fill) - 1
            n = 0
            while r >= 0 and ink[r, c]:
                n += 1
                r -= 1
            ths.append(n)
        stroke = float(np.median(ths)) if ths else 0.0
    edge = top_fill - stroke / 2.0                        # centre of the top edge stroke
    prec = max(stroke / 2.0, 1.0) + 1.0 + yax.misfit + cal_px
    val = float(yax.to_val(edge))
    lo, hi = sorted([float(yax.to_val(edge + prec)), float(yax.to_val(edge - prec))])
    r = {"x": float(index), "y": val, "lo": lo, "hi": hi, "px": [cb, edge], "px_lo": edge + prec,
         "px_hi": edge - prec}
    # error bar: thin stem at the bar centre
    top_i = int(round(top_fill - stroke))
    sc, sw = stem_column(ink_up, int(c0 + 0.2 * w), int(c1 - 0.2 * w) + 1, (max(top_i - 30, 0), max(top_i - 4, 1)))
    notes = [f"bar top stroke {stroke:.0f} px, y misfit {yax.misfit:.1f} px"]
    if sc is None:
        # no stem above: an upper end hidden or absent
        r["note"] = "; ".join(notes + ["no error bar stem found above the bar"])
        return r
    up = follow_stem(ink_up, sc, top_i - 2, -1)
    up_c, up_t = _cap_centre(ink_up, sc, up, -1, sw)
    # downwards inside the bar: the stem is ink on the fill
    down = follow_stem(ink, sc, int(top_fill) + 2, +1)
    hidden_low = down is None or down >= base_row - 3 or down <= top_fill + 3
    if hidden_low:
        lo_row, lo_t = edge + (edge - up_c), up_t
        notes.append("lower end not seen inside the bar: taken as the mirror of the upper end")
    else:
        lo_row, lo_t = _cap_centre(ink, sc, down, +1, sw)
    m = 1.0 + yax.misfit + cal_px
    b_hi, b_lo = float(yax.to_val(up_c)), float(yax.to_val(lo_row))
    r.update({"bar_lo": b_lo, "bar_hi": b_hi,
              "bar_lo_outer": float(yax.to_val(lo_row + lo_t + m)),
              "bar_hi_outer": float(yax.to_val(up_c - up_t - m)),
              "px_bar": [sc, up_c, lo_row]})
    r["note"] = "; ".join(notes + [f"error bar ends at rows {up_c:.0f} and {lo_row:.0f}"])
    return r


def frame(ink, min_frac=0.3):
    """The y-axis line (leftmost long vertical) and x-axis line (lowest long horizontal)."""
    H, W = ink.shape
    vs = vlines(ink, int(min_frac * H))
    hs = hlines(ink, int(min_frac * W))
    if not vs or not hs:
        raise ValueError("axis lines not found")
    yl = min(vs, key=lambda v: v[0])
    xl = max(hs, key=lambda h: h[1])
    return yl, xl


def y_axis_from_ticks(ink, yl, values, side="left", min_len=12, max_len=120, log=False, keep=None):
    c0, c1, r0, r1 = yl
    t = ticks_y(ink, (c0, c1), (r0 - 15, r1 + 15), side=side, min_len=min_len, max_len=max_len)
    if keep is not None:
        t = [x for x in t if keep(x)]
    rows = sorted([p for p, _ in t], reverse=True)       # bottom to top
    return Axis(rows, values, log=log, what=f"y ticks {[round(r) for r in rows]}")


def x_axis_from_ticks(ink, xl, values, side="below", min_len=12, max_len=120, log=False, keep=None):
    r0, r1, c0, c1 = xl
    t = ticks_x(ink, (r0, r1), (c0 - 15, c1 + 15), side=side, min_len=min_len, max_len=max_len)
    if keep is not None:
        t = [x for x in t if keep(x)]
    cols = sorted(p for p, _ in t)
    return Axis(cols, values, log=log, what=f"x ticks {[round(c) for c in cols]}")


def bar_series(img, fill_rgb, tol, y_values, ink_thr=60.0, outline=True, min_width=25, tick_len=(12, 120),
               side="left", ink_sat=70.0, ink_up_thr=None, cal_px=0.0):
    """All bars of one fill colour in a bar chart, left to right, as indices 1, 2, ...
    ink_up_thr: a lighter threshold for error-bar stems above the bars (blurred bitmaps)."""
    ink = dark(img, ink_thr, ink_sat)
    ink_up = dark(img, ink_up_thr, ink_sat) if ink_up_thr else None
    yl, xl = frame(ink)
    yax = y_axis_from_ticks(ink, yl, y_values, side=side, min_len=tick_len[0], max_len=tick_len[1])
    fill = near(img, fill_rgb, tol)
    fill[: yl[2], :] = False
    fill[xl[0]:, :] = False
    fill[:, : yl[1] + 3] = False
    bars = find_bars(fill, min_width=min_width)
    return [read_bar(img, fill, ink, yax, a, b, xl[0], i + 1, outline=outline, ink_up=ink_up, cal_px=cal_px)
            for i, (a, b) in enumerate(bars)], yax


def axis_from_spec(ink, yl, xl, spec, which):
    """Calibrate one axis. spec: {"mode": "ticks"|"labels", "values": [...], "log": bool,
    "side": ..., "min_len": .., "max_len": .., "band": px, "gap": px, "skip": [indices of
    found marks to drop, e.g. a label that is not a tick label]}."""
    log = spec.get("log", False)
    if spec["mode"] == "ticks":
        if which == "x":
            return x_axis_from_ticks(ink, xl, spec["values"], side=spec.get("side", "below"),
                                     min_len=spec.get("min_len", 12), max_len=spec.get("max_len", 120), log=log)
        return y_axis_from_ticks(ink, yl, spec["values"], side=spec.get("side", "left"),
                                 min_len=spec.get("min_len", 12), max_len=spec.get("max_len", 120), log=log)
    band, gap = spec.get("band", 220), spec.get("gap", 40)
    H, W = ink.shape
    if which == "x":
        r1 = xl[1]
        rows = (r1 + spec.get("offset", 8), min(r1 + spec.get("offset", 8) + band, H))
        if "rows" in spec:                                 # where the labels are (no x-axis line under them)
            rows = tuple(spec["rows"])
        found = text_centres(ink, rows, (max(yl[0] - 300, 0), W), "col", gap=gap)
    else:
        c0 = yl[0]
        cols = (max(c0 - spec.get("offset", 8) - band, 0), c0 - spec.get("offset", 8))
        rows = tuple(spec["rows"]) if "rows" in spec else (0, min(xl[1] + 55, H))
        found = text_centres(ink, rows, cols, "row", gap=gap)
        found = sorted(found, key=lambda t: -t[0])          # bottom to top
    found = [f for i, f in enumerate(found) if i not in spec.get("skip", [])]
    return Axis([f[0] for f in found], spec["values"], log=log,
                what=f"{which} labels at {[round(f[0]) for f in found]}")


def curve_panel(img, palette, name, xspec, yspec, at, seed, tol=60.0, max_jump=25, ink_thr=120.0,
                paper=225.0, min_run=3, interp_max=60, extra_px=0.0, note=""):
    """Read the curve of colour `name` (a key of palette) at x positions `at`.
    seed: (column, row) of a point on the curve, from which it is traced both ways."""
    ink = dark(img, ink_thr)
    yl, xl = frame(ink)
    xax = axis_from_spec(ink, yl, xl, xspec, "x")
    yax = axis_from_spec(ink, yl, xl, yspec, "y")
    if yspec["mode"] == "labels":
        # a label centre need not sit exactly on its value: compare each label with the nearest
        # drawn horizontal line (x axis, zero line) or the y-axis end, and carry the largest offset
        lines = [(h[0] + h[1]) / 2 for h in hlines(ink, int(0.3 * img.shape[1]))] + [yl[2]]
        offs = [min(abs(p - q) for q in lines) for p in yax.px]
        offs = [o for o in offs if o < 60]
        lab_off = max(offs) if offs else 0.0
        extra_px = extra_px + lab_off
        note = (note + ", " if note else "") + f"label-to-line offset {lab_off:.0f} px"
    cls, keys, dmin = classify(img, palette, paper=paper)
    mask = (cls == keys.index(name)) & (dmin < tol)
    mask[:, : yl[1] + 2] = False                         # the y-axis line
    mask[xl[0] - 1: xl[1] + 2, :] = False                # the x-axis line
    c0, r0 = seed
    left_c, right_c = yl[1] + 3, min(xl[3], img.shape[1] - 1)
    cr, hr = trace(mask, int(c0), right_c, seed_row=r0, max_jump=max_jump, min_run=min_run)
    cl, hl = trace(mask, int(c0), left_c, seed_row=r0, max_jump=max_jump, min_run=min_run)
    cent = np.where(np.isfinite(cr), cr, cl)
    half = np.where(np.isfinite(hr), hr, hl)
    return read_traced(cent, half, xax, yax, at, extra_px=extra_px, interp_max=interp_max, note=note)


# ------------------------------------------------------------------ markers

def markers(mask, open_px=15, min_area=200, split=True):
    """Blobs of a marker mask after hole filling and opening. Returns [(col, row, h, w, slice)]."""
    m = ndi.binary_fill_holes(mask)
    m = ndi.binary_opening(m, structure=np.ones((open_px, open_px), bool))
    lab, n = ndi.label(m)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        blob = lab[sl] == i
        area = int(blob.sum())
        if area < min_area:
            continue
        h, w = blob.shape
        if split and w > 1.5 * h:
            # touching markers in a row: split where the column height dips
            hcol = blob.sum(axis=0)
            parts = runs(np.nonzero(hcol >= 0.8 * hcol.max())[0])
            for a, b in parts:
                sub = blob[:, a:b + 1]
                rr = np.nonzero(sub.any(axis=1))[0]
                rmid = sl[0].start + (rr.min() + rr.max()) / 2.0
                cm = sl[1].start + (a + b) / 2.0
                out.append((cm, rmid, float(rr.max() - rr.min() + 1), float(h), None))
            continue
        rr = np.nonzero(blob.any(axis=1))[0]
        cc = np.nonzero(blob.any(axis=0))[0]
        out.append((sl[1].start + (cc.min() + cc.max()) / 2.0, sl[0].start + (rr.min() + rr.max()) / 2.0,
                    float(h), float(w), sl))
    out.sort(key=lambda t: t[0])
    return out


def marker_reading(ink, xax, yax, col, row, h, x_value=None, stem_half=2, cal_px=0.0, xlog=None):
    """A marker centred at (col, row) of height h, with the error bar followed along its stem."""
    prec = 2.0 + yax.misfit + cal_px
    y = float(yax.to_val(row))
    lo, hi = sorted([float(yax.to_val(row + prec)), float(yax.to_val(row - prec))])
    x = float(xax.to_val(col)) if x_value is None else x_value
    r = {"x": x, "y": y, "lo": lo, "hi": hi, "px": [col, row], "px_lo": row + prec, "px_hi": row - prec}
    top, bot = int(row - h / 2), int(row + h / 2)
    up = follow_stem(ink, col, top - 1, -1, half=stem_half)
    dn = follow_stem(ink, col, bot + 1, +1, half=stem_half)
    m = 1.0 + yax.misfit + cal_px
    notes = []
    if up is None or up >= top - 3:
        up_c, up_t = float(top), 0.0
        notes.append("upper end of the error bar inside the marker: at most the marker's edge")
    else:
        up_c, up_t = _cap_centre(ink, col, up, -1, 2 * stem_half + 1)
    if dn is None or dn <= bot + 3:
        dn_c, dn_t = float(bot), 0.0
        notes.append("lower end of the error bar inside the marker: at most the marker's edge")
    else:
        dn_c, dn_t = _cap_centre(ink, col, dn, +1, 2 * stem_half + 1)
    r.update({"bar_hi": float(yax.to_val(up_c)), "bar_lo": float(yax.to_val(dn_c)),
              "bar_hi_outer": float(yax.to_val(up_c - up_t - m)),
              "bar_lo_outer": float(yax.to_val(dn_c + dn_t + m)), "px_bar": [col, up_c, dn_c]})
    r["note"] = "; ".join(notes + [f"marker centre, y misfit {yax.misfit:.1f} px, x misfit {xax.misfit:.1f} px"])
    return r
