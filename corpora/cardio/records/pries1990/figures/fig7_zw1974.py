"""Fig. 7: open triangles on the long-dashed line (Zweifach 1974, ref. 25). Calibration and
matching in _fig7.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig7 as F  # noqa: E402

WANT = "open_tri"


def read(image, at):
    return F.read_series(image, [float(a) for a in at], WANT)
