"""Fig. 4(b) (PDF p. 4): the blue curve, threshold for linear instability or sulcification against eta
(equibiaxial growth).

Shared code in _tal.py. Axes: matplotlib frame with ticks inward; the bottom and left frame lines are
the axes. Ticks matched to the printed labels x 2, 4, 6, 8, 10 (0 at the left frame line) and
y 1.2, 1.4, 1.6, 1.8, 2.0 (1.0 at the bottom frame line). The curve is the large blue component(s): it
is cut where the blue "o" symbols sit on it (eta = 3, 6, 10), so it is not read there; the blue labels
and symbols are small components and drop out. It is the lowest long blue run in each column.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [2, 4, 6, 8, 10], "at_axis": 0, "major_len": 20, "max_len": 80},
    "y": {"ticks": [1.2, 1.4, 1.6, 1.8, 2.0], "at_axis": 1.0, "major_len": 20, "max_len": 80},
    "ink": "blue", "part": "solid", "rank": 0, "w": 11, "pad": 14, "min_solid": 300,
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
