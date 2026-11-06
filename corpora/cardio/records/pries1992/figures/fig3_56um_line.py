"""Fig. 3, 5.6 um panel (p. 5): the Eq. 3 line (Table 2 B and C). With markers masked, the lowest
run in a column below 1.9 (the top frame line is 2). Calibration in _fig3.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def band(x):
    return (0.8, 1.9, "bottom")


def read(image, at):
    return F.read_line(image, at, "5.6", band, "the panel's line")
