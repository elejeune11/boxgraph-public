"""Fig. 4(e) (PDF p. 4): the yellow points labelled eta = 10, finite-element energy-minimizing half-wavelength l_h/2 of triple junctions against g.

Shared code in _tal.py. Axes: matplotlib frame with ticks inward; the bottom and left frame lines are the
axes. Ticks matched to the printed labels x 1.2, 1.4, 1.6, 1.8, 2.0 (1.0 at the left frame line) and
y 2, 4, 6, 8 (0 at the bottom frame line; 10 is at the top frame line and not used).
Points: the olive ink mask (marker interiors; their outlines are black), the cores farther than 12 px from any background pixel (markers have a coloured radius of about 18 px; the joining solid, dashed and dotted lines are about 10 px wide and have no core); each core centroid is a marker centre, +- (misfit + 5 px) as overlapping markers or lines can shift a core.
"""
from pathlib import Path

SPEC = {'x': {'ticks': [1.2, 1.4, 1.6, 1.8, 2.0], 'at_axis': 1.0, 'major_len': 20, 'max_len': 80},
 'y': {'ticks': [2, 4, 6, 8], 'at_axis': 0, 'major_len': 20, 'max_len': 80},
 'ink': 'olive',
 'pad': 14,
 'core': 12,
 'area': [20, 1200],
 'max_aspect': 1.8,
 'hole_max': 0,
 'pad_px': 5}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_markers(image, SPEC)
