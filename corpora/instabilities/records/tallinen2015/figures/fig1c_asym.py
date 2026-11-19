"""Fig. 1(c) (PDF p. 2): the dashed line, the stiff-layer asymptote 1 + (3/(8 eta))^(2/3) of g.

Shared code in _tal.py. Calibration as fig1c_threshold.py (same crop, same tick matching). The
dashed line is the set of small connected blue components (the dashes); between dashes its
centre is a quadratic fit to the dash centres within +-60 columns.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [1, 2, 3, 4, 5], "at_axis": 0, "major_len": 30},
    "y": {"ticks": [1.2, 1.4, 1.6, 1.8, 2.0], "at_axis": 1.0, "major_len": 30},
    "ink": "blue", "part": "dashed", "rank": 0, "w": 16, "fit_px": 60,
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
