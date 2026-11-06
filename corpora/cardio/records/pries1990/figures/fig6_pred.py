"""Fig. 6: the open circles on the dashed line (PREDICTED, network A). Same calibration as
fig6_meas; every open marker is read at the generation read from the image."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402
from fig6_meas import DIAMETER, EXCLUDE, OPEN_R, X, Y  # noqa: E402

WANT = "open"


def read(image, at):
    return P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=EXCLUDE)
