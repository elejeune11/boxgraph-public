"""Fig. 3: relative apparent viscosity modified by Eq. 7 (W = 3.5 um) against diameter; the curve labelled HD = 0.6 (fourth from the bottom of the five curves)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pries as P  # noqa: E402

PANEL = 0
Y_LABELS = [25.0, 20.0, 15.0, 10.0, 5.0, 0.0]  # the printed tick labels, top to bottom
FROM_BOTTOM = 3


def read(image, at):
    cal = P.calibrate(image, PANEL, Y_LABELS)
    return P.read_rank(cal, [float(a) for a in at], FROM_BOTTOM, P.n_fig3)
