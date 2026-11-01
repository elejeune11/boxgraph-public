"""Fig. S4 A: the running adhesion frequency, a band of overlapping filled squares, read at the given repeat numbers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s4  # noqa: E402

# the printed tick labels matched to the ticks found (y bottom to top, x left to right)
CONFIG = {'y_labels': [0, 0.2, 0.4, 0.6], 'x_labels': [0, 50, 100, 150, 200, 250, 300]}


def read(image, at):
    return _s4.read_band(image, at, **CONFIG)
