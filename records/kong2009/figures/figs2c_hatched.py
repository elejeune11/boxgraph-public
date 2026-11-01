"""Fig. S2 C: the hatched bars (hatched bar: P1D6 tips on GG-7 without a5b1-Fc, mean +- SEM; one bar (x = 1))."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; which bars to read
CONFIG = {'y_labels': [0, 0.1, 0.2, 0.3], 'kind': 'hatched'}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
