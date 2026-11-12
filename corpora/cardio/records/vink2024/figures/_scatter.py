"""Shared reading code for the per-participant scatter plots of the vink2024 supplement (GraphPad Prism style:
filled red circles for ANOCA patients, filled blue triangles for controls, black axes with ticks pointing out).
The figures are embedded rasters (the supplement was converted from a .docx); they are read at the crop and dpi
of figures.yaml.

Calibration. y: the y axis and its left-pointing ticks, as in _bars.calibrate (major ticks are those at least 70%
as long as the longest; they are matched top to bottom to the printed labels; a straight line is fitted and its
rms misfit widens every interval). x: the x axis is the long horizontal line at y = 0; in each column the black
run going down from just below it is measured; column groups with a run form the ticks, the major ones (at least
70% as long as the longest) are matched left to right to the printed labels, and a line is fitted.

Markers. A colour mask per group: red (R > 170, R - G > 80, R - B > 80) or blue (B > 170, B - R > 60). Connected
components of the mask are markers or clusters of fused markers. The area of one marker, A1, is the median area
of the components after discarding those more than 40% from the first median (fused clusters and specks).
A component is ceil(area/A1 - 0.35) markers (a little more than a marker's area counts as one: antialiasing and
small overlaps); specks below 0.3 A1 are dropped. A cluster of n markers is split by k-means (k = n, seeded by
farthest-point sampling, 30 iterations) and each centre is a marker. Red circles are drawn over blue triangles,
so a triangle under a circle loses area and a hidden one is not found: the reading says how many it found.

Intervals: y of an isolated marker +- (2 px + misfit); of a marker split from a cluster +- (half the marker's
radius + misfit). x has no interval in the record's format; the note gives the same half-widths in x units.
"""

import importlib.util
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)


def masks(image):
    im = np.asarray(image)[..., :3].astype(int)
    R, G, Bl = im[..., 0], im[..., 1], im[..., 2]
    red = (R > 170) & (R - G > 80) & (R - Bl > 80)
    blue = (Bl > 170) & (Bl - R > 60)
    return {"red": red, "blue": blue}


def x_axis(ink, xr, labels, yc):
    H, W = ink.shape
    start = xr[-1] + 2
    runs = np.zeros(W, int)
    for c in range(W):
        n, r = 0, start
        while r < H and ink[r, c]:
            n += 1
            r += 1
        runs[c] = n
    ticks = []
    for g in B._groups(np.where(runs > 4)[0]):
        ticks.append(((g[0] + g[-1]) / 2.0, int(max(runs[g]))))
    longest = max(t[1] for t in ticks)
    major = [t[0] for t in ticks if t[1] >= 0.7 * longest]
    if len(major) != len(labels):
        raise RuntimeError(f"expected {len(labels)} major x ticks, found {major} (all: {ticks})")
    return B.Axis(major, labels)


def _kmeans(pts, k, iters=30):
    cen = [pts[0]]
    for _ in range(1, k):
        d = np.min([((pts - c) ** 2).sum(axis=1) for c in cen], axis=0)
        cen.append(pts[int(np.argmax(d))])
    cen = np.array(cen, float)
    for _ in range(iters):
        lab = np.argmin(((pts[:, None, :] - cen[None, :, :]) ** 2).sum(axis=2), axis=1)
        new = np.array([pts[lab == j].mean(axis=0) if (lab == j).any() else cen[j] for j in range(k)])
        if np.allclose(new, cen):
            break
        cen = new
    return cen


def read_points(image, ylabels, xlabels, colour, exclude=()):
    """exclude: boxes (c0, r0, c1, r1) in the crop to leave out (a legend's marker inside the plot area)."""
    ay, ink, yc, xr = B.calibrate(image, ylabels)
    ax = x_axis(ink, xr, xlabels, yc)
    m = masks(image)[colour].copy()
    for c0, r0, c1, r1 in exclude:
        m[r0:r1, c0:c1] = False
    m[:, : yc[-1] + 2] = False
    m[xr[0] - 1:, :] = False
    lab, n = ndimage.label(m)
    areas = ndimage.sum(m, lab, range(1, n + 1))
    a1 = float(np.median(areas))
    near = areas[(areas > 0.6 * a1) & (areas < 1.4 * a1)]
    a1 = float(np.median(near)) if len(near) else a1
    rad = float(np.sqrt(a1 / np.pi))
    out = []
    for i in range(1, n + 1):
        a = areas[i - 1]
        if a < 0.3 * a1:
            continue
        k = max(1, int(np.ceil(a / a1 - 0.35)))
        rr, cc = np.nonzero(lab == i)
        pts = np.stack([cc, rr], axis=1).astype(float)
        cen = pts.mean(axis=0)[None, :] if k == 1 else _kmeans(pts, k)
        tol = 2.0 if k == 1 else rad / 2.0
        for c, r in cen:
            y, x = ay.val(r), ax.val(c)
            lo, hi = ay.interval(r, tol)
            dx = abs(ax.b) * (tol + ax.misfit)
            out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(c), float(r)],
                        "note": (f"{colour} marker at ({c:.0f}, {r:.0f})" +
                                 ("" if k == 1 else f", one of {k} split from a fused cluster of area {a / a1:.2f} markers") +
                                 f"; x +- {dx:.3g}; misfits x {ax.misfit:.2f} px, y {ay.misfit:.2f} px")})
    out.sort(key=lambda d: (d["x"], d["y"]))
    if out:
        out[0]["note"] += f"; {len(out)} {colour} markers found (one marker = {a1:.0f} px, radius {rad:.1f} px)"
    return out
