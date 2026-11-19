"""Fig. 1(a) (PDF p. 2): the solid line labelled eta = 1 (third line from the bottom), Eq. 1 threshold g against l/a.

Shared code in _tal.py. Axes: Mathematica-style open axes, ticks inward. x: long ticks every 1
(labels 0, 2, 4, 6 on every second one; 0 at the y axis). y: short ticks every 0.1, long ticks every 0.5
(labels 2 and 3 on the second and fourth long tick; 1 at the x axis), so the long ticks are 1.5-3. Solid lines are the large blue components (the dashed eta_b line is excluded);
at l/a >= 1.5 the lines are separate and keep their order, so this one is the RANK-th from the
bottom: eta = 2, 1.5, 1, 0.8, 0.6, then (above the dashed eta_b line) 0.4, 0.3, ...
"""
from pathlib import Path

RANK = 2

SPEC = {
    "x": {"ticks": [1, 2, 3, 4, 5, 6], "at_axis": 0, "major_len": 22},
    "y": {"ticks": [1.5, 2, 2.5, 3], "at_axis": 1, "major_len": 22},
    "ink": "blue", "part": "solid", "rank": RANK, "w": 11,
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
