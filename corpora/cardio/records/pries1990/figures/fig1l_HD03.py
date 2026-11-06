"""Fig. 1, lower panel: relative apparent viscosity (Eqs. 2, 3) against diameter; the curve labelled HD = 0.3 (second from the bottom of the five curves)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pries as P  # noqa: E402

PANEL = 1
Y_LABELS = [8.0, 6.0, 4.0, 2.0, 0.0]  # the printed tick labels, top to bottom
FROM_BOTTOM = 1


def read(image, at):
    cal = P.calibrate(image, PANEL, Y_LABELS)
    return P.read_rank(cal, [float(a) for a in at], FROM_BOTTOM, P.n_fig1_lower)
