"""Fig. 2(a) (PDF p. 3): the dotted blue line, threshold g of linear instability against eta (eta < eta_s).

Shared code in _tal.py. Axes: matplotlib frame with ticks inward; the bottom and left frame lines are
the axes. Ticks matched to the printed labels x 2, 4, 6, 8 (0 at the left frame line) and
y 1.2, 1.4, 1.6, 1.8 (1.0 at the bottom frame line); the labels 10 and 2.0 sit at the right and top
frame lines and are not used. The dotted line is the set of small blue components (dots, under 120 px); between dots the
centre is a quadratic fit to the dot centres within +-40 columns.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [2, 4, 6, 8], "at_axis": 0, "major_len": 20, "span_end": 2900},
    "y": {"ticks": [1.2, 1.4, 1.6, 1.8], "at_axis": 1.0, "major_len": 20, "span_start": 200},
    "ink": "blue", "part": "dashed", "rank": 0, "w": 10, "pad": 14, "min_solid": 120, "fit_px": 40,
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
