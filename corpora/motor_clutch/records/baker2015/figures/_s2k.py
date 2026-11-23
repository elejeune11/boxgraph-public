"""Supp. Fig. 2k: force against indentation depth, one marker colour per UV dose. The panel is an
embedded, blurred bitmap with grey axis lines and dashed grey gridlines.

- y axis: the rows where a grey horizontal line crosses at least 30% of the plot width (frame bottom
  = 0, dashed gridlines 0.5, 1, 1.5, frame top = 2), matched to the printed labels in order.
- x axis: the centres of the five printed labels 0, 50, 100, 150, 200 under the axis (dark text
  blobs), matched in order; the frame's left and right lines are checked against "0" and "200".
- markers: blobs of the series colour (opened to drop anti-aliased fringes); blobs inside the legend
  box (found as the long grey vertical lines inside the frame) are ignored. Each blob gives one point
  (depth, force); points hidden under another series' marker are not returned.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YVALS = [0, 0.5, 1, 1.5, 2]
XVALS = [0, 50, 100, 150, 200]


def grey(img):
    f = img.astype(float)
    return (f.mean(axis=2) < 185) & (f.max(axis=2) - f.min(axis=2) < 25)


def axes(img):
    g = grey(img)
    H, W = g.shape
    vs = [v for v in K.vlines(g, int(0.5 * H)) if v[1] - v[0] < 20]
    left, right = min(vs, key=lambda v: v[0]), max(vs, key=lambda v: v[0])
    # the legend box: long grey verticals strictly inside the frame
    inner = [v for v in K.vlines(g, int(0.2 * H)) if left[1] + 10 < v[0] < right[0] - 10 and v[1] - v[0] < 20]
    legend = None
    if len(inner) >= 2:
        l0, l1 = min(inner, key=lambda v: v[0]), max(inner, key=lambda v: v[0])
        legend = (l0[0] - 5, l1[1] + 5, min(l0[2], l1[2]) - 5, max(l0[3], l1[3]) + 5)
    # horizontal lines, counted right of the legend (its own top and bottom edges are not axis lines)
    c0 = (legend[1] + 5) if legend is not None else left[1] + 3
    c1 = right[0] - 3
    frac = g[:, c0:c1].mean(axis=1)
    rows = [(a + b) / 2.0 for a, b in K.runs(np.nonzero(frac > 0.3)[0])]
    rows = [r for r in rows if left[2] - 15 <= r <= left[3] + 60]
    yax = K.Axis(sorted(rows, reverse=True), YVALS, what=f"y lines {rows}")
    base = max(rows)
    txt = K.dark(img, 120.0, 60.0)
    band = txt[int(base) + 25:int(base) + 120, :]
    cols = np.nonzero(band.any(axis=0))[0]
    groups = []
    for a, b in K.runs(cols):
        if groups and a - groups[-1][1] <= 25:
            groups[-1] = (groups[-1][0], b)
        else:
            groups.append((a, b))
    centres = [(a + b) / 2.0 for a, b in groups if b - a >= 10]
    xax = K.Axis(centres, XVALS, what=f"x labels {centres}")
    frame_off = max(abs(xax.to_px(0) - (left[0] + left[1]) / 2), abs(xax.to_px(200) - (right[0] + right[1]) / 2))
    return yax, xax, frame_off, legend, base


def points(img, rgb, tol):
    yax, xax, frame_off, legend, base = axes(img)
    m = K.near(img, rgb, tol)
    if legend is not None:
        m[legend[2]:legend[3], legend[0]:legend[1]] = False
    bl = K.blobs(m, open_px=7, min_area=150)
    full = max((max(b[2], b[3]) for b in bl), default=0.0)
    out = []
    for col, row, h, w, area in bl:
        hidden = max(full - min(h, w), 0.0)
        py = 2.5 + yax.misfit + hidden / 2
        x = xax.to_val(col)
        y = yax.to_val(row)
        out.append({"x": round(x, 2) + 0.0, "y": y, "lo": yax.to_val(row + py), "hi": yax.to_val(row - py),
                    "px": [col, row], "px_lo": row + py, "px_hi": row - py,
                    "note": f"marker {h:.0f}x{w:.0f} px of {full:.0f}; x from its centre column (x misfit "
                            f"{xax.misfit:.1f} px, frame-to-label offset {frame_off:.1f} px), y misfit {yax.misfit:.1f} px"})
    return out
