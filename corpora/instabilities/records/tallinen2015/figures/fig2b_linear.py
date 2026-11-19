"""Fig. 2(b) (PDF p. 3): the blue solid line (g < gs), wavelength of linear instability l/h against g.

Shared code in _tal.py. Axes and tick matching as fig2b_eta1.py: x 1.2-2.2 (1.0 at the left frame line),
y 2, 4, 6, 8 (0 at the bottom frame line). The solid line is the large blue component through g < 1.55 (the eta = 1/2 polyline starts right of gs, so in these columns the solid blue line is the only long blue component). Lines of other colours drawn over it cut it into pieces, so pieces of 120 px or more count as solid; the dots of the dotted end are about 15 px. It is the lowest such run.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [1.2, 1.4, 1.6, 1.8, 2.0, 2.2], "at_axis": 1.0, "major_len": 20, "span_end": 2900},
    "y": {"ticks": [2, 4, 6, 8], "at_axis": 0, "major_len": 20, "span_start": 200},
    "ink": "blue", "part": "solid", "rank": 0, "w": 10, "pad": 14, "fit_px": 40, "min_solid": 120,
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
