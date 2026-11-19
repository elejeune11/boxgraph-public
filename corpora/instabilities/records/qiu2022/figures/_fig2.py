"""Shared reading code for Fig. 2 (PDF p. 4), panels (a) shell and (b) balloon normalization.

Calibration: the plot box and its inward tick marks are found by boxgraph.digitize.find_axes; the
labelled ticks between the box edges are matched in order to the printed tick labels given in each
reading's SPEC (the box edges carry the first and last label). The misfit of the linear fit is
added to every interval.

Curves: each pressure is drawn in one colour (MATLAB's default order, matched to the curve labels
printed next to the curves: blue, red, yellow, purple, green from the lowest pressure up), once
solid (numerics) and once dashed (Eq. 8). At a column c, the pixels of that colour in the columns
c-60..c+60 are split into runs per column; the run centres are fitted with one quadratic, and their
residuals are clustered (a gap of more than 4 px separates two lines). A solid line covers nearly
every column of the window (coverage >= 0.82); a dashed one about two thirds. The cluster wanted is
fitted again on its own and evaluated at c; its 95% interval is half the median vertical extent of its
runs (the centre lies within the ink) plus twice the rms scatter of the fit plus the calibration misfit.
Where the dashed and solid lines coincide there is one cluster with full coverage; it is read as both,
and the note says so.

Points: the coloured dots (numerical wrinkling onsets) are found by a morphological opening of the
colour mask with a disk wider than any line, keeping round blobs; the black crosses (Eq. 11) by
matching a plus-shaped template (arm half-length and thickness measured on the figure) near each
dot, counting both black and dot pixels as the cross (the dots are drawn over the crosses).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from boxgraph import digitize

COLORS = {
    "blue": (0, 114, 189),
    "red": (217, 83, 25),
    "yellow": (237, 177, 32),
    "purple": (126, 47, 142),
    "green": (119, 172, 48),
}
TOL = 60.0
HALF = 60  # half window, px
CROSS_H = {"a": 31, "b": 26}  # cross arm half-length at 900 dpi, measured on each panel
CROSS_T = 10  # cross arm thickness
DOT_OPEN = 10  # opening radius, px: lines (about 10-13 px wide) vanish, dots (about 32 px) remain


LABELS = {  # printed tick labels, from the box's left/bottom edge to its right/top edge
    "a": {"x": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], "y": [0, 1, 2, 3, 4, 5, 6, 7, 8]},
    "b": {"x": [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3], "y": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]},
}
ORDER = ["blue", "red", "yellow", "purple", "green"]  # curve labels from the lowest pressure up


def read_spec(image, at, spec):
    s = dict(LABELS[spec["panel"]], **spec)
    if spec["kind"] == "curve":
        return read_curve(image, at, s)
    return read_points(image, at, dict(s, colors=ORDER))


def calibrate(image, spec):
    fa = digitize.find_axes(image)
    c0, r0, c1, r1 = fa.box
    xl, yl = [float(v) for v in spec["x"]], [float(v) for v in spec["y"]]
    if len(fa.x_ticks) != len(xl) - 2 or len(fa.y_ticks) != len(yl) - 2:
        raise ValueError(f"ticks found {len(fa.x_ticks)}, {len(fa.y_ticks)}; labels {len(xl)}, {len(yl)}")
    xm = [(c0, xl[0])] + list(zip(fa.x_ticks, xl[1:-1])) + [(c1, xl[-1])]
    ys = sorted(fa.y_ticks, reverse=True)  # bottom first
    ym = [(r1, yl[0])] + list(zip(ys, yl[1:-1])) + [(r0, yl[-1])]
    return digitize.Axis("linear", xm), digitize.Axis("linear", ym), fa.box


def color_mask(image, name, box, inset=6):
    rgb = image[..., :3].astype(float)
    d = np.sqrt(((rgb - np.array(COLORS[name], float)) ** 2).sum(axis=2))
    m = d < TOL
    c0, r0, c1, r1 = (int(round(v)) for v in box)
    out = np.zeros_like(m)
    out[r0 + inset:r1 - inset, c0 + inset:c1 - inset] = m[r0 + inset:r1 - inset, c0 + inset:c1 - inset]
    return out


def _runs(col):
    idx = np.flatnonzero(col)
    if idx.size == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i > p + 2:
            out.append((s, p))
            s = i
        p = i
    out.append((s, p))
    return out


def _clusters(mask, c):
    pts = []  # column, centre row, vertical extent
    for cc in range(c - HALF, c + HALF + 1):
        if 0 <= cc < mask.shape[1]:
            for s, e in _runs(mask[:, cc]):
                pts.append((cc, (s + e) / 2, e - s + 1))
    if len(pts) < 5:
        return []
    p = np.array(pts, float)
    coef = np.polyfit(p[:, 0] - c, p[:, 1], 2)
    res = p[:, 1] - np.polyval(coef, p[:, 0] - c)
    order = np.argsort(res)
    groups, cur = [], [order[0]]
    for a, b in zip(order[:-1], order[1:]):
        if res[b] - res[a] > 4:
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    out = []
    for g in groups:
        q = p[g]
        cover = len(set(q[:, 0].astype(int))) / (2 * HALF + 1)
        deg = 2 if len(set(q[:, 0])) > 10 else 1
        cf = np.polyfit(q[:, 0] - c, q[:, 1], deg)
        rms = float(np.sqrt(np.mean((q[:, 1] - np.polyval(cf, q[:, 0] - c)) ** 2)))
        out.append({"row": float(np.polyval(cf, 0.0)), "half": float(np.median(q[:, 2])) / 2 + 2 * rms,
                    "cover": cover, "n": len(q)})
    return [o for o in out if o["cover"] >= 0.25]


def read_curve(image, at, spec):
    xa, ya, box = calibrate(image, spec)
    mask = color_mask(image, spec["color"], box)
    mis_x, mis_y = max(xa.residual_px, 0.5), max(ya.residual_px, 0.5)
    out = []
    for x in at:
        c = int(round(xa.to_pixel(x)))
        cl = _clusters(mask, c)
        solid = [o for o in cl if o["cover"] >= 0.82]
        dashed = [o for o in cl if o["cover"] < 0.82]
        note = ""
        if spec["line"] == "solid":
            pick = solid[0] if len(solid) == 1 else None
            if len(solid) != 1:
                note = f"{len(solid)} full-coverage clusters of this colour"
        else:
            if len(dashed) == 1:
                pick = dashed[0]
            elif not dashed and len(solid) == 1:
                pick, note = solid[0], "dashed and solid lines coincide here; read as one"
            else:
                pick, note = None, f"{len(dashed)} partial and {len(solid)} full clusters"
        if pick is None:
            out.append({"x": x, "y": None, "note": note or "line not found"})
            continue
        row, half = pick["row"], pick["half"] + mis_y + mis_x * 0.0
        y, lo, hi = ya.to_value(row), ya.to_value(row + half), ya.to_value(row - half)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, row],
                    "px_lo": row - half, "px_hi": row + half,
                    "note": (note + f"; coverage {pick['cover']:.2f}").lstrip("; ")})
    return out


def find_dot(image, name, box):
    m = color_mask(image, name, box)
    yy, xx = np.mgrid[-DOT_OPEN:DOT_OPEN + 1, -DOT_OPEN:DOT_OPEN + 1]
    disk = xx**2 + yy**2 <= DOT_OPEN**2
    op = ndimage.binary_opening(m, structure=disk)
    lab, n = ndimage.label(op)
    best = None
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        h, w = np.ptp(rr) + 1, np.ptp(cc) + 1
        if rr.size < 150 or max(h, w) > 1.5 * min(h, w) or max(h, w) > 60:
            continue
        cand = (rr.size, cc.mean(), rr.mean())
        if best is None or cand[0] > best[0]:
            best = cand
    return None if best is None else (best[1], best[2])


def find_cross(image, near, box, h):
    rgb = image[..., :3].astype(float)
    black = rgb.max(axis=2) < 90
    # dots and lines are drawn over the crosses: coloured ink counts as hiding the cross
    colored = (rgb.max(axis=2) - rgb.min(axis=2)) > 60
    ink = (black | ndimage.binary_dilation(colored, iterations=2)).astype(float)
    t = CROSS_T
    hk = ndimage.uniform_filter(ink, size=(t, 2 * h + 1))
    vk = ndimage.uniform_filter(ink, size=(2 * h + 1, t))
    score = np.minimum(hk, vk)
    # the four arm ends (the outer quarter of each arm) must be black
    bl = black.astype(float)
    e, s = max(h // 4, 3), (7 * h) // 8
    outer = np.minimum.reduce([
        ndimage.shift(ndimage.uniform_filter(bl, size=(t, e)), (0, d), order=0) for d in (s, -s)
    ] + [ndimage.shift(ndimage.uniform_filter(bl, size=(e, t)), (d, 0), order=0) for d in (s, -s)])
    score = np.where(outer > 0.5, score, 0.0)
    c, r = int(round(near[0])), int(round(near[1]))
    w = 45
    sub = score[r - w:r + w + 1, c - w:c + w + 1]
    if sub.size == 0 or sub.max() < 0.8:
        return None
    rr, cc = np.nonzero(sub >= sub.max() - 0.01)
    return (c - w + cc.mean(), r - w + rr.mean(), (np.ptp(cc) + np.ptp(rr)) / 2)


def read_points(image, at, spec):
    """at: the curve labels (pressures) of the points to read, in the order of COLOR_ORDER;
    the y returned is the x axis position (curvature) of the dot or cross on that curve."""
    xa, ya, box = calibrate(image, spec)
    mis = max(xa.residual_px, 0.5)
    out = []
    for p, name in zip(at, spec["colors"]):
        dot = find_dot(image, name, box)
        if dot is None:
            out.append({"x": p, "y": None, "note": f"no {name} dot found"})
            continue
        if spec["kind"] == "dot":
            col, row, extra, note = dot[0], dot[1], 2.0, f"{name} dot"
        else:
            cr = find_cross(image, dot, box, CROSS_H[spec["panel"]])
            if cr is None:
                out.append({"x": p, "y": None, "note": f"no cross near the {name} dot"})
                continue
            col, row, extra, note = cr[0], cr[1], 1.5 + cr[2], f"cross nearest the {name} dot"
        half = extra + mis
        v, lo, hi = xa.to_value(col), xa.to_value(col - half), xa.to_value(col + half)
        out.append({"x": p, "y": v, "lo": lo, "hi": hi, "px": [col, row],
                    "note": f"{note}; M axis there {ya.to_value(row):.4g}"})
    return out
