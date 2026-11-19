"""Fig. 2b (PDF p. 6): the energy variation delta phi^b / zeta^4 (axis "x 10^-3") along the bifurcation
curve, against eps.

Calibration by `_diab.calibrate`: x ticks labelled 0, 0.1, ..., 0.5 and y ticks labelled -2, 0, 2, ...,
10, found as tick marks outside the axes. The single solid curve is followed (`_diab.read_tracked`)
from its stroke at eps = 0.15 to both ends; the dotted zero line and the thin asterisks at M and B are
removed by opening the ink with a 15 px square, the M and B labels by the run-length test of the
follower. The values are in the axis's own units (the axis label's "x 10^-3" is not applied).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013_d", Path(__file__).with_name("_diab.py"))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    out, *_ = d.read_tracked(image, at, [0, 0.1, 0.2, 0.3, 0.4, 0.5], [-2, 0, 2, 4, 6, 8, 10], 0.15,
                             x_range=(0.005, 0.5))
    return out
