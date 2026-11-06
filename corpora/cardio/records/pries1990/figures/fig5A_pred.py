"""Fig. 5, upper panel (network A): the open circles joined by the dashed line (PREDICTED).
Same calibration as fig5A_meas."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402
from fig5A_meas import DIAMETER, EXCLUDE, OPEN_R, TOL, X, Y  # noqa: E402

WANT = "open"


def read(image, at):
    return P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=EXCLUDE,
                         at=[float(a) for a in at], at_tol=TOL)
