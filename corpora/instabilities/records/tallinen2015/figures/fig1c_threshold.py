"""Fig. 1(c) (PDF p. 2): the solid line, threshold growth g of the first unstable mode against eta.

Shared code in _tal.py (calibration, line choice, intervals). Axes: Mathematica-style open axes with
ticks inward; long ticks matched to the printed labels x 1, 2, 3, 4, 5 (0 at the y axis). On y,
short ticks stand every 0.05 and long ones every 0.2; the labels 1.0 (at the x axis), 1.5 (a short
tick, ten short-tick steps above 1.0) and 2.0 (the top long tick) fix the long ticks at 1.2-2.0. The solid line is the large connected blue component; the dashed
asymptote (small dashes) and the black dashed guide lines at eta_b, eta_s and gs are excluded.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [1, 2, 3, 4, 5], "at_axis": 0, "major_len": 30},
    "y": {"ticks": [1.2, 1.4, 1.6, 1.8, 2.0], "at_axis": 1.0, "major_len": 30},
    "ink": "blue", "part": "solid", "rank": 0, "w": 16,
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
