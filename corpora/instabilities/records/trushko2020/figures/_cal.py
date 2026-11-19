"""Shared reading code for the figures of trushko2020 read in the second pass (everything except
Fig. 4H/4I, which use _fig4.py).

Calibration, from the image only:
- ink is found as pixels darker than `dark` (sum of channels) and nearly neutral (axes are black or
  dark grey in every panel);
- the x axis is the row with the longest ink run in the lower part of the crop, the y axis the
  column with the longest ink run in the left part (or a column given by the caller, for a right
  axis);
- tick marks are short ink runs perpendicular to an axis, on the side the caller names; their
  centres are matched to values: the first tick from the origin side has value `v0`, and each
  further tick `step` more (or a decade more on a log axis), allowing for ticks too faint to be
  found (the spacing is the largest that makes every gap a whole number of spacings);
- a straight line is fitted through (pixel, value) for each axis; its rms misfit (pixels) is
  kept and enters every interval.
"""
import importlib.util
import math
from pathlib import Path

import numpy as np
from scipy import ndimage


def load(name):
    spec = importlib.util.spec_from_file_location("trushko2020_" + name, Path(__file__).with_name(name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ink(image, dark=330, chroma=60):
    im = image.astype(float)
    return (im.sum(axis=2) < dark) & (im.max(axis=2) - im.min(axis=2) < chroma)


def colour(image, rgb, tol=60.0):
    d = np.sqrt(((image.astype(float) - np.array(rgb, float)) ** 2).sum(axis=2))
    return d < tol


def groups(idx, gap=1):
    out = []
    for c in idx:
        c = int(c)
        if out and c - out[-1][-1] <= gap:
            out[-1].append(c)
        else:
            out.append([c])
    return out


def longest_run(v, gap=2):
    best, bs, be, start, last = 0, 0, 0, None, None
    for i, x in enumerate(list(v) + [False] * (gap + 2)):
        if x:
            if start is None:
                start = i
            last = i
        elif start is not None and i - last > gap:
            if last + 1 - start > best:
                best, bs, be = last + 1 - start, start, last + 1
            start = None
    return best, bs, be


def _spacing_indices(p):
    p = np.array(p, float)
    gaps = np.abs(np.diff(p))
    d = gaps.min()
    s = d
    for k in range(1, 8):
        s = d / k
        if np.all(np.abs(gaps / s - np.round(gaps / s)) < 0.1):
            break
    return [int(round(abs(q - p[0]) / s)) for q in p]


class Axis:
    """value = f(pixel), linear in value or in log10(value)."""

    def __init__(self, px, vals, log=False):
        self.log = log
        self.px = np.array(px, float)
        u = np.log10(vals) if log else np.array(vals, float)
        self.a, self.b = np.polyfit(self.px, u, 1)
        res = u - (self.a * self.px + self.b)
        self.rms_px = max(float(np.sqrt(np.mean(res ** 2))) / abs(self.a), 0.5)
        self.vals = list(vals)

    def val(self, p):
        u = self.a * p + self.b
        return float(10 ** u) if self.log else float(u)

    def pix(self, v):
        u = math.log10(v) if self.log else v
        return (u - self.b) / self.a

    def span(self, p, dp):
        """values at p - dp and p + dp, sorted"""
        a, b = self.val(p - dp), self.val(p + dp)
        return min(a, b), max(a, b)


def axes_lines(image, ycol_side="left", dark=330, xrow=None, ycol=None):
    """Rows of the x axis line and columns of the y axis line, with their ink extents."""
    m = ink(image, dark)
    H, W = m.shape
    if xrow is None:
        xrow = max(range(H // 3, H), key=lambda r: longest_run(m[r])[0])
    if ycol is None:
        cols = range(0, W // 2) if ycol_side == "left" else range(W // 2, W)
        ycol = max(cols, key=lambda c: longest_run(m[:, c])[0])
    n0 = longest_run(m[xrow])[0]
    xr = [r for r in range(max(xrow - 12, 0), min(xrow + 13, H)) if longest_run(m[r])[0] > 0.6 * n0]
    n1 = longest_run(m[:, ycol])[0]
    yc = [c for c in range(max(ycol - 12, 0), min(ycol + 13, W)) if longest_run(m[:, c])[0] > 0.6 * n1]
    _, x0, x1 = longest_run(m[xrow])
    _, y0, y1 = longest_run(m[:, ycol])
    return dict(xr0=min(xr), xr1=max(xr), yc0=min(yc), yc1=max(yc), xext=(x0, x1), yext=(y0, y1), mask=m)


def ticks_x(L, side="out", depth=(3, 12), frac=0.6, lim=None):
    m = L["mask"]
    if side == "out":
        band = m[L["xr1"] + depth[0]:L["xr1"] + depth[1], :]
    else:
        band = m[L["xr0"] - depth[1]:L["xr0"] - depth[0], :]
    v = band.mean(0) > frac
    lo, hi = lim if lim else (L["xext"][0] - 3, L["xext"][1] + 3)
    v[:max(lo, 0)] = False
    v[hi:] = False
    return [float(np.mean(g)) for g in groups(np.where(v)[0]) if len(g) <= 25]


def ticks_y(L, side="out", depth=(3, 12), frac=0.6, lim=None, right=False):
    m = L["mask"]
    if (side == "out") != right:
        band = m[:, L["yc0"] - depth[1]:L["yc0"] - depth[0]]
    else:
        band = m[:, L["yc1"] + depth[0]:L["yc1"] + depth[1]]
    v = band.mean(1) > frac
    lo, hi = lim if lim else (0, L["xr0"] + 3)
    v[:max(lo, 0)] = False
    v[hi:] = False
    return [float(np.mean(g)) for g in groups(np.where(v)[0]) if len(g) <= 25]


def calibrate(px, v0, step, log=False, reverse=False, keep=None):
    """Assign values to tick centres: the tick nearest the origin side has v0 (sorted ascending
    pixels, or descending when reverse), the others v0 + step * index (log: v0 * step**index)."""
    p = sorted(px, reverse=reverse)
    if keep is not None:
        p = keep(p)
    idx = _spacing_indices(p)
    vals = [v0 * step ** i for i in idx] if log else [v0 + step * i for i in idx]
    return Axis(p, vals, log)


def calibrate_from(origin_px, px, v0, step, log=False):
    """Ticks indexed from the axis origin (the crossing with the other axis), whose value is v0:
    tick at p has v0 + step * round(|p - origin| / spacing). The origin itself is a mark."""
    q = [float(v) for v in px if abs(v - origin_px) > 6]
    p, idx = whole_spacings(float(origin_px), q)
    vals = [v0 * step ** i for i in idx] if log else [v0 + step * i for i in idx]
    return Axis(p, vals, log)


def whole_spacings(origin, q, max_index=None):
    """Marks a whole number of tick spacings from `origin` (itself a mark): the spacing starts as
    the smallest gap between neighbouring marks and is refitted by least squares over the marks
    that fit it; stray ink that is not a whole number of spacings away is dropped."""
    q = sorted(q, key=lambda v: abs(v - origin))
    d_all = np.abs(np.array(q) - origin)
    gaps = np.abs(np.diff([origin] + q))
    # the spacing that puts the most marks a whole number of spacings away (ties: the wider)
    cands = [g / n for g in gaps if g > 6 for n in (1, 2, 3) if g / n > 15]
    best = None
    for c in cands:
        k = np.round(d_all / c)
        n_ok = int(((np.abs(d_all / c - k) < 0.12) & (k > 0)).sum())
        if best is None or n_ok > best[0] or (n_ok == best[0] and c > best[1]):
            best = (n_ok, c)
    s = best[1]
    for _ in range(3):
        k = np.round(d_all / s)
        ok = (np.abs(d_all / s - k) < 0.2) & (k > 0)
        if max_index is not None:
            ok &= k <= max_index
        s = float((d_all[ok] * k[ok]).sum() / (k[ok] ** 2).sum())
    p, idx = [origin], [0]
    for v, dd in zip(q, d_all):
        kk = dd / s
        if abs(kk - round(kk)) < 0.15 and round(kk) not in idx and (max_index is None or round(kk) <= max_index):
            p.append(v)
            idx.append(int(round(kk)))
    return p, idx


def log_axis(anchor_px, anchor_val, ticks, sign):
    """A logarithmic axis from tick marks: the mark at anchor_px has the printed value anchor_val
    (a decade label); sign is +1 when values grow with the pixel coordinate (x) and -1 when they
    shrink (y, rows). The decade length D is the one that puts the most marks at whole mantissas
    (1, 2, ..., 9 times a power of ten) within 3 px; those marks, with their values, are fitted."""
    import math
    q = [float(t) for t in ticks if abs(t - anchor_px) > 4]
    a0 = math.log10(anchor_val)
    best = None
    for t in q:
        for mnt in range(2, 11):
            for dec in (0, 1, 2):
                span = math.log10(mnt) + dec
                D = abs(t - anchor_px) / span
                if D < 50:
                    continue
                pts = [(anchor_px, anchor_val)]
                for v in q:
                    u = a0 + sign * (v - anchor_px) / D
                    k = math.floor(u + 1e-9)
                    mt = 10 ** (u - k)
                    m_r = min(max(round(mt), 1), 10)
                    if abs(D * math.log10(mt / m_r)) < 3:
                        pts.append((v, m_r * 10 ** k))
                if best is None or len(pts) > len(best[1]) or (len(pts) == len(best[1]) and D > best[0]):
                    best = (D, pts)
    pts = best[1]
    return Axis([p for p, _ in pts], [v for _, v in pts], log=True)


def saturated(image, chroma=80):
    im = image.astype(float)
    return (im.max(axis=2) - im.min(axis=2)) > chroma


def blobs(mask, radius, min_area=None):
    """Filled round markers: open the mask with a disk (removes lines and bars thinner than the
    disk), label what remains; returns (col, row, area) for each blob."""
    r = int(radius)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = xx ** 2 + yy ** 2 <= r * r
    op = ndimage.binary_opening(mask, structure=disk)
    lab, n = ndimage.label(op)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if min_area and len(rr) < min_area:
            continue
        out.append((float(cc.mean()), float(rr.mean()), int(len(rr))))
    return out


def stem_end(mask, col, row, step, half=2, gap=3):
    """Follow an error bar stem from (col, row) up (step -1) or down (+1) through ink in the
    columns col-half..col+half; return the last ink row (the bar end)."""
    c0, c1 = int(round(col)) - half, int(round(col)) + half + 1
    r = int(round(row))
    last, miss = r, 0
    H = mask.shape[0]
    while 0 <= r + step < H:
        r += step
        if mask[r, c0:c1].any():
            last, miss = r, 0
        else:
            miss += 1
            if miss > gap:
                break
    return last


def point(xa, ya, col, row, dc, dr, note="", bar=None, bar_px=None):
    """A reading dict: value at (col, row) with a pixel half-uncertainty (dc, dr) plus calibration
    misfit (twice the rms) on each axis."""
    x = xa.val(col)
    lo, hi = ya.span(row, dr + 2 * ya.rms_px)
    y = ya.val(row)
    d = {"x": x, "y": y, "lo": min(lo, y), "hi": max(hi, y), "px": [float(col), float(row)],
         "px_lo": float(row + dr + 2 * ya.rms_px), "px_hi": float(row - dr - 2 * ya.rms_px),
         "note": (note + "; " if note else "") + f"x +- {abs(xa.val(col + dc + 2 * xa.rms_px) - x):.3g}; "
                 f"axis rms {xa.rms_px:.2f}/{ya.rms_px:.2f} px"}
    if bar is not None:
        (top, bot), e = bar, (bar_px or 2.0) + 2 * ya.rms_px
        a, b = ya.val(top), ya.val(bot)
        lo_b, hi_b = min(a, b), max(a, b)
        d["bar_lo"], d["bar_hi"] = lo_b, hi_b
        lo_o = min(ya.val(top - e), ya.val(top + e), ya.val(bot - e), ya.val(bot + e))
        hi_o = max(ya.val(top - e), ya.val(top + e), ya.val(bot - e), ya.val(bot + e))
        d["bar_lo_outer"], d["bar_hi_outer"] = min(lo_o, lo_b), max(hi_o, hi_b)
    return d


def scatter(mask, open_radius, min_area=80):
    """Round markers of one colour that may touch: the mask is opened with a small disk (removes
    lines drawn over or under them), connected blobs are labelled, and a blob k times the median
    blob area (rounded) is k touching markers, split along its long axis. Returns (col, row, k)."""
    r = int(open_radius)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    op = ndimage.binary_opening(mask, structure=(xx ** 2 + yy ** 2 <= r * r))
    lab, n = ndimage.label(op)
    bl = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if len(rr) >= min_area:
            bl.append((rr, cc))
    if not bl:
        return []
    med = float(np.median([len(b[0]) for b in bl]))
    rad = np.sqrt(med / np.pi)
    pts = []
    for rr, cc in bl:
        k = max(1, int(round(len(rr) / med)))
        cr, c0 = rr.mean(), cc.mean()
        if k == 1:
            pts.append((float(c0), float(cr), 1))
            continue
        X = np.stack([cc - c0, rr - cr], axis=1).astype(float)
        w, v = np.linalg.eigh(X.T @ X)
        u = v[:, -1]
        proj = X @ u
        Lg = proj.max() - proj.min()
        for j in range(k):
            t = -Lg / 2 + rad + j * (Lg - 2 * rad) / (k - 1)
            pts.append((float(c0 + t * u[0]), float(cr + t * u[1]), k))
    return pts, rad


def ranked(ya, pts, rad, note=""):
    """Markers of one group with no numeric x: each becomes a reading at x = its rank (1 = lowest
    value), so that the group is a curve of its values. Interval: 3 px on a single marker's
    centre, half a radius on one split from touching markers, plus calibration misfit."""
    pts = sorted(pts, key=lambda p: -p[1])     # lowest value (largest row) first
    out = []
    for i, (c, r, k) in enumerate(pts, start=1):
        e = 3.0 if k == 1 else rad / 2
        lo, hi = ya.span(r, e + 2 * ya.rms_px)
        y = ya.val(r)
        out.append({"x": float(i), "y": y, "lo": min(lo, y), "hi": max(hi, y), "px": [c, r],
                    "px_lo": r + e + 2 * ya.rms_px, "px_hi": r - e - 2 * ya.rms_px,
                    "note": (f"split from {k} touching markers; " if k > 1 else "") + note})
    return out


def dots_with_band(image, xa, ya, dot_rgb, band_rgb, radius, box, dot_tol=45.0, band_tol=40.0,
                   min_area=150, centre_px=4.0, legend=None):
    """Coloured dots of one series, each with the shaded band (its error band) around it.
    Dots: pixels within dot_tol of dot_rgb, opened with a disk of `radius`; blobs inside `box`
    (c0, r0, c1, r1), leaving out the `legend` box. Band: in the dot's column, the run of pixels
    of the dot or band colour that contains the dot; its ends are the band's ends (where another
    series overlaps, the run stops at the other colour, so such an end is read as at most that)."""
    dm = colour(image, dot_rgb, dot_tol)
    c0, r0, c1, r1 = box
    lim = np.zeros_like(dm)
    lim[r0:r1, c0:c1] = True
    if legend:
        a0, b0, a1, b1 = legend
        lim[b0:b1, a0:a1] = False
    dm &= lim
    bm = (colour(image, band_rgb, band_tol) | colour(image, dot_rgb, dot_tol)) & lim
    out = []
    for c, r, area in sorted(blobs(dm, radius, min_area=min_area)):
        ci = int(round(c))
        idx = np.where(bm[:, ci])[0]
        run = next((g for g in groups(idx, gap=3) if g[0] <= r <= g[-1]), None)
        bar, why = None, "no band"
        if run:
            # keep the band only where both its ends meet the paper (another series' band or
            # dot next to an end would make that end uncertain)
            def clear(row, step):   # paper within 10 px beyond the end (its soft edge between)
                for k in range(2, 11):
                    px = image[max(0, min(image.shape[0] - 1, row + step * k)), ci].astype(float)
                    if px.min() > 215:
                        return True
                return False
            if clear(run[0], -1) and clear(run[-1], +1):
                bar, why = (run[0], run[-1]), f"band rows {run[0]}-{run[-1]}"
            else:
                why = "band end overlapped by another series: band not read"
        out.append(point(xa, ya, c, r, centre_px, centre_px, bar=bar, bar_px=3.0, note=why))
    return out


def curve_at(mask, xa, ya, at, pick="mid", rowlim=None, halfwin=0, note=""):
    """Centre of the mask in the column of each x in `at` (pick top / bottom / mid run);
    interval: half the run height (the line or band) plus calibration misfit."""
    out = []
    H = mask.shape[0]
    r0, r1 = rowlim if rowlim else (0, H)
    for x in at:
        c = int(round(xa.pix(float(x))))
        cols = range(c - halfwin, c + halfwin + 1)
        runs = []
        for cc in cols:
            idx = np.where(mask[r0:r1, cc])[0] + r0
            runs += [g for g in groups(idx, gap=2) if len(g) >= 2]
        if not runs:
            out.append({"x": float(x), "y": None, "note": "no curve in this column"})
            continue
        if pick == "top":
            g = min(runs, key=lambda g: g[0])
            top, bot = g[0], g[-1]
        elif pick == "bottom":
            g = max(runs, key=lambda g: g[-1])
            top, bot = g[0], g[-1]
        elif pick == "largest":
            g = max(runs, key=len)
            top, bot = g[0], g[-1]
        else:
            top, bot = min(g[0] for g in runs), max(g[-1] for g in runs)
        row = (top + bot) / 2
        half = (bot - top + 1) / 2
        p = point(xa, ya, c, row, 0.5, half + 1, note=note + f"; run {bot - top + 1} px")
        p["x"] = float(x)
        out.append(p)
    return out
