"""Fig. 3c (PDF p. 7): goldenrod open triangles (up) with min-max error bars, MuVi SPIM, AP length
fold change at t = -1 min by row. Calibration in _fig3cd.py; the red confocal triangles and the cyan
simulation line are drawn on top; the legend's sample (below 0.75) is left out.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3cd as F  # noqa: E402


def read(image, at):
    # a bar runs on under the red confocal triangle drawn over it: gaps of up to 80 rows are bridged
    return F.markers(image, at, F.Y_C, F.GOLD, [F.RED, F.CYAN], "triangle_up", (0.85, 1.19), dash_gap=80)
