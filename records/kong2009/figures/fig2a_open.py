"""Fig. 2 A: the open bars (open bars, FNIII7-10 tips on a5b1-Fc captured by 15 ug/ml GG-7, mean +- SEM; x = 1 Ca2+/Mg2+, 2 Mg2+/EGTA, 3 Mn2+, 4 Mn2+ with cyclo(-GRGDSP), 5 Mn2+ with HFN7.1 (the 0.3 tick merges with the end of the axis line and is not used))."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; which bars to read
CONFIG = {'y_labels': [0, 0.1, 0.2], 'kind': 'open'}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
