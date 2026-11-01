"""Fig. 2 B: the closed bars (closed bars (FN/integrin): FNIII7-10 tips on a5b1-Fc captured by GG-7, mean +- SEM; x = 1 Ca2+/Mg2+ (GG-7 100 ug/ml), 2 Mg2+/EGTA (20 ug/ml), 3 Mn2+ (10 ug/ml))."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; which bars to read
CONFIG = {'y_labels': [0, 0.1, 0.2, 0.3, 0.4], 'kind': 'closed'}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
