"""Supplemental Fig. 2 (PDF p. 13): the dark diagonal line (the caption calls it the line of perfect agreement; the
legend labels it 'R2 Linear = 0,690'), read at the requested x (observer 2 MBV).

Calibration as in _sfig2.py (y from the grey gridlines, x from the centres of the x labels). The line is the only
dark (channel mean < 100) ink inside the plot area besides nothing else: the rings are coloured, the gridlines and
axes light grey, the text outside the plot. At the column of each requested x, the dark rows inside the plot
(between the top gridline's row - 200 px and the x axis) form one run; its centre is the line, its half
thickness plus 1.5 px and the misfit the interval.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("_sfig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sfig2.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    ay, ax, half_comma, xaxis = F.calibrate(image)
    im = np.asarray(image)[..., :3].astype(int)
    dark = im.mean(axis=2) < 100
    top = int(max(ay.rows[0] - 200, 0))
    out = []
    for xv in at:
        x = float(xv)
        c = int(round((x - ax.a) / ax.b))
        rows = np.where(dark[top: int(xaxis) - 3, c])[0] + top
        if len(rows) == 0:
            out.append({"x": x, "y": None, "note": f"no dark line in column {c}"})
            continue
        g = F.B._groups(rows, gap=2)
        if len(g) != 1:
            out.append({"x": x, "y": None, "note": f"{len(g)} dark runs in column {c}: ambiguous"})
            continue
        r = (g[0][0] + g[0][-1]) / 2.0
        lo, hi = ay.interval(r, (g[0][-1] - g[0][0] + 1) / 2.0 + 1.5)
        dx = abs(ax.b) * (half_comma + ax.misfit)
        # the line is not horizontal: an x error of dx moves it by slope * dx, added to the interval
        slope = None
        g2 = np.where(dark[top: int(xaxis) - 3, c + 20])[0]
        if len(g2):
            slope = (ay.val(np.mean(g2) + top) - ay.val(r)) / (ax.val(c + 20) - ax.val(c))
            lo, hi = lo - abs(slope) * dx, hi + abs(slope) * dx
        out.append({"x": x, "y": ay.val(r), "lo": lo, "hi": hi, "px": [float(c), r],
                    "note": f"line at row {r:.1f} in column {c}; x label centring +- {dx:.3g} carried through the slope"
                            f" ({slope if slope is None else round(slope, 3)}); misfits x {ax.misfit:.2f} px, y {ay.misfit:.2f} px"})
    return out
