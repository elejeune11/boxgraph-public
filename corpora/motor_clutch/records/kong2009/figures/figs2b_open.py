"""Fig. S2 B: the open bars (open bar: streptavidin tips without FNIII7-10 on ma5b1 in bilayers, Mg2+/EGTA, mean +- SEM; one bar (x = 1))."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; which bars to read
CONFIG = {'y_labels': [0, 0.05, 0.1, 0.15], 'kind': 'open'}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
