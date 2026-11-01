"""Fig. 3A: the light grey open squares (Fc/GG-7), with their SEM bars.
With `at`, reads the line joining these markers at those forces instead."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lt  # noqa: E402

# the printed tick labels matched to the ticks found (bottom segment first, where the y axis is broken);
# the rough outer width of a marker in pixels at the reading's dpi; regions not searched for markers:
# the panel title;
# the squares' outline is thinner than their lines
CONFIG = {'y_segments': [[0, 1, 2, 3, 4], [8, 16, 24]], 'x_labels': [0, 20, 40, 60], 'colour': 'lightgrey', 'shape': 'square', 'size': 85, 'exclude': [(0.6, 0.0, 1.0, 0.3)], 'bars': True, 'outline': 5}


def read(image, at):
    return _lt.read_panel(image, at, **CONFIG)
