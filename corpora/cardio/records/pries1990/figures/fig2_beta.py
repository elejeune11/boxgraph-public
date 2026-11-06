"""Fig. 2: fractional erythrocyte flow FQE against fractional blood flow FQB at one bifurcation;
the open circles (daughter vessel beta). Same calibration as fig2_alpha."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402
from fig2_alpha import DIAMETER, LEGEND, OPEN_R, X, Y  # noqa: E402

WANT = "open"


def read(image, at):
    return P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=LEGEND)
