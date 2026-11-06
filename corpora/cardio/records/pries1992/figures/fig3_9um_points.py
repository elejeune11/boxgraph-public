"""Fig. 3, 9 um panel (p. 5): the filled circles, measured eta_rel against H_D (present data).
Markers found by _fig3.read_filled; nothing where the panel label stands (eta_rel > 5.8) is
kept."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def read(image, at):
    return F.read_filled(image, "9", exclude=lambda x, y: y > 5.8)
