"""Shared reading for Supp. Fig. 3c (PDF p. 25): apical area (dashed) and AP size (solid) of cells
along the ventral midline in anterior (purple), mid (orange) and posterior (light blue) 60 um bins,
relative to initial, against time; one line per bin over n = 3 embryos, with min-max bands (gnuplot,
see _gp.py).

Calibration: y: the major inward ticks on the left frame line carry the printed 1.2, 1, 0.8, 0.6,
0.4, 0.2 (top to bottom) and the bottom frame line 0; x: the frame lines carry the printed -5 and 6,
the inward ticks on the bottom frame line -4 to 5.
The two lines of a region share its colour. From t = 1 min on, the AP size (solid) lies well above
the area (dashed) for every region. At a time t, in each column within +-15 px, the runs of the
colour at least 12 px tall are found (the thin hatching lines of the bands are shorter); the uppermost
run is the AP size (the solid line is continuous, so it is the top run in every column); the
lowermost is the area, taken only in columns holding two or more runs (in a dash gap the only run is
the solid line); each value is the median centre over those columns.
95% interval: 2 px, the calibration misfit and half the line's half thickness (as _gp.read_lines),
plus the spread (half the range) of the column centres.
"""
import numpy as np

import _gp

YLABELS = [(1.2, "tick:0"), (1.0, "tick:1"), (0.8, "tick:2"), (0.6, "tick:3"), (0.4, "tick:4"),
           (0.2, "tick:5"), (0.0, "frame-bottom")]
XLABELS = [(-5.0, "frame-left")] + [(float(v), f"tick:{k}") for k, v in enumerate(range(-4, 6))] + [(6.0, "frame-right")]
COLOURS = {"anterior": (148, 0, 211), "mid": (230, 159, 0), "posterior": (86, 180, 233)}


def read(image, at, region, which):
    cal = _gp.calibrate(image, YLABELS, XLABELS)
    fr = cal["fr"]
    m = _gp._inside(_gp.colour_mask(image, COLOURS[region], 40), fr)
    # the legend lies above 1.05 (right) and below 0.45 left of t = -2: the rows and times read avoid it
    out = []
    for x in at:
        c0 = int(round(_gp.to_col(cal, float(x))))
        cents, halves = [], []
        for c in range(c0 - 15, c0 + 16):
            runs = [r for r in _gp.column_runs(m[:, c]) if r[1] - r[0] + 1 >= 12]
            if len(runs) < (2 if which == "lower" else 1):
                continue
            r = runs[0] if which == "upper" else runs[-1]
            cents.append((r[0] + r[1]) / 2.0)
            halves.append((r[1] - r[0] + 1) / 2.0)
        if len(cents) < 5:
            out.append({"x": float(x), "y": None, "note": "the two lines of this colour not both found here"})
            continue
        row = float(np.median(cents))
        spread = (max(cents) - min(cents)) / 2.0
        e = 2.0 + max(cal["my"], 0.5) + 0.5 * float(np.median(halves)) + spread
        y = _gp.to_val(cal, row)
        lo, hi = sorted([_gp.to_val(cal, row + e), _gp.to_val(cal, row - e)])
        out.append({"x": float(x), "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c0), row],
                    "note": f"{which} run of the colour over {len(cents)} columns; y {cal['ny']} marks misfit "
                            f"{cal['my']:.2f} px, x {cal['nx']} marks misfit {cal['mx']:.2f} px"})
    return out
