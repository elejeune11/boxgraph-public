"""Fig. 4(d) (PDF p. 4): the blue points labelled eta = 0.86, finite-element energy-minimizing half-wavelength l_y/2 of zigzags against g.

Shared code in _tal.py. Axes: matplotlib frame with ticks inward; the bottom and left frame lines are the
axes. Ticks matched to the printed labels x 1.2, 1.4, 1.6, 1.8, 2.0 (1.0 at the left frame line) and
y 2, 4, 6, 8 (0 at the bottom frame line; 10 is at the top frame line and not used).
Points: the blue ink mask (marker interiors; their outlines are black), the cores farther than 12 px from any background pixel (markers have a coloured radius of about 18 px; the joining solid, dashed and dotted lines are about 10 px wide and have no core); each core centroid is a marker centre, +- (misfit + 5 px) as overlapping markers or lines can shift a core. Two series share this colour: l_y/2 (solid line) and l_x/2 (dashed line); at each g the two points are told apart by height, l_y/2 being the upper one except at g = 2.0, where the dashed (l_x/2) line ends above the solid one. Where only one point is seen at a g (the two coincide or one is hidden), it is kept in both series.
"""
from pathlib import Path

SPEC = {'x': {'ticks': [1.2, 1.4, 1.6, 1.8, 2.0], 'at_axis': 1.0, 'major_len': 20, 'max_len': 80},
 'y': {'ticks': [2, 4, 6, 8], 'at_axis': 0, 'major_len': 20, 'max_len': 80},
 'ink': 'blue',
 'pad': 14,
 'core': 12,
 'area': [20, 1200],
 'max_aspect': 1.8,
 'hole_max': 0,
 'pad_px': 5,
 'pick': 'upper',
 'pick_flip_x': [2.0]}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_markers(image, SPEC)
