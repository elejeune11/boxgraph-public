"""Fig. 3, upper-left panel (p. 5): the filled circles, measured eta_rel against H_D in 3.3 um
capillaries (Gaehtgens & Pries data). Markers found by _fig3.read_filled; nothing found where the
panel label '3.3 um n: 72' stands (H_D > 0.5, eta_rel > 3.1) is kept."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def read(image, at):
    return F.read_filled(image, "3.3/4.4", exclude=lambda x, y: x > 0.5 and y > 3.1)
