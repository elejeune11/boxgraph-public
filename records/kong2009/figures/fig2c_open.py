"""Fig. 2 C: the open bars (open bars, FNIII7-10 tips on tra5b1-Fc captured by 100 ug/ml GG-7, mean +- SEM; x = 1 Ca2+/Mg2+, 2 Mg2+/EGTA, 3 Mn2+)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; which bars to read
CONFIG = {'y_labels': [0, 0.1, 0.2, 0.3, 0.4, 0.5], 'kind': 'open'}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
