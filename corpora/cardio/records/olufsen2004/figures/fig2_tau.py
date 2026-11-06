"""Fig. 2 (PDF p. 8): the blue curve tau(R). Calibration in _fig2.py.

At each R the value is the centre of the blue run in that pixel column (below the legend, so the
legend's blue sample is never taken). The interval adds, in value units:
  * the calibration misfit of both axes (the x misfit through the local slope);
  * one pixel of centre placement, and one column of x placement through the local slope;
  * the curve is drawn as a polyline (kinks are visible): the largest offset of the centre from
    the chord through the centres 50 columns either side (more than one vertex spacing), a bound on how far the drawn polyline
    can sit from a smooth curve through its vertices;
  * where the blue run touches green or red ink (a time-scale line drawn over it), the hidden
    side is widened to the far edge of that ink.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("_fig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

HALF_WINDOW = 50  # columns either side; the polyline's vertices are about 40-50 columns apart


def _centre(blue, col, r0, r1):
    runs = _f.runs_in_col(blue, col, r0, r1)
    if not runs:
        return None
    s, e = max(runs, key=lambda se: se[0])  # the lowest blue run: the curve lies below the legend
    return s, e


def read(image, at):
    cal = _f.calibrate(image)
    blue = _f.colour(image, "blue")
    other = _f.colour(image, "red") | _f.colour(image, "green")
    left, top, right, bot = cal["box"]
    # rows below the legend frame (the legend is the black rectangle in the upper right)
    k = cal["k"]
    legend_rows = [r for r in range(top + 5, bot) if k[r, int(right) - 200:int(right) - 40].mean() > 0.9]
    legend_bottom = max(legend_rows) + 2 if legend_rows else top
    out = []
    for x in at:
        x = float(x)
        c = int(round(_f.col_of(cal, x) - 0.5))
        r0 = legend_bottom if c > (right - 760) else top + 2
        se = _centre(blue, c, r0, bot - 1)
        if se is None:
            out.append({"x": x, "y": None, "note": "no blue ink in this column (curve above the plot box)"})
            continue
        s, e = se
        row = (s + e) / 2 + 0.5
        cen = {}
        for dc in (-HALF_WINDOW, HALF_WINDOW):
            q = _centre(blue, c + dc, r0, bot - 1)
            if q is not None:
                cen[dc] = (q[0] + q[1]) / 2 + 0.5
        slope = (cen[HALF_WINDOW] - cen[-HALF_WINDOW]) / (2 * HALF_WINDOW) if len(cen) == 2 else 0.0
        chord = abs(row - (cen[HALF_WINDOW] + cen[-HALF_WINDOW]) / 2) if len(cen) == 2 else 0.0
        half_px = cal["ymis"] + abs(slope) * cal["xmis"] + 1.0 + abs(slope) * 1.0 + chord
        lo_row, hi_row = row + half_px, row - half_px  # lo value is the larger row
        note = f"slope {slope:.2f} px/px, chord offset {chord:.1f} px"
        # hidden by another line drawn over the curve?
        above = other[max(s - 3, 0):s, c].any()
        below = other[e + 1:e + 4, c].any()
        if above or below:
            if above:
                t = s - 1
                while t > 0 and other[t, c]:
                    t -= 1
                hi_row = min(hi_row, t)
            if below:
                t = e + 1
                while t < other.shape[0] - 1 and other[t, c]:
                    t += 1
                lo_row = max(lo_row, t)
            note += "; touches a time-scale line, the hidden side widened to its far edge"
        y = float(_f.val_of_row(cal, row))
        lo = float(_f.val_of_row(cal, lo_row))
        hi = float(_f.val_of_row(cal, hi_row))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [c + 0.5, row],
                    "px_lo": hi_row, "px_hi": lo_row, "note": note})
    return out
