"""Fig. 5, upper panel: |Z_in|/R x 100 of the leg in the model (bold line)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402
import _w69 as W  # noqa: E402


def read(image, at):
    cal = F.calibrate(image)
    return W.bold_curve(cal, "mod", at, F.BOLD_HALF, 52, -1, method="dp")
