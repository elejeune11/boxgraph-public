"""Shared reading code for the figures of diab2013 (Proc. R. Soc. A 469, 20120753).

The figures are bitmaps embedded in the PDF; rendered at 1200 dpi their lines are blurred over a
few pixels but clean (black on white, no scan noise).

Calibration (`calibrate`), all from the image:
- the x axis is the longest dark row in the lower part of the crop, the y axis the longest dark
  column in its left part (each a band a few pixels thick);
- tick marks stick out of the axes outwards: on the x axis they hang below the axis band, on the y
  axis they stick out left of it. The columns (rows) where a short band just outside the axis is
  mostly dark are grouped into ticks; the y axis's own continuation below the x axis counts as the
  first x tick, and the x axis's continuation left of the y axis as the lowest y tick, when they
  stick out.
- the ticks, sorted, are matched one to one to the printed tick labels the caller passes (the
  labels seen on the figure); a linear (or log10) fit gives the axis, and its largest residual in
  pixels is the calibration misfit.

Curves (`stroke_mask`, `local_fit`): the ink is thresholded at grey 128 and opened with a square
of side `open_px`, which removes thin dotted guide lines, thin tick marks and hairlines but keeps
the plotted curves (about twice as thick). At each x position the caller picks, from the runs of
that mask in the columns within +-`win` pixels, the ones that belong to the wanted curve; the
centres of those runs are fitted with a straight line, in row(col) where the curve is shallow and
in col(row) where it is steep, and evaluated at the column of x.

Interval (95%): half the line thickness measured along the y axis (thickness / cos of the local
angle), plus the calibration misfit of both axes (the x misfit carried through the local slope),
plus twice the rms residual of the local fit.
"""
import math

import numpy as np


def groups(idx, gap=1):
    out = []
    for c in idx:
        c = int(c)
        if out and c - out[-1][-1] <= gap:
            out[-1].append(c)
        else:
            out.append([c])
    return out


def dark(image, thr=128):
    gray = image.astype(float).mean(axis=2) if image.ndim == 3 else image.astype(float)
    return gray < thr


class Axis:
    def __init__(self, pix, vals, scale="linear"):
        self.scale = scale
        u = np.log10(vals) if scale == "log10" else np.asarray(vals, float)
        p = np.asarray(pix, float)
        self.b, self.a = np.polyfit(p, u, 1)
        self.misfit = float(max(np.max(np.abs(p - (u - self.a) / self.b)), 0.5))
        self.pix, self.vals = list(p), list(vals)

    def val(self, p):
        u = self.a + self.b * p
        return 10.0**u if self.scale == "log10" else u

    def pix_of(self, v):
        u = math.log10(v) if self.scale == "log10" else v
        return (u - self.a) / self.b


def calibrate(dk, x_labels, y_labels, x_scale="linear", y_scale="linear", tick_len=(4, 30),
              y_axis_region=None, x_axis_region=None, top=0, x_side="out"):
    """Find the axes and their ticks, and match them to the printed labels (sorted)."""
    H, W = dk.shape
    # x axis: longest dark row in the lower part
    r0 = int(0.4 * H) if x_axis_region is None else x_axis_region[0]
    r1 = H if x_axis_region is None else x_axis_region[1]
    frac = dk[r0:r1].mean(1)
    rows = np.where(frac > 0.85 * frac.max())[0] + r0
    xa = max(groups(rows), key=len)
    # grow the band over the axis line's blurred edges
    full = dk.mean(1)
    while xa[-1] + 1 < H and full[xa[-1] + 1] > 0.5 * full[xa[-1]]:
        xa = xa + [xa[-1] + 1]
    while xa[0] - 1 >= 0 and full[xa[0] - 1] > 0.5 * full[xa[0]]:
        xa = [xa[0] - 1] + xa
    # y axis: longest dark column in the left part (above the x axis)
    c0 = 0 if y_axis_region is None else y_axis_region[0]
    c1 = int(0.5 * W) if y_axis_region is None else y_axis_region[1]
    fc = dk[top:xa[0], c0:c1].mean(0)
    cols = np.where(fc > 0.85 * fc.max())[0] + c0
    ya = max(groups(cols), key=len)
    # the extent of the axes
    xrow = xa[len(xa) // 2]
    xc = np.where(dk[xrow])[0]
    x_end = max(g[-1] for g in groups(xc, 3) if g[0] <= ya[-1] + 2)
    ycol = ya[len(ya) // 2]
    yr = np.where(dk[:, ycol])[0]
    y_top = min(g[0] for g in groups(yr, 3) if g[-1] >= xa[0] - 2)
    # x ticks: below the x axis band
    lo, hi = tick_len
    if x_side == "out":
        band = dk[xa[-1] + 1 + lo:xa[-1] + 1 + hi, ya[0] - 30:x_end + 3].mean(0)
    else:  # ticks standing up inside the plot
        band = dk[xa[0] - hi:xa[0] - lo, ya[0] - 30:x_end + 3].mean(0)
    xt = [float(np.mean(g)) + ya[0] - 30 for g in groups(np.where(band > 0.7)[0]) if len(g) <= 40]
    if len(xt) > len(x_labels):
        # an extra mark (a labelled point on the axis): keep the evenly spaced ticks
        from boxgraph.digitize import regular_ticks
        xt = regular_ticks(xt, tol=3.0)
    # y ticks: left of the y axis band
    band = dk[y_top - 3:xa[-1] + 30, ya[0] - hi:ya[0] - lo].mean(1)
    yt = [float(np.mean(g)) + y_top - 3 for g in groups(np.where(band > 0.7)[0]) if len(g) <= 40]
    if len(xt) != len(x_labels) or len(yt) != len(y_labels):
        raise ValueError(f"ticks found x {[round(v) for v in xt]} y {[round(v) for v in yt]}; "
                         f"labels x {x_labels} y {y_labels}")
    xs = sorted(xt)
    ys = sorted(yt, reverse=True)  # rows grow downwards; labels ascend upwards
    xax = Axis(xs, sorted(x_labels), x_scale)
    yax = Axis(ys, sorted(y_labels), y_scale)
    return dict(x=xax, y=yax, x_row=(xa[0], xa[-1]), y_col=(ya[0], ya[-1]), x_end=x_end, y_top=y_top)


def open_mask(dk, k):
    """Binary opening with a k x k square (erosion then dilation), numpy only."""
    from scipy import ndimage
    st = np.ones((k, k), bool)
    return ndimage.binary_opening(dk, structure=st)


def drop_small(mask, min_area):
    """Remove connected pieces smaller than min_area pixels (dots of chain lines, serifs)."""
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    if n == 0:
        return mask
    area = ndimage.sum(mask, lab, index=np.arange(1, n + 1))
    keep = np.concatenate([[False], area >= min_area])
    return keep[lab]


def piece_points(mask, keep):
    """Centre-line points of the stroke pieces (connected components) for which keep(rows, cols)
    is true: run centres along each piece's longer extent (per column for a shallow piece, per row
    for a steep one). Returns [(col, row), ...]."""
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    pts = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rs, cs = np.where(lab[sl] == i)
        rs = rs + sl[0].start
        cs = cs + sl[1].start
        if not keep(rs, cs):
            continue
        if np.ptp(cs) >= np.ptp(rs):
            for c in np.unique(cs):
                pts.append((float(c), float(rs[cs == c].mean())))
        else:
            for r in np.unique(rs):
                pts.append((float(cs[rs == r].mean()), float(r)))
    return pts


def runs_in_col(mask, c, r_top, r_bot):
    idx = np.where(mask[r_top:r_bot, c])[0] + r_top
    return [(g[0], g[-1]) for g in groups(idx)]


def thickness(mask, cols, r_top, r_bot):
    th = []
    for c in cols:
        th += [b - a + 1 for a, b in runs_in_col(mask, c, r_top, r_bot)]
    return float(np.median(th)) if th else float("nan")


def track(runs, c_start, r_start, c_stop, lw, max_gap=400, tol=None):
    """Follow one curve column by column from (c_start, r_start) to c_stop: in each column take the
    run whose span is nearest the row extrapolated from the last points followed; a column with no
    run within the tolerance is skipped (a gap between dashes). Returns {col: row of run centre}."""
    step = 1 if c_stop >= c_start else -1
    got = {}
    hist = [(c_start, r_start)]
    tol = 1.5 * lw if tol is None else tol
    last = c_start
    for c in range(c_start, c_stop + step, step):
        if abs(c - last) > max_gap:
            break
        h = hist[-30:]
        if len(h) >= 8 and np.ptp([p[0] for p in h]) > 3:
            b, a = np.polyfit([p[0] for p in h], [p[1] for p in h], 1)
            pred = a + b * c
            slope = abs(b)
        else:
            pred, slope = h[-1][1], 0.0
        best = None
        for a_, b_ in runs(c):
            if b_ - a_ + 1 > 2.5 * lw * math.sqrt(1 + slope**2) + lw:
                continue  # far longer than the curve's own run: a glyph or another line
            dist = 0.0 if a_ <= pred <= b_ else min(abs(a_ - pred), abs(b_ - pred))
            if best is None or dist < best[0]:
                best = (dist, a_, b_)
        if best is None or best[0] > tol + (1.5 * slope + 0.5) * abs(c - last):
            continue
        r = (best[1] + best[2]) / 2
        got[c] = r
        hist.append((c, r))
        last = c
    return got


def fit_points(pts, col, lw, rob=True):
    """pts: list of (col, row) centres. Returns row at col, slope drow/dcol, rms residual."""
    P = np.array(pts, float)
    if len(P) < 5:
        return None
    cs, rs = P[:, 0], P[:, 1]
    steep = np.ptp(rs) > np.ptp(cs)
    keep = np.ones(len(P), bool)
    for _ in range(4):
        if keep.sum() < 5:
            return None
        if steep:
            b, a = np.polyfit(rs[keep], cs[keep], 1)
            res = cs - (a + b * rs)
        else:
            b, a = np.polyfit(cs[keep], rs[keep], 1)
            res = rs - (a + b * cs)
        rms = float(np.sqrt(np.mean(res[keep] ** 2)))
        new = np.abs(res) <= max(3 * rms, lw / 2)
        if not rob or (new == keep).all():
            break
        keep = new
    if steep:
        if abs(b) < 1e-9:
            return None
        slope = 1.0 / b
        row = (col - a) / b
    else:
        slope = b
        row = a + b * col
    return float(row), float(slope), rms, int(keep.sum())


def read_at(cal, curve, at, lw, win=80, extra_note=""):
    """Read y at each x of `at` from curve points [(col, row), ...]: the points within `win` px
    (along the curve) of the point nearest the position's column, fitted by a local line."""
    X = cal["x"]
    items = list(curve.items() if isinstance(curve, dict) else curve)
    out = []
    for x in at:
        x = float(x)
        col = X.pix_of(x)
        near = [(c, r) for c, r in items if abs(c - col) <= win]
        if not near:
            out.append({"x": x, "y": None, "note": "curve not followed here"})
            continue
        c0, r0 = min(near, key=lambda p: abs(p[0] - col))
        pts = [(c, r) for c, r in items if (c - c0) ** 2 + (r - r0) ** 2 <= win**2]
        f = fit_points(pts, col, lw)
        if f is None:
            out.append({"x": x, "y": None, "note": "curve not followed here"})
            continue
        row, slope, rms, n = f
        y, lo, hi, dpx = value(cal, col, row, slope, lw, rms)
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(col), float(row)],
                    "px_lo": float(row + dpx), "px_hi": float(row - dpx),
                    "note": f"line {lw:.0f} px; calibration misfit x {X.misfit:.1f} px, y {cal['y'].misfit:.1f} px; "
                            f"local slope {slope:.2f} px/px, fit rms {rms:.1f} px over {n} points" + extra_note})
    return out


def read_tracked(image, at, x_labels, y_labels, start_x, pick="lowest", y_scale="linear",
                 open_px=15, x_range=None, row_range=None, cal_kw=None, exclude=None):
    """Calibrate, keep the thick strokes, follow one curve from `start_x` (the stroke picked there:
    'lowest', 'highest', or an index from the bottom) to both ends of x_range, and read it at `at`.
    `exclude(col, a, b)` may reject runs (legend, labels) by position."""
    dk = dark(image)
    cal = calibrate(dk, x_labels, y_labels, y_scale=y_scale, **(cal_kw or {}))
    m = open_mask(dk, open_px)
    X = cal["x"]
    r_top = cal["y_top"] if row_range is None else row_range[0]
    r_bot = cal["x_row"][0] - 3 if row_range is None else row_range[1]

    c0 = int(round(X.pix_of(start_x)))

    def raw_runs(c):
        rr = runs_in_col(m, c, r_top, r_bot)
        if exclude is not None:
            rr = [(a, b) for a, b in rr if not exclude(c, a, b)]
        return rr

    lw = float(np.median([b - a + 1 for c in range(c0 - 20, c0 + 21) for a, b in raw_runs(c)] or [open_px]))
    lw = min(lw, 3 * open_px)
    m = drop_small(m, 2.5 * open_px * open_px)

    def runs(c):
        rr = runs_in_col(m, c, r_top, r_bot)
        if exclude is not None:
            rr = [(a, b) for a, b in rr if not exclude(c, a, b)]
        return rr

    rr = runs(c0)
    if isinstance(pick, tuple):
        # the first stroke, from start_x outwards, whose centre lies between the two y values
        r_lo, r_hi = sorted((cal["y"].pix_of(pick[0]), cal["y"].pix_of(pick[1])))
        for dc in sorted(range(-300, 301), key=abs):
            band = [(a, b) for a, b in runs(c0 + dc) if r_lo <= (a + b) / 2 <= r_hi]
            if band:
                c0 = c0 + dc
                rr = band
                break
        else:
            raise ValueError("no stroke in the start band")
        pick = "lowest"
    if pick == "lowest":
        a, b = rr[-1]
    elif pick == "highest":
        a, b = rr[0]
    else:
        a, b = rr[-1 - int(pick)]
    lw = float(b - a + 1) if abs(b - a) < 3 * lw else lw
    xr = x_range or (x_labels[0], x_labels[-1])
    cl, cr = int(X.pix_of(xr[0])), int(X.pix_of(xr[1]))
    curve = track(runs, c0, (a + b) / 2, cr, lw)
    curve.update(track(runs, c0, (a + b) / 2, cl, lw))
    return read_at(cal, curve, at, lw), cal, curve, lw


def value(cal, col, row, slope, lw, rms):
    """y value and its 95% interval at (col, row) on a curve of local slope drow/dcol."""
    xax, yax = cal["x"], cal["y"]
    half = lw / 2 * math.sqrt(1 + slope**2)
    d_px = half + yax.misfit + abs(slope) * xax.misfit + 2 * rms
    y = yax.val(row)
    a, b = yax.val(row + d_px), yax.val(row - d_px)
    return float(y), float(min(a, b)), float(max(a, b)), d_px
