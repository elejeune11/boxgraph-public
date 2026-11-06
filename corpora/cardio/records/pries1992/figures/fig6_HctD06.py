"""Fig. 6 (p. 7): the thin solid line for discharge hematocrit 0.6, top thin line.
Calibration and curve choice in _fig6.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig6 as F  # noqa: E402


def read(image, at):
    return F.read(image, at, heavy=False, rank=0, label="thin line 1 of 3 from the top")
