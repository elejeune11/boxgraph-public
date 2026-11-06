"""Fig. 1, upper panel: HT/HD against diameter; the curve labelled HD = 0.3 (second from the bottom of the five curves)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pries as P  # noqa: E402

PANEL = 0
Y_LABELS = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]  # the printed tick labels, top to bottom
FROM_BOTTOM = 1


def read(image, at):
    cal = P.calibrate(image, PANEL, Y_LABELS)
    return P.read_rank(cal, [float(a) for a in at], FROM_BOTTOM, P.n_fig1_upper)
