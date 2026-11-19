"""Fig. 3(c) (PDF p. 3), eta = 4: the blue loop, finite-element amplitude A/h against g.

Shared code in _tal.py. Axes: MATLAB frame with ticks inward; the bottom and left frame lines are the
axes. Ticks matched to the printed labels x 1.22, 1.24, 1.26, 1.28 and y 0.2-1.4 (the frame lines are not used: they are 8 px thick). The dashed
vertical lines also stand on the bottom frame line; their first dash (46 px) is longer than a tick (18 px)
and is excluded by length.
The loop is the large blue component (the blue Unfolding arrow lies above it and is not the lowest blue run in the columns read); it is the lowest blue run in each column.
"""
from pathlib import Path

SPEC = {'x': {'ticks': [1.22, 1.24, 1.26, 1.28], 'major_len': 0, 'max_len': 30},
 'y': {'ticks': [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4], 'major_len': 0},
 'ink': 'blue',
 'part': 'solid',
 'rank': 0,
 'w': 20,
 'min_solid': 800}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_curve(image, at, SPEC)
