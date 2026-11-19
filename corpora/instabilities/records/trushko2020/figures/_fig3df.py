"""Shared reading code for Fig. 3D (normalised capsule thickness) and Fig. 3F (capsule pressure)
against time (PDF p. 7), four series each: 1% green, 1.5% red, 2% blue, 2.5% orange; dots are
the means, the shaded bands their SEM (legend, p. 8: "error bars are SEM").

Calibration (_cal.py), from the ticks:
- x (both panels): ticks below the axis every 5 h from 0 at the y axis (labels 0, 10, ..., 60 on
  every second tick);
- Fig. 3D y: ticks left of the axis every 0.025 from the top tick, labelled 1.05, down to the
  tick labelled 0.8 just above the axis break (labels 0.8, 0.85, ..., 1.05 on every second
  tick); the ticks below the break (0) are not used;
- Fig. 3F y: ticks left of the axis every 50 Pa from the x axis crossing (labels 0, 100, ..., 600
  on every second tick from the second). The crossing is labelled "-0.1"; it is taken as -100 Pa,
  the value the evenly spaced labels 0-600 give it.
Dots: pixels near the series' dot colour (sampled from the image) opened with a disk of radius
8 px (a dot is about 30 px across; the lines between dots are thinner); the legend is left out.
Band: the run of the series' band or dot colour through the dot's column; read only where both
ends meet the paper, so a band crossed by another series is not read. Dots hidden under another
series' band are not found, and are missing from the reading. Interval on a dot: 5 px on its
centre plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

DOT = {"1": (10, 129, 52), "1.5": (230, 42, 34), "2": (1, 108, 172), "2.5": (240, 125, 20)}
BAND = {"1": (70, 161, 105), "1.5": (236, 91, 84), "2": (60, 145, 190), "2.5": (242, 155, 80)}


def _ticks_from_top(ticks, v_top, step, n_keep):
    p = sorted(ticks)
    keep, idx = C.whole_spacings(p[0], p[1:], max_index=n_keep)
    return C.Axis(keep, [v_top - step * k for k in idx])


def read_series(image, panel, series):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    xa = C.calibrate_from(xo, C.ticks_x(L), 0.0, 5.0)
    if panel == "3D":
        ya = _ticks_from_top(C.ticks_y(L), 1.05, 0.025, 10)
        H, W = image.shape[:2]
        legend = (int(0.28 * W), int(0.66 * H), int(0.58 * W), int(0.9 * H))
    else:
        ya = C.calibrate_from(yo, C.ticks_y(L), -100.0, 50.0)
        H, W = image.shape[:2]
        legend = (int(0.26 * W), 0, int(0.53 * W), int(0.25 * H))
    box = (L["yc1"] + 3, 0, image.shape[1], L["xr0"] - 2)
    return C.dots_with_band(image, xa, ya, DOT[series], BAND[series], 8, box, dot_tol=45.0,
                            band_tol=35.0, min_area=200, centre_px=5.0, legend=legend)
