"""Fig. 5, lower panel: phase of Z_in of the leg in the model (bold line)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402
import _w69 as W  # noqa: E402


def read(image, at):
    cal = F.calibrate(image)
    return W.bold_curve(cal, "ph", at, F.BOLD_HALF, 90, -95, method="dp")
