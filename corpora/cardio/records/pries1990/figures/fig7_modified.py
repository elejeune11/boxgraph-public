"""Fig. 7: filled circles (simulation of network A, modified viscosity law). Calibration and
matching in _fig7.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig7 as F  # noqa: E402

WANT = "filled_circle"


def read(image, at):
    return F.read_series(image, [float(a) for a in at], WANT)
