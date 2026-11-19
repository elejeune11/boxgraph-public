"""Shared reading code for the scatter-over-box plots of single groups: Fig. 3K (spring constant
of 1% capsules), Fig. 3L (pressure at buckling, 1% capsules), Fig. 4J (spring constants of 2.5%
capsules with and without a monolayer).

Calibration (_cal.py): the y axis is the longest ink column in the left half; the ticks found
are the long ticks pointing left (the minor ticks are dots on the axis line and are not found),
indexed from the x axis crossing, whose printed value is the panel's lowest label. Steps: 3K
0.01 N/m from 0 (labels 0, 0.02, ..., 0.08 on every second tick); 3L 20 Pa from 60 (labels 60,
80, ..., 180 on every tick); 4J 0.01 N/m from 0 (labels 0,00 to 0,12 with decimal commas on
every second tick; the ticks between labels are as long as the labelled ones).
Touching markers are split by area; where three or more overlap closely the count can still
come out one short of the n in the legend (the record compares the count found with that n).
The box lines printed with their values (3K 0.017, 0.029, 0.048; 3L 119, 128, 144) are a check
of the calibration, done by hand on the overlay.
Markers: pixels near the marker colour (red, or black for the 4J empty-capsule group) inside the
group's column range, opened with a disk of radius 6 px, touching markers split by area. The
box, whiskers and small black squares (mean, extremes) are not the marker colour (red groups) or
are thinner than the disk (black lines). The group has no numeric x: each marker's x is its rank.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

PANELS = {
    # y origin value, minor step, tick side
    "3K": (0.0, 0.01, "out"),
    "3L": (60.0, 20.0, "out"),
    "4J": (0.0, 0.01, "out"),
}


def read_group(image, panel, rgb, tol, cols=None, open_radius=6, black=False):
    L = C.axes_lines(image)
    v0, step, side = PANELS[panel]
    yo = (L["xr0"] + L["xr1"]) / 2
    ya = C.calibrate_from(yo, C.ticks_y(L, side), v0, step)
    if black:
        m = C.ink(image, 300)
    else:
        m = C.colour(image, rgb, tol)
    m[L["xr0"] - 3:, :] = False
    m[:, :L["yc1"] + 4] = False
    if cols:
        W = image.shape[1]
        a, b = int(cols[0] * W), int(cols[1] * W)
        m[:, :a] = False
        m[:, b:] = False
    pts, rad = C.scatter(m, open_radius, min_area=150)
    return C.ranked(ya, pts, rad, note=f"axis rms {ya.rms_px:.2f} px; ticks {len(ya.px)}")
