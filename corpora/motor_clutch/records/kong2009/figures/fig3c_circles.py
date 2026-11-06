"""Fig. 3C: the black open circles (FN/a5b1-Fc/GG-7, Mn2+), with their SEM bars.
With `at`, reads the line joining these markers at those forces instead."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lt  # noqa: E402

# the printed tick labels matched to the ticks found (bottom segment first, where the y axis is broken);
# the rough outer width of a marker in pixels at the reading's dpi; regions not searched for markers:
# the panel title and the legend;
# two circles are partly covered by the grey squares drawn over them; near (5.5 pN, 0.24 s) two overlapping circles and a diamond mimic a third circle
CONFIG = {'y_segments': [[0, 3, 6], [16, 24]], 'x_labels': [0, 20, 40, 60], 'colour': 'black', 'shape': 'circle', 'size': 115, 'exclude': [(0.55, 0.0, 1.0, 0.2), (0.7, 0.25, 1.0, 0.8), (0.19, 0.93, 0.215, 0.96)], 'bars': True, 'thr': 0.8}


def read(image, at):
    return _lt.read_panel(image, at, **CONFIG)
