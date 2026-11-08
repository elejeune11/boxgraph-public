"""Shared reading code for the waveform figures of mynard2014 (Figs. 3-10, PDF pp. 45-52).

The figure pages are raster images (blurred black ink on white, some curves in light grey), so
every crop is an upsampled raster. One panel per crop.

Calibration, all from the image:
  axes      the y axis is the column group with the longest dark vertical runs in the left half of
            the crop; the x axis is the row group with the longest dark horizontal runs in the lower
            half. The plot box runs from the y axis to the right end of the x axis line, and from the
            top of the y axis line to the x axis.
  y ticks   short dark runs (at most `tick_max` px) standing off the y axis on the side given by
            `ytick` ("in" = into the plot, "out" = to the left), in groups no taller than 4 axis
            widths. They are matched in order, top to bottom, to the printed labels in the spec (the
            evenly spaced subset with the smallest straight-line misfit, so a curve touching the axis
            near a tick is ignored), fitted by a straight line, and the largest misfit is reported
            and added to every interval.
  x ticks   the same on the x axis, when the panel has labelled x ticks (spec "x"). Panels without
            any x tick (Figs. 6-9) are read on the fraction of the plotted interval: 0 at the centre
            of the y axis line, 1 at the right end of the x axis line (the curves span exactly that
            width). This is stated in each reading's `what`.

Curves, told apart by ink:
  black     ink darker than 128 (of 255) inside the plot box, the axis lines and ticks removed, and
            the boxes in spec "mask" (panel letters, labels and their leader lines; fractions of the
            plot box) blanked.
  solid     the black components wider than `long` x the plot width (the continuous line; dashes
            that touch it are part of it there).
  dashed    the other black components larger than `min_dash` px.
  grey      ink between 120 and 225 that is more than `grey_gap` px from black ink, opened to remove
            the antialiased rims of black lines.
Each curve is traced column by column from the left: the run touching the previous column's run,
or the run nearest a straight-line prediction from the previous 12 columns. The dashed curve is
followed from dash to dash; across a gap of at most `max_gap` columns its centre is interpolated
between the facing dash ends; where no dash is drawn for longer, the dashes lie inside the solid
line ("fused") and the dashed curve is somewhere inside the solid line's run. A grey curve that
disappears under black ink is likewise somewhere inside the black run there ("hidden").

Options in a reading's SPEC (all layout, none a value read from the paper except the tick labels):
  open      diameter (px) of a disk opening that keeps the thicker solid line and drops the thinner
            dashes before the solid line is picked out (Figs. 7-8, where the solid line is thicker).
  mask      boxes blanked (panel letters, curve labels, arrows and leader lines).
  yband     keep only ink between two values of the y axis, to separate two curves of one style
            where they stand apart (the CEP midwall and subepicardial lines of Fig. 3).
  side      keep only the dash ink above or below the traced solid line (the two branches of the
            dashed pressure-area loop of Fig. 10A).
  subpanel  a row of panels inside one box that share the y axis (Fig. 6): panel k lies between the
            k-th and (k+1)-th vertical box line, the box lines are removed, and x runs from 0 to 1
            between the two lines' centres.
  max_gap, min_dash, reach, grey_gap: dash pattern and line-rim sizes for the figure at hand.
A curve that touches the top or bottom of the plot box at a position is not read there (it may be
clipped).

Intervals (95%): a clean run of about the line's thickness h = w sqrt(1 + slope^2) (w measured on
the image as the median run of the curve) gives its centre +- 2 px; a thicker run (another line
fused to it) gives the centre anywhere from h/2 inside one end to h/2 inside the other, +- 2 px; a
dash gap gives the interpolated centre +- max(8 px, a quarter of the rise across the gap); a fused
or hidden reading spans the whole covering run. The y calibration misfit, the x calibration misfit
times the local slope, and 1 px are added; on an x axis without ticks the x "misfit" is the
uncertainty of the panel's ends, half the axis (or box) line's width plus 2 px. A
reading whose interval is wider than `max_px` is reported as unreadable.
"""

import itertools

import numpy as np
from scipy import ndimage


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    r = _runs(v)
    return max(r, key=lambda x: x[1] - x[0]) if r else (0, 0)


def _group(idx):
    """Contiguous groups of sorted integer positions."""
    out, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            out.append(cur)
            cur = []
        cur.append(int(i))
    if cur:
        out.append(cur)
    return out


def axes(dark):
    H, W = dark.shape
    cl = np.array([(lambda r: r[1] - r[0])(_longest(dark[:, j])) for j in range(W // 2)])
    cols = np.flatnonzero(cl > 0.85 * cl.max())
    yg = _group(cols)[0]
    rl = np.array([(lambda r: r[1] - r[0])(_longest(dark[i])) for i in range(H)])
    rl[: H // 2] = 0
    rows = np.flatnonzero(rl > 0.85 * rl.max())
    xg = _group(rows)[-1]
    la, lb = yg[0], yg[-1]
    ba, bb = xg[0], xg[-1]
    # the axis lines' partly dark edge columns and rows belong to them too
    while lb + 1 < len(cl) and cl[lb + 1] > 0.3 * cl.max():
        lb += 1
    while ba - 1 > 0 and rl[ba - 1] > 0.3 * rl.max():
        ba -= 1
    top = min(_longest(dark[:, j])[0] for j in yg)
    xend = max(_longest(dark[i])[1] for i in xg)
    return {"la": la, "lb": lb, "ba": ba, "bb": bb, "top": top, "xend": xend, "aw": lb - la + 1}


def _tick_cands(lengths, off, aw, tmax):
    cands = []
    nz = [i for i, n in enumerate(lengths) if n > 1]
    for g in _group(nz):
        m = max(lengths[i] for i in g)
        if 4 <= m <= tmax and len(g) <= 4 * aw + 4:
            cands.append(off + (g[0] + g[-1]) / 2.0)
    return cands


def _inward(line):
    n = 0
    while n < len(line) and line[n]:
        n += 1
    return n


def _match(cands, labels, what):
    """The candidates that match the labels in order with the smallest straight-line misfit. One
    label may have no tick found (hidden under a curve that touches the axis there), if at least
    three others do."""
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
            if mis <= 6.0 and (best is None or (k > 0, mis) < (best[4] > 0, best[2])):
                best = (a, b, mis, list(sub), k)
    if best is None:
        raise ValueError(f"{what}: no evenly spaced set of ticks among {cands} for {labels}")
    return best[:4]


def calibrate(dark, spec):
    ax = axes(dark)
    la, lb, ba, bb, top, aw = ax["la"], ax["lb"], ax["ba"], ax["bb"], ax["top"], ax["aw"]
    tmax = spec.get("tick_max", 30)
    if spec.get("ytick", "in") == "in":
        yl = [_inward(dark[r, lb + 1:]) for r in range(top, ba)]
    else:
        yl = [_inward(dark[r, :la][::-1]) for r in range(top, ba)]
    yc = _tick_cands(yl, top, aw, tmax)
    ya, yb, ym, yt = _match(yc, spec["y"], "y axis")
    if spec.get("x"):
        if spec.get("xtick", "in") == "in":
            xl = [_inward(dark[:ba, c][::-1]) for c in range(lb + 1, ax["xend"])]
        else:
            xl = [_inward(dark[bb + 1:, c]) for c in range(lb + 1, ax["xend"])]
        xc = _tick_cands(xl, lb + 1, aw, tmax)
        if spec.get("x0_on_axis"):
            xc = [(la + lb) / 2.0] + xc  # the first label sits on the y axis line itself
        xa, xb, xm, xt = _match(xc, spec["x"], "x axis")
    else:
        c0, c1 = (la + lb) / 2.0, ax["xend"] - 0.5
        xb = 1.0 / (c1 - c0)
        # no ticks to fit: the ends are known to within half the axis line's width and 2 px of blur
        xa, xm, xt = -c0 * xb, aw / 2.0 + 2.0, [c0, c1]
    return {**ax, "y": (ya, yb, ym, yt), "x": (xa, xb, xm, xt)}


def masks(image, spec):
    g = image[..., :3].astype(float).mean(axis=2)
    dark = g < 128
    cal = calibrate(dark, spec)
    H, W = dark.shape
    top, ba, lb, xend = cal["top"], cal["ba"], cal["lb"], cal["xend"]
    tm = spec.get("tick_max", 30)
    inside = np.zeros_like(dark)
    r0 = top + (0 if spec.get("ytick", "in") == "out" else 0)
    inside[r0:ba - 1, lb + 1:xend] = True
    # tick marks off the axes
    if spec.get("ytick", "in") == "in":
        for r in cal["y"][3]:
            inside[int(r) - 3 * cal["aw"]:int(r) + 3 * cal["aw"], lb + 1:lb + 2 + tm] = False
    if spec.get("x") and spec.get("xtick", "in") == "in":
        for c in cal["x"][3]:
            inside[ba - 2 - tm:ba, int(c) - 3 * cal["aw"]:int(c) + 3 * cal["aw"]] = False
    pw, ph = xend - (lb + 1), ba - r0
    for f0, g0, f1, g1 in spec.get("mask", []):
        inside[int(r0 + g0 * ph):int(r0 + g1 * ph), int(lb + 1 + f0 * pw):int(lb + 1 + f1 * pw)] = False
    c0, c1 = lb + 1, xend
    if "yband" in spec:
        # two curves of the same style, apart in value over the positions read: keep only ink
        # between these two values (axis units), so the other curve is not seen
        ya_, yb_ = cal["y"][0], cal["y"][1]
        ra, rb = sorted(((v - ya_) / yb_ for v in spec["yband"]))
        band = np.zeros_like(inside)
        band[max(int(ra), 0):int(rb) + 1, :] = True
        inside &= band
    if "subpanel" in spec:
        # a row of panels sharing the y axis, inside one box (Fig. 6): the box lines and the
        # vertical separators are the long dark rows and columns; panel k lies between the k-th
        # and (k+1)-th vertical line, and its x runs from 0 to 1 between their centres
        cl = np.array([(lambda r: r[1] - r[0])(_longest(dark[:, j])) for j in range(W)])
        vg = _group(np.flatnonzero(cl > 0.85 * cl.max()))
        rl = np.array([(lambda r: r[1] - r[0])(_longest(dark[i])) for i in range(H)])
        for i in np.flatnonzero(rl > 0.5 * W):
            inside[max(i - 2, 0):i + 3, :] = False
        for g in vg:
            inside[:, max(g[0] - 2, 0):g[-1] + 3] = False
        k = spec["subpanel"]
        ga, gb = vg[k], vg[k + 1]
        ca, cb = (ga[0] + ga[-1]) / 2.0, (gb[0] + gb[-1]) / 2.0
        xb = 1.0 / (cb - ca)
        cal["x"] = (-ca * xb, xb, (gb[-1] - gb[0] + 1) / 2.0 + 2.0, [ca, cb])
        c0, c1 = ga[-1] + 3, gb[0] - 2
        lim = np.zeros_like(inside)
        lim[:, c0:c1] = True
        inside &= lim
        pw = c1 - c0
    black = dark & inside
    thick = black
    if spec.get("open"):
        rr = spec["open"] / 2.0
        yy, xx = np.mgrid[-int(rr):int(rr) + 1, -int(rr):int(rr) + 1]
        thick = ndimage.binary_opening(black, structure=(xx * xx + yy * yy) <= rr * rr)
    lab, n = ndimage.label(thick, structure=np.ones((3, 3)))
    sl = ndimage.find_objects(lab)
    long_ = np.zeros(n + 1, bool)
    for k, s in enumerate(sl, start=1):
        if s[1].stop - s[1].start >= spec.get("long", 0.2) * pw:
            long_[k] = True
    solid = long_[lab] & thick
    rest = black & ~ndimage.binary_dilation(solid, iterations=spec.get("dash_gap", 3))
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    sizes = ndimage.sum(rest, lab, index=np.arange(1, n + 1)) if n else np.array([])
    dash = np.concatenate([[False], sizes >= spec.get("min_dash", 60)])[lab] & rest
    grey = None
    if spec.get("curve") == "grey":
        gg = (g > 120) & (g < 225) & inside
        gg &= ~ndimage.binary_dilation(dark, iterations=spec.get("grey_gap", 6))
        gg = ndimage.binary_opening(gg, structure=np.ones((5, 5)))
        gl, gn = ndimage.label(gg, structure=np.ones((3, 3)))
        if gn:
            gs = ndimage.sum(gg, gl, index=np.arange(1, gn + 1))
            gg = np.concatenate([[False], gs >= spec.get("min_grey", 400)])[gl]
        grey = gg
    return {"cal": cal, "black": black, "solid": solid, "dash": dash, "grey": grey, "c0": c0, "c1": c1}


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


def trace_line(mask, c0, c1, tol=40.0, start=None):
    """A continuous line: per column (run, 'line') or (pred, 'lost')."""
    out, hist, prev, lost = {}, [], None, 0
    for c in range(c0, c1):
        runs = _runs(mask[:, c])
        pred = _predict(hist, c)
        if prev is None and pred is None:
            if not runs:
                continue
            run = max(runs, key=lambda r: r[1] - r[0]) if start is None else _nearest(runs, start)[0]
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


def refine(m, solid_tr, spec):
    """Only the traced solid line is solid: dash ink fused to the thick component off the traced
    run goes back to the dashes."""
    traced = np.zeros_like(m["black"])
    for c, e in solid_tr.items():
        if e[1] == "line":
            traced[e[0][0]:e[0][1], c] = True
    rest = m["black"] & ~ndimage.binary_dilation(traced, iterations=spec.get("dash_gap", 3))
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    sizes = ndimage.sum(rest, lab, index=np.arange(1, n + 1)) if n else np.array([])
    m["dash"] = np.concatenate([[False], sizes >= spec.get("min_dash", 60)])[lab] & rest
    m["solid"] = traced
    side = spec.get("side")
    if side:
        # a dashed loop around the solid line (Fig. 10A): keep the dash ink on one side of it
        keep = np.zeros_like(m["dash"])
        for c, e in solid_tr.items():
            if e[1] == "line":
                if side == "above":
                    keep[:e[0][0], c] = True
                else:
                    keep[e[0][1]:, c] = True
        m["dash"] &= keep
    return m


def _dash_components(m, reach):
    """Each dash: its column span, the centre row of its end columns, and whether each end runs
    into the solid line (within `reach` px of solid ink)."""
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
    """The dashed curve, from dash to dash (see the module docstring)."""
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
                # a dash coming out from under the solid line: the one nearest that line
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
                ok = d <= 60 or k == last or len(runs) == 1  # a lone dash is the dashed line
            if ok:
                out[c] = ((a, b), "line")
                hist.append((c, _mid((a, b))))
                last = k
                continue
        L = comps.get(last)
        ahead = [kk for kk, v in comps.items() if c < v["cmin"] <= c + horizon]
        R = None
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
            # no dash drawn here: the dashed line is under the black ink around the solid line
            # (any black run within `reach` px of the solid line's run, since a dash ends that close)
            bl = [r for r in _runs(m["black"][:, c]) if r[0] <= s[0][1] + reach and r[1] >= s[0][0] - reach]
            bl = bl or [s[0]]
            out[c] = ((min(r[0] for r in bl), max(r[1] for r in bl)), "fused")
            continue
        out[c] = (pred, "lost")
    return out


def trace_grey(m, edge=150, near=40):
    """The grey line (the only grey ink): where grey ink is seen, its run (the one continuing the
    previous column's, else the longest); where none is seen, the grey line is under black ink, and
    the black run nearest the straight line between the grey seen on either side (or the grey seen
    on one side, within `edge` columns of the plot edge) holds it."""
    grey, black, c0, c1 = m["grey"], m["black"], m["c0"], m["c1"]
    seen = {}
    prev = None
    for c in range(c0, c1):
        runs = [r for r in _runs(grey[:, c]) if r[1] - r[0] >= 3]
        if not runs:
            prev = None
            continue
        if prev is not None:
            run, d = _nearest(runs, _mid(prev))
            if d > near:
                run = max(runs, key=lambda r: r[1] - r[0])
        else:
            run = max(runs, key=lambda r: r[1] - r[0])
        seen[c] = run
        prev = run
    cols = sorted(seen)
    out = {c: (r, "line") for c, r in seen.items()}
    if not cols:
        return out
    import bisect
    for c in range(c0, c1):
        if c in seen:
            continue
        i = bisect.bisect_left(cols, c)
        cl = cols[i - 1] if i > 0 else None
        cr = cols[i] if i < len(cols) else None
        if cl is not None and cr is not None:
            yl, yr = _mid(seen[cl]), _mid(seen[cr])
            pred = yl + (yr - yl) * (c - cl) / (cr - cl)
        elif cl is not None and c - cl <= edge:
            pred = _mid(seen[cl])
        elif cr is not None and cr - c <= edge:
            pred = _mid(seen[cr])
        else:
            out[c] = (None, "lost")
            continue
        runs = [r for r in _runs(black[:, c]) if r[1] - r[0] >= 3]
        b, d = _nearest(runs, pred) if runs else (None, None)
        # under the only black run in the column, or under the black run near the prediction
        ok = b is not None and (d <= near or (len(runs) == 1 and d <= 3 * near))
        out[c] = (b, "hidden") if ok else (None, "lost")
    return out


def width(tr, cols):
    ls = [tr[c][0][1] - tr[c][0][0] for c in cols if tr[c][1] == "line"]
    return float(np.median(ls)) if ls else 10.0


def read_spec(image, at, spec):
    m = masks(image, spec)
    cal = m["cal"]
    xa, xb, xm, _ = cal["x"]
    ya, yb, ym, _ = cal["y"]
    solid_tr = trace_line(m["solid"], m["c0"], m["c1"], start=None)
    curve = spec.get("curve", "solid")
    if curve == "solid":
        tr = solid_tr
    elif curve == "dashed":
        m = refine(m, solid_tr, spec)
        tr = trace_dashed(m, solid_tr, spec.get("max_gap", 35), spec.get("reach", 30.0))
    else:
        tr = trace_grey(m)
    cen = {}
    for c, e in tr.items():
        if e[1] in ("line", "fused", "hidden"):
            cen[c] = _mid(e[0])
        elif e[1] == "gap":
            cen[c] = float(e[0])
    w = width(tr, list(tr))
    max_px = spec.get("max_px", 160)
    out = []
    for x in at:
        c = int(round((x - xa) / xb))
        e = tr.get(c)
        if e is None or e[1] == "lost" or e[0] is None:
            out.append({"x": x, "y": None, "note": "curve not found here (outside the trace or lost)"})
            continue
        ks = [k for k in range(c - 8, c + 9) if k in cen]
        slope = abs(np.polyfit(ks, [cen[k] for k in ks], 1)[0]) if len(ks) >= 3 else 0.0
        h = w * np.sqrt(1.0 + slope * slope)
        state = e[1]
        if state == "gap":
            yc = float(e[0])
            half = max(8.0, 0.25 * e[2])
            lo, hi = yc - half, yc + half
        else:
            a, b = e[0][0], e[0][1] - 1
            if a <= cal["top"] + 1 or b >= cal["ba"] - 3:
                out.append({"x": x, "y": None, "note": f"{state}: the line runs into the plot edge here (may be clipped)"})
                continue
            if state == "hidden":
                # the grey line's centre may lie just beside the black run: its visible ink within
                # `grey_gap` px of black ink was removed with the black lines' rims
                ext = spec.get("grey_gap", 6) + w / 2.0
                lo, hi = a - ext, b + ext
            elif state == "fused":
                lo, hi = float(a), float(b)
            elif b - a <= h + 6:
                yc = (a + b) / 2.0
                lo, hi = yc - 2.0, yc + 2.0
            else:
                lo, hi = a + h / 2.0 - 2.0, b - h / 2.0 + 2.0
                if hi < lo:
                    lo, hi = (a + b) / 2.0 - 2.0, (a + b) / 2.0 + 2.0
        yc = (lo + hi) / 2.0
        pad = ym + xm * slope + 1.0
        lo, hi = lo - pad, hi + pad
        if hi - lo > max_px:
            out.append({"x": x, "y": None, "note": f"{state}: interval {hi - lo:.0f} px, too wide to read"})
            continue
        v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
        out.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; line {w:.0f} px; x misfit {xm:.1f} px, y misfit {ym:.1f} px"})
    return out

