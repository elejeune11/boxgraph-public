"""Fig. 7: filled triangles on the dotted line (Zweifach and Lipowsky 1977, ref. 26). Calibration
and matching in _fig7.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig7 as F  # noqa: E402

WANT = "filled_tri"


def read(image, at):
    return F.read_series(image, [float(a) for a in at], WANT)
