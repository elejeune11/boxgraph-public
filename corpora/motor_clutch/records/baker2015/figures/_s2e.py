"""Supp. Fig. 2e: cantilever deflection against indentation depth, example curves for single fibres.
An embedded, blurred bitmap with grey frame and dashed grey gridlines.

- y axis: rows where a grey horizontal line crosses at least 20% of the plot width once the legend box
  is blanked (frame bottom = 0.0, dashed gridlines 0.5, 1.0, 1.5, frame top = 2.0), matched in order.
- x axis: the centres of the printed labels 0, 200, 400, 600 under the axis, matched in order.
- curves: pixels of the series colour; in the column of each requested x (and two either side) the
  run of that colour gives the row; the interval is the run's half-height, the misfits and the
  local slope times the x misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YVALS = [0, 0.5, 1.0, 1.5, 2.0]
XVALS = [0, 200, 400, 600]


def grey(img):
    f = img.astype(float)
    return (f.mean(axis=2) < 215) & (f.max(axis=2) - f.min(axis=2) < 25)


def axes(img):
    g = grey(img)
    H, W = g.shape
    vs = [v for v in K.vlines(g, int(0.5 * H)) if v[1] - v[0] < 20]
    left, right = min(vs, key=lambda v: v[0]), max(vs, key=lambda v: v[0])
    inner = [v for v in K.vlines(g, int(0.12 * H)) if left[1] + 10 < v[0] < right[0] - 10 and v[1] - v[0] < 20]
    legend = None
    if len(inner) >= 2:
        l0, l1 = min(inner, key=lambda v: v[0]), max(inner, key=lambda v: v[0])
        legend = (l0[0] - 5, l1[1] + 5, min(l0[2], l1[2]) - 5, max(l0[3], l1[3]) + 5)
        g = g.copy()
        g[legend[2]:legend[3], legend[0]:legend[1]] = False
    frac = g[:, left[1] + 3:right[0] - 3].mean(axis=1)
    rows = [(a + b) / 2.0 for a, b in K.runs(np.nonzero(frac > 0.2)[0])]
    rows = [r for r in rows if left[2] - 15 <= r <= left[3] + 60]
    yax = K.Axis(sorted(rows, reverse=True), YVALS, what=f"y lines {rows}")
    base = max(rows)
    txt = K.dark(img, 120.0, 60.0)
    band = txt[int(base) + 40:int(base) + 130, :]
    band[:, : max(left[0] - 40, 0)] = False                  # the y labels and the axis title
    cols = np.nonzero(band.any(axis=0))[0]
    groups = []
    for a, b in K.runs(cols):
        if groups and a - groups[-1][1] <= 25:
            groups[-1] = (groups[-1][0], b)
        else:
            groups.append((a, b))
    centres = [(a + b) / 2.0 for a, b in groups if b - a >= 10]
    xax = K.Axis(centres, XVALS, what=f"x labels {centres}")
    return yax, xax, legend


def curve(img, at, rgb, tol):
    yax, xax, legend = axes(img)
    m = K.near(img, rgb, tol)
    if legend is not None:
        m[legend[2]:legend[3], legend[0]:legend[1]] = False
    out = []
    for x in at:
        c = int(round(xax.to_px(float(x))))
        cents, halfs = [], []
        for cc in range(c - 2, c + 3):
            rr = np.nonzero(m[:, cc])[0]
            if len(rr) == 0:
                continue
            a, b = max(K.runs(rr), key=lambda t: t[1] - t[0])
            cents.append((a + b) / 2.0)
            halfs.append((b - a + 1) / 2.0)
        if not cents:
            out.append({"x": float(x), "y": None, "note": "no pixel of the curve's colour in this column"})
            continue
        row = float(np.median(cents))
        slope = abs(cents[-1] - cents[0]) / max(len(cents) - 1, 1)
        prec = max(halfs) + 1.0 + yax.misfit + slope * (xax.misfit + 1.0)
        out.append({"x": float(x), "y": yax.to_val(row), "lo": yax.to_val(row + prec), "hi": yax.to_val(row - prec),
                    "px": [float(c), row], "px_lo": row + prec, "px_hi": row - prec,
                    "note": f"run half-height {max(halfs):.0f} px, slope {slope:.1f} px/px, "
                            f"y misfit {yax.misfit:.1f} px, x misfit {xax.misfit:.1f} px"})
    return out
