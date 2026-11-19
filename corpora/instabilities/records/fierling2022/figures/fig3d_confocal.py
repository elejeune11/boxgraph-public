"""Fig. 3d (PDF p. 7): dark-red open triangles (down) with dashed min-max error bars, confocal, DV
length fold change at t = -1 min by row (drawn 0.1 left of each row). Calibration in _fig3cd.py;
the navy simulation line is drawn on top; dashes joined across gaps of up to 60 rows; the legend's
sample (below 0.74) is left out.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3cd as F  # noqa: E402


def read(image, at):
    return F.markers(image, at, F.Y_D, F.DRED, [F.DBLUE], "triangle_down", (0.745, 1.25), dash_gap=60)
