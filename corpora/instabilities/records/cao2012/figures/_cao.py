"""Shared reading code for the plots of cao2012 (rendered at 1200 dpi).

The plots are embedded bitmaps of about 150 dpi: at 1200 dpi each source pixel is a block of
8 x 8 px, so line positions are quantized in steps of 8 px (q = 8).

Calibration, all from the image:
  * the frame is found as the rows and columns of the frame ink (blue in Figs. 2-7, dark grey in
    Figs. 8, 11, 13) whose longest run is at least 60% of the longest; each side's coordinate is the
    centre of its line;
  * tick marks are short runs (min_tick..max_tick px) of frame ink standing inward from the bottom
    frame line (x) and from the left frame line (y); a log axis's minor ticks are dropped by length
    when the spec asks for major ticks only. They are matched in order to the printed labels in the
    spec; a label printed at a frame corner is put at the frame line itself;
  * a straight line (in log10 of the value for a log axis) is fitted through these positions and the
    largest misfit, in pixels, is reported and added to every interval.

Curves are traced column by column, both ways, from a seed: the k-th run of curve ink (counted from
the bottom) in the column at a given x, or the run nearest a given y there (a choice of which curve,
not a value). Text, legends and label boxes named in the spec are blanked first. At each column the
run nearest a prediction is kept; the prediction is a quadratic fit to the last 200 traced columns
(linear while fewer than 40), so that a trace carries on through a crossing. With w' = w sqrt(1 +
slope^2) the line's vertical thickness:
  * clean: a run up to w' + q long is the line itself; its centre is the value;
  * fused: a longer run holds another line (a second curve, a dash, a leader, text); the centre is
    the prediction clipped to the run, and the interval the whole run less w'/2 at each end;
  * ambiguous: two runs about equally near the prediction (within w' of each other); the interval
    spans both, and the column is kept out of the prediction's history;
  * gap: no run near the prediction; the prediction is kept for at most max_gap columns.
Intervals (95%): a clean run gives its centre +- (q/2 + y misfit + 1 px); a fused or ambiguous run
the range above +- the same; a gap the prediction +- (gap_px + y misfit); to each is added
|slope| (q/2 + x misfit), the shift in y of an error in x where the curve is steep. A reading wider
than max_px is reported as unreadable.

Markers are connected components of a colour mask (closed, holes filled, optionally opened to drop
the anti-aliased edge of a curve of a similar colour) with an area within the spec's range; the
value is the centroid of the filled shape, the interval +- (misfit + 3 px): the centroid of a
shape about 60 px across averages the 8-px quantization of its outline.
"""

import math

import numpy as np
from scipy import ndimage


# ----------------------------------------------------------------------------- masks

def rgb(image):
    return np.asarray(image)[..., :3].astype(int)


def blue_mask(image):
    a = rgb(image)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (b - r > 50) & (b - g > 35)


def black_mask(image, level=330):
    a = rgb(image)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    chroma = np.max(a, axis=2) - np.min(a, axis=2)
    return (r + g + b < level) & (chroma < 45)


def color_mask(image, color, tol=70):
    a = rgb(image)
    return np.sqrt(((a - np.array(color)) ** 2).sum(axis=2)) < tol


# ----------------------------------------------------------------------------- calibration

def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    r = _runs(v)
    return max((b - a for a, b in r), default=0)


def frame(fmask):
    H, W = fmask.shape
    rl = np.array([_longest(fmask[i]) for i in range(H)])
    cl = np.array([_longest(fmask[:, j]) for j in range(W)])
    rows = np.flatnonzero(rl > 0.6 * rl.max())
    cols = np.flatnonzero(cl > 0.6 * cl.max())

    def side(idx, first):
        idx = sorted(idx.tolist(), reverse=not first)
        grp = [idx[0]]
        for i in idx[1:]:
            if abs(i - grp[-1]) != 1:
                break
            grp.append(i)
        return float(min(grp)), float(max(grp))

    t, b, l, r = side(rows, True), side(rows, False), side(cols, True), side(cols, False)
    return {"top": t, "bottom": b, "left": l, "right": r,
            "c_top": (t[0] + t[1]) / 2, "c_bottom": (b[0] + b[1]) / 2,
            "c_left": (l[0] + l[1]) / 2, "c_right": (r[0] + r[1]) / 2}


def _inward(line):
    n = 0
    while n < len(line) and line[n]:
        n += 1
    return n


def _groups(lengths, lo, hi, off):
    out, cur = [], []
    for i, n in enumerate(list(lengths) + [0]):
        if lo <= n <= hi:
            cur.append(i)
        elif cur:
            if len(cur) <= 20:
                out.append((off + (cur[0] + cur[-1]) / 2.0, max(lengths[j] for j in cur)))
            cur = []
    return out


def ticks(fmask, fr, min_tick=15, max_tick=150):
    """Tick marks inward from the bottom (x) and left (y) frame lines: [(position, length)]."""
    t0, b0 = int(fr["top"][1]) + 1, int(fr["bottom"][0]) - 1
    l0, r0 = int(fr["left"][1]) + 1, int(fr["right"][0]) - 1
    xb = [_inward(fmask[t0:b0 + 1, c][::-1]) for c in range(l0 + 6, r0 - 6)]
    yl = [_inward(fmask[rr, l0:r0 + 1]) for rr in range(t0 + 6, b0 - 6)]
    return _groups(xb, min_tick, max_tick, l0 + 6), _groups(yl, min_tick, max_tick, t0 + 6)


class Axis:
    def __init__(self, pix, vals, log):
        self.log = log
        p = np.array(pix, float)
        v = np.log10(vals) if log else np.array(vals, float)
        self.b, self.a = np.polyfit(p, v, 1)
        self.misfit = float(np.max(np.abs((v - self.a) / self.b - p))) if len(p) > 2 else 0.0
        self.pix, self.vals = list(p), list(vals)

    def val(self, px):
        u = self.a + self.b * px
        return 10 ** u if self.log else u

    def px(self, val):
        u = math.log10(val) if self.log else val
        return (u - self.a) / self.b


def calibrate(fmask, spec):
    fr = frame(fmask)
    tx, ty = ticks(fmask, fr, spec.get("min_tick", 15), spec.get("max_tick", 150))
    out = {}
    for name, tk, lo_key, hi_key in (("x", tx, "c_left", "c_right"), ("y", ty, "c_bottom", "c_top")):
        s = spec[name]
        found = [p for p, n in tk if n >= s.get("major_len", 0)]
        if name == "y":
            found = sorted(found, reverse=True)  # bottom to top
        labels = s["ticks"]
        if len(found) != len(labels):
            raise ValueError(f"{name}: found {len(found)} ticks at {[round(p) for p in found]}, "
                             f"expected {len(labels)} for {labels}")
        pix, vals = list(found), list(labels)
        if s.get("lo") is not None:
            pix.insert(0, fr[lo_key]); vals.insert(0, s["lo"])
        if s.get("hi") is not None:
            pix.append(fr[hi_key]); vals.append(s["hi"])
        out[name] = Axis(pix, vals, s.get("log", False))
    out["frame"] = fr
    return out


# ----------------------------------------------------------------------------- curves

def _col_runs(mask, c):
    return _runs(mask[:, c])


def trace(mask, c0, r0, c_end, w, max_gap=40, near=None, hw=200, q=8):
    """Follow the line through (c0, r0) to column c_end; {col: (centre, lo, hi, kind, slope)}.
    The prediction is a quadratic fit to the last hw traced columns (linear while fewer than 40),
    so that the trace carries on through a crossing or a tangency with another line."""
    step = 1 if c_end >= c0 else -1
    pts = {}
    hist = []
    gap = 0
    for c in range(c0, c_end + step, step):
        if len(hist) >= 40:
            hc = np.array([h[0] for h in hist[-hw:]], float) - c
            hr = np.array([h[1] for h in hist[-hw:]], float)
            p2, p1, p0 = np.polyfit(hc, hr, 2)
            pred, slope = p0, p1
        elif len(hist) >= 3:
            hc = [h[0] for h in hist]
            hr = [h[1] for h in hist]
            k, k0 = np.polyfit(hc, hr, 1)
            pred, slope = k * c + k0, k
        elif hist:
            pred, slope = hist[-1][1], 0.0
        else:
            pred, slope = r0, 0.0
        th = w * math.sqrt(1 + slope * slope)
        lim = near if near is not None else max(2 * th, 40)
        cands = []
        for a, b in _col_runs(mask, c):
            d = 0 if a <= pred <= b else min(abs(a - pred), abs(b - 1 - pred))
            if d <= lim:
                cands.append((d, a, b))
        cands.sort()
        if not cands:
            gap += 1
            if gap > max_gap:
                break
            pts[c] = (pred, pred, pred, "gap", slope)
            continue
        gap = 0
        _, a, b = cands[0]
        if len(cands) > 1 and cands[1][0] < cands[0][0] + th:
            # two lines about equally near: which one is ours is not known here
            lo = min(a, cands[1][1]) + th / 2
            hi = max(b, cands[1][2]) - 1 - th / 2
            pts[c] = (min(max(pred, lo), hi), lo, hi, "ambiguous", slope)
            continue  # kept out of the history
        if b - a <= th + q:
            ctr = (a + b - 1) / 2
            pts[c] = (ctr, ctr, ctr, "clean", slope)
            hist.append((c, ctr))
        else:
            lo, hi = a + th / 2, b - 1 - th / 2
            ctr = min(max(pred, lo), hi)
            pts[c] = (ctr, lo, hi, "fused", slope)
            hist.append((c, ctr))
    return pts


def seed_row(mask, c, rank, rows=None):
    runs = [(a, b) for a, b in _col_runs(mask, c) if rows is None or rows[0] <= a <= rows[1]]
    runs = sorted(runs, key=lambda ab: -ab[0])  # bottom first
    a, b = runs[rank]
    return (a + b - 1) / 2


def curve_mask(image, spec, fr):
    kind = spec.get("ink", "black")
    a = rgb(image)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "black":
        m = black_mask(image)
    elif kind == "red":  # red-dominant ink (dark red hexagons, shaded red spheres)
        m = (r - g > 70) & (r - b > 70)
    elif kind == "blue":  # blue-dominant ink (shaded blue spheres)
        m = (b - r > 60) & (b - g > 40)
    else:
        m = color_mask(image, spec["ink"], spec.get("tol", 70))
    pad = spec.get("pad", 14)
    out = np.zeros_like(m)
    t, b = int(fr["top"][1]) + pad, int(fr["bottom"][0]) - pad
    l, r = int(fr["left"][1]) + pad, int(fr["right"][0]) - pad
    out[t:b, l:r] = m[t:b, l:r]
    for x0, y0, x1, y1 in spec.get("blank", []):  # boxes of text, legend (pixels of the crop)
        out[y0:y1, x0:x1] = False
    return out


def read_curve(image, at, spec):
    fmask = blue_mask(image) if spec.get("frame", "blue") == "blue" else black_mask(image, 450)
    cal = calibrate(fmask, spec)
    X, Y, fr = cal["x"], cal["y"], cal["frame"]
    mis = max(X.misfit, Y.misfit)
    mask = curve_mask(image, spec, fr)
    w = spec.get("w", 8.0)
    seed = spec["seed"]
    c0 = int(round(X.px(seed[0])))
    if len(seed) == 3:  # [x, "near", y]: the line nearest y at x (which curve is meant, not a value)
        ry = Y.px(seed[2])
        a, b = min(_col_runs(mask, c0), key=lambda ab: abs((ab[0] + ab[1] - 1) / 2 - ry))
        r0 = (a + b - 1) / 2
    else:  # [x, k]: the k-th line from the bottom at x
        r0 = seed_row(mask, c0, seed[1], spec.get("seed_rows"))
    left = int(fr["left"][1]) + spec.get("pad", 14) + 1
    right = int(fr["right"][0]) - spec.get("pad", 14) - 1
    pts = trace(mask, c0, r0, right, w, spec.get("max_gap", 40))
    pts.update(trace(mask, c0, r0, left, w, spec.get("max_gap", 40)))
    out = []
    max_px = spec.get("max_px", 120)
    for x in at:
        c = int(round(X.px(x)))
        if c not in pts:
            out.append({"x": x, "y": None, "note": "outside the traced part of the curve"})
            continue
        ctr, lo, hi, kind, slope = pts[c]
        pad = spec.get("q", 4) + Y.misfit + 1
        if kind == "gap":
            pad = spec.get("gap_px", 8) + Y.misfit
        pad += abs(slope) * (X.misfit + spec.get("q", 4))  # where the curve is steep, x error moves y
        top_row, bot_row = lo - pad, hi + pad
        if bot_row - top_row > max_px:
            out.append({"x": x, "y": None, "px": [c, ctr],
                        "note": f"line fused with others over {bot_row - top_row:.0f} px: unreadable"})
            continue
        y, y_hi, y_lo = Y.val(ctr), Y.val(top_row), Y.val(bot_row)
        out.append({"x": x, "y": float(y), "lo": float(min(y_lo, y_hi)), "hi": float(max(y_lo, y_hi)),
                    "px": [c, float(ctr)], "px_lo": float(top_row), "px_hi": float(bot_row),
                    "note": f"{kind} run; calibration misfit {mis:.1f} px"})
    return out


# ----------------------------------------------------------------------------- markers

def read_markers(image, spec):
    fmask = blue_mask(image) if spec.get("frame", "blue") == "blue" else black_mask(image, 450)
    cal = calibrate(fmask, spec)
    X, Y, fr = cal["x"], cal["y"], cal["frame"]
    mis = max(X.misfit, Y.misfit)
    m = curve_mask(image, spec, fr)
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=2))
    if spec.get("open"):  # drop thin lines (a curve's anti-aliased edge) of the marker colour
        m = ndimage.binary_opening(m, iterations=spec["open"])
    lab, n = ndimage.label(m)
    amin, amax = spec["area"]
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if not (amin <= len(ys) <= amax):
            continue
        cx, cy = xs.mean(), ys.mean()
        pad = mis + 3
        out.append({"x": float(X.val(cx)), "y": float(Y.val(cy)),
                    "lo": float(Y.val(cy + pad)), "hi": float(Y.val(cy - pad)),
                    "px": [float(cx), float(cy)], "px_lo": float(cy - pad), "px_hi": float(cy + pad),
                    "note": f"marker centroid, area {len(ys)} px; x within {abs(X.val(cx + pad) - X.val(cx)):.3g}; "
                            f"calibration misfit {mis:.1f} px"})
    out.sort(key=lambda d: d["x"])
    return out

