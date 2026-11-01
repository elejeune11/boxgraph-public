"""Fig. 1 G (PDF p. 2): histograms drawn as red outlined, hatched bars.

Calibration from the image: the frame; x from the long ticks on the bottom edge and the frame
edges where they lie on the tick grid; y from the ticks on the left edge (long and short) and
the frame edges where they lie on the grid. The caller gives the matched labels.
Bars: in the red mask, each column's top stroke (the first red run from the top) gives the bar
top at the centre of the stroke. Bar edges are the vertical outline strokes: columns that are
red over at least 85% of their height below their own top stroke (hatching crosses a column
only in short pieces). The frame's left edge closes the first bar. A bar's value is the median
top-stroke centre over the middle half of its columns; it is reported at the centre of the bin
between its two edges (in the x axis unit). Its interval: half the stroke thickness, the spread
of the top over the bar, the y calibration misfit and 1 px.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("gardel_lib", Path(__file__).with_name("_lib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def read_hist(img, xv, xstep, yv, ystep, level=120, min_height=4):
    fr = L.frame(img)
    tx = L.ticks(img, fr["bottom"], (fr["left"] + 15, fr["right"] - 15), "x", -1, 160, lw=fr["lw_row"], level=level)
    ty = L.ticks(img, fr["left"], (fr["top"] + 15, fr["bottom"] - 15), "y", 1, 160, lw=fr["lw_col"], level=level)
    ax, bx, mx, dx = L.grid_axis(tx, fr["left"], fr["right"], xv[0], xv[1], xstep)
    ay, by, my, dy = L.grid_axis(ty, fr["bottom"], fr["top"], yv[0], yv[1], ystep)
    red = L.hue_mask(img, "red", min_sat=60)
    lw = fr["lw_row"]
    top_in = int(fr["top"] + lw)
    bot_in = int(fr["bottom"] - lw / 2 - 2)
    c0, c1 = int(fr["left"] + lw / 2 + 2), int(fr["right"] - lw / 2 - 2)
    tops = np.full(red.shape[1], np.nan)
    thick = np.full(red.shape[1], np.nan)
    vert = np.zeros(red.shape[1], bool)
    for c in range(c0, c1):
        col = red[top_in:bot_in, c]
        on = np.where(col)[0]
        if len(on) == 0:
            continue
        s = on[0]
        e = s
        while e + 1 < len(col) and col[e + 1]:
            e += 1
        tops[c] = top_in + (s + e) / 2.0
        thick[c] = e - s + 1
        below = col[s:]
        if len(below) > 30 and below.mean() > 0.85:
            vert[c] = True
    found = [(s + e - 1) / 2.0 for s, e in L.runs(vert)]
    # the bins are of equal width: fit a regular grid to the outline strokes found (a black
    # tick drawn over an outline can hide it), then take every grid edge
    d = np.diff(found)
    med = float(np.median(d))
    w0 = float(np.median([x for x in d if 0.8 * med < x < 1.2 * med]))
    f = np.array(found)
    k = np.zeros(len(f))
    keep = np.ones(len(f), bool)
    last = 0
    for i in range(1, len(f)):
        q = (f[i] - f[last]) / w0
        if abs(q - round(q)) > 0.25 or round(q) == 0:
            keep[i] = False          # not on the bin grid: a hatching or tick artefact
            continue
        k[i] = k[last] + round(q)
        last = i
    w, e0 = np.polyfit(k[keep], f[keep], 1)
    keep &= np.abs(f - (e0 + w * k)) < 0.25 * w
    w, e0 = np.polyfit(k[keep], f[keep], 1)
    grid_mis = float(np.max(np.abs(f[keep] - (e0 + w * k[keep]))))
    # the top stroke's own thickness: where hatching joins the stroke the first red run is
    # longer; the stroke centre is then half the typical thickness below the run's start
    th_typ = float(np.nanmedian(thick))
    starts = tops - (thick - 1) / 2.0
    tops = np.where(thick > 1.3 * th_typ, starts + (th_typ - 1) / 2.0, tops)
    thick = np.where(thick > 1.3 * th_typ, th_typ, thick)
    has_red = np.where(~np.isnan(tops))[0]
    kmin = int(np.ceil((fr["left"] - e0) / w - 0.3))
    kmax = int(np.floor((has_red[-1] - e0) / w + 0.7)) if len(has_red) else kmin
    edges = [e0 + w * j for j in range(kmin, kmax + 1)]
    if edges[0] > fr["left"] + 5:
        edges.insert(0, e0 + w * (kmin - 1))
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        if b - a < 10:
            continue
        lo_c, hi_c = int(a + 0.25 * (b - a)), int(b - 0.25 * (b - a))
        t = tops[lo_c:hi_c + 1]
        t = t[~np.isnan(t)]
        if len(t) < min_height:
            continue
        r = float(np.median(t))
        th = float(np.nanmedian(thick[lo_c:hi_c + 1]))
        if th < 0.5 * th_typ:
            continue        # only a sliver of red at the axis: no bar top drawn in this bin
        spread = float(np.max(t) - np.min(t))
        x = ((a + b) / 2.0 - ax) / bx
        y = (r - ay) / by
        e_px = th / 2.0 + spread / 2.0 + my + 1.0
        e = e_px / abs(by)
        note = f"bar between columns {a:.0f} and {b:.0f} (x {(a - ax) / bx:.2f} to {(b - ax) / bx:.2f}), top stroke {th:.0f} px"
        if not out:
            note += (f"; x axis {dx}; y axis {dy}; bin grid fitted to {int(keep.sum())} outline strokes, "
                     f"width {w:.1f} px, misfit {grid_mis:.1f} px")
        out.append({"x": float(x), "y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [(a + b) / 2.0, r],
                    "px_lo": r - e_px, "px_hi": r + e_px, "note": note})
    return out
