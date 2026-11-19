"""Fig. 8 (PDF p. 8): the trajectory of the critical point for r_p = 0.75R (the lightest blue
curve), k*R against lambda*/R, as lambda_max varies.

Calibration by _colour_curves.py (see its docstring). The lightest trajectory is drawn in
(153, 153, 255), the colour of the end of the colour bar labelled 0.75 (the bar there is
(152, 152, 254)); it is the largest part of that colour (the next largest is the colour bar).
"""
import importlib.util
from pathlib import Path

import numpy as np


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_colour_curves", Path(__file__).with_name("_colour_curves.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal = m.calibrate(image, [30.0, 20.0, 10.0], 0.1)
    mask, lab, order, sizes = m.colour_parts(cal, (153, 153, 255))
    return m.read_mask(cal, np.isin(lab, order[:1]), at, "trajectory r_p = 0.75 R, colour (153, 153, 255)")
