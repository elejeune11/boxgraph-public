"""Shared reading code for the erdmann2004 figures (all vector line plots, black on white).

Everything here is found in the rendered crop:
  frame:  the plot box, the four longest dark lines (their centre rows/columns);
  ticks:  the major inner tick marks along one frame edge, found as short dark strokes in a
          band just inside the frame, beyond the reach of the dotted minor ticks;
  curves: dark runs in a column, followed from a starting run by `trace`.
The caller (one small file per reading) gives only the printed axis labels it matched to
the ticks, and a rule saying which curve it reads.
"""
import math

import numpy as np


def gray(img):
    return img.astype(float).mean(axis=2)


def dark(img, thr=128.0):
    return gray(img) < thr


def _long_lines(d, axis, frac):
    """Indices along `axis` whose longest dark run covers at least `frac` of the other size."""
    a = d if axis == 0 else d.T            # rows of a are scanned
    n = a.shape[1]
    out = []
    for i in range(a.shape[0]):
        v = a[i]
        best, run = 0, 0
        for x in v:
            run = run + 1 if x else 0
            if run > best:
                best = run
        if best >= frac * n:
            out.append(i)
    return out


def _groups(idx):
    gs, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            gs.append(cur)
            cur = []
        cur.append(i)
    if cur:
        gs.append(cur)
    return gs


def frame(img):
    """(left, top, right, bottom): centres of the frame lines, and their half-thickness."""
    d = dark(img)
    rows = _groups(_long_lines(d, 0, 0.5))
    cols = _groups(_long_lines(d, 1, 0.5))
    top, bot = rows[0], rows[-1]
    left, right = cols[0], cols[-1]
    c = lambda g: (g[0] + g[-1]) / 2.0 + 0.5
    half = max(len(top), len(bot), len(left), len(right)) / 2.0
    return dict(left=c(left), right=c(right), top=c(top), bottom=c(bot), half=half,
                inner=dict(left=left[-1] + 1, right=right[0], top=top[-1] + 1, bottom=bot[0]))


def ticks(img, fr, edge, depth=(9, 15)):
    """Positions of the major tick marks along an edge ('top', 'bottom', 'left', 'right'):
    stroke centres in a band `depth` pixels inside the frame line. At these resolutions the
    dotted minor ticks reach about 6-7 px and the major ones about 18-20 px, so the band
    holds only major ticks (and whatever curve happens to cross it)."""
    d = dark(img)
    inn = fr["inner"]
    d0, d1 = depth
    if edge in ("top", "bottom"):
        if edge == "top":
            band = d[inn["top"] + d0:inn["top"] + d1, inn["left"] + 3:inn["right"] - 3]
        else:
            band = d[inn["bottom"] - d1:inn["bottom"] - d0, inn["left"] + 3:inn["right"] - 3]
        prof = band.mean(axis=0)
        off = inn["left"] + 3
    else:
        if edge == "left":
            band = d[inn["top"] + 3:inn["bottom"] - 3, inn["left"] + d0:inn["left"] + d1]
        else:
            band = d[inn["top"] + 3:inn["bottom"] - 3, inn["right"] - d1:inn["right"] - d0]
        prof = band.mean(axis=1)
        off = inn["top"] + 3
    on = np.nonzero(prof > 0.9)[0]          # a tick fills the whole band
    out = []
    for g in _groups(list(on)):
        if len(g) <= 25:                    # a stroke, not a curve lying along the edge
            out.append(off + (g[0] + g[-1]) / 2.0 + 0.5)
    return out


def regular(pos, tol=2.5):
    """The longest evenly spaced subsequence of tick positions (curves crossing the band can
    add strokes; they do not fall on the grid)."""
    p = sorted(pos)
    best = []
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            s = p[j] - p[i]
            if s < 20:
                continue
            m = [p[i], p[j]]
            while True:
                want = m[-1] + s
                near = [x for x in p if abs(x - want) <= tol]
                if not near:
                    break
                m.append(min(near, key=lambda x: abs(x - want)))
            # also extend backwards
            while True:
                want = m[0] - s
                near = [x for x in p if abs(x - want) <= tol]
                if not near:
                    break
                m.insert(0, min(near, key=lambda x: abs(x - want)))
            if len(m) > len(best) or (len(m) == len(best) and m[1] - m[0] > best[1] - best[0]):
                best = m
    return best


class Axis:
    """u = a + b * pixel, with u the value (linear) or log10 of the value (log10 scale)."""

    def __init__(self, marks, scale="linear"):
        self.scale = scale
        P = np.array([m[0] for m in marks], float)
        U = np.array([m[1] for m in marks], float)
        self.b, self.a = np.polyfit(P, U, 1)
        self.misfit = float(np.max(np.abs(P - (U - self.a) / self.b)))
        self.n = len(marks)
        self.marks = marks

    def u(self, p):
        return self.a + self.b * p

    def value(self, p):
        u = self.u(p)
        return 10.0 ** u if self.scale == "log10" else u

    def pixel_u(self, u):
        return (u - self.a) / self.b

    def pixel(self, v):
        return self.pixel_u(math.log10(v) if self.scale == "log10" else v)


def calibrate(tick_pos, anchor_px, anchor_u, step_u, extra=(), scale="linear"):
    """Assign values to evenly spaced ticks: the tick k spacings from the anchor (a frame
    edge or tick whose printed label is known) has u = anchor_u + k * step_u. `extra` are
    further (pixel, u) marks, e.g. a frame edge that carries a printed label."""
    t = regular(tick_pos)
    s = float(np.median(np.diff(t)))
    marks = [(p, anchor_u + round((p - anchor_px) / s) * step_u) for p in t]
    marks += list(extra)
    return Axis(marks, scale), t


def column_runs(d, c, r0, r1):
    """(centre, half-height) of the dark runs in column c between rows r0 and r1."""
    col = d[int(r0):int(r1), int(c)]
    idx = np.nonzero(col)[0]
    out = []
    for g in _groups(list(idx)):
        out.append((r0 + (g[0] + g[-1]) / 2.0 + 0.5, (g[-1] - g[0] + 1) / 2.0))
    return out


def trace(d, c0, r0, cmin, cmax, rmin, rmax, max_gap=12):
    """Follow a curve from (c0, r0) column by column both ways; at each column take the run
    nearest the position the recent slope predicts. A run much thicker than the line is a
    crossing: its centre is replaced by the prediction and the column is marked ambiguous.
    Returns column -> (centre, half, ambiguous)."""
    runs = column_runs(d, c0, rmin, rmax)
    if not runs:
        return {}
    start = min(runs, key=lambda r: abs(r[0] - r0))
    typ = start[1]
    path = {c0: (start[0], start[1], False)}
    for step in (1, -1):
        hist = [(c0, start[0])]
        c, gap = c0 + step, 0
        while cmin <= c <= cmax and gap <= max_gap:
            rec = hist[-40:]
            if len(rec) > 3:
                xs = np.array([q[0] for q in rec], float)
                ys = np.array([q[1] for q in rec], float)
                slope, icpt = np.polyfit(xs, ys, 1)
                slope = float(slope)
                pred = float(icpt + slope * c)
            else:
                slope, pred = 0.0, hist[-1][1]
            rs = column_runs(d, c, rmin, rmax)
            if rs:
                best = min(rs, key=lambda r: abs(r[0] - pred))
                reach = 3 * typ + abs(slope) * (gap + 1) + 4
                if abs(best[0] - pred) <= reach + best[1]:
                    exp = typ * math.sqrt(1 + slope * slope) + 2
                    if best[1] > 1.3 * exp:
                        top, bot = best[0] - best[1], best[0] + best[1]
                        cen = min(max(pred, top + typ), bot - typ)
                        path[c] = (cen, best[1], True)
                        hist.append((c, cen))
                    else:
                        path[c] = (best[0], best[1], False)
                        hist.append((c, best[0]))
                    gap = 0
                    c += step
                    continue
            gap += 1
            c += step
    return path


def at_column(path, c, slope_window=8):
    """Centre, half-height, ambiguity and local slope of a traced curve at a (fractional)
    column, from the nearest traced columns."""
    cs = sorted(k for k in path if abs(k - c) <= slope_window)
    if len(cs) < 3:
        return None
    ci = int(round(c))
    near = [k for k in cs if abs(k - ci) <= 1]
    if not near:
        return None
    k = min(near, key=lambda k: abs(k - c))
    cen, half, amb = path[k]
    xs = np.array(cs, float)
    ys = np.array([path[q][0] for q in cs])
    slope = float(np.polyfit(xs, ys, 1)[0])
    cen = cen + slope * (c - k)
    amb = amb or any(path[q][2] for q in near)
    return cen, half, amb, slope


def point(xax, yax, x_value, path, extra_note="", line_px=None):
    """One reading of a traced curve at x_value, with a 95% interval in y from: where the
    line's centre is (a quarter of its thickness, at least 1 px), the y calibration misfit,
    and the x calibration misfit times the local slope; a crossing widens it to the merged run."""
    c = xax.pixel(x_value)
    got = at_column(path, c)
    note = (f"x {xax.n} marks misfit {xax.misfit:.2f} px; y {yax.n} marks misfit {yax.misfit:.2f} px"
            + (f"; {extra_note}" if extra_note else ""))
    if got is None:
        return {"x": x_value, "y": None, "note": "curve not traced at this x; " + note}
    cen, half, amb, slope = got
    lw = line_px if line_px is not None else 2 * half
    err = max(1.0, 0.25 * lw) + max(yax.misfit, 0.5) + abs(slope) * max(xax.misfit, 0.5)
    if amb:
        err = max(err, half)
        note = "crossing another curve here: interval spans the merged run; " + note
    u, ulo, uhi = yax.u(cen), yax.u(cen + err), yax.u(cen - err)
    if ulo > uhi:
        ulo, uhi = uhi, ulo
    f = (lambda q: 10.0 ** q) if yax.scale == "log10" else (lambda q: q)
    return {"x": x_value, "y": f(u), "lo": f(ulo), "hi": f(uhi), "px": [c, cen],
            "px_lo": cen - err, "px_hi": cen + err, "note": note}


def line_width(d, fr):
    """The commonest thickness of the curves: run heights in columns across the box."""
    hs = []
    for c in range(int(fr["left"]) + 30, int(fr["right"]) - 30, 7):
        for _, h in column_runs(d, c, fr["inner"]["top"] + 30, fr["inner"]["bottom"] - 30):
            hs.append(int(round(2 * h)))
    vals, counts = np.unique(hs, return_counts=True)
    return float(vals[np.argmax(counts)])


MARGIN = 22   # px kept clear of the frame: the major ticks reach about 20 px into the box


def components(d, fr):
    """Connected dark blobs inside the box (clear of the frame and its ticks):
    list of dict(area, rows, cols)."""
    from scipy import ndimage
    inn = fr["inner"]
    r0, r1 = inn["top"] + MARGIN, inn["bottom"] - MARGIN
    c0, c1 = inn["left"] + MARGIN, inn["right"] - MARGIN
    sub = d[r0:r1, c0:c1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)
    out = []
    for i, sl in enumerate(objs, start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        rr = rr + sl[0].start + r0
        cc = cc + sl[1].start + c0
        out.append(dict(area=len(rr), rows=rr, cols=cc,
                        touches=(rr.min() == r0 or rr.max() == r1 - 1 or cc.min() == c0 or cc.max() == c1 - 1)))
    return out


def solid_mask(d, fr, min_area):
    """Only the blobs of at least `min_area` pixels: the solid lines, without dashes or dots."""
    m = np.zeros_like(d)
    for o in components(d, fr):
        if o["area"] >= min_area:
            m[o["rows"], o["cols"]] = True
    return m


def dash_list(d, fr, min_area, max_area, allow_touch=False):
    """The separate dashes: blobs within the area limits that do not touch the clear margin
    (unless `allow_touch`: a dash cut by the margin is still a straight piece of its line).
    Each: centroid (col, row), its two ends (by the blob's principal direction) and area."""
    out = []
    for o in components(d, fr):
        if not (min_area <= o["area"] <= max_area) or (o["touches"] and not allow_touch):
            continue
        c, r = o["cols"] + 0.5, o["rows"] + 0.5
        mc, mr = c.mean(), r.mean()
        cov = np.cov(np.vstack([c - mc, r - mr]))
        w, v = np.linalg.eigh(cov)
        u = v[:, np.argmax(w)]
        if u[0] < 0:
            u = -u
        t = (c - mc) * u[0] + (r - mr) * u[1]
        out.append(dict(c=mc, r=mr, area=o["area"], dir=u,
                        a=(mc + t.min() * u[0], mr + t.min() * u[1]),
                        b=(mc + t.max() * u[0], mr + t.max() * u[1])))
    return sorted(out, key=lambda q: q["c"])


def chains(ds, max_gap=140.0, max_off=30.0):
    """Link dashes into dashed lines, left to right: a dash continues a chain when its left
    end lies ahead of the chain's last dash along that dash's direction, at most `max_gap`
    away and at most `max_off` off the line."""
    left = list(ds)
    out = []
    while left:
        ch = [left.pop(0)]
        while True:
            last = ch[-1]
            best, bd = None, None
            for q in left:
                dx, dy = q["a"][0] - last["b"][0], q["a"][1] - last["b"][1]
                along = dx * last["dir"][0] + dy * last["dir"][1]
                off = abs(-dx * last["dir"][1] + dy * last["dir"][0])
                if 0 < along <= max_gap and off <= max_off and (bd is None or along + off < bd):
                    best, bd = q, along + off
            if best is None:
                break
            ch.append(best)
            left.remove(best)
        out.append(ch)
    return sorted(out, key=len, reverse=True)


# ------------------------------------------------------------------------------------------
# Panels: which ticks calibrate each axis and the printed labels matched to them.
# Each axis: (edge whose ticks are used, anchor, step in u per tick, labelled frame edges).
# An anchor is a frame edge ('left', 'right', 'top', 'bottom') or 'first' (the first regular
# tick), with the u its printed label gives; u is the value on a linear axis and log10 of it
# on a log axis ("log N", "log T", "log f/N0" are printed as their log10 values).
# ------------------------------------------------------------------------------------------
PANELS = {
    # Fig. 2(a): x labels 0..5, ticks every 1, left frame under "0"; y labels 0.0..1.0, ticks
    # every 0.2 on the right edge, top frame at "1.0".
    "2a": dict(x=("top", ("left", 0.0), 1.0, {"left": 0.0}), y=("right", ("top", 1.0), -0.2, {"top": 1.0}),
               xs="linear", ys="linear"),
    # Fig. 2(b): x ticks every 0.5 (labels 0..5 on whole numbers), frame from "0" to "5".
    "2b": dict(x=("top", ("left", 0.0), 0.5, {"left": 0.0, "right": 5.0}),
               y=("left", ("top", 1.0), -0.2, {"top": 1.0}), xs="linear", ys="linear"),
    # Fig. 2(c): x ticks every 5 (labels 0..50 every 10), right frame at "50" (the left frame is
    # thickened by the steep p10 line); y ticks every 0.05 (labels every 0.1), top frame "0.5".
    "2c": dict(x=("top", ("right", 50.0), 5.0, {"right": 50.0}),
               y=("right", ("top", 0.5), -0.05, {"top": 0.5}), xs="linear", ys="linear"),
    # Fig. 2(d): x ticks every 0.0005 (labels 0, 0.001, 0.002, 0.003), left frame "0".
    "2d": dict(x=("top", ("left", 0.0), 0.0005, {"left": 0.0}),
               y=("right", ("top", 1.0), -0.2, {"top": 1.0}), xs="linear", ys="linear"),
    # Fig. 3(a): x ticks every 10 (labels 0..80 every 20), frame from "0" to "80"; y "log N",
    # ticks every 1 from "1" down to "-4" at the bottom frame.
    "3a": dict(x=("top", ("left", 0.0), 10.0, {"left": 0.0, "right": 80.0}),
               y=("right", ("bottom", -4.0), -1.0, {"bottom": -4.0}), xs="linear", ys="log10"),
    # Fig. 3(d): x ticks every 0.5 (labels 0..3), left frame "0"; y "log N" with major tick
    # "0" and minor ticks at log10 of 2..9 and 0.5..0.9 (calibrated by `log_minor`).
    "3d": dict(x=("top", ("left", 0.0), 0.5, {"left": 0.0}), y="log_minor", xs="linear", ys="log10"),
    # Fig. 4(a): x "log f/N0", ticks every decade (labels -5..1), right frame at "1";
    # y "T", ticks every 2 (labels 0..10), bottom frame "0".
    "4a": dict(x=("top", ("right", 1.0), 1.0, {"right": 1.0}),
               y=("left", ("bottom", 0.0), -2.0, {"bottom": 0.0}), xs="log10", ys="linear"),
    # Fig. 4(b): x ticks every 10, the first one labelled "10" (labels 10, 30, 50, 70);
    # y "log T", ticks every 2 (labels 0..20 every 4), bottom frame "0", top frame "20".
    "4b": dict(x=("top", ("first", 10.0), 10.0, {}),
               y=("right", ("bottom", 0.0), -2.0, {"bottom": 0.0, "top": 20.0}), xs="linear", ys="log10"),
}


def _axis(img, fr, spec, scale):
    edge, (anchor, au), step, frames = spec
    t = regular(ticks(img, fr, edge))
    s = float(np.median(np.diff(t)))
    ap = t[0] if anchor == "first" else fr[anchor]
    # step: the change of u from one tick to the next in the direction of increasing pixel
    marks = [(p, au + round((p - ap) / s) * step) for p in t]
    marks += [(fr[e], u) for e, u in frames.items()]
    return Axis(marks, scale)


def log_minor(img, fr):
    """A log axis with minor ticks at log10(n): the major tick (the longest stroke) is u = 0;
    every tick, minor or major, is matched to the nearest log10(n), n = 0.5..0.9, 1..10, using
    the top frame as a first guess for u = 1; then all matched ticks are fitted."""
    edge = "right"
    major = ticks(img, fr, edge)
    z = max(major, key=lambda p: min(p - fr["top"], fr["bottom"] - p))   # the most interior one
    all_t = ticks(img, fr, edge, depth=(2, 5))
    decade = z - fr["top"]
    cands = [math.log10(n / 10) for n in range(5, 10)] + [math.log10(n) for n in range(1, 11)]
    marks = []
    for p in all_t:
        u0 = (z - p) / decade
        c = min(cands, key=lambda q: abs(q - u0))
        if abs(c - u0) < 0.02:
            marks.append((p, c))
    return Axis(marks, "log10")


def setup(img, panel):
    fr = frame(img)
    P = PANELS[panel]
    xax = _axis(img, fr, P["x"], P["xs"])
    yax = log_minor(img, fr) if P["y"] == "log_minor" else _axis(img, fr, P["y"], P["ys"])
    return fr, xax, yax


def start_run(m, fr, col, k, from_top=True):
    inn = fr["inner"]
    rs = column_runs(m, int(round(col)), inn["top"] + MARGIN, inn["bottom"] - MARGIN)
    rs = sorted(rs, key=lambda r: r[0], reverse=not from_top)
    return rs[k][0] if len(rs) > k else None


def read_curve(img, at, panel, start_x=None, start="right", k=0, from_top=True, solid_min_area=None, note=""):
    """Read one traced curve at the x values `at`. The curve is the k-th dark run from the top
    (or bottom) in the starting column: at x = start_x, or just inside the right/left frame."""
    fr, xax, yax = setup(img, panel)
    d = dark(img)
    m = solid_mask(d, fr, solid_min_area) if solid_min_area else d
    inn = fr["inner"]
    if start_x is not None:
        c0 = int(round(xax.pixel(start_x)))
    elif start == "right":
        c0 = inn["right"] - MARGIN - 3
    else:
        c0 = inn["left"] + MARGIN + 3
    r0 = start_run(m, fr, c0, k, from_top)
    if r0 is None:
        return [{"x": x, "y": None, "note": "no starting run found"} for x in at]
    path = trace(m, c0, r0, inn["left"] + MARGIN, inn["right"] - MARGIN,
                 inn["top"] + MARGIN, inn["bottom"] - MARGIN)
    return [point(xax, yax, x, path, note) for x in at]


def read_dashes(img, panel, which, min_area, max_area, note="", allow_touch=False, min_chain=3):
    """Read a dashed line dash by dash, each at its centroid. `which` picks the chain:
    'longest', 'all', 'right' (the chain reaching furthest right) or 'second_right'."""
    fr, xax, yax = setup(img, panel)
    d = dark(img)
    ds = dash_list(d, fr, min_area, max_area, allow_touch)
    chs = [c for c in chains(ds) if len(c) >= min_chain]
    if which == "longest":
        ch = chs[0]
    elif which == "all":
        ch = sorted([q for c in chs for q in c], key=lambda q: q["c"])
    else:
        by_right = sorted(chs, key=lambda c: max(q["c"] for q in c), reverse=True)
        ch = by_right[0] if which == "right" else by_right[1]
    out = []
    for q in ch:
        slope = q["dir"][1] / q["dir"][0] if abs(q["dir"][0]) > 1e-9 else 0.0
        err = 1.0 + max(yax.misfit, 0.5) + abs(slope) * max(xax.misfit, 0.5)
        u, ulo, uhi = yax.u(q["r"]), yax.u(q["r"] + err), yax.u(q["r"] - err)
        ulo, uhi = min(ulo, uhi), max(ulo, uhi)
        f = (lambda v: 10.0 ** v) if yax.scale == "log10" else (lambda v: v)
        out.append({"x": float(xax.value(q["c"])), "y": f(u), "lo": f(ulo), "hi": f(uhi),
                    "px": [q["c"], q["r"]], "px_lo": q["r"] - err, "px_hi": q["r"] + err,
                    "note": (f"dash centroid ({q['area']} px), chain of {len(ch)} dashes; x {xax.n} marks "
                             f"misfit {xax.misfit:.2f} px; y {yax.n} marks misfit {yax.misfit:.2f} px"
                             + (f"; {note}" if note else ""))})
    return out
