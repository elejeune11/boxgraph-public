"""Shared figure-reading code for wan2002 (Figs. 1-5). Everything is found in the image.

The panels are black-ink line plots (one solid and one dashed curve) with a left axis, often a
right axis (pressure), and a bottom axis, each with short tick marks drawn outside the axis line.

Calibration (calibrate). Ink is gray < 170. The axis lines are the columns (rows) whose longest
unbroken run of ink exceeds 0.3 of the crop's height (width). The ticks of each axis are found
outside its line (_find_ticks): runs of ink going outward from the line; where the blurred scan
breaks or merges them, the peaks of the darkness profile just beside the line. A label printed at
an axis corner (the first time under the left axis, the lowest value on the bottom axis) has the
other axis line as its tick. Of these candidates, the n that form an evenly spaced row are matched,
in order, to the n printed tick labels each reader passes in (left to right; top to bottom). A
straight line value -> pixel is fitted to each axis and its worst misfit (px) is reported and added
to every interval.

Curves. The ink inside the plot box. The solid curve (solid_path) is the cheapest left-to-right
path through the ink's column runs: steps cost per row of gap between runs, per column skipped,
per row the centre moves and per change of slope, so the path keeps to the unbroken solid line
and through crossings keeps its own direction. Columns it skipped get the run on the straight line
between its ends. The dashed curve is the ink off the solid path (specks dropped), its longest
run per column.

Value at x. The column of x comes from the x calibration. The value is the centre of the curve's
run in that column and the interval is the run (the stroke's thickness, or its length where the
curve is steep). In a gap (between dashes, or a break of the solid line) no wider than max_gap px:
the straight line between the run centres at the gap's ends, with an interval spanning both end
runs. Dashed curves that run along the solid one (Figs. 2-5, hidden_ok): where no dash lies near,
the dashed line is inside the solid stroke, and the value is that stroke widened by a line
thickness each way. Every interval is widened by the y misfit, the x misfit times the local slope
and `pad` px. Pixel sizes are given at 1100 dpi and scaled to the reading's dpi.
"""
import numpy as np
from scipy import ndimage


def dark(image, level=128):
    return image[..., :3].astype(float).mean(axis=2) < level


def groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return out


def _runs(col):
    return [(g[0], g[-1]) for g in groups(np.where(col)[0])]


def _longest(a):
    """Longest run of True along axis 0 of a 2D boolean array, per column."""
    best = np.zeros(a.shape[1], int)
    cur = np.zeros(a.shape[1], int)
    for row in a:
        cur = np.where(row, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def axes_lines(d, frac=0.5):
    """Column groups (vertical lines) and row groups (horizontal lines) whose longest unbroken run
    of ink is longer than frac x 0.6 of the crop."""
    h, w = d.shape
    cols = groups(np.where(_longest(d) > frac * h * 0.6)[0])
    rows = groups(np.where(_longest(d.T) > frac * w * 0.6)[0])
    return rows, cols


def _tick_scan(d, line, side, span, tick_min, tick_max, look):
    out = []
    lo, hi = span
    for i in range(max(0, lo), hi):
        if side == "left":
            edge = line[0] - 1
            seq = d[i, max(0, edge - look): edge + 1][::-1]
        elif side == "right":
            edge = line[-1] + 1
            seq = d[i, edge: edge + look + 1]
        else:
            edge = line[-1] + 1
            seq = d[edge: edge + look + 1, i]
        n = 0
        for v in seq:
            if not v:
                break
            n += 1
        if tick_min <= n <= tick_max:
            out.append(i)
    return [0.5 * (g[0] + g[-1]) for g in groups(out, gap=2)]


def _profile_peaks(g, line, side, span, band, sep):
    """Peaks of the darkness just outside an axis line: mean darkness (0 white .. 1 black) of the
    `band` px beyond the line's outer edge, along the line; ticks are its peaks."""
    from scipy.signal import find_peaks
    lo, hi = max(0, span[0]), min(span[1], g.shape[0] if side != "down" else g.shape[1])
    dk = 1.0 - g / 255.0
    if side == "left":
        e = line[0] - 2
        sig = dk[lo:hi, max(0, e - band): e].mean(axis=1)
    elif side == "right":
        e = line[-1] + 2
        sig = dk[lo:hi, e: e + band].mean(axis=1)
    else:
        e = line[-1] + 2
        sig = dk[e: e + band, lo:hi].mean(axis=0)
    pk, _ = find_peaks(sig, height=0.25, prominence=0.12, distance=max(2, int(sep)))
    return [float(lo + i) for i in pk]


def _regular(cands, n, tol_frac=0.15):
    """The n positions among the candidates that best form an evenly spaced row (the labels are
    evenly spaced values): every pair of candidates and every pair of label indices propose a
    spacing; the proposal that every label index finds a candidate for, with the smallest misfit,
    wins. None if no proposal matches all n."""
    cands = sorted(set(round(c, 1) for c in cands))
    best = None
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            for ia in range(n):
                for ib in range(ia + 1, n):
                    step = (cands[j] - cands[i]) / (ib - ia)
                    if step <= 0:
                        continue
                    start = cands[i] - ia * step
                    pos = []
                    for k in range(n):
                        want = start + k * step
                        c = min(cands, key=lambda q: abs(q - want))
                        if abs(c - want) > tol_frac * step:
                            break
                        pos.append(c)
                    else:
                        if len(set(pos)) < n:
                            continue
                        idx = np.arange(n)
                        a, b = np.polyfit(idx, pos, 1)
                        mis = float(np.abs(a * idx + b - np.asarray(pos)).max())
                        if best is None or mis < best[0]:
                            best = (mis, pos)
    return best[1] if best else None


def _find_ticks(d, g, line, side, span, tick_min, tick_max, n, corners, s):
    """Ticks of one axis, n of them (one per printed label). First the clean way: runs of ink
    tick_min..tick_max px outward from the axis line (or, where the scan blurs a tick into its label,
    up to 4 tick_max), with the axis corners (a label printed at a corner, such as the first time
    under the left axis, has the other axis line as its tick). If that does not give n evenly spaced
    ticks: the peaks of the darkness profile just outside the line, plus the corners, and the n of
    them that best form an evenly spaced row."""
    cs = [c for c in corners if c is not None]
    for look in (tick_max, 4 * tick_max):
        t = _tick_scan(d, line, side, span, tick_min, look, look)
        if len(t) == n and _regular(t, n) is not None:
            return t, "tick marks"
        if len(t) >= n - 2:
            t2 = _regular(t + cs, n)
            if t2 is not None:
                return t2, "tick marks and axis corners"
    pk = _profile_peaks(g, line, side, span, max(4, int(round(7 * s))), 8 * s)
    t = _regular(pk + cs, n)
    if t is None:
        raise ValueError(f"no {n} evenly spaced ticks on the {side} axis: profile peaks at {[round(p) for p in pk]}")
    return t, "darkness peaks beside the axis and axis corners"


def fit(pix, vals, what):
    if len(pix) != len(vals):
        raise ValueError(f"expected {len(vals)} {what} ticks, found {len(pix)} at {[round(p) for p in pix]}")
    pix, vals = np.asarray(pix, float), np.asarray(vals, float)
    a, b = np.polyfit(vals, pix, 1)
    return float(a), float(b), float(np.abs(a * vals + b - pix).max())


def calibrate(image, x_vals, y_left, y_right=None, dpi=1100, tick_min=6, tick_max=45, level=170, frac=0.5,
              x_tick_max=None):
    """x_vals left to right; y_left / y_right: printed labels of the left / right axis, top to bottom.
    Pixel lengths (tick_min, tick_max, x_tick_max) are given at 1100 dpi and scaled to dpi."""
    s = dpi / 1100.0
    tick_min, tick_max = tick_min * s, int(round(tick_max * s))
    x_tick_max = int(round(x_tick_max * s)) if x_tick_max else None
    d = dark(image, level)
    rows, cols = axes_lines(d, frac)
    bottom = rows[-1]
    left = cols[0]
    right = cols[-1] if len(cols) > 1 else None
    top_line = rows[0] if len(rows) > 1 else None
    # vertical extent of the left axis line
    lc = left[len(left) // 2]
    ys = np.where(d[:, lc])[0]
    y0 = int(ys.min())
    cy = [0.5 * (bottom[0] + bottom[-1]), 0.5 * (top_line[0] + top_line[-1]) if top_line else None]
    g = image[..., :3].astype(float).mean(axis=2)
    span_y = (y0 - 5, bottom[-1] + 4)
    yl, how_l = _find_ticks(d, g, left, "left", span_y, tick_min, tick_max, len(y_left), cy, s)
    a_l, b_l, mis_l = fit(yl, y_left, "left y")
    cal = dict(s=s, d=d, bottom=bottom, left=left, right=right, top=top_line, y_top=y0,
               yl=yl, a_l=a_l, b_l=b_l, mis_l=mis_l, how_l=how_l)
    if y_right is not None:
        yr, how_r = _find_ticks(d, g, right, "right", span_y, tick_min, tick_max, len(y_right), cy, s)
        cal.update(yr=yr, how_r=how_r)
        cal["a_r"], cal["b_r"], cal["mis_r"] = fit(yr, y_right, "right y")
    xr = (left[0] - 5, (right[-1] if right else d.shape[1] - 1) + 6)
    cx = [0.5 * (left[0] + left[-1]), 0.5 * (right[0] + right[-1]) if right else None]
    xt, how_x = _find_ticks(d, g, bottom, "down", xr, tick_min, x_tick_max or tick_max, len(x_vals), cx, s)
    cal["xt"], cal["how_x"] = xt, how_x
    cal["a_x"], cal["b_x"], cal["mis_x"] = fit(xt, x_vals, "x")
    return cal


def note(cal, side):
    m = cal["mis_l"] if side == "left" else cal["mis_r"]
    n = len(cal["yl"]) if side == "left" else len(cal["yr"])
    how = cal["how_l"] if side == "left" else cal["how_r"]
    return (f"calibrated on {len(cal['xt'])} x ticks ({cal['how_x']}) and {n} {side} y ticks ({how}); "
            f"misfit x {cal['mis_x']:.1f} px, y {m:.1f} px")


def ink(cal, inset=6, min_area=25):
    """Dark ink inside the plot box (axis lines and outward ticks excluded), specks dropped.
    inset (px) and min_area (px^2) are given at 1100 dpi and scaled."""
    d = cal["d"]
    inset = int(round(inset * cal["s"]))
    min_area = min_area * cal["s"] ** 2
    h, w = d.shape
    box = np.zeros_like(d)
    r1 = cal["bottom"][0] - inset
    r0 = (cal["top"][-1] + inset) if cal["top"] else max(0, cal["y_top"] - 2)
    c0 = cal["left"][-1] + inset
    c1 = (cal["right"][0] - inset) if cal["right"] else w
    box[r0:r1, c0:c1] = True
    return _drop_specks(d & box, min_area)


def _drop_specks(m, min_area):
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    if n == 0:
        return m
    area = ndimage.sum(m, lab, index=np.arange(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = area >= min_area
    return keep[lab]


def _dist(r, p):
    """Distance (rows) from row p to the run r; 0 inside it."""
    return 0.0 if r[0] <= p <= r[1] else min(abs(r[0] - p), abs(r[1] - p))


def solid_path(m, s=1.0, w_row=1.0, w_col=3.0, w_centre=0.05, w_slope=2.0, max_skip=40):
    """The solid curve as the cheapest left-to-right path through the runs of ink, one run per
    column. A step from a run in an earlier ink column (at most max_skip px back, scaled by s) to a
    run in this one costs w_row per row of gap between the runs, w_col per column skipped, w_centre
    per row the centre moves and w_slope per px/column the step's slope differs from the path's
    slope so far (smoothed); entering after the first or leaving before the last ink column costs
    w_col per column. The solid line has few and short breaks, so it is the cheap path; a path that
    turns onto a dash at a crossing pays for the turn and then for the dash's gaps."""
    w = m.shape[1]
    cs = [c for c in range(w) if m[:, c].any()]
    if not cs:
        return {}
    runs = [_runs(m[:, c]) for c in cs]
    cen = [[0.5 * (r[0] + r[1]) for r in rr] for rr in runs]
    first, last = cs[0], cs[-1]
    K = max(2, int(round(max_skip * s)))
    cost, back, slope = [], [], []
    for k in range(len(cs)):
        ck, bk, sk = [], [], []
        for j, r in enumerate(runs[k]):
            best, arg, sl = w_col * (cs[k] - first), None, 0.0
            kk = k - 1
            while kk >= 0 and cs[k] - cs[kk] <= K:
                dcol = cs[k] - cs[kk]
                for i, q in enumerate(runs[kk]):
                    gap = max(0, r[0] - q[1] - 1, q[0] - r[1] - 1)
                    dc = cen[k][j] - cen[kk][i]
                    inst = dc / dcol
                    v = (cost[kk][i] + w_row * gap + w_col * (dcol - 1) + w_centre * abs(dc)
                         + w_slope * abs(inst - slope[kk][i]))
                    if v < best:
                        best, arg, sl = v, (kk, i), 0.8 * slope[kk][i] + 0.2 * inst
                kk -= 1
            ck.append(best)
            bk.append(arg)
            sk.append(sl)
        cost.append(ck)
        back.append(bk)
        slope.append(sk)
    k, j = min(((k, j) for k in range(len(cs)) for j in range(len(runs[k]))),
               key=lambda t: cost[t[0]][t[1]] + w_col * (last - cs[t[0]]))
    out = {}
    while True:
        out[cs[k]] = runs[k][j]
        if back[k][j] is None:
            break
        k, j = back[k][j]
    # columns the path skipped: the run that the straight line between the path's ends passes
    # through (or comes within a line thickness of) belongs to the solid curve too
    thick = float(np.median([b - a + 1 for a, b in out.values()]))
    pc = sorted(out)
    rk = dict(zip(cs, runs))
    for c1, c2 in zip(pc, pc[1:]):
        if c2 - c1 < 2:
            continue
        m1, m2 = 0.5 * sum(out[c1]), 0.5 * sum(out[c2])
        for c in range(c1 + 1, c2):
            if c not in rk:
                continue
            want = m1 + (m2 - m1) * (c - c1) / (c2 - c1)
            r = min(rk[c], key=lambda q: _dist(q, want))
            if _dist(r, want) <= thick:
                out[c] = r
    return out


def _value(cal, side, row):
    a, b = (cal["a_l"], cal["b_l"]) if side == "left" else (cal["a_r"], cal["b_r"])
    return (row - b) / a


def _slope(tr, c, k=8):
    l, r = tr.get(c - k), tr.get(c + k)
    if l is None or r is None:
        return 0.0
    return abs(0.5 * (r[0] + r[1]) - 0.5 * (l[0] + l[1])) / (2 * k)


def read_curve(image, at, cal, which, side, pad=2.0, max_gap=60, hidden_ok=False, **mask_kw):
    """which: 'solid' or 'dashed'; side: 'left' or 'right' axis for the values. pad and max_gap
    (px) are given at 1100 dpi and scaled.

    hidden_ok (dashed only): where no dash lies within max_gap/2 of x's column, the dashed curve is
    taken to run inside the solid stroke (the two coincide; used only for panels where the image
    shows the dashed line running along the solid one). The value is then the solid run's centre and
    the interval the solid run widened by one line thickness each way."""
    pad, max_gap = pad * cal["s"], max_gap * cal["s"]
    m = ink(cal, **mask_kw)
    mis_y = cal["mis_l"] if side == "left" else cal["mis_r"]
    out = []
    st = solid_path(m, cal["s"])
    if which == "solid":
        tr = st
    else:
        # the dashed curve: the ink off the solid path (where the two touch, the dash is lost there)
        dashed = m.copy()
        for c, (a, b) in st.items():
            dashed[a:b + 1, c] = False
        dashed = _drop_specks(dashed, mask_kw.get("min_area", 25) * cal["s"] ** 2)
        # one run per column, the longest (the dashed curve is a function of time)
        tr = {}
        for c in range(dashed.shape[1]):
            r = _runs(dashed[:, c])
            if r:
                tr[c] = max(r, key=lambda q: q[1] - q[0])
    cols = sorted(tr)
    for x in at:
        cf = cal["a_x"] * x + cal["b_x"]
        c = int(round(cf))
        if c in tr:
            r0, r1 = tr[c]
            rc = 0.5 * (r0 + r1)
            how = f"{which} curve run in column {c}"
        elif cols:
            lefts = [q for q in cols if q < c]
            rights = [q for q in cols if q > c]
            if (not lefts or not rights or rights[0] - lefts[-1] > max_gap) and hidden_ok and c in st:
                thick = float(np.median([b - a + 1 for a, b in st.values()]))
                r0, r1 = st[c][0] - thick, st[c][1] + thick
                rc = 0.5 * (st[c][0] + st[c][1])
                how = (f"no dash within the gap around column {c}: the dashed line runs inside the solid stroke "
                       f"(run widened by the line thickness, {thick:.0f} px)")
                p = pad + mis_y + _slope(st, c) * cal["mis_x"]
                lo_r, hi_r = r0 - p, r1 + p
                v1, v2 = _value(cal, side, lo_r), _value(cal, side, hi_r)
                out.append({"x": x, "y": _value(cal, side, rc), "lo": min(v1, v2), "hi": max(v1, v2),
                            "px": [cf, rc], "px_lo": lo_r, "px_hi": hi_r, "note": f"{how}; " + note(cal, side)})
                continue
            if not lefts or not rights or rights[0] - lefts[-1] > max_gap:
                out.append({"x": x, "y": None, "note": f"no {which} curve near column {c}"})
                continue
            cl, cr = lefts[-1], rights[0]
            ml, mr = 0.5 * sum(tr[cl]), 0.5 * sum(tr[cr])
            rc = ml + (mr - ml) * (c - cl) / (cr - cl)
            r0 = min(tr[cl][0], tr[cr][0], rc)
            r1 = max(tr[cl][1], tr[cr][1], rc)
            how = f"gap between dashes, columns {cl}-{cr}, interpolated"
        else:
            out.append({"x": x, "y": None, "note": f"no {which} curve in column {c}"})
            continue
        p = pad + mis_y + _slope(tr, c) * cal["mis_x"]
        lo_r, hi_r = r0 - p, r1 + p
        v1, v2 = _value(cal, side, lo_r), _value(cal, side, hi_r)
        out.append({"x": x, "y": _value(cal, side, rc), "lo": min(v1, v2), "hi": max(v1, v2),
                    "px": [cf, rc], "px_lo": lo_r, "px_hi": hi_r,
                    "note": f"{how}; " + note(cal, side)})
    return out
