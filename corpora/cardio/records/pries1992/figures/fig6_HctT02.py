"""Fig. 6 (p. 7): the heavy solid line labelled 0.2 (fixed tube hematocrit), bottom heavy line.
Calibration and curve choice in _fig6.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig6 as F  # noqa: E402


def read(image, at):
    return F.read(image, at, heavy=True, rank=2, label="heavy line 3 of 3 from the top")
