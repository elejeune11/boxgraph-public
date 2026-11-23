"""Shared reader for the MATLAB line panels of this paper (Figs 8j-l, 9a-c, 10k, 11k).

Every panel has a left and a bottom axis drawn in dark grey with tick marks
pointing into the plot, and coloured curves. Everything is found in the image:

  axes   the column (row) of neutral dark pixels with the longest continuous run
         in the left (bottom) part of the crop;
  ticks  short neutral dark strokes just inside each axis, kept as the largest
         evenly spaced set and matched in order to the printed labels the
         calling file gives (the labels are the only values typed in); where a
         printed label sits at the corner of the two axes, the other axis line is
         its mark;
  curve  pixels of the curve's hue, traced from a seed point given in data
         coordinates (only a rough position, to pick which curve), column by
         column with digitize.trace.

The 95% interval of a value is the half-thickness of the traced line, plus half
a pixel, plus the calibration misfit of the y axis, plus the slope times the
calibration misfit of the x axis, plus one pixel for the antialiased edge.
"""
import math

import numpy as np

from boxgraph.digitize import _longest_run, regular_ticks, trace


def hue(img):
    f = img.astype(float)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx, mn = f.max(axis=2), f.min(axis=2)
    d = np.where(mx - mn == 0, 1e-9, mx - mn)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60.0
    return h, mx - mn, f.mean(axis=2)


def hue_mask(img, lo, hi, smin=45, vmin=0, vmax=255):
    h, s, v = hue(img)
    m = (s >= smin) & (v >= vmin) & (v <= vmax)
    if lo <= hi:
        return m & (h >= lo) & (h <= hi)
    return m & ((h >= lo) | (h <= hi))


def _neutral_dark(img):
    _, s, v = hue(img)
    return (s < 40) & (v < 140)


def _axis_line(nd, axis, frac_lo, frac_hi):
    """Pixel range (start, end inclusive) and centre of the longest dark line."""
    n = nd.shape[1] if axis == "col" else nd.shape[0]
    lo, hi = int(frac_lo * n), int(frac_hi * n)
    runs = []
    for k in range(lo, hi):
        line = nd[:, k] if axis == "col" else nd[k, :]
        L, s, e = _longest_run(line, gap=2)
        runs.append((L, k, s, e))
    best = max(runs, key=lambda t: t[0])
    keep = [t for t in runs if t[0] >= 0.8 * best[0] and abs(t[1] - best[1]) <= 25]
    k0, k1 = min(t[1] for t in keep), max(t[1] for t in keep)
    return k0, k1, best[2], best[3]


def _ticks(strip_counts, lo, hi, need):
    """Centres of runs of positions whose strip holds a tick stroke."""
    on = [i for i in range(lo, hi) if strip_counts[i] >= need]
    groups, cur = [], []
    for i in on + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            if len(cur) <= 40:
                groups.append((cur[0] + cur[-1]) / 2.0 + 0.5)
            cur = []
        if i is not None:
            cur.append(i)
    return groups


def calibrate(img, xlabels, ylabels, x_corner=None, y_corner=None, tick_len=0.006):
    """Axes from the image. xlabels/ylabels: printed tick labels in increasing order
    for the ticks found inside the plot (not counting a label at the corner);
    x_corner/y_corner: the printed label at the corner of the axes, if any."""
    nd = _neutral_dark(img)
    H, W = nd.shape
    c0, c1, yr0, yr1 = _axis_line(nd, "col", 0.0, 0.45)   # y axis
    r0, r1, xc0, xc1 = _axis_line(nd, "row", 0.45, 1.0)   # x axis
    L = max(6, int(tick_len * W))
    # y ticks: strokes just right of the y axis
    ystrip = nd[:, c1 + 2:c1 + 2 + L].sum(axis=1)
    ycand = [p for p in _ticks(ystrip, yr0, r0 - 10, 0.6 * L)]
    xstrip = nd[r0 - 2 - L:r0 - 2, :].sum(axis=0)
    xcand = [p for p in _ticks(xstrip, c1 + 10, xc1 + 1, 0.6 * L)]
    yt = sorted(ycand, reverse=True)  # bottom first
    xt = sorted(xcand)
    for t in (yt, xt):                # labelled ticks are evenly spaced (to 5%: the panels are resampled bitmaps)
        d = np.abs(np.diff(t))
        if len(d) > 1 and (d.max() - d.min()) > 0.05 * np.median(d):
            raise ValueError(f"uneven ticks {t}")
    if len(yt) < len(ylabels) or len(xt) < len(xlabels):
        raise ValueError(f"ticks found x {xcand} y {ycand}; need {len(xlabels)} and {len(ylabels)}")
    ymarks = list(zip(yt[:len(ylabels)], ylabels))
    xmarks = list(zip(xt[:len(xlabels)], xlabels))
    if y_corner is not None:
        ymarks.append(((r0 + r1) / 2.0 + 0.5, y_corner))
    if x_corner is not None:
        xmarks.append(((c0 + c1) / 2.0 + 0.5, x_corner))
    Y, X = np.array(ymarks, float), np.array(xmarks, float)
    by, ay = np.polyfit(Y[:, 1], Y[:, 0], 1)      # row = ay + by * value
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    mis_y = max(0.5, float(np.max(np.abs(Y[:, 0] - (ay + by * Y[:, 1])))))
    mis_x = max(0.5, float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1])))))
    return dict(ay=ay, by=by, ax=ax, bx=bx, mis_y=mis_y, mis_x=mis_x, left=c1 + 1, bottom=r0,
                n_x=len(X), n_y=len(Y))


def read_curve(img, at, cal, mask, seed, xmin=None, xmax=None, legend=None):
    """Trace the curve in mask from seed (x, y in data units) and read it at `at`.
    legend: (x0, x1, y0, y1) in data units, a region blanked before tracing."""
    m = mask.copy()
    m[:, :int(cal["left"]) + 3] = False
    m[int(cal["bottom"]) - 3:, :] = False
    if legend is not None:
        x0, x1, y0, y1 = legend
        cc0, cc1 = sorted((cal["ax"] + cal["bx"] * x0, cal["ax"] + cal["bx"] * x1))
        rr0, rr1 = sorted((cal["ay"] + cal["by"] * y0, cal["ay"] + cal["by"] * y1))
        m[int(rr0):int(rr1) + 1, int(cc0):int(cc1) + 1] = False
    seeds = seed if isinstance(seed[0], (tuple, list)) else [seed]   # several seeds: a sharp corner
    path = {}                                                         # can stop one trace
    for sx, sy in reversed(seeds):
        sc = cal["ax"] + cal["bx"] * sx
        sr = cal["ay"] + cal["by"] * sy
        path.update(trace(m, (sc, sr), max_gap=40))
    out = []
    note0 = f"x {cal['n_x']} marks misfit {cal['mis_x']:.2f} px; y {cal['n_y']} marks misfit {cal['mis_y']:.2f} px"
    for xv in at:
        pc = cal["ax"] + cal["bx"] * xv
        col = int(math.floor(pc))
        if col not in path or col - 1 not in path or col + 1 not in path:
            out.append({"x": xv, "y": None, "note": "curve not traced at this column"})
            continue
        centre, half, amb = path[col]
        slope = (path[col + 1][0] - path[col - 1][0]) / 2.0
        h = half + 0.5 + 1.0 + cal["mis_y"] + abs(slope) * cal["mis_x"]
        if amb:
            h += half
        y = (centre - cal["ay"]) / cal["by"]
        a, b = (centre - h - cal["ay"]) / cal["by"], (centre + h - cal["ay"]) / cal["by"]
        out.append({"x": xv, "y": float(y), "lo": float(min(a, b)), "hi": float(max(a, b)),
                    "px": [float(pc), float(centre)], "px_lo": float(centre - h), "px_hi": float(centre + h),
                    "note": ("merged with another curve here; " if amb else "") + note0})
    return out
