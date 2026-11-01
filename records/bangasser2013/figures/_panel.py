"""Shared reading code for the figures of bangasser2013 (Excel-style charts).

Every reading file in this directory is a small stub that names one panel, one
series and its axis labels, and calls `read_spec` here. The stubs pin this file
by its SHA-256, so a change here forces each stub to be re-checked.

Everything is found in the image:
  axes      the black spines are the longest dark vertical / horizontal lines;
            the tick marks are the short dark strokes sticking out of a spine
            (outside the plot box). The major ticks are matched, in order, to
            the printed labels given in the stub (the only paper values used);
            a linear (or log10) fit of pixel against value gives the calibration
            and its misfit (largest residual, at least half a pixel).
  curves    pixels nearest in colour to the series' colour among the panel's
            series colours (and within a tolerance); per column, the runs of
            that mask; the curve is followed from its longest-trusted column
            outward, keeping the run nearest the previous one. The value is the
            run's centre.
  markers   coloured blobs of a marker's size; the centroid is the point; error
            bars are the thin dark lines through it, their ends the last dark
            pixels (the caps) along that column.
  bars      coloured blobs standing on the x spine; the top edge is the value.

Intervals (95%): half a line thickness of placement error on the curve's centre
(the figures are rasters upsampled from about 300 dpi, so the centre of a line is
known to about a source pixel), plus half the excess of the run over the normal
line thickness where the curve is steep, plus the calibration misfit, plus one
pixel of quantisation.
"""
from itertools import combinations

import numpy as np
from scipy import ndimage as ndi


# ---------------------------------------------------------------------------- basics

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
    """The black axis lines. Returns dict with the left / right vertical spines
    (column range, row extent) and the bottom horizontal spine (row range,
    column extent). `region` = (c0, r0, c1, r1) restricts the search."""
    m = black(img, thr)
    H, W = m.shape
    c0, r0, c1, r1 = region if region else (0, 0, W, H)
    sub = m[r0:r1, c0:c1]
    h, w = sub.shape

    def longest(v, gap=bridge):
        """Longest dark run, bridging gaps of up to `gap` pixels (a curve drawn over a spine)."""
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

    def vspine(g):
        n, s = max(info[c] for c in g)
        col = [c for c in g if info[c][0] >= 0.9 * n]
        return {"c0": c0 + min(col), "c1": c0 + max(col), "r0": r0 + s, "r1": r0 + s + n}

    def hspine(g):
        n, s = max(hinfo[r] for r in g)
        row = [r for r in g if hinfo[r][0] >= 0.9 * n]
        return {"r0": r0 + min(row), "r1": r0 + max(row), "c0": c0 + s, "c1": c0 + s + n}

    return {"left": vspine(vg[0]), "right": vspine(vg[-1]) if len(vg) > 1 else None,
            "bottom": hspine(hg[-1]) if hg else None, "top": hspine(hg[0]) if len(hg) > 1 else None}


def _tick_runs(m, positions, start, step, limit):
    out = {}
    for p in positions:
        n = 0
        k = start
        while 0 <= k < limit(p) and n < 400 and m(p, k):
            n += 1
            k += step
        out[p] = n
    return out


def ticks(img, sp, which, thr=110, min_len=6):
    """Centres (pixel) and lengths of the tick marks on one spine, outside the box.
    which: 'left', 'right' (y ticks) or 'bottom' (x ticks)."""
    m = black(img, thr)
    H, W = m.shape
    if which in ("left", "right"):
        s = sp[which]
        # both y spines span the plot's height; a line crossing one spine can cut its dark run
        r_lo = min(s["r0"], sp["left"]["r0"])
        r_hi = max(s["r1"], sp["left"]["r1"])
        rows = range(max(r_lo - 6, 0), min(r_hi + 6, H))
        if which == "left":
            def mm(r, k):
                return any(m[r, k - j] for j in range(3) if k - j >= 0)
            runs = {}
            for r in rows:
                n, k = 0, s["c0"] - 1
                while k >= 0 and m[r, k]:
                    n += 1
                    k -= 1
                runs[r] = n
        else:
            runs = {}
            for r in rows:
                n, k = 0, s["c1"] + 1
                while k < W and m[r, k]:
                    n += 1
                    k += 1
                runs[r] = n
    else:
        s = sp["bottom"]
        # coloured dashes lying on the x axis can cut its dark run: scan to the image's edge
        cols = range(max(s["c0"] - 6, 0), W)
        runs = {}
        for c in cols:
            n, k = 0, s["r1"] + 1
            skip = 0
            while k < H and not m[k, c] and skip < s.get("skip", 0):
                k += 1
                skip += 1
            while k < H and m[k, c]:
                n += 1
                k += 1
            runs[c] = n
    # a tick is a short, narrow run of positions with a long-enough stroke
    good = [p for p, n in runs.items() if min_len <= n <= 300]
    out = []
    for g in _groups(good):
        if len(g) > 40:          # too wide for a tick: a label or another line
            continue
        lens = np.array([runs[p] for p in g], float)
        centre = (g[0] + g[-1]) / 2.0 + 0.5
        if which == "bottom":
            # the tick at a vertical spine is the spine's own extension: take the spine's centre
            for key in ("left", "right"):
                v = sp.get(key)
                if v is not None and g[0] - 3 <= v["c0"] <= g[-1] + 3:
                    centre = (v["c0"] + v["c1"]) / 2.0 + 0.5
        out.append((centre, float(lens.max())))
    if not out:
        return []
    longest = max(n for _, n in out)
    return [p for p, n in out if n >= 0.6 * longest]


def fit_axis(pix, labels, scale):
    """Match tick pixels to labels (same count, or the best evenly spaced subset)."""
    vals = np.array([np.log10(v) if scale == "log10" else v for v in labels], float)
    pix = sorted(pix)
    n = len(vals)
    if len(pix) < n:
        raise ValueError(f"found {len(pix)} ticks for {n} labels")
    best = None
    cands = [pix] if len(pix) == n else combinations(pix, n)
    for sub in cands:
        p = np.array(sub)
        # labels are given in pixel order (left-to-right or top-to-bottom)
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
    sp = spines(img, region, thr=spec.get("spine_thr", 110), frac=spec.get("spine_frac", 0.35),
                bridge=spec.get("bridge", 3))
    if sp["bottom"] is not None and sp["bottom"]["r0"] < 0.5 * (sp["left"]["r0"] + sp["left"]["r1"]):
        sp["bottom"] = None          # only a top frame line was found
    if sp["bottom"] is None or spec.get("x_spine_hidden"):
        # the x spine is covered by a coloured line: put it at the lowest y tick (the axis's own
        # extension past the y spine) and look for the x ticks a little below it
        yt0 = ticks(img, sp, spec["y"].get("side", "left"), min_len=spec.get("tick_min", 6))
        r = int(round(max(yt0)))
        # the axis's lower edge: where the 0 tick (left of the y spine) ends going down
        mk = black(img, spec.get("spine_thr", 110))
        cl = int(sp["left"]["c0"]) - 8
        r_end = r
        while r_end + 1 < img.shape[0] and mk[r_end + 1, cl]:
            r_end += 1
        sp["bottom"] = {"r0": r, "r1": r_end, "c0": int(sp["left"]["c0"]) - 10, "c1": img.shape[1] - 1,
                        "skip": spec.get("x_tick_skip", 30)}
    xs = spec["x"]
    ys = spec["y"]
    side = ys.get("side", "left")
    xt = ticks(img, sp, "bottom", min_len=spec.get("tick_min", 6))
    yt = ticks(img, sp, side, min_len=spec.get("tick_min", 6))
    if xs.get("drop_x"):
        xt = [p for p in xt if not any(lo <= p <= hi for lo, hi in xs["drop_x"])]
    xa = fit_axis(xt, xs["labels"], xs.get("scale", "linear"))
    ya = fit_axis(yt, ys["labels"], ys.get("scale", "linear"))
    box = (sp["left"]["c1"] + 1, min(sp["left"]["r0"], sp[side]["r0"]),
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
        rs = [(a, b) for a, b in _runs_col(mask[:, c]) if b - a >= min_run]
        runs[c] = rs
    single = [c for c, rs in runs.items() if len(rs) == 1]
    if not single:
        return {}
    # start in the longest stretch of columns with exactly one run
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
                jump = abs(cbest[0] - prev)
                if jump < 60 + 40 * miss + cbest[1]:
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
    rr0 = int(r0 - spec.get("above", 0))
    keep[max(rr0, 0):int(r1) + spec.get("below", 0), int(c0) + pad:int(c1) - pad + spec.get("right_extra", 0)] = True
    for (a, b, c, d) in spec.get("blank", []):    # regions holding labels of the same colour
        keep[b:d, a:c] = False
    m &= keep
    if spec.get("open"):
        m = ndi.binary_opening(m, iterations=spec["open"])
    ca, cb = int(c0) + pad, int(c1) - pad + spec.get("right_extra", 0)
    if spec.get("x_range"):
        # the series is visible only over this x range (elsewhere it lies under another series)
        lo_v, hi_v = spec["x_range"]
        ca = max(ca, int(to_px(xa, lo_v)))
        cb = min(cb, int(to_px(xa, hi_v)) + 1)
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
            # at the edge of the plot box (the curve starts at the spine): the nearest traced column
            cn = min(tr, key=lambda c: abs(c - ci))
            if abs(cn - ci) <= 20:
                near = [c for c in tr if abs(c - cn) <= 3]
                reach = float(abs(cn - ci))
        if not near:
            out.append({"x": float(x), "y": None,
                        "note": "no pixel of this series at this x (hidden or outside the curve)"})
            continue
        cen = float(np.mean([tr[c][0] for c in near]))
        L = float(max(tr[c][1] for c in near))
        half = 0.5 * thick + 0.5 * max(L - thick, 0.0) + ya["misfit"] + 1.0
        # x calibration error moves the column; add the curve's slope across it
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


# ---------------------------------------------------------------------------- markers

def _dark_width(dark, r, ci, reach=120):
    """Width of the dark horizontal run through column ci (+-2 px) in row r, or 0."""
    W = dark.shape[1]
    hits = [c for c in range(max(ci - 2, 0), min(ci + 3, W)) if dark[r, c]]
    if not hits:
        return 0
    a = hits[0]
    while a - 1 >= 0 and dark[r, a - 1] and ci - a < reach:
        a -= 1
    b = hits[-1]
    while b + 1 < W and dark[r, b + 1] and b - ci < reach:
        b += 1
    return b - a + 1


def _bar_end(dark, col, r_edge, direction, stem_max=14, max_gap=20, max_wide=30):
    """Walk from a marker edge along the error bar's column. The stem is a thin dark line;
    a cap is a short wide stroke at its end. A thick line (a connecting line, a curve)
    running along the column for more than `max_wide` rows blocks the walk.
    Returns (row of the bar end or None, blocked)."""
    H = dark.shape[0]
    ci = int(round(col))
    r = int(r_edge)
    last, gap, wide = None, 0, 0
    widths = {}
    while 0 <= r < H and gap <= max_gap:
        w = _dark_width(dark, r, ci)
        if w > 3 * stem_max:
            break                      # a long horizontal line (an axis): the bar ended before it
        if w == 0:
            gap += 1
        else:
            gap = 0
            last = r
            widths[r] = w
            if w > stem_max:
                wide += 1
                if wide > max_wide:
                    return None, True
            else:
                wide = 0
        r += direction
    if last is None:
        return None, False
    # the cap: the run of wide rows at the end of the bar; its middle row is the bar's end
    stems = [v for v in widths.values() if v <= stem_max]
    sw = float(np.median(stems)) if stems else 0.0
    k = last
    while k in widths and widths[k] > 1.6 * sw and abs(k - last) < 40:
        k -= direction
    return (last + k) / 2.0 if k != last else float(last), False


def _split_blobs(m, open_it):
    """Label marker blobs; a blob much larger than the typical marker (two markers touching)
    is split by eroding it until it falls apart. Returns [(rows, cols, split)]."""
    lab, n = ndi.label(m)
    blobs = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        blobs.append((rr, cc))
    if not blobs:
        return []
    areas = np.array([len(b[0]) for b in blobs])
    big = areas.max()
    typical = np.median(areas[areas >= 0.3 * big])
    out = []
    for rr, cc in blobs:
        if len(rr) < 0.3 * typical:
            continue
        if len(rr) > 1.45 * typical:
            sub = np.zeros_like(m)
            sub[rr, cc] = True
            k = 1
            parts = 1
            while k < 60:
                er = ndi.binary_erosion(sub, iterations=k)
                l2, parts = ndi.label(er)
                if parts >= 2 or not er.any():
                    break
                k += 2
            if parts >= 2:
                for j in range(1, parts + 1):
                    r2, c2 = np.where(l2 == j)
                    if len(r2) < 0.05 * len(rr):
                        continue
                    out.append((r2, c2, k))
                continue
        out.append((rr, cc, 0))
    return out


def read_markers(img, spec, at):
    cal = calibrate(img, spec)
    xa, ya = cal["x"], cal["y"]
    c0, r0, c1, r1 = cal["box"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    keep = np.zeros_like(m)
    keep[int(r0) - spec.get("above", 0):int(r1) + 2, int(c0) - spec.get("left_extra", 0):int(c1) + 2] = True
    for (a, b, c, d) in spec.get("blank", []):
        keep[b:d, a:c] = False
    m &= keep
    m = ndi.binary_closing(m, iterations=2)      # fill the anti-aliased seams of a marker
    # Markers are discs (or squares) of one size, much thicker than any line of the same colour.
    # The distance to the nearest non-marker pixel peaks at a marker's centre at about its
    # half-width R; lines and dashes never get past half their thickness. Each core where the
    # distance exceeds `core` x R is one marker (two touching markers give two cores).
    dt = ndi.distance_transform_edt(m)
    R = float(dt.max())
    if R < 3:
        return []
    core = dt >= spec.get("core", 0.6) * R
    lab, n = ndi.label(core)
    found = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        w = dt[rr, cc]
        peak = float(w.max())
        # the centre: the dt-weighted centroid of the core's top (a disc's distance map is a cone)
        top_ = w >= peak - 2.0
        r = float((rr[top_] * w[top_]).sum() / w[top_].sum()) + 0.5
        c = float((cc[top_] * w[top_]).sum() / w[top_].sum()) + 0.5
        found.append((r, c, peak, len(rr)))
    dark = black(img, spec.get("bar_thr", 120), smax=spec.get("bar_smax", 90))
    stem_max = spec.get("stem_max", 14)
    out = []
    for r, c, peak, area in found:
        # an unhidden marker reaches R; a partly hidden one less, and its centre is less certain
        hidden = max(0.0, R - peak)
        top, bot = int(round(r - R)), int(round(r + R))
        y = to_val(ya, r)
        x = to_val(xa, c)
        e = 1.5 + ya["misfit"] + hidden + spec.get("marker_err_px", 0.0)
        a1, a2 = to_val(ya, r - e), to_val(ya, r + e)
        row = {"x": x, "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [c, r],
               "note": f"marker centre (half-width {peak:.0f} of {R:.0f} px"
                       f"{', partly hidden' if hidden > 2 else ''}); "
                       f"x misfit {xa['misfit']:.1f} px, y misfit {ya['misfit']:.1f} px"}
        if spec.get("error_bars"):
            gap = spec.get("bar_gap", 20)    # a coloured line crossing the bar interrupts its dark run
            up, bl_up = _bar_end(dark, c, top - 1, -1, stem_max=stem_max, max_gap=gap)
            dn, bl_dn = _bar_end(dark, c, bot + 1, +1, stem_max=stem_max, max_gap=gap)
            got_up = up is not None and (top - up) > 6
            got_dn = dn is not None and (dn - bot) > 6
            if bl_up or bl_dn:
                row["note"] += "; a thick line runs along the bar on one side"
            if got_up or got_dn:
                if not got_up:
                    up = r - (dn - r)
                    row["note"] += "; upper bar end hidden: mirrored from the lower"
                if not got_dn:
                    dn = r + (r - up)
                    row["note"] += "; lower bar end hidden: mirrored from the upper"
                up_c, dn_c = float(up), float(dn)   # the caps' middle rows
                hi_v, lo_v = to_val(ya, up_c), to_val(ya, dn_c)
                if ya["b"] > 0:
                    hi_v, lo_v = lo_v, hi_v
                pp = (2.5 + ya["misfit"]) / abs(ya["b"])
                if ya["scale"] == "linear":
                    row.update({"bar_lo": lo_v, "bar_hi": hi_v, "bar_lo_outer": lo_v - pp, "bar_hi_outer": hi_v + pp})
                row.update({"px_lo": up_c, "px_hi": dn_c})
                row["note"] += "; error bar ends read along the marker's column"
            else:
                hi_v, lo_v = to_val(ya, top), to_val(ya, bot)
                if ya["b"] > 0:
                    hi_v, lo_v = lo_v, hi_v
                row.update({"bar_lo": lo_v, "bar_hi": hi_v, "bar_lo_outer": lo_v, "bar_hi_outer": hi_v})
                row["note"] += "; error bar hidden inside the marker: at most the marker"
        out.append(row)
    out.sort(key=lambda d: d["x"])
    return out


# ---------------------------------------------------------------------------- bars

def read_bars(img, spec, at):
    """Bars of one colour on a categorical x axis. The stub gives the printed category
    labels (spec['categories']) in left-to-right order for the bars of this colour."""
    sp = spines(img, spec.get("region"), thr=spec.get("spine_thr", 110), frac=spec.get("spine_frac", 0.35))
    ys = spec["y"]
    yt = ticks(img, sp, "left", min_len=spec.get("tick_min", 6))
    ya = fit_axis(yt, ys["labels"], ys.get("scale", "linear"))
    base = sp["bottom"]["r0"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    m[base - 1:] = False
    m[:, :sp["left"]["c1"] + 2] = False
    m = ndi.binary_opening(m, iterations=spec.get("open", 2))
    lab, n = ndi.label(m)
    bars = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if len(rr) < spec.get("min_area", 200):
            continue
        if rr.max() < base - 12:              # not standing on the axis
            continue
        width = cc.max() - cc.min() + 1
        if width < spec.get("min_width", 15):
            continue
        # top edge: the median over the bar's inner columns of the first coloured row
        inner = range(cc.min() + width // 4, cc.max() - width // 4 + 1)
        tops = []
        for c in inner:
            col = np.where(lab[:, c] == i)[0]
            if len(col):
                tops.append(col.min())
        top = float(np.median(tops))
        spread = float(np.max(tops) - np.min(tops)) if tops else 0.0
        bars.append((float(cc.mean()) + 0.5, top, spread, width))
    bars.sort()
    cats = spec["categories"]
    out = []
    if len(bars) != len(cats):
        return [{"x": float(v), "y": None, "note": f"found {len(bars)} bars for {len(cats)} categories"} for v in cats]
    for (c, top, spread, width), x in zip(bars, cats):
        e = 1.0 + 0.5 * spread + ya["misfit"] + spec.get("edge_err", 1.0)
        y = to_val(ya, top)
        a1, a2 = to_val(ya, top - e), to_val(ya, top + e)
        out.append({"x": float(x), "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [c, top],
                    "px_lo": top - e, "px_hi": top + e,
                    "note": f"bar top edge ({width} px wide); y misfit {ya['misfit']:.1f} px ({len(ya['marks'])} ticks)"})
    return out


def read_vlines(img, spec, at):
    """Dashed vertical lines, one per colour in spec['series'] (in the order of `at`):
    the x position of each, as the reading's y value (the reading's x is the label of
    the series, e.g. the parameter value the legend gives it). The dashed column is
    where the colour mask holds many short vertical runs (dashes)."""
    cal = calibrate(img, spec)
    xa = cal["x"]
    c0, r0, c1, r1 = cal["box"]
    out = []
    for x, color in zip(at, spec["series"]):
        others = [c for c in spec.get("others", ()) if tuple(c) != tuple(color)]
        m = colour_mask(img, color, others, spec.get("tol", 60))
        m[:, :int(c0) + 4] = False
        m[:, int(c1) - 4:] = False
        counts = np.zeros(m.shape[1])
        for c in range(int(c0) + 4, int(c1) - 4):
            rs = _runs_col(m[:, c])
            counts[c] = sum(1 for a, b in rs if 8 <= b - a <= 120)
        top = counts.max()
        cols = np.where(counts >= max(4, 0.5 * top))[0]
        if top < 4 or len(cols) == 0:
            out.append({"x": float(x), "y": None, "note": "dashed line not found"})
            continue
        g = max(_groups(cols, gap=2), key=len)
        w = counts[g]
        cen = float((g * w).sum() / w.sum()) + 0.5
        half = 0.5 * (g[-1] - g[0] + 1) + xa["misfit"] + 1.0
        mid_row = float(np.mean([np.mean([(a + b) / 2 for a, b in _runs_col(m[:, int(c)])]) for c in g]))
        v = to_val(xa, cen)
        lo, hi = sorted([to_val(xa, cen - half), to_val(xa, cen + half)])
        out.append({"x": float(x), "y": v, "lo": lo, "hi": hi, "px": [cen, mid_row],
                    "note": f"dashed line {g[-1] - g[0] + 1} px wide, {int(top)} dashes; x misfit {xa['misfit']:.1f} px "
                            f"({len(xa['marks'])} ticks)"})
    return out


def read_hlines(img, spec, at):
    """A dashed horizontal line of one colour: its height on the y axis, returned as the
    reading's y at x = at[0] (the label of the series). The dashed rows are where the
    colour mask holds many short horizontal runs (dashes) across the plot."""
    cal = calibrate(img, spec)
    ya = cal["y"]
    c0, r0, c1, r1 = cal["box"]
    m = colour_mask(img, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    m[:, :int(c0) + 4] = False
    m[:, int(c1) - 4:] = False
    counts = np.zeros(m.shape[0])
    for r in range(int(r0), int(r1)):
        rs = _runs_col(m[r, :])
        counts[r] = sum(1 for a, b in rs if 15 <= b - a <= 200)
    top = counts.max()
    rows = np.where(counts >= max(4, 0.5 * top))[0]
    if top < 4 or len(rows) == 0:
        return [{"x": float(at[0]), "y": None, "note": "dashed line not found"}]
    g = max(_groups(rows, gap=2), key=len)
    w = counts[g]
    cen = float((g * w).sum() / w.sum()) + 0.5
    half = 0.5 * (g[-1] - g[0] + 1) + ya["misfit"] + 1.0
    on = [c for c in range(int(c0) + 4, int(c1) - 4) if m[int(cen), c]]
    col = float(np.median(on)) if on else float(c0 + c1) / 2
    v = to_val(ya, cen)
    lo, hi = sorted([to_val(ya, cen - half), to_val(ya, cen + half)])
    return [{"x": float(at[0]), "y": v, "lo": lo, "hi": hi, "px": [col, cen], "px_lo": cen - half, "px_hi": cen + half,
             "note": f"dashed line {g[-1] - g[0] + 1} px thick, {int(top)} dashes; y misfit {ya['misfit']:.1f} px "
                     f"({len(ya['marks'])} ticks)"}]


def read_spec(image, at, spec):
    if spec.get("kind") == "hlines":
        return read_hlines(image, spec, at)
    if spec.get("kind") == "vlines":
        return read_vlines(image, spec, at)
    kind = spec.get("kind", "curve")
    if kind == "curve":
        return read_curve(image, spec, at)
    if kind == "markers":
        return read_markers(image, spec, at)
    if kind == "bars":
        return read_bars(image, spec, at)
    raise ValueError(kind)
