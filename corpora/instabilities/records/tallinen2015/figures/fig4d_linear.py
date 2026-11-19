"""Fig. 4(d) (PDF p. 4): the thick black curve, wavelength of linear instability against g.

Shared code in _tal.py. Axes: matplotlib frame with ticks inward; the bottom and left frame lines are the
axes. Ticks matched to the printed labels x 1.2, 1.4, 1.6, 1.8, 2.0 (1.0 at the left frame line) and
y 2, 4, 6, 8 (0 at the bottom frame line; 10 is at the top frame line and not used).
The curve is the large black component (marker outlines, tick marks and text are small components and drop out); it is the lowest long black run in each column.
"""
from pathlib import Path

SPEC = {'x': {'ticks': [1.2, 1.4, 1.6, 1.8, 2.0], 'at_axis': 1.0, 'major_len': 20, 'max_len': 80},
 'y': {'ticks': [2, 4, 6, 8], 'at_axis': 0, 'major_len': 20, 'max_len': 80},
 'ink': 'black',
 'part': 'solid',
 'rank': 0,
 'w': 14,
 'pad': 14,
 'min_solid': 500}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
