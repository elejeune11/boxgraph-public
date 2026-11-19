"""Fig. 1(b) (PDF p. 2): the solid line, l/a of the first unstable mode against eta.

Shared code in _tal.py (calibration, line choice, intervals). Axes: Mathematica-style open axes with
ticks inward; major ticks matched to the printed labels x 1, 2, 3, 4, 5 (0 at the y axis); on y the long ticks
stand at every unit and the labels 2, 4, 6 on every second one, so the long ticks are 1-7 (0 at the
x axis). The solid line is the large connected blue component; the dashed asymptote is
made of small dashes and is excluded.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [1, 2, 3, 4, 5], "at_axis": 0, "major_len": 30},
    "y": {"ticks": [1, 2, 3, 4, 5, 6, 7], "at_axis": 0, "major_len": 30},
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
