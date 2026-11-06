"""Fig. 3, 9 um panel (p. 5): the Eq. 3 line (Table 2 B and C). With markers masked, the lowest
run in a column below 5.8 (the panel label stands above). Calibration in _fig3.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def band(x):
    return (0.8, 5.8, "bottom")


def read(image, at):
    return F.read_line(image, at, "9", band, "the panel's line")
