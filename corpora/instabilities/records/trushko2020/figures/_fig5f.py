"""Shared reading code for Fig. 5F (PDF p. 11): histograms of fold number, experiment (top, dark
green bars, 2.5% alginate capsules, n = 43) and simulations (bottom, light green bars, n = 184,
kbar_s/cbar_b = 0.1).

Calibration (_cal.py): x ticks below the axis every 0.5 from the y axis, which stands at -0.5
(the bins are centred on the labels 0, 1, ..., 5; the ticks between labels mark bin edges); y
ticks left of the axis indexed from the x axis crossing at 0, with the step between the ticks
found: experiment 5 counts (labels 0, 5, ..., 25), simulations 20 counts (labels 0, 20, ...,
100); the ticks between labels are dots on the axis line and are not found. Check: the bars
read sum to the legend's n (43 and 184) within the reading intervals.
Bars: in the column of each bin centre, the topmost pixel of the bar colour (any green: green
channel well above red and blue) above the x axis; its row is the bar top. A bin with no bar in
its column reads 0 (top at the axis). Interval: 2 px on the edge plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

YSTEP = {"exp": 5.0, "sim": 20.0}


def read_hist(image, which):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    xa = C.calibrate_from(xo, C.ticks_x(L), -0.5, 0.5)
    ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, YSTEP[which])
    im = image.astype(int)
    green = (im[:, :, 1] - im[:, :, 0] > 40) & (im[:, :, 1] - im[:, :, 2] > 30)
    green[L["xr0"] - 1:, :] = False
    out = []
    for k in range(6):
        c = int(round(xa.pix(float(k))))
        rows = np.where(green[:, c - 3:c + 4].any(axis=1))[0]
        top = float(rows.min()) if len(rows) else float(yo)
        p = C.point(xa, ya, c, top, 1, 2, note=f"bin {k}; " + ("bar top" if len(rows) else "no bar: 0"))
        p["x"] = float(k)
        out.append(p)
    return out
