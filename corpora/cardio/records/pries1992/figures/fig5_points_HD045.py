"""Fig. 5 (p. 6): the filled circles, measured relative viscosity at hematocrit 0.45 (the compiled
data of Fig. 2, per the caption). Calibration in _fig5.py; markers found and split by
_fig5.read_dots. The letters (data at H_D 0.2 and 0.6) are not markers and are not read here."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402


def read(image, at):
    return F.read_dots(image)
