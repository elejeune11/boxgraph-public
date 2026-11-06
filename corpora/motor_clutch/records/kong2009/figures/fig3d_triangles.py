"""Fig. 3D: the black open triangles (FN/ma5b1, Mg2+/EGTA), with their SEM bars.
With `at`, reads the line joining these markers at those forces instead."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lt  # noqa: E402

# the printed tick labels matched to the ticks found (bottom segment first, where the y axis is broken);
# the rough outer width of a marker in pixels at the reading's dpi; regions not searched for markers:
# the panel title;
# the small triangles are mostly filled by the lines meeting inside them
CONFIG = {'y_segments': [[0, 0.5, 1.0, 1.5]], 'x_labels': [0, 20, 40, 60], 'colour': 'black', 'shape': 'triangle', 'size': 160, 'exclude': [(0.55, 0.0, 1.0, 0.25)], 'bars': True, 'max_inner': 0.88}


def read(image, at):
    return _lt.read_panel(image, at, **CONFIG)
