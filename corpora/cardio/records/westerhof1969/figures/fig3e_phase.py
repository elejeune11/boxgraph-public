"""Fig. 3, lower panel: phase of curve e (bold, NEW RADII)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402
import _w69 as W  # noqa: E402


def read(image, at):
    cal = F.calibrate(image)
    return W.bold_curve(cal, "ph", at, F.BOLD_R, 40, -90, seed_x=5.0)
