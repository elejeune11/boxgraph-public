"""Fig. 3, 40 um panel (p. 5): the Eq. 3 line (Table 2 B and C). With markers masked, the lowest
run in a column, below 5.8 where the panel label stands (H_D < 0.6). Calibration in _fig3.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def band(x):
    return (0.8, 7.2, "bottom") if x >= 0.6 else (0.8, 5.8, "bottom")


def read(image, at):
    return F.read_line(image, at, "40", band, "the panel's line")
