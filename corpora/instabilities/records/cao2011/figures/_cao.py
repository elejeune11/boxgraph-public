"""Shared reading code for the cao2011 figures (vector line plots and coloured FE markers).

Everything is found in the rendered crop:
  axes:    the plot has an open L frame: the y axis is the column with the longest vertical run of
           neutral (grey or black) ink, the x axis the row with the longest horizontal run;
  ticks:   short neutral strokes standing on an axis line (either side); the major ticks are the
           longest ones, and only the evenly spaced majors are kept;
  values:  each axis is calibrated from its major ticks (and the corner where it carries a printed
           label), anchored to one printed label the caller matched on the page;
  curves:  the dark runs crossing a column inside the plot, counted from the top or the bottom;
  markers: connected blobs of one marker colour, each read at the centre of its bounding box; a
           marker partly hidden by another one is placed from its visible edge, and a blob of
           several overlapping markers is split by the maxima of its distance transform.
Each reading file says which panel (axis labels) and which curve or marker colour it reads.
"""
import math

import numpy as np
from scipy import ndimage


def gray(img):
    return img[..., :3].astype(float).mean(axis=2)


def neutral_ink(img, thr=170.0, spread=45.0):
    a = img[..., :3].astype(float)
    return (a.mean(axis=2) < thr) & (a.max(axis=2) - a.min(axis=2) < spread)


def _groups(idx):
    gs, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            gs.append(cur)
            cur = []
        cur.append(int(i))
    if cur:
        gs.append(cur)
    return gs


def _longest_runs(m):
    """For each row of m: (length, start, end) of its longest run of True."""
    out = []
    for v in m:
        idx = np.flatnonzero(v)
        best = (0, 0, 0)
        for g in _groups(idx):
            if len(g) > best[0]:
                best = (len(g), g[0], g[-1] + 1)
        out.append(best)
    return out


def find_axes(img):
    """The y axis (column, row extent) and the x axis (row, column extent) of an open L frame."""
    ink = neutral_ink(img)
    cols = _longest_runs(ink.T)
    rows = _longest_runs(ink)
    cmax = max(c[0] for c in cols)
    rmax = max(r[0] for r in rows)
    yc = [i for i, c in enumerate(cols) if c[0] >= 0.9 * cmax]
    xr = [i for i, r in enumerate(rows) if r[0] >= 0.9 * rmax]
    yc = max(_groups(yc), key=len)
    xr = max(_groups(xr), key=len)
    ycol = (yc[0] + yc[-1]) / 2.0 + 0.5
    xrow = (xr[0] + xr[-1]) / 2.0 + 0.5
    ytop = min(cols[i][1] for i in yc)
    ybot = max(cols[i][2] for i in yc)
    xl = min(rows[i][1] for i in xr)
    xrt = max(rows[i][2] for i in xr)
    return dict(ycol=ycol, yhalf=len(yc) / 2.0, ytop=ytop, ybot=ybot, ycols=(yc[0], yc[-1]),
                xrow=xrow, xhalf=len(xr) / 2.0, xleft=xl, xright=xrt, xrows=(xr[0], xr[-1]))


def _ticks_on(ink, line_lo, line_hi, span, horizontal, maxlen):
    """Tick strokes standing on an axis line occupying rows (or columns) line_lo..line_hi:
    list of (position, length) for strokes on either side."""
    out = []
    if horizontal:
        n = ink.shape[0]
        lens = np.zeros(ink.shape[1])
        for c in range(span[0], span[1]):
            up = 0
            r = line_lo - 1
            while r >= 0 and ink[r, c] and up < maxlen:
                up += 1
                r -= 1
            dn = 0
            r = line_hi + 1
            while r < n and ink[r, c] and dn < maxlen:
                dn += 1
                r += 1
            lens[c] = max(up, dn)
    else:
        n = ink.shape[1]
        lens = np.zeros(ink.shape[0])
        for r in range(span[0], span[1]):
            lf = 0
            c = line_lo - 1
            while c >= 0 and ink[r, c] and lf < maxlen:
                lf += 1
                c -= 1
            rt = 0
            c = line_hi + 1
            while c < n and ink[r, c] and rt < maxlen:
                rt += 1
                c += 1
            lens[r] = max(lf, rt)
    on = np.flatnonzero((lens >= 6) & (lens < maxlen))
    for g in _groups(on):
        if len(g) <= 14:
            out.append(((g[0] + g[-1]) / 2.0 + 0.5, float(lens[g].max())))
    return out


def regular(pos, rel_tol=0.025, min_gap=40.0):
    """The longest evenly spaced subsequence (to rel_tol of the spacing: the printed tick
    marks are placed to a few pixels at these resolutions)."""
    p = sorted(pos)
    best = []
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            s = p[j] - p[i]
            if s < min_gap:
                continue
            tol = max(3.0, rel_tol * s)
            m = [p[i], p[j]]
            while True:
                near = [x for x in p if abs(x - (m[-1] + s)) <= tol]
                if not near:
                    break
                m.append(min(near, key=lambda x: abs(x - (m[-1] + s))))
            while True:
                near = [x for x in p if abs(x - (m[0] - s)) <= tol]
                if not near:
                    break
                m.insert(0, min(near, key=lambda x: abs(x - (m[0] - s))))
            if len(m) > len(best) or (len(m) == len(best) and m[1] - m[0] > best[1] - best[0]):
                best = m
    return best


class Axis:
    """value = a + b * pixel, fitted to (pixel, printed value) marks."""

    def __init__(self, marks):
        P = np.array([m[0] for m in marks], float)
        U = np.array([m[1] for m in marks], float)
        self.b, self.a = np.polyfit(P, U, 1)
        self.misfit = float(np.max(np.abs(P - (U - self.a) / self.b)))
        self.n = len(marks)
        self.marks = marks

    def value(self, p):
        return float(self.a + self.b * p)

    def pixel(self, v):
        return float((v - self.a) / self.b)


def calibrate(img, spec):
    """spec: x=(anchor, step, n_majors), y=(anchor, step, n_majors). anchor is ('corner', value)
    when the axes' corner carries a printed label, or ('first', value): the value printed at the
    first major tick (leftmost for x, lowest for y). step is the value between neighbouring majors
    in the direction of increasing value; n_majors is how many evenly spaced majors the caller
    counted on the page (a check)."""
    ax = find_axes(img)
    ink = neutral_ink(img)
    maxlen = int(0.04 * max(img.shape[:2]))
    xt = _ticks_on(ink, ax["xrows"][0], ax["xrows"][1],
                   (int(ax["ycols"][1]) + 4, int(ax["xright"])), True, maxlen)
    yt = _ticks_on(ink, ax["ycols"][0], ax["ycols"][1],
                   (int(ax["ytop"]), int(ax["xrows"][0]) - 4), False, maxlen)
    out = {"axes": ax}
    for name, ticks, corner_px, sign in (("x", xt, ax["ycol"], 1), ("y", yt, ax["xrow"], -1)):
        anchor, step, nmaj = spec[name]
        # the majors are the longest strokes; a curve running into the axis can make a longer
        # stroke, so the length threshold steps down until an evenly spaced set of the counted
        # number of majors appears
        maj = []
        for L in sorted({t[1] for t in ticks}, reverse=True):
            maj = regular([t[0] for t in ticks if t[1] >= 0.75 * L])
            if len(maj) >= nmaj:
                break
        if len(maj) != nmaj:
            raise ValueError(f"{name}: found {len(maj)} major ticks, expected {nmaj}: {maj}")
        s = float(np.median(np.diff(maj)))
        if anchor[0] == "corner":
            p0, v0 = corner_px, anchor[1]
        else:
            p0 = maj[0] if sign > 0 else maj[-1]
            v0 = anchor[1]
        marks = [(p, v0 + sign * round((p - p0) / s) * step) for p in maj]
        if anchor[0] == "corner":
            marks.append((corner_px, anchor[1]))
        out[name] = Axis(marks)
        out[name + "_ticks"] = maj
    return out


# Panels: the printed axis labels matched to the major ticks. Each axis: (anchor, step, number
# of evenly spaced major ticks counted on the page); see `calibrate`.
PANELS = {
    # Fig. 2(a): x labels 0, 0.02 ... 0.10 ("0" at the corner); y labels -0.10 (corner) ... 0.10
    "2a": dict(x=(("corner", 0.0), 0.02, 5), y=(("corner", -0.10), 0.05, 4)),
    # Fig. 2(b): x as (a); y labels -0.05 (corner), -0.04 ... 0.01
    "2b": dict(x=(("corner", 0.0), 0.02, 5), y=(("corner", -0.05), 0.01, 6)),
    # Fig. 3: x labels 0 (corner), 0.5, 1.0, 1.5, 2.0; y labels -1.5 (corner), -1.0 ... 1.0
    "3": dict(x=(("corner", 0.0), 0.5, 4), y=(("corner", -1.5), 0.5, 5)),
    # Fig. 4: x labels 0 (corner), 0.001 ... 0.005; y the corner is 0 (one tick spacing below
    # the label 0.05), labels 0.05 ... 0.20
    "4": dict(x=(("corner", 0.0), 0.001, 5), y=(("corner", 0.0), 0.05, 4)),
    # Fig. 5: x labels 0 (corner), 0.005 ... 0.025; y labels 0.1 ... 0.5, the corner one
    # spacing below 0.1, i.e. 0
    "5": dict(x=(("corner", 0.0), 0.005, 5), y=(("corner", 0.0), 0.1, 5)),
    # Fig. 6: x labels 0.010 ... 0.045 on the majors (the corner is unlabelled); y 0 ... 0.5
    "6": dict(x=(("first", 0.010), 0.005, 8), y=(("first", 0.0), 0.1, 6)),
    # Fig. 7: x labels 0 (corner), 0.1 ... 0.5; y labels 0.010 ... 0.040: the major at 0.010
    # is shortened by a marker, so the six majors 0.015 ... 0.040 are used
    "7": dict(x=(("corner", 0.0), 0.1, 5), y=(("first", 0.015), 0.005, 6)),
    # Fig. 8: x labels 0 (corner), 1 ... 8; y labels 0.1 ... 0.5, the corner one spacing
    # below 0.1, i.e. 0
    "8": dict(x=(("corner", 0.0), 1.0, 8), y=(("corner", 0.0), 0.1, 5)),
    # Fig. 9: x labels 0 (corner), 0.005 ... 0.030; y labels 0.20 (corner), 0.25 ... 0.50
    "9": dict(x=(("corner", 0.0), 0.005, 6), y=(("corner", 0.20), 0.05, 6)),
}


def load(img, panel):
    return calibrate(img, PANELS[panel])


# ------------------------------------------------------------------------------- curves


def column_runs(m, c, r0, r1):
    col = m[int(r0):int(r1), int(c)]
    out = []
    for g in _groups(np.flatnonzero(col)):
        out.append((r0 + (g[0] + g[-1]) / 2.0 + 0.5, (g[-1] - g[0] + 1) / 2.0))
    return out


def read_runs(img, cal, at, pick, count=None, r_range=None, thr=150.0, note="", lw=None,
              local_slope=True, neutral=False):
    """At each x of `at`, the dark runs in that column inside the plot (clear of the axes);
    `pick(runs, x, Y)` returns the index of the run that is the wanted curve (runs sorted top
    to bottom, as (centre row, half height); Y the y axis), or None. With `count`, a column
    whose number of runs differs is not read. r_range: (vmin, vmax) of y to look in.
    neutral: only grey/black ink (leaves out coloured markers)."""
    ax, X, Y = cal["axes"], cal["x"], cal["y"]
    m = neutral_ink(img, thr=thr) if neutral else gray(img) < thr
    r0 = ax["ytop"] + 10
    r1 = ax["xrows"][0] - 12
    if r_range is not None:
        a, b = Y.pixel(r_range[1]), Y.pixel(r_range[0])
        r0, r1 = max(r0, min(a, b)), min(r1, max(a, b))
    out = []
    for x in at:
        c = X.pixel(x)
        ci = int(round(c))
        runs = column_runs(m, ci, r0, r1)
        base = (f"x {X.n} marks misfit {X.misfit:.2f} px; y {Y.n} marks misfit {Y.misfit:.2f} px"
                + (f"; {note}" if note else ""))
        if count is not None and len(runs) != count:
            out.append({"x": x, "y": None, "note": f"{len(runs)} runs in this column, expected {count}; " + base})
            continue
        k = pick(runs, x, Y)
        if k is None or not (-len(runs) <= k < len(runs)):
            out.append({"x": x, "y": None, "note": "curve not separable here; " + base})
            continue
        cen, half = runs[k]
        slope = 0.0
        if local_slope:
            ys = []
            for dc in (-6, 6):
                rr = column_runs(m, ci + dc, cen - 3 * half - 30, cen + 3 * half + 30)
                if rr:
                    ys.append(min(rr, key=lambda q: abs(q[0] - cen))[0])
            if len(ys) == 2:
                slope = (ys[1] - ys[0]) / 12.0
        w = lw if lw is not None else 2 * half / math.sqrt(1 + slope * slope)
        err = max(1.5, 0.25 * w) + max(Y.misfit, 0.5) + abs(slope) * max(X.misfit, 0.5)
        if 2 * half > 2.0 * w * math.sqrt(1 + slope * slope) + 4:
            err = max(err, half)
            base = "run thicker than the line (curves touching): interval spans it; " + base
        y, lo, hi = Y.value(cen), Y.value(cen + err), Y.value(cen - err)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, cen],
                    "px_lo": cen - err, "px_hi": cen + err, "note": base})
    return out


def read_traced(img, cal, at, start_x, start_pick, r_range=None, thr=110.0, neutral=True, note="",
                max_gap=120):
    """Follow one curve column by column from a start column (where `start_pick(runs, Y)` names
    its run) both ways, taking at each column the run nearest the position the recent slope
    predicts; columns where nothing is near (a marker on the curve, a gap) are bridged.
    Then read it at `at` like read_runs."""
    ax, X, Y = cal["axes"], cal["x"], cal["y"]
    m = neutral_ink(img, thr=thr) if neutral else gray(img) < thr
    r0 = ax["ytop"] + 10
    r1 = ax["xrows"][0] - 12
    if r_range is not None:
        a, b = Y.pixel(r_range[1]), Y.pixel(r_range[0])
        r0, r1 = max(r0, min(a, b)), min(r1, max(a, b))
    c0 = int(round(X.pixel(start_x)))
    runs = column_runs(m, c0, r0, r1)
    k = start_pick(runs, Y)
    path = {c0: runs[k]}
    typ = runs[k][1]
    cmin, cmax = int(ax["ycols"][1]) + 15, int(ax["xright"]) - 2
    for step in (1, -1):
        hist = [(c0, runs[k][0])]
        c, gap = c0 + step, 0
        while cmin <= c <= cmax and gap <= max_gap:
            rec = hist[-30:]
            if len(rec) > 4:
                sl, ic = np.polyfit([q[0] for q in rec], [q[1] for q in rec], 1)
                pred = ic + sl * c
            else:
                sl, pred = 0.0, hist[-1][1]
            rs = column_runs(m, c, r0, r1)
            ok = [q for q in rs if abs(q[0] - pred) <= 2 * typ + abs(sl) * (gap + 1) + 3
                  and q[1] <= 1.6 * typ * math.sqrt(1 + sl * sl) + 2]
            if ok:
                best = min(ok, key=lambda q: abs(q[0] - pred))
                path[c] = best
                hist.append((c, best[0]))
                gap = 0
            else:
                gap += 1
            c += step
    out = []
    base = (f"traced from x = {start_x}; x {X.n} marks misfit {X.misfit:.2f} px; y {Y.n} marks misfit "
            f"{Y.misfit:.2f} px" + (f"; {note}" if note else ""))
    for x in at:
        c = X.pixel(x)
        near = sorted(q for q in path if abs(q - c) <= 6)
        if len(near) < 4 or min(abs(q - c) for q in near) > 1.5:
            out.append({"x": x, "y": None, "note": "curve hidden here (marker or arrow on it); " + base})
            continue
        cs = np.array(near, float)
        ys = np.array([path[q][0] for q in near])
        sl, ic = np.polyfit(cs, ys, 1)
        cen = float(ic + sl * c)
        w = 2 * typ
        err = max(1.5, 0.25 * w) + max(Y.misfit, 0.5) + abs(sl) * max(X.misfit, 0.5)
        y, lo, hi = Y.value(cen), Y.value(cen + err), Y.value(cen - err)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, cen],
                    "px_lo": cen - err, "px_hi": cen + err, "note": base})
    return out


# ------------------------------------------------------------------------------ markers


def color_mask(img, kind):
    a = img[..., :3].astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "blue":
        m = (b > r + 35) & (b > g + 25)
    elif kind == "red":
        m = (r > g + 45) & (r > b + 35) & (r < 235)
    elif kind == "green":
        m = (g > r + 35) & (g > b + 15)
    else:
        raise ValueError(kind)
    return ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=2))


def blobs(m, min_area):
    lab, n = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        if len(rr) < min_area:
            continue
        out.append(dict(r0=sl[0].start, r1=sl[0].stop, c0=sl[1].start, c1=sl[1].stop,
                        area=len(rr), mask=(lab[sl] == i)))
    return out


def big_region(img, kind, min_frac=0.02):
    """Bounding box (r0, r1, c0, c1) of the largest blob of a colour when it covers more than
    min_frac of the crop (a colour-map inset), else None."""
    m = color_mask(img, kind)
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    i = int(np.argmax(sizes))
    if sizes[i] < min_frac * m.size:
        return None
    sl = ndimage.find_objects(lab)[i]
    return (sl[0].start, sl[0].stop, sl[1].start, sl[1].stop)


def read_markers(img, cal, kind, occluders=(), min_area=200, exclude_labelled=True, note="",
                 region=None, exclude_inset=None):
    """Markers of one colour, each at its centre. Returns readings sorted by x.
    occluders: colours of other markers that may hide part of these.
    exclude_labelled: drop markers with text (neutral ink) beside them on the right: a legend.
    region: (xmin, xmax, ymin, ymax) in axis values to keep.
    exclude_inset: a colour whose large region (a colour-map inset) is masked out, with a margin.
    Thin blobs (arrows, leader lines: filling under 35% of their box, or thinner than half a
    marker) are not markers."""
    ax, X, Y = cal["axes"], cal["x"], cal["y"]
    m = color_mask(img, kind)
    m[:, : int(ax["ycols"][1]) + 3] = False
    m[int(ax["xrows"][0]) - 2:, :] = False
    if exclude_inset is not None:
        box = big_region(img, exclude_inset)
        if box is not None:
            g = 40
            m[max(0, box[0] - g):box[1] + g, max(0, box[2] - g):box[3] + g] = False
    occ = np.zeros_like(m)
    for k in occluders:
        occ |= color_mask(img, k)
    # a black curve or reference line drawn across a marker cuts it in two: the dark ink next to
    # the marker colour is taken as marker, then thin parts (lines, arrows) are opened away
    line = neutral_ink(img, thr=120.0)
    m = ndimage.binary_fill_holes(m | (line & ndimage.binary_dilation(m, iterations=10)))
    yy, xx = np.mgrid[-5:6, -5:6]
    m = ndimage.binary_opening(m, structure=(xx * xx + yy * yy) <= 25)   # drops lines and arrows
    bl = blobs(m, min_area)
    if bl:
        typ = float(np.median([max(b["r1"] - b["r0"], b["c1"] - b["c0"]) for b in bl]))
        bl = [b for b in bl if b["area"] >= 0.35 * (b["r1"] - b["r0"]) * (b["c1"] - b["c0"])
              and min(b["r1"] - b["r0"], b["c1"] - b["c0"]) >= 0.5 * typ]
    if not bl:
        return []
    sizes = sorted(max(b["r1"] - b["r0"], b["c1"] - b["c0"]) for b in bl)
    d = float(np.percentile(sizes, 60))
    hs = sorted(b["r1"] - b["r0"] for b in bl if b["r1"] - b["r0"] <= 1.15 * d)
    ws = sorted(b["c1"] - b["c0"] for b in bl if b["c1"] - b["c0"] <= 1.15 * d)
    dh, dw = float(np.median(hs[len(hs) // 3:])), float(np.median(ws[len(ws) // 3:]))
    ink = neutral_ink(img, thr=120.0)
    pts = []
    for b in bl:
        h, w = b["r1"] - b["r0"], b["c1"] - b["c0"]
        if h > 1.25 * dh or w > 1.25 * dw:
            # several overlapping markers in a row. The two end markers are placed from the
            # blob's extreme points along its long direction (their outer edges are visible):
            # for a marker of semi-axes (a, b) the centre lies (a^2 ux, b^2 uy)/s inside the
            # extreme point, s = sqrt(a^2 ux^2 + b^2 uy^2). Markers between them are found as
            # maxima of the distance transform away from the ends, with a wide interval.
            rr, cc = np.nonzero(b["mask"])
            P = np.vstack([cc + 0.5, rr + 0.5]).T
            mu = P.mean(axis=0)
            w_, v_ = np.linalg.eigh(np.cov((P - mu).T))
            u = v_[:, np.argmax(w_)]
            t = (P - mu) @ u
            a2, b2 = (dw / 2.0) ** 2, (dh / 2.0) ** 2
            s = math.sqrt(a2 * u[0] ** 2 + b2 * u[1] ** 2)
            off = np.array([a2 * u[0], b2 * u[1]]) / s
            ends = []
            for sel, sign in ((t <= t.min() + 2, 1.0), (t >= t.max() - 2, -1.0)):
                e = P[sel].mean(axis=0) + sign * off
                ends.append((e[1], e[0]))
            dt = ndimage.distance_transform_edt(b["mask"])
            pk = (dt == ndimage.maximum_filter(dt, size=int(0.6 * min(dh, dw)))) & (dt > 0.3 * min(dh, dw))
            lab, n = ndimage.label(pk)
            mids = []
            for (pr, pc) in ndimage.center_of_mass(pk, lab, range(1, n + 1)):
                q = (b["r0"] + pr + 0.5, b["c0"] + pc + 0.5)
                if all(math.hypot(q[0] - (e[0] + b["r0"]), q[1] - (e[1] + b["c0"])) > 0.6 * min(dh, dw) for e in ends) \
                        and all(math.hypot(q[0] - m_[0], q[1] - m_[1]) > 0.5 * min(dh, dw) for m_ in mids):
                    mids.append(q)
            k = 2 + len(mids)
            for e in ends:
                pts.append(dict(r=b["r0"] + e[0], c=b["c0"] + e[1], er=0.08 * dh + 2, ec=0.08 * dw + 2,
                                how=f"end marker of a row of {k} overlapping markers, placed from its outer edge"))
            for q in mids:
                pts.append(dict(r=q[0], c=q[1], er=0.3 * dh, ec=0.3 * dw,
                                how=f"middle marker of a row of {k} overlapping markers (distance-transform peak)"))
            continue
        near_occ = occ[max(0, b["r0"] - 6):b["r1"] + 6, max(0, b["c0"] - 6):b["c1"] + 6].any()
        if b["area"] < (0.2 if near_occ else 0.5) * dh * dw:
            continue    # an arrowhead, or a sliver too small to place
        r = (b["r0"] + b["r1"]) / 2.0
        c = (b["c0"] + b["c1"]) / 2.0
        er, ec, how = 1.5, 1.5, "bounding-box centre"
        if h < 0.85 * dh:
            above = occ[max(0, b["r0"] - 6):b["r0"] + 3, b["c0"]:b["c1"]].any()
            below = occ[b["r1"] - 3:b["r1"] + 6, b["c0"]:b["c1"]].any()
            if above and not below:
                r = b["r1"] - dh / 2.0
            elif below and not above:
                r = b["r0"] + dh / 2.0
            er = 0.1 * dh + 2
            how = "partly hidden: placed from its visible edge"
        if w < 0.85 * dw:
            left = occ[b["r0"]:b["r1"], max(0, b["c0"] - 6):b["c0"] + 3].any()
            right = occ[b["r0"]:b["r1"], b["c1"] - 3:b["c1"] + 6].any()
            if left and not right:
                c = b["c1"] - dw / 2.0
            elif right and not left:
                c = b["c0"] + dw / 2.0
            ec = 0.1 * dw + 2
            how = "partly hidden: placed from its visible edge"
        if exclude_labelled:
            # a legend entry: a text glyph (ink over a good part of the marker's height) just to
            # the right; a dashed or dotted reference line is only a few rows thick
            band = ink[int(r - dh / 2):int(r + dh / 2), int(b["c1"] + 0.3 * dw):int(b["c1"] + 2.5 * dw)]
            if band.size and band.any(axis=1).sum() > 0.35 * dh:
                continue
        pts.append(dict(r=r, c=c, er=er, ec=ec, how=how))
    out = []
    for p in sorted(pts, key=lambda q: q["c"]):
        x, y = X.value(p["c"]), Y.value(p["r"])
        if region is not None and not (region[0] <= x <= region[1] and region[2] <= y <= region[3]):
            continue
        err = p["er"] + max(Y.misfit, 0.5)
        lo, hi = Y.value(p["r"] + err), Y.value(p["r"] - err)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [p["c"], p["r"]],
                    "px_lo": p["r"] - err, "px_hi": p["r"] + err,
                    "note": (f"{kind} marker, {p['how']}; marker {dh:.0f} x {dw:.0f} px; x +-{abs(X.b) * (p['ec'] + max(X.misfit, .5)):.2g}; "
                             f"x {X.n} marks misfit {X.misfit:.2f} px; y {Y.n} marks misfit {Y.misfit:.2f} px"
                             + (f"; {note}" if note else ""))})
    return out
