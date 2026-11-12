"""Supplemental Fig. 2 (PDF p. 13): interobserver scatter of baseline MBV, observer 1 (y) against observer 2 (x),
hollow red circles for patients, hollow blue circles for controls (SPSS style). The figure is an embedded raster.

Calibration. y: SPSS draws a light grey gridline at every labelled y value. Grey pixels (channel spread < 30,
mean 110-230) are masked; rows whose longest grey run exceeds half the width are lines. The lowest such line is
the x axis (it carries no label) and is dropped; the remaining lines, top to bottom, are matched to the printed
labels ,70 ... ,20 and a line is fitted (misfit in px). x: the axis has no tick marks. The labels (,20 ... ,70)
are the dark text in the first band of text rows below the x axis; each label is a group of text columns separated
from the next by a wide gap, and SPSS centres a label on its value, so a label's value is at the centre of its
box. Because the leading comma makes "centre of the box" uncertain by half a comma's width, every x carries that
in its note, and the misfit of the line fitted through the label centres.

Markers. Hollow rings, drawn in muted colours: red (R - G > 35, R - B > 30) or blue (B - R > 18, B - G > 10).
The antialiased ring breaks into arcs, so the mask is dilated by 12 px to join them and its holes are filled: each
ring becomes a disc, whose area counts the rings in a cluster and whose centroid is the ring's centre. Two
dilated discs whose rings overlap by half cover only about 1.4 discs, so a component of area a is
floor(a/A1 + 0.7) rings (a single disc varies by about 10% in area). Connected components smaller than 0.3 of a ring are specks; a component of about n rings in area
(ceil(area/A1 - 0.35)) is split by k-means on its pixels, as in _scatter.py. Intervals: an isolated ring +- (2 px
+ misfit) in y; a ring split from a cluster +- (a quarter of the ring's radius + misfit).
"""

import importlib.util
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("_scatter", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_scatter.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
B = S.B

YLABELS = [0.70, 0.60, 0.50, 0.40, 0.30, 0.20]
XLABELS = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]


def calibrate(image):
    im = np.asarray(image)[..., :3].astype(int)
    spread = im.max(axis=2) - im.min(axis=2)
    mean = im.mean(axis=2)
    grey = (spread < 30) & (mean > 110) & (mean < 230)
    H, W = grey.shape
    hr = np.array([B._longest_run(grey[r, :]) for r in range(H)])
    lines = [(g[0] + g[-1]) / 2.0 for g in B._groups(np.where(hr > 0.5 * W)[0], gap=2)]
    xaxis = lines[-1]
    grid = lines[:-1]
    if len(grid) != len(YLABELS):
        raise RuntimeError(f"expected {len(YLABELS)} gridlines, found {grid} (x axis at {xaxis})")
    ay = B.Axis(grid, YLABELS)
    dark = mean < 140
    # the first band of text rows below the x axis
    rows = np.where(dark[int(xaxis) + 8:, :].any(axis=1))[0] + int(xaxis) + 8
    band = B._groups(rows, gap=3)[0]
    sub = dark[band[0]: band[-1] + 1, :]
    cols = np.where(sub.any(axis=0))[0]
    labels = B._groups(cols, gap=40)
    centres = [(g[0] + g[-1]) / 2.0 for g in labels]
    comma = []
    for g in labels:
        sg = B._groups(np.where(sub[:, g[0]: g[-1] + 1].any(axis=0))[0], gap=3)
        comma.append((sg[0][-1] - sg[0][0] + 1) / 2.0 if len(sg) > 2 else 0.0)
    if len(centres) != len(XLABELS):
        raise RuntimeError(f"expected {len(XLABELS)} x labels, found {centres}")
    ax = B.Axis(centres, XLABELS)
    return ay, ax, float(np.mean(comma)), xaxis


def read(image, at, colour):
    ay, ax, half_comma, xaxis = calibrate(image)
    im = np.asarray(image)[..., :3].astype(int)
    R, G, Bl = im[..., 0], im[..., 1], im[..., 2]
    if colour == "red":
        m = (R - G > 35) & (R - Bl > 30)
    else:
        m = (Bl - R > 18) & (Bl - G > 10)
    m[int(xaxis) - 2:, :] = False
    # the antialiased ring breaks into arcs: close it with a small dilation, label, and keep the ring pixels
    md = ndimage.binary_fill_holes(ndimage.binary_dilation(m, iterations=12))
    m = md
    lab, n = ndimage.label(md)
    areas = ndimage.sum(m, lab, range(1, n + 1))
    a1 = float(np.median(areas))
    near = areas[(areas > 0.6 * a1) & (areas < 1.4 * a1)]
    a1 = float(np.median(near)) if len(near) else a1
    out = []
    for i in range(1, n + 1):
        a = areas[i - 1]
        if a < 0.3 * a1:
            continue
        k = max(1, int(np.floor(a / a1 + 0.7)))
        rr, cc = np.nonzero(lab == i)
        pts = np.stack([cc, rr], axis=1).astype(float)
        cen = pts.mean(axis=0)[None, :] if k == 1 else S._kmeans(pts, k)
        for c, r in cen:
            tol = 2.0 if k == 1 else max(4.0, 0.25 * np.sqrt(a1 / np.pi) * 3)
            lo, hi = ay.interval(r, tol)
            dx = abs(ax.b) * (tol + half_comma + ax.misfit)
            out.append({"x": ax.val(c), "y": ay.val(r), "lo": lo, "hi": hi, "px": [float(c), float(r)],
                        "note": (f"{colour} ring at ({c:.0f}, {r:.0f})" + ("" if k == 1 else f", one of {k} split from a cluster") +
                                 f"; x +- {dx:.3g} (label centring {half_comma:.0f} px, misfit {ax.misfit:.2f} px); "
                                 f"y misfit {ay.misfit:.2f} px")})
    out.sort(key=lambda d: (d["x"], d["y"]))
    if out:
        out[0]["note"] += f"; {len(out)} {colour} rings found"
    return out
