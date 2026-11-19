"""Shared reading code for Fig. S2 (PDF p. 24): fluorescence (FITC) intensity in regions of
interest (ROIs) against time, capsule permeability controls.

Read: S2B, S2D, S2F, the purple ROI 1 curve (ROI 1 lies in the monolayer lumen for B, and in the
lumen for D and F; the caption's panels A, C, E show where); S2G, both curves (blue: ROI 3 of the
unbent lumen, panel C; red: ROI 3 of the bent lumen, panel E), mean normalised intensity.
Not read: ROIs 2-4 of S2B and of the main plots of S2D/S2F (in B the green, cyan and magenta
traces are noisy and overlap; in D and F they lie on the x axis), and the insets of S2D/S2F
(three overlapping traces).

Calibration (_cal.py), all from ticks pointing out of the axes, indexed from the axis crossing:
S2B x every 10 min from 0 (labels 0, 20, ..., 120 on every second tick), y every 5 from 0
(labels 0, 10, ..., 60 on every second tick); S2D and S2F x every 1 h from 0 (labels 0, 2, ...,
12 on every second tick), y every 1000 from 0 (labels 0, 2000, ... on every second tick); S2G x
every 1 h from 0 (labels 0, 2, ..., 12), y every 0.1 from 0 (labels 0,0, 0,2, ..., 1,0 with
decimal commas, on every second tick).
Curve: pixels near the curve's colour (sampled from the image) in the column of each x; the
legend lines are left out by taking the run nearest the top (ROI 1 lies above its legend in the
columns read) or, in S2G, by masking the legend box (lower left of the plot). Interval: half
the run height (line, markers and noise) plus calibration misfit.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

STEPS = {"B": (10.0, 5.0), "D": (1.0, 1000.0), "F": (1.0, 1000.0), "G": (1.0, 0.1)}
RGB = {"roi1": (130, 30, 230), "unbent": (40, 160, 230), "bent": (230, 20, 20)}


def read_curve(image, at, panel, which):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    sx, sy = STEPS[panel]
    xa = C.calibrate_from(xo, C.ticks_x(L), 0.0, sx)
    ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, sy)
    m = C.colour(image, RGB[which], 80.0)
    m[:, :L["yc1"] + 3] = False
    H, W = m.shape
    if panel == "G":
        m[int(0.75 * H):, :int(0.45 * W)] = False     # the legend box
    return C.curve_at(m, xa, ya, at, pick="top", rowlim=(0, L["xr0"] - 2), note=f"S2{panel} {which}")
