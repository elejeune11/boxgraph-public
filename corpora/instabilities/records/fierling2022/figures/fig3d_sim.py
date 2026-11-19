"""Fig. 3d (PDF p. 7): the dashed navy line, simulated DV length fold change at t = -1 min against the
distance from the midline (rows). Calibration in _fig3cd.py; colour dark-blue (0, 0, 139); the
dashes are read over a window of +-40 columns; the legend's sample line (value about 0.635) is
outside the value range searched.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3cd as F  # noqa: E402


def read(image, at):
    return F.line(image, at, F.Y_D, F.DBLUE, (0.68, 1.2), win=40)
