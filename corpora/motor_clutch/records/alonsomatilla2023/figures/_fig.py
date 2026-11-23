"""Shared reading code for the figures of alonsomatilla2023 (MATLAB-style panels).

Each reading file in this folder is a stub naming one panel's printed axis labels and
one series (its colour and a seed point on it), and calls `read_spec`. Stubs pin this
file by SHA-256, so a change here forces every stub to be re-checked.

Everything is found in the image:
  axes    the left and bottom axis lines are the longest dark vertical and horizontal
          strokes of the crop (searched in its left and lower parts). MATLAB draws the
          tick marks inside the box: short dark strokes rising from the bottom axis and
          running right from the left axis. They are matched, in pixel order, to the
          printed labels the stub gives (the only paper values used); when there are
          more strokes than labels the subset with the smallest misfit of a straight
          line (linear or log10) is used. The largest residual (at least half a pixel)
          is the axis misfit. A label at the axis corner itself is placed on the other
          axis line ('x0_at_axis' / 'y0_at_axis').
  curves  pixels within a colour distance `tol` of the series colour (and nearer to it
          than to the stub's other colours), inside the box, outside blanked regions
          (legend, labels). The curve is followed column by column from the seed, keeping
          the run nearest the previous centre; gaps (dashes, markers) are bridged by
          linear interpolation between the traced columns either side.

Intervals (95%): half the line thickness, the y misfit, one pixel, half the jump
across a bridged gap, and the local slope times the x misfit.
"""
from itertools import combinations

import numpy as np


def gray(img):
    return img.astype(float).mean(axis=2)


def sat(img):
    f = img.astype(float)
    return f.max(axis=2) - f.min(axis=2)


def dark(img, thr=110, smax=70):
    return (gray(img) < thr) & (sat(img) < smax)


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _longest(v):
    on = np.where(v)[0]
    best, bs = 0, 0
    for g in _groups(on, gap=2):
        n = int(g[-1] - g[0] + 1)
        if n > best:
            best, bs = n, int(g[0])
    return best, bs


def _extend(cnt, g):
    """Widen a group of axis-line columns (rows) to its neighbours still a quarter as dark."""
    a, b = int(g[0]), int(g[-1])
    thr = 0.25 * cnt[a:b + 1].max()
    while a > 0 and cnt[a - 1] >= thr:
        a -= 1
    while b + 1 < len(cnt) and cnt[b + 1] >= thr:
        b += 1
    return np.arange(a, b + 1)


def axes_lines(img, spec):
    """The left and bottom axis lines: the columns (rows) with the most dark pixels in the
    left (lower) part of the crop; a coloured curve drawn over an axis only interrupts it."""
    m = dark(img, spec.get("thr", 110), spec.get("smax", 70))
    H, W = m.shape
    cw = int(W * spec.get("left_frac", 0.45))
    cnt = m[:, :cw].sum(axis=0)
    cnt[:int(spec.get("left_from", 0))] = 0      # an axis title left of the axis, written vertically
    g = _extend(cnt, _groups(np.where(cnt >= 0.7 * cnt.max())[0])[0])
    rows_on = np.where(m[:, g].any(axis=1))[0]
    big = max(_groups(rows_on, gap=int(0.12 * H)), key=len)
    left = {"c0": int(g[0]), "c1": int(g[-1]), "r0": int(big[0]), "r1": int(big[-1])}
    rh = int(H * (1 - spec.get("bottom_frac", 0.45)))
    cnt = m[rh:, :].sum(axis=1)
    g = _extend(cnt, _groups(np.where(cnt >= 0.7 * cnt.max())[0])[-1]) + rh
    cols_on = np.where(m[g, :].any(axis=0))[0]
    big = max(_groups(cols_on, gap=int(0.12 * W)), key=len)
    bottom = {"r0": int(g[0]), "r1": int(g[-1]), "c0": int(big[0]), "c1": int(big[-1])}
    if spec.get("left_from_top"):
        # curves drawn along the left axis hide it: take the box's left edge where the top
        # line (the row with most dark pixels in the upper part) begins, as thick as that line
        th = int(H * 0.4)
        cnt = m[:th, :].sum(axis=1)
        gt = _extend(cnt, _groups(np.where(cnt >= 0.7 * cnt.max())[0])[0])
        cols_on = np.where(m[gt, :].all(axis=0))[0]
        big = max(_groups(cols_on, gap=3), key=len)
        c0 = int(big[0])
        left = {"c0": c0, "c1": c0 + len(gt) - 1, "r0": int(gt[0]), "r1": bottom["r1"]}
    return left, bottom


def _tick_runs(m, left, bottom, which, max_len):
    out = {}
    if which == "x":
        for c in range(left["c1"] + 3, bottom["c1"] - 2):
            n, r = 0, bottom["r0"] - 1
            while r >= 0 and m[r, c] and n <= max_len:
                n += 1
                r -= 1
            out[c] = n
    else:
        for r in range(left["r0"] + 2, bottom["r0"] - 2):
            n, c = 0, left["c1"] + 1
            while c < m.shape[1] and m[r, c] and n <= max_len:
                n += 1
                c += 1
            out[r] = n
    return out


def _far_runs(m, left, bottom, which, max_len):
    """Tick runs on the opposite sides of the box (MATLAB draws ticks on all four): rising
    downward from the top line, running left from the right line."""
    out = {}
    if which == "x":
        r_top = left["r0"]
        while r_top + 1 < m.shape[0] and m[r_top + 1, (left["c1"] + bottom["c1"]) // 2]:
            r_top += 1
        for c in range(left["c1"] + 3, bottom["c1"] - 2):
            n, r = 0, r_top + 1
            while r < bottom["r0"] and m[r, c] and n <= max_len:
                n += 1
                r += 1
            out[c] = n
    else:
        mid = (left["r0"] + bottom["r0"]) // 2
        c_right = bottom["c1"] + 1
        while c_right - 1 > left["c1"] and not m[mid, c_right - 1]:
            c_right -= 1
        while c_right - 1 > left["c1"] and m[mid, c_right - 1]:
            c_right -= 1
        for r in range(left["r0"] + 2, bottom["r0"] - 2):
            n, c = 0, c_right - 1
            while c > left["c1"] and m[r, c] and n <= max_len:
                n += 1
                c -= 1
            out[r] = n
    return out


def ticks(img, left, bottom, which, spec):
    """Tick positions along one axis: short dark strokes inside the box from either side,
    pooled (a curve drawn over a tick on one side leaves the other)."""
    m = dark(img, spec.get("thr", 110), spec.get("smax", 70))
    lo, hi = spec.get("tick_len", (8, 80))
    found = []
    for runs in (_tick_runs(m, left, bottom, which, hi), _far_runs(m, left, bottom, which, hi)):
        good = [p for p, n in runs.items() if lo <= n <= hi]
        out = []
        for g in _groups(good):
            if which == "x" and g[-1] >= bottom["c1"] - 0.015 * m.shape[1]:
                continue                                  # the right line of the box itself
            if which == "y" and g[0] <= left["r0"] + 0.015 * m.shape[0]:
                continue                                  # the top line of the box itself
            top = max(runs[p] for p in g)
            g = [p for p in g if runs[p] >= 0.8 * top]  # a long tick touching a short one
            if g[-1] - g[0] + 1 > max(25, 0.012 * m.shape[1]):
                continue
            out.append(((g[0] + g[-1]) / 2.0 + 0.5, top))
        if out:
            L = max(n for _, n in out)
            found += [p for p, n in out if n >= spec.get("major", 0.6) * L]
    pooled = []
    for p in sorted(found):
        if pooled and p - pooled[-1][-1] <= max(4, 0.006 * m.shape[1]):
            pooled[-1].append(p)
        else:
            pooled.append([p])
    return [float(np.mean(g)) for g in pooled]


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
    left, bottom = axes_lines(img, spec)
    xt = ticks(img, left, bottom, "x", spec)
    yt = ticks(img, left, bottom, "y", spec)
    m = dark(img, spec.get("thr", 110), spec.get("smax", 70))
    if spec["x"].get("x0_at_axis"):
        xt = xt + [(left["c0"] + left["c1"]) / 2.0 + 0.5]
    if spec["x"].get("x_end_at_axis"):          # the last label at the right line of the box
        found = []
        for frac in (0.2, 0.35, 0.5, 0.65, 0.8):   # several rows: a curve may cross the line at one
            mid = int(left["r0"] + frac * (bottom["r0"] - left["r0"]))
            e = bottom["c1"]
            while e > left["c1"] and not m[mid, e]:
                e -= 1
            c = e
            while c > left["c1"] and m[mid, c - 1]:
                c -= 1
            found.append((c + e) / 2.0 + 0.5)
        xt = xt + [float(np.median(found))]
    if spec["y"].get("y0_at_axis"):
        yt = yt + [(bottom["r0"] + bottom["r1"]) / 2.0 + 0.5]
    if spec["y"].get("y_end_at_axis"):          # the last label at the top line of the box
        mid = (left["c1"] + bottom["c1"]) // 2
        r = left["r0"]
        while r + 1 < m.shape[0] and m[r + 1, mid]:
            r += 1
        yt = yt + [(left["r0"] + r) / 2.0 + 0.5]
    xa = fit_axis(xt, spec["x"]["labels"], spec["x"].get("scale", "linear"))
    ya = fit_axis(yt, spec["y"]["labels"], spec["y"].get("scale", "linear"))
    box = (left["c1"] + 1, left["r0"], bottom["c1"], bottom["r0"])
    return {"x": xa, "y": ya, "box": box}


def colour_mask(img, color, others=(), tol=60):
    f = img.astype(float)
    d = np.sqrt(((f - np.array(color, float)) ** 2).sum(axis=2))
    m = d < tol
    for o in others:
        m &= d <= np.sqrt(((f - np.array(o, float)) ** 2).sum(axis=2))
    return m


def _runs(col, min_run):
    return [(float(g[0]), float(g[-1] + 1)) for g in _groups(np.where(col)[0]) if g[-1] + 1 - g[0] >= min_run]


def trace(mask, c_from, c_to, seed, min_run=3, max_jump=40):
    runs = {c: _runs(mask[:, c], min_run) for c in range(c_from, c_to)}
    start = int(seed[0])
    if not runs.get(start):
        cands = [c for c in runs if runs[c] and abs(c - start) <= 15]
        if not cands:
            return {}
        start = min(cands, key=lambda c: abs(c - start))
    a, b = min(runs[start], key=lambda t: abs((t[0] + t[1]) / 2 - seed[1]))
    out = {start: ((a + b) / 2, b - a)}
    for d in (1, -1):
        prev, miss, c = out[start][0], 0, start + d
        while c_from <= c < c_to:
            rs = runs[c]
            if rs:
                cen = [((a + b) / 2, b - a) for a, b in rs]
                cb = min(cen, key=lambda t: abs(t[0] - prev))
                if abs(cb[0] - prev) < max_jump + 6 * miss + cb[1]:
                    out[c] = cb
                    prev, miss = cb[0], 0
                else:
                    miss += 1
            else:
                miss += 1
            if miss > 400:
                break
            c += d
    return out


def read_curve(img, spec, at):
    cal = calibrate(img, spec)
    xa, ya = cal["x"], cal["y"]
    c0, r0, c1, r1 = cal["box"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    keep = np.zeros_like(m)
    pad = spec.get("inset", 3)
    keep[int(r0) + pad:int(r1) - pad + spec.get("below", 0), int(c0) + pad:int(c1) - pad] = True
    for (a, b, c, d) in spec.get("blank", []):
        keep[b:d, a:c] = False
    m &= keep
    tr = trace(m, int(c0) + pad, int(c1) - pad, spec["seed"], spec.get("min_run", 3), spec.get("max_jump", 40))
    if not tr:
        return [{"x": float(x), "y": None, "note": "curve not found"} for x in at]
    thick = float(np.median([L for _, L in tr.values()]))
    if spec.get("drop_markers"):
        # symbols of the same colour sit on the line: columns whose run is much thicker than
        # the line are left out and bridged like a gap
        tr = {c: v for c, v in tr.items() if v[1] <= spec["drop_markers"] * thick}
    gap_max = spec.get("gap", 60)
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
                cen, L = tr[cl_]
            else:
                w = min(max((col - (cl_ + 0.5)) / (cr_ - cl_), 0.0), 1.0)
                cen = (1 - w) * tr[cl_][0] + w * tr[cr_][0]
                L = max(tr[cl_][1], tr[cr_][1])
                extra = 0.5 * abs(tr[cr_][0] - tr[cl_][0])
                how = f"; interpolated across a gap of {cr_ - cl_} columns"
        else:
            cn = min(tr, key=lambda c: abs(c - ci))
            if abs(cn - ci) > spec.get("edge", 12):
                out.append({"x": float(x), "y": None, "note": "no pixel of this series near this x"})
                continue
            cen, L = tr[cn]
            how = f"; nearest traced column {abs(cn - ci)} px away"
        half = 0.5 * thick + 0.5 * max(L - thick, 0.0) + ya["misfit"] + 1.0 + extra
        near = sorted(c for c in tr if abs(c - ci) <= 6)
        if len(near) > 2:
            ys_ = np.array([tr[c][0] for c in near])
            slope = float(np.max(np.abs(np.diff(ys_)) / np.diff(np.array(near, float))))
            half += min(slope, 20.0) * xa["misfit"]
        y = to_val(ya, cen)
        a1, a2 = to_val(ya, cen - half), to_val(ya, cen + half)
        out.append({"x": float(x), "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [col, cen],
                    "px_lo": cen - half, "px_hi": cen + half,
                    "note": f"line {thick:.0f} px, run {L:.0f} px; x misfit {xa['misfit']:.1f} px "
                            f"({len(xa['marks'])} ticks), y misfit {ya['misfit']:.1f} px ({len(ya['marks'])} ticks)" + how})
    return out


def scaled(spec, width):
    """Pixel positions in a stub (seed, blanked boxes, lengths) are given for a crop
    `ref_width` px wide; scale them to the crop actually rendered."""
    f = width / float(spec.get("ref_width", width))
    s = dict(spec)
    s["seed"] = (spec["seed"][0] * f, spec["seed"][1] * f)
    s["blank"] = [[int(v * f) for v in b] for b in spec.get("blank", [])]
    lo, hi = spec.get("tick_len", (8, 80))
    s["tick_len"] = (max(int(lo * f), 4), int(hi * f))
    s["max_jump"] = spec.get("max_jump", 40) * f
    s["gap"] = int(spec.get("gap", 60) * f)
    s["edge"] = int(spec.get("edge", 12) * f)
    s["inset"] = max(int(spec.get("inset", 3) * f), 2)
    s["left_from"] = int(spec.get("left_from", 0) * f)
    return s


def read_spec(image, at, spec):
    return read_curve(image, scaled(spec, image.shape[1]), at)
