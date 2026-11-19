"""Fig. 1(b) (PDF p. 2): the dashed line, the stiff-layer asymptote (8 pi^3 eta/3)^(1/3) of l/a.

Shared code in _tal.py. Calibration as fig1b_mode.py (same crop, same tick matching). The dashed
line is the set of small connected blue components (the dashes); between dashes its centre is a
quadratic fit to the dash centres within +-60 columns.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [1, 2, 3, 4, 5], "at_axis": 0, "major_len": 30},
    "y": {"ticks": [1, 2, 3, 4, 5, 6, 7], "at_axis": 0, "major_len": 30},
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
