"""Shared reading code for the impedance figures of westerhof1971 (Figs. 2-5, pp. 3-5).

Each figure has a modulus panel (|Z| against FREQ (HZ)) and, below it, a phase panel that has no
frequency axis of its own: it shares the modulus panel's. A phase crop therefore includes the
modulus panel's frequency axis, its ticks and labels, and the phase panel under it.

Everything is found in the image:
- the scan is slightly rotated (up to about 1 degree). The tilt is measured on the frequency axis
  line, and positions are taken in a frame (u, v) rotated with it, so u runs along the frequency
  axis and v along the ordinate;
- the frequency axis ticks are the short stubs under the axis line, matched to the printed labels
  0, 2, ..., 14; the ordinate ticks are the short stubs left of the ordinate line, matched to the
  printed labels (the labelled ones and the unlabelled ones between them, evenly spaced);
- a straight line is fitted through each axis' ticks; its worst misfit enters every interval
  (the axes are hand-drawn: tick spacings vary by a few per cent);
- the drawn line is the connected ink of widest extent in the plot; it is read in the columns
  where it runs alone, and interpolated across the columns where a symbol touches it;
- dots (Figs. 2-3) are blobs left by an opening wider than the line; rings (Figs. 4-5) are found
  by an annulus template whose size is measured on the clean rings; crosses by their shape.
The only numbers typed in are the axis labels and, per panel, boxes around the panel's text
(axis title, unit, legend words) which is not data.
"""

import itertools
import math

import numpy as np
from scipy import ndimage


# ------------------------------------------------------------------ basics

def ink_of(image):
    g = image[..., :3].astype(float).mean(axis=2)
    paper, darkest = np.percentile(g, 99), np.percentile(g, 0.5)
    return g < (paper + darkest) / 2


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _line_angle(rr, cc, max_deg=2.5, step=0.01):
    """Angle (radians, row increasing with column) and offset of the strongest near-horizontal line
    through the points (rr, cc): the projection r - c tan(a) with the sharpest peak."""
    best = None
    for deg in np.arange(-max_deg, max_deg + step / 2, step):
        t = math.tan(math.radians(deg))
        proj = np.round(rr - cc * t).astype(int)
        lo = proj.min()
        h = np.bincount(proj - lo)
        k = int(np.argmax(h))
        if best is None or h[k] > best[0]:
            best = (h[k], math.radians(deg), k + lo)
    return best[1], best[2]


def _regular(cands, n):
    """The n candidates, in order, whose spacing is most even."""
    cands = sorted(cands)
    if len(cands) < n:
        return None
    best = None
    for sub in itertools.combinations(cands, n):
        d = np.diff(sub)
        score = float(np.ptp(d)) / float(np.mean(d))
        if best is None or score < best[0]:
            best = (score, list(sub))
    return best[1]


class Frame:
    """Rotated pixel frame: u along the frequency axis, v across it (down)."""

    def __init__(self, theta):
        self.c, self.s = math.cos(theta), math.sin(theta)

    def uv(self, col, row):
        return col * self.c + row * self.s, -col * self.s + row * self.c

    def cr(self, u, v):
        return u * self.c - v * self.s, u * self.s + v * self.c


def _fit(pairs):
    p = np.array([a for a, _ in pairs], float)
    v = np.array([b for _, b in pairs], float)
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs((v - a) / b - p)))
    return a, b, max(misfit, 0.5)


# ------------------------------------------------------------------ calibration

def calibrate(ink, x_labels, y_labels, phase, zero_at_axes=False):
    """Find the frequency axis, its ticks, the ordinate line and its ticks.

    phase: the ordinate line is the phase panel's, below the frequency axis; otherwise the
    modulus panel's, above it."""
    H, W = ink.shape
    # frequency axis: the strongest near-horizontal line in the crop
    rr, cc = np.nonzero(ink)
    if len(rr) > 400_000:
        pick = np.random.default_rng(0).choice(len(rr), 400_000, replace=False)
        rr, cc = rr[pick], cc[pick]
    theta, off = _line_angle(rr, cc)
    fr = Frame(theta)
    t = math.tan(theta)
    cols = np.arange(W)
    axis_row = off + cols * t
    # axis thickness and extent: ink in a band around the line
    band = np.zeros(W, int)
    on = np.zeros(W, bool)
    for c in range(W):
        r0 = int(round(axis_row[c]))
        if 0 <= r0 < H:
            seg = ink[max(r0 - 15, 0): r0 + 16, c]
            on[c] = seg[12:19].any() if len(seg) >= 19 else False
            band[c] = seg.sum()
    longest = max(b - a for a, b in _runs(on))
    pieces = [r for r in _runs(on) if r[1] - r[0] >= 0.2 * longest]  # the axis may be drawn in pieces
    xrun = (min(a for a, _ in pieces), max(b for _, b in pieces))
    half = max(float(np.median(band[xrun[0]:xrun[1]][on[xrun[0]:xrun[1]]])) / 2.0, 2.0)
    # refine: a straight line fitted through the centres of the axis' runs, column by column
    pc, pr = [], []
    for c in range(xrun[0], xrun[1], 2):
        r0 = int(round(axis_row[c]))
        seg = ink[max(r0 - 15, 0): r0 + 16, c]
        rs = [(a + b - 1) / 2.0 + max(r0 - 15, 0) for a, b in _runs(seg) if b - a <= 3 * half + 2]
        if len(rs) == 1:
            pc.append(c)
            pr.append(rs[0])
    pc, pr = np.array(pc, float), np.array(pr, float)
    for _ in range(3):
        sl, ic = np.polyfit(pc, pr, 1)
        keep = np.abs(pr - (ic + sl * pc)) <= 2.0
        pc, pr = pc[keep], pr[keep]
    theta, off = math.atan(sl), ic + 0.5
    fr = Frame(theta)
    t = math.tan(theta)
    axis_row = off + cols * t
    # x ticks: short stubs below the axis line
    probe_lo, probe_hi = int(half + 4), int(half + 4 + 2.0 * half)
    stub = np.zeros(W, bool)
    for c in range(xrun[0], xrun[1]):
        r0 = axis_row[c]
        rows = (r0 + np.arange(probe_lo, probe_hi)).round().astype(int)
        rows = rows[(rows >= 0) & (rows < H)]
        stub[c] = len(rows) > 0 and ink[rows, c].all()
    xt = []
    for a, b in _runs(stub):
        if b - a <= 6 * half:
            cc0 = (a + b - 1) / 2.0
            xt.append(fr.uv(cc0, off + cc0 * t)[0])
    xs = _regular(xt, len(x_labels))
    if xs is None:
        raise RuntimeError(f"found {len(xt)} frequency ticks, need {len(x_labels)}")
    xa, xb, xmis = _fit(list(zip(xs, x_labels)))
    v_axis = fr.uv(0, off)[1]

    # ordinate line: strongest near-vertical line, perpendicular to the frequency axis, on the
    # chosen side of the frequency axis
    U, V = _uv_grid(fr, H, W)
    region = (V > v_axis + 3 * half) if phase else (V < v_axis - 3 * half)
    if phase:
        # start the phase panel below the frequency labels: the first blank band of rows
        rows_ink = (ink & region).any(axis=1)
        start = None
        r = int(off + 3 * half) + 1
        seen = False
        gap = 0
        while r < H:
            if rows_ink[r]:
                seen = True
                gap = 0
            elif seen:
                gap += 1
                if gap >= int(8 * half):
                    start = r
                    break
            r += 1
        if start is None:
            raise RuntimeError("no blank band below the frequency labels")
        region = V > fr.uv(0, start)[1]
    m = ink & region & (U < np.percentile(U, 40))
    uu = np.round(U[m]).astype(int)
    h = np.bincount(uu - uu.min())
    u_y = float(np.argmax(h) + uu.min())
    # the ordinate line's run along v
    sel = m & (np.abs(U - u_y) <= 2 * half + 2)
    vv = np.sort(V[sel])
    vr = _runs(np.isin(np.arange(int(vv.min()), int(vv.max()) + 1), np.round(vv).astype(int)))
    v0, v1 = max(vr, key=lambda r: r[1] - r[0])
    v0 += int(vv.min())
    v1 += int(vv.min())
    # y ticks: stubs left of the ordinate line
    ycands = []
    du = np.arange(int(half + 4), int(half + 4 + 2.0 * half))
    vs = np.arange(v0 - 4 * half, v1 + 4 * half)
    hit = np.zeros(len(vs), bool)
    for i, v in enumerate(vs):
        cs, rs = fr.cr(u_y - du, np.full(len(du), v))
        cs, rs = np.round(cs).astype(int), np.round(rs).astype(int)
        ok = (cs >= 0) & (cs < W) & (rs >= 0) & (rs < H)
        hit[i] = ok.all() and ink[rs, cs].all()
    for a, b in _runs(hit):
        if b - a <= 6 * half:
            ycands.append(float(vs[a] + vs[b - 1]) / 2.0)
    ys = _regular(ycands, len(y_labels))
    if ys is None:
        raise RuntimeError(f"found {len(ycands)} ordinate ticks, need {len(y_labels)}")
    # y labels are given bottom to top: largest v first
    ymarks = list(zip(sorted(ys, reverse=True), y_labels))
    if zero_at_axes:
        # the printed 0 of each axis stands at the other axis' line (no tick of its own): the
        # ordinate's 0 at the frequency axis line, the frequency's 0 at the ordinate line
        ymarks.append((v_axis, 0.0))
        xa, xb, xmis = _fit(list(zip(xs, x_labels)) + [(u_y, 0.0)])
    ya, yb, ymis = _fit(ymarks)
    return dict(frame=fr, theta=theta, half=half, x=(xa, xb, xmis), y=(ya, yb, ymis), u_y=u_y,
                v_axis=v_axis, v_top=v0, v_bot=v1, U=U, V=V, region=region, xticks=xs, yticks=ys)


def _uv_grid(fr, H, W):
    r, c = np.mgrid[0:H, 0:W].astype(np.float32)
    return c * fr.c + r * fr.s, -c * fr.s + r * fr.c


def interior(ink, cal):
    """Ink inside the plot: right of the ordinate line, on the panel's side of the frequency axis."""
    return ink & cal["region"] & (cal["U"] > cal["u_y"] + 3 * cal["half"])


def to_x(cal, u):
    a, b, _ = cal["x"]
    return a + b * u


def to_y(cal, v):
    a, b, _ = cal["y"]
    return a + b * v


def u_of_x(cal, x):
    a, b, _ = cal["x"]
    return (x - a) / b


# ------------------------------------------------------------------ analysis of the plot

def _disk(r):
    r = int(max(r, 1))
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def _widest(mask):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        return None
    sl = ndimage.find_objects(lab)
    k = int(np.argmax([s[1].stop - s[1].start for s in sl])) + 1
    return lab == k


def analyse(image, x_labels, y_labels, phase, rings=False, ignore=(), zero_at_axes=False):
    """Calibrate, then describe the plot: the drawn line (the connected ink of widest extent) and
    its thickness L (median height of its single runs); solid blobs (what survives an opening with
    a disk wider than the line: the dots of Figs. 2-3); and, for Figs. 4-5, the rings.

    ignore: boxes [c0, r0, c1, r1] in the crop around the panel's text (axis title, unit, legend
    words), which is not data."""
    ink = ink_of(image)
    cal = calibrate(ink, x_labels, y_labels, phase, zero_at_axes)
    m = interior(ink, cal)
    for c0, r0, c1, r1 in ignore:
        m[r0:r1, c0:c1] = False
    line = _widest(m)
    lens = []
    for c in np.flatnonzero(line.any(axis=0))[::3]:
        rs = _runs(line[:, c])
        if len(rs) == 1:
            lens.append(rs[0][1] - rs[0][0])
    L = float(np.median(lens))
    # specks of paper inside a printed dot are filled first (holes smaller than L x L)
    holes = ndimage.binary_fill_holes(m) & ~m
    hl, hn = ndimage.label(holes)
    small = np.flatnonzero(ndimage.sum(holes, hl, index=np.arange(1, hn + 1)) < L * L) + 1
    op = ndimage.binary_opening(m | np.isin(hl, small), structure=_disk(0.6 * L + 1))
    bl, bn = ndimage.label(op)
    blobs = []
    for k, s in enumerate(ndimage.find_objects(bl)):
        sub = bl[s] == k + 1
        rr, cc = np.nonzero(sub)
        blobs.append({"c": cc.mean() + s[1].start + 0.5, "r": rr.mean() + s[0].start + 0.5,
                      "h": s[0].stop - s[0].start, "w": s[1].stop - s[1].start, "area": int(sub.sum())})
    A = dict(cal=cal, m=m, line=line, L=L, blobs=blobs, image_shape=m.shape, rings=[], ring_size=None)
    if rings:
        A["rings"], A["ring_size"] = _find_rings(m)
    return A


def _find_rings(m):
    """Rings by template. Their size comes from the clean rings: holes in the ink that are round
    (fill of their box at least 0.6, aspect within 0.7-1.4); inner diameter d = the median hole
    size, ring thickness t = the median ink run outward from the holes' right edges. Then every
    point whose annulus between d/2 and d/2 + t is at least 85% inked is a ring centre (a ring on
    the line, a ring filled in, or a ring with a cross in it all qualify; a line alone, a cross
    alone or a small dot does not). Neighbouring hits are merged; the centre is their
    score-weighted centroid."""
    from scipy.signal import fftconvolve

    holes = ndimage.binary_fill_holes(m) & ~m
    hl, hn = ndimage.label(holes)
    dias, thick = [], []
    for k, s in enumerate(ndimage.find_objects(hl)):
        sub = ndimage.binary_fill_holes(hl[s] == k + 1)
        h, w = sub.shape
        if min(h, w) < 12 or not (0.7 <= h / w <= 1.4) or sub.sum() < 0.6 * h * w:
            continue
        dias.append((h + w) / 2.0)
        rc, cc = (s[0].start + s[0].stop) // 2, s[1].stop
        run = 0
        while cc + run < m.shape[1] and m[rc, cc + run]:
            run += 1
        thick.append(run)
    if not dias:
        return [], None
    d = float(np.median(dias))
    tk = [x for x in thick if x > 0]
    t = float(np.percentile(tk, 25)) if tk else 0.25 * d  # runs from rings on the line run on
    ri, ro = d / 2.0 + 1, d / 2.0 + t - 1
    R = int(math.ceil(d / 2.0 + t))
    y, x = np.mgrid[-R:R + 1, -R:R + 1]
    rr = np.sqrt(x * x + y * y)
    ker = ((rr >= ri) & (rr <= ro)).astype(float)
    score = fftconvolve(m.astype(float), ker, mode="same") / ker.sum()
    lab, n = ndimage.label(score >= 0.8)
    hits = []
    inner = rr <= 0.8 * d / 2
    for k, s in enumerate(ndimage.find_objects(lab)):
        sub = lab[s] == k + 1
        r_, c_ = np.nonzero(sub)
        w = score[s][sub]
        r0 = float((r_ * w).sum() / w.sum()) + s[0].start
        c0 = float((c_ * w).sum() / w.sum()) + s[1].start
        spread = max(s[0].stop - s[0].start, s[1].stop - s[1].start)
        ir, ic = int(round(r0)), int(round(c0))
        if ir - R < 0 or ic - R < 0:
            continue
        win = m[ir - R: ir + R + 1, ic - R: ic + R + 1]
        if win.shape != ker.shape or win[inner].mean() < 0.15:
            continue  # every symbol of these figures has ink inside its ring (a dot or a cross)
        hits.append({"c": c0 + 0.5, "r": r0 + 0.5, "spread": spread, "score": float(w.max()),
                     "fill": float(win[inner].mean()),
                     "vert": float(win[(np.abs(x) <= 1) & inner].mean()),
                     "horz": float(win[(np.abs(y) <= 1) & inner].mean())})
    hits.sort(key=lambda q: -q["score"])
    merged = []
    for q in hits:
        if all(math.hypot(q["c"] - p["c"], q["r"] - p["r"]) > d + t for p in merged):
            merged.append(q)
    return merged, (d, t)


def symbol_mask(A, pts, rad):
    H, W = A["image_shape"]
    out = np.zeros((H, W), bool)
    for q in pts:
        _paint(out, q["c"], q["r"], rad)
    return out


def _paint(out, c, r, rad):
    H, W = out.shape
    r0, r1 = int(max(r - rad, 0)), int(min(r + rad + 1, H))
    c0, c1 = int(max(c - rad, 0)), int(min(c + rad + 1, W))
    if r1 <= r0 or c1 <= c0:
        return
    yy, xx = np.mgrid[r0:r1, c0:c1]
    out[r0:r1, c0:c1] |= (yy + 0.5 - r) ** 2 + (xx + 0.5 - c) ** 2 <= rad * rad


# ------------------------------------------------------------------ the drawn line

def _path(cm, L):
    """Column -> (centre row, half-height) of the line where the line runs alone: the column holds a
    single run no thicker than the line drawn at its local slope. Columns where a symbol, a dot or
    a cross touches the line (several runs, or a thicker run) are left out."""
    single = {}
    for c in np.flatnonzero(cm.any(axis=0)):
        r = _runs(cm[:, c])
        if len(r) == 1:
            single[int(c)] = ((r[0][0] + r[0][1]) / 2.0, (r[0][1] - r[0][0]) / 2.0)
    path = {}
    for c, (r, h) in single.items():
        nb = [single[k][0] for k in (c - 8, c + 8) if k in single]
        if len(nb) != 2:
            continue
        slope = abs(nb[1] - nb[0]) / 16
        if 2 * h <= 1.35 * L * math.sqrt(1 + slope * slope) + 3:
            path[c] = (r, h)
    return path


def read_line(A, at, note=""):
    """The drawn line at each frequency in `at`. Where something touches the line, it is
    interpolated (a quadratic through the clean columns on both sides) and the interval widened by
    the difference from a straight interpolation."""
    cal, fr, L = A["cal"], A["cal"]["frame"], A["L"]
    path = _path(A["line"], L)
    pc = np.array(sorted(path))
    centre = np.array([path[c][0] for c in pc])
    halfh = np.array([path[c][1] for c in pc])
    uu = (pc + 0.5) * fr.c + centre * fr.s
    vv = -(pc + 0.5) * fr.s + centre * fr.c
    order = np.argsort(uu)
    uu, vv, halfh = uu[order], vv[order], halfh[order]
    xmis, ymis = cal["x"][2], cal["y"][2]
    out = []
    for x in at:
        ut = u_of_x(cal, x)
        if ut < uu.min() - 2 or ut > uu.max() + 2:
            out.append({"x": x, "y": None, "note": "the drawn line does not reach this frequency"})
            continue
        j = int(np.searchsorted(uu, ut))
        jl, jr = max(j - 1, 0), min(j, len(uu) - 1)
        nt = note
        if uu[jr] - uu[jl] > 4:  # a gap: something touches the line here
            near = (uu >= uu[jl] - 40) & (uu <= uu[jr] + 40)
            t = (ut - uu[jl]) / (uu[jr] - uu[jl])
            vlin = vv[jl] + t * (vv[jr] - vv[jl])
            if near.sum() >= 10 and (uu[near] < ut).any() and (uu[near] > ut).any():
                v = float(np.polyval(np.polyfit(uu[near], vv[near], 2), ut))
            else:
                v = vlin
            slope = (vv[jr] - vv[jl]) / (uu[jr] - uu[jl])
            hw = max(halfh[jl], halfh[jr]) + 0.5 + abs(v - vlin) + 0.15 * L + abs(slope) * xmis + ymis
            nt = (nt + "; " if nt else "") + (f"something touches the line here; line interpolated across "
                                               f"{uu[jr] - uu[jl]:.0f} px")
        else:
            i = jl if abs(uu[jl] - ut) <= abs(uu[jr] - ut) else jr
            j0, j1 = max(i - 3, 0), min(i + 4, len(uu))
            slope = float(np.polyfit(uu[j0:j1], vv[j0:j1], 1)[0]) if j1 - j0 >= 3 else 0.0
            v = vv[i] + slope * (ut - uu[i])
            hw = halfh[i] + 0.5 + abs(slope) * xmis + ymis
        y = to_y(cal, v)
        a, b = to_y(cal, v - hw), to_y(cal, v + hw)
        col, row = fr.cr(ut, v)
        _, rlo = fr.cr(ut, v - hw)
        _, rhi = fr.cr(ut, v + hw)
        out.append({"x": x, "y": float(y), "lo": float(min(a, b)), "hi": float(max(a, b)),
                    "px": [float(col), float(row)], "px_lo": float(rlo), "px_hi": float(rhi),
                    "note": (nt + "; " if nt else "") + _calnote(cal)})
    return out


def _calnote(cal):
    return (f"calibration misfit {cal['x'][2]:.1f} px in f, {cal['y'][2]:.1f} px in y; scan tilt "
            f"{math.degrees(cal['theta']):.2f} deg")


# ------------------------------------------------------------------ symbols

def _point(cal, col, row, hw_px, note):
    fr = cal["frame"]
    u, v = fr.uv(col, row)
    x = to_x(cal, u)
    y = to_y(cal, v)
    hw = hw_px + cal["y"][2]
    a, b = to_y(cal, v - hw), to_y(cal, v + hw)
    _, rlo = fr.cr(u, v - hw)
    _, rhi = fr.cr(u, v + hw)
    return {"x": float(x), "y": float(y), "lo": float(min(a, b)), "hi": float(max(a, b)),
            "px": [float(col), float(row)], "px_lo": float(rlo), "px_hi": float(rhi), "note": note}


def dots_of(A):
    """The solid dots: blobs of the dots' common size (letters and the line are gone after the
    opening, or are too large). A blob longer than 2.2 dot diameters is touching dots, split
    evenly along its longer side into as many dots as its length holds."""
    bs = A["blobs"]
    if not bs:
        return [], 0.0
    dia = float(np.median([max(b["h"], b["w"]) for b in bs]))
    area = float(np.median([b["area"] for b in bs]))
    out = []
    for b in bs:
        if b["area"] < 0.3 * area or max(b["h"], b["w"]) > 3.2 * dia:
            continue
        long = max(b["h"], b["w"])
        n = int(round(long / dia)) if long > 2.2 * dia else 1
        if n >= 2:
            horiz = b["w"] >= b["h"]
            span = (b["w"] if horiz else b["h"]) - dia
            for i in range(n):
                off = -span / 2 + span * i / (n - 1)
                out.append(dict(b, c=b["c"] + (off if horiz else 0), r=b["r"] + (0 if horiz else off), split=True))
        else:
            out.append(dict(b, split=False))
    return out, dia


def read_dots(A):
    cal = A["cal"]
    ds, dia = dots_of(A)
    out = [_point(cal, d["c"], d["r"], dia / 2 if d["split"] else max(d["h"], dia) / 4,
                  ("one of touching dots, split by length; " if d["split"] else "") + _calnote(cal)) for d in ds]
    out.sort(key=lambda r: (r["x"], r["y"]))
    return out


def read_circles(A):
    cal = A["cal"]
    d, t = A["ring_size"]
    out = []
    for q in A["rings"]:
        kind = ("ring filled in" if q["fill"] >= 0.97 else
                "ring with a cross in it" if q["vert"] > 0.85 and q["horz"] > 0.85 else "ring")
        out.append(_point(cal, q["c"], q["r"], d / 4 + q["spread"] / 2, kind + "; " + _calnote(cal)))
    out.sort(key=lambda r: (r["x"], r["y"]))
    return out


def read_crosses(A):
    """Crosses. (1) Apart from everything: plus-shaped ink. (2) Inside an open ring: both diameters
    of the ring's inner disk inked while the disk is not filled in. (3) On the line: the cross's
    vertical arm sticks out of the line as a narrow run thicker than the line; its centre is the
    middle of the arm where the arm shows on both sides of the line, or the arm's free end less
    half an arm's length (from the free crosses) where it shows on one side only."""
    cal, L, m = A["cal"], A["L"], A["m"]
    d, t = A["ring_size"]
    rings = A["rings"]
    taken = symbol_mask(A, rings, d / 2 + t + 2)
    out, arms = [], []
    rest = m & ~A["line"] & ~taken
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    for k, s in enumerate(ndimage.find_objects(lab)):
        sub = lab[s] == k + 1
        h, w = sub.shape
        if not (0.5 * d <= max(h, w) <= 3 * d) or min(h, w) < 0.5 * max(h, w):
            continue
        if sub.sum() > 0.45 * h * w:
            continue
        rowsum, colsum = sub.sum(axis=1), sub.sum(axis=0)
        if rowsum.max() < 0.6 * w or colsum.max() < 0.6 * h:
            continue
        rr = int(np.argmax(rowsum)) + s[0].start + 0.5
        cc = int(np.argmax(colsum)) + s[1].start + 0.5
        arms.append(h)
        out.append(_point(cal, cc, rr, L / 2 + 1, "cross apart from the line; " + _calnote(cal)))
    for q in rings:
        if q["fill"] < 0.97 and q["vert"] > 0.85 and q["horz"] > 0.85:
            out.append(_point(cal, q["c"], q["r"], d / 4 + q["spread"] / 2,
                              "cross inside a ring; " + _calnote(cal)))
    arm = float(np.median(arms)) if arms else None
    # (3) arms sticking out of the line
    line = A["line"] & ~taken
    path = _path(A["line"], L)
    pc = np.array(sorted(path))
    if arm is not None and len(pc) > 10:
        pr = np.array([path[c][0] for c in pc])
        thick = []
        for c in np.flatnonzero(line.any(axis=0)):
            if c < pc.min() + 10 or c > pc.max() - 10:
                continue
            lr = float(np.interp(c, pc, pr))
            if any(math.hypot(c - q["c"], lr - q["r"]) < d / 2 + t + L for q in rings):
                continue  # next to a ring an arm cannot be told from the ring's own ink
            if abs(float(np.interp(c + 10, pc, pr)) - float(np.interp(c - 10, pc, pr))) > 0.6 * 20:
                continue  # where the line is steep a cross's arm cannot be told from the line
            rs = [r for r in _runs(line[:, c]) if r[0] - 2 <= lr <= r[1] + 2]
            if not rs:
                continue
            a, b = rs[0]
            if taken[max(a - 3, 0): b + 3, c].any():
                continue
            up, dn = lr - L / 2 - a, b - (lr + L / 2)
            if max(up, dn) > 0.25 * arm:
                thick.append((int(c), a, b, up, dn))
        groups, cur = [], []
        for tc in thick:
            if cur and tc[0] - cur[-1][0] > 2:
                groups.append(cur)
                cur = []
            cur.append(tc)
        if cur:
            groups.append(cur)
        for g in groups:
            if len(g) > 1.5 * arm or len(g) < 2:
                continue
            # the vertical arm: the columns sticking out furthest
            ext = np.array([max(x[3], x[4]) for x in g])
            arm_cols = [x for x, e in zip(g, ext) if e >= ext.max() - 3]
            g_c = (arm_cols[0][0] + arm_cols[-1][0]) / 2.0 + 0.5
            a = min(x[1] for x in arm_cols)
            b = max(x[2] for x in arm_cols)
            up = max(x[3] for x in arm_cols)
            dn = max(x[4] for x in arm_cols)
            if up > 0.25 * arm and dn > 0.25 * arm:
                r0, hw, how = (a + b) / 2.0, abs(up - dn) / 2 + L / 2, "its arm shows on both sides of the line"
            elif up > dn:
                r0, hw, how = a + arm / 2.0, L, "its arm shows above the line only"
            else:
                r0, hw, how = b - arm / 2.0, L, "its arm shows below the line only"
            out.append(_point(cal, g_c, r0, hw, f"cross on the line ({how}); " + _calnote(cal)))
    out.sort(key=lambda r: (r["x"], r["y"]))
    return out
