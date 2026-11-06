"""Fig. 8 (p. 9): systolic pressure / brachial systolic pressure against % abdominal stenosis, three
lines (upper thigh, knee, ankle). Shared by the readings of this panel.

Calibration (_figlib.calibrate): x from the short inward ticks next to the labels 0-100, y from the
inward ticks next to the labels 1.4-0.0 that are found (the 1.2 tick is not: the lines start next to
it); the small rotation of the scan is measured on the frame lines and taken out. The printed tick
spacing is itself slightly uneven, which the misfit (about 4 px, 0.003) records.

From 0 to about 55 % the three lines run flat and apart: the short-dashed one on top, the long
dash-dot one in the middle and the solid one at the bottom. The legend draws Upper Thigh as a solid
line, Knee as a short-dashed line and Ankle as a long-dash, dot-dot line, so top = knee, middle =
ankle, bottom = upper thigh. Beyond about 58 % the lines meet and cross and cannot be told apart
reliably; there they are read together as one band (fig8_band), whose interval holds all three.
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figlib", Path(__file__).with_name("_figlib.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)

XV = [0, 20, 40, 60, 80, 100]
YV = [1.4, 1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
ORDER = {"knee": 0, "ankle": 1, "thigh": 2}


def _cal(image):
    d = fl.dark(image)
    fr, X, Y, cal = fl.calibrate(d, XV, YV, x_ends=False, y_ends=False, depth=(3, 13))
    return d, fr, X, Y, cal


def read_flat(image, at, which):
    d, fr, X, Y, cal = _cal(image)
    return fl.stacked_lines(d, cal, at, 1.05, 1.2, 3, ORDER[which])


def read_band(image, at):
    d, fr, X, Y, cal = _cal(image)
    return fl.band(d, cal, at, 0.3, 1.25)
