"""Shared reading code for Fig. 3J (PDF p. 7, right): force (uN) against indentation depth (um)
for one representative 1% alginate capsule; red indentation curve, blue withdraw curve.

Calibration (_cal.py): x ticks below the axis every 5 um from 0 at the y axis (labels 0, 10, ...,
50 on every second tick); y ticks left of the axis every 0.25 uN from -0.5 at the x axis (labels
-0,5, 0,0, ..., 3,0 with decimal commas, on every second tick). Ticks indexed from the crossing.
Curve: pixels near the curve's colour (sampled from the image), in the column of each x; the
legend lines lie above both curves, so the lowest run in the column is taken. Interval: half
the run height (the line's thickness, larger where steep) plus calibration misfit.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

RGB = {"indentation": (235, 30, 30), "withdraw": (25, 95, 170)}


def read_curve(image, at, which):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    xa = C.calibrate_from(xo, C.ticks_x(L), 0.0, 5.0)
    ya = C.calibrate_from(yo, C.ticks_y(L), -0.5, 0.25)
    m = C.colour(image, RGB[which], 70.0)
    m[:, :L["yc1"] + 2] = False
    return C.curve_at(m, xa, ya, at, pick="bottom", rowlim=(0, L["xr0"] - 2), note=which)
