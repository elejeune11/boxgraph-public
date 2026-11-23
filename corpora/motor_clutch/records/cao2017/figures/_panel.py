"""Shared reading code for the figures of cao2017 (vector plots with black frames).

Adapted from bangasser2013/figures/_panel.py. Every reading file in this directory
is a small stub that names one panel, one series and its axis labels, and calls
`read_spec` here. The stubs pin this file by its SHA-256, so a change here forces
each stub to be re-checked.

Everything is found in the image:
  axes      the black spines are the longest dark vertical / horizontal lines;
            the tick marks are the short dark strokes sticking out of a spine
            (outside the plot box). The major ticks are matched, in order, to
            the printed labels given in the stub (the only paper values used);
            a linear fit of pixel against value gives the calibration and its
            misfit (largest residual, at least half a pixel). Ticks may point
            out of the box or (`ticks_in`) into it; where a corner tick is
            covered, the frame line standing at a labelled value is used as
            that mark (`x_spines`, `y_spine_bottom`).
  curves    pixels nearest in colour to the series' colour among the panel's
            series colours (and within a tolerance); per column, the runs of
            that mask; the curve is followed from its longest single-run stretch
            outward, keeping the run nearest the previous one. The value is the
            run's centre.
  bars      blobs of one colour standing on the x spine; the top edge is the
            value; error bars are the thin dark line above (and below) the bar's
            centre, their ends the caps.

Intervals (95%): half a line thickness of placement error on the curve's centre,
plus half the excess of the run over the normal line thickness where the curve is
steep, plus the calibration misfit, plus one pixel of quantisation, plus the
curve's slope times the x misfit.
"""
from itertools import combinations

import numpy as np
from scipy import ndimage as ndi


def gray(img):
    return img.astype(float).mean(axis=2)


def sat(img):
    f = img.astype(float)
    return f.max(axis=2) - f.min(axis=2)


def black(img, thr=110, smax=70):
    return (gray(img) < thr) & (sat(img) < smax)


def _groups(idx, gap=1):
    """Split sorted integer positions into runs (bridging gaps up to `gap`)."""
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


# ---------------------------------------------------------------------------- spines

def spines(img, region=None, thr=110, frac=0.35, bridge=3):
    """The black axis lines: left / right vertical spines and bottom / top horizontal ones.
    `region` = (c0, r0, c1, r1) restricts the search."""
    m = black(img, thr)
    H, W = m.shape
    c0, r0, c1, r1 = region if region else (0, 0, W, H)
    sub = m[r0:r1, c0:c1]
    h, w = sub.shape

    def longest(v, gap=bridge):
        on = np.where(v)[0]
        if len(on) == 0:
            return 0, 0
        best, bs = 0, 0
        for g in _groups(on, gap=gap):
            n = int(g[-1] - g[0] + 1)
            if n > best:
                best, bs = n, int(g[0])
        return best, bs

    vcols = []
    for c in range(w):
        n, s = longest(sub[:, c])
        if n >= frac * h:
            vcols.append((c, n, s))
    hrows = []
    for r in range(h):
        n, s = longest(sub[r])
        if n >= frac * w:
            hrows.append((r, n, s))
    if not vcols:
        raise ValueError("no vertical axis spine found")
    vg = _groups([c for c, _, _ in vcols], gap=2)
    hg = _groups([r for r, _, _ in hrows], gap=2) if hrows else []
    info = {c: (n, s) for c, n, s in vcols}
    hinfo = {r: (n, s) for r, n, s in hrows}

    # a spine's width: the columns (rows) dark over at least 90% of its length (a coloured curve
    # drawn across it interrupts its longest dark run, but not its coverage)
    def vspine(g):
        n, s = max(info[c] for c in g)
        col = [c for c in range(max(g[0] - 3, 0), min(g[-1] + 4, w)) if sub[s:s + n, c].mean() >= 0.9]
        return {"c0": c0 + min(col), "c1": c0 + max(col), "r0": r0 + s, "r1": r0 + s + n}

    def hspine(g):
        n, s = max(hinfo[r] for r in g)
        row = [r for r in range(max(g[0] - 3, 0), min(g[-1] + 4, h)) if sub[r, s:s + n].mean() >= 0.9]
        return {"r0": r0 + min(row), "r1": r0 + max(row), "c0": c0 + s, "c1": c0 + s + n}

    return {"left": vspine(vg[0]), "right": vspine(vg[-1]) if len(vg) > 1 else None,
            "bottom": hspine(hg[-1]) if hg else None, "top": hspine(hg[0]) if len(hg) > 1 else None}


def ticks(img, sp, which, thr=110, min_len=6, inside=False, max_len=300):
    """Centres of the tick marks on one spine: 'left' (y) or 'bottom' (x); outside the box, or
    with `inside`, pointing into it. Strokes longer than `max_len` (a frame line, a dashed line
    touching the spine) are not ticks."""
    m = black(img, thr)
    H, W = m.shape
    runs = {}
    if which == "left":
        s = sp["left"]
        start, step = (s["c1"] + 1, 1) if inside else (s["c0"] - 1, -1)
        for r in range(max(s["r0"] - 6, 0), min(s["r1"] + 6, H)):
            n, k = 0, start
            while 0 <= k < W and m[r, k]:
                n += 1
                k += step
            runs[r] = n
    else:
        s = sp["bottom"]
        start, step = (s["r0"] - 1, -1) if inside else (s["r1"] + 1, 1)
        for c in range(max(s["c0"] - 6, 0), min(s["c1"] + 6, W)):
            n, k = 0, start
            while 0 <= k < H and m[k, c]:
                n += 1
                k += step
            runs[c] = n
    good = [p for p, n in runs.items() if min_len <= n <= max_len]
    out = []
    for g in _groups(good):
        if len(g) > 40:
            continue
        lens = np.array([runs[p] for p in g], float)
        centre = (g[0] + g[-1]) / 2.0 + 0.5
        if which == "bottom":
            for key in ("left", "right"):
                v = sp.get(key)
                if v is not None and g[0] - 3 <= v["c0"] <= g[-1] + 3:
                    centre = (v["c0"] + v["c1"]) / 2.0 + 0.5
        else:
            for key in ("bottom", "top"):
                v = sp.get(key)
                if v is not None and g[0] - 3 <= v["r0"] <= g[-1] + 3:
                    centre = (v["r0"] + v["r1"]) / 2.0 + 0.5
        out.append((centre, float(lens.max())))
    if not out:
        return []
    longest = max(n for _, n in out)
    return [p for p, n in out if n >= 0.6 * longest]


def fit_axis(pix, labels):
    """Match tick pixels to labels (same count, or the best evenly fitting subset)."""
    vals = np.array(labels, float)
    pix = sorted(pix)
    n = len(vals)
    if len(pix) < n:
        raise ValueError(f"found {len(pix)} ticks for {n} labels")
    best = None
    cands = [pix] if len(pix) == n else combinations(pix, n)
    for sub in cands:
        p = np.array(sub)
        b, a = np.polyfit(vals, p, 1)
        res = float(np.max(np.abs(p - (a + b * vals))))
        if best is None or res < best[0]:
            best = (res, a, b, list(p))
    res, a, b, used = best
    return {"a": a, "b": b, "misfit": max(res, 0.5), "marks": used}


def to_px(ax, v):
    return ax["a"] + ax["b"] * v


def to_val(ax, p):
    return float((p - ax["a"]) / ax["b"])


def calibrate(img, spec):
    sp = spines(img, spec.get("region"), thr=spec.get("spine_thr", 110), frac=spec.get("spine_frac", 0.35))
    kw = {"min_len": spec.get("tick_min", 6), "inside": spec.get("ticks_in", False),
          "max_len": spec.get("tick_max", 300)}
    xt = ticks(img, sp, "bottom", **kw)
    yt = ticks(img, sp, "left", **kw)
    xl, yl = list(spec["x"]["labels"]), list(spec["y"]["labels"])
    # frame lines that stand at a labelled value (a tick hidden in a corner): their centres are marks
    if spec.get("x_spines"):
        lv, rv = spec["x_spines"]
        xt = [(sp["left"]["c0"] + sp["left"]["c1"]) / 2.0 + 0.5] + sorted(xt) + [(sp["right"]["c0"] + sp["right"]["c1"]) / 2.0 + 0.5]
        xl = [lv] + xl + [rv]
    if spec.get("y_spine_bottom") is not None:
        yt = sorted(yt) + [(sp["bottom"]["r0"] + sp["bottom"]["r1"]) / 2.0 + 0.5]
        yl = yl + [spec["y_spine_bottom"]]
    xa = fit_axis(xt, xl)
    ya = fit_axis(yt, yl)
    box = (sp["left"]["c1"] + 1, sp["left"]["r0"],
           (sp["right"]["c0"] if sp["right"] else max(xt) + 8), sp["bottom"]["r0"])
    return {"x": xa, "y": ya, "box": box, "spines": sp}


# ---------------------------------------------------------------------------- colour

def colour_mask(img, color, others=(), tol=60):
    f = img.astype(float)
    d = np.sqrt(((f - np.array(color, float)) ** 2).sum(axis=2))
    m = d < tol
    for o in others:
        do = np.sqrt(((f - np.array(o, float)) ** 2).sum(axis=2))
        m &= d <= do
    return m


def _runs_col(col):
    on = np.where(col)[0]
    return [(float(g[0]), float(g[-1] + 1)) for g in _groups(on)]


def trace(mask, c_from, c_to, min_run=3, max_miss=120):
    """Follow one curve across columns c_from..c_to. Returns {col: (centre, length)}."""
    runs = {}
    for c in range(c_from, c_to):
        runs[c] = [(a, b) for a, b in _runs_col(mask[:, c]) if b - a >= min_run]
    single = [c for c, rs in runs.items() if len(rs) == 1]
    if not single:
        return {}
    best = max(_groups(single), key=len)
    start = int(best[len(best) // 2])
    out = {}
    a, b = runs[start][0]
    out[start] = ((a + b) / 2, b - a)
    for direction in (1, -1):
        prev = out[start][0]
        miss = 0
        c = start + direction
        while c_from <= c < c_to:
            rs = runs[c]
            if rs:
                cen = [((a + b) / 2, b - a) for a, b in rs]
                cbest = min(cen, key=lambda t: abs(t[0] - prev))
                if abs(cbest[0] - prev) < 60 + 40 * miss + cbest[1]:
                    out[c] = cbest
                    prev = cbest[0]
                    miss = 0
                else:
                    miss += 1
            else:
                miss += 1
            if miss > max_miss:
                break
            c += direction
    return out


def read_curve(img, spec, at):
    cal = calibrate(img, spec)
    xa, ya = cal["x"], cal["y"]
    c0, r0, c1, r1 = cal["box"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    pad = spec.get("inset", 4)
    keep = np.zeros_like(m)
    keep[int(r0):int(r1) + spec.get("below", 0), int(c0) + pad:int(c1) - pad] = True
    for (a, b, c, d) in spec.get("blank", []):    # legend swatches and labels of the same colour
        keep[b:d, a:c] = False
    m &= keep
    ca, cb = int(c0) + pad, int(c1) - pad
    tr = trace(m, ca, cb, spec.get("min_run", 3), spec.get("max_miss", 120))
    if not tr:
        return [{"x": float(x), "y": None, "note": "curve not found"} for x in at]
    thick = float(np.median([L for _, L in tr.values()]))
    out = []
    for x in at:
        col = float(to_px(xa, x))
        ci = int(np.floor(col))
        near = [c for c in tr if abs(c - ci) <= 3]
        reach = 0.0
        if not near:
            cn = min(tr, key=lambda c: abs(c - ci))
            if abs(cn - ci) <= 20:
                near = [c for c in tr if abs(c - cn) <= 3]
                reach = float(abs(cn - ci))
        if not near:
            out.append({"x": float(x), "y": None, "note": "no pixel of this series at this x"})
            continue
        cen = float(np.mean([tr[c][0] for c in near]))
        L = float(max(tr[c][1] for c in near))
        half = 0.5 * thick + 0.5 * max(L - thick, 0.0) + ya["misfit"] + 1.0
        cl = [c for c in tr if abs(c - ci) <= 3 + int(xa["misfit"]) + 2]
        if len(cl) > 2:
            ys_ = np.array([tr[c][0] for c in sorted(cl)])
            slope = float(np.max(np.abs(np.diff(ys_))))
            half += slope * (xa["misfit"] + reach)
        y = to_val(ya, cen)
        a1, a2 = to_val(ya, cen - half), to_val(ya, cen + half)
        out.append({"x": float(x), "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [col, cen],
                    "px_lo": cen - half, "px_hi": cen + half,
                    "note": f"line {thick:.0f} px thick, run {L:.0f} px; x misfit {xa['misfit']:.1f} px "
                            f"({len(xa['marks'])} ticks), y misfit {ya['misfit']:.1f} px ({len(ya['marks'])} ticks)"})
    return out


# ---------------------------------------------------------------------------- bars

def _bar_end(dark, col, start, step, stop, max_gap=6):
    """From row `start`, walk along column `col` (+-2 px) while it is dark; return the last dark row."""
    H = dark.shape[0]
    r, last, gap = start, None, 0
    while 0 <= r < H and r != stop and gap <= max_gap:
        if dark[r, max(col - 2, 0):col + 3].any():
            last, gap = r, 0
        else:
            gap += 1
        r += step
    return last


def read_bars(img, spec, at):
    """Bars of one colour (or hatch: spec['hatch'] reads a bar by its outline) on a categorical
    x axis. The stub gives the category positions (spec['categories']) left to right."""
    sp = spines(img, spec.get("region"), thr=spec.get("spine_thr", 110), frac=spec.get("spine_frac", 0.35))
    ya = fit_axis(ticks(img, sp, "left", min_len=spec.get("tick_min", 6)), spec["y"]["labels"])
    base = sp["bottom"]["r0"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    m[base - 1:] = False
    m[:, :sp["left"]["c1"] + 2] = False
    if sp["right"] is not None:
        m[:, sp["right"]["c0"] - 2:] = False
    for (a, b, c, d) in spec.get("blank", []):
        m[b:d, a:c] = False
    m = ndi.binary_opening(m, iterations=spec.get("open", 2))
    lab, n = ndi.label(m)
    bars = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if len(rr) < spec.get("min_area", 200) or rr.max() < base - 12:
            continue
        width = cc.max() - cc.min() + 1
        if width < spec.get("min_width", 15):
            continue
        inner = range(cc.min() + width // 4, cc.max() - width // 4 + 1)
        tops = [np.where(lab[:, c] == i)[0].min() for c in inner if (lab[:, c] == i).any()]
        top = float(np.median(tops))
        spread = float(np.max(tops) - np.min(tops)) if tops else 0.0
        bars.append((float(cc.mean()) + 0.5, top, spread, width))
    bars.sort()
    cats = spec["categories"]
    if len(bars) != len(cats):
        return [{"x": float(v), "y": None, "note": f"found {len(bars)} bars for {len(cats)} categories"} for v in cats]
    dark = black(img, spec.get("bar_thr", 110))
    out = []
    for (c, top, spread, width), x in zip(bars, cats):
        e = 1.0 + 0.5 * spread + ya["misfit"] + spec.get("edge_err", 1.0)
        y = to_val(ya, top)
        a1, a2 = to_val(ya, top - e), to_val(ya, top + e)
        row = {"x": float(x), "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [c, top],
               "note": f"bar top edge ({width} px wide); y misfit {ya['misfit']:.1f} px ({len(ya['marks'])} ticks)"}
        if spec.get("error_bars"):
            ci = int(round(c))
            up = _bar_end(dark, ci, int(top) - 3, -1, 0)
            if up is not None and int(top) - up > 6:
                # the lower half is hidden in (or drawn over) the bar: look for dark pixels below the top
                inside = int(top) + 3 + spec.get("frame_px", 6)
                dn = _bar_end(dark, ci, inside, +1, base - 2)
                hidden = dn is None or dn - inside < 4 or not spec.get("lower_visible", False)
                if hidden:
                    dn = top + (top - up)
                    row["note"] += "; lower bar end hidden in the bar: mirrored from the upper"
                hi_v, lo_v = to_val(ya, up), to_val(ya, dn)
                pp = (2.5 + ya["misfit"]) / abs(ya["b"])
                row.update({"bar_lo": lo_v, "bar_hi": hi_v, "bar_lo_outer": lo_v - pp, "bar_hi_outer": hi_v + pp,
                            "px_lo": float(up), "px_hi": float(dn)})
                row["note"] += "; error bar ends read along the bar's centre column"
            else:
                row["note"] += "; no error bar found above the bar"
        out.append(row)
    return out


def read_spec(image, at, spec):
    kind = spec.get("kind", "curve")
    if kind == "curve":
        return read_curve(image, spec, at)
    if kind == "bars":
        return read_bars(image, spec, at)
    raise ValueError(kind)
