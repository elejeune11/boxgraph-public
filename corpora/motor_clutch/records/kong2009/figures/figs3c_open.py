"""Fig. S3 C: the open bars (open bars: average molecular stiffness of FN/a5b1-Fc/GG-7 events in Ca2+/Mg2+ at 25-40 pN, in three lifetime bins, mean +- SEM; x = bins 1, 2, 3, labelled with average lifetimes 0.3, 2.8 and 13.4 s)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bars  # noqa: E402

# the printed y tick labels matched to the ticks found, bottom to top; which bars to read
CONFIG = {'y_labels': [0, 0.3, 0.6, 0.9], 'kind': 'open'}


def read(image, at):
    return _bars.read_panel(image, at, **CONFIG)
