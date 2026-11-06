"""Fig. 5A: the light grey open squares (Fc/GG-7, replotted from Fig. 3), with their SEM bars.
With `at`, reads the line joining these markers at those forces instead. (Audit addition: on this
panel's axes every square above 24 pN lies on the lower segment, so the line can be read at 30-50 pN.)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lt  # noqa: E402

# the printed tick labels matched to the ticks found (bottom segment first, where the y axis is broken);
# the rough outer width of a marker in pixels at the reading's dpi; regions not searched for markers:
# the panel title;
# the squares' outline is thinner than their lines; the square at 51 pN is partly covered by a circle
# and a triangle, so the outline threshold is lowered to 0.85 (all nine squares are then found, and no
# other spot)
CONFIG = {'y_segments': [[0, 3, 6, 9, 12], [16, 24]], 'x_labels': [0, 20, 40, 60], 'colour': 'lightgrey', 'shape': 'square', 'size': 105, 'exclude': [(0.55, 0.0, 1.0, 0.13)], 'bars': True, 'outline': 5, 'thr': 0.85}


def read(image, at):
    return _lt.read_panel(image, at, **CONFIG)
