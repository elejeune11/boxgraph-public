"""Fig. 3A (p. 4): the solid black "Theory" curve, the flat-wrinkle boundary of Eq. 4,
read as the mismatch strain eM (horizontal axis, linear 0 ... 0.6) at given modulus ratios
mu_f/mu_s (vertical axis, logarithmic 10^-1 ... 10^5).

The reading's x is the modulus ratio (the plot's vertical axis) and its y the mismatch
strain (the plot's horizontal axis), so that the curve can be compared with Eq. 4, which
gives eM from the ratio.

Calibration: the frame and the tick marks are found with boxgraph.digitize.find_axes.
Horizontal: the y axis line is eM = 0 and the six evenly spaced ticks are 0.1 ... 0.6 (the
last on the right frame edge). Vertical: the bottom frame edge is labelled 10^-1 and the top
edge 10^5; the decade ticks 10^0 ... 10^4 between them are matched to the found tick marks
(each decade position predicted from the frame, then snapped to the nearest tick within 6 px;
a decade with no tick found, where the curve hugs the axis, is left out of the fit).

The curve: at the row of each ratio, the dark (black, unsaturated) pixels right of the
frame's tick zone; the curve is the first dark run. Over the rows within the vertical
calibration misfit of that row, the run's leftmost and rightmost columns bound the value.
Where the curve lies within the tick zone (ratios above ~200) it cannot be read.
"""
import math
import sys

import numpy as np


def _digitize():
    try:
        from boxgraph import digitize as D
    except ImportError:  # run outside the package
        sys.path.insert(0, ".")
        from boxgraph import digitize as D
    return D


def _fit(px, vals):
    px, vals = np.asarray(px, float), np.asarray(vals, float)
    b, a = np.polyfit(px, vals, 1)
    mis = float(np.max(np.abs(px - (vals - a) / b)))
    return a, b, max(mis, 0.5)


def calibrate(img):
    D = _digitize()
    fa = D.find_axes(img)
    c0, r_top, c_right, r_bot = fa.box
    x_col0 = fa.y_axis_col
    xt = sorted(fa.x_ticks)
    if len(xt) != 6:
        raise ValueError(f"expected six x ticks 0.1 ... 0.6, found {xt}")
    ax, bx, mx = _fit([x_col0] + xt, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    r_bottom = fa.x_axis_row
    r_topedge = r_top - 0.5
    step = (r_bottom - r_topedge) / 6.0
    rows, logs = [r_bottom, r_topedge], [-1.0, 5.0]
    for k in range(1, 6):
        pred = r_bottom - k * step
        near = [c for c in fa.y_candidates if abs(c - pred) <= 6.0]
        if near:
            rows.append(min(near, key=lambda c: abs(c - pred)))
            logs.append(-1.0 + k)
    ay, by, my = _fit(rows, logs)
    return (ax, bx, mx), (ay, by, my), (c0, r_top, c_right, r_bot)


def read(image, at):
    (ax, bx, mx), (ay, by, my), box = calibrate(image)
    img = image.astype(int)
    gray = img.mean(2)
    sat = img.max(2) - img.min(2)
    dark = (gray < 110) & (sat < 60)
    c0 = int(round(box[0]))
    tick_zone = 45  # inward tick marks reach about 35 px from the frame
    out = []
    for ratio in at:
        row = (math.log10(ratio) - ay) / by
        r_lo, r_hi = int(math.floor(row - my)), int(math.ceil(row + my))
        def first_run(r):
            line = dark[r, c0 + tick_zone:]
            on = np.nonzero(line)[0]
            if len(on) == 0:
                return None
            s = e = on[0]
            while e + 1 < len(line) and line[e + 1]:
                e += 1
            return s + c0 + tick_zone, e + c0 + tick_zone

        lefts, rights, centre = [], [], None
        mid = first_run(int(round(row)))
        if mid is not None:
            centre = (mid[0] + mid[1]) / 2.0
            for r in range(r_lo, r_hi + 1):
                run = first_run(r)
                # the same curve in the neighbouring rows: a run that touches the middle row's run
                if run is not None and run[0] <= mid[1] + 3 and run[1] >= mid[0] - 3:
                    lefts.append(run[0])
                    rights.append(run[1])
        if not lefts or centre is None:
            out.append({"x": ratio, "y": None, "note": "curve not found at this ratio"})
            continue
        if lefts[0] <= c0 + tick_zone + 1:
            out.append({"x": ratio, "y": None, "note": "curve inside the tick zone of the left frame"})
            continue
        # at least half the line's thickness (about 16 px) either side of the centre
        lo_c = min(min(lefts), centre - 8.0) - mx
        hi_c = max(max(rights), centre + 8.0) + mx
        y = ax + bx * centre
        out.append({"x": ratio, "y": float(y), "lo": float(ax + bx * lo_c), "hi": float(ax + bx * hi_c),
                    "px": [float(centre), float(row)],
                    "note": f"curve run {min(lefts)}-{max(rights)} px over rows {r_lo}-{r_hi}; "
                            f"misfit x {mx:.1f} px, y {my:.1f} px"})
    return out
