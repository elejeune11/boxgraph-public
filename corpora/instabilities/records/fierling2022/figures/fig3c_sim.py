"""Fig. 3c (PDF p. 7): the solid cyan line, simulated AP length fold change at t = -1 min against the
distance from the midline (rows). Calibration in _fig3cd.py; colour (0, 238, 238); the legend's
sample line (value about 0.64) is outside the value range searched.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3cd as F  # noqa: E402


def read(image, at):
    return F.line(image, at, F.Y_C, F.CYAN, (0.8, 1.1))
