"""Shared reading code for the plots of wang2014 (rendered at 1200 dpi).

The plots are embedded bitmaps of roughly 300 dpi, so at 1200 dpi each source pixel is a block of
about 4 x 4 px (q = 4); lines are quantized in those steps.

Calibration, all from the image:
  * the frame is found as the rows and columns of dark ink whose longest run is at least 60% of
    the longest; each side's coordinate is the centre of its line;
  * tick marks are short runs of dark ink (min_tick..max_tick px) standing inward from the bottom
    frame line (x) and from the left frame line (y). They are matched in order to the printed
    labels in the spec; a label printed at a frame corner is put at the frame line itself; a log
    axis uses its decade ticks only (minor ticks are shorter and dropped by length);
  * a straight line (in log10 of the value for a log axis) is fitted through these positions and
    the largest misfit, in pixels, is reported and added to every interval.

Curves are traced column by column, both ways, from a seed (the run of curve ink nearest a given y
at a given x: a choice of which curve, not a value). At each column the run nearest a prediction
(quadratic fit to the last traced columns) is kept, so a trace carries on through a crossing:
  * clean: a run up to w' + q long (w' the line's vertical thickness) is the line; its centre is
    the value;
  * fused: a longer run holds something else as well; the centre is the prediction clipped to the
    run and the interval the whole run less w'/2 at each end;
  * gap: no run near the prediction (the line is hidden under another); the prediction is kept for
    at most max_gap columns and the interval widened by gap_px.
Intervals (95%): +- (q + y misfit + 1 px) around the centre or the run, plus |slope| (q + x
misfit) where the curve is steep.

Markers are connected components of a colour mask (closed, holes filled) with an area in the
spec's range; the value is the centroid, the interval +- (misfit + marker radius / 3).
"""

import math

import numpy as np
from scipy import ndimage


def rgb(image):
    return np.asarray(image)[..., :3].astype(int)


def black_mask(image, level=330):
    a = rgb(image)
    chroma = np.max(a, axis=2) - np.min(a, axis=2)
    return (a.sum(axis=2) < level) & (chroma < 60)


def ink(image, kind):
    a = rgb(image)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "red":
        return (r - g > 90) & (r - b > 90)
    if kind == "red_bridged":  # a band of red markers with a thin line of another colour over it
        red = (r - g > 60) & (r - b > 60)
        return ndimage.binary_closing(red, structure=np.ones((41, 1), bool))
    if kind == "blue":
        return (b - r > 80) & (b - g > 60)
    if kind == "green":
        return (g - r > 60) & (g - b > 40)
    if kind == "magenta":
        return (r - g > 80) & (b - g > 80)
    if kind == "brown":  # dark red-brown stars
        return (r - b > 50) & (r - g > 30) & (r < 220) & (g < 150)
    if kind == "black":
        return black_mask(image)
    raise ValueError(kind)


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    return max((b - a for a, b in _runs(v)), default=0)


def frame(fmask, frac=0.6):
    H, W = fmask.shape
    rl = np.array([_longest(fmask[i]) for i in range(H)])
    cl = np.array([_longest(fmask[:, j]) for j in range(W)])
    rows = np.flatnonzero(rl > frac * rl.max())
    cols = np.flatnonzero(cl > frac * cl.max())

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
            if len(cur) <= 24:
                out.append((off + (cur[0] + cur[-1]) / 2.0 + 0.5, max(lengths[j] for j in cur)))
            cur = []
    return out


def ticks(fmask, fr, min_tick=12, max_tick=120, edge=10):
    t0, b0 = int(fr["top"][1]) + 1, int(fr["bottom"][0]) - 1
    l0, r0 = int(fr["left"][1]) + 1, int(fr["right"][0]) - 1
    xb = [_inward(fmask[t0:b0 + 1, c][::-1]) for c in range(l0 + edge, r0 - edge)]
    yl = [_inward(fmask[rr, l0:r0 + 1]) for rr in range(t0 + edge, b0 - edge)]
    return _groups(xb, min_tick, max_tick, l0 + edge), _groups(yl, min_tick, max_tick, t0 + edge)


class Axis:
    def __init__(self, pix, vals, log):
        self.log = log
        p = np.array(pix, float)
        v = np.log10(vals) if log else np.array(vals, float)
        self.b, self.a = np.polyfit(p, v, 1)
        self.misfit = float(np.max(np.abs((v - self.a) / self.b - p))) if len(p) > 2 else 0.0

    def val(self, px):
        u = self.a + self.b * px
        return 10 ** u if self.log else u

    def px(self, val):
        u = math.log10(val) if self.log else val
        return (u - self.a) / self.b


def calibrate(image, spec):
    fmask = black_mask(image, spec.get("frame_level", 330))
    if spec.get("frame_box"):  # only the frame region of the crop (pixels of the crop)
        x0, y0, x1, y1 = spec["frame_box"]
        m = np.zeros_like(fmask)
        m[y0:y1, x0:x1] = fmask[y0:y1, x0:x1]
        fmask = m
    fr = frame(fmask)
    tx, ty = ticks(fmask, fr, spec.get("min_tick", 12), spec.get("max_tick", 120))
    out = {}
    for name, tk, lo_key, hi_key in (("x", tx, "c_left", "c_right"), ("y", ty, "c_bottom", "c_top")):
        s = spec[name]
        found = [p for p, n in tk if n >= s.get("major_len", 0)]
        if name == "y":
            found = sorted(found, reverse=True)
        labels = s["ticks"]
        if len(found) != len(labels):
            raise ValueError(f"{name}: found {len(found)} ticks at {[(round(p), n) for p, n in tk]}, "
                             f"expected {len(labels)} for {labels}")
        pix, vals = list(found), list(labels)
        if s.get("lo") is not None:
            pix.insert(0, fr[lo_key]); vals.insert(0, s["lo"])
        if s.get("hi") is not None:
            pix.append(fr[hi_key]); vals.append(s["hi"])
        out[name] = Axis(pix, vals, s.get("log", False))
    out["frame"] = fr
    return out


def _restrict(m, fr, spec):
    pad = spec.get("pad", 12)
    out = np.zeros_like(m)
    t, b = int(fr["top"][1]) + pad, int(fr["bottom"][0]) - pad
    l, r = int(fr["left"][1]) + pad, int(fr["right"][0]) - pad
    out[t:b, l:r] = m[t:b, l:r]
    for x0, y0, x1, y1 in spec.get("blank", []):
        out[y0:y1, x0:x1] = False
    return out


def trace(mask, c0, r0, c_end, w, q, max_gap=60):
    step = 1 if c_end >= c0 else -1
    pts, hist, gap = {}, [], 0
    for c in range(c0, c_end + step, step):
        if len(hist) >= 40:
            hc = np.array([h[0] for h in hist[-150:]], float) - c
            hr = np.array([h[1] for h in hist[-150:]], float)
            _, p1, p0 = np.polyfit(hc, hr, 2)
            pred, slope = p0, p1
        elif len(hist) >= 3:
            k, k0 = np.polyfit([h[0] for h in hist], [h[1] for h in hist], 1)
            pred, slope = k * c + k0, k
        elif hist:
            pred, slope = hist[-1][1], 0.0
        else:
            pred, slope = r0, 0.0
        th = w * math.sqrt(1 + slope * slope)
        lim = max(2 * th, 30)
        cands = []
        for a, b in _runs(mask[:, c]):
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
        if b - a <= th + q:
            ctr = (a + b - 1) / 2
            pts[c] = (ctr, ctr, ctr, "clean", slope)
        else:
            lo, hi = a + th / 2, b - 1 - th / 2
            ctr = min(max(pred, lo), hi)
            pts[c] = (ctr, lo, hi, "fused", slope)
        hist.append((c, ctr))
    return pts


def read_curve(image, at, spec):
    cal = calibrate(image, spec)
    X, Y, fr = cal["x"], cal["y"], cal["frame"]
    mis = max(X.misfit, Y.misfit)
    mask = _restrict(ink(image, spec["ink"]), fr, spec)
    w, q = spec.get("w", 20.0), spec.get("q", 4)
    sx, sy = spec["seed"]
    c0 = int(round(X.px(sx)))
    ry = Y.px(sy)
    a, b = min(_runs(mask[:, c0]), key=lambda ab: abs((ab[0] + ab[1] - 1) / 2 - ry))
    r0 = (a + b - 1) / 2
    pad = spec.get("pad", 12)
    left, right = int(fr["left"][1]) + pad + 1, int(fr["right"][0]) - pad - 1
    pts = trace(mask, c0, r0, right, w, q, spec.get("max_gap", 60))
    pts.update(trace(mask, c0, r0, left, w, q, spec.get("max_gap", 60)))
    out = []
    for x in at:
        c = int(round(X.px(x)))
        if c not in pts:
            out.append({"x": x, "y": None, "note": "outside the traced part of the curve"})
            continue
        ctr, lo, hi, kind, slope = pts[c]
        e = q + Y.misfit + 1 + (spec.get("gap_px", 10) if kind == "gap" else 0)
        e += abs(slope) * (X.misfit + q)
        top, bot = lo - e, hi + e
        if bot - top > spec.get("max_px", 120):
            out.append({"x": x, "y": None, "px": [c, ctr], "note": f"{kind} run {bot - top:.0f} px tall: unreadable"})
            continue
        y1, y2 = Y.val(top), Y.val(bot)
        out.append({"x": x, "y": float(Y.val(ctr)), "lo": float(min(y1, y2)), "hi": float(max(y1, y2)),
                    "px": [c, float(ctr)], "px_lo": float(top), "px_hi": float(bot),
                    "note": f"{kind} run; calibration misfit {mis:.1f} px"})
    return out


def markers(image, spec):
    """Marker centroids: [(cx, cy, area, (r0, r1, c0, c1))] in crop pixels, plus the calibration."""
    cal = calibrate(image, spec)
    fr = cal["frame"]
    m = ink(image, spec["ink"])
    m = _restrict(m, fr, dict(spec, pad=spec.get("pad", -40))) if spec.get("pad", -40) >= 0 else _restrict_out(m, fr, spec)
    m = ndimage.binary_closing(m, iterations=spec.get("close", 3))
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    amin, amax = spec["area"]
    found = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        ys, xs = np.nonzero(lab[sl] == i)
        if not (amin <= len(ys) <= amax):
            continue
        found.append((xs.mean() + sl[1].start, ys.mean() + sl[0].start, len(ys),
                      (sl[0].start, sl[0].stop, sl[1].start, sl[1].stop)))
    return found, cal


def _restrict_out(m, fr, spec):
    """Keep a margin outside the frame too (markers drawn on the frame line)."""
    g = -spec.get("pad", -40)
    out = np.zeros_like(m)
    t, b = max(int(fr["top"][0]) - g, 0), int(fr["bottom"][1]) + g
    l, r = max(int(fr["left"][0]) - g, 0), int(fr["right"][1]) + g
    out[t:b, l:r] = m[t:b, l:r]
    for x0, y0, x1, y1 in spec.get("blank", []):
        out[y0:y1, x0:x1] = False
    return out


def read_hollow_markers(image, spec):
    """Hollow markers joined by a line of the same colour (computed boundary points).

    The colour mask (inside the frame widened by `margin` px, `blank` boxes removed) is closed by
    `close` px (default 2; more bridges a ring broken by a line of another colour), its holes filled (a ring becomes a disc, a square outline a square), then opened with a
    disc of radius `r_open` px, which removes the joining line (thinner than 2 r_open) and keeps
    the markers. Markers that touch (a chain of squares) stay one blob, so each marker is a local
    maximum of the distance to the blob's edge, at least `r_min` px deep, with no deeper one within
    `sep` px; plateaus are merged. The value is that point; the interval +- (misfit + 3 px), the
    3 px for the quantized marker outline."""
    cal = calibrate(image, spec)
    X, Y, fr = cal["x"], cal["y"], cal["frame"]
    mis = max(X.misfit, Y.misfit)
    m0 = ink(image, spec["ink"])
    g = spec.get("margin", 60)
    m = np.zeros_like(m0)
    t, b = max(int(fr["top"][0]) - g, 0), int(fr["bottom"][1]) + g
    l, r = max(int(fr["left"][0]) - g, 0), int(fr["right"][1]) + g
    m[t:b, l:r] = m0[t:b, l:r]
    for x0, y0, x1, y1 in spec.get("blank", []):
        m[y0:y1, x0:x1] = False
    m = ndimage.binary_closing(m, iterations=spec.get("close", 2))
    m = ndimage.binary_fill_holes(m)
    ro = spec["r_open"]
    yy, xx = np.mgrid[-ro:ro + 1, -ro:ro + 1]
    m = ndimage.binary_opening(m, structure=(xx * xx + yy * yy) <= ro * ro)
    dt = ndimage.distance_transform_edt(m)
    sep = spec["sep"]
    peak = ndimage.maximum_filter(dt, size=2 * sep + 1)
    cand = np.argwhere((dt >= peak - 1e-9) & (dt >= spec["r_min"]))
    pts = []
    for i, j in sorted(cand.tolist(), key=lambda ij: (-dt[ij[0], ij[1]], ij[0], ij[1])):
        hit = [p for p in pts if abs(p[0] - i) <= sep and abs(p[1] - j) <= sep]
        if hit:
            hit[0][2].append((i, j))
            continue
        pts.append([i, j, [(i, j)]])
    out = []
    for _, _, members in pts:
        cy = float(np.mean([p[0] for p in members])) + 0.5
        cx = float(np.mean([p[1] for p in members])) + 0.5
        e = mis + 3
        out.append({"x": float(X.val(cx)), "y": float(Y.val(cy)), "lo": float(Y.val(cy + e)), "hi": float(Y.val(cy - e)),
                    "px": [cx, cy], "px_lo": cy - e, "px_hi": cy + e,
                    "note": f"filled-marker centre (depth {dt[int(cy), int(cx)]:.0f} px); x within "
                            f"[{X.val(cx - e):.3g}, {X.val(cx + e):.3g}]; calibration misfit {mis:.1f} px"})
    out.sort(key=lambda d: (d["x"], d["y"]))
    return out


def read_markers(image, spec):
    found, cal = markers(image, spec)
    X, Y = cal["x"], cal["y"]
    mis = max(X.misfit, Y.misfit)
    out = []
    for cx, cy, area, box in found:
        e = mis + math.sqrt(area) / 6 + 1
        x = float(X.val(cx))
        xe = abs(X.val(cx + e) - X.val(cx - e)) / 2
        out.append({"x": x, "y": float(Y.val(cy)), "lo": float(Y.val(cy + e)), "hi": float(Y.val(cy - e)),
                    "px": [float(cx), float(cy)], "px_lo": float(cy - e), "px_hi": float(cy + e),
                    "note": f"marker centroid, area {area} px; x within +-{xe:.3g}; calibration misfit {mis:.1f} px"})
    out.sort(key=lambda d: (d["x"], d["y"]))
    return out
