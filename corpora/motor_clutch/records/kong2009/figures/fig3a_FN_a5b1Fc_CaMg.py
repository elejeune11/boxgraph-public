"""Fig. 3 A: the black open circles (FN/a5b1-Fc/GG-7, Ca2+/Mg2+), with their SEM bars.
With `at`, reads the line joining the circles at those forces instead."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lt  # noqa: E402

# printed tick labels matched to the ticks found, bottom segment first (the y axis is broken above 4)
CONFIG = {"y_segments": [[0, 1, 2, 3, 4], [8, 16, 24]], "x_labels": [0, 20, 40, 60],
          "colour": "black", "shape": "circle", "size": 115,
          # the panel title (top right) is not searched for markers
          "exclude": [(0.6, 0.0, 1.0, 0.3)]}


def read(image, at):
    return _lt.read_panel(image, at, **CONFIG)
