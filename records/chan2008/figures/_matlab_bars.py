"""Shared reading code for single-colour MATLAB bar charts in a black box (Fig. S5, S11D).

Not a reading itself: each reading's file loads this one by path and pins its
SHA-256, so a change here forces a change in every file that uses it.

Calibration, from the image: the box is the longest dark horizontal and vertical
lines; MATLAB draws its ticks as short dark strokes inside the box along the
bottom and left edges. The caller names the printed tick labels (and, where the
labels sit on the box edges, the edge values); tick strokes are matched to them
in order, with any stray stroke (a dashed line, a bar edge) dropped by keeping
the strokes nearest an evenly spaced set. Bars are found by colour, scanning
each column up from the bottom edge; a bar's top is the median top of its
inner columns. Bins form an even grid fitted to the bars found; a bin of the
grid with no bar reads 0.
"""
import numpy as np


def _black(img):
    f = img.astype(float)
    return (f.max(axis=2) < 110) & (f.max(axis=2) - f.min(axis=2) < 60)


def _bar_mask(img):
    f = img.astype(float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    return (B - R > 50) & (B - G > 40)


def _lines(frac, thr):
    on = np.where(frac > thr)[0]
    if len(on) == 0:
        return []
    groups = np.split(on, np.where(np.diff(on) > 2)[0] + 1)
    return [(float(gr.mean()), float(frac[gr].max())) for gr in groups]


def box(img, region=None):
    """Plot box (left, top, right, bottom) in pixels: the longest dark lines."""
    k = _black(img)
    h, w = k.shape
    r0, r1, c0, c1 = region or (0, h, 0, w)
    sub = k[r0:r1, c0:c1]
    rows = _lines(sub.mean(axis=1), 0.5)
    cols = _lines(sub.mean(axis=0), 0.5)
    top, bottom = rows[0][0] + r0, rows[-1][0] + r0
    left, right = cols[0][0] + c0, cols[-1][0] + c0
    return left, top, right, bottom


def _strokes(prof, thr):
    on = np.where(prof > thr)[0]
    if len(on) == 0:
        return []
    groups = np.split(on, np.where(np.diff(on) > 2)[0] + 1)
    return [float(gr.mean()) for gr in groups if len(gr) <= 25]


def _match(cands, n, lo, hi, edges):
    """Pick n strokes in (lo, hi) that best fit an even spacing (edges, if given, pin the ends)."""
    cands = sorted(c for c in cands if min(lo, hi) + 6 < c < max(lo, hi) - 6)
    if edges is None:
        cands = sorted(cands + [lo, hi])           # a labelled tick may sit on the box edge
    if edges is not None:
        e0, e1, v0, v1, vals = edges
        want = [lo + (v - v0) / (v1 - v0) * (hi - lo) for v in vals]
        return [min(cands, key=lambda c: abs(c - wv)) if cands else None for wv in want]
    if len(cands) == n:
        return cands
    best, best_err = None, None
    from itertools import combinations
    for comb in combinations(cands, n):
        d = np.diff(comb)
        err = float(np.std(d)) if len(d) > 1 else 0.0
        if best_err is None or err < best_err:
            best, best_err = list(comb), err
    return best


def calibrate(img, bx, x_ticks, y_ticks, x_edges=None, y_edges=None):
    """Axis fits from the tick strokes. x_edges/y_edges: values at the box's left/right
    (bottom/top) edges when the labels sit on them, else None."""
    left, top, right, bottom = bx
    k = _black(img)
    # x ticks: strokes hanging from the top edge (MATLAB repeats them there; at the bottom
    # the bars' black outlines would pass for ticks)
    band = k[int(top) + 4:int(top) + 14, int(left):int(right)].mean(axis=0)
    xc = [c + int(left) for c in _strokes(band, 0.6)]
    ex = (None if x_edges is None else (left, right, x_edges[0], x_edges[1], x_ticks))
    xs = _match(xc, len(x_ticks), left, right, ex)
    xm = [(p, v) for p, v in zip(xs, x_ticks) if p is not None]
    if x_edges is not None:
        xm += [(left, x_edges[0]), (right, x_edges[1])]
    # y ticks: strokes from the left edge
    band = k[int(top):int(bottom), int(left) + 4:int(left) + 14].mean(axis=1)
    yc = [r + int(top) for r in _strokes(band, 0.6)]
    ey = (None if y_edges is None else (bottom, top, y_edges[0], y_edges[1], y_ticks))
    ys = _match(yc, len(y_ticks), bottom, top, ey) if y_edges is None else \
        [min(yc, key=lambda r: abs(r - (bottom + (v - y_edges[0]) / (y_edges[1] - y_edges[0]) * (top - bottom))))
         if yc else None for v in y_ticks]
    ym = [(p, v) for p, v in zip(ys, y_ticks) if p is not None]
    if y_edges is not None:
        ym += [(bottom, y_edges[0]), (top, y_edges[1])]
    X, Y = np.array(xm, float), np.array(ym, float)
    bxs, axs = np.polyfit(X[:, 1], X[:, 0], 1)
    bys, ays = np.polyfit(Y[:, 1], Y[:, 0], 1)
    return dict(ax=axs, bx=bxs, ay=ays, by=bys,
                misfit_x=float(np.max(np.abs(X[:, 0] - (axs + bxs * X[:, 1])))),
                misfit_y=float(np.max(np.abs(Y[:, 0] - (ays + bys * Y[:, 1])))),
                n_x=len(X), n_y=len(Y), box=bx)


def bars(img, bx):
    left, top, right, bottom = bx
    m = _bar_mask(img)
    axis = int(round(bottom))
    tops = np.full(m.shape[1], np.nan)
    for c in range(int(left) + 3, int(right) - 2):
        r, gap, t = axis - 1, 0, None
        while r > top and gap <= (8 if t is None else 2):
            if m[r, c]:
                t, gap = r, 0
            else:
                gap += 1
            r -= 1
        if t is not None:
            tops[c] = t
    on = np.where(~np.isnan(tops))[0]
    out = []
    if len(on) == 0:
        return out
    k = _black(img)
    for grp in np.split(on, np.where(np.diff(on) > 2)[0] + 1):
        if len(grp) >= 8:
            core = grp[2:-2]
            t = float(np.nanmedian(tops[core]))
            # the bar's edge is the centre of its black outline (as the axis line is taken at its
            # centre): count the black rows above the coloured fill in the inner columns
            n = []
            for c in core[::3]:
                r, cnt = int(t) - 1, 0
                while r > top and k[r, c]:
                    cnt, r = cnt + 1, r - 1
                n.append(cnt)
            t_edge = t - 0.5 - float(np.median(n)) / 2.0
            out.append(((grp[0] + grp[-1]) / 2.0, t_edge, float(grp[-1] - grp[0] + 1)))
    return out


def read_bars(img, bx, cal, bin_width=None, edge_px=3.0, x_range=None):
    """One reading per bin of the grid between the box edges (or x_range)."""
    left, top, right, bottom = bx
    found = bars(img, bx)
    xval = lambda c: (c - cal["ax"]) / cal["bx"]
    yval = lambda r: (r - cal["ay"]) / cal["by"]
    centres = [c for c, _, _ in found]
    width = float(np.median([wd for _, _, wd in found]))
    d = np.diff(centres)
    adjacent = d[d < 1.6 * width] if len(d) else d
    if bin_width is not None:
        s = bin_width * cal["bx"]
    elif len(adjacent):
        s = float(np.median(adjacent))          # bins from neighbouring bars
    else:
        s = width / 0.8                         # MATLAB's default bar fills 0.8 of its bin
    ks = np.array([round((c - centres[0]) / s) for c in centres])
    if len(set(ks.tolist())) > 1 and bin_width is None:
        s, a = np.polyfit(ks, centres, 1)
    else:
        a = float(np.mean([c - k * s for c, k in zip(centres, ks)]))
    lo_px, hi_px = (left, right) if x_range is None else (cal["ax"] + cal["bx"] * x_range[0],
                                                          cal["ax"] + cal["bx"] * x_range[1])
    k0 = int(np.ceil((lo_px + 0.3 * s - a) / s))
    k1 = int(np.floor((hi_px - 0.3 * s - a) / s))
    unit = abs(cal["by"])
    note = (f"x {cal['n_x']} marks misfit {cal['misfit_x']:.2f} px; "
            f"y {cal['n_y']} marks misfit {cal['misfit_y']:.2f} px")
    out = []
    for k in range(k0, k1 + 1):
        c = a + k * s
        hit = [b for b in found if abs(b[0] - c) < 0.4 * s]
        x = float(xval(c))
        if hit:
            cx, t, wd = hit[0]
            y = float(yval(t))
            err = (edge_px + cal["misfit_y"]) / unit
            out.append({"x": x, "y": y, "lo": max(0.0, y - err), "hi": y + err, "px": [cx, t],
                        "px_lo": t - err * unit, "px_hi": t + err * unit, "note": "bar top; " + note})
        else:
            err = (edge_px + cal["misfit_y"]) / unit
            out.append({"x": x, "y": 0.0, "lo": 0.0, "hi": err, "px": [c, bottom],
                        "note": "no bar rising above the axis line in this bin: 0 within the interval; " + note})
    return out
