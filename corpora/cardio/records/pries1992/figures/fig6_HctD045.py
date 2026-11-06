"""Fig. 6 (p. 7): the thin broken line for discharge hematocrit 0.45, middle thin line.
Calibration and curve choice in _fig6.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig6 as F  # noqa: E402


def read(image, at):
    return F.read(image, at, heavy=False, rank=1, label="thin line 2 of 3 from the top")
