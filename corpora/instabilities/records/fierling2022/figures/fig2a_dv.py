"""Fig. 2a (PDF p. 5): the dashed navy step line 'Actual DV size' (midline pre-strain 0.43).
Calibration as in fig2a_target.py; colour dark-blue (0, 0, 139); dashes read over +-20 columns.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2a  # noqa: E402
from fig2a_target import Y  # noqa: E402


def read(image, at):
    return _fig2a.read_line(image, at, Y, _fig2a.DBLUE, (0.9, 1.045), win=20)
