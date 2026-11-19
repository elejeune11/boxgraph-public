"""Fig. 3E (PDF p. 7): Young's modulus (kPa) of alginate capsules against alginate concentration,
box plots with points (1% green, 1.5% red, 2% blue, 2.5% orange). The points overlap too much to
be told apart (52 points in the 1.5% box), so each box is read: its middle line (the legend does
not say whether it is the median or the mean) with the box's lower and upper edges as the bar.

Calibration (_cal.py): x ticks below the axis, one per box, matched to the labels 1, 1.5, 2,
2.5 (step 0.5 from the leftmost tick); y ticks left of the axis indexed from the x axis
crossing, labelled 0 to 35 kPa on every second tick; the step between the ticks found is
2.5 kPa (the unlabelled ticks between labels are as long as the labelled ones).
Box lines: in the box's colour (sampled from the image), rows whose colour run spans at least
80% of the box width, searched within 30% of the tick spacing of each x tick; the box's widest
run gives its width. The three such lines are the box top, the middle line and the box bottom;
points lying on a line can lengthen it but not create one wider than the box. Interval: the
line's thickness plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

COLOURS = [(25, 135, 55), (225, 30, 30), (20, 105, 180), (245, 125, 20)]


def read(image, at):
    L = C.axes_lines(image)
    yo = (L["xr0"] + L["xr1"]) / 2
    ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, 2.5)
    xt = sorted(C.ticks_x(L))
    xa = C.calibrate(xt, 1.0, 0.5)
    sp = float(np.median(np.diff(xt)))
    out = []
    for t, rgb in zip(xt, COLOURS):
        m = C.colour(image, rgb, 70.0)
        a, b = int(t - 0.35 * sp), int(t + 0.35 * sp)
        sub = m[:L["xr0"] - 3, a:b]
        runs = [C.longest_run(sub[r], gap=3)[0] for r in range(sub.shape[0])]
        width = max(runs)
        rows = [r for r, n in enumerate(runs) if n >= 0.8 * width]
        lines = [(g[0] + g[-1]) / 2 for g in C.groups(rows, gap=2)]
        thick = [(g[-1] - g[0] + 1) / 2 for g in C.groups(rows, gap=2)]
        if len(lines) != 3:
            out.append({"x": xa.val(t), "y": None, "note": f"found {len(lines)} box lines, not 3"})
            continue
        top, mid, bot = lines
        p = C.point(xa, ya, t, mid, 2, thick[1] + 1, bar=(top, bot), bar_px=max(thick[0], thick[2]) + 1,
                    note=f"box width {width} px; lines at rows {[round(v) for v in lines]}")
        p["x"] = xa.val(t)
        out.append(p)
    return out
