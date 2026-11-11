"""Shared reading code for the wave intensity figures of davies2006 (Fig. 3, PDF p. 5; Fig. 5, PDF p. 7).

Each figure is one low-resolution raster image in the PDF (rendered at 1200 dpi, one image pixel is a
block of about 8 x 8 page pixels, `blk`, measured as the width of the axis lines). One crop holds the
whole figure: the WI+ panel (top), the WI- panel (middle) and the pressure and velocity panel
(bottom). Everything is found in the image; the only numbers typed in are the printed tick labels.

Calibration
  y axes    the vertical axis lines: columns whose longest run of ink (< 190) is longer than 12% of the
            crop height. Each run is one panel's y axis; the left ones are numbered top to bottom
            (0 = WI+, 1 = WI-, 2 = velocity), and the right one is the pressure axis of the bottom panel.
  y ticks   rows where the strip from 1 to 4 `blk` inside the axis line has mean grey below 200
            (ticks are grey ~100-160; the dashed onset lines are lighter, ~215, and are not taken),
            grouped; matched top to bottom to the printed labels (the evenly spaced subset with the
            smallest straight-line misfit; one label may be unmatched); the largest misfit is reported
            and added to every interval.
  x axis    only the bottom panel has one (0 to 1000 ms): the long horizontal line in the lower part
            of the crop, ticks pointing up into the panel, matched left to right to the labels. The
            WI panels have no x axis; they are read on the bottom panel's time axis. This is the one
            assumption of the reading: the three panels share their time scale, which the figure
            itself shows, because each grey dashed onset line is one straight vertical line through
            all three panels, meeting a wave's onset in the WI panels and the matching inflexion of
            pressure and velocity below.
Curves
  WI        black ink (< 120) in the panel; the trace is every connected component that reaches
            within 3 blk of the zero row and spans more than 3 blk (the line may break where it
            touches zero; wave labels, circles and text stand apart from it). The grey zero line
            (~160) is not ink at this threshold. Acceleration waves are filled black under the trace,
            so for WI+ ("upper") the trace is the topmost ink of the component in each column, for
            WI- ("lower") the bottommost; the line's centre is half a line width inside that edge (the
            width is the median thickness of the edge run where the trace is unfilled).
  pressure  the solid line: at ink < 180 the dashed line falls apart into short dashes, while the
            solid line is one long component, or a few where it is steep (its anti-aliased pixels
            are lighter there). The component of widest span is taken, and the components spanning
            at least 4% of the panel whose end meets its end (within 3 blk in columns and 8 blk in
            rows) are chained on. The chain is traced column by column from the left (the run
            touching the previous one, else the run nearest a straight-line prediction).
  velocity  the dashed line: the other ink (< 200) components (the dashes), followed from dash to dash; across
            a gap of at most `max_gap` columns its centre is interpolated between the facing dash ends;
            where it runs under the solid line it is somewhere in the solid line's run ("fused").
            Curve labels ("velocity", "pressure") are blanked by `mask` boxes (fractions of the panel).
  peaks     (WI readings with `peaks`): the local maxima of WI+ (minima of WI-) of the traced centre
            line whose prominence exceeds `peaks` (axis units); x is the time of the extremum. An
            extremum within its interval of the panel's frame may be clipped and is not reported.
Fig. 4 (PDF p. 6) is a blurred scan rather than a block raster, with boxed panels (WI+ and WI- in
one panel with ticks on both frames, pressure and velocity below): `blk` is then the frame line
width (16 px), a wide "axis" (a tall filled wave near the left edge) is not taken as an axis, the
pressure axis is the right frame beside the bottom panel, the panels stop 6 blk inside the right
frame, and the bottom panel stops one blk above the x ticks (their height measured on the image).
Intervals (95%): the edge or run centre +- (one image pixel `blk` + 2 px); a fused run spans the whole
run; a dash gap +- max(blk, a quarter of the rise across the gap); plus the y misfit and the x misfit
times the local slope. A curve touching the panel's top or bottom edge is not read there.
The tracing functions for the solid and dashed lines follow the shared reading code of the
mynard2014 record (figures/_wave.py there), simplified.
"""

import itertools

import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    r = _runs(v)
    return max(r, key=lambda x: x[1] - x[0]) if r else (0, 0)


def _groups(idx):
    out, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            out.append(cur)
            cur = []
        cur.append(int(i))
    if cur:
        out.append(cur)
    return out


def _match(cands, labels, what):
    best = None
    label_sets = [list(labels)]
    if len(labels) >= 4:
        label_sets += [list(labels[:i]) + list(labels[i + 1:]) for i in range(len(labels))]
    for k, labs in enumerate(label_sets):
        n = len(labs)
        if len(cands) < n:
            continue
        v = np.array(labs, float)
        for sub in itertools.combinations(cands, n):
            p = np.array(sub, float)
            b, a = np.polyfit(p, v, 1)
            mis = float(np.max(np.abs((v - a) / b - p)))
            if mis <= 12.0 and (best is None or (k > 0, mis) < (best[3] > 0, best[2])):
                best = (a, b, mis, k)
    if best is None:
        raise ValueError(f"{what}: no evenly spaced set of ticks among {cands} for {labels}")
    return best[:3]


def find_axes(g):
    H, W = g.shape
    ink = g < 190
    segs = []
    for j in range(W):
        for a, b in _runs(ink[:, j]):
            if b - a > 0.12 * H:
                segs.append((j, a, b))
    # group adjacent columns whose runs overlap
    axes = []
    for j, a, b in segs:
        for ax in axes:
            if j - ax["c1"] <= 1 and a < ax["r1"] and b > ax["r0"]:
                ax["c1"] = j
                ax["r0"], ax["r1"] = min(ax["r0"], a), max(ax["r1"], b)
                break
        else:
            axes.append({"c0": j, "c1": j, "r0": a, "r1": b})
    # axis lines are thin: drop wide "segments" (a tall filled wave near the left edge, Fig. 4)
    wmin = min(ax["c1"] - ax["c0"] + 1 for ax in axes)
    axes = [ax for ax in axes if ax["c1"] - ax["c0"] + 1 <= 2 * wmin]
    left = sorted([ax for ax in axes if ax["c0"] < 0.2 * W], key=lambda ax: ax["r0"])
    right = [ax for ax in axes if ax["c0"] > 0.8 * W]
    blk = int(np.median([ax["c1"] - ax["c0"] + 1 for ax in left]))
    # x axis: the longest horizontal ink run in the lower fifth
    best = None
    for i in range(int(0.8 * H), H):
        a, b = _longest(g[i] < 190)
        if best is None or b - a > best[2] - best[1]:
            best = (i, a, b)
    rows = [i for i in range(int(0.8 * H), H) if (lambda r: r[1] - r[0])(_longest(g[i] < 190)) > 0.9 * (best[2] - best[1])]
    xg = _groups(rows)[0]
    # a wavy axis line (Fig. 4 is a scan) runs over a few rows: its extent is the longest run of
    # columns inked in any row of a band around the core rows
    band = g[max(xg[0] - 2 * blk, 0): xg[-1] + 2 * blk + 1].min(axis=0) < 190
    a, b = _longest(band)
    best = (best[0], a, b)
    # a blurred axis line (Fig. 4) has dark rows just above its core: they belong to it
    top = xg[0]
    while top > 0 and g[top - 1, best[1]:best[2]].mean() < 200:
        top -= 1
    xg = [top] + list(xg)
    return {"left": left, "right": right, "blk": blk, "xr0": xg[0], "xr1": xg[-1], "xc0": best[1], "xc1": best[2]}


def calibrate(g, spec):
    A = find_axes(g)
    blk = A["blk"]
    # the strip searched for ticks, in px from the axis line (Fig. 4's ticks are shorter than 4 blk)
    t0, t1 = spec.get("ytick", (blk, 4 * blk))
    if spec.get("axis", "left") == "left":
        ax = A["left"][spec["panel"]]
        strip = g[:, ax["c1"] + t0: ax["c1"] + t1].mean(axis=1)
    else:
        # the right axis line beside the panel (Fig. 4 has a boxed WI panel above the P/U panel)
        pl = A["left"][spec["panel"]]
        ax = max(A["right"], key=lambda r: min(r["r1"], pl["r1"]) - max(r["r0"], pl["r0"]))
        strip = g[:, ax["c0"] - t1: ax["c0"] - t0].mean(axis=1)
    idx = [i for i in range(max(ax["r0"] - blk, 0), ax["r1"] + blk) if strip[i] < 200]
    yc = [(gg[0] + gg[-1]) / 2.0 for gg in _groups(idx) if len(gg) <= 3 * blk]
    ya, yb, ym = _match(yc, spec["y"], "y axis")
    u0, u1 = spec.get("xtick", (blk, 4 * blk))
    xs = g[A["xr0"] - u1: A["xr0"] - u0, :].mean(axis=0)
    idx = [j for j in range(A["xc0"], A["xc1"] + 1) if xs[j] < 200]
    xc = [(gg[0] + gg[-1]) / 2.0 for gg in _groups(idx) if len(gg) <= 3 * blk]
    xa, xb, xm = _match(xc, spec["x"], "x axis")
    # height of the x ticks (standing up from the axis line): the ink run above the line
    hs = []
    for c in xc:
        h, r = 0, A["xr0"] - 1
        while r > 0 and g[r, int(round(c))] < 200:
            h, r = h + 1, r - 1
        hs.append(h)
    return {"A": A, "ax": ax, "blk": blk, "x": (xa, xb, xm), "y": (ya, yb, ym), "xtick_h": int(np.median(hs))}


def panel_box(cal, spec, H, W):
    A, blk = cal["A"], cal["blk"]
    pax = A["left"][spec["panel"]]
    r0, r1 = pax["r0"], pax["r1"]
    ext = 3 * blk
    c0 = pax["c1"] + 6 * blk
    c1 = (A["right"][0]["c0"] - 6 * blk) if (spec["panel"] == len(A["left"]) - 1 and A["right"]) else A["xc1"]
    for r in A["right"]:
        c1 = min(c1, r["c0"] - 6 * blk)  # inside a boxed panel's right frame and its ticks (Fig. 4)
    if spec["kind"] == "upper":
        r1 += ext
    elif spec["kind"] == "lower":
        r0 -= ext
    else:
        r1 = min(r1, A["xr0"] - blk)
    return int(r0), int(r1), int(c0), int(min(c1, W))


def _apply_mask(m, box, spec):
    r0, r1, c0, c1 = box
    ph, pw = r1 - r0, c1 - c0
    for f0, g0, f1, g1 in spec.get("mask", []):
        m[int(r0 + g0 * ph):int(r0 + g1 * ph), int(c0 + f0 * pw):int(c0 + f1 * pw)] = False
    return m


# ---- WI traces --------------------------------------------------------------------------------
def wi_centres(g, cal, spec):
    H, W = g.shape
    box = panel_box(cal, spec, H, W)
    r0, r1, c0, c1 = box
    ink = np.zeros(g.shape, bool)
    ink[r0:r1, c0:c1] = g[r0:r1, c0:c1] < 120
    ink = _apply_mask(ink, box, spec)
    lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
    sl = ndimage.find_objects(lab)
    # the trace returns to zero between waves and may break there: every component that comes
    # within 3 blk of the zero row and spans more than 3 blk is part of it (labels never come
    # near the zero line)
    ya, yb, _ = cal["y"]
    z = (0.0 - ya) / yb
    keep = np.zeros(n + 1, bool)
    for i, s in enumerate(sl, start=1):
        if s[1].stop - s[1].start > 3 * cal["blk"] and s[0].start - 3 * cal["blk"] <= z <= s[0].stop + 3 * cal["blk"]:
            keep[i] = True
    comp = keep[lab]
    upper = spec["kind"] == "upper"
    edges, thick = {}, []
    for c in range(c0, c1):
        rs = _runs(comp[:, c])
        if not rs:
            continue
        run = rs[0] if upper else rs[-1]
        edges[c] = run[0] if upper else run[1] - 1
        if run[1] - run[0] < 5 * cal["blk"]:
            thick.append(run[1] - run[0])
    w = float(np.median(thick)) if thick else float(cal["blk"])
    cen = {c: (e + w / 2.0 - 0.5 if upper else e - w / 2.0 + 0.5) for c, e in edges.items()}
    return cen, w, box


def _slope(cen, c):
    ks = [k for k in range(c - 8, c + 9) if k in cen]
    return abs(np.polyfit(ks, [cen[k] for k in ks], 1)[0]) if len(ks) >= 3 else 0.0


def _value(cal, spec, row):
    ya, yb, _ = cal["y"]
    return (ya + yb * row) * spec.get("mult", 1.0)


def read_wi(image, at, spec):
    g = image[..., :3].astype(float).mean(axis=2)
    cal = calibrate(g, spec)
    cen, w, box = wi_centres(g, cal, spec)
    xa, xb, xm = cal["x"]
    ym = cal["y"][2]
    blk = cal["blk"]
    out = []
    if spec.get("peaks"):
        cols = sorted(cen)
        vals = np.array([_value(cal, spec, cen[c]) for c in cols]) / spec.get("mult", 1.0)
        sig = vals if spec["kind"] == "upper" else -vals
        pk, _ = find_peaks(sig, prominence=spec["peaks"])
        for i in pk:
            c = cols[i]
            row = cen[c]
            half = blk + 2.0 + ym
            if row - half < box[0] or row + half > box[1]:
                continue  # an extremum at the panel frame may be clipped there: not reported
            v, v1, v2 = _value(cal, spec, row), _value(cal, spec, row - half), _value(cal, spec, row + half)
            out.append({"x": float(xa + xb * c), "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                        "px": [float(c), float(row)], "px_lo": float(row - half), "px_hi": float(row + half),
                        "note": f"extremum of the traced line; time +- {abs(xb) * (blk + xm):.1f} ms; line {w:.0f} px; "
                                f"misfit x {xm:.1f} px, y {ym:.1f} px"})
        return out
    for x in at:
        c = int(round((x - xa) / xb))
        if c not in cen:
            out.append({"x": x, "y": None, "note": "no trace in this column (outside the plotted interval)"})
            continue
        row = cen[c]
        s = _slope(cen, c)
        half = blk + 2.0 + ym + xm * s
        if row - half < box[0] or row + half > box[1]:
            out.append({"x": x, "y": None, "note": "the trace runs into the panel edge here"})
            continue
        v, v1, v2 = _value(cal, spec, row), _value(cal, spec, row - half), _value(cal, spec, row + half)
        out.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(row)], "px_lo": float(row - half), "px_hi": float(row + half),
                    "note": f"{spec['kind']} edge; line {w:.0f} px; misfit x {xm:.1f} px, y {ym:.1f} px"})
    return out


# ---- pressure (solid) and velocity (dashed) ----------------------------------------------------
def _mid(r):
    return (r[0] + r[1] - 1) / 2.0


def _nearest(runs, pred):
    best, bd = None, None
    for a, b in runs:
        d = 0.0 if a <= pred <= b - 1 else min(abs(pred - a), abs(pred - (b - 1)))
        if bd is None or d < bd:
            best, bd = (a, b), d
    return best, bd


def _predict(hist, col):
    if not hist:
        return None
    pts = hist[-12:]
    if len(pts) < 3:
        return pts[-1][1]
    c = np.array([p[0] for p in pts], float)
    y = np.array([p[1] for p in pts], float)
    k, m = np.polyfit(c, y, 1)
    return k * col + m


def trace_line(mask, c0, c1, tol=40.0):
    out, hist, prev, lost = {}, [], None, 0
    for c in range(c0, c1):
        runs = _runs(mask[:, c])
        pred = _predict(hist, c)
        if prev is None and pred is None:
            if not runs:
                continue
            run = max(runs, key=lambda r: r[1] - r[0])
        else:
            touch = [r for r in runs if prev is not None and r[0] <= prev[1] and r[1] >= prev[0]]
            if len(touch) == 1:
                run = touch[0]
            elif touch:
                run = _nearest(touch, pred)[0]
            else:
                run, d = _nearest(runs, pred) if runs else (None, None)
                if run is not None and d > tol + 6.0 * lost:
                    run = None
        if run is None:
            lost += 1
            prev = None
            out[c] = (pred, "lost")
            continue
        lost = 0
        prev = run
        out[c] = (run, "line")
        hist.append((c, _mid(run)))
    return out


def pu_masks(g, cal, spec):
    H, W = g.shape
    box = panel_box(cal, {**spec, "panel": len(cal["A"]["left"]) - 1}, H, W)
    r0, r1, c0, c1 = box
    r0 -= cal["blk"] // 2  # the pressure maximum reaches the top tick (the panel title is just above)
    r1 = min(r1, cal["A"]["xr0"] - cal["xtick_h"] - cal["blk"])  # above the x axis ticks
    box = (r0, r1, c0, c1)
    ink = np.zeros(g.shape, bool)
    ink[r0:r1, c0:c1] = g[r0:r1, c0:c1] < 200
    ink = _apply_mask(ink, box, spec)
    # the grey dashed onset lines are vertical: columns where light grey ink (150-240) covers more
    # than a quarter of the panel height; their light ink is dropped (the curves are darker there,
    # and a curve's pixels lost where it crosses one are bridged as a dash gap)
    core = ink & (g < 180)  # before the onset lines are dropped: the solid line stays whole
    grey = (g[r0:r1, c0:c1] >= 150) & (g[r0:r1, c0:c1] < 240)
    vcols = np.flatnonzero(grey.sum(axis=0) > 0.25 * (r1 - r0)) + c0
    blk = cal["blk"]
    for c in vcols:
        sub = ink[r0:r1, max(c - blk, c0):c + blk + 1]
        sub &= ~(g[r0:r1, max(c - blk, c0):c + blk + 1] >= 150)
    lab, n = ndimage.label(core, structure=np.ones((3, 3)))
    sl = ndimage.find_objects(lab)
    # the solid line may break where it is steep (light anti-aliased pixels): start from the
    # component with the widest span and chain on the components (spanning at least 4% of the
    # panel) whose end meets the chain's end within 3 blk in columns and 8 blk in rows
    span = {k: (s[1].start, s[1].stop) for k, s in enumerate(sl, start=1) if s[1].stop - s[1].start >= 0.04 * (c1 - c0)}

    def ends(k):
        rows, cols = np.nonzero(lab[sl[k - 1]] == k)
        rows, cols = rows + sl[k - 1][0].start, cols + sl[k - 1][1].start
        lo, hi = cols.min(), cols.max()
        return (lo, float(rows[cols <= lo + 2].mean())), (hi, float(rows[cols >= hi - 2].mean()))

    k0 = max(span, key=lambda k: span[k][1] - span[k][0])
    chain = [k0]
    E = {k: ends(k) for k in span}
    (lc, lr), (rc, rr) = E[k0]
    grown = True
    while grown:
        grown = False
        for k in sorted(span):
            if k in chain:
                continue
            (a, ar), (b, br) = E[k]
            if abs(a - rc) <= 3 * blk and abs(ar - rr) <= 8 * blk:
                chain.append(k)
                rc, rr = b, br
                grown = True
            elif abs(b - lc) <= 3 * blk and abs(br - lr) <= 8 * blk:
                chain.append(k)
                lc, lr = a, ar
                grown = True
    solid = np.isin(lab, chain)
    return {"black": ink, "solid": solid, "box": box, "c0": c0, "c1": c1}


def refine(m, solid_tr, min_dash, gap=3):
    traced = np.zeros_like(m["black"])
    for c, e in solid_tr.items():
        if e[1] == "line":
            traced[e[0][0]:e[0][1], c] = True
    rest = m["black"] & ~ndimage.binary_dilation(traced, iterations=gap)
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    sizes = ndimage.sum(rest, lab, index=np.arange(1, n + 1)) if n else np.array([])
    m["dash"] = np.concatenate([[False], sizes >= min_dash])[lab] & rest
    m["solid"] = traced
    return m


def _dash_components(m, reach):
    dash = m["dash"]
    lab, n = ndimage.label(dash, structure=np.ones((3, 3)))
    dsol = ndimage.distance_transform_edt(~m["solid"]) if m["solid"].any() else np.full(dash.shape, 1e9)
    comps = {}
    for k, s in enumerate(ndimage.find_objects(lab), start=1):
        rows, cols = np.nonzero(lab[s] == k)
        rows, cols = rows + s[0].start, cols + s[1].start
        cmin, cmax = int(cols.min()), int(cols.max())
        lsel, rsel = cols <= cmin + 2, cols >= cmax - 2
        comps[k] = {"cmin": cmin, "cmax": cmax, "lrow": float(rows[lsel].mean()), "rrow": float(rows[rsel].mean()),
                    "ltouch": bool(dsol[rows[lsel], cols[lsel]].min() <= reach),
                    "rtouch": bool(dsol[rows[rsel], cols[rsel]].min() <= reach)}
    return lab, comps


def trace_dashed(m, solid_tr, max_gap, reach=12.0, horizon=400):
    lab, comps = _dash_components(m, reach)
    c0, c1 = m["c0"], m["c1"]
    out, hist, last = {}, [], None
    for c in range(c0, c1):
        pred = _predict(hist, c)
        col = lab[:, c]
        runs = [(a, b, int(col[a])) for a, b in _runs(col > 0) if b - a >= 3]
        emerging = c - 1 in out and out[c - 1][1] in ("fused", "lost")
        if runs:
            s = solid_tr.get(c)
            if emerging and s is not None and s[1] == "line":
                (a, b), _ = _nearest([(r[0], r[1]) for r in runs], _mid(s[0]))
                k = next(r[2] for r in runs if r[0] == a)
                ok = True
            elif pred is None or emerging:
                cand = [r for r in runs if last is None or r[2] == last] or runs
                a, b, k = max(cand, key=lambda r: r[1] - r[0])
                ok = True
            else:
                (a, b), d = _nearest([(r[0], r[1]) for r in runs], pred)
                k = next(r[2] for r in runs if r[0] == a)
                ok = d <= 60 or k == last
            if ok:
                out[c] = ((a, b), "line")
                hist.append((c, _mid((a, b))))
                last = k
                continue
        L = comps.get(last)
        ahead = [kk for kk, v in comps.items() if c < v["cmin"] <= c + horizon]
        if L is not None and ahead:
            R = min(ahead, key=lambda kk: np.hypot(comps[kk]["cmin"] - L["cmax"], comps[kk]["lrow"] - L["rrow"]))
            gl = comps[R]["cmin"] - L["cmax"]
            if gl <= max_gap and np.hypot(gl, comps[R]["lrow"] - L["rrow"]) <= 1.5 * max_gap:
                yl, yr = L["rrow"], comps[R]["lrow"]
                out[c] = (yl + (yr - yl) * (c - L["cmax"]) / gl, "gap", abs(yr - yl))
                continue
        touching = [kk for kk in ahead if comps[kk]["ltouch"]]
        s = solid_tr.get(c)
        left_ok = L is None or L["rtouch"]
        right_ok = (not ahead) or bool(touching)
        if s is not None and s[1] == "line" and left_ok and right_ok:
            bl = [r for r in _runs(m["black"][:, c]) if r[0] <= s[0][1] + reach and r[1] >= s[0][0] - reach]
            bl = bl or [s[0]]
            out[c] = ((min(r[0] for r in bl), max(r[1] for r in bl)), "fused")
            continue
        out[c] = (pred, "lost")
    return out


def read_pu(image, at, spec):
    g = image[..., :3].astype(float).mean(axis=2)
    cal = calibrate(g, spec)
    blk = cal["blk"]
    m = pu_masks(g, cal, spec)
    solid_tr = trace_line(m["solid"], m["c0"], m["c1"])
    if spec["kind"] == "solid":
        tr = solid_tr
    else:
        m = refine(m, solid_tr, spec.get("min_dash", 4 * blk))
        tr = trace_dashed(m, solid_tr, spec.get("max_gap", 6 * blk), spec.get("reach", 3.0 * blk))
    cen = {}
    for c, e in tr.items():
        if e[1] in ("line", "fused"):
            cen[c] = _mid(e[0])
        elif e[1] == "gap":
            cen[c] = float(e[0])
    xa, xb, xm = cal["x"]
    ym = cal["y"][2]
    r0, r1 = m["box"][0], m["box"][1]
    out = []
    for x in at:
        c = int(round((x - xa) / xb))
        e = tr.get(c)
        if e is not None and e[1] == "lost":
            # a short break of the line (lighter pixels where it is steep): bridged between the
            # traced columns on either side when they are at most 8 blk apart
            ks = sorted(cen)
            left = [k for k in ks if k < c]
            right = [k for k in ks if k > c]
            if left and right and right[0] - left[-1] <= 8 * blk:
                cl, cr = left[-1], right[0]
                yc = cen[cl] + (cen[cr] - cen[cl]) * (c - cl) / (cr - cl)
                e = (yc, "gap", abs(cen[cr] - cen[cl]))
        if e is None or e[1] == "lost" or e[0] is None:
            out.append({"x": x, "y": None, "note": "curve not found here (outside the trace or lost)"})
            continue
        s = _slope(cen, c)
        state = e[1]
        if state == "gap":
            yc = float(e[0])
            half = max(float(blk), 0.25 * e[2])
            lo, hi = yc - half, yc + half
        else:
            a, b = e[0][0], e[0][1] - 1
            if a <= r0 + 2 or b >= r1 - 2:
                out.append({"x": x, "y": None, "note": f"{state}: the line runs into the panel edge here"})
                continue
            if state == "fused":
                lo, hi = float(a), float(b)
            else:
                yc = (a + b) / 2.0
                lo, hi = yc - blk / 2.0 - 2.0, yc + blk / 2.0 + 2.0
        yc = (lo + hi) / 2.0
        pad = ym + xm * s + blk / 2.0
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = _value(cal, spec, yc), _value(cal, spec, lo), _value(cal, spec, hi)
        out.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; misfit x {xm:.1f} px, y {ym:.1f} px"})
    return out
