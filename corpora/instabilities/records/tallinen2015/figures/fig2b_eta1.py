"""Fig. 2(b) (PDF p. 3): the red points labelled eta = 1: finite-element energy-minimizing wavelengths l/h against g.

Shared code in _tal.py. Axes: matplotlib frame, ticks inward; the bottom and left frame lines are the
axes. Ticks matched to the printed labels x 1.2, 1.4, 1.6, 1.8, 2.0, 2.2 (1.0 at the left frame line)
and y 2, 4, 6, 8 (0 at the bottom frame line); 2.4 and 10 sit at the right and top frame lines and are
not used. Points: the red ink mask, small holes filled (hollow circles = smooth folds become
discs), then the cores farther than 14 px from any background pixel (the circles have a radius
of about 20 px, the joining lines are about 10 px wide and have no such core); each core's centroid
is a circle's centre, +- (misfit + 5 px) since lines or overlapping circles of other colours can shift
a core by a few pixels. 
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [1.2, 1.4, 1.6, 1.8, 2.0, 2.2], "at_axis": 1.0, "major_len": 20, "span_end": 2900},
    "y": {"ticks": [2, 4, 6, 8], "at_axis": 0, "major_len": 20, "span_start": 200},
    "ink": "red", "pad": 14, "core": 14, "area": [20, 900], "max_aspect": 1.8, "hole_max": 2500,
    "pad_px": 5, "blank": [[1200, 1050, 1520, 1220]],
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_markers(image, SPEC)
