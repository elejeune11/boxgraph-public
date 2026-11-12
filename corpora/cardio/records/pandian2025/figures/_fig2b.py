"""Shared reading code for Fig. 2b (PDF p. 5): % volume coverage of the segmented network against the
binarization threshold, three polylines in grey levels: Network-1 light grey (core grey about 169),
Network-2 mid grey (about 122), Network-3 black (about 5); a dotted black line marks 100 %.

The figure is a raster image; at 900 dpi one y unit (1 %) is about 7.1 px and the lines are about
27 px thick.

Calibration (_axes.py): axis lines are the darkest column / row; major ticks are dark runs at least
20 px outside the axes, matched in order to the printed labels 200, 150, 100, 50, 0 (y) and 0.0, 0.1,
0.2, 0.3, 0.4 (x). The largest misfit widens every interval.

Reading a curve at x: in the image column of x (the mean of the columns x-2..x+2 px), the runs of
pixels whose grey lies in the curve's band are found (runs shorter than 8 px are the anti-aliased
edges of a darker line and are dropped). Runs within 12 px of the 100 % dotted line, and runs above
the 188 % level (the legend), are dropped. The value is the centre of the run. Interval: +/- (3 px +
misfit). Where the run is shorter than 80 % of the curve's own thickness (median run length over the
plot), the curve is partly covered by another one;
a run longer than the thickness (steep segment, vertex, line end) widens the interval by half the
excess; a run that reaches the x axis line (Network-3 at 0.4) is centred half a thickness below its top
edge, +/- half a thickness; its centre is then taken half a thickness from its
free edge and the interval is widened to +/- half a thickness; the note says so. A column with no run
gives y = None.
"""

import numpy as np
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_axes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

BANDS = {"n1": (148, 200), "n2": (100, 147), "n3": (0, 60)}


def calibrate(image):
    g = A.gray(image)
    ya, xa = A.frame(g, (250, 2600, 60, 1600))
    ty = A.ticks_left(g, ya, (60, xa[1] + 5), 20)
    tx = A.ticks_down(g, xa, (ya[0] - 5, 2600), 20)
    ay, by, my = A.fit(ty, [200, 150, 100, 50, 0])
    ax, bx, mx = A.fit(tx, [0.0, 0.1, 0.2, 0.3, 0.4])
    return dict(g=g, ay=ay, by=by, my=my, ax=ax, bx=bx, mx=mx, ya=ya, xa=xa)


def col_runs(cal, c, band):
    g = cal["g"]
    prof = g[:, c - 2: c + 3].mean(axis=1)
    lo, hi = band
    r_top = int(round((188 - cal["ay"]) / cal["by"]))
    r_100 = (100 - cal["ay"]) / cal["by"]
    out = []
    for a, b in A.runs((prof >= lo) & (prof <= hi)):
        if b - a < 8 or a < r_top or a > cal["xa"][0] - 4:
            continue
        if abs((a + b - 1) / 2.0 - r_100) < 12:
            continue
        out.append((a, b))
    return out, prof


def thickness(cal, band):
    lens = []
    for c in range(cal["ya"][1] + 20, cal["g"].shape[1] - 80, 15):
        rr, _ = col_runs(cal, c, band)
        lens += [b - a for a, b in rr]
    return float(np.median(lens)) if lens else 0.0


def read_curve(image, at, key):
    cal = calibrate(image)
    band = BANDS[key]
    T = thickness(cal, band)
    out = []
    for x in at:
        c = int(round((x - cal["ax"]) / cal["bx"]))
        rr, prof = col_runs(cal, c, band)
        if not rr:
            out.append({"x": x, "y": None, "note": f"no run of the curve's grey in column {c}"})
            continue
        a, b = max(rr, key=lambda ab: ab[1] - ab[0])
        L = b - a
        note = f"run {a}-{b} ({L} px; curve thickness {T:.0f} px); misfit {cal['my']:.2f} px"
        if b >= cal["xa"][0] - 2:
            # the line lies on the x axis line: only its top edge is seen
            r = a + T / 2.0
            tol = T / 2.0 + cal["my"]
            note += "; the line merges with the x axis line: centre taken half a thickness below its top edge"
        elif L >= 0.8 * T:
            r = (a + b - 1) / 2.0
            # a run longer than the line is thick lies on a steep segment, a vertex or the line's end:
            # the centreline value there is known only to within the excess
            tol = 3 + cal["my"] + max(0.0, (L - T) / 2.0)
            if L > 1.3 * T:
                note += "; steep segment, vertex or line end: interval widened by half the run's excess over the thickness"
        else:
            # the covered side is the one where the neighbouring pixel is darker than the band
            above = prof[a - 2] if a >= 2 else 255
            below = prof[b + 1] if b + 1 < len(prof) else 255
            if above < band[0]:
                r = b - T / 2.0
            elif below < band[0]:
                r = a + T / 2.0
            else:
                r = (a + b - 1) / 2.0
            tol = T / 2.0 + cal["my"]
            note += "; partly covered by another curve: centre taken half a thickness from the free edge"
        y = cal["ay"] + cal["by"] * r
        lo, hi = sorted((cal["ay"] + cal["by"] * (r + tol), cal["ay"] + cal["by"] * (r - tol)))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(c), r], "px_lo": r + tol, "px_hi": r - tol,
                    "note": note})
    return out
