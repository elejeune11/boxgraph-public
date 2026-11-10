"""Fig. 5P(ii), bottom (p. 6): average viable cell count against normalized radius R, for the perfused
annulus (panel 1), the media control (2) and the PBS control (3); green lines (N = 3 constructs).

Calibration. y: only panel 1 has a labelled y axis (its long dark vertical line, ticks out to the left,
matched to 0, 20, 40, 60 from the bottom; the 0 tick is the x axis). Panels 2 and 3 have no y axis of
their own; they stand on the same thick x axis row and have the same height, and are read with panel 1's
y calibration (an assumption of a shared scale, stated in each reading's note). x: the thick x axis row
holds three separate dark segments, one per panel, numbered from the left; in each, the ticks below it
are matched to 0.0, 0.5, 1.0 (the long ticks; minor ticks, if any, are shorter).

The green line (within 70 of (40, 140, 60); the grey core-region shading and its dashed borders are not
green) is traced as in _curves.py from where it stands clear of the x axis (R = 0.5, 0.95, 0.92). Where the line lies on the thick black x axis, the
interval extends under it (_curves.py).
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _curves as K  # noqa: E402

GREEN = (40, 140, 60)


def calibrate(image, panel):
    rows, cols = C.frame(image, 110, 0.15)
    xr, yc = rows[-1], cols[0]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 15, 0, xr[2] + 5, 110)]
    if len(yt) != 4:
        raise RuntimeError(f"expected 4 y ticks, found {yt}")
    ax_y = C.Axis(yt, [60, 40, 20, 0])
    g = C.gray(image) < 110
    segs = [(s, e) for s, e in C.runs(g[int(xr[0])]) if e - s > 300]
    if len(segs) != 3:
        raise RuntimeError(f"expected 3 x axis segments, found {segs}")
    s, e = segs[panel - 1]
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 20, s, e, 110, 16)]
    if len(xt) != 3:
        raise RuntimeError(f"expected 3 x ticks in panel {panel}, found {xt}")
    ax_x = C.Axis(xt, [0.0, 0.5, 1.0])
    box = (s, 0, e, xr[1] + 1)
    return ax_x, ax_y, box


def read(image, at, panel):
    ax_x, ax_y, box = calibrate(image, panel)
    seed = {1: 0.5, 2: 0.95, 3: 0.92}[panel]  # where each line stands clear of the x axis
    out = K.read_traced(image, at, ax_x, ax_y, box, GREEN, 70, seed, pick="lowest", max_gap=20)
    if panel != 1:
        for r in out:
            r["note"] = (r.get("note") or "") + "; y scale taken from panel 1 (this panel has no y axis of its own)"
    return out


_ = np
