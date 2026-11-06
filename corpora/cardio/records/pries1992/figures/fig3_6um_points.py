"""Fig. 3, 6 um panel (p. 5): the filled circles, measured eta_rel against H_D (Gaehtgens & Pries
data). Markers found by _fig3.read_filled; nothing where the panel label stands (H_D > 0.6,
eta_rel < 1.1) is kept."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def read(image, at):
    return F.read_filled(image, "6", exclude=lambda x, y: x > 0.6 and y < 1.1)
