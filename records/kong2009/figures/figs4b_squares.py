"""Fig. S4 B: the four filled squares (adhesion frequency versus elapsed time)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s4  # noqa: E402

# the printed tick labels matched to the ticks found (y bottom to top, x left to right)
CONFIG = {'y_labels': [0, 0.1, 0.2, 0.3], 'x_labels': [0, 40, 80, 120, 160, 200, 240]}


def read(image, at):
    return _s4.read_squares(image, at, **CONFIG)
