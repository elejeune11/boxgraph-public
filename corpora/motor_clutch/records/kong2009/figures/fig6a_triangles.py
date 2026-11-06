"""Fig. 6A: the black open triangles (Fig. 3C circles replotted) (positions only).
With `at`, reads the line joining these markers at those forces instead."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lt  # noqa: E402

# the printed tick labels matched to the ticks found (bottom segment first, where the y axis is broken);
# the rough outer width of a marker in pixels at the reading's dpi; regions not searched for markers:
# the panel title;
# the triangles' outline is thinner than the lines
CONFIG = {'y_segments': [[0, 3, 6, 9, 12], [16, 24]], 'x_labels': [0, 20, 40, 60], 'colour': 'black', 'shape': 'triangle', 'size': 180, 'exclude': [(0.5, 0.0, 1.0, 0.17)], 'bars': False, 'outline': 8}


def read(image, at):
    return _lt.read_panel(image, at, **CONFIG)
