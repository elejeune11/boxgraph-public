"""Shared reading code for Fig. 3c (PDF p. 6), "Mesh Sensitivity": three black filled circles (left axis,
maximum velocity, um/s) and three grey filled circles (right axis, time required for a converged solution,
s) against the element count, joined by thin lines; a dotted grey vertical line marks the chosen mesh.
Raster figure, read at 1500 dpi.

Calibration (_axes.py): the left axis line is the darkest column, the x axis the darkest row (inside
the plot frame). Left y ticks (outward, >= 20 px): matched to 2000, 1500, 1000, 500, 0. The right axis
carries the same labels 2000 ... 0 on the same rows (its ticks are drawn level with the left ones; the
code checks this by finding the right ticks, outward to the right, and uses them for the grey points).
x ticks (outward, >= 20 px, a tick every 1e6, labelled 0.0, 5.0e6, 1.0e7, 1.5e7): the 16 ticks are
matched to 0, 1e6, ..., 1.5e7.

Markers: pixels darker than 80 (black) or with grey 140-205 (grey points) inside the plot frame; their
distance transform exceeds 15 px only inside a marker (the joining lines and the dotted line are under
8 px thick); each local maximum is a marker centre. Interval: +/- (3 px + misfit) in y; the marker
radius is about 28 px.
"""

import numpy as np
from scipy import ndimage as ndi
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_axes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def ticks_right(g, col, rows, min_len, dark=110):
    hits = []
    for r in range(*rows):
        n, c = 0, col
        while c < g.shape[1] and g[r, c] < dark:
            n += 1
            c += 1
        hits.append(n >= min_len)
    return [rows[0] + (a + b - 1) / 2.0 for a, b in A.runs(hits)]


def calibrate(image):
    g = A.gray(image)
    H, W = g.shape
    ya, xa = A.frame(g, (550, 1500, 200, 2100))
    # right axis: the darkest column right of the plot
    cs = (g[300:1900, 2100:2500] < 110).sum(axis=0)
    rc = 2100 + int(np.flatnonzero(cs >= 0.85 * cs.max())[-1])
    ty = A.ticks_left(g, ya, (200, xa[1] + 5), 20)
    tr = ticks_right(g, rc + 1, (200, xa[1] + 5), 20)
    tx = A.ticks_down(g, xa, (ya[0] - 5, rc + 5), 20)
    labels = [2000, 1500, 1000, 500, 0]
    ay, by, my = A.fit(ty, labels)
    ar, br, mr = A.fit(tr, labels)
    ax, bx, mx = A.fit(tx, [k * 1e6 for k in range(16)])
    return dict(g=g, ay=ay, by=by, my=my, ar=ar, br=br, mr=mr, ax=ax, bx=bx, mx=mx,
                box=(ya[1] + 3, rc - 3, 200, xa[0] - 3))


def read_points(image, which):
    cal = calibrate(image)
    g = cal["g"]
    c0, c1, r0, r1 = cal["box"]
    m = np.zeros_like(g, bool)
    sub = g[r0:r1, c0:c1]
    m[r0:r1, c0:c1] = (sub < 80) if which == "black" else ((sub >= 140) & (sub <= 205))
    dt = ndi.distance_transform_edt(m)
    a, b, mis = (cal["ay"], cal["by"], cal["my"]) if which == "black" else (cal["ar"], cal["br"], cal["mr"])
    out = []
    for r, c in sorted(A.peaks(dt, 15, 40), key=lambda rc: rc[1]):
        x = cal["ax"] + cal["bx"] * c
        tol = 3 + mis
        y = a + b * r
        lo, hi = sorted((a + b * (r + tol), a + b * (r - tol)))
        out.append({"x": round(x, -3), "y": y, "lo": lo, "hi": hi, "px": [float(c), float(r)],
                    "px_lo": r + tol, "px_hi": r - tol,
                    "note": f"{which} marker at element count {x:.4g} (x misfit {cal['mx']:.2f} px); "
                            f"radius {dt[r, c]:.0f} px; y misfit {mis:.2f} px"})
    return out
