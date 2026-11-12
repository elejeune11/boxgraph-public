"""Shared reading code for Fig. 4e (PDF p. 8): pressure (Pa) against time (s) from the grid model of the device,
control (black filled circles, black line) and IL-1beta (grey filled circles, grey line), one point at each
second 1 ... 7. Raster figure read at 900 dpi.

Calibration (_axes.py): axis lines are the darkest column / row in the box; y ticks (left, >= 15 px) are matched
to 40, 30, 20, 10, 0 and x ticks (down, >= 15 px) to 0, 1, ..., 7.

Markers: pixels darker than 80 (black) or of grey 150-215 (grey), whose distance transform exceeds 14 px (the
markers have a radius of about 26 px, the lines are about 6 px thick); local maxima at least 30 px apart. The
legend's two markers (upper right, above the 30.2 Pa level and right of t = 1.5 s) are left out. At each x in
`at` the marker whose centre is within 25 px of the x tick is taken; if there is none (the grey marker at t = 1 s
is hidden behind the black one) y is None. Interval: +/- (3 px + misfit).
"""

import numpy as np
from scipy import ndimage as ndi
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_axes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def calibrate(image):
    g = A.gray(image)
    ya, xa = A.frame(g, (250, 2300, 30, 1800))
    ty = A.ticks_left(g, ya, (30, xa[1] + 5), 15)
    tx = A.ticks_down(g, xa, (ya[0] - 5, 2300), 15)
    ay, by, my = A.fit(ty, [40, 30, 20, 10, 0])
    ax, bx, mx = A.fit(tx, list(range(8)))
    return dict(g=g, ay=ay, by=by, my=my, ax=ax, bx=bx, mx=mx, ya=ya, xa=xa)


def read_series(image, at, which):
    cal = calibrate(image)
    g = cal["g"]
    m = (g < 80) if which == "black" else ((g >= 150) & (g <= 215))
    r_leg = int((30.2 - cal["ay"]) / cal["by"])
    c_leg = int((1.5 - cal["ax"]) / cal["bx"])
    m[:r_leg, c_leg:] = False
    m[cal["xa"][0] - 3:, :] = False
    m[:, : cal["ya"][1] + 3] = False
    dt = ndi.distance_transform_edt(m)
    pk = A.peaks(dt, 14, 30)
    out = []
    for x in at:
        c = (x - cal["ax"]) / cal["bx"]
        near = [(r, cc) for r, cc in pk if abs(cc - c) <= 25]
        if not near:
            out.append({"x": x, "y": None, "note": f"no {which} marker at t = {x:g} s (hidden behind the other series' marker)"})
            continue
        r, cc = near[0]
        tol = 3 + cal["my"]
        y = cal["ay"] + cal["by"] * r
        lo, hi = sorted((cal["ay"] + cal["by"] * (r + tol), cal["ay"] + cal["by"] * (r - tol)))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(cc), float(r)], "px_lo": r + tol, "px_hi": r - tol,
                    "note": f"{which} marker centre (radius {dt[r, cc]:.0f} px); misfit {cal['my']:.2f} px (y), {cal['mx']:.2f} px (x)"})
    return out
