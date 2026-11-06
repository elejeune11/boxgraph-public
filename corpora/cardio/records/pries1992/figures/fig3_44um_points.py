"""Fig. 3, upper-left panel (p. 5): the open circles, measured eta_rel against H_D in 4.4 um
capillaries (Gaehtgens & Pries data). Each round hole of the ink is one open circle
(_fig3.read_open); holes where the panel label '4.4 um n: 96' stands (H_D > 0.5,
eta_rel < 1.25) or the label '3.3 um n: 72' stands (H_D > 0.5, eta_rel > 3.1) are letters and
digits, not markers. Open circles hidden under filled ones have no hole and are not found."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def read(image, at):
    return F.read_open(image, "3.3/4.4", exclude=lambda x, y: x > 0.5 and (y < 1.25 or y > 3.1))
