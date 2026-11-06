"""Shared reading code for the figures of bangasser2013b (Excel-style charts).

Each reading file here is a stub naming one panel, one series (by its colour in
the image) and the printed axis labels, and calls `read_spec`. Stubs pin this file
by SHA-256, so any change here forces each stub to be re-checked.

Everything is found in the image:
  axes    the black spines are the longest dark vertical / horizontal lines of the
          crop; the tick marks are the short dark strokes sticking out of a spine
          (outside the plot box). The ticks are matched, in pixel order, to the
          printed labels the stub gives (the only paper values used); a least-squares
          line (linear or log10) of pixel against value is the calibration, and its
          largest residual (at least half a pixel) is the misfit.
  curves  pixels nearer in colour to the series' colour than to any other colour of
          the panel (and within a tolerance); per column the runs of that mask; the
          curve is followed from the longest stretch of columns with one run,
          keeping the run nearest to the previous centre. The value is the run's centre.
  drops   a vertical segment of the series (the abrupt failure of an ODE cycle):
          the columns where the series' mask has a long vertical run; the value is
          the centre column of the longest such group, on the x axis.

Intervals (95%): half the line thickness, half the excess of the run over the
normal thickness (steep parts), the calibration misfit and one pixel; across x,
the curve's slope times the x misfit.
"""
from itertools import combinations

import numpy as np


def gray(img):
    return img.astype(float).mean(axis=2)


def sat(img):
    f = img.astype(float)
    return f.max(axis=2) - f.min(axis=2)


def black(img, thr=110, smax=70):
    return (gray(img) < thr) & (sat(img) < smax)


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _longest(v, gap=3):
    on = np.where(v)[0]
    best, bs = 0, 0
    for g in _groups(on, gap=gap):
        n = int(g[-1] - g[0] + 1)
        if n > best:
            best, bs = n, int(g[0])
    return best, bs


# ------------------------------------------------------------------ calibration

def spines(img, thr=110, frac=0.35, region=None):
    m = black(img, thr)
    H, W = m.shape
    c0, r0, c1, r1 = region if region else (0, 0, W, H)
    sub = m[r0:r1, c0:c1]
    h, w = sub.shape
    vc = {}
    for c in range(w):
        n, s = _longest(sub[:, c])
        if n >= frac * h:
            vc[c] = (n, s)
    hr = {}
    for r in range(h):
        n, s = _longest(sub[r])
        if n >= frac * w:
            hr[r] = (n, s)
    if not vc or not hr:
        raise ValueError("axis spines not found")
    g = _groups(list(vc), gap=2)[0]                  # leftmost vertical line
    n, s = max(vc[c] for c in g)
    cols = [c for c in g if vc[c][0] >= 0.9 * n]
    left = {"c0": c0 + min(cols), "c1": c0 + max(cols), "r0": r0 + s, "r1": r0 + s + n}
    g = _groups(list(hr), gap=2)[-1]                 # lowest horizontal line
    n, s = max(hr[r] for r in g)
    rows = [r for r in g if hr[r][0] >= 0.9 * n]
    bottom = {"r0": r0 + min(rows), "r1": r0 + max(rows), "c0": c0 + s, "c1": c0 + s + n}
    return {"left": left, "bottom": bottom}


def ticks(img, sp, which, thr=110, min_len=6, region=None):
    m = black(img, thr)
    H, W = m.shape
    runs = {}
    if which == "left":
        s = sp["left"]
        for r in range(max(s["r0"] - 8, 0), min(sp["bottom"]["r1"] + 8, H)):
            n, k = 0, s["c0"] - 1
            while k >= 0 and m[r, k]:
                n += 1
                k -= 1
            runs[r] = n
    else:
        s = sp["bottom"]
        cend = region[2] if region else W
        coloured = sat(img) >= 70
        for c in range(max(sp["left"]["c0"] - 8, 0), cend):
            n, k = 0, s["r1"] + 1
            while k < H and k <= s["r1"] + 40 and coloured[k, c] and not m[k, c]:
                k += 1                                 # a coloured line drawn over the axis
            while k < H and m[k, c]:
                n += 1
                k += 1
            runs[c] = n
    good = [p for p, n in runs.items() if min_len <= n <= 300]
    out = []
    if which == "bottom":
        v = sp["left"]
        lo_, hi_, spine_c = v["c0"] - 8, v["c1"] + 8, (v["c0"] + v["c1"]) / 2.0 + 0.5
    else:
        b = sp["bottom"]
        lo_, hi_, spine_c = b["r0"] - 8, b["r1"] + 8, (b["r0"] + b["r1"]) / 2.0 + 0.5
    at_spine = []
    for g in _groups(good):
        if len(g) > 40:
            continue
        L = max(runs[p] for p in g)
        if g[-1] >= lo_ and g[0] <= hi_:              # the tick at the other spine is that spine itself
            at_spine.append(L)
            continue
        out.append(((g[0] + g[-1]) / 2.0 + 0.5, L))
    if at_spine:
        out.append((spine_c, max(at_spine)))
    if not out:
        return []
    longest = max(n for _, n in out)
    return [p for p, n in out if n >= 0.6 * longest]


def fit_axis(pix, labels, scale):
    vals = np.array([np.log10(v) if scale == "log10" else v for v in labels], float)
    pix = sorted(pix)
    n = len(vals)
    if len(pix) < n:
        raise ValueError(f"found {len(pix)} ticks for {n} labels")
    best = None
    for sub in ([pix] if len(pix) == n else combinations(pix, n)):
        p = np.array(sub)
        b, a = np.polyfit(vals, p, 1)
        res = float(np.max(np.abs(p - (a + b * vals))))
        if best is None or res < best[0]:
            best = (res, a, b, list(p))
    res, a, b, used = best
    return {"a": a, "b": b, "misfit": max(res, 0.5), "scale": scale, "marks": used}


def to_px(ax, v):
    u = np.log10(v) if ax["scale"] == "log10" else v
    return ax["a"] + ax["b"] * u


def to_val(ax, p):
    u = (p - ax["a"]) / ax["b"]
    return float(10 ** u) if ax["scale"] == "log10" else float(u)


def calibrate(img, spec):
    region = spec.get("region")
    sp = spines(img, spec.get("spine_thr", 110), spec.get("spine_frac", 0.35), region)
    xt = ticks(img, sp, "bottom", min_len=spec.get("tick_min", 6), region=region)
    yt = ticks(img, sp, "left", min_len=spec.get("tick_min", 6), region=region)
    xa = fit_axis(xt, spec["x"]["labels"], spec["x"].get("scale", "linear"))
    ya = fit_axis(yt, spec["y"]["labels"], spec["y"].get("scale", "linear"))
    c1 = region[2] if region else img.shape[1]
    box = (sp["left"]["c1"] + 1, sp["left"]["r0"], min(max(xt) + 8, c1), sp["bottom"]["r0"])
    return {"x": xa, "y": ya, "box": box, "spines": sp}


# ------------------------------------------------------------------ colour and curves

def colour_mask(img, color, others=(), tol=60):
    f = img.astype(float)
    d = np.sqrt(((f - np.array(color, float)) ** 2).sum(axis=2))
    m = d < tol
    for o in others:
        m &= d <= np.sqrt(((f - np.array(o, float)) ** 2).sum(axis=2))
    return m


def _runs_col(col):
    return [(float(g[0]), float(g[-1] + 1)) for g in _groups(np.where(col)[0])]


def trace(mask, c_from, c_to, min_run=3, max_miss=150, max_len=None, seed=None):
    """Follow one curve. Starts in the longest stretch of columns holding one run, or,
    with `seed` = (column, row), at the run nearest that point (to pick one of two
    curves of the same colour)."""
    runs = {}
    for c in range(c_from, c_to):
        rs = [(a, b) for a, b in _runs_col(mask[:, c]) if b - a >= min_run]
        if max_len:
            rs = [(a, b) for a, b in rs if b - a <= max_len]
        runs[c] = rs
    if seed is not None:
        start = int(seed[0])
        if not runs.get(start):
            return {}
        a, b = min(runs[start], key=lambda t: abs((t[0] + t[1]) / 2 - seed[1]))
    else:
        single = [c for c, rs in runs.items() if len(rs) == 1]
        if not single:
            return {}
        best = max(_groups(single), key=len)
        start = int(best[len(best) // 2])
        a, b = runs[start][0]
    out = {start: ((a + b) / 2, b - a)}
    for direction in (1, -1):
        prev, miss, c = out[start][0], 0, start + direction
        while c_from <= c < c_to:
            rs = runs[c]
            if rs:
                cen = [((a + b) / 2, b - a) for a, b in rs]
                cb = min(cen, key=lambda t: abs(t[0] - prev))
                if abs(cb[0] - prev) < 60 + 40 * miss + cb[1]:
                    out[c] = cb
                    prev, miss = cb[0], 0
                else:
                    miss += 1
            else:
                miss += 1
            if miss > max_miss:
                break
            c += direction
    return out


def _mask(img, spec, cal):
    c0, r0, c1, r1 = cal["box"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    keep = np.zeros_like(m)
    pad = spec.get("inset", 4)
    keep[max(int(r0) - spec.get("above", 0), 0):int(r1) + spec.get("below", 0),
         int(c0) + pad:int(c1) - pad + spec.get("right_extra", 0)] = True
    for (a, b, c, d) in spec.get("blank", []):       # labels of the same colour
        keep[b:d, a:c] = False
    return m & keep


def read_curve(img, spec, at):
    cal = calibrate(img, spec)
    xa, ya = cal["x"], cal["y"]
    m = _mask(img, spec, cal)
    c0, _, c1, _ = cal["box"]
    pad = spec.get("inset", 4)
    ca, cb = int(c0) + pad, int(c1) - pad + spec.get("right_extra", 0)
    if spec.get("x_range"):
        lo_v, hi_v = spec["x_range"]
        ca = max(ca, int(to_px(xa, lo_v)))
        cb = min(cb, int(to_px(xa, hi_v)) + 1)
    if spec.get("pick"):
        tr = pick_runs(m, ca, cb, spec["pick"], spec.get("min_run", 3))
    else:
        tr = trace(m, ca, cb, spec.get("min_run", 3), spec.get("max_miss", 150), spec.get("max_len"),
                   spec.get("seed"))
    if not tr:
        return [{"x": float(x), "y": None, "note": "curve not found"} for x in at]
    thick = float(np.median([L for _, L in tr.values()]))
    gap_max = spec.get("gap", 3)            # bridge a gap (between dashes) of up to this many columns each side
    edge = spec.get("edge", 20)             # at the plot's edge, use the nearest traced column this close
    out = []
    for x in at:
        col = float(to_px(xa, x))
        ci = int(np.floor(col))
        left = [c for c in tr if ci - gap_max <= c <= ci]
        right = [c for c in tr if ci <= c <= ci + gap_max]
        extra, how = 0.0, ""
        if left and right:
            cl_, cr_ = max(left), min(right)
            if cl_ == cr_:
                cen, L = tr[cl_][0], tr[cl_][1]
            else:
                w = (col - (cl_ + 0.5)) / (cr_ - cl_)
                w = min(max(w, 0.0), 1.0)
                cen = (1 - w) * tr[cl_][0] + w * tr[cr_][0]
                L = max(tr[cl_][1], tr[cr_][1])
                extra = 0.5 * abs(tr[cr_][0] - tr[cl_][0])
                how = f"; interpolated across a gap of {cr_ - cl_} columns"
        else:
            cn = min(tr, key=lambda c: abs(c - ci))
            if abs(cn - ci) > edge:
                out.append({"x": float(x), "y": None,
                            "note": "no pixel of this series at this x (a gap in the dashes, hidden, or outside the curve)"})
                continue
            # only on one side, near the plot's edge or a long gap: extrapolate flat, widened by the slope
            side = sorted(c for c in tr if abs(c - cn) <= 6)
            cen, L = tr[cn][0], tr[cn][1]
            if len(side) > 1:
                s_ = abs(tr[side[-1]][0] - tr[side[0]][0]) / max(side[-1] - side[0], 1)
                extra = s_ * abs(cn + 0.5 - col)
            how = f"; nearest traced column {abs(cn - ci)} px away"
        half = 0.5 * thick + 0.5 * max(L - thick, 0.0) + ya["misfit"] + 1.0 + extra
        cl = sorted(c for c in tr if abs(c - ci) <= gap_max + int(xa["misfit"]) + 3)
        if len(cl) > 2:
            ys_ = np.array([tr[c][0] for c in cl])
            dc = np.diff(np.array(cl, float))
            slope = float(np.max(np.abs(np.diff(ys_)) / dc))
            half += slope * xa["misfit"]
        y = to_val(ya, cen)
        a1, a2 = to_val(ya, cen - half), to_val(ya, cen + half)
        out.append({"x": float(x), "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [col, cen],
                    "px_lo": cen - half, "px_hi": cen + half,
                    "note": f"line {thick:.0f} px thick, run {L:.0f} px; x misfit {xa['misfit']:.1f} px "
                            f"({len(xa['marks'])} ticks), y misfit {ya['misfit']:.1f} px ({len(ya['marks'])} ticks)"
                            + how})
    return out


def pick_runs(mask, c_from, c_to, which, min_run=3):
    """Per column, the highest ('top') or lowest ('bottom') run of the mask: for two curves
    of one colour that never cross, the upper or the lower one."""
    out = {}
    for c in range(c_from, c_to):
        rs = [(a, b) for a, b in _runs_col(mask[:, c]) if b - a >= min_run]
        if rs:
            a, b = rs[0] if which == "top" else rs[-1]
            out[c] = ((a + b) / 2, b - a)
    return out


def read_drops(img, spec, at):
    """One vertical segment per series in spec['series'] (same order as `at`): its
    position on the x axis is the reading's y; the reading's x is the series label."""
    cal = calibrate(img, spec)
    xa, ya = cal["x"], cal["y"]
    span = abs(to_px(ya, spec["drop_from"]) - to_px(ya, spec["drop_to"]))
    out = []
    for x, color in zip(at, spec["series"]):
        others = [c for c in spec.get("others", ()) if tuple(c) != tuple(color)]
        sub = dict(spec, color=color, others=others)
        m = _mask(img, sub, cal)
        c0, r0, c1, r1 = cal["box"]
        lens = np.zeros(m.shape[1])
        rows = np.zeros(m.shape[1])
        for c in range(int(c0) + 4, m.shape[1]):
            n, s = _longest(m[:, c], gap=spec.get("drop_gap", 60))   # a dash of another series may cross it
            lens[c] = n
            rows[c] = s + n / 2
        cols = np.where(lens >= 0.8 * span)[0]
        if len(cols) == 0:
            out.append({"x": float(x), "y": None, "note": "no vertical segment of this colour found"})
            continue
        # the rightmost long vertical stroke: the failure, not the near-vertical initial rise at t = 0
        gs = [h for h in _groups(cols, gap=1) if len(h) >= 3] or _groups(cols, gap=1)
        g = gs[-1]
        # the whole stroke: neighbouring columns whose run is at least half the longest
        top_ = lens[g].max()
        wide = np.where(lens >= 0.5 * top_)[0]
        g = next(h for h in _groups(wide, gap=1) if h[0] <= g[0] and h[-1] >= g[-1])
        cen = float(g.mean()) + 0.5
        half = 0.5 * (g[-1] - g[0] + 1) + xa["misfit"] + 1.0
        v = to_val(xa, cen)
        lo, hi = sorted([to_val(xa, cen - half), to_val(xa, cen + half)])
        out.append({"x": float(x), "y": v, "lo": lo, "hi": hi, "px": [cen, float(np.mean(rows[g]))],
                    "note": f"vertical segment {g[-1] - g[0] + 1} px wide, {lens[g].max():.0f} px long; "
                            f"x misfit {xa['misfit']:.1f} px ({len(xa['marks'])} ticks)"})
    return out


def read_spec(image, at, spec):
    kind = spec.get("kind", "curve")
    if kind == "curve":
        return read_curve(image, spec, at)
    if kind == "drops":
        return read_drops(image, spec, at)
    raise ValueError(kind)
