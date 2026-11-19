"""Fig. 3(a) (PDF p. 3), eta = 0.5: the dashed vertical line labelled Linear instability.

Shared code in _tal.py. Axes: MATLAB frame with ticks inward; the bottom and left frame lines are the
axes. Ticks matched to the printed labels x 1.6, 1.7, 1.8, 1.9 and y 0.2-1.4 (the frame lines are not used: they are 8 px thick). The dashed
vertical lines also stand on the bottom frame line; their first dash (46 px) is longer than a tick (18 px)
and is excluded by length.
The line is read with read_vline: the second dashed vertical black line from the left.
"""
from pathlib import Path

SPEC = {'x': {'ticks': [1.6, 1.7, 1.8, 1.9], 'major_len': 0, 'max_len': 30},
 'y': {'ticks': [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4], 'major_len': 0},
 'ink': 'black',
 'index': 1}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_vline(image, at, SPEC)
