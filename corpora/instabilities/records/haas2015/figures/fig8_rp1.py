"""Fig. 8 (PDF p. 8): the trajectory of the critical point for r_p = R (the darkest blue curve,
labelled "r_p = R"), k*R against lambda*/R, as lambda_max varies.

Calibration by _colour_curves.py (see its docstring): labelled y ticks 30, 20, 10 from the top;
x labels 0, 0.2, ... under every second tick (0.1 per tick). The six trajectories are drawn in
six flat colours; this one is (0, 0, 153), and it is the largest part of that colour (the next
largest is the dark end of the colour bar).
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
    mask, lab, order, sizes = m.colour_parts(cal, (0, 0, 153))
    return m.read_mask(cal, np.isin(lab, order[:1]), at, "trajectory r_p = R, colour (0, 0, 153)")
