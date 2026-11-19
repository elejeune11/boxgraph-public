"""Fig. 3c (PDF p. 7): red open triangles (up) with min-max error bars, confocal, AP length fold
change at t = -1 min by row (drawn 0.1 left of each row). Calibration in _fig3cd.py; the cyan
simulation line is drawn on top; the legend's sample (below 0.75) is left out.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3cd as F  # noqa: E402


def read(image, at):
    return F.markers(image, at, F.Y_C, F.RED, [F.CYAN], "triangle_up", (0.85, 1.19))
