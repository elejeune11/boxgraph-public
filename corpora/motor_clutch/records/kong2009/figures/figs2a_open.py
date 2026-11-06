"""Fig. S2 A: the open histogram bars (FNIII7-10 tips). The x axis has a tick every 5 pN, labelled every 10 pN."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; x tick labels where the x axis is numeric; which bars to read
CONFIG = {'y_labels': [0, 0.1, 0.2, 0.3], 'kind': 'open', 'bars': False, 'x_labels': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90], 'min_w': 60}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
