"""Shared reading code for the high-resolution (600-1200 dpi) readings of liu2025.

Everything is found in the rendered crop itself:

  axes     the x axis is the longest dark horizontal line in the lower part of the crop, the y axis
           the longest dark vertical line in its left part (a right-hand y axis: the right part).
           Ticks are the dark runs that stick out of an axis line (outwards, or inwards with
           `inward`), grouped by position; the major ticks are those at least `major` (default 0.75)
           of the longest. The reading names which major tick (0 = leftmost / lowest, counted from
           an optional `skip`) carries which printed label; a least-squares line (linear or log10)
           of pixel against value is the calibration and its largest residual (at least half a
           pixel) is the misfit.
  markers  filled symbols with a dark outline. The symbol's fill colour (within `tol`) is opened
           with a disk of a third of the symbol's size, which removes curves and error bars, and
           each remaining blob seeds a search: the symbol's outline (a ring for a circle, an
           upward or downward triangle) of the size measured from the largest unhidden blob is
           moved over the dark pixels within one symbol size of the seed, and the best-covered
           position is the point. Partly hidden symbols are found by their visible outline; their
           interval is widened by the share of the outline that is hidden.
  bars     the error bar of a symbol is the thin dark vertical line through its centre, followed
           up and down from the outline; its end is where the line (or its cap) stops.
  curves   pixels of a colour, per column; the run nearest a reference (top, bottom or the
           previous position) is the curve.
Intervals (95%): the y misfit, one pixel, half the line or outline thickness, the slope times the
x misfit, and for symbols the hidden share of the outline times the symbol size.
"""
import math

import numpy as np
from scipy import ndimage


# ---------------------------------------------------------------- masks
def gray(img):
    return img.astype(float).mean(axis=2)


def dark(img, thr=110, smax=60):
    f = img.astype(float)
    return (f.mean(axis=2) < thr) & ((f.max(axis=2) - f.min(axis=2)) < smax)


def colour(img, rgb, tol):
    f = img.astype(float)
    return np.sqrt(((f - np.array(rgb, float)) ** 2).sum(axis=2)) <= tol


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _longest(v, gap=2):
    best, bs, start, last = 0, 0, None, None
    for i, x in enumerate(list(v) + [False] * (gap + 2)):
        if x:
            if start is None:
                start = i
            last = i
        elif start is not None and i - last > gap:
            if last + 1 - start > best:
                best, bs = last + 1 - start, start
            start = None
    return best, bs


def source_px(img):
    """Size, in rendered pixels, of one pixel of the raster image the figure was printed from:
    over the non-white part of the crop, the mean length of runs of identical colour along rows
    and columns (a vector figure, or a fine raster, gives about 1)."""
    f = img.astype(int)
    ink = f.mean(axis=2) < 235
    out = []
    for a in (0, 1):
        same = np.all(np.diff(f, axis=1 - a if a else 1) == 0, axis=2) if a == 0 else \
            np.all(np.diff(f, axis=0) == 0, axis=2)
        m = ink[:, 1:] & ink[:, :-1] if a == 0 else ink[1:, :] & ink[:-1, :]
        frac = same[m].mean() if m.any() else 0.0
        out.append(1.0 / max(1.0 - frac, 1e-3))
    return float(np.mean(out))


# ---------------------------------------------------------------- axes
def spines(img, side="left", thr=110, lower=0.5, region=None):
    """Row of the x axis (centre and thickness), column of the y axis, and their extents."""
    m = dark(img, thr)
    H, W = m.shape
    r0 = int(H * lower)
    rows = [(r, *_longest(m[r])) for r in range(r0, H)]
    best = max(n for _, n, _ in rows)
    xr = [r for r, n, _ in rows if n >= 0.9 * best]
    xr = [r for r in xr if r <= min(xr) + 8]
    n, s = max(((n, s) for r, n, s in rows if r in xr))
    if region is None:
        cs = range(0, W // 2) if side == "left" else range(W // 2, W)
    else:
        cs = range(*region)
    cols = [(c, *_longest(m[:, c])) for c in cs]
    bc = max(n for _, n, _ in cols)
    yc = [c for c, n, _ in cols if n >= 0.9 * bc]
    yc = [c for c in yc if c <= min(yc) + 8] if side == "left" else [c for c in yc if c >= max(yc) - 8]
    nc, sc = max(((n, s) for c, n, s in cols if c in yc))
    return {"r0": min(xr), "r1": max(xr), "x_from": s, "x_to": s + n,
            "c0": min(yc), "c1": max(yc), "y_from": sc, "y_to": sc + nc}


def ticks(img, sp, axis, inward=False, thr=110, cap=None, region=None, side="left"):
    """Tick candidates on an axis: {position: length} of dark runs perpendicular to it."""
    m = dark(img, thr)
    H, W = m.shape
    out = {}
    if axis == "x":
        lo, hi = region or (sp["x_from"], sp["x_to"])
        start, step = (sp["r1"] + 1, 1) if not inward else (sp["r0"] - 1, -1)
        cap = cap or int(0.08 * H)
        for c in range(max(lo, 0), min(hi, W)):
            n, r = 0, start
            while 0 <= r < H and m[r, c] and n <= cap:
                n += 1
                r += step
            if 3 <= n <= cap:
                out[c] = n
    else:
        lo, hi = region or (sp["y_from"], sp["y_to"])
        if side == "left":
            start, step = (sp["c0"] - 1, -1) if not inward else (sp["c1"] + 1, 1)
        else:
            start, step = (sp["c1"] + 1, 1) if not inward else (sp["c0"] - 1, -1)
        cap = cap or int(0.08 * W)
        for r in range(max(lo, 0), min(hi, H)):
            n, c = 0, start
            while 0 <= c < W and m[r, c] and n <= cap:
                n += 1
                c += step
            if 3 <= n <= cap:
                out[r] = n
    return out


def majors(runs, frac=0.75, maxw=12):
    gs = _groups(list(runs))
    items = [((g[0] + g[-1] + 1) / 2.0, max(runs[p] for p in g)) for g in gs if len(g) <= maxw]
    if not items:
        return []
    L = max(n for _, n in items)
    return sorted(p for p, n in items if n >= frac * L)


class Ax:
    def __init__(self, pix, marks, scale):
        p = np.array([pix[i] for i, _ in marks], float)
        u = np.array([math.log10(v) if scale == "log10" else v for _, v in marks], float)
        self.b, self.a = np.polyfit(u, p, 1)  # p = a + b u... (polyfit returns slope, intercept)
        self.b, self.a = self.b, self.a
        self.scale = scale
        self.misfit = max(float(np.max(np.abs(p - (self.a + self.b * u)))), 0.5)
        self.n = len(marks)

    def px(self, v):
        return self.a + self.b * (math.log10(v) if self.scale == "log10" else v)

    def val(self, p):
        u = (p - self.a) / self.b
        return 10.0 ** u if self.scale == "log10" else u


def calibrate(img, spec):
    """spec: {"side", "thr", "x": {"marks": [(i, v)], "scale", "region", "inward", "major", "skip"},
    "y": {...}}. Returns x and y Ax objects, the spines and the major tick positions."""
    thr = spec.get("thr", 110)
    sp = spines(img, spec.get("side", "left"), thr, spec.get("lower", 0.5), spec.get("ycols"))
    if "spines" in spec:
        sp.update(spec["spines"](sp))
    out = {"sp": sp}
    for a in ("x", "y"):
        s = spec[a]
        t = ticks(img, sp, a, s.get("inward", False), thr, s.get("cap"), s.get("region"), spec.get("side", "left"))
        mj = majors(t, s.get("major", 0.75))
        if a == "y":
            mj = sorted(mj, reverse=True)  # lowest first
        mj = mj[s.get("skip", 0):]
        out[a + "t"] = mj
        out[a] = Ax(mj, s["marks"], s.get("scale", "linear"))
    return out


# ---------------------------------------------------------------- symbols
def _template(shape, R, t):
    """Outline pixels (dy, dx) of a symbol of half-size R and line thickness t, about its centre.
    Triangles: centre at the middle of their height (the bounding box's centre)."""
    n = int(math.ceil(R + t)) + 1
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(float)
    if shape == "circle":
        d = np.sqrt(xx ** 2 + yy ** 2)
        m = np.abs(d - R) <= t / 2
    else:
        sgn = -1 if shape == "up" else 1  # apex up: apex at dy = -R
        # vertices at height R*sgn (apex) and base at -R*sgn; half-width of base w = 2R/sqrt(3)
        w = 2 * R / math.sqrt(3)
        verts = [(sgn * R, 0.0), (-sgn * R, -w), (-sgn * R, w)]
        m = np.zeros_like(xx, bool)
        for (y1, x1), (y2, x2) in zip(verts, verts[1:] + verts[:1]):
            dy, dx = y2 - y1, x2 - x1
            L2 = dy * dy + dx * dx
            tt = np.clip(((yy - y1) * dy + (xx - x1) * dx) / L2, 0, 1)
            dist = np.sqrt((yy - y1 - tt * dy) ** 2 + (xx - x1 - tt * dx) ** 2)
            m |= dist <= t / 2
    return m


def _filled(shape, R):
    n = int(math.ceil(R)) + 1
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(float)
    if shape == "circle":
        return xx ** 2 + yy ** 2 <= (0.7 * R) ** 2
    sgn = -1 if shape == "up" else 1
    # inner region of the triangle: between the base and the apex, inside the sides (shrunk)
    h = (yy * sgn + R) / (2 * R)  # 0 at the base, 1 at the apex
    return (h > 0.15) & (h < 0.6) & (np.abs(xx) < (1 - h) * 2 * R / math.sqrt(3) * 0.7)


def symbol_size(img, fill_rgb, tol, box, exclude=()):
    """Half-height of the largest blob of the fill colour (the legend symbol is excluded by the
    caller's box); the outline radius is that plus half the outline width."""
    c0, r0, c1, r1 = box
    fill = colour(img, fill_rgb, tol)
    keep = np.zeros_like(fill)
    keep[r0:r1, c0:c1] = True
    for (a, b, c, d) in exclude:
        keep[b:d, a:c] = False
    lab, n = ndimage.label(fill & keep)
    sizes = ndimage.sum(fill, lab, range(1, n + 1))
    rr, cc = np.nonzero(lab == int(np.argmax(sizes)) + 1)
    return (rr.max() - rr.min() + 1) / 2.0


def symbols(img, fill_rgb, tol, shape, ax_x, ax_y, box, R=None, t=None, thr=110, min_cov=0.5,
            min_fill=0.15, exclude=(), size_box=None, src=None, **_):
    """Find symbols of one fill colour inside box (c0, r0, c1, r1): positions where the symbol's
    outline (ring or triangle of half-size R, line t) covers at least min_cov dark pixels and
    whose inside holds at least min_fill of the fill colour; best positions, one per symbol."""
    from scipy.signal import fftconvolve

    c0, r0, c1, r1 = box
    if src is None:
        src = source_px(img)
    keep = np.zeros(img.shape[:2], bool)
    keep[r0:r1, c0:c1] = True
    for (a, b, c, d) in exclude:
        keep[b:d, a:c] = False
    fill = colour(img, fill_rgb, tol)
    dk = dark(img, thr)
    # work on the box only (with a margin), for speed
    m = 80
    ra, rb, ca, cb = max(r0 - m, 0), min(r1 + m, img.shape[0]), max(c0 - m, 0), min(c1 + m, img.shape[1])
    dks, fls, kps = dk[ra:rb, ca:cb].astype(float), fill[ra:rb, ca:cb].astype(float), keep[ra:rb, ca:cb]

    def maps(Rt, tt):
        tp, inn = _template(shape, Rt, tt), _filled(shape, Rt)
        cv = fftconvolve(dks, tp[::-1, ::-1].astype(float), mode="same") / tp.sum()
        fl = fftconvolve(fls, inn[::-1, ::-1].astype(float), mode="same") / inn.sum()
        di = fftconvolve(dks, inn[::-1, ::-1].astype(float), mode="same") / inn.sum()
        return cv, fl, cv - di  # outline found, inside filled, outline found less dark inside

    if R is None and size_box is not None:  # from a given symbol's blob
        R = symbol_size(img, fill_rgb, tol, size_box) + 2.0
    if R is None:  # the size whose outline best matches the best-matching symbol (inside clear)
        best = (-1.0, None)
        for Rt in np.arange(8.0, 70.0, 2.0):
            cv, fl, sc = maps(Rt, t or max(2.0, Rt / 6, src))
            s = float(np.max(np.where(kps & (fl >= 0.5), sc, -1.0)))
            if s > best[0] + 0.01:
                best = (s, Rt)
        R = best[1]
    if t is None:
        t = max(2.0, R / 6, src)
    cv, fl, sc = maps(R, t)
    cov = np.zeros(img.shape[:2])
    cov[ra:rb, ca:cb] = cv
    score = np.zeros(img.shape[:2])
    score[ra:rb, ca:cb] = np.where(kps & (cv >= min_cov) & (fl >= min_fill), np.maximum(sc, 1e-6), 0.0)
    out = []
    taken = []
    order = np.argsort(-score, axis=None)
    for idx in order:
        if score.flat[idx] <= 0:
            break
        yr, xc = divmod(int(idx), score.shape[1])
        if any(abs(yr - a) < R and abs(xc - b) < R for a, b in taken):
            continue
        taken.append((yr, xc))
    for yr, xc in taken:
        cv = float(cov[yr, xc])
        cy, cx = yr + 0.5, xc + 0.5
        cov_ = cv
        hidden = max(0.0, 1.0 - cov_ / 0.85)  # an unhidden outline covers about 85-100%
        tri = 0.0 if shape == "circle" else R / 3.0  # bounding-box centre against centroid
        pad_y = ax_y.misfit + max(1.0, src) + t / 2 + tri + hidden * R
        pad_x = ax_x.misfit + max(1.0, src) + t / 2 + hidden * R
        y = ax_y.val(cy)
        v1, v2 = ax_y.val(cy - pad_y), ax_y.val(cy + pad_y)
        x = ax_x.val(cx)
        out.append({"x": float(x), "y": float(y), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cx), float(cy)], "px_lo": float(cy - pad_y), "px_hi": float(cy + pad_y),
                    "x_lo": float(min(ax_x.val(cx - pad_x), ax_x.val(cx + pad_x))),
                    "x_hi": float(max(ax_x.val(cx - pad_x), ax_x.val(cx + pad_x))),
                    "R": float(R), "cov": cov_,
                    "note": f"{shape} symbol, half-size {R:.0f} px, outline {cov_ * 100:.0f}% found, "
                            f"source raster pixel {src:.1f} px"
                            f"{' (partly hidden)' if hidden > 0 else ''}; x misfit {ax_x.misfit:.1f} px "
                            f"({ax_x.n} ticks), y misfit {ax_y.misfit:.1f} px ({ax_y.n} ticks)"})
    return sorted(out, key=lambda d: d["x"])


def error_bar(img, d, ax_y, thr=110, gap=3, band=2, R=None):
    """Follow the thin dark line through a symbol's centre column up and down from its outline."""
    dk = dark(img, thr)
    cx, cy = d["px"]
    R = R or d["R"]
    c = int(cx)
    on = dk[:, max(0, c - band):c + band + 1].any(axis=1)
    def walk(start, step):
        r, last, miss = start, None, 0
        while 0 <= r < len(on) and miss <= gap:
            if on[r]:
                last, miss = r, 0
            else:
                miss += 1
            r += step
        return last
    up = walk(int(cy - R - 1), -1)
    dn = walk(int(cy + R + 1), 1)
    err = ax_y.misfit + 1.0
    top = up if up is not None and up < cy - R - 1 else cy - R
    bot = dn + 1 if dn is not None and dn > cy + R + 1 else cy + R
    hidden = []
    if top == cy - R:
        hidden.append("upper")
    if bot == cy + R:
        hidden.append("lower")
    vals = [ax_y.val(top), ax_y.val(bot)]
    outer = [ax_y.val(top - err), ax_y.val(bot + err)]
    d["bar_lo"], d["bar_hi"] = float(min(vals)), float(max(vals))
    d["bar_lo_outer"], d["bar_hi_outer"] = float(min(outer)), float(max(outer))
    d["bar_px"] = [float(top), float(bot)]
    if hidden:
        d["note"] += f"; error bar ({' and '.join(hidden)} end) within the symbol: taken as at most its extent"
    return d


# ---------------------------------------------------------------- curves
def curve(img, rgb, tol, ax_x, ax_y, at, box, pick="top", exclude=(), min_run=2, thick=None, near=None):
    """Read a curve of one colour at x values. pick: 'top', 'bottom', 'all' or an index."""
    c0, r0, c1, r1 = box
    src = source_px(img)
    m = colour(img, rgb, tol)
    keep = np.zeros_like(m)
    keep[r0:r1, c0:c1] = True
    for (a, b, c, d) in exclude:
        keep[b:d, a:c] = False
    m &= keep

    def runs(c):
        rs = _groups(np.nonzero(m[:, c])[0])
        return [(float(g[0]), float(g[-1] + 1)) for g in rs if len(g) >= min_run]

    lens = []
    for c in range(c0, c1, 3):
        rs = runs(c)
        if rs:
            lens.append(rs[0][1] - rs[0][0])
    th = thick or (float(np.percentile(lens, 30)) if lens else 3.0)
    out = []
    for x in at:
        col = ax_x.px(x)
        ci = int(math.floor(col))
        rs = runs(ci) if c0 <= ci < c1 else []
        if not rs:
            out.append({"x": float(x), "y": None, "note": "no pixel of this colour at this x"})
            continue
        if pick == "top":
            a, b = rs[0]
        elif pick == "bottom":
            a, b = rs[-1]
        elif callable(pick):
            a, b = pick(rs, x)
        else:
            a, b = rs[pick] if len(rs) > pick else rs[-1]
        cen = 0.5 * (a + b)
        neigh = []
        for cc in (ci - 3, ci + 3):
            rr = runs(cc) if c0 <= cc < c1 else []
            if rr:
                neigh.append(min(rr, key=lambda q: abs(0.5 * (q[0] + q[1]) - cen)))
        slope = abs(0.5 * (neigh[-1][0] + neigh[-1][1]) - 0.5 * (neigh[0][0] + neigh[0][1])) / 6.0 \
            if len(neigh) == 2 else 0.0
        half = 0.5 * max(b - a, th)
        pad = half + ax_y.misfit + max(1.0, src) + slope * (ax_x.misfit + src)
        v1, v2 = ax_y.val(cen - pad), ax_y.val(cen + pad)
        out.append({"x": float(x), "y": float(ax_y.val(cen)), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(col), float(cen)], "px_lo": float(cen - pad), "px_hi": float(cen + pad),
                    "note": f"run {b - a:.0f} px (line {th:.0f} px); x misfit {ax_x.misfit:.1f} px ({ax_x.n} ticks), "
                            f"y misfit {ax_y.misfit:.1f} px ({ax_y.n} ticks)"})
    return out


def blobs(img, fill_rgb, tol, shape, ax_x, ax_y, box, exclude=(), min_area=None, src=None, R=None, open_px=None,
          **_):
    """Symbols of a coarse raster, by their fill: the pixels of the fill colour, opened with a
    disk of one source pixel (anti-aliasing and thin lines go), split into connected blobs. A
    symbol's position is its fill's centroid (for a triangle, the centroid of the triangle).
    The typical (median) blob area sets the symbol size; a blob under 60% of it is a symbol
    partly hidden under another, and its interval is widened by half the symbol size."""
    c0, r0, c1, r1 = box
    if src is None:
        src = source_px(img)
    keep = np.zeros(img.shape[:2], bool)
    keep[r0:r1, c0:c1] = True
    for (a, b, c, d) in exclude:
        keep[b:d, a:c] = False
    m = colour(img, fill_rgb, tol) & keep
    k = open_px or max(1, int(round(src / 2)))  # open_px: wider, to cut away lines of the symbols' colour
    se = np.add.outer(np.arange(-k, k + 1) ** 2, np.arange(-k, k + 1) ** 2) <= k * k
    m = ndimage.binary_opening(m, structure=se)
    lab, n = ndimage.label(m)
    if n == 0:
        return []
    areas = ndimage.sum(m, lab, range(1, n + 1))
    amin = min_area or 4 * src * src
    big = float(areas.max())  # an unhidden symbol's fill
    Rf = R or math.sqrt(big / math.pi)  # radius of a whole fill
    # pieces of one symbol cut by a line drawn over it: join pieces whose boxes lie within one
    # fill diameter of each other; the joined symbol is at the centre of their common box
    pieces = []
    for i in np.argsort(-areas):
        if areas[i] < amin:
            continue
        rr, cc = np.nonzero(lab == i + 1)
        pieces.append([rr.min(), rr.max() + 1, cc.min(), cc.max() + 1, float(areas[i]), rr.mean(), cc.mean(), 1])
    groups = []
    span = 2.2 * Rf if shape == "circle" else 2.8 * Rf  # a triangle's box is wider than its area's circle
    for p in pieces:
        for g in groups:
            if max(g[1], p[1]) - min(g[0], p[0]) <= span and max(g[3], p[3]) - min(g[2], p[2]) <= span:
                g[0], g[1], g[2], g[3] = min(g[0], p[0]), max(g[1], p[1]), min(g[2], p[2]), max(g[3], p[3])
                g[4] += p[4]
                g[7] += 1
                break
        else:
            groups.append(list(p))
    out = []
    for g in groups:
        a = g[4]
        if g[7] > 1 or shape == "circle":
            cy, cx = (g[0] + g[1]) / 2.0, (g[2] + g[3]) / 2.0
            if shape != "circle":  # a triangle's centroid is a third of the way from its base
                cy = g[0] + (2 / 3 if shape == "up" else 1 / 3) * (g[1] - g[0])
        else:
            cy, cx = g[5] + 0.5, g[6] + 0.5
        hidden = a < 0.6 * big
        # a partly hidden symbol: its visible part may sit anywhere within it, up to the hidden share
        pad = ax_y.misfit + max(1.0, src) + (Rf * (1.0 - a / big) if hidden else 0.0) + \
            (0.0 if shape == "circle" else 0.15 * Rf)
        v1, v2 = ax_y.val(cy - pad), ax_y.val(cy + pad)
        out.append({"x": float(ax_x.val(cx)), "y": float(ax_y.val(cy)), "lo": float(min(v1, v2)),
                    "hi": float(max(v1, v2)), "px": [float(cx), float(cy)], "px_lo": float(cy - pad),
                    "px_hi": float(cy + pad), "R": float(Rf),
                    "note": f"{shape} symbol by its fill: {a:.0f} px of a typical {big:.0f}"
                            f"{' (partly hidden under another symbol)' if hidden else ''}; source raster pixel "
                            f"{src:.1f} px; x misfit {ax_x.misfit:.1f} px ({ax_x.n} ticks), y misfit "
                            f"{ax_y.misfit:.1f} px ({ax_y.n} ticks)"})
    return sorted(out, key=lambda d: d["x"])


def bars(img, colours, tol, ax_y, box, labels, min_width=12, thr=110, err=False, gap=3, smax=60):
    """Bars of a bar chart standing on the baseline (the bottom of box). A bar is a run of
    columns where one of the colours reaches down to just above the baseline; its value is its
    top edge (median over the middle 60% of its columns), at its centre. Bars are labelled left
    to right with `labels` (the category numbers printed under them). With err, the error bar
    is the thin dark vertical line through the bar's centre: followed up from the top edge to its
    cap, and down inside the bar if it is drawn there (else the lower end is the mirror of the
    upper one, and the note says so)."""
    c0, r0, c1, r1 = box
    src = source_px(img)
    m = np.zeros(img.shape[:2], bool)
    for rgb in colours:
        m |= colour(img, rgb, tol)
    keep = np.zeros_like(m)
    keep[r0:r1, c0:c1] = True
    m &= keep
    base = r1 - 1
    probe = base - max(3, int(2 * src))
    tops = {}
    for c in range(c0, c1):
        if not m[probe - 2:probe + 1, c].any():
            continue
        r = probe
        miss = 0
        top = r
        while r > r0 and miss <= 2:
            if m[r, c]:
                top, miss = r, 0
            else:
                miss += 1
            r -= 1
        tops[c] = top
    cols = sorted(tops)
    groups = [g for g in _groups(cols) if len(g) >= min_width]
    dk = dark(img, thr, smax)
    out = []
    for lab, g in zip(labels, groups):
        n = len(g)
        mid = g[int(0.2 * n):int(0.8 * n) + 1]
        top = float(np.median([tops[c] for c in mid]))
        cx = 0.5 * (g[0] + g[-1] + 1)
        pad = ax_y.misfit + max(1.0, src)
        v1, v2 = ax_y.val(top - pad), ax_y.val(top + pad)
        d = {"x": float(lab), "y": float(ax_y.val(top)), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
             "px": [float(cx), float(top)], "px_lo": float(top - pad), "px_hi": float(top + pad),
             "note": f"bar {n} px wide, top edge; source raster pixel {src:.1f} px; y misfit {ax_y.misfit:.1f} px "
                     f"({ax_y.n} ticks)"}
        if err:
            ci = int(cx)
            on = dk[:, max(0, ci - 3):ci + 4].any(axis=1)
            r, last, miss = int(top) - 1, None, 0
            while r > 0 and miss <= gap:
                if on[r]:
                    last, miss = r, 0
                else:
                    miss += 1
                r -= 1
            up = float(last) if last is not None and last < top - 2 else None
            r, lastd, miss = int(top) + 1, None, 0
            while r < base and miss <= gap:
                if on[r]:
                    lastd, miss = r, 0
                else:
                    miss += 1
                r += 1
            down = float(lastd + 1) if lastd is not None and lastd > top + 2 else None
            if up is None:
                d["note"] += "; no error bar found above the bar"
            else:
                e = ax_y.misfit + max(1.0, src)
                hi, hi_o = ax_y.val(up), ax_y.val(up - e)
                if down is None:
                    lo, lo_o = 2 * d["y"] - hi, 2 * d["y"] - hi_o
                    d["note"] += "; lower end of the error bar hidden in the bar: taken as the mirror of the upper"
                else:
                    lo, lo_o = ax_y.val(down), ax_y.val(down + e)
                d["bar_lo"], d["bar_hi"] = float(min(lo, hi)), float(max(lo, hi))
                d["bar_lo_outer"], d["bar_hi_outer"] = float(min(lo_o, hi_o)), float(max(lo_o, hi_o))
                d["bar_px"] = [float(up), float(down if down is not None else 2 * top - up)]
        out.append(d)
    if len(groups) != len(labels):
        for d in out:
            d["note"] += f"; {len(groups)} bars found for {len(labels)} labels"
    return out


def boxes(img, rgb, tol, ax_x, ax_y, box, xticks, min_width=40, min_frac=0.35, thr=110, cap_frac=0.5, caps=True):
    """Boxes of a box plot drawn as filled rectangles (mean +- s.e.m. here) with whiskers. A box is
    a run of columns where the fill colour covers rows of the plot; its top and bottom edges are
    the first and last rows where the fill covers at least min_frac of its columns (points drawn
    over it are ignored). The value is the middle of the box, and its interval is the box itself
    (widened by the misfit). Whiskers: the nearest rows above and below the box where a dark
    horizontal run spans at least cap_frac of the box width around its centre (the caps; plotted
    points give only short dark runs). x is the value of the nearest x tick (xticks: values)."""
    c0, r0, c1, r1 = box
    src = source_px(img)
    m = colour(img, rgb, tol)
    keep = np.zeros_like(m)
    keep[r0:r1, c0:c1] = True
    m &= keep
    colfill = m.sum(axis=0)
    cols = [c for c in range(c0, c1) if colfill[c] >= 15]
    groups = [g for g in _groups(cols, gap=45) if g[-1] - g[0] + 1 >= min_width]  # points over a box split it
    dk = dark(img, thr)
    tick_px = [(ax_x.px(v), v) for v in xticks]
    out = []
    for g in groups:
        a, b = int(g[0]), int(g[-1]) + 1
        frac = m[:, a:b].mean(axis=1)
        rows = np.nonzero(frac >= min_frac)[0]
        if len(rows) == 0:
            continue
        rows = max(_groups(rows, gap=12), key=len)  # the box: the longest run (across its mean line)
        top, bot = float(rows.min()), float(rows.max() + 1)
        cx = 0.5 * (a + b)
        mid = 0.5 * (top + bot)
        e = ax_y.misfit + max(1.0, src) + 1.0  # the box's outline lies outside the fill: one more pixel
        v_mid = ax_y.val(mid)
        vt, vb = ax_y.val(top - e), ax_y.val(bot + e)
        x = min(tick_px, key=lambda q: abs(q[0] - cx))[1]
        d = {"x": float(x), "y": float(v_mid), "lo": float(min(vt, vb)), "hi": float(max(vt, vb)),
             "px": [float(cx), float(mid)], "px_lo": float(top - e), "px_hi": float(bot + e),
             "note": f"box {b - a} px wide, fill rows {top:.0f}-{bot:.0f}; value at its middle, interval the box; "
                     f"source raster pixel {src:.1f} px; y misfit {ax_y.misfit:.1f} px ({ax_y.n} ticks)"}
        if not caps:
            out.append(d)
            continue
        w = b - a
        need = cap_frac * w

        def cap_row(rng):
            for r in rng:
                row = dk[r, a:b]
                if not row.any():
                    continue
                best = max((q[-1] - q[0] + 1 for q in _groups(np.nonzero(row)[0], gap=3)), default=0)
                if best >= need:
                    return r
            return None
        skip = 4 + int(2 * max(src, 3))  # past the box's own outline
        up = cap_row(range(int(top) - skip, r0, -1))
        dn = cap_row(range(int(bot) + skip, r1))
        if up is not None and dn is not None:
            ee = ax_y.misfit + max(1.0, src)
            hi, lo = ax_y.val(up), ax_y.val(dn + 1)
            d["bar_lo"], d["bar_hi"] = float(min(lo, hi)), float(max(lo, hi))
            ho, lo_o = ax_y.val(up - ee), ax_y.val(dn + 1 + ee)
            d["bar_lo_outer"], d["bar_hi_outer"] = float(min(lo_o, ho)), float(max(lo_o, ho))
            d["bar_px"] = [float(up), float(dn + 1)]
        else:
            d["note"] += "; whisker caps not found"
        out.append(d)
    return out


def plateaus(img, spec, t_read, labels, sat=80, exclude=(), colours=None):
    """The steady values of several time courses, each labelled in the panel by its parameter
    (labels: those values, top to bottom as the curves lie at t_read). At the column of t_read,
    the runs of saturated (coloured) pixels are the curves; curves of the same parameter drawn on
    top of each other (here three substrate viscosities) make one run. The value is the run's
    centre and its interval the whole run (all the overlapping curves), widened by the y misfit
    and a source pixel. The returned x is the label, not the time."""
    cal = calibrate(img, spec)
    ax, ay, sp = cal["x"], cal["y"], cal["sp"]
    src = source_px(img)
    f = img.astype(int)
    m = (f.max(axis=2) - f.min(axis=2)) > sat
    if colours:  # only the curves of these colours (rgb, tol)
        cm = np.zeros_like(m)
        for rgb, tol in colours:
            cm |= colour(img, rgb, tol)
        m &= cm
    m[:, : sp["c1"] + 2] = False
    m[sp["r0"] - 1:, :] = False
    for (a, b, c, d) in exclude:
        m[b:d, a:c] = False
    c = int(ax.px(t_read))
    band = m[:, c - 2:c + 3].any(axis=1)
    runs = [(float(g[0]), float(g[-1] + 1)) for g in _groups(np.nonzero(band)[0], gap=3) if len(g) >= 2]
    out = []
    for lab, (a, b) in zip(labels, runs):
        cen = 0.5 * (a + b)
        pad = 0.5 * (b - a) + ay.misfit + max(1.0, src)
        v1, v2 = ay.val(cen - pad), ay.val(cen + pad)
        out.append({"x": float(lab), "y": float(ay.val(cen)), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(cen)], "px_lo": float(cen - pad), "px_hi": float(cen + pad),
                    "note": f"plateau at t = {t_read:g} s: run {b - a:.0f} px (the overlapping curves); source raster "
                            f"pixel {src:.1f} px; y misfit {ay.misfit:.1f} px ({ay.n} ticks)"})
    if len(runs) != len(labels):
        for d in out:
            d["note"] += f"; {len(runs)} runs found for {len(labels)} labels"
    return out


def read_symbols(image, spec, fill, tol, shape, exclude=(), bars=False, mode="outline", **kw):
    """Calibrate, find the symbols, and (optionally) their error bars. With spec["break"] =
    (column fraction, value): symbols right of that share of the crop's width (past a broken
    axis) sit on the axis's last major tick, whose label is the value; they are read there
    if within a symbol's size of that tick, else returned without a value."""
    cal = calibrate(image, spec)
    sp = cal["sp"]
    box = spec.get("box", lambda s: (s["c1"] + 2, s["y_from"], s["x_to"], s["r0"] - 1))(sp)
    find = blobs if mode == "fill" else symbols
    rows = find(image, fill, tol, shape, cal["x"], cal["y"], box, exclude=exclude, **kw)
    if "break" in spec:
        frac, val = spec["break"]
        cut = frac * image.shape[1]
        t = ticks(image, sp, "x", spec["x"].get("inward", False), spec.get("thr", 110),
                  region=(int(cut), image.shape[1]))
        last = max(majors(t, spec["x"].get("major", 0.75)))
        for d in rows:
            if d["px"][0] > cut:
                if abs(d["px"][0] - last) <= max(2 * d["R"], 0.025 * image.shape[1]):
                    d["x"] = float(val)
                    d["note"] += (f"; right of the axis break, {last - d['px'][0]:.0f} px left of the last major "
                                  f"tick, the only labelled one there ({val:g}): read as at that tick")
                else:
                    d["y"] = None
                    d["note"] += "; right of the axis break, not on a labelled tick"
    if bars:
        rows = [error_bar(image, d, cal["y"]) for d in rows]
    return clean(rows)


def clean(rows, keys=("R", "cov", "x_lo", "x_hi")):
    for d in rows:
        for k in keys:
            d.pop(k, None)
    return rows
